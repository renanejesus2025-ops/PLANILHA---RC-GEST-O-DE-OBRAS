"""
Validação de campos numéricos não negativos.

Primeiro uso: Quantidade Orçada e Valor Unitário de SERVIÇOS/ORÇAMENTO
(Etapa 3, Seções 8 e 9) — "bloquear texto inválido, valores não
numéricos e quantidade/valor negativos; zero é permitido quando
aplicável". Colocado em um pacote genérico (`src/validacoes/`, não
`src/orcamento/`) porque a regra em si ("número, não negativo") não é
específica de orçamento — é uma validação de tipo/formato reutilizável
por qualquer campo numérico futuro que precisar da mesma garantia.
"""

from __future__ import annotations

from src.excecoes import ErroValorNumericoInvalido


def validar_numero_nao_negativo(valor: object, nome_campo: str) -> None:
    """
    Levanta `ErroValorNumericoInvalido` se `valor` não for None e:
    - não for um número (`int`/`float`, excluindo `bool`, que é
      tecnicamente uma subclasse de `int` em Python mas não representa
      uma quantidade/valor); ou
    - for negativo.

    `None` é sempre aceito (campo ainda não preenchido) — esta função
    não decide obrigatoriedade, apenas valida o valor quando presente.
    Zero é sempre aceito quando o valor é numérico.
    """
    if valor is None:
        return
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErroValorNumericoInvalido(
            f"{nome_campo} deve ser numérico; recebido: {valor!r}."
        )
    if valor < 0:
        raise ErroValorNumericoInvalido(
            f"{nome_campo} não pode ser negativo; recebido: {valor}."
        )


def validar_numero(valor: object, nome_campo: str) -> None:
    """
    Levanta `ErroValorNumericoInvalido` se `valor` não for None e não for
    um número (`int`/`float`, excluindo `bool`) — mesma exclusão de tipo
    de `validar_numero_nao_negativo`, mas SEM exigir não-negatividade.

    Usado por campos que são deltas com sinal significativo (Etapa 5,
    "Impacto no Orçamento"/"Impacto no Prazo" de ALTERAÇÕES) — uma
    Alteração pode reduzir o orçamento ou antecipar um prazo, então o
    sinal negativo é um dado válido, não um erro (diferente de
    `Financeiro.valor`/`Pagamento.valor`, Etapa 4, Seção 21, cujo sinal é
    dado pelo Tipo e por isso nunca pode ser negativo).

    `None` é sempre aceito (campo ainda não preenchido).
    """
    if valor is None:
        return
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErroValorNumericoInvalido(
            f"{nome_campo} deve ser numérico; recebido: {valor!r}."
        )
