"""
Testes do módulo de Orçamento (Etapa 3).

Cobre os itens 1–17 da Seção 27 (os itens 18–20, sobre o workbook em si,
estão em `testes/test_excel_construtor.py`) e os Cenários A–H da
Seção 29.
"""

from __future__ import annotations

import pytest

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroReferenciaInvalida, ErroValorNumericoInvalido
from src.ids.gerador_id import eh_formato_de_id
from src.modelo.entidades import Etapa, Obra, ServicoOrcamento, Subetapa
from src.modelo.enums import StatusServico
from src.orcamento.calculos import total_previsto_etapa, total_previsto_obra, total_previsto_subetapa
from src.orcamento.servicos import registrar_servico


def _construir_hierarquia(base: BaseDados, *, nome_etapa="Alvenaria", nome_subetapa="Reboco"):
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Residencial Jardim das Flores"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome=nome_etapa))
    subetapa = base.adicionar_subetapa(
        Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome=nome_subetapa)
    )
    return obra, etapa, subetapa


# --------------------------------------------------------------------
# 1. Quantidade × Valor Unitário calcula corretamente (Seção 10)
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "quantidade,valor_unitario,esperado",
    [(10, 100, 1000), (100, 50, 5000), (25, 12.50, 312.50)],
)
def test_valor_calculado_quantidade_vezes_valor_unitario(quantidade, valor_unitario, esperado):
    servico = ServicoOrcamento(
        id="SRV-0001",
        id_subetapa="SUB-0001",
        descricao="Serviço de teste",
        quantidade_orcada=quantidade,
        valor_unitario=valor_unitario,
    )
    assert servico.valor_calculado == esperado


# --------------------------------------------------------------------
# 2/5. Valor Calculado é preservado (antes e depois de um ajuste manual)
# --------------------------------------------------------------------
def test_valor_calculado_e_preservado_antes_do_ajuste():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco",
        quantidade_orcada=100, valor_unitario=50,
    )
    assert servico.valor_calculado == 5000


def test_valor_calculado_continua_preservado_apos_ajuste_manual():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco",
        quantidade_orcada=100, valor_unitario=50, valor_previsto_manual=5300,
    )
    assert servico.valor_calculado == 5000  # nunca sobrescrito (Seção 3)
    assert servico.valor_previsto == 5300


# --------------------------------------------------------------------
# 3. Sem ajuste manual, Valor Previsto = Valor Calculado
# --------------------------------------------------------------------
def test_sem_ajuste_manual_valor_previsto_igual_ao_calculado():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco",
        quantidade_orcada=100, valor_unitario=50,
    )
    assert servico.ajuste_manual is False
    assert servico.valor_previsto == servico.valor_calculado == 5000


# --------------------------------------------------------------------
# 4. Com ajuste manual, Valor Previsto usa o valor informado
# --------------------------------------------------------------------
def test_com_ajuste_manual_valor_previsto_usa_valor_informado():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco",
        quantidade_orcada=100, valor_unitario=50, valor_previsto_manual=5300,
    )
    assert servico.valor_previsto == 5300


# --------------------------------------------------------------------
# 6. Ajuste Manual pode ser identificado
# --------------------------------------------------------------------
def test_ajuste_manual_e_identificavel_como_sim_ou_nao():
    sem_ajuste = ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="A")
    com_ajuste = ServicoOrcamento(
        id="SRV-0002", id_subetapa="SUB-0001", descricao="B", valor_previsto_manual=100.0
    )
    assert sem_ajuste.ajuste_manual is False
    assert com_ajuste.ajuste_manual is True


# --------------------------------------------------------------------
# 7/8/9. Rejeição de quantidade negativa, valor unitário negativo e
# valores não numéricos (Seções 8 e 9)
# --------------------------------------------------------------------
def test_quantidade_negativa_e_rejeitada():
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="A", quantidade_orcada=-10)


def test_valor_unitario_negativo_e_rejeitado():
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="A", valor_unitario=-50)


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_valores_nao_numericos_sao_rejeitados_na_quantidade(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(
            id="SRV-0001", id_subetapa="SUB-0001", descricao="A", quantidade_orcada=valor_invalido
        )


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_valores_nao_numericos_sao_rejeitados_no_valor_unitario(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(
            id="SRV-0001", id_subetapa="SUB-0001", descricao="A", valor_unitario=valor_invalido
        )


def test_quantidade_zero_e_permitida():
    """Seção 8: 'permitir valores positivos e zero quando tecnicamente aplicável'."""
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="A", quantidade_orcada=0, valor_unitario=50
    )
    assert servico.valor_calculado == 0


def test_valor_unitario_zero_e_permitido():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="A", quantidade_orcada=10, valor_unitario=0
    )
    assert servico.valor_calculado == 0


