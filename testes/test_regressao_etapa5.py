"""
Testes de regressão pós-Etapa 5 (Etapa 5.1, Correção 7 — itens 9, 10, 11).

A auditoria pré-Etapa 6 (AUD-26) encontrou que a suíte comprovava
Orçamento (Etapa 3), Financeiro (Etapa 4) e Alterações (Etapa 5)
isoladamente, mas nunca em conjunto: não havia nenhum teste que
registrasse Alterações e voltasse a chamar as funções de totais de
Orçamento (`src/orcamento/calculos.py`) para confirmar que continuam
corretas. Este arquivo fecha esse gap, e também comprova explicitamente
(item 9) que a regra de Valor Previsto por substituição (Opção C,
REG-026) continua intacta depois das correções desta etapa — ela NÃO
foi alterada, mas a auditoria pediu uma prova de regressão explícita.
"""

from __future__ import annotations

from datetime import date

from src.alteracoes.calculos import total_alteracoes_aprovadas
from src.alteracoes.movimentos import registrar_alteracao
from src.base_dados.repositorio import BaseDados
from src.financeiro.calculos import (
    a_pagar,
    custo_realizado,
    orcamento_vigente,
    percentual_orcamento_consumido,
    saldo_caixa,
    saldo_orcamentario,
)
from src.financeiro.movimentos import registrar_lancamento
from src.modelo.entidades import (
    Alteracao,
    Etapa,
    Financeiro,
    Obra,
    Pagamento,
    ServicoOrcamento,
    Subetapa,
)
from src.modelo.enums import StatusAprovacaoAlteracao, TipoAlteracao, TipoLancamentoFinanceiro
from src.orcamento.calculos import total_previsto_etapa, total_previsto_obra, total_previsto_subetapa


def _hierarquia_com_servico(base: BaseDados, *, quantidade: float, valor_unitario: float):
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    servico = base.adicionar_servico(
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Chapisco",
            quantidade_orcada=quantidade, valor_unitario=valor_unitario,
        )
    )
    return obra, etapa, subetapa, servico


# ----------------------------------------------------------------------
# Item 9 — Valor Previsto continua por SUBSTITUIÇÃO (Opção C), não soma
# ----------------------------------------------------------------------
def test_valor_previsto_continua_por_substituicao_nao_por_soma():
    """Correção 4 do plano de Etapa 5.1: NÃO alterar esta regra — este
    teste apenas comprova, depois das demais correções, que ela
    continua intacta: Valor Previsto = Valor Calculado OU (se houver
    Ajuste Manual) o valor manual — NUNCA Calculado + Ajuste."""
    base = BaseDados()
    _obra, _etapa, _subetapa, servico = _hierarquia_com_servico(base, quantidade=10, valor_unitario=100)
    assert servico.valor_calculado == 1_000
    assert servico.valor_previsto == 1_000  # sem ajuste: Previsto = Calculado

    servico.valor_previsto_manual = 1_500
    assert servico.valor_calculado == 1_000  # Calculado nunca é sobrescrito
    assert servico.valor_previsto == 1_500  # Previsto = o valor manual (substituição)
    assert servico.valor_previsto != servico.valor_calculado + 1_500  # NUNCA soma


# ----------------------------------------------------------------------
# Item 10 — Regressão das Etapas 1–4 após registrar Alterações (Etapa 5)
# ----------------------------------------------------------------------
def test_totais_de_orcamento_continuam_corretos_apos_registrar_alteracoes():
    """AUD-26: registra uma Alteração (Etapa 5) e reexecuta os totais de
    Orçamento (Etapa 3) — eles não devem ser afetados pela existência de
    Alterações, aprovadas ou não (Orçamento Previsto ≠ Orçamento Vigente)."""
    base = BaseDados()
    obra, etapa, subetapa, servico = _hierarquia_com_servico(base, quantidade=10, valor_unitario=1_000)

    assert total_previsto_subetapa(base, subetapa.id) == 10_000
    assert total_previsto_etapa(base, etapa.id) == 10_000
    assert total_previsto_obra(base, obra.id) == 10_000

    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Aumento de escopo",
            tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=50_000,
            status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 19),
        ),
    )

    # Os totais de Orçamento Previsto (Etapa 3) não mudam — Alterações
    # só entram no Orçamento Vigente (Etapa 5/REG-017), uma camada
    # diferente (ver item 11 abaixo).
    assert total_previsto_subetapa(base, subetapa.id) == 10_000
    assert total_previsto_etapa(base, etapa.id) == 10_000
    assert total_previsto_obra(base, obra.id) == 10_000


