"""
Geração e validação de IDs técnicos internos.

Fonte da regra: prompt de homologação "FUNDAÇÃO TÉCNICA — ETAPA 1"
(2026-09-16), Seção 7, e AGENTS.md §11 ("Código para a máquina. Nome
para o usuário.").

Os IDs gerados aqui são de uso exclusivamente interno/técnico. Nenhuma
camada de interface (fora do escopo desta etapa) deve exibi-los ao
Operador ou ao Cliente — `eh_formato_de_id` é o utilitário que essa
camada poderá usar para se proteger de exibir um ID por engano.
"""

from __future__ import annotations

import re

from config.ids_config import LARGURA_SEQUENCIAL, PREFIXOS_ID
from src.excecoes import ErroFormatoIdInvalido, ErroPrefixoDesconhecido

# Aceita 4+ dígitos: o formato homologado tem 4, mas o contador pode
# eventualmente ultrapassar 9999 (caso-limite não homologado — ver
# relatório da Etapa 1). O regex não trava esse caso, apenas o padrão
# "<3 letras>-<dígitos>".
_PADRAO_ID = re.compile(r"^[A-Z]{3}-\d{4,}$")


def obter_prefixo(entidade: str) -> str:
    """Retorna o prefixo homologado de 3 letras para o nome de entidade informado."""
    try:
        return PREFIXOS_ID[entidade.upper()]
    except KeyError as exc:
        raise ErroPrefixoDesconhecido(
            f"Entidade '{entidade}' não possui prefixo de ID configurado "
            "em config/ids_config.py."
        ) from exc


def eh_formato_de_id(valor: str) -> bool:
    """
    True se `valor` tem a forma de um ID técnico interno (ex.: "SRV-0001").

    Utilitário de proteção: a camada de interface (futura) pode usar esta
    função para garantir que nunca está prestes a exibir um ID técnico
    como se fosse um rótulo amigável (AGENTS.md §11).
    """
    return bool(_PADRAO_ID.match(valor))


def validar_formato_id(valor: str, entidade: str | None = None) -> None:
    """
    Levanta ErroFormatoIdInvalido se `valor` não for um ID técnico válido.

    Se `entidade` for informada, também valida que o prefixo de `valor`
    corresponde ao prefixo homologado daquela entidade.
    """
    if not eh_formato_de_id(valor):
        raise ErroFormatoIdInvalido(
            f"'{valor}' não corresponde ao padrão homologado "
            f"'<PREFIXO>-<{LARGURA_SEQUENCIAL} dígitos>'."
        )
    if entidade is not None:
        prefixo_esperado = obter_prefixo(entidade)
        if not valor.startswith(f"{prefixo_esperado}-"):
            raise ErroFormatoIdInvalido(
                f"'{valor}' não usa o prefixo '{prefixo_esperado}-' "
                f"esperado para a entidade '{entidade}'."
            )


class GeradorId:
    """
    Gera IDs sequenciais e estáveis por entidade.

    Cada instância mantém seus próprios contadores. Como a Seção 5 desta
    homologação define "1 arquivo Excel = 1 obra", uma instância de
    `GeradorId` por arquivo/obra é suficiente — não há necessidade de
    coordenar contadores entre obras nesta etapa.
    """

    def __init__(self) -> None:
        self._contadores: dict[str, int] = {}

    def gerar(self, entidade: str) -> str:
        """Gera o próximo ID técnico para a entidade informada.

        Exemplo: gerar("ETAPAS") -> "ETA-0001", depois "ETA-0002", ...
        """
        prefixo = obter_prefixo(entidade)
        proximo = self._contadores.get(prefixo, 0) + 1
        self._contadores[prefixo] = proximo
        return f"{prefixo}-{proximo:0{LARGURA_SEQUENCIAL}d}"

    def proximo_sequencial(self, entidade: str) -> int:
        """Consulta (sem consumir) qual seria o próximo número de sequência."""
        prefixo = obter_prefixo(entidade)
        return self._contadores.get(prefixo, 0) + 1