# --------------------------------------------------------------------
# 10/11. Vínculo Serviço->Subetapa->Etapa é preservado
# --------------------------------------------------------------------
def test_servico_mantem_vinculo_com_subetapa():
    base = BaseDados()
    _obra, _etapa, subetapa = _construir_hierarquia(base)
    servico = registrar_servico(
        base,
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"),
            id_subetapa=subetapa.id,
            descricao="Reboco interno",
            quantidade_orcada=100,
            valor_unitario=50,
        ),
    )
    assert servico.id_subetapa == subetapa.id
    assert base.servicos[servico.id] is servico


def test_subetapa_mantem_vinculo_com_etapa():
    base = BaseDados()
    _obra, etapa, subetapa = _construir_hierarquia(base)
    assert subetapa.id_etapa == etapa.id


def test_servico_sem_subetapa_valida_e_rejeitado_pela_base():
    base = BaseDados()
    with pytest.raises(ErroReferenciaInvalida):
        registrar_servico(
            base, ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-9999", descricao="Inválido")
        )


# --------------------------------------------------------------------
# 12/13/14. Totais por Subetapa, Etapa e Obra (Seção 14, Cenários F/G/H)
# --------------------------------------------------------------------
def test_total_por_subetapa_e_consistente_cenario_f():
    """CENÁRIO F: dois serviços em uma Subetapa."""
    base = BaseDados()
    _obra, _etapa, subetapa = _construir_hierarquia(base)
    for descricao, quantidade, valor_unitario in [("Chapisco", 100, 12), ("Reboco", 100, 18)]:
        registrar_servico(
            base,
            ServicoOrcamento(
                id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"),
                id_subetapa=subetapa.id,
                descricao=descricao,
                quantidade_orcada=quantidade,
                valor_unitario=valor_unitario,
            ),
        )
    assert total_previsto_subetapa(base, subetapa.id) == 1200 + 1800


def test_total_por_etapa_e_consistente_cenario_g():
    """CENÁRIO G: duas Subetapas em uma Etapa."""
    base = BaseDados()
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    sub_a = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Chapisco"))
    sub_b = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    registrar_servico(
        base,
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=sub_a.id, descricao="Serviço A",
            quantidade_orcada=100, valor_unitario=10,
        ),
    )
    registrar_servico(
        base,
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=sub_b.id, descricao="Serviço B",
            quantidade_orcada=50, valor_unitario=20,
        ),
    )
    assert total_previsto_subetapa(base, sub_a.id) == 1000
    assert total_previsto_subetapa(base, sub_b.id) == 1000
    assert total_previsto_etapa(base, etapa.id) == 2000


def test_total_da_obra_e_consistente_cenario_h():
    """CENÁRIO H: múltiplas Etapas."""
    base = BaseDados()
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa_1 = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    etapa_2 = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Elétrica"))
    sub_1 = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa_1.id, nome="Reboco"))
    sub_2 = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa_2.id, nome="Fiação"))
    registrar_servico(
        base,
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=sub_1.id, descricao="Serviço A",
            quantidade_orcada=100, valor_unitario=10,
        ),
    )
    registrar_servico(
        base,
        ServicoOrcamento(
            id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=sub_2.id, descricao="Serviço B",
            quantidade_orcada=200, valor_unitario=5,
        ),
    )
    assert total_previsto_etapa(base, etapa_1.id) == 1000
    assert total_previsto_etapa(base, etapa_2.id) == 1000
    assert total_previsto_obra(base, obra.id) == 2000


def test_totais_usam_valor_previsto_nao_valor_calculado_quando_ha_ajuste():
    base = BaseDados()
    _obra, _etapa, subetapa = _construir_hierarquia(base)
    registrar_servico(
        base,
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id,
            descricao="Reboco", quantidade_orcada=100, valor_unitario=50,
            valor_previsto_manual=5300,
        ),
    )
    assert total_previsto_subetapa(base, subetapa.id) == 5300  # não 5000


# --------------------------------------------------------------------
# 15. Serviços fora da base ativa não entram no orçamento corrente
# (Seções 18/19)
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "status,esperado_incluido",
    [
        (None, True),
        (StatusServico.ATIVO, True),
        (StatusServico.CONCLUIDO, True),
        (StatusServico.CANCELADO, False),
        (StatusServico.RETIRADO_DO_ESCOPO, False),
        (StatusServico.SUBSTITUIDO, False),
    ],
)
def test_integra_orcamento_corrente_por_status(status, esperado_incluido):
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="A",
        quantidade_orcada=10, valor_unitario=10, status=status,
    )
    assert servico.integra_orcamento_corrente is esperado_incluido


