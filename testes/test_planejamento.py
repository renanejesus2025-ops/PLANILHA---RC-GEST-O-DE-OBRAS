"""
Testes do módulo PLANEJAMENTO (Etapa 8 — Cronograma da Obra).

Cobre a decisão estrutural homologada em 2026-09-23 (Opção A): as datas
do cronograma moram nas próprias ETAPAS/SUBETAPAS, com fonte de verdade
única por registro; a entidade PLANEJAMENTO permanece reservada, sem uso
como tabela (mas continua registrável — regressão da Etapa 1).

Cobre também: Duração Prevista/Real e Variação de Prazo por
Etapa/Subetapa; consolidação MIN/MAX no nível da Obra; e a regressão de
que datas não alteram Orçamento, Financeiro, Compras ou Execução.
"""

from __future__ import annotations

from datetime import date

from src.base_dados.repositorio import BaseDados
from src.execucao.calculos import percentual_execucao_obra
from src.financeiro.calculos import orcamento_vigente, saldo_caixa
from src.modelo.entidades import (
    Etapa,
    Obra,
    Planejamento,
    ServicoOrcamento,
    Subetapa,
    dias_entre,
)
from src.modelo.enums import MetodoExecucao, StatusExecucao
from src.orcamento.calculos import total_previsto_obra
from src.planejamento.calculos import (
    data_fim_prevista_obra,
    data_fim_real_obra,
    data_inicio_prevista_obra,
    data_inicio_real_obra,
    duracao_prevista_obra_dias,
    etapas_da_obra,
)


def _obra(base: BaseDados) -> Obra:
    return base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra"))


def _etapa(base: BaseDados, id_obra: str, *, nome: str = "Alvenaria", **datas) -> Etapa:
    return base.adicionar_etapa(
        Etapa(id=base.gerador_id.gerar("ETAPAS"), id_obra=id_obra, nome=nome, **datas)
    )


def _subetapa(base: BaseDados, id_etapa: str, *, nome: str = "Reboco", **datas) -> Subetapa:
    return base.adicionar_subetapa(
        Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=id_etapa, nome=nome, **datas)
    )


# ----------------------------------------------------------------------
# dias_entre — convenção de subtração pura (Etapa 8)
# ----------------------------------------------------------------------
def test_dias_entre_subtracao_pura_sem_contagem_inclusiva():
    """Duas datas iguais = 0 dias (não 1). Nenhuma fonte define contagem
    inclusiva — a subtração pura é a mesma operação de toda variação do
    projeto (REG-005/REG-010/REG-028)."""
    assert dias_entre(date(2026, 3, 1), date(2026, 3, 1)) == 0
    assert dias_entre(date(2026, 3, 1), date(2026, 3, 2)) == 1
    assert dias_entre(date(2026, 3, 1), date(2026, 3, 31)) == 30


def test_dias_entre_sem_uma_das_datas_e_nao_calculavel():
    """`None` ("não calculável"), nunca 0 — mesmo princípio de REG-031."""
    assert dias_entre(None, date(2026, 3, 1)) is None
    assert dias_entre(date(2026, 3, 1), None) is None
    assert dias_entre(None, None) is None


def test_dias_entre_aceita_resultado_negativo():
    """Fim anterior ao início não é bloqueado — o sistema informa, o
    Operador decide (REG-032); mesma convenção de sinal de
    `Alteracao.impacto_prazo_dias`."""
    assert dias_entre(date(2026, 3, 10), date(2026, 3, 1)) == -9


# ----------------------------------------------------------------------
# Duração e Variação de Prazo por ETAPA
# ----------------------------------------------------------------------
def test_duracao_prevista_da_etapa():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
    )
    assert etapa.duracao_prevista_dias == 60


def test_duracao_real_da_etapa():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_inicio_real=date(2026, 3, 5), data_fim_real=date(2026, 5, 10),
    )
    assert etapa.duracao_real_dias == 66


