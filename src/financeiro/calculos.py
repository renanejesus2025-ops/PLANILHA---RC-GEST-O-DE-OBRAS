"""
Motor de Cálculos do módulo FINANCEIRO — Etapa 4.

Fonte: prompt de homologação "FINANCEIRO — ETAPA 4" (2026-09-17).

Princípio central (Seção 2): **o sistema informa, o Operador decide** —
nenhuma função aqui bloqueia um estouro de orçamento ou satura um
percentual em 100%; elas apenas calculam e retornam o número real,
inclusive negativo (Saldo) ou acima de 100% (% Consumido).

Separação obrigatória (Seção 3) mantida nomeando cada função por
conceito, nunca misturando:

- ORÇAMENTO (Etapa 3: `src.orcamento.calculos`) × CAIXA (`saldo_caixa`);
- CUSTO REALIZADO (`custo_realizado`, reconhecimento) × PAGAMENTO
  (`total_pago`/`total_pago_obra`, baixa financeira);
- APORTE (`total_aportes`) × CUSTO (`custo_realizado`).

**Elegibilidade/filtro por Situação (Seção 22/23):** nenhuma função
abaixo exclui lançamentos por `Financeiro.situacao` — esse campo
permanece [H] (domínio de cancelamento não homologado), e excluir
registros com base num campo de texto livre seria inventar um domínio
fechado que a própria homologação pede para não inventar. Todos os
lançamentos/pagamentos registrados na Obra entram nos totais,
independentemente de `situacao`. Isto é uma pendência registrada no
relatório da Etapa 4, não uma omissão silenciosa.

**Orçamento Vigente (Seção 4):** = Orçamento Inicial (Etapa 3,
`total_previsto_obra`) + Aportes + Alterações Formais Aprovadas.

**Nota da Etapa 5:** a parcela de Alterações Formais Aprovadas, antes
deliberadamente ausente (Seção 4 da Etapa 4: "não inventar implementação
de Alterações", pois o módulo ainda não existia), foi implementada —
ver `src/alteracoes/calculos.py:total_alteracoes_aprovadas`. REG-017
está, a partir desta etapa, completamente implementado (3 parcelas).

**Divisão por zero (Seção 7):** `percentual_orcamento_consumido` retorna
`None` — não `0` — quando o Orçamento Vigente é zero, seguindo o mesmo
padrão já usado em `ServicoOrcamento.variacao` (Etapa 3) para "não
calculável". Nunca retorna `0%` como se fosse um cálculo válido.
"""

from __future__ import annotations

from typing import Optional

from src.alteracoes.calculos import total_alteracoes_aprovadas
from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Financeiro, Pagamento
from src.modelo.enums import TipoLancamentoFinanceiro
from src.orcamento.calculos import total_previsto_obra


# --------------------------------------------------------------------
# Auxiliares internos
# --------------------------------------------------------------------
def _lancamentos_da_obra(
    base: BaseDados, id_obra: str, tipo: TipoLancamentoFinanceiro | None = None
) -> list[Financeiro]:
    """Lançamentos FINANCEIRO da Obra informada, opcionalmente filtrados por Tipo."""
    itens = [f for f in base.financeiro.values() if f.id_obra == id_obra]
    if tipo is not None:
        itens = [f for f in itens if f.tipo is tipo]
    return itens


def pagamentos_do_lancamento(base: BaseDados, id_financeiro: str) -> list[Pagamento]:
    """Todos os Pagamentos (parciais e/ou totais) vinculados a um lançamento FINANCEIRO."""
    return [p for p in base.pagamentos.values() if p.id_financeiro == id_financeiro]


# --------------------------------------------------------------------
# Tipos de movimentação (Seções 9/10/11/12)
# --------------------------------------------------------------------
def total_aportes(base: BaseDados, id_obra: str) -> float:
    """Σ Valor dos lançamentos do tipo Aporte (Seção 9) — aumenta o Orçamento Vigente."""
    return sum(f.valor for f in _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.APORTE))


def total_outras_entradas(base: BaseDados, id_obra: str) -> float:
    """
    Σ Valor dos lançamentos do tipo Outras Entradas (Seção 10) — entra no
    Caixa, mas NÃO aumenta o Orçamento Vigente e NÃO é Custo Realizado.
    """
    return sum(
        f.valor for f in _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.OUTRAS_ENTRADAS)
    )


def custo_realizado(base: BaseDados, id_obra: str) -> float:
    """
    Σ Valor dos lançamentos do tipo Despesa/Custo (Seção 11/16) — o
    reconhecimento do custo, independentemente de estar pago.
    """
    return sum(f.valor for f in _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.DESPESA))


