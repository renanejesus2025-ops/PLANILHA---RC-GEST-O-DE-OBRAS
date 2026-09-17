"""
Configuração dos IDs técnicos internos.

Fonte: prompt de homologação "FUNDAÇÃO TÉCNICA — ETAPA 1" (2026-09-16),
Seção 7 ("IDS INTERNOS"), homologado pelo responsável pelo projeto (Renan).

Padrão homologado: "<PREFIXO>-<sequencial>", sequencial com largura mínima
de 4 dígitos, zero-padded (ex.: OBR-0001).

Os 11 prefixos abaixo foram informados **literalmente** na homologação:
OBR, ETA, SUB, SRV, FIN, COM, EXE, ALT, PEN, ATU, DOC.

PLANEJAMENTO e FORNECEDORES não constavam na lista literal, mas a própria
homologação instrui explicitamente: "Outras entidades devem seguir o
mesmo princípio." Os prefixos PLN (Planejamento) e FOR (Fornecedores)
foram **derivados** dessa regra explícita (3 letras maiúsculas, sem
colisão com os demais 11) — isto é uma aplicação da regra dada, não uma
regra de negócio nova. Recomenda-se confirmar esses dois prefixos
formalmente na próxima atualização do DAD_001 (ver relatório da Etapa 1).
"""

from __future__ import annotations

from typing import Final

# Nome de entidade (compatível com DAD_001 / Seção 9 desta homologação) -> prefixo.
PREFIXOS_ID: Final[dict[str, str]] = {
    "OBRAS": "OBR",
    "ETAPAS": "ETA",
    "SUBETAPAS": "SUB",
    "SERVICOS_ORCAMENTO": "SRV",
    "PLANEJAMENTO": "PLN",  # derivado — ver docstring acima
    "FORNECEDORES": "FOR",  # derivado — ver docstring acima
    "COMPRAS": "COM",
    "FINANCEIRO": "FIN",
    "EXECUCAO_MEDICOES": "EXE",
    "ALTERACOES": "ALT",
    "PENDENCIAS": "PEN",
    "ATUALIZACOES": "ATU",
    "DOCUMENTOS": "DOC",
}

# Largura mínima do sequencial numérico do ID (ex.: 4 -> "0001").
# Caso o contador ultrapasse 9999, o formato passará a ter mais dígitos;
# nenhuma decisão foi homologada sobre limitar/rejeitar esse caso-limite
# (ver relatório da Etapa 1, seção de pendências).
LARGURA_SEQUENCIAL: Final[int] = 4