def test_hierarquia_e_ids_permanecem_consistentes_apos_alteracoes_e_financeiro():
    """Regressão das Etapas 1/2: a cadeia Obra→Etapa→Subetapa→Serviço e a
    unicidade dos IDs continuam íntegras mesmo com Financeiro e
    Alterações registrados por cima."""
    base = BaseDados()
    obra, etapa, subetapa, servico = _hierarquia_com_servico(base, quantidade=1, valor_unitario=1_000)
    registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id,
            tipo=TipoLancamentoFinanceiro.APORTE, data=date(2026, 9, 19), valor=5_000,
        ),
    )
    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Alteração",
            tipo_alteracao=TipoAlteracao.PRAZO, status_aprovacao=StatusAprovacaoAlteracao.CANCELADA,
            data=date(2026, 9, 19),
        ),
    )

    assert base.subetapas[subetapa.id].id_etapa == etapa.id
    assert base.servicos[servico.id].id_subetapa == subetapa.id
    assert base.etapas[etapa.id].id_obra == obra.id
    todos_os_ids = (
        list(base.obras) + list(base.etapas) + list(base.subetapas) + list(base.servicos)
        + list(base.financeiro) + list(base.alteracoes)
    )
    assert len(todos_os_ids) == len(set(todos_os_ids))  # nenhuma colisão entre entidades


# ----------------------------------------------------------------------
# Item 11 — Integração completa: Alterações → Orçamento → Financeiro
# ----------------------------------------------------------------------
def test_integracao_completa_alteracoes_orcamento_financeiro():
    """Cenário ponta a ponta cobrindo as Etapas 1 a 5 juntas: hierarquia,
    orçamento, aporte, despesa com pagamento parcial e uma alteração
    aprovada — confirma que Orçamento Vigente, Saldo Orçamentário, %
    Consumido, Saldo de Caixa e A Pagar continuam mutuamente coerentes."""
    base = BaseDados()
    obra, etapa, subetapa, servico = _hierarquia_com_servico(base, quantidade=1, valor_unitario=100_000)
    assert total_previsto_obra(base, obra.id) == 100_000

    registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id,
            tipo=TipoLancamentoFinanceiro.APORTE, data=date(2026, 9, 19), valor=20_000,
        ),
    )
    despesa = registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id,
            tipo=TipoLancamentoFinanceiro.DESPESA, data=date(2026, 9, 19),
            valor=30_000, descricao="Compra de material",
        ),
    )
    base.adicionar_pagamento(
        Pagamento(id=base.gerador_id.gerar("PAGAMENTOS"), id_financeiro=despesa.id, data=date(2026, 9, 19), valor=18_000)
    )
    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Ampliação de escopo",
            tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=15_000,
            status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 19),
        ),
    )
    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Pedido ainda não avaliado",
            tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=99_999,
            status_aprovacao=StatusAprovacaoAlteracao.EM_ANALISE, data=date(2026, 9, 19),
        ),
    )

    # Orçamento Vigente = Orçamento Previsto (Etapa 3) + Aportes + Alterações Aprovadas
    assert total_alteracoes_aprovadas(base, obra.id) == 15_000
    assert orcamento_vigente(base, obra.id) == 100_000 + 20_000 + 15_000  # 135_000
    assert custo_realizado(base, obra.id) == 30_000  # independe de pagamento (REG-004)
    assert saldo_orcamentario(base, obra.id) == 135_000 - 30_000  # 105_000
    assert percentual_orcamento_consumido(base, obra.id) == 30_000 / 135_000 * 100
    assert a_pagar(base, despesa.id) == 30_000 - 18_000  # 12_000
    # Saldo de Caixa = Entradas (Aporte) − Saídas (Pagamento) — a Despesa
    # reconhecida NÃO reduz o Caixa por si só (REG-018).
    assert saldo_caixa(base, obra.id) == 20_000 - 18_000  # 2_000