def total_outras_saidas(base: BaseDados, id_obra: str) -> float:
    """
    Σ Valor dos lançamentos do tipo Outras Saídas (Seção 12) — reduz o
    Caixa, mas NÃO é automaticamente Custo Realizado.
    """
    return sum(
        f.valor for f in _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.OUTRAS_SAIDAS)
    )


# --------------------------------------------------------------------
# Orçamento Vigente, Saldo Orçamentário, % Consumido (Seções 4/5/6/7)
# --------------------------------------------------------------------
def orcamento_vigente(base: BaseDados, id_obra: str) -> float:
    """
    ORÇAMENTO VIGENTE = ORÇAMENTO INICIAL (Etapa 3) + APORTES (Etapa 4)
    + ALTERAÇÕES FORMAIS APROVADAS (Etapa 5) — REG-017 completo.

    Antes da Etapa 5, esta função somava apenas as 2 primeiras parcelas
    (ver relatório da Etapa 4, "Limitações"/REG-017 nota da Revisão 7) —
    a parcela de Alterações estava preparada, mas não implementada.
    """
    return (
        total_previsto_obra(base, id_obra)
        + total_aportes(base, id_obra)
        + total_alteracoes_aprovadas(base, id_obra)
    )


def saldo_orcamentario(base: BaseDados, id_obra: str) -> float:
    """
    SALDO ORÇAMENTÁRIO = ORÇAMENTO VIGENTE − CUSTO REALIZADO (Seção 5).

    Pode ser negativo em caso de estouro de orçamento — não é bloqueado
    nem corrigido automaticamente (Seção 2/29, Cenário F).
    """
    return orcamento_vigente(base, id_obra) - custo_realizado(base, id_obra)


def percentual_orcamento_consumido(base: BaseDados, id_obra: str) -> Optional[float]:
    """
    % ORÇAMENTO CONSUMIDO = CUSTO REALIZADO / ORÇAMENTO VIGENTE × 100
    (Seção 6). Pode ultrapassar 100% (estouro, Cenário F) — nunca é
    limitado artificialmente.

    Retorna `None` ("não calculável", Seção 7) quando o Orçamento
    Vigente é zero — nunca `0%`, que seria uma leitura inválida do
    resultado de uma divisão por zero (Cenário J).
    """
    vigente = orcamento_vigente(base, id_obra)
    if vigente == 0:
        return None
    return custo_realizado(base, id_obra) / vigente * 100


# --------------------------------------------------------------------
# Pagamentos e A Pagar (Seções 13/14/20)
# --------------------------------------------------------------------
def total_pago(base: BaseDados, id_financeiro: str) -> float:
    """Σ Valor de todos os Pagamentos (parciais e/ou totais) de um lançamento."""
    return sum(p.valor for p in pagamentos_do_lancamento(base, id_financeiro))


def a_pagar(base: BaseDados, id_financeiro: str) -> float:
    """
    A PAGAR = CUSTO RECONHECIDO − TOTAL PAGO (Seção 14), para o
    lançamento FINANCEIRO informado (deve ser do tipo Despesa/Custo).
    """
    lancamento = base.financeiro[id_financeiro]
    return lancamento.valor - total_pago(base, id_financeiro)


def total_pago_obra(base: BaseDados, id_obra: str) -> float:
    """Σ Total Pago de todas as Despesas/Custos da Obra."""
    despesas = _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.DESPESA)
    return sum(total_pago(base, d.id) for d in despesas)


def total_a_pagar_obra(base: BaseDados, id_obra: str) -> float:
    """Σ A Pagar de todas as Despesas/Custos da Obra."""
    despesas = _lancamentos_da_obra(base, id_obra, TipoLancamentoFinanceiro.DESPESA)
    return sum(a_pagar(base, d.id) for d in despesas)


# --------------------------------------------------------------------
# Saldo de Caixa (Seção 15/16)
# --------------------------------------------------------------------
def total_entradas(base: BaseDados, id_obra: str) -> float:
    """Entradas de Caixa = Aportes + Outras Entradas (Seção 15)."""
    return total_aportes(base, id_obra) + total_outras_entradas(base, id_obra)


def total_saidas(base: BaseDados, id_obra: str) -> float:
    """
    Saídas de Caixa = Pagamentos + Outras Saídas (Seção 15) — NUNCA a
    Despesa/Custo em si (Seção 16: o reconhecimento do custo não reduz
    o Caixa sem pagamento).
    """
    return total_pago_obra(base, id_obra) + total_outras_saidas(base, id_obra)


def saldo_caixa(base: BaseDados, id_obra: str) -> float:
    """SALDO DE CAIXA = ENTRADAS − SAÍDAS (Seção 15)."""
    return total_entradas(base, id_obra) - total_saidas(base, id_obra)
