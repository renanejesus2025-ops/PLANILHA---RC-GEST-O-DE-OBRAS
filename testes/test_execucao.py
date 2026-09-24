"""
Testes do módulo EXECUÇÃO/MEDIÇÕES (Etapa 7 — Progresso Físico).

Cobre as regras homologadas em REG_001: elegibilidade (REG-022), % de
Execução do Serviço por Método Quantitativo e por Status (REG-007), Peso
Automático Global (REG-008), Proteção do Peso Manual (REG-023),
Redistribuição Proporcional (REG-024), Bloqueio quando todos os
elegíveis têm peso manual (REG-025), consolidação até a Obra (REG-020),
e regressão: Execução não altera Orçamento/Financeiro/Compras (REG-021 —
Aporte não influencia peso físico automaticamente).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroDistribuicaoPesoInvalida, ErroReferenciaInvalida, ErroValorNumericoInvalido
from src.execucao.calculos import (
    contribuicao_etapa,
    contribuicao_subetapa,
    peso_automatico_bruto,
    peso_consolidado_etapa,
    peso_consolidado_subetapa,
    peso_efetivo_servico,
    pesos_efetivos_obra,
    percentual_execucao_obra,
    percentual_execucao_servico,
    quantidade_executada_acumulada,
    servico_elegivel_execucao,
    servicos_elegiveis_obra,
)
from src.execucao.movimentos import registrar_medicao
from src.financeiro.calculos import orcamento_vigente, saldo_orcamentario
from src.financeiro.movimentos import registrar_lancamento
from src.modelo.entidades import Etapa, ExecucaoMedicao, Financeiro, Obra, ServicoOrcamento, Subetapa
from src.modelo.enums import MetodoExecucao, StatusExecucao, StatusServico, TipoLancamentoFinanceiro
from src.orcamento.calculos import total_previsto_obra


def _hierarquia(base: BaseDados) -> tuple[Obra, Etapa, Subetapa]:
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    return obra, etapa, subetapa


def _servico(
    base: BaseDados,
    id_subetapa: str,
    *,
    quantidade: float = 10,
    valor_unitario: float = 100,
    metodo: MetodoExecucao | None = None,
    status_execucao: StatusExecucao | None = None,
    status: StatusServico | None = None,
    peso_ajustado: float | None = None,
    descricao: str = "Chapisco",
) -> ServicoOrcamento:
    return base.adicionar_servico(
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=id_subetapa, descricao=descricao,
            quantidade_orcada=quantidade, valor_unitario=valor_unitario,
            metodo_execucao=metodo, status_execucao=status_execucao, status=status,
            peso_ajustado=peso_ajustado,
        )
    )


# ----------------------------------------------------------------------
# Entidade / validação
# ----------------------------------------------------------------------
def test_quantidade_executada_negativa_e_rejeitada():
    with pytest.raises(ErroValorNumericoInvalido):
        ExecucaoMedicao(id="EXE-0001", id_servico="SRV-0001", data_medicao=date(2026, 9, 23), quantidade_executada=-1)


def test_quantidade_executada_zero_e_permitida():
    medicao = ExecucaoMedicao(id="EXE-0001", id_servico="SRV-0001", data_medicao=date(2026, 9, 23), quantidade_executada=0)
    assert medicao.quantidade_executada == 0


def test_registrar_medicao_rejeita_servico_inexistente():
    base = BaseDados()
    with pytest.raises(ErroReferenciaInvalida):
        registrar_medicao(
            base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico="SRV-9999", data_medicao=date(2026, 9, 23))
        )


# ----------------------------------------------------------------------
# REG-022 — Elegibilidade
# ----------------------------------------------------------------------
def test_servico_ativo_com_valor_previsto_e_elegivel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, status=StatusServico.ATIVO)
    assert servico_elegivel_execucao(base, servico.id) is True


def test_servico_cancelado_nao_e_elegivel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, status=StatusServico.CANCELADO)
    assert servico_elegivel_execucao(base, servico.id) is False


def test_servico_retirado_do_escopo_nao_e_elegivel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, status=StatusServico.RETIRADO_DO_ESCOPO)
    assert servico_elegivel_execucao(base, servico.id) is False


def test_servico_sem_status_e_elegivel_por_padrao():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, status=None)
    assert servico_elegivel_execucao(base, servico.id) is True


def test_servico_sem_valor_previsto_nao_e_elegivel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = base.adicionar_servico(
        ServicoOrcamento(id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Sem preço")
    )
    assert servico.valor_previsto is None
    assert servico_elegivel_execucao(base, servico.id) is False


# ----------------------------------------------------------------------
# REG-007 — % de Execução do Serviço
# ----------------------------------------------------------------------
def test_percentual_execucao_metodo_quantitativo():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, quantidade=10, metodo=MetodoExecucao.QUANTITATIVO)
    registrar_medicao(
        base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico=servico.id, data_medicao=date(2026, 9, 23), quantidade_executada=4)
    )
    assert percentual_execucao_servico(base, servico.id) == 40.0


def test_percentual_execucao_metodo_quantitativo_acumula_multiplas_medicoes():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, quantidade=10, metodo=MetodoExecucao.QUANTITATIVO)
    for quantidade in (2, 3, 1):
        registrar_medicao(
            base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico=servico.id, data_medicao=date(2026, 9, 23), quantidade_executada=quantidade)
        )
    assert quantidade_executada_acumulada(base, servico.id) == 6
    assert percentual_execucao_servico(base, servico.id) == 60.0


def test_percentual_execucao_quantitativo_pode_superar_100_sem_bloqueio():
    """REG-009: excedente não é bloqueado, apenas informado (mesma
    política de REG-010/REG-032)."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, quantidade=10, metodo=MetodoExecucao.QUANTITATIVO)
    registrar_medicao(
        base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico=servico.id, data_medicao=date(2026, 9, 23), quantidade_executada=15)
    )
    assert percentual_execucao_servico(base, servico.id) == 150.0


