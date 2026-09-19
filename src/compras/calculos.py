"""
Motor de Cálculos do módulo COMPRAS — Etapa 6.

Compra é deliberadamente DISTINTA de Custo Realizado, Pago, A Pagar e
Saldo de Caixa (prompt de homologação "ETAPA 6 — COMPRAS", Seção 5,
regra 18) — nenhuma função aqui altera nenhum desses valores
(`src/financeiro/calculos.py` permanece intocado). Compra também não
altera o Orçamento Vigente nem o progresso físico (regras 7–9).

Único indicador calculado: a comparação entre o Valor da Compra e o
Planejado (Valor Previsto do Serviço vinculado, quando houver) —
Variação, nunca "Desvio" (regra 14, mesmo princípio já usado em
Orçamento/REG-028 e Alterações).

    Variação R$ = Compra − Planejado                    (regra 15)
    Variação %  = (Compra − Planejado) / Planejado × 100 (regra 16)

Uma Compra acima do Planejado NÃO é bloqueada nem corrigida
automaticamente (regras 10/11/19/20 — "o sistema informa, o Operador
decide", mesmo princípio já usado em REG-032/Estouro de Orçamento).

Planejado (regra 2 da decisão de design da Etapa 6): só existe quando a
Compra tem `id_servico` preenchido — os vínculos opcionais a Etapa/
Subetapa são puramente informativos/de rastreabilidade e não alimentam
este cálculo (não especificado pela homologação; evita inventar uma
regra de qual total usar quando só Etapa/Subetapa estão vinculados).

Planejado ausente OU igual a zero (regra 17): mesmo tratamento já
homologado para divisão por zero em `percentual_orcamento_consumido`
(REG-031) — Variação % retorna `None` ("não calculável"), nunca 0%.
Variação R$ também retorna `None` quando não há Planejado (uma
subtração contra "nada" não é um número válido).
"""

from __future__ import annotations

from typing import Optional

from src.base_dados.repositorio import BaseDados


def planejado(base: BaseDados, id_compra: str) -> Optional[float]:
    """Valor Previsto do Serviço vinculado à Compra, ou `None` se não houver vínculo."""
    compra = base.compras[id_compra]
    if compra.id_servico is None:
        return None
    servico = base.servicos.get(compra.id_servico)
    if servico is None:
        return None
    return servico.valor_previsto


def variacao_reais(base: BaseDados, id_compra: str) -> Optional[float]:
    """Variação R$ = Compra − Planejado (REG-010, regra 15). `None` sem Planejado."""
    compra = base.compras[id_compra]
    valor_planejado = planejado(base, id_compra)
    if valor_planejado is None or compra.valor is None:
        return None
    return compra.valor - valor_planejado


def variacao_percentual(base: BaseDados, id_compra: str) -> Optional[float]:
    """
    Variação % = Variação R$ / Planejado × 100 (regra 16). `None` quando
    não há Planejado ou quando Planejado = 0 (regra 17 — mesmo
    tratamento de REG-031, nunca 0%).
    """
    compra = base.compras[id_compra]
    valor_planejado = planejado(base, id_compra)
    if valor_planejado is None or compra.valor is None:
        return None
    if valor_planejado == 0:
        return None
    return (compra.valor - valor_planejado) / valor_planejado * 100
