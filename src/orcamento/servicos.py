"""
Orquestração de alto nível para registrar um Serviço/Orçamento.

`ServicoOrcamento.__post_init__` (em `src/modelo/entidades.py`) já
garante, para QUALQUER instância criada, que Quantidade Orçada e Valor
Unitário são numéricos e não negativos (Etapa 3, Seções 8 e 9) —
`registrar_servico` não repete essa validação, apenas delega o registro
para `BaseDados.adicionar_servico` (Etapa 1), que continua responsável
exclusivamente pela integridade referencial/hierárquica (REG-019).

Esta função existe para dar um único ponto de entrada nomeado ao fluxo
"validar e registrar um Serviço", coerente com a separação de
responsabilidades pedida na Etapa 3 (Seção 26) — sem duplicar nem
substituir o que a Etapa 1 já fazia.
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import ServicoOrcamento


def registrar_servico(base: BaseDados, servico: ServicoOrcamento) -> ServicoOrcamento:
    """Registra um Serviço/Orçamento já validado (ver docstring do módulo) na base."""
    return base.adicionar_servico(servico)