def test_percentual_execucao_quantitativo_sem_quantidade_orcada_e_nao_calculavel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = base.adicionar_servico(
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Sem quantidade",
            valor_unitario=100, metodo_execucao=MetodoExecucao.QUANTITATIVO,
        )
    )
    assert percentual_execucao_servico(base, servico.id) is None


@pytest.mark.parametrize(
    "status_execucao, esperado",
    [(StatusExecucao.PENDENTE, 0.0), (StatusExecucao.EM_ANDAMENTO, 50.0), (StatusExecucao.CONCLUIDO, 100.0)],
)
def test_percentual_execucao_metodo_status(status_execucao, esperado):
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, metodo=MetodoExecucao.STATUS, status_execucao=status_execucao)
    assert percentual_execucao_servico(base, servico.id) == esperado


def test_percentual_execucao_sem_metodo_definido_e_nao_calculavel():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, metodo=None)
    assert percentual_execucao_servico(base, servico.id) is None


# ----------------------------------------------------------------------
# REG-008 — Peso Automático Global
# ----------------------------------------------------------------------
def test_peso_automatico_soma_100_entre_elegiveis():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=300, descricao="A")
    s2 = _servico(base, subetapa.id, quantidade=1, valor_unitario=700, descricao="B")
    assert peso_automatico_bruto(base, s1.id) == pytest.approx(30.0)
    assert peso_automatico_bruto(base, s2.id) == pytest.approx(70.0)


def test_peso_automatico_e_global_nao_muda_ao_reorganizar_subetapa():
    """REG-008: o peso é o mesmo em qualquer nível — reorganizar um
    Serviço entre Subetapas não altera seu peso global."""
    base = BaseDados()
    obra, etapa, subetapa1 = _hierarquia(base)
    subetapa2 = base.adicionar_subetapa(Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Pintura"))
    s1 = _servico(base, subetapa1.id, quantidade=1, valor_unitario=500, descricao="A")
    s2 = _servico(base, subetapa2.id, quantidade=1, valor_unitario=500, descricao="B")
    peso_antes = peso_automatico_bruto(base, s1.id)
    s1.id_subetapa = subetapa2.id  # move para outra Subetapa
    assert peso_automatico_bruto(base, s1.id) == peso_antes == 50.0


def test_peso_automatico_ignora_servico_cancelado():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A")
    _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="B", status=StatusServico.CANCELADO)
    assert peso_automatico_bruto(base, s1.id) == 100.0  # único elegível


# ----------------------------------------------------------------------
# REG-023/024 — Proteção do Peso Manual + Redistribuição Proporcional
# ----------------------------------------------------------------------
def test_peso_manual_e_protegido_e_nao_e_alterado_pela_redistribuicao():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A", peso_ajustado=40.0)
    s2 = _servico(base, subetapa.id, quantidade=1, valor_unitario=300, descricao="B")
    s3 = _servico(base, subetapa.id, quantidade=1, valor_unitario=200, descricao="C")

    pesos = pesos_efetivos_obra(base, _obra.id)
    assert pesos[s1.id] == 40.0  # peso manual, protegido, inalterado
    # s2/s3 dividem os 60% restantes proporcionalmente aos seus pesos
    # automáticos brutos entre si (300:200 -> 60%:40% dos 60 pontos).
    assert pesos[s2.id] == pytest.approx(36.0)
    assert pesos[s3.id] == pytest.approx(24.0)
    assert sum(pesos.values()) == pytest.approx(100.0)