def test_variacao_de_prazo_positiva_e_atraso():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_fim_prevista=date(2026, 4, 30), data_fim_real=date(2026, 5, 10),
    )
    assert etapa.variacao_prazo_dias == 10


def test_variacao_de_prazo_negativa_e_antecipacao():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_fim_prevista=date(2026, 4, 30), data_fim_real=date(2026, 4, 20),
    )
    assert etapa.variacao_prazo_dias == -10


def test_variacao_de_prazo_zero_quando_terminou_na_data():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_fim_prevista=date(2026, 4, 30), data_fim_real=date(2026, 4, 30),
    )
    assert etapa.variacao_prazo_dias == 0


def test_etapa_sem_data_real_nao_tem_variacao_calculavel():
    """Obra em andamento: sem Fim Real, a variação é `None` — nunca 0,
    que seria ler "no prazo" onde não há informação."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id, data_fim_prevista=date(2026, 4, 30))
    assert etapa.variacao_prazo_dias is None
    assert etapa.duracao_real_dias is None


def test_etapa_sem_nenhuma_data_nao_calcula_nada():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    assert etapa.duracao_prevista_dias is None
    assert etapa.duracao_real_dias is None
    assert etapa.variacao_prazo_dias is None


# ----------------------------------------------------------------------
# Duração e Variação de Prazo por SUBETAPA (campos novos na Etapa 8)
# ----------------------------------------------------------------------
def test_subetapa_agora_tem_datas_proprias():
    """SUBETAPAS não possuía nenhum campo de data antes da Etapa 8,
    embora UI_001 já previsse "datas previstas e reais das Etapas/
    Subetapas" na tela Cronograma da Obra."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    subetapa = _subetapa(
        base, etapa.id,
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 3, 15),
        data_inicio_real=date(2026, 3, 5), data_fim_real=date(2026, 3, 20),
    )
    assert subetapa.duracao_prevista_dias == 14
    assert subetapa.duracao_real_dias == 15
    assert subetapa.variacao_prazo_dias == 5


