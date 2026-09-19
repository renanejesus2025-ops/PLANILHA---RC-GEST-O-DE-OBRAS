"""
Orquestração de alto nível para registrar uma Compra.

Mesmo raciocínio de `src/alteracoes/movimentos.py` (Etapa 5) e
`src/financeiro/movimentos.py` (Etapa 4): `Compra.__post_init__` já
garante que `valor` é numérico e não negativo (Etapa 6) — esta função
não repete a validação, só delega o registro para
`BaseDados.adicionar_compra` (Etapa 1, estendida na Etapa 6),
responsável pela integridade referencial (Obra/Fornecedor/Etapa/
Subetapa/Serviço, quando informados).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Compra


def registrar_compra(base: BaseDados, compra: Compra) -> Compra:
    """Registra uma Compra já validada (ver docstring do módulo) na base."""
    return base.adicionar_compra(compra)
