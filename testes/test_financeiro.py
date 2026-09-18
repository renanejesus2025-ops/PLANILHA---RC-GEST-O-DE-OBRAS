"""
Testes do módulo FINANCEIRO (Etapa 4).

Cobre a entidade `Financeiro` estendida, a nova entidade `Pagamento`, o
Motor de Cálculos (`src/financeiro/calculos.py`) e os Cenários A–J da
Seção 34 da homologação.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroPagamentoDeTipoInvalido, ErroReferenciaInvalida, ErroValorNumericoInvalido
from src.financeiro.calculos import (
    a_pagar,
    custo_realizado,
    orcamento_vigente,
    percentual_orcamento_consumido,
    saldo_caixa,
    saldo_orcamentario,
    total_a_pagar_obra,
    total_aportes,
    total_entradas,
    total_outras_entradas,
    total_outras_saidas,
    total_pago,
    total_pago_obra,
    total_saidas,
)
from src.financeiro.movimentos import registrar_lancamento, registrar_pagamento
from src.modelo.entidades import Etapa, Financeiro, Obra, Pagamento, ServicoOrcamento, Subetapa
from src.modelo.enums import TipoLancamentoFinanceiro


def _obra_com_orcamento(base: BaseDados, valor_orcado: float) -> Obra:
    """Obra com um único Serviço orçado em `valor_orcado` (Orçamento Inicial)."""
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    if valor_orcado:
        base.adicionar_servico(
            ServicoOrcamento(
                id=gid.gerar("SERVICOS_ORCAMENTO"),
                id_subetapa=subetapa.id,
                descricao="Serviço",
                quantidade_orcada=1,
                valor_unitario=valor_orcado,
            )
        )
    return obra


def _lancar(base: BaseDados, id_obra: str, tipo: TipoLancamentoFinanceiro, valor: float, **kwargs) -> Financeiro:
    return registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"),
            id_obra=id_obra,
            tipo=tipo,
            data=date(2026, 9, 17),
            valor=valor,
            **kwargs,
        ),
    )


def _pagar(base: BaseDados, id_financeiro: str, valor: float) -> Pagamento:
    return registrar_pagamento(
        base,
        Pagamento(id=base.gerador_id.gerar("PAGAMENTOS"), id_financeiro=id_financeiro, data=date(2026, 9, 17), valor=valor),
    )


# --------------------------------------------------------------------
# Domínio "Tipo" (Seção 8) — 4 tipos homologados
# --------------------------------------------------------------------
def test_quatro_tipos_homologados_existem():
    assert {t.rotulo for t in TipoLancamentoFinanceiro} == {
        "Aporte",
        "Outras Entradas",
        "Despesa/Custo",
        "Outras Saídas",
    }


def test_apenas_aporte_aumenta_orcamento_vigente():
    for tipo in TipoLancamentoFinanceiro:
        esperado = tipo is TipoLancamentoFinanceiro.APORTE
        assert tipo.aumenta_orcamento_vigente is esperado


def test_apenas_despesa_e_custo_realizado():
    for tipo in TipoLancamentoFinanceiro:
        esperado = tipo is TipoLancamentoFinanceiro.DESPESA
        assert tipo.e_custo_realizado is esperado


# --------------------------------------------------------------------
# Seção 21 — valores negativos rejeitados (sinal vem do Tipo)
# --------------------------------------------------------------------
def test_valor_negativo_em_financeiro_e_rejeitado():
    with pytest.raises(ErroValorNumericoInvalido):
        Financeiro(id="FIN-0001", id_obra="OBR-0001", tipo=TipoLancamentoFinanceiro.APORTE, data=date(2026, 9, 17), valor=-10000)


def test_valor_negativo_em_pagamento_e_rejeitado():
    with pytest.raises(ErroValorNumericoInvalido):
        Pagamento(id="PGT-0001", id_financeiro="FIN-0001", data=date(2026, 9, 17), valor=-500)


# --------------------------------------------------------------------
# Seção 20 — Pagamento só pode referenciar Despesa/Custo existente
# --------------------------------------------------------------------
def test_pagamento_de_lancamento_inexistente_e_rejeitado():
    base = BaseDados()
    with pytest.raises(ErroReferenciaInvalida):
        registrar_pagamento(base, Pagamento(id="PGT-0001", id_financeiro="FIN-9999", data=date(2026, 9, 17), valor=100))


def test_pagamento_de_aporte_e_rejeitado():
    """Só existe 'pagamento' de uma Despesa/Custo — não de Aporte/Outras Entradas/Outras Saídas."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    aporte = _lancar(base, obra.id, TipoLancamentoFinanceiro.APORTE, 20000)
    with pytest.raises(ErroPagamentoDeTipoInvalido):
        registrar_pagamento(base, Pagamento(id="PGT-0001", id_financeiro=aporte.id, data=date(2026, 9, 17), valor=100))


# --------------------------------------------------------------------
# CENÁRIO A — Somente Orçamento
# --------------------------------------------------------------------
def test_cenario_a_somente_orcamento():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    assert orcamento_vigente(base, obra.id) == 100_000
    assert custo_realizado(base, obra.id) == 0
    assert saldo_orcamentario(base, obra.id) == 100_000
    assert percentual_orcamento_consumido(base, obra.id) == 0.0