def test_subetapa_sem_datas_continua_valida():
    """Nenhum campo novo é obrigatório — Subetapas cadastradas antes da
    Etapa 8 (sem datas) continuam válidas, sem migração."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    subetapa = _subetapa(base, etapa.id)
    assert subetapa.data_inicio_prevista is None
    assert subetapa.duracao_prevista_dias is None
    assert base.subetapas[subetapa.id] is subetapa


# ----------------------------------------------------------------------
# Consolidação no nível da OBRA (MIN/MAX das Etapas)
# ----------------------------------------------------------------------
def test_consolidacao_da_obra_usa_menor_inicio_e_maior_fim():
    base = BaseDados()
    obra = _obra(base)
    _etapa(
        base, obra.id, nome="Fundação",
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
    )
    _etapa(
        base, obra.id, nome="Alvenaria",
        data_inicio_prevista=date(2026, 5, 1), data_fim_prevista=date(2026, 8, 31),
    )
    assert data_inicio_prevista_obra(base, obra.id) == date(2026, 3, 1)
    assert data_fim_prevista_obra(base, obra.id) == date(2026, 8, 31)
    assert duracao_prevista_obra_dias(base, obra.id) == 183


def test_consolidacao_da_obra_ignora_etapas_sem_data():
    """Etapa ainda sem data não zera nem invalida a consolidação — é
    simplesmente ignorada no MIN/MAX."""
    base = BaseDados()
    obra = _obra(base)
    _etapa(
        base, obra.id, nome="Fundação",
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
    )
    _etapa(base, obra.id, nome="Acabamento")  # sem nenhuma data
    assert data_inicio_prevista_obra(base, obra.id) == date(2026, 3, 1)
    assert data_fim_prevista_obra(base, obra.id) == date(2026, 4, 30)


def test_consolidacao_da_obra_sem_nenhuma_data_e_nao_calculavel():
    """Nunca inventa uma data (ex.: hoje ou 1900-01-00) quando não há
    nenhuma informada."""
    base = BaseDados()
    obra = _obra(base)
    _etapa(base, obra.id)
    assert data_inicio_prevista_obra(base, obra.id) is None
    assert data_fim_prevista_obra(base, obra.id) is None
    assert duracao_prevista_obra_dias(base, obra.id) is None


def test_consolidacao_de_obra_sem_etapas_e_nao_calculavel():
    base = BaseDados()
    obra = _obra(base)
    assert etapas_da_obra(base, obra.id) == []
    assert data_inicio_prevista_obra(base, obra.id) is None
    assert data_fim_real_obra(base, obra.id) is None


def test_consolidacao_de_datas_reais_da_obra():
    """As datas consolidadas continuam existindo (item 7 da decisão D1) —
    o que deixou de existir é a COMPARAÇÃO entre elas."""
    base = BaseDados()
    obra = _obra(base)
    _etapa(
        base, obra.id, nome="Fundação",
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
        data_inicio_real=date(2026, 3, 3), data_fim_real=date(2026, 5, 5),
    )
    _etapa(
        base, obra.id, nome="Alvenaria",
        data_inicio_prevista=date(2026, 5, 1), data_fim_prevista=date(2026, 8, 31),
        data_inicio_real=date(2026, 5, 6), data_fim_real=date(2026, 9, 10),
    )
    assert data_inicio_real_obra(base, obra.id) == date(2026, 3, 3)
    assert data_fim_real_obra(base, obra.id) == date(2026, 9, 10)
    assert duracao_prevista_obra_dias(base, obra.id) == 183


# ----------------------------------------------------------------------
# CENÁRIO 3 — regressão do indicador REMOVIDO (Alternativa D1, 2026-09-23)
# ----------------------------------------------------------------------
def test_cenario3_nenhuma_funcao_produz_o_resultado_enganoso_de_113_dias():
    """
    Cenário 3 preservado como regressão, com a finalidade redefinida pela
    decisão D1: em vez de provar que a supressão funciona, prova que o
    indicador consolidado NÃO EXISTE MAIS e que, portanto, o número
    enganoso de −113 dias é inalcançável por qualquer função do módulo.

    Obra com a Fundação concluída em 10/05 e a Alvenaria prevista para
    31/08 ainda em execução. `MAX(Fim Real) − MAX(Fim Previsto)` daria
    −113 dias, lido como "113 dias de antecipação" numa obra atrasada.
    """
    from src.planejamento import calculos

    base = BaseDados()
    obra = _obra(base)
    fundacao = _etapa(
        base, obra.id, nome="Fundação",
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
        data_inicio_real=date(2026, 3, 5), data_fim_real=date(2026, 5, 10),
    )
    alvenaria = _etapa(
        base, obra.id, nome="Alvenaria",
        data_inicio_prevista=date(2026, 5, 1), data_fim_prevista=date(2026, 8, 31),
        data_inicio_real=date(2026, 5, 11),  # começou, mas NÃO terminou
    )

    # (a) Nenhuma função pública do motor produz −113 (nem qualquer outra
    #     comparação entre Fim Real e Fim Previsto no nível da Obra).
    publicas = [
        getattr(calculos, nome) for nome in dir(calculos)
        if not nome.startswith("_") and callable(getattr(calculos, nome))
        and getattr(getattr(calculos, nome), "__module__", "") == calculos.__name__
    ]
    resultados = [f(base, obra.id) for f in publicas]
    assert -113 not in resultados
    assert all(r != -113 for r in resultados)

    # (b) O indicador consolidado e sua regra de supressão não existem.
    assert not hasattr(calculos, "variacao_prazo_obra_dias")
    assert not hasattr(calculos, "duracao_real_obra_dias")
    assert not hasattr(calculos, "ha_etapa_prevista_nao_concluida")

    # (c) A Fundação continua mostrando corretamente a SUA variação.
    assert fundacao.variacao_prazo_dias == 10  # 10/05 − 30/04 = 10 dias de atraso

    # (d) A Etapa em andamento não produz variação nenhuma — nem falsa,
    #     nem consolidada: sem Fim Real, é "não calculável" no próprio
    #     registro, que é onde o indicador tem significado definido.
    assert alvenaria.data_fim_real is None
    assert alvenaria.variacao_prazo_dias is None

    # (e) As datas consolidadas da Obra continuam disponíveis (item 7).
    assert data_fim_prevista_obra(base, obra.id) == date(2026, 8, 31)
    assert data_fim_real_obra(base, obra.id) == date(2026, 5, 10)


def test_contraexemplo_d2_prevista_sem_real_e_real_sem_prevista():
    """Contraexemplo da auditoria (defeito D-2), preservado: uma Etapa com
    Fim Previsto e sem Fim Real, e outra com Fim Real e sem Fim Previsto.
    Ele derrubava a fórmula baseada em contagens. Sem o indicador
    consolidado, o caso deixa de existir como risco — este teste prova
    que nenhuma comparação consolidada é produzida para esses dados."""
    from src.planejamento import calculos

    base = BaseDados()
    obra = _obra(base)
    a = _etapa(base, obra.id, nome="A", data_fim_prevista=date(2026, 4, 30))  # prevista, sem real
    b = _etapa(base, obra.id, nome="B", data_fim_real=date(2026, 5, 10))  # real, sem prevista

    assert not hasattr(calculos, "variacao_prazo_obra_dias")
    # Cada Etapa responde só pelo que tem — sem misturar operandos.
    assert a.variacao_prazo_dias is None  # falta Fim Real
    assert b.variacao_prazo_dias is None  # falta Fim Previsto
    # As datas consolidadas continuam corretas e vêm de Etapas distintas,
    # o que é exatamente o motivo de não existir subtração entre elas.
    assert data_fim_prevista_obra(base, obra.id) == date(2026, 4, 30)
    assert data_fim_real_obra(base, obra.id) == date(2026, 5, 10)


def test_datas_invertidas_na_etapa_nao_sao_bloqueadas():
    """A Nota de Implementação afirma que datas invertidas não são
    bloqueadas (REG-032, "o sistema informa, o Operador decide") — aqui
    isso é verificado na própria entidade, não só em `dias_entre`."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(
        base, obra.id,
        data_inicio_prevista=date(2026, 4, 30), data_fim_prevista=date(2026, 3, 1),
    )
    assert etapa.duracao_prevista_dias == -60  # negativa, informativa, não bloqueada
    assert base.etapas[etapa.id] is etapa  # registro aceito normalmente


