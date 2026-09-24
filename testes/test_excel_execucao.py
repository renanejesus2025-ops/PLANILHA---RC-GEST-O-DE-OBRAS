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


# ----------------------------------------------------------------------
# D-COM-2 (Etapa 8.2) — divisão por zero NUNCA pode virar #DIV/0!
# ----------------------------------------------------------------------
def _formula_peso_automatico(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    return ws.cell(row=2, column=COL_SRV_PESO_AUTOMATICO).value


def test_peso_automatico_trata_denominador_zero_como_nd(tmp_path):
    """
    D-COM-2: o denominador do Peso Automático (Σ Valor Previsto dos
    Serviços Elegíveis) pode ser zero — basta que todos os elegíveis
    estejam orçados em 0. Sem guarda, o Excel devolvia `#DIV/0!`, que se
    propagava até `Início!B9`. REG-031 exige "não calculável" ("N/D"),
    nunca erro. O Python já retornava `None`.
    """
    formula = _formula_peso_automatico(tmp_path)
    assert '"N/D"' in formula
    assert "=0," in formula  # guarda explícita de denominador zero


def test_peso_efetivo_distribui_igualmente_quando_base_proporcional_e_zero(tmp_path):
    """Espelha o ramo `total_bruto_automaticos == 0` de
    `pesos_efetivos_obra` (Etapa 7): a faixa restante é dividida
    igualmente entre os automáticos elegíveis, via COUNTIFS."""
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Serviços"]
    formula = ws.cell(row=2, column=COL_SRV_PESO_EFETIVO).value
    assert "SUMPRODUCT(ISNUMBER(" in formula


def test_nenhuma_divisao_do_workbook_fica_sem_guarda(tmp_path):
    """
    Auditoria de toda a cadeia (exigida pela Etapa 8.2), não só de
    `Início!B9`: toda fórmula que divide precisa proteger o denominador.
    Sem isso, um `#DIV/0!` atravessa Peso Automático → Peso Efetivo →
    Contribuição → Subetapa → Etapa → Obra → Início.
    """
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    wb = openpyxl.load_workbook(caminho)

    desprotegidas = []
    for nome in wb.sheetnames:
        for linha in wb[nome].iter_rows():
            for celula in linha:
                valor = celula.value
                if not (isinstance(valor, str) and valor.startswith("=") and "/" in valor):
                    continue
                # "Despesa/Custo" é rótulo de domínio, não divisão.
                if "/" not in valor.replace("Despesa/Custo", ""):
                    continue
                # Toda divisão legítima do projeto é guardada por um IF
                # que testa vazio ou zero antes de dividir.
                if not ('=0,' in valor or '="",' in valor or '=0,"N/D"' in valor):
                    desprotegidas.append((nome, celula.coordinate, valor))
    assert desprotegidas == [], f"divisão sem guarda de denominador: {desprotegidas}"


def test_percentual_execucao_da_obra_e_nd_quando_nao_ha_servico_elegivel(tmp_path):
    """
    Etapa 8.2 (item 11.1): sem nenhum Serviço Elegível (REG-022), o `SUM`
    de uma coluna vazia devolvia 0 e a tela exibia "0,00% executado" —
    enquanto `percentual_execucao_obra` (Python) devolve `None`, "não
    calculável". Ler 0% onde não há base de cálculo é a mesma leitura
    inválida que REG-031 proíbe para divisão por zero.
    """
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Início"]
    rotulos = [ws.cell(row=r, column=1).value for r in range(1, 14)]
    linha = rotulos.index("% Execução Física da Obra") + 1
    formula = ws.cell(row=linha, column=2).value
    assert '"N/D"' in formula
    assert "SUMPRODUCT(ISNUMBER(" in formula  # contagem de elegíveis, sem range fixo
    assert "SUM(TabelaEtapas[" in formula  # o cálculo em si permanece


def test_contagem_de_elegiveis_espelha_os_criterios_do_python(tmp_path):
    """A contagem usada na guarda precisa aplicar exatamente os mesmos
    critérios de exclusão de REG-022 que `servico_elegivel_execucao`."""
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Início"]
    rotulos = [ws.cell(row=r, column=1).value for r in range(1, 14)]
    formula = ws.cell(row=rotulos.index("% Execução Física da Obra") + 1, column=2).value
    for excluido in ("Cancelado", "Retirado do Escopo", "Substituído"):
        assert f'<>"{excluido}"' in formula
