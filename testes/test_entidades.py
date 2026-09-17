"""
Testes unitários das entidades do modelo de dados e dos domínios
fechados já homologados (MetodoExecucao, StatusExecucao,
TipoLancamentoFinanceiro).
"""

from __future__ import annotations

from datetime import date

from src.modelo.entidades import Financeiro, ServicoOrcamento
from src.modelo.enums import MetodoExecucao, StatusExecucao, TipoLancamentoFinanceiro


def test_valor_calculado_e_none_sem_quantidade_ou_valor_unitario():
    servico = ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco")
    assert servico.valor_calculado is None


def test_valor_calculado_e_calculado_quando_ambos_informados():
    servico = ServicoOrcamento(
        id="SRV-0001",
        id_subetapa="SUB-0001",
        descricao="Reboco",
        quantidade_orcada=100.0,
        valor_unitario=25.5,
    )
    assert servico.valor_calculado == 2550.0


def test_metodo_execucao_quantitativo_e_status_sao_valores_distintos():
    assert MetodoExecucao.QUANTITATIVO != MetodoExecucao.STATUS


def test_status_execucao_tabela_fechada_homologada_rev5():
    """Pendente=0%, Em andamento=50%, Concluído=100% (REG-007, Revisão 5)."""
    assert StatusExecucao.PENDENTE.percentual == 0.0
    assert StatusExecucao.EM_ANDAMENTO.percentual == 50.0
    assert StatusExecucao.CONCLUIDO.percentual == 100.0


def test_servico_com_metodo_status_usa_status_execucao():
    servico = ServicoOrcamento(
        id="SRV-0002",
        id_subetapa="SUB-0001",
        descricao="Limpeza pós-obra",
        metodo_execucao=MetodoExecucao.STATUS,
        status_execucao=StatusExecucao.EM_ANDAMENTO,
    )
    assert servico.status_execucao.percentual == 50.0


def test_peso_automatico_original_e_preservado_junto_ao_peso_ajustado():
    """REG-008 (Revisão 5): o sistema deve preservar o peso automático
    original ao lado do peso ajustado manualmente."""
    servico = ServicoOrcamento(
        id="SRV-0003",
        id_subetapa="SUB-0001",
        descricao="Pintura externa",
        peso_automatico_original=0.12,
        peso_ajustado=0.20,
    )
    assert servico.peso_automatico_original == 0.12
    assert servico.peso_ajustado == 0.20


def test_lancamento_financeiro_aporte_nao_exige_servico_vinculado():
    """REG-021: aporte só afeta peso físico se vinculado a Serviço elegível,
    mas o vínculo é opcional (o aporte pode existir sem afetar o físico)."""
    lancamento = Financeiro(
        id="FIN-0001",
        id_obra="OBR-0001",
        tipo=TipoLancamentoFinanceiro.APORTE,
        data=date(2026, 9, 16),
        valor=50000.0,
    )
    assert lancamento.id_servico_vinculado is None
    assert lancamento.tipo is TipoLancamentoFinanceiro.APORTE
