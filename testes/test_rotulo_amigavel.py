"""
Teste do item 8 da lista mínima da Etapa 1:
"garantia de que IDs técnicos não sejam usados como rótulos amigáveis."

Reforça AGENTS.md §11: "Código para a máquina. Nome para o usuário."
"""

from __future__ import annotations

import pytest

from src.excecoes import ErroHierarquiaInvalida
from src.hierarquia.validacoes import validar_nome_nao_e_id_tecnico
from src.ids.gerador_id import GeradorId
from src.modelo.entidades import Etapa, Obra, ServicoOrcamento, Subetapa


def test_nomes_amigaveis_reais_sao_aceitos():
    for nome in ["Fundação", "Alvenaria", "Elétrica", "Hidráulica", "Reboco", "Fornecedor ABC"]:
        validar_nome_nao_e_id_tecnico(nome)  # não deve levantar


@pytest.mark.parametrize("id_tecnico", ["ETA-0001", "SUB-0001", "SRV-0001", "OBR-0001"])
def test_ids_tecnicos_nao_podem_ser_usados_como_nome_amigavel(id_tecnico: str):
    with pytest.raises(ErroHierarquiaInvalida):
        validar_nome_nao_e_id_tecnico(id_tecnico)


def test_entidades_construidas_com_ids_gerados_mantem_nomes_amigaveis_distintos():
    """
    Constrói a cadeia Obra -> Etapa -> Subetapa -> Serviço com IDs gerados
    pelo GeradorId e garante que o `id` técnico de cada uma nunca é igual
    ao seu nome/rótulo amigável — ou seja, a camada de dados não confunde
    a chave técnica com o texto que a interface deveria exibir.
    """
    gerador = GeradorId()

    obra = Obra(id=gerador.gerar("OBRAS"), nome="Residencial Jardim das Flores")
    etapa = Etapa(id=gerador.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria")
    subetapa = Subetapa(id=gerador.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Alvenaria interna")
    servico = ServicoOrcamento(
        id=gerador.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Reboco"
    )

    for entidade, rotulo_amigavel in [
        (obra, obra.nome),
        (etapa, etapa.nome),
        (subetapa, subetapa.nome),
        (servico, servico.descricao),
    ]:
        assert entidade.id != rotulo_amigavel
        validar_nome_nao_e_id_tecnico(rotulo_amigavel)  # o rótulo real não "parece" um ID
