"""
Motor de Cálculos do módulo ALTERAÇÕES — Etapa 5.

Fecha REG-017 (Orçamento Vigente = Orçamento Inicial + Aportes +
Alterações Formais Aprovadas) — a única parcela que faltava desde a
Etapa 4, onde `orcamento_vigente` só somava Orçamento Inicial + Aportes
(ver `src/financeiro/calculos.py`, nota da Revisão 7 em REG-017).

Elegibilidade (Etapa 5, decisão homologada 2026-09-17; domínio de
Status CORRIGIDO na Etapa 5.1, 2026-09-19, para 4 valores): só
Alterações com `status_aprovacao == StatusAprovacaoAlteracao.APROVADA`
somam — Em análise, Rejeitada e Cancelada ficam visíveis na base,
nunca excluídas do repositório, apenas fora da soma (mesmo princípio
de não-exclusão já usado para `StatusServico`, Etapa 3, e para
`situacao` de FINANCEIRO, Etapa 4).

A soma é pelo campo `impacto_orcamento` (que pode ser negativo — uma
Alteração aprovada pode REDUZIR o orçamento), não pelo `tipo_alteracao`
— uma Alteração de Escopo também pode ter impacto financeiro.
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.enums import StatusAprovacaoAlteracao


def total_alteracoes_aprovadas(base: BaseDados, id_obra: str) -> float:
    """Σ Impacto no Orçamento das Alterações Aprovadas da Obra (REG-017)."""
    alteracoes = [
        a
        for a in base.alteracoes.values()
        if a.id_obra == id_obra
        and a.status_aprovacao is not None
        and a.status_aprovacao.integra_orcamento_vigente
    ]
    return sum((a.impacto_orcamento or 0.0) for a in alteracoes)
