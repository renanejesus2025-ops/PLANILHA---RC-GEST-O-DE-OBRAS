"""
Consolidação do orçamento previsto pela hierarquia oficial:

    SERVIÇO → SUBETAPA → ETAPA → OBRA   (REG-019)

O total em cada nível é a soma do **Valor Previsto** (não do Valor
Calculado) dos Serviços elegíveis — "elegível" aqui significa apenas
`servico.integra_orcamento_corrente` (Etapa 3, Seções 18/19): exclui
Cancelado, Retirado do Escopo e Substituído.

Deliberadamente FORA do escopo desta etapa (Seção 14): Aportes,
Alterações Aprovadas, Custo Realizado, Pagamentos, Saldo de Caixa —
nenhuma dessas camadas é somada aqui. Isto é só o orçamento previsto
dos serviços (REG-003), não o Orçamento Vigente/Disponível (REG-017).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import ServicoOrcamento


def _servicos_elegiveis(servicos) -> list[ServicoOrcamento]:
    return [s for s in servicos if s.integra_orcamento_corrente]


def total_previsto_subetapa(base: BaseDados, id_subetapa: str) -> float:
    """Σ Valor Previsto dos Serviços elegíveis vinculados a esta Subetapa."""
    servicos = [s for s in base.servicos.values() if s.id_subetapa == id_subetapa]
    return sum((s.valor_previsto or 0.0) for s in _servicos_elegiveis(servicos))


def total_previsto_etapa(base: BaseDados, id_etapa: str) -> float:
    """Σ Valor Previsto dos Serviços elegíveis de todas as Subetapas desta Etapa."""
    ids_subetapas = {s.id for s in base.subetapas.values() if s.id_etapa == id_etapa}
    servicos = [s for s in base.servicos.values() if s.id_subetapa in ids_subetapas]
    return sum((s.valor_previsto or 0.0) for s in _servicos_elegiveis(servicos))


def total_previsto_obra(base: BaseDados, id_obra: str) -> float:
    """Σ Valor Previsto dos Serviços elegíveis de toda a Obra (todas as Etapas/Subetapas)."""
    ids_etapas = {e.id for e in base.etapas.values() if e.id_obra == id_obra}
    ids_subetapas = {s.id for s in base.subetapas.values() if s.id_etapa in ids_etapas}
    servicos = [s for s in base.servicos.values() if s.id_subetapa in ids_subetapas]
    return sum((s.valor_previsto or 0.0) for s in _servicos_elegiveis(servicos))
