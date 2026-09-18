"""
Orquestração de alto nível para registrar movimentações financeiras.

Mesmo raciocínio de `src/orcamento/servicos.py` (Etapa 3): `Financeiro`/
`Pagamento.__post_init__` já garantem, para QUALQUER instância criada,
que `valor` é numérico e não negativo (Etapa 4, Seção 21) — as funções
abaixo não repetem essa validação, apenas delegam para `BaseDados`, que
continua responsável exclusivamente pela integridade referencial
(Obra/Serviço/Fornecedor/Compra existentes; Pagamento só sobre
Despesa/Custo — Seções 13/14/20).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Financeiro, Pagamento


def registrar_lancamento(base: BaseDados, lancamento: Financeiro) -> Financeiro:
    """Registra uma movimentação financeira (Aporte/Outras Entradas/Despesa-Custo/Outras Saídas) já validada."""
    return base.adicionar_financeiro(lancamento)


def registrar_pagamento(base: BaseDados, pagamento: Pagamento) -> Pagamento:
    """Registra a baixa (parcial ou total) de um lançamento do tipo Despesa/Custo."""
    return base.adicionar_pagamento(pagamento)