def test_servico_cancelado_nao_entra_no_total_da_subetapa():
    base = BaseDados()
    _obra, _etapa, subetapa = _construir_hierarquia(base)
    registrar_servico(
        base,
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id,
            descricao="Serviço ativo", quantidade_orcada=100, valor_unitario=10,
            status=StatusServico.ATIVO,
        ),
    )
    registrar_servico(
        base,
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id,
            descricao="Serviço cancelado", quantidade_orcada=999, valor_unitario=999,
            status=StatusServico.CANCELADO,
        ),
    )
    # Só o serviço ativo (1000) deve entrar — o cancelado (998001) não.
    assert total_previsto_subetapa(base, subetapa.id) == 1000


def test_servico_nao_e_apagado_ao_ser_cancelado():
    """Seção 19: não apagar automaticamente registros — o serviço
    cancelado continua existindo na base, só não soma no total."""
    base = BaseDados()
    _obra, _etapa, subetapa = _construir_hierarquia(base)
    servico = registrar_servico(
        base,
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id,
            descricao="Serviço cancelado", quantidade_orcada=10, valor_unitario=10,
            status=StatusServico.CANCELADO,
        ),
    )
    assert servico.id in base.servicos
    assert base.servicos[servico.id].status is StatusServico.CANCELADO


# --------------------------------------------------------------------
# 16/17. IDs técnicos continuam internos; nomes amigáveis na interface
# --------------------------------------------------------------------
def test_id_tecnico_e_distinto_do_rotulo_amigavel_do_servico():
    servico = ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="Reboco interno")
    assert eh_formato_de_id(servico.id)
    assert not eh_formato_de_id(servico.descricao)


def test_status_amigavel_no_dropdown_nao_e_um_id_tecnico():
    for status in StatusServico:
        assert not eh_formato_de_id(status.rotulo)


# --------------------------------------------------------------------
# Cenários A–E da Seção 29 (F/G/H já cobertos acima)
# --------------------------------------------------------------------
def test_cenario_a_sem_ajuste_manual():
    servico = ServicoOrcamento(
        id="SRV-A", id_subetapa="SUB-0001", descricao="Cenário A",
        quantidade_orcada=100, valor_unitario=50,
    )
    assert servico.valor_calculado == 5000
    assert servico.valor_previsto == 5000
    assert servico.ajuste_manual is False


def test_cenario_b_com_ajuste_manual():
    servico = ServicoOrcamento(
        id="SRV-B", id_subetapa="SUB-0001", descricao="Cenário B",
        quantidade_orcada=100, valor_unitario=50, valor_previsto_manual=5300,
    )
    assert servico.valor_calculado == 5000
    assert servico.valor_previsto == 5300
    assert servico.ajuste_manual is True
    assert servico.variacao == 300


def test_cenario_c_quantidade_zero_nao_inventa_regra_adicional():
    """CENÁRIO C: Quantidade = 0, Valor Unitário = 50 — sem regra adicional
    além do que já está homologado: Valor Calculado = 0 × 50 = 0."""
    servico = ServicoOrcamento(
        id="SRV-C", id_subetapa="SUB-0001", descricao="Cenário C",
        quantidade_orcada=0, valor_unitario=50,
    )
    assert servico.valor_calculado == 0
    assert servico.valor_previsto == 0


def test_cenario_d_quantidade_negativa_e_rejeitada():
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(id="SRV-D", id_subetapa="SUB-0001", descricao="Cenário D", quantidade_orcada=-10)


def test_cenario_e_valor_unitario_negativo_e_rejeitado():
    with pytest.raises(ErroValorNumericoInvalido):
        ServicoOrcamento(id="SRV-E", id_subetapa="SUB-0001", descricao="Cenário E", valor_unitario=-50)


# --------------------------------------------------------------------
# Variação (Seção 13) — nome "Variação", nunca "Desvio"
# --------------------------------------------------------------------
def test_variacao_e_zero_quando_nao_ha_ajuste_manual():
    servico = ServicoOrcamento(
        id="SRV-0001", id_subetapa="SUB-0001", descricao="A",
        quantidade_orcada=100, valor_unitario=50,
    )
    assert servico.variacao == 0


def test_variacao_e_none_quando_faltam_dados_para_o_calculo():
    servico = ServicoOrcamento(id="SRV-0001", id_subetapa="SUB-0001", descricao="A")
    assert servico.variacao is None