def test_alterar_valor_orcado_de_outro_servico_nao_afeta_peso_manual():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A", peso_ajustado=25.0)
    s2 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="B")

    assert pesos_efetivos_obra(base, _obra.id)[s1.id] == 25.0
    s2.valor_unitario = 999_999  # muda o valor orçado do outro serviço
    assert pesos_efetivos_obra(base, _obra.id)[s1.id] == 25.0  # continua protegido


def test_peso_efetivo_servico_conveniencia():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=1000)
    assert peso_efetivo_servico(base, s1.id) == 100.0


# ----------------------------------------------------------------------
# REG-025 — Bloqueio quando todos os elegíveis têm peso manual
# ----------------------------------------------------------------------
def test_bloqueia_quando_todos_manuais_somam_100():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A", peso_ajustado=60.0)
    s2 = _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="B", peso_ajustado=40.0)
    pesos = pesos_efetivos_obra(base, _obra.id)
    assert pesos[s1.id] == 60.0
    assert pesos[s2.id] == 40.0


def test_bloqueia_quando_todos_manuais_nao_somam_100():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A", peso_ajustado=60.0)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="B", peso_ajustado=30.0)
    with pytest.raises(ErroDistribuicaoPesoInvalida):
        pesos_efetivos_obra(base, _obra.id)


def test_evento_que_desbalanceia_peso_manual_total_dispara_bloqueio():
    """Cenário do teste necessário de REG-025: novo Serviço elegível 100%
    manual força a soma a deixar de totalizar 100%."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="A", peso_ajustado=100.0)
    assert pesos_efetivos_obra(base, _obra.id)  # ainda ok: soma = 100
    _servico(base, subetapa.id, quantidade=1, valor_unitario=500, descricao="B", peso_ajustado=20.0)
    with pytest.raises(ErroDistribuicaoPesoInvalida):
        pesos_efetivos_obra(base, _obra.id)


# ----------------------------------------------------------------------
# REG-020 — Consolidação até a Obra
# ----------------------------------------------------------------------
def test_percentual_execucao_obra_consolida_pesos_e_percentuais():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    s1 = _servico(base, subetapa.id, quantidade=1, valor_unitario=300, descricao="A", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.CONCLUIDO)
    s2 = _servico(base, subetapa.id, quantidade=1, valor_unitario=700, descricao="B", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.PENDENTE)
    # peso: 30% / 70%; % exec: 100% / 0% -> 30%*1 + 70%*0 = 30%
    assert percentual_execucao_obra(base, _obra.id) == pytest.approx(30.0)


def test_percentual_execucao_obra_trata_servico_sem_medicao_como_zero():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=1000, metodo=None)  # sem % calculável
    assert percentual_execucao_obra(base, _obra.id) == 0.0


def test_percentual_execucao_obra_100_quando_tudo_concluido():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=400, descricao="A", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.CONCLUIDO)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=600, descricao="B", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.CONCLUIDO)
    assert percentual_execucao_obra(base, _obra.id) == pytest.approx(100.0)


def test_percentual_execucao_obra_none_sem_servico_elegivel():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra vazia"))
    assert percentual_execucao_obra(base, obra.id) is None
    assert servicos_elegiveis_obra(base, obra.id) == []


def test_contribuicao_e_peso_consolidado_por_grupo():
    base = BaseDados()
    obra, etapa, subetapa1 = _hierarquia(base)
    subetapa2 = base.adicionar_subetapa(Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Pintura"))
    _servico(base, subetapa1.id, quantidade=1, valor_unitario=500, descricao="A", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.CONCLUIDO)
    _servico(base, subetapa2.id, quantidade=1, valor_unitario=500, descricao="B", metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.PENDENTE)

    assert peso_consolidado_subetapa(base, subetapa1.id) == pytest.approx(50.0)
    assert contribuicao_subetapa(base, subetapa1.id) == pytest.approx(50.0)  # 50% peso * 100% exec
    assert contribuicao_subetapa(base, subetapa2.id) == pytest.approx(0.0)  # 50% peso * 0% exec

    assert peso_consolidado_etapa(base, etapa.id) == pytest.approx(100.0)
    assert contribuicao_etapa(base, etapa.id) == pytest.approx(50.0)


# ----------------------------------------------------------------------
# Regressão — Execução não altera Orçamento/Financeiro (REG-021)
# ----------------------------------------------------------------------
def test_execucao_nao_altera_orcamento_previsto():
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id, quantidade=10, valor_unitario=1_000, metodo=MetodoExecucao.QUANTITATIVO)
    previsto_antes = total_previsto_obra(base, _obra.id)
    registrar_medicao(
        base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico=servico.id, data_medicao=date(2026, 9, 23), quantidade_executada=5)
    )
    assert total_previsto_obra(base, _obra.id) == previsto_antes


def test_aporte_financeiro_nao_altera_peso_fisico_automaticamente():
    """REG-021: aporte sem vínculo com Serviço não deve alterar o
    progresso físico da Obra."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    _servico(base, subetapa.id, quantidade=1, valor_unitario=1_000, metodo=MetodoExecucao.STATUS, status_execucao=StatusExecucao.EM_ANDAMENTO)
    percentual_antes = percentual_execucao_obra(base, _obra.id)

    registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=_obra.id,
            tipo=TipoLancamentoFinanceiro.APORTE, data=date(2026, 9, 23), valor=50_000,
        ),
    )
    assert percentual_execucao_obra(base, _obra.id) == percentual_antes
    assert orcamento_vigente(base, _obra.id) == 1_000 + 50_000  # Aporte segue afetando o Orçamento Vigente normalmente
    assert saldo_orcamentario(base, _obra.id) == 1_000 + 50_000  # nenhum custo lançado


