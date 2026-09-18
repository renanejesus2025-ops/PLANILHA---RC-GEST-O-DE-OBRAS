"""
Orquestração de alto nível para registrar uma Alteração.

Mesmo raciocínio de `src/orcamento/servicos.py` (Etapa 3) e
`src/financeiro/movimentos.py` (Etapa 4): `Alteracao.__post_init__` já
garante que `impacto_orcamento`/`impacto_prazo_dias` são numéricos
(Etapa 5) — esta função não repete a validação, só delega o registro
para `BaseDados.adicionar_alteracao` (Etapa 1), responsável pela
integridade referencial (Obra existente).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Alteracao


def registrar_alteracao(base: BaseDados, alteracao: Alteracao) -> Alteracao:
    """Registra uma Alteração já validada (ver docstring do módulo) na base."""
    return base.adicionar_alteracao(alteracao)
