"""
Testes de integração da `BaseDados`: constrói a hierarquia oficial
completa (Obra → Etapa → Subetapa → Serviço) e valida unicidade de ID,
integridade referencial e o comportamento com as demais entidades.
"""

from __future__ import annotations

import pytest

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroIdDuplicado, ErroReferenciaInvalida
from src.modelo.entidades import (
    Compra,
    Etapa,
    Financeiro,
    Fornecedor,
    Obra,
    ServicoOrcamento,
    Subetapa,
)
from src.modelo.enums import TipoLancamentoFinanceiro
from datetime import date


def test_constroi_hierarquia_obra_etapa_subetapa_servico_end_to_end():
    base = BaseDados()

    obra = base.adicionar_obra(
        Obra(id=base.gerador_id.gerar("OBRAS"), nome="Residencial Jardim das Flores")
    )
    etapa = base.adicionar_etapa(
        Etapa(id=base.gerador_id.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria")
    )
    subetapa = base.adicionar_subetapa(
        Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Alvenaria interna")
    )
    servico = base.adicionar_servico(
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"),
            id_subetapa=subetapa.id,
            descricao="Reboco",
        )
    )

    assert base.obras[obra.id] is obra
    assert base.etapas[etapa.id] is etapa
    assert base.subetapas[subetapa.id] is subetapa
    assert base.servicos[servico.id] is servico
    assert servico.id_subetapa == subetapa.id
    assert subetapa.id_etapa == etapa.id
    assert etapa.id_obra == obra.id


def test_ids_unicos_id_duplicado_e_rejeitado():
    base = BaseDados()
    obra_id = base.gerador_id.gerar("OBRAS")
    base.adicionar_obra(Obra(id=obra_id, nome="Obra A"))
    with pytest.raises(ErroIdDuplicado):
        base.adicionar_obra(Obra(id=obra_id, nome="Obra A (duplicada)"))


def test_etapa_com_obra_inexistente_e_rejeitada():
    base = BaseDados()
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_etapa(Etapa(id="ETA-0001", id_obra="OBR-9999", nome="Alvenaria"))


def test_subetapa_com_etapa_inexistente_e_rejeitada():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra A"))
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_subetapa(
            Subetapa(id="SUB-0001", id_etapa="ETA-9999", nome="Alvenaria interna")
        )


def test_servico_com_subetapa_inexistente_e_rejeitado():
    base = BaseDados()
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_servico(
            ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-9999", descricao="Reboco")
        )


def test_compra_pode_referenciar_fornecedor_e_servico_existentes():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra A"))
    etapa = base.adicionar_etapa(Etapa(id=base.gerador_id.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(
        Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Alvenaria interna")
    )
    servico = base.adicionar_servico(
        ServicoOrcamento(id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Reboco")
    )
    fornecedor = base.adicionar_fornecedor(
        Fornecedor(id=base.gerador_id.gerar("FORNECEDORES"), nome_razao_social="Fornecedor ABC")
    )

    compra = base.adicionar_compra(
        Compra(
            id=base.gerador_id.gerar("COMPRAS"),
            id_obra=obra.id,
            id_fornecedor=fornecedor.id,
            id_servico=servico.id,
        )
    )
    assert base.compras[compra.id] is compra


def test_compra_com_fornecedor_inexistente_e_rejeitada():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra A"))
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_compra(
            Compra(id="COM-0001", id_obra=obra.id, id_fornecedor="FOR-9999")
        )


def test_financeiro_aporte_sem_vinculo_a_servico_e_permitido():
    """REG-021: aporte não precisa estar vinculado a um Serviço para existir
    em FINANCEIRO — o vínculo é o que decide se ele afeta o peso físico,
    não uma condição de existência do lançamento."""
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra A"))
    lancamento = base.adicionar_financeiro(
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"),
            id_obra=obra.id,
            tipo=TipoLancamentoFinanceiro.APORTE,
            data=date(2026, 9, 16),
            valor=50000.0,
        )
    )
    assert base.financeiro[lancamento.id] is lancamento
    assert lancamento.id_servico_vinculado is None


def test_financeiro_com_servico_vinculado_inexistente_e_rejeitado():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra A"))
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_financeiro(
            Financeiro(
                id="FIN-0001",
                id_obra=obra.id,
                tipo=TipoLancamentoFinanceiro.DESPESA,
                data=date(2026, 9, 16),
                valor=1000.0,
                id_servico_vinculado="SRV-9999",
            )
        )
