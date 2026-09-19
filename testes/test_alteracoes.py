"""
Testes do módulo ALTERAÇÕES (Etapa 5).

Cobre o domínio fechado de Tipo/Status (REG-012 fechado nesta etapa), o
Motor de Cálculos (`src/alteracoes/calculos.py`) e a integração com
Orçamento Vigente (REG-017 completo).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.excecoes import ErroValorNumericoInvalido
from src.modelo.entidades import Alteracao
from src.modelo.enums import StatusAprovacaoAlteracao, TipoAlteracao


def test_tres_tipos_de_alteracao_homologados():
    assert {t.rotulo for t in TipoAlteracao} == {"Escopo", "Prazo", "Orçamento"}


def test_quatro_status_de_aprovacao_homologados():
    """Domínio corrigido na Etapa 5.1 (auditoria pós-Etapa 5): 4 valores, não 3."""
    assert {s.rotulo for s in StatusAprovacaoAlteracao} == {
        "Em análise", "Aprovada", "Rejeitada", "Cancelada",
    }


def test_apenas_status_aprovada_integra_orcamento_vigente():
    for status in StatusAprovacaoAlteracao:
        esperado = status is StatusAprovacaoAlteracao.APROVADA
        assert status.integra_orcamento_vigente is esperado


def test_impacto_no_orcamento_negativo_e_permitido():
    """Diferente de Financeiro (Etapa 4): o sinal aqui é significativo (redução de orçamento)."""
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Redução de escopo",
        tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=-5000,
        status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_orcamento == -5000


def test_impacto_no_prazo_negativo_e_permitido():
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Antecipação de prazo",
        tipo_alteracao=TipoAlteracao.PRAZO, impacto_prazo_dias=-10, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_prazo_dias == -10


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_impacto_no_orcamento_nao_numerico_e_rejeitado(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        Alteracao(
            id="ALT-0001", id_obra="OBR-0001", descricao="X",
            impacto_orcamento=valor_invalido, data=date(2026, 9, 17),
        )


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_impacto_no_prazo_nao_numerico_e_rejeitado(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        Alteracao(
            id="ALT-0001", id_obra="OBR-0001", descricao="X",
            impacto_prazo_dias=valor_invalido, data=date(2026, 9, 17),
        )


def test_alteracao_sem_impacto_informado_e_permitida():
    """Uma Alteração de Escopo pode não ter impacto financeiro nem de prazo (Seção informativa)."""
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Troca de acabamento",
        tipo_alteracao=TipoAlteracao.ESCOPO, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_orcamento is None
    assert alteracao.impacto_prazo_dias is None


from src.alteracoes.calculos import total_alteracoes_aprovadas
from src.alteracoes.movimentos import registrar_alteracao
from src.base_dados.repositorio import BaseDados
from src.financeiro.calculos import orcamento_vigente
from src.financeiro.movimentos import registrar_lancamento
from src.modelo.entidades import Etapa, Financeiro, Obra, ServicoOrcamento, Subetapa
from src.modelo.enums import TipoLancamentoFinanceiro


def _obra_com_orcamento(base: BaseDados, valor_orcado: float) -> Obra:
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    if valor_orcado:
        base.adicionar_servico(
            ServicoOrcamento(
                id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Serviço",
                quantidade_orcada=1, valor_unitario=valor_orcado,
            )
        )
    return obra


def _alterar(base: BaseDados, id_obra: str, *, impacto: float, status: StatusAprovacaoAlteracao) -> Alteracao:
    return registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=id_obra, descricao="Alteração",
            tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=impacto,
            status_aprovacao=status, data=date(2026, 9, 17),
        ),
    )


def test_soma_apenas_alteracoes_aprovadas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _alterar(base, obra.id, impacto=10_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.EM_ANALISE)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.REJEITADA)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.CANCELADA)
    assert total_alteracoes_aprovadas(base, obra.id) == 10_000


@pytest.mark.parametrize(
    "status",
    [
        StatusAprovacaoAlteracao.EM_ANALISE,
        StatusAprovacaoAlteracao.REJEITADA,
        StatusAprovacaoAlteracao.CANCELADA,
    ],
)
def test_status_nao_aprovada_nao_integra_orcamento_vigente(status):
    """Etapa 5.1 (Correção 7, itens 6/7/8): Em análise, Rejeitada e Cancelada
    individualmente não devem impactar o Orçamento Vigente."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    _alterar(base, obra.id, impacto=50_000, status=status)
    assert orcamento_vigente(base, obra.id) == 100_000


def test_alteracao_com_status_nao_aprovada_permanece_registrada_na_base():
    """Histórico preservado: Alteração não aprovada nunca é apagada (REG-012)."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    alteracao = _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.REJEITADA)
    assert alteracao.id in base.alteracoes
    assert base.alteracoes[alteracao.id].status_aprovacao is StatusAprovacaoAlteracao.REJEITADA


def test_alteracao_aprovada_com_impacto_negativo_reduz_a_soma():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _alterar(base, obra.id, impacto=10_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=-3_000, status=StatusAprovacaoAlteracao.APROVADA)
    assert total_alteracoes_aprovadas(base, obra.id) == 7_000


def test_alteracao_sem_impacto_no_orcamento_nao_afeta_a_soma():
    """Uma Alteração de Escopo/Prazo sem Impacto no Orçamento não soma nem falha."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Só prazo",
            tipo_alteracao=TipoAlteracao.PRAZO, impacto_prazo_dias=5,
            status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 17),
        ),
    )
    assert total_alteracoes_aprovadas(base, obra.id) == 0


def test_orcamento_vigente_completo_soma_inicial_aportes_e_alteracoes_aprovadas():
    """REG-017 completo: Orçamento Inicial + Aportes + Alterações Formais Aprovadas."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id, tipo=TipoLancamentoFinanceiro.APORTE,
            data=date(2026, 9, 17), valor=20_000,
        ),
    )
    _alterar(base, obra.id, impacto=15_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.EM_ANALISE)
    assert orcamento_vigente(base, obra.id) == 100_000 + 20_000 + 15_000
