"""
Testes do gerador/validador de IDs técnicos internos.

Cobre os itens 1, 2 e 3 da lista de testes mínimos da Etapa 1:
1. geração de ID; 2. unicidade de ID; 3. formato de ID.
"""

from __future__ import annotations

import pytest

from src.excecoes import ErroFormatoIdInvalido, ErroPrefixoDesconhecido
from src.ids.gerador_id import GeradorId, eh_formato_de_id, obter_prefixo, validar_formato_id


def test_gera_id_com_prefixo_e_sequencial_homologados():
    gerador = GeradorId()
    assert gerador.gerar("OBRAS") == "OBR-0001"
    assert gerador.gerar("ETAPAS") == "ETA-0001"
    assert gerador.gerar("SUBETAPAS") == "SUB-0001"
    assert gerador.gerar("SERVICOS_ORCAMENTO") == "SRV-0001"


def test_gera_ids_sequenciais_e_estaveis_por_entidade():
    gerador = GeradorId()
    primeiro = gerador.gerar("ETAPAS")
    segundo = gerador.gerar("ETAPAS")
    terceiro = gerador.gerar("ETAPAS")
    assert [primeiro, segundo, terceiro] == ["ETA-0001", "ETA-0002", "ETA-0003"]


def test_ids_sao_unicos_mesmo_entre_entidades_diferentes():
    gerador = GeradorId()
    ids_gerados = {gerador.gerar("OBRAS"), gerador.gerar("ETAPAS"), gerador.gerar("SUBETAPAS")}
    assert len(ids_gerados) == 3  # nenhuma colisão


def test_contador_de_uma_entidade_nao_afeta_outra():
    gerador = GeradorId()
    gerador.gerar("ETAPAS")
    gerador.gerar("ETAPAS")
    assert gerador.gerar("SUBETAPAS") == "SUB-0001"


@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("OBR-0001", True),
        ("SRV-0042", True),
        ("srv-0042", False),  # minúsculo não é o formato homologado
        ("OBR0001", False),  # falta o hífen
        ("OBRA-0001", False),  # prefixo com 4 letras
        ("OBR-1", False),  # menos de 4 dígitos
        ("Alvenaria", False),  # nome amigável, não ID
    ],
)
def test_formato_de_id_e_reconhecido_corretamente(valor: str, esperado: bool):
    assert eh_formato_de_id(valor) is esperado


def test_validar_formato_id_aceita_id_valido_do_prefixo_correto():
    validar_formato_id("ETA-0007", entidade="ETAPAS")  # não deve levantar


def test_validar_formato_id_rejeita_formato_invalido():
    with pytest.raises(ErroFormatoIdInvalido):
        validar_formato_id("ETAPA-7")


def test_validar_formato_id_rejeita_prefixo_de_outra_entidade():
    with pytest.raises(ErroFormatoIdInvalido):
        validar_formato_id("SUB-0001", entidade="ETAPAS")


def test_obter_prefixo_de_entidade_desconhecida_levanta_erro():
    with pytest.raises(ErroPrefixoDesconhecido):
        obter_prefixo("ENTIDADE_INEXISTENTE")


def test_prefixos_homologados_explicitamente_na_etapa_1():
    """Os 11 prefixos citados literalmente na Seção 7 da homologação."""
    esperados = {
        "OBRAS": "OBR",
        "ETAPAS": "ETA",
        "SUBETAPAS": "SUB",
        "SERVICOS_ORCAMENTO": "SRV",
        "FINANCEIRO": "FIN",
        "COMPRAS": "COM",
        "EXECUCAO_MEDICOES": "EXE",
        "ALTERACOES": "ALT",
        "PENDENCIAS": "PEN",
        "ATUALIZACOES": "ATU",
        "DOCUMENTOS": "DOC",
    }
    for entidade, prefixo in esperados.items():
        assert obter_prefixo(entidade) == prefixo
