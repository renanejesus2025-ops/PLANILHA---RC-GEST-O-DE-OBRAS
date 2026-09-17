"""
Construção do arquivo Excel funcional — Etapa 2 ("Base da Obra") e
Etapa 3 ("Orçamento").

Gera um workbook com 5 abas — nenhuma aba nova foi criada na Etapa 3
(Seção 23: "reutilizar a aba Serviços quando possível"; "menos abas +
melhor organização"):

    Início      — cadastro amigável da Obra + Orçamento Inicial (Σ Etapas).
    Etapas      — 1 linha = 1 Etapa, agora com Total Previsto (Σ Subetapas).
    Subetapas   — 1 linha = 1 Subetapa, agora com Total Previsto (Σ Serviços).
    Serviços    — 1 linha = 1 Serviço, agora com a base orçamentária completa
                  (Quantidade, Valor Unitário, Valor Calculado, Ajuste
                  Manual, Valor Previsto, Variação, Status).
    Base_Dados  — aba técnica oculta (metadados internos e prefixos de ID).

Princípios seguidos (Etapa 2, Seções 2/12/14/15/17/22, mantidos; Etapa 3,
Seções 2/3/4/5/6/10/11/12/13/14/15/18/19/20/21/24/25/30/31/36):

- 1 arquivo Excel = 1 obra; hierarquia oficial obrigatória OBRA → ETAPA →
  SUBETAPA → SERVIÇO; "código para a máquina, nome para o usuário"; uma
  linha = um registro; sem VBA/macro/ActiveX.
- **Valor Previsto (Etapa 3, Opção C — [D] HOMOLOGADO nesta implementação,
  Seção 36):** Valor Calculado = Quantidade × Valor Unitário (sempre
  calculado, nunca sobrescrito); Valor Previsto = Valor Calculado, salvo
  Ajuste Manual do Operador (Seções 11/12) — o Valor Calculado permanece
  visível e preservado mesmo quando há ajuste.
- **Variação = Valor Previsto − Valor Calculado** (Seção 13) — termo
  "Variação", nunca "Desvio"; variação PERCENTUAL não é exposta aqui
  (pendência registrada no relatório da Etapa 3, por poder colidir com
  thresholds de alerta ainda não homologados — REG-013/014/015).
- **Status do Serviço — [D] HOMOLOGADO na Etapa 3 (Seção 18):** domínio
  fechado Ativo/Concluído/Cancelado/Retirado do Escopo/Substituído (ver
  `StatusServico`). Os totais (Seções 14/19) excluem Cancelado, Retirado
  do Escopo e Substituído via `SUMIFS` com critérios "<>", chaveados
  pelo ID técnico (nunca pelo nome — ver `_criar_intervalos_nomeados` e
  a Seção 21 sobre o risco de nomes duplicados).
- **Nenhum alerta/formatação condicional de desvio foi criado** (Etapa 3,
  Seção 31) — a coluna Variação é um número simples, sem cor/ícone.
- **Nenhuma fórmula de Aporte/Alteração/Custo Realizado foi somada aos
  totais** (Seção 14/15/16/17) — os totais desta etapa são só o
  orçamento previsto dos serviços (REG-003), não o Orçamento Vigente
  (REG-017).

**Uso do GeradorId da Etapa 1** (mantido da Etapa 2): quando esta função
recebe entidades já construídas via `BaseDados`/`GeradorId`, o ID
técnico é escrito como valor literal; nas linhas em branco do modelo,
uma fórmula de planilha replica o mesmo padrão "PREFIXO-0000". As
colunas CALCULADAS (Valor Calculado, Ajuste Manual, Valor Previsto,
Variação, Total Previsto, e os vínculos técnicos ocultos) são SEMPRE
fórmulas — inclusive nas linhas com dado literal — porque são valores
derivados que devem continuar corretos se o Operador editar Quantidade/
Valor Unitário/Status diretamente no Excel depois.
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from config.ids_config import PREFIXOS_ID
from src.base_dados.repositorio import BaseDados
from src.excel.estilos import (
    ALINHAMENTO_CABECALHO,
    BORDA_CELULA,
    FONTE_CABECALHO,
    FONTE_CALCULADA,
    FONTE_ROTULO_FORM,
    PREENCHIMENTO_CABECALHO,
    PREENCHIMENTO_CALCULADO,
)
from src.modelo.enums import StatusServico

# Linhas em branco pré-formatadas (fórmulas de ID/vínculo já ativas),
# prontas para uso direto no Excel sem dado nenhum inventado.
LINHAS_MODELO = 30

# (título da coluna, largura, oculta, calculada-por-fórmula)
COLUNAS_ETAPAS = [
    ("ID (técnico)", 14, True, False),
    ("Nome", 30, False, False),
    ("Ordem", 10, False, False),
    ("Status", 20, False, False),
    ("ID_Obra (técnico)", 16, True, False),
    ("Total Previsto (Subetapas)", 22, False, True),
]
COLUNAS_SUBETAPAS = [
    ("ID (técnico)", 14, True, False),
    ("Nome", 30, False, False),
    ("Etapa", 26, False, False),
    ("Status", 20, False, False),
    ("ID_Etapa (técnico)", 16, True, False),
    ("Total Previsto (Serviços)", 22, False, True),
]
COLUNAS_SERVICOS = [
    ("ID (técnico)", 14, True, False),                      # A
    ("Descrição", 34, False, False),                        # B
    ("Subetapa", 26, False, False),                         # C
    ("Unidade de Medida", 16, False, False),                # D
    ("Quantidade Orçada", 16, False, False),                # E
    ("Valor Unitário", 14, False, False),                   # F
    ("Valor Calculado", 16, False, True),                   # G
    ("Valor Previsto (Ajuste Manual)", 24, False, False),   # H
    ("Ajuste Manual", 14, False, True),                     # I
    ("Valor Previsto", 16, False, True),                    # J
    ("Variação", 14, False, True),                          # K
    ("Status", 20, False, False),                           # L
    ("ID_Subetapa (técnico)", 18, True, False),             # M
]

# Índices de coluna (1-based) da aba Serviços — evita "números mágicos".
COL_SRV_ID = 1
COL_SRV_DESCRICAO = 2
COL_SRV_SUBETAPA = 3
COL_SRV_UNIDADE = 4
COL_SRV_QUANTIDADE = 5
COL_SRV_VALOR_UNITARIO = 6
COL_SRV_VALOR_CALCULADO = 7
COL_SRV_VALOR_PREVISTO_MANUAL = 8
COL_SRV_AJUSTE_MANUAL = 9
COL_SRV_VALOR_PREVISTO = 10
COL_SRV_VARIACAO = 11
COL_SRV_STATUS = 12
COL_SRV_ID_SUBETAPA = 13

COL_SUB_ID = 1
COL_SUB_NOME = 2
COL_SUB_ETAPA = 3
COL_SUB_STATUS = 4
COL_SUB_ID_ETAPA = 5
COL_SUB_TOTAL = 6

COL_ETA_ID = 1
COL_ETA_NOME = 2
COL_ETA_ORDEM = 3
COL_ETA_STATUS = 4
COL_ETA_ID_OBRA = 5
COL_ETA_TOTAL = 6

NOME_INTERVALO_ETAPAS = "Lista_Etapas"
NOME_INTERVALO_SUBETAPAS = "Lista_Subetapas"

# Lista fechada do Status do Serviço (Etapa 3, Seção 18) — mesma fonte
# (`StatusServico`) usada pelo Python, nunca digitada de novo à mão.
_ROTULOS_STATUS_SERVICO = [s.rotulo for s in StatusServico]
_LISTA_STATUS_SERVICO = '"' + ",".join(_ROTULOS_STATUS_SERVICO) + '"'
_ROTULO_CANCELADO = StatusServico.CANCELADO.rotulo
_ROTULO_RETIRADO = StatusServico.RETIRADO_DO_ESCOPO.rotulo
_ROTULO_SUBSTITUIDO = StatusServico.SUBSTITUIDO.rotulo


def construir_workbook(base: BaseDados | None = None) -> Workbook:
    """
    Gera o workbook completo (5 abas) a partir de uma `BaseDados`.

    Ver docstring do módulo para o comportamento com `base` vazia
    (modelo/template) ou populada (usado pelos testes).
    """
    base = base or BaseDados()

    if base.obras:
        id_obra = next(iter(base.obras))
    else:
        id_obra = base.gerador_id.gerar("OBRAS")
    obra = base.obras.get(id_obra)

    etapas = list(base.etapas.values())
    ultima_linha_etapas = 1 + len(etapas) + LINHAS_MODELO

    wb = Workbook()
    wb.remove(wb.active)  # remove a aba padrão "Sheet"

    _construir_aba_inicio(wb, obra=obra, ultima_linha_etapas=ultima_linha_etapas)
    _construir_aba_etapas(wb, etapas, id_obra=id_obra)
    _construir_aba_subetapas(wb, list(base.subetapas.values()), base.etapas)
    _construir_aba_servicos(wb, list(base.servicos.values()), base.subetapas)
    _construir_aba_base_dados(wb, id_obra=id_obra)
    _criar_intervalos_nomeados(wb)

    wb.active = 0  # abre na aba "Início"
    return wb


# --------------------------------------------------------------------
# Aba: Início (Obra)
# --------------------------------------------------------------------
def _construir_aba_inicio(wb: Workbook, *, obra, ultima_linha_etapas: int) -> None:
    """ENTIDADE: OBRAS — formulário vertical (Etapa 2, Seção 5)."""
    ws = wb.create_sheet("Início")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 42

    titulo = ws.cell(row=1, column=1, value="Dados da Obra")
    titulo.font = FONTE_CABECALHO
    titulo.fill = PREENCHIMENTO_CABECALHO
    titulo.alignment = ALINHAMENTO_CABECALHO
    ws.cell(row=1, column=2).fill = PREENCHIMENTO_CABECALHO
    ws.row_dimensions[1].height = 24

    campos = [
        ("Nome da Obra", getattr(obra, "nome", None), None),
        ("Cliente/Contratante", getattr(obra, "cliente_contratante", None), None),
        ("Endereço", getattr(obra, "endereco", None), None),
        ("Responsável Técnico", getattr(obra, "responsavel_tecnico", None), None),
        ("Data Inicial Planejada", getattr(obra, "data_inicio", None), "data"),
        ("Data Final Planejada", getattr(obra, "data_prevista_termino", None), "data"),
    ]

    linha = 2
    for rotulo, valor, tipo in campos:
        celula_rotulo = ws.cell(row=linha, column=1, value=rotulo)
        celula_rotulo.font = FONTE_ROTULO_FORM
        celula_valor = ws.cell(row=linha, column=2, value=valor)
        celula_valor.border = BORDA_CELULA
        if tipo == "data":
            celula_valor.number_format = "DD/MM/YYYY"
            dv = DataValidation(
                type="date",
                operator="greaterThanOrEqual",
                formula1="1900-01-01",
                allow_blank=True,
                showErrorMessage=True,
                errorTitle="Data inválida",
                error="Informe uma data válida.",
            )
            ws.add_data_validation(dv)
            dv.add(celula_valor.coordinate)
        linha += 1

    # Orçamento Inicial (Previsto) — Etapa 3, Seção 15: "o orçamento dos
    # serviços constitui a base do orçamento inicial da obra". Agora que
    # Valor Previsto está homologado (Seção 36), esta célula soma os
    # totais por Etapa (Etapas!Total Previsto) — NÃO inclui Aportes,
    # Alterações, Custo Realizado ou Saldo de Caixa (Seção 15/16/17: essa
    # lógica de Orçamento Vigente pertence a uma etapa futura).
    celula_rotulo = ws.cell(row=linha, column=1, value="Orçamento Inicial (Previsto)")
    celula_rotulo.font = FONTE_ROTULO_FORM
    letra_total_etapas = get_column_letter(COL_ETA_TOTAL)
    celula_valor = ws.cell(
        row=linha,
        column=2,
        value=f"=SUM(Etapas!${letra_total_etapas}$2:${letra_total_etapas}${ultima_linha_etapas})",
    )
    celula_valor.number_format = "#,##0.00"
    celula_valor.border = BORDA_CELULA
    celula_valor.fill = PREENCHIMENTO_CALCULADO
    celula_valor.font = FONTE_CALCULADA

    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Etapas
# --------------------------------------------------------------------
def _construir_aba_etapas(wb: Workbook, etapas: list, *, id_obra: str) -> None:
    ws = wb.create_sheet("Etapas")
    _escrever_cabecalho(ws, COLUNAS_ETAPAS)

    ultima_linha = 1 + len(etapas) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["ETAPAS"]

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(etapas):
            etapa = etapas[indice]
            ws.cell(row=r, column=COL_ETA_ID, value=etapa.id)
            ws.cell(row=r, column=COL_ETA_NOME, value=etapa.nome)
            ws.cell(row=r, column=COL_ETA_ORDEM, value=etapa.ordem)
            ws.cell(row=r, column=COL_ETA_STATUS, value=etapa.status)
        else:
            ws.cell(
                row=r,
                column=COL_ETA_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )

        # Sempre fórmula, linha literal ou não (campo derivado):
        ws.cell(row=r, column=COL_ETA_ID_OBRA, value=f'=IF($B{r}="","",Base_Dados!$B$2)')
        ws.cell(
            row=r,
            column=COL_ETA_TOTAL,
            value=(
                f'=IF($B{r}="","",SUMIFS(Subetapas!${get_column_letter(COL_SUB_TOTAL)}:'
                f'${get_column_letter(COL_SUB_TOTAL)},'
                f'Subetapas!${get_column_letter(COL_SUB_ID_ETAPA)}:'
                f'${get_column_letter(COL_SUB_ID_ETAPA)},$A{r}))'
            ),
        )

    dv_ordem = DataValidation(
        type="whole",
        operator="greaterThan",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Ordem inválida",
        error="Informe um número inteiro maior que zero.",
    )
    ws.add_data_validation(dv_ordem)
    dv_ordem.add(f"C2:C{ultima_linha}")

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_ETA_TOTAL).number_format = "#,##0.00"
        ws.cell(row=r, column=COL_ETA_TOTAL).fill = PREENCHIMENTO_CALCULADO
        ws.cell(row=r, column=COL_ETA_TOTAL).font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_ETAPAS))
    _aplicar_filtro_e_congelamento(ws, ultima_linha, len(COLUNAS_ETAPAS))


# --------------------------------------------------------------------
# Aba: Subetapas
# --------------------------------------------------------------------
def _construir_aba_subetapas(wb: Workbook, subetapas: list, etapas_por_id: dict) -> None:
    ws = wb.create_sheet("Subetapas")
    _escrever_cabecalho(ws, COLUNAS_SUBETAPAS)

    ultima_linha = 1 + len(subetapas) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["SUBETAPAS"]

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(subetapas):
            subetapa = subetapas[indice]
            etapa = etapas_por_id.get(subetapa.id_etapa)
            ws.cell(row=r, column=COL_SUB_ID, value=subetapa.id)
            ws.cell(row=r, column=COL_SUB_NOME, value=subetapa.nome)
            ws.cell(row=r, column=COL_SUB_ETAPA, value=getattr(etapa, "nome", None))
            ws.cell(row=r, column=COL_SUB_STATUS, value=subetapa.status)
        else:
            ws.cell(
                row=r,
                column=COL_SUB_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )

        ws.cell(
            row=r,
            column=COL_SUB_ID_ETAPA,
            value=f'=IF($C{r}="","",INDEX(Etapas!$A:$A,MATCH($C{r},Etapas!$B:$B,0)))',
        )
        ws.cell(
            row=r,
            column=COL_SUB_TOTAL,
            value=(
                f'=IF($B{r}="","",SUMIFS(Serviços!${get_column_letter(COL_SRV_VALOR_PREVISTO)}:'
                f'${get_column_letter(COL_SRV_VALOR_PREVISTO)},'
                f'Serviços!${get_column_letter(COL_SRV_ID_SUBETAPA)}:'
                f'${get_column_letter(COL_SRV_ID_SUBETAPA)},$A{r},'
                f'Serviços!${get_column_letter(COL_SRV_STATUS)}:'
                f'${get_column_letter(COL_SRV_STATUS)},"<>{_ROTULO_CANCELADO}",'
                f'Serviços!${get_column_letter(COL_SRV_STATUS)}:'
                f'${get_column_letter(COL_SRV_STATUS)},"<>{_ROTULO_RETIRADO}",'
                f'Serviços!${get_column_letter(COL_SRV_STATUS)}:'
                f'${get_column_letter(COL_SRV_STATUS)},"<>{_ROTULO_SUBSTITUIDO}"))'
            ),
        )

    dv_etapa = DataValidation(
        type="list",
        formula1=NOME_INTERVALO_ETAPAS,
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Etapa inválida",
        error="Selecione uma Etapa já cadastrada na aba Etapas.",
    )
    ws.add_data_validation(dv_etapa)
    dv_etapa.add(f"C2:C{ultima_linha}")

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_SUB_TOTAL).number_format = "#,##0.00"
        ws.cell(row=r, column=COL_SUB_TOTAL).fill = PREENCHIMENTO_CALCULADO
        ws.cell(row=r, column=COL_SUB_TOTAL).font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_SUBETAPAS))
    _aplicar_filtro_e_congelamento(ws, ultima_linha, len(COLUNAS_SUBETAPAS))


# --------------------------------------------------------------------
# Aba: Serviços (Serviços/Orçamento) — base orçamentária (Etapa 3)
# --------------------------------------------------------------------
def _construir_aba_servicos(wb: Workbook, servicos: list, subetapas_por_id: dict) -> None:
    ws = wb.create_sheet("Serviços")
    _escrever_cabecalho(ws, COLUNAS_SERVICOS)

    ultima_linha = 1 + len(servicos) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["SERVICOS_ORCAMENTO"]

    letra_qtd = get_column_letter(COL_SRV_QUANTIDADE)
    letra_vu = get_column_letter(COL_SRV_VALOR_UNITARIO)
    letra_vc = get_column_letter(COL_SRV_VALOR_CALCULADO)
    letra_vpm = get_column_letter(COL_SRV_VALOR_PREVISTO_MANUAL)
    letra_vp = get_column_letter(COL_SRV_VALOR_PREVISTO)
    letra_subetapa = get_column_letter(COL_SRV_SUBETAPA)

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(servicos):
            servico = servicos[indice]
            subetapa = subetapas_por_id.get(servico.id_subetapa)
            ws.cell(row=r, column=COL_SRV_ID, value=servico.id)
            ws.cell(row=r, column=COL_SRV_DESCRICAO, value=servico.descricao)
            ws.cell(row=r, column=COL_SRV_SUBETAPA, value=getattr(subetapa, "nome", None))
            ws.cell(row=r, column=COL_SRV_UNIDADE, value=servico.unidade_medida)
            ws.cell(row=r, column=COL_SRV_QUANTIDADE, value=servico.quantidade_orcada)
            ws.cell(row=r, column=COL_SRV_VALOR_UNITARIO, value=servico.valor_unitario)
            ws.cell(row=r, column=COL_SRV_VALOR_PREVISTO_MANUAL, value=servico.valor_previsto_manual)
            rotulo_status = servico.status.rotulo if servico.status is not None else None
            ws.cell(row=r, column=COL_SRV_STATUS, value=rotulo_status)
        else:
            ws.cell(
                row=r,
                column=COL_SRV_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )

        # Colunas SEMPRE calculadas por fórmula (linha literal ou não):
        ws.cell(
            row=r,
            column=COL_SRV_VALOR_CALCULADO,
            value=f'=IF(OR(${letra_qtd}{r}="",${letra_vu}{r}=""),"",${letra_qtd}{r}*${letra_vu}{r})',
        )
        ws.cell(
            row=r,
            column=COL_SRV_AJUSTE_MANUAL,
            value=f'=IF(${letra_vpm}{r}="","NÃO","SIM")',
        )
        ws.cell(
            row=r,
            column=COL_SRV_VALOR_PREVISTO,
            value=f'=IF(${letra_vpm}{r}="",${letra_vc}{r},${letra_vpm}{r})',
        )
        ws.cell(
            row=r,
            column=COL_SRV_VARIACAO,
            value=f'=IF(OR(${letra_vp}{r}="",${letra_vc}{r}=""),"",${letra_vp}{r}-${letra_vc}{r})',
        )
        ws.cell(
            row=r,
            column=COL_SRV_ID_SUBETAPA,
            value=(
                f'=IF(${letra_subetapa}{r}="","",'
                f'INDEX(Subetapas!$A:$A,MATCH(${letra_subetapa}{r},Subetapas!$B:$B,0)))'
            ),
        )

    # Dropdown "Subetapa" — nomes amigáveis (nunca IDs).
    dv_subetapa = DataValidation(
        type="list",
        formula1=NOME_INTERVALO_SUBETAPAS,
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Subetapa inválida",
        error="Selecione uma Subetapa já cadastrada na aba Subetapas.",
    )
    ws.add_data_validation(dv_subetapa)
    dv_subetapa.add(f"C2:C{ultima_linha}")

    # Dropdown "Status" — domínio fechado homologado na Etapa 3 (Seção 18).
    dv_status = DataValidation(
        type="list",
        formula1=_LISTA_STATUS_SERVICO,
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Status inválido",
        error="Selecione um dos status oficiais: " + ", ".join(_ROTULOS_STATUS_SERVICO) + ".",
    )
    ws.add_data_validation(dv_status)
    dv_status.add(f"L2:L{ultima_linha}")

    # Quantidade e Valor Unitário: numéricos e não negativos (Seções 8/9).
    dv_quantidade = DataValidation(
        type="decimal",
        operator="greaterThanOrEqual",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Quantidade inválida",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_quantidade)
    dv_quantidade.add(f"E2:E{ultima_linha}")

    dv_valor_unitario = DataValidation(
        type="decimal",
        operator="greaterThanOrEqual",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_valor_unitario)
    dv_valor_unitario.add(f"F2:F{ultima_linha}")
    # Nenhuma validação de sinal foi aplicada a "Valor Previsto (Ajuste
    # Manual)" (coluna H) — as Seções 8/9 da Etapa 3 só pedem essa regra
    # para Quantidade e Valor Unitário; estender a mesma regra ao ajuste
    # manual não foi solicitado e não foi inventado aqui.

    for r in range(2, ultima_linha + 1):
        for coluna in (
            COL_SRV_QUANTIDADE,
            COL_SRV_VALOR_UNITARIO,
            COL_SRV_VALOR_CALCULADO,
            COL_SRV_VALOR_PREVISTO_MANUAL,
            COL_SRV_VALOR_PREVISTO,
            COL_SRV_VARIACAO,
        ):
            ws.cell(row=r, column=coluna).number_format = "#,##0.00"

    for indice_coluna, (_titulo, _largura, _oculta, calculada) in enumerate(COLUNAS_SERVICOS, start=1):
        if not calculada:
            continue
        for r in range(2, ultima_linha + 1):
            celula = ws.cell(row=r, column=indice_coluna)
            celula.fill = PREENCHIMENTO_CALCULADO
            celula.font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_SERVICOS))
    _aplicar_filtro_e_congelamento(ws, ultima_linha, len(COLUNAS_SERVICOS))


# --------------------------------------------------------------------
# Aba técnica oculta: Base_Dados
# --------------------------------------------------------------------
def _construir_aba_base_dados(wb: Workbook, *, id_obra: str) -> None:
    """
    "Base técnica" (Etapa 2, área 5): metadados internos usados pelas
    fórmulas das demais abas. Fica OCULTA, mas não protegida por senha —
    o mecanismo de proteção do Excel segue [H] (SEC_001 Seção 4).
    """
    ws = wb.create_sheet("Base_Dados")

    ws["A1"] = "Metadados internos — não editar"
    ws["A1"].font = FONTE_CABECALHO
    ws["A1"].fill = PREENCHIMENTO_CABECALHO
    ws["B1"].fill = PREENCHIMENTO_CABECALHO

    ws["A2"] = "ID da Obra (técnico)"
    ws["A2"].font = FONTE_ROTULO_FORM
    ws["B2"] = id_obra

    ws["A4"] = "Prefixos de ID técnico homologados (ver Etapa 1, Seção 7)"
    ws["A4"].font = FONTE_ROTULO_FORM
    linha = 5
    for entidade, prefixo in PREFIXOS_ID.items():
        ws.cell(row=linha, column=1, value=entidade)
        ws.cell(row=linha, column=2, value=prefixo)
        linha += 1

    linha += 1
    ws.cell(row=linha, column=1, value="Status do Serviço homologados (Etapa 3, Seção 18)").font = FONTE_ROTULO_FORM
    linha += 1
    for status in StatusServico:
        ws.cell(row=linha, column=1, value=status.rotulo)
        ws.cell(row=linha, column=2, value="integra orçamento corrente" if status.integra_orcamento_corrente else "excluído do orçamento corrente")
        linha += 1

    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 30

    ws.sheet_state = "hidden"


# --------------------------------------------------------------------
# Intervalos nomeados (fonte dos dropdowns amigáveis)
# --------------------------------------------------------------------
def _criar_intervalos_nomeados(wb: Workbook) -> None:
    """
    Intervalos Nomeados para as colunas "Nome" de Etapas/Subetapas — ver
    docstring equivalente na versão da Etapa 2. Mantido sem alteração.
    """
    wb.defined_names[NOME_INTERVALO_ETAPAS] = DefinedName(
        NOME_INTERVALO_ETAPAS, attr_text="Etapas!$B$2:$B$1000"
    )
    wb.defined_names[NOME_INTERVALO_SUBETAPAS] = DefinedName(
        NOME_INTERVALO_SUBETAPAS, attr_text="Subetapas!$B$2:$B$1000"
    )


# --------------------------------------------------------------------
# Auxiliares genéricos
# --------------------------------------------------------------------
def _escrever_cabecalho(ws: Worksheet, colunas: list[tuple[str, int, bool, bool]]) -> None:
    for indice, (titulo, largura, oculta, _calculada) in enumerate(colunas, start=1):
        celula = ws.cell(row=1, column=indice, value=titulo)
        celula.font = FONTE_CABECALHO
        celula.fill = PREENCHIMENTO_CABECALHO
        celula.alignment = ALINHAMENTO_CABECALHO
        letra = celula.column_letter
        ws.column_dimensions[letra].width = largura
        if oculta:
            ws.column_dimensions[letra].hidden = True
    ws.row_dimensions[1].height = 30


def _aplicar_bordas(ws: Worksheet, ultima_linha: int, n_colunas: int) -> None:
    for linha_de_celulas in ws.iter_rows(min_row=1, max_row=ultima_linha, min_col=1, max_col=n_colunas):
        for celula in linha_de_celulas:
            celula.border = BORDA_CELULA


def _aplicar_filtro_e_congelamento(ws: Worksheet, ultima_linha: int, n_colunas: int) -> None:
    """Filtro (Etapa 3, Seção 24) e congelamento de cabeçalho (mantido da Etapa 2)."""
    ultima_coluna = get_column_letter(n_colunas)
    ws.auto_filter.ref = f"A1:{ultima_coluna}{ultima_linha}"
    ws.freeze_panes = "A2"
