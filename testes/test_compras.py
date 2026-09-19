"""
Testes do módulo COMPRAS (Etapa 6).

Cobre as regras homologadas no prompt "ETAPA 6 — COMPRAS", Seção 5:
compra sem fornecedor é permitida (regra 3); vínculos opcionais e
independentes a Etapa/Subetapa/Serviço (regras 5/6); nenhum efeito
automático em Financeiro/Orçamento/Execução (regras 2/7/8/9); compra
acima do previsto não bloqueia nem altera o orçamento automaticamente
(regras 10/11); Variação R$/% (regras 13-17); Compra distinta de Custo
Realizado/Pago/A Pagar/Saldo de Caixa (regra 18).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.base_dados.repositorio import BaseDados
from src.compras.calculos import planejado, variacao_percentual, variacao_reais
from src.compras.movimentos import registrar_compra
from src.excecoes import ErroReferenciaInvalida, ErroValorNumericoInvalido
from src.financeiro.calculos import custo_realizado, orcamento_vigente, saldo_caixa, saldo_orcamentario
from src.modelo.entidades import Compra, Etapa, Fornecedor, Obra, ServicoOrcamento, Subetapa
from src.orcamento.calculos import total_previsto_obra


def _obra_com_servico(base: BaseDados, *, valor_previsto: float = 1_000) -> tuple[Obra, Etapa, Subetapa, ServicoOrcamento]:
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Fundação"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Escavação"))
    servico = base.adicionar_servico(
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Cimento",
            quantidade_orcada=1, valor_unitario=valor_previsto,
        )
    )
    return obra, etapa, subetapa, servico


# ----------------------------------------------------------------------
# Regra 3 — Compra pode existir sem fornecedor cadastrado
# ----------------------------------------------------------------------
def test_compra_sem_fornecedor_e_permitida():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra"))
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Compra avulsa")
    )
    assert compra.id_fornecedor is None
    assert base.compras[compra.id] is compra


def test_compra_com_fornecedor_cadastrado_e_aceita():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra"))
    fornecedor = base.adicionar_fornecedor(
        Fornecedor(id=base.gerador_id.gerar("FORNECEDORES"), nome_razao_social="Fornecedor ABC")
    )
    compra = registrar_compra(
        base,
        Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Cimento", id_fornecedor=fornecedor.id),
    )
    assert compra.id_fornecedor == fornecedor.id


# ----------------------------------------------------------------------
# Regras 5/6 — vínculos opcionais e independentes a Etapa/Subetapa/Serviço
# ----------------------------------------------------------------------
def test_compra_vinculada_apenas_a_etapa_e_aceita():
    base = BaseDados()
    obra, etapa, _subetapa, _servico = _obra_com_servico(base)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item genérico", id_etapa=etapa.id)
    )
    assert compra.id_etapa == etapa.id
    assert compra.id_subetapa is None
    assert compra.id_servico is None


def test_compra_vinculada_apenas_a_subetapa_e_aceita():
    base = BaseDados()
    obra, _etapa, subetapa, _servico = _obra_com_servico(base)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_subetapa=subetapa.id)
    )
    assert compra.id_subetapa == subetapa.id


def test_compra_com_etapa_inexistente_e_rejeitada():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra"))
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_compra(
            Compra(id="COM-0001", id_obra=obra.id, descricao="Item", id_etapa="ETA-9999")
        )


def test_compra_com_subetapa_inexistente_e_rejeitada():
    base = BaseDados()
    obra = base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra"))
    with pytest.raises(ErroReferenciaInvalida):
        base.adicionar_compra(
            Compra(id="COM-0001", id_obra=obra.id, descricao="Item", id_subetapa="SUB-9999")
        )


def test_multiplos_itens_de_um_mesmo_pedido_sao_multiplos_registros_compra():
    """Regra 5: "múltiplos itens" = múltiplas linhas/registros Compra."""
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base)
    item1 = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item 1", id_servico=servico.id)
    )
    item2 = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item 2")
    )
    assert {item1.id, item2.id}.issubset(base.compras.keys())
    assert len(base.compras) == 2


# ----------------------------------------------------------------------
# Validação numérica (mesmo padrão de Financeiro/Pagamento)
# ----------------------------------------------------------------------
@pytest.mark.parametrize("valor_invalido", [-1, -0.01, "abc", True])
def test_valor_invalido_e_rejeitado(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        Compra(id="COM-0001", id_obra="OBR-0001", descricao="Item", valor=valor_invalido)


def test_valor_zero_e_permitido():
    compra = Compra(id="COM-0001", id_obra="OBR-0001", descricao="Item", valor=0)
    assert compra.valor == 0


# ----------------------------------------------------------------------
# Regras 13-17 — Variação R$ / Variação % (via Serviço vinculado)
# ----------------------------------------------------------------------
def test_planejado_e_o_valor_previsto_do_servico_vinculado():
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=1_000)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=1_200)
    )
    assert planejado(base, compra.id) == 1_000
    assert variacao_reais(base, compra.id) == 200  # 1200 - 1000 (regra 15)
    assert variacao_percentual(base, compra.id) == 20.0  # (1200-1000)/1000*100 (regra 16)


def test_compra_abaixo_do_previsto_gera_variacao_negativa():
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=1_000)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=800)
    )
    assert variacao_reais(base, compra.id) == -200
    assert variacao_percentual(base, compra.id) == -20.0


def test_compra_sem_servico_vinculado_nao_tem_planejado_nem_variacao():
    """Etapa/Subetapa vinculados são só rastreabilidade — não alimentam a Variação."""
    base = BaseDados()
    obra, etapa, subetapa, _servico = _obra_com_servico(base)
    compra = registrar_compra(
        base,
        Compra(
            id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item",
            id_etapa=etapa.id, id_subetapa=subetapa.id, valor=500,
        ),
    )
    assert planejado(base, compra.id) is None
    assert variacao_reais(base, compra.id) is None
    assert variacao_percentual(base, compra.id) is None


def test_planejado_zero_nao_calcula_variacao_percentual_nunca_zero_por_cento():
    """Regra 17: mesmo tratamento já homologado em REG-031 — 'N/D', nunca 0%."""
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=0)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=500)
    )
    assert planejado(base, compra.id) == 0
    assert variacao_reais(base, compra.id) == 500  # subtração simples continua válida
    assert variacao_percentual(base, compra.id) is None  # divisão por zero — não calculável


# ----------------------------------------------------------------------
# Regras 9/10/11/18 — compra não bloqueia nem altera Orçamento/Financeiro
# ----------------------------------------------------------------------
def test_compra_acima_do_previsto_nao_e_bloqueada():
    """Regra 10: nenhuma exceção é levantada por a Compra ultrapassar o Planejado."""
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=100)
    compra = registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=999_999)
    )
    assert compra.valor == 999_999  # registrado normalmente, sem bloqueio


def test_compra_nao_altera_orcamento_previsto_nem_vigente():
    """Regras 9/11: nenhuma automação Compra→Orçamento."""
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=1_000)
    total_antes = total_previsto_obra(base, obra.id)
    vigente_antes = orcamento_vigente(base, obra.id)
    saldo_antes = saldo_orcamentario(base, obra.id)

    registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=50_000)
    )

    assert total_previsto_obra(base, obra.id) == total_antes
    assert orcamento_vigente(base, obra.id) == vigente_antes
    assert saldo_orcamentario(base, obra.id) == saldo_antes


def test_compra_nao_cria_lancamento_financeiro_nem_altera_custo_ou_caixa():
    """Regras 2/18: Compra é distinta de Custo Realizado/Pago/A Pagar/Saldo de Caixa."""
    base = BaseDados()
    obra, _etapa, _subetapa, servico = _obra_com_servico(base, valor_previsto=1_000)
    assert len(base.financeiro) == 0

    registrar_compra(
        base, Compra(id=base.gerador_id.gerar("COMPRAS"), id_obra=obra.id, descricao="Item", id_servico=servico.id, valor=5_000)
    )

    assert len(base.financeiro) == 0  # nenhum lançamento financeiro criado automaticamente
    assert custo_realizado(base, obra.id) == 0
    assert saldo_caixa(base, obra.id) == 0
