"""
Testes da aba Execução e das colunas de Execução Física acrescentadas à
aba Serviços (Etapa 7).

Mesmo raciocínio de `testes/test_excel_compras.py` (Etapa 6): sem motor
de planilha neste ambiente — verificação pelo TEXTO da fórmula.
"""

from __future__ import annotations

import openpyxl
from openpyxl.utils import get_column_letter

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import (
    COL_EXE_SERVICO,
    COL_SRV_CONTRIBUICAO,
    COL_SRV_METODO_EXECUCAO,
    COL_SRV_PERCENTUAL_EXECUCAO,
    COL_SRV_PESO_AJUSTADO,
    COL_SRV_PESO_AUTOMATICO,
    COL_SRV_PESO_EFETIVO,
    COL_SRV_QTD_EXECUTADA_ACUM,
    COL_SRV_STATUS_EXECUCAO,
    COLUNAS_EXECUCAO,
    COLUNAS_SERVICOS,
    construir_workbook,
)


def test_aba_execucao_existe(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    wb = openpyxl.load_workbook(caminho)
    assert "Execução" in wb.sheetnames


def test_cabecalho_da_aba_execucao(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Execução"]
    titulos_esperados = [titulo for titulo, _l, _o, _c in COLUNAS_EXECUCAO]
    titulos_no_arquivo = [ws.cell(row=1, column=i + 1).value for i in range(len(COLUNAS_EXECUCAO))]
    assert titulos_no_arquivo == titulos_esperados


def test_aba_execucao_e_uma_tabela_estruturada_sem_range_fixo(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Execução"]
    tabela = ws.tables["TabelaExecucao"]
    assert tabela.ref == f"A1:F{1 + 30}"  # cabeçalho + LINHAS_MODELO
    assert tabela.autoFilter is not None


def test_dropdown_de_servico_e_opcional_e_usa_nome_nao_id(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Execução"]
    letra_servico = ws.cell(row=1, column=COL_EXE_SERVICO).column_letter
    dv_servico = next(dv for dv in ws.data_validations.dataValidation if str(dv.sqref).startswith(f"{letra_servico}2"))
    assert dv_servico.formula1 == "Lista_Servicos" and dv_servico.allow_blank


def test_colunas_de_execucao_foram_acrescentadas_em_servicos(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    titulos_esperados = [titulo for titulo, _l, _o, _c in COLUNAS_SERVICOS]
    titulos_no_arquivo = [ws.cell(row=1, column=i + 1).value for i in range(len(COLUNAS_SERVICOS))]
    assert titulos_no_arquivo == titulos_esperados
    assert "Método de Execução" in titulos_esperados
    assert "% Execução do Serviço" in titulos_esperados
    assert "Peso Efetivo" in titulos_esperados


def test_formula_qtd_executada_acumulada_soma_a_aba_execucao(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    formula = ws.cell(row=2, column=COL_SRV_QTD_EXECUTADA_ACUM).value
    assert "SUMIFS(" in formula
    assert "Execução!" in formula


def test_formula_percentual_execucao_despacha_por_metodo(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    formula = ws.cell(row=2, column=COL_SRV_PERCENTUAL_EXECUCAO).value
    assert "Quantitativo" in formula
    assert "Status" in formula
    assert "Pendente" in formula and "Em andamento" in formula and "Concluído" in formula


def test_formula_peso_automatico_usa_denominador_global_da_obra(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    formula = ws.cell(row=2, column=COL_SRV_PESO_AUTOMATICO).value
    assert "SUMIFS(" in formula
    assert "<>Cancelado" in formula and "<>Retirado do Escopo" in formula and "<>Substituído" in formula


def test_formula_peso_efetivo_protege_peso_manual(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    letra_peso_ajustado = get_column_letter(COL_SRV_PESO_AJUSTADO)
    formula = ws.cell(row=2, column=COL_SRV_PESO_EFETIVO).value
    assert f"${letra_peso_ajustado}2<>\"\"" in formula  # protege o peso manual quando preenchido


def test_dropdown_metodo_execucao_tem_2_opcoes_fechadas(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    letra = ws.cell(row=1, column=COL_SRV_METODO_EXECUCAO).column_letter
    dv = next(dv for dv in ws.data_validations.dataValidation if str(dv.sqref).startswith(f"{letra}2"))
    assert "Quantitativo" in dv.formula1 and "Status" in dv.formula1


def test_dropdown_status_execucao_tem_3_opcoes_fechadas(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    letra = ws.cell(row=1, column=COL_SRV_STATUS_EXECUCAO).column_letter
    dv = next(dv for dv in ws.data_validations.dataValidation if str(dv.sqref).startswith(f"{letra}2"))
    assert "Pendente" in dv.formula1 and "Em andamento" in dv.formula1 and "Concluído" in dv.formula1


def test_formula_contribuicao_multiplica_peso_efetivo_por_percentual(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    letra_peso_efetivo = get_column_letter(COL_SRV_PESO_EFETIVO)
    letra_percentual = get_column_letter(COL_SRV_PERCENTUAL_EXECUCAO)
    formula = ws.cell(row=2, column=COL_SRV_CONTRIBUICAO).value
    assert f"${letra_peso_efetivo}2" in formula and f"${letra_percentual}2" in formula


def test_percentuais_de_execucao_sao_formatados_como_percentual(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    for coluna in (COL_SRV_PERCENTUAL_EXECUCAO, COL_SRV_PESO_AUTOMATICO, COL_SRV_PESO_EFETIVO, COL_SRV_CONTRIBUICAO):
        assert ws.cell(row=2, column=coluna).number_format == "0.00%"


def test_inicio_tem_linha_de_execucao_fisica_da_obra(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Início"]
    rotulos = [ws.cell(row=r, column=1).value for r in range(1, 12)]
    assert "% Execução Física da Obra" in rotulos
    linha = rotulos.index("% Execução Física da Obra") + 1
    formula = ws.cell(row=linha, column=2).value
    assert "SUM(" in formula and "TabelaEtapas" in formula