def test_hierarquia_e_ids_permanecem_consistentes_apos_execucao():
    base = BaseDados()
    obra, etapa, subetapa = _hierarquia(base)
    servico = _servico(base, subetapa.id)
    medicao = registrar_medicao(
        base, ExecucaoMedicao(id=base.gerador_id.gerar("EXECUCAO_MEDICOES"), id_servico=servico.id, data_medicao=date(2026, 9, 23), quantidade_executada=1)
    )
    assert base.execucoes[medicao.id].id_servico == servico.id
    todos_os_ids = (
        list(base.obras) + list(base.etapas) + list(base.subetapas) + list(base.servicos) + list(base.execucoes)
    )
    assert len(todos_os_ids) == len(set(todos_os_ids))


# ----------------------------------------------------------------------
# D-COM-2 (Etapa 8.2) — base proporcional zero: Python × Excel equivalentes
# ----------------------------------------------------------------------
def test_peso_efetivo_divide_igualmente_quando_todos_elegiveis_tem_valor_zero():
    """Ramo `total_bruto_automaticos == 0` de `pesos_efetivos_obra`
    (Etapa 7): sem base proporcional, a faixa é dividida igualmente.
    Cobre o cenário que, no Excel, produzia `#DIV/0!` até a Etapa 8.2."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    a = _servico(base, subetapa.id, quantidade=0, valor_unitario=0, descricao="A")
    b = _servico(base, subetapa.id, quantidade=0, valor_unitario=0, descricao="B")
    assert peso_automatico_bruto(base, a.id) is None  # não calculável (denominador zero)
    pesos = pesos_efetivos_obra(base, _obra.id)
    assert pesos[a.id] == pytest.approx(50.0)
    assert pesos[b.id] == pytest.approx(50.0)
    assert sum(pesos.values()) == pytest.approx(100.0)


def test_peso_manual_convive_com_base_zero_sem_quebrar_a_soma():
    """Peso manual protegido (REG-023) + automáticos sem base
    proporcional: os automáticos dividem igualmente a faixa restante."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    manual = _servico(base, subetapa.id, quantidade=0, valor_unitario=0, descricao="Manual", peso_ajustado=25.0)
    auto = _servico(base, subetapa.id, quantidade=0, valor_unitario=0, descricao="Auto")
    pesos = pesos_efetivos_obra(base, _obra.id)
    assert pesos[manual.id] == 25.0  # protegido
    assert pesos[auto.id] == pytest.approx(75.0)
    assert sum(pesos.values()) == pytest.approx(100.0)


def test_servico_com_valor_zero_ao_lado_de_positivo_recebe_peso_zero():
    """Com base proporcional válida, o serviço orçado em zero recebe peso
    zero — e não aciona o ramo de divisão igualitária."""
    base = BaseDados()
    _obra, _etapa, subetapa = _hierarquia(base)
    zero = _servico(base, subetapa.id, quantidade=0, valor_unitario=0, descricao="Zero")
    positivo = _servico(base, subetapa.id, quantidade=1, valor_unitario=1000, descricao="Positivo")
    pesos = pesos_efetivos_obra(base, _obra.id)
    assert pesos[zero.id] == pytest.approx(0.0)
    assert pesos[positivo.id] == pytest.approx(100.0)
