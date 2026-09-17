"""
Validações estruturais da hierarquia oficial homologada:

    OBRA → ETAPA → SUBETAPA → SERVIÇO (REG-019, DAD_001)

Este módulo conhece apenas integridade referencial e nível hierárquico.
Não conhece o Motor de Cálculos (peso, % execução, saldo etc.) — isso
pertence a uma camada arquitetural separada, fora do escopo desta etapa.
"""

from __future__ import annotations

from typing import Mapping

from src.excecoes import ErroHierarquiaInvalida, ErroReferenciaInvalida
from src.ids.gerador_id import eh_formato_de_id, obter_prefixo


def validar_referencia_existente(
    id_referenciado: str, colecao: Mapping[str, object], nome_colecao: str
) -> None:
    """Levanta ErroReferenciaInvalida se `id_referenciado` não existir em `colecao`."""
    if id_referenciado not in colecao:
        raise ErroReferenciaInvalida(
            f"Referência inválida: '{id_referenciado}' não existe em {nome_colecao}."
        )


def validar_prefixo_da_entidade(id_valor: str, entidade: str) -> None:
    """Levanta ErroHierarquiaInvalida se o prefixo de `id_valor` não bater com `entidade`."""
    prefixo_esperado = obter_prefixo(entidade)
    if not id_valor.startswith(f"{prefixo_esperado}-"):
        raise ErroHierarquiaInvalida(
            f"'{id_valor}' não é um ID de {entidade} "
            f"(prefixo esperado '{prefixo_esperado}-')."
        )


def validar_nome_nao_e_id_tecnico(nome_amigavel: str) -> None:
    """
    Levanta ErroHierarquiaInvalida se um valor destinado a rótulo amigável
    tiver, na verdade, formato de ID técnico.

    Reforça AGENTS.md §11: "Código para a máquina. Nome para o usuário."
    """
    if eh_formato_de_id(nome_amigavel):
        raise ErroHierarquiaInvalida(
            f"'{nome_amigavel}' tem formato de ID técnico e não deve ser "
            "usado como nome/rótulo amigável."
        )


def validar_cadeia_obra_etapa_subetapa_servico(
    *,
    id_obra: str,
    id_etapa: str,
    id_subetapa: str,
    obras: Mapping[str, object],
    etapas: Mapping[str, object],
    subetapas: Mapping[str, object],
) -> None:
    """
    Valida a cadeia completa OBRA → ETAPA → SUBETAPA para um Serviço,
    conforme a hierarquia oficial homologada (REG-019).

    Não valida o Serviço em si (isso é feito no ponto de inserção do
    Serviço, via `BaseDados.adicionar_servico`) — apenas a consistência
    da cadeia de ancestrais informada.
    """
    validar_referencia_existente(id_obra, obras, "OBRAS")
    validar_referencia_existente(id_etapa, etapas, "ETAPAS")
    validar_referencia_existente(id_subetapa, subetapas, "SUBETAPAS")

    etapa = etapas[id_etapa]
    if getattr(etapa, "id_obra", None) != id_obra:
        raise ErroHierarquiaInvalida(
            f"Etapa '{id_etapa}' não pertence à Obra '{id_obra}' "
            "(hierarquia OBRA → ETAPA violada, REG-019)."
        )

    subetapa = subetapas[id_subetapa]
    if getattr(subetapa, "id_etapa", None) != id_etapa:
        raise ErroHierarquiaInvalida(
            f"Subetapa '{id_subetapa}' não pertence à Etapa '{id_etapa}' "
            "(hierarquia ETAPA → SUBETAPA violada, REG-019)."
        )
