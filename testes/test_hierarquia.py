"""
Testes da hierarquia oficial homologada OBRA → ETAPA → SUBETAPA → SERVIÇO
(REG-019) e das validações estruturais de referência.

Cobre os itens 4, 5, 6 e 7 da lista mínima da Etapa 1:
4. relacionamento válido; 5. relacionamento inválido;
6. hierarquia Obra → Etapa → Subetapa → Serviço;
7. tentativa de referência inexistente.
"""

from __future__ import annotations

import pytest

from src.excecoes import ErroHierarquiaInvalida, ErroReferenciaInvalida
from src.hierarquia.validacoes import (
    validar_cadeia_obra_etapa_subetapa_servico,
    validar_prefixo_da_entidade,
    validar_referencia_existente,
)
from src.ids.gerador_id import GeradorId
from src.modelo.entidades import Etapa, Obra, Subetapa


def _construir_cadeia_valida(gerador: GeradorId | None = None):
    gerador = gerador or GeradorId()
    obra = Obra(id=gerador.gerar("OBRAS"), nome="Residencial Jardim das Flores")
    etapa = Etapa(id=gerador.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria")
    subetapa = Subetapa(id=gerador.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Alvenaria interna")
    return obra, etapa, subetapa


def test_relacionamento_valido_etapa_pertence_a_obra():
    obra, etapa, _ = _construir_cadeia_valida()
    assert etapa.id_obra == obra.id


def test_relacionamento_invalido_subetapa_com_etapa_de_outra_obra():
    """item 5: relacionamento inválido — Subetapa aponta para Etapa que não é filha da Obra informada."""
    gerador = GeradorId()  # compartilhado entre as duas obras, para garantir IDs distintos
    obra_1, etapa_1, _ = _construir_cadeia_valida(gerador)
    obra_2, etapa_2, subetapa_2 = _construir_cadeia_valida(gerador)

    obras = {obra_1.id: obra_1, obra_2.id: obra_2}
    etapas = {etapa_1.id: etapa_1, etapa_2.id: etapa_2}
    subetapas = {subetapa_2.id: subetapa_2}

    # subetapa_2 pertence a etapa_2 (que pertence a obra_2) — chamar a
    # validação afirmando que ela pertence a obra_1 deve falhar.
    with pytest.raises(ErroHierarquiaInvalida):
        validar_cadeia_obra_etapa_subetapa_servico(
            id_obra=obra_1.id,
            id_etapa=etapa_2.id,
            id_subetapa=subetapa_2.id,
            obras=obras,
            etapas=etapas,
            subetapas=subetapas,
        )


def test_hierarquia_completa_obra_etapa_subetapa_valida():
    """item 6: cadeia Obra -> Etapa -> Subetapa consistente não levanta erro."""
    obra, etapa, subetapa = _construir_cadeia_valida()
    validar_cadeia_obra_etapa_subetapa_servico(
        id_obra=obra.id,
        id_etapa=etapa.id,
        id_subetapa=subetapa.id,
        obras={obra.id: obra},
        etapas={etapa.id: etapa},
        subetapas={subetapa.id: subetapa},
    )  # não deve levantar


def test_referencia_para_obra_inexistente_e_rejeitada():
    """item 7: tentativa de referência inexistente."""
    with pytest.raises(ErroReferenciaInvalida):
        validar_referencia_existente("OBR-9999", {}, "OBRAS")


def test_referencia_para_etapa_inexistente_na_cadeia_e_rejeitada():
    obra, etapa, subetapa = _construir_cadeia_valida()
    with pytest.raises(ErroReferenciaInvalida):
        validar_cadeia_obra_etapa_subetapa_servico(
            id_obra=obra.id,
            id_etapa="ETA-9999",
            id_subetapa=subetapa.id,
            obras={obra.id: obra},
            etapas={etapa.id: etapa},
            subetapas={subetapa.id: subetapa},
        )


def test_validar_prefixo_da_entidade_aceita_prefixo_correto():
    validar_prefixo_da_entidade("SUB-0001", "SUBETAPAS")  # não deve levantar


def test_validar_prefixo_da_entidade_rejeita_prefixo_trocado():
    with pytest.raises(ErroHierarquiaInvalida):
        validar_prefixo_da_entidade("ETA-0001", "SUBETAPAS")