def test_subetapa_sem_datas_reais_nao_calcula_duracao_real_nem_variacao():
    """Fecha a lacuna de cobertura apontada pela auditoria (M-3): só
    `duracao_prevista_dias` da Subetapa estava coberta."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    subetapa = _subetapa(
        base, etapa.id,
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 3, 15),
    )
    assert subetapa.duracao_prevista_dias == 14
    assert subetapa.duracao_real_dias is None
    assert subetapa.variacao_prazo_dias is None


def test_etapa_sem_datas_nao_afeta_a_consolidacao_nem_as_demais():
    """Uma Etapa sem nenhuma data não altera as datas consolidadas da
    Obra nem a variação das demais Etapas."""
    base = BaseDados()
    obra = _obra(base)
    fundacao = _etapa(
        base, obra.id, nome="Fundação",
        data_fim_prevista=date(2026, 4, 30), data_fim_real=date(2026, 5, 10),
        data_inicio_real=date(2026, 3, 5),
    )
    _etapa(base, obra.id, nome="Sem prazo definido")  # nenhuma data
    assert data_fim_prevista_obra(base, obra.id) == date(2026, 4, 30)
    assert data_fim_real_obra(base, obra.id) == date(2026, 5, 10)
    assert fundacao.variacao_prazo_dias == 10


def test_consolidacao_nao_mistura_obras_diferentes():
    base = BaseDados()
    obra_a = _obra(base)
    obra_b = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Outra Obra"))
    _etapa(base, obra_a.id, data_inicio_prevista=date(2026, 3, 1))
    _etapa(base, obra_b.id, nome="Etapa B", data_inicio_prevista=date(2025, 1, 1))
    assert data_inicio_prevista_obra(base, obra_a.id) == date(2026, 3, 1)
    assert data_inicio_prevista_obra(base, obra_b.id) == date(2025, 1, 1)


def test_consolidacao_da_obra_nao_sobrescreve_datas_declaradas_da_obra():
    """As datas próprias da Obra (digitadas pelo Operador) permanecem
    intocadas — a consolidação é um valor derivado, exposto ao lado,
    nunca uma automação que altera o que foi declarado (REG-032)."""
    base = BaseDados()
    obra = base.adicionar_obra(
        Obra(
            id=base.gerador_id.gerar("OBRAS"), nome="Obra",
            data_inicio=date(2026, 1, 1), data_prevista_termino=date(2026, 12, 31),
        )
    )
    _etapa(
        base, obra.id,
        data_inicio_prevista=date(2026, 3, 1), data_fim_prevista=date(2026, 4, 30),
    )
    assert data_inicio_prevista_obra(base, obra.id) == date(2026, 3, 1)  # derivado das Etapas
    assert obra.data_inicio == date(2026, 1, 1)  # declarado — inalterado
    assert obra.data_prevista_termino == date(2026, 12, 31)  # declarado — inalterado


# ----------------------------------------------------------------------
# Regressão — PLANEJAMENTO reservada e etapas anteriores intactas
# ----------------------------------------------------------------------
def test_entidade_planejamento_continua_registravel_mesmo_reservada():
    """A Opção A não apagou nada: a entidade e `adicionar_planejamento`
    (Etapa 1) continuam funcionando — apenas não são usadas como tabela
    do produto."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    item = base.adicionar_planejamento(
        Planejamento(
            id=base.gerador_id.gerar("PLANEJAMENTO"), id_etapa=etapa.id,
            data_inicio_prevista=date(2026, 3, 1),
        )
    )
    assert base.planejamentos[item.id] is item


