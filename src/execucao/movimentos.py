"""
Orquestração de alto nível para registrar uma Medição de Execução.

Mesmo raciocínio de `src/compras/movimentos.py` (Etapa 6) e
`src/alteracoes/movimentos.py` (Etapa 5): `ExecucaoMedicao.__post_init__`
já garante que `quantidade_executada` é numérica e não negativa (Etapa 7)
— esta função não repete a validação, só delega o registro para
`BaseDados.adicionar_execucao` (Etapa 1), responsável pela integridade
referencial (Serviço deve existir).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import ExecucaoMedicao


def registrar_medicao(base: BaseDados, medicao: ExecucaoMedicao) -> ExecucaoMedicao:
    """Registra uma Medição já validada (ver docstring do módulo) na base."""
    return base.adicionar_execucao(medicao)