# --------------------------------------------------------------------
# CENÁRIO B — Aporte
# --------------------------------------------------------------------
def test_cenario_b_aporte():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.APORTE, 20_000)
    assert orcamento_vigente(base, obra.id) == 120_000
    assert custo_realizado(base, obra.id) == 0  # aporte não entra em Custo Realizado


# --------------------------------------------------------------------
# CENÁRIO C — Despesa não paga
# --------------------------------------------------------------------
def test_cenario_c_despesa_nao_paga():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 10_000)
    assert custo_realizado(base, obra.id) == 10_000
    assert total_pago(base, despesa.id) == 0
    assert a_pagar(base, despesa.id) == 10_000
    assert saldo_orcamentario(base, obra.id) == 90_000
    # Caixa NÃO reduz pela despesa enquanto não houver pagamento:
    assert saldo_caixa(base, obra.id) == 0


# --------------------------------------------------------------------
# CENÁRIO D — Pagamento parcial
# --------------------------------------------------------------------
def test_cenario_d_pagamento_parcial():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 10_000)
    _pagar(base, despesa.id, 3_000)
    _pagar(base, despesa.id, 2_000)
    assert custo_realizado(base, obra.id) == 10_000
    assert total_pago(base, despesa.id) == 5_000
    assert a_pagar(base, despesa.id) == 5_000


# --------------------------------------------------------------------
# CENÁRIO E — Pagamento total
# --------------------------------------------------------------------
def test_cenario_e_pagamento_total():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 10_000)
    _pagar(base, despesa.id, 10_000)
    assert a_pagar(base, despesa.id) == 0


# --------------------------------------------------------------------
# CENÁRIO F — Estouro de orçamento (não bloqueia)
# --------------------------------------------------------------------
def test_cenario_f_estouro_de_orcamento():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 105_000)  # não deve levantar exceção
    assert saldo_orcamentario(base, obra.id) == -5_000
    assert percentual_orcamento_consumido(base, obra.id) == pytest.approx(105.0)


# --------------------------------------------------------------------
# CENÁRIO G — Outras Entradas
# --------------------------------------------------------------------
def test_cenario_g_outras_entradas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.APORTE, 20_000)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.OUTRAS_ENTRADAS, 5_000)
    assert orcamento_vigente(base, obra.id) == 20_000  # só o Aporte aumenta o Orçamento Vigente
    assert total_entradas(base, obra.id) == 25_000  # Caixa recebe as duas entradas
    assert total_outras_entradas(base, obra.id) == 5_000


# --------------------------------------------------------------------
# CENÁRIO H — Outras Saídas
# --------------------------------------------------------------------
def test_cenario_h_outras_saidas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.OUTRAS_SAIDAS, 3_000)
    assert saldo_caixa(base, obra.id) == -3_000
    assert custo_realizado(base, obra.id) == 0  # não se transforma em Custo Realizado
    assert total_outras_saidas(base, obra.id) == 3_000


# --------------------------------------------------------------------
# CENÁRIO I — Custo + Pagamento (parcial)
# --------------------------------------------------------------------
def test_cenario_i_custo_mais_pagamento():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 15_000)
    _pagar(base, despesa.id, 5_000)
    assert custo_realizado(base, obra.id) == 15_000
    assert total_pago(base, despesa.id) == 5_000
    assert a_pagar(base, despesa.id) == 10_000


# --------------------------------------------------------------------
# CENÁRIO J — Orçamento zero (divisão por zero tratada)
# --------------------------------------------------------------------
def test_cenario_j_orcamento_zero():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 1_000)
    assert orcamento_vigente(base, obra.id) == 0
    assert saldo_orcamentario(base, obra.id) == -1_000
    assert percentual_orcamento_consumido(base, obra.id) is None  # nunca 0% nem erro


# --------------------------------------------------------------------
# Saldo de Caixa consolidado (Seção 15) e A Pagar por Obra (Seção 14)
# --------------------------------------------------------------------
def test_saldo_de_caixa_entradas_menos_saidas_com_pagamento_e_outras_saidas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.APORTE, 50_000)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.OUTRAS_ENTRADAS, 1_000)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 20_000)
    _pagar(base, despesa.id, 12_000)
    _lancar(base, obra.id, TipoLancamentoFinanceiro.OUTRAS_SAIDAS, 500)

    assert total_entradas(base, obra.id) == 51_000
    assert total_saidas(base, obra.id) == 12_500  # 12.000 pago + 500 outras saídas
    assert saldo_caixa(base, obra.id) == 38_500


def test_total_a_pagar_obra_soma_multiplas_despesas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    d1 = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 10_000)
    d2 = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 5_000)
    _pagar(base, d1.id, 4_000)
    assert total_a_pagar_obra(base, obra.id) == 6_000 + 5_000
    assert total_pago_obra(base, obra.id) == 4_000


# --------------------------------------------------------------------
# Autonomia do Operador (Seção 22/23) — nenhum bloqueio de cancelamento
# --------------------------------------------------------------------
def test_situacao_e_texto_livre_e_nao_exclui_registro_dos_totais():
    """Seção 23: cancelamento não é transformado em exclusão; `situacao`
    continua [H] (texto livre) e não filtra os totais (ver docstring de
    `src/financeiro/calculos.py`)."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    despesa = _lancar(base, obra.id, TipoLancamentoFinanceiro.DESPESA, 1_000, situacao="Cancelado")
    assert despesa.id in base.financeiro
    assert custo_realizado(base, obra.id) == 1_000  # nenhum filtro por situação foi inventado