def test_datas_nao_alteram_orcamento_execucao_nem_financeiro():
    """Cronograma é uma camada de datas independente — não toca em
    nenhum valor financeiro nem no progresso físico (mesmo princípio de
    separação conceitual de REG-021)."""
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id)
    subetapa = _subetapa(base, etapa.id)
    base.adicionar_servico(
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id,
            descricao="Chapisco", quantidade_orcada=1, valor_unitario=10_000,
            metodo_execucao=MetodoExecucao.STATUS, status_execucao=StatusExecucao.EM_ANDAMENTO,
        )
    )
    previsto_antes = total_previsto_obra(base, obra.id)
    execucao_antes = percentual_execucao_obra(base, obra.id)
    vigente_antes = orcamento_vigente(base, obra.id)
    caixa_antes = saldo_caixa(base, obra.id)

    etapa.data_inicio_prevista = date(2026, 3, 1)
    etapa.data_fim_real = date(2026, 12, 31)
    subetapa.data_inicio_prevista = date(2026, 3, 1)
    subetapa.data_fim_real = date(2026, 12, 31)

    assert total_previsto_obra(base, obra.id) == previsto_antes
    assert percentual_execucao_obra(base, obra.id) == execucao_antes
    assert orcamento_vigente(base, obra.id) == vigente_antes
    assert saldo_caixa(base, obra.id) == caixa_antes


def test_hierarquia_e_ids_permanecem_consistentes_com_datas():
    base = BaseDados()
    obra = _obra(base)
    etapa = _etapa(base, obra.id, data_inicio_prevista=date(2026, 3, 1))
    subetapa = _subetapa(base, etapa.id, data_inicio_prevista=date(2026, 3, 1))
    assert base.subetapas[subetapa.id].id_etapa == etapa.id
    assert base.etapas[etapa.id].id_obra == obra.id
    todos_os_ids = list(base.obras) + list(base.etapas) + list(base.subetapas)
    assert len(todos_os_ids) == len(set(todos_os_ids))
