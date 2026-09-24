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
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from config.ids_config import PREFIXOS_ID
from src.base_dados.repositorio import BaseDados
from src.excel.estilos import (
    ALINHAMENTO_CABECALHO,
    BORDA_CELULA,
    FONTE_CABECALHO,
    FONTE_CALCULADA,
    FONTE_ROTULO_FORM,
    FORMATO_MOEDA_BR,
    PREENCHIMENTO_CABECALHO,
    PREENCHIMENTO_CALCULADO,
)
from src.modelo.enums import (
    MetodoExecucao,
    StatusAprovacaoAlteracao,
    StatusExecucao,
    StatusServico,
    TipoAlteracao,
    TipoLancamentoFinanceiro,
)

# Linhas em branco pré-formatadas (fórmulas de ID/vínculo já ativas),
# prontas para uso direto no Excel sem dado nenhum inventado.
LINHAS_MODELO = 30

# (título da coluna, largura, oculta, calculada-por-fórmula)
# Etapa 8 (Planejamento/Cronograma da Obra) — as 7 colunas de cronograma
# abaixo são idênticas em Etapas e Subetapas: 4 datas digitadas pelo
# Operador (fonte de verdade única do registro, decisão homologada em
# 2026-09-23, Opção A) + 3 colunas calculadas. Elas ficam NAS PRÓPRIAS
# abas Etapas/Subetapas — que já são Tabelas Excel estruturadas e se
# expandem sozinhas — em vez de numa terceira aba "Cronograma" montada
# por fórmulas: uma aba-espelho teria buffer fixo de linhas e voltaria a
# ignorar silenciosamente registros além dele, exatamente o defeito
# corrigido na Etapa 5.1 (AUD-20/AUD-21). Ver relatório da Etapa 8.
_COLUNAS_CRONOGRAMA = [
    ("Data Início Prevista", 18, False, False),
    ("Data Fim Prevista", 18, False, False),
    ("Data Início Real", 16, False, False),
    ("Data Fim Real", 16, False, False),
    ("Duração Prevista (dias)", 20, False, True),
    ("Duração Real (dias)", 18, False, True),
    ("Variação de Prazo (dias)", 20, False, True),
]

COLUNAS_ETAPAS = [
    ("ID (técnico)", 14, True, False),
    ("Nome", 30, False, False),
    ("Ordem", 10, False, False),
    ("Status", 20, False, False),
    ("ID_Obra (técnico)", 16, True, False),
    ("Total Previsto (Subetapas)", 22, False, True),
    # Etapa 7 — valores informativos de grupo, NÃO um "% da Etapa"
    # isolado (REG-020 marca essa fórmula como [H] — ver
    # `src/execucao/calculos.py`, docstring do módulo).
    ("Peso Consolidado (Execução)", 24, False, True),
    ("Contribuição na Obra (Execução)", 28, False, True),
    *_COLUNAS_CRONOGRAMA,  # Etapa 8
]
COLUNAS_SUBETAPAS = [
    ("ID (técnico)", 14, True, False),
    ("Nome", 30, False, False),
    ("Etapa", 26, False, False),
    ("Status", 20, False, False),
    ("ID_Etapa (técnico)", 16, True, False),
    ("Total Previsto (Serviços)", 22, False, True),
    # Etapa 7 — mesma ressalva da aba Etapas acima.
    ("Peso Consolidado (Execução)", 24, False, True),
    ("Contribuição na Obra (Execução)", 28, False, True),
    *_COLUNAS_CRONOGRAMA,  # Etapa 8
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
    # Etapa 7 — Execução/Medições (Progresso Físico, REG-007/008/020):
    ("Método de Execução", 18, False, False),               # M
    ("Status de Execução", 18, False, False),                # N
    ("Qtd. Executada (acum.)", 20, False, True),            # O
    ("% Execução do Serviço", 20, False, True),             # P
    ("Peso Ajustado (manual)", 20, False, False),           # Q
    ("Peso Automático", 16, False, True),                   # R
    ("Peso Efetivo", 16, False, True),                      # S
    ("Contribuição na Obra", 18, False, True),              # T
    ("ID_Subetapa (técnico)", 18, True, False),             # U
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
# Etapa 7:
COL_SRV_METODO_EXECUCAO = 13
COL_SRV_STATUS_EXECUCAO = 14
COL_SRV_QTD_EXECUTADA_ACUM = 15
COL_SRV_PERCENTUAL_EXECUCAO = 16
COL_SRV_PESO_AJUSTADO = 17
COL_SRV_PESO_AUTOMATICO = 18
COL_SRV_PESO_EFETIVO = 19
COL_SRV_CONTRIBUICAO = 20
COL_SRV_ID_SUBETAPA = 21

# --------------------------------------------------------------------
# Etapa 4 — colunas das abas Financeiro e Pagamentos
# --------------------------------------------------------------------
COLUNAS_FINANCEIRO = [
    ("ID (técnico)", 14, True, False),      # A
    ("Tipo", 20, False, False),             # B
    ("Data", 14, False, False),             # C
    ("Descrição", 34, False, False),        # D
    ("Valor", 16, False, False),            # E
    ("Entrada/Saída", 26, False, True),     # F
    ("Aporte", 16, False, True),            # G
    ("Custo Realizado", 18, False, True),   # H
    ("Total Pago", 16, False, True),        # I
    ("A Pagar", 16, False, True),           # J
    ("Situação", 18, False, False),         # K
    ("Observação", 30, False, False),       # L
    ("ID_Obra (técnico)", 16, True, False), # M
]
COL_FIN_ID = 1
COL_FIN_TIPO = 2
COL_FIN_DATA = 3
COL_FIN_DESCRICAO = 4
COL_FIN_VALOR = 5
COL_FIN_ENTRADA_SAIDA = 6
COL_FIN_APORTE = 7
COL_FIN_CUSTO_REALIZADO = 8
COL_FIN_TOTAL_PAGO = 9
COL_FIN_A_PAGAR = 10
COL_FIN_SITUACAO = 11
COL_FIN_OBSERVACAO = 12
COL_FIN_ID_OBRA = 13

COLUNAS_PAGAMENTOS = [
    ("ID (técnico)", 14, True, False),                # A
    ("Lançamento (Despesa/Custo)", 34, False, False),  # B
    ("Data do Pagamento", 16, False, False),           # C
    ("Valor Pago", 16, False, False),                  # D
    ("Observação", 30, False, False),                  # E
    ("ID_Financeiro (técnico)", 18, True, False),       # F
]
COL_PAG_ID = 1
COL_PAG_LANCAMENTO = 2
COL_PAG_DATA = 3
COL_PAG_VALOR = 4
COL_PAG_OBSERVACAO = 5
COL_PAG_ID_FINANCEIRO = 6

# --------------------------------------------------------------------
# Etapa 5 — colunas da aba Alterações
# --------------------------------------------------------------------
COLUNAS_ALTERACOES = [
    ("ID (técnico)", 14, True, False),        # A
    ("Tipo", 16, False, False),                # B
    ("Data", 14, False, False),                # C
    ("Descrição", 34, False, False),           # D
    ("Impacto no Orçamento", 20, False, False),# E
    ("Impacto no Prazo (dias)", 20, False, False), # F
    ("Status de Aprovação", 18, False, False), # G
    ("Solicitante", 22, False, False),         # H
    ("ID_Obra (técnico)", 16, True, False),    # I
]
COL_ALT_ID = 1
COL_ALT_TIPO = 2
COL_ALT_DATA = 3
COL_ALT_DESCRICAO = 4
COL_ALT_IMPACTO_ORCAMENTO = 5
COL_ALT_IMPACTO_PRAZO = 6
COL_ALT_STATUS = 7
COL_ALT_SOLICITANTE = 8
COL_ALT_ID_OBRA = 9

# --------------------------------------------------------------------
# Etapa 6 — colunas da aba Compras
# --------------------------------------------------------------------
COLUNAS_COMPRAS = [
    ("ID (técnico)", 14, True, False),                 # A
    ("Descrição", 30, False, False),                   # B
    ("Fornecedor", 24, False, False),                  # C
    ("Data da Compra", 14, False, False),              # D
    ("Valor", 16, False, False),                       # E
    ("Forma de Pagamento", 20, False, False),          # F
    ("Status de Aprovação", 18, False, False),         # G
    ("Status de Entrega", 18, False, False),           # H
    ("Etapa (opcional)", 24, False, False),            # I
    ("Subetapa (opcional)", 24, False, False),         # J
    ("Serviço (opcional)", 28, False, False),          # K
    ("Planejado (Valor Previsto)", 22, False, True),   # L
    ("Variação R$", 16, False, True),                  # M
    ("Variação %", 14, False, True),                   # N
    ("Observação", 30, False, False),                  # O
    ("ID_Obra (técnico)", 16, True, False),            # P
    ("ID_Etapa (técnico)", 16, True, False),           # Q
    ("ID_Subetapa (técnico)", 18, True, False),        # R
    ("ID_Servico (técnico)", 18, True, False),         # S
]
COL_COM_ID = 1
COL_COM_DESCRICAO = 2
COL_COM_FORNECEDOR = 3
COL_COM_DATA = 4
COL_COM_VALOR = 5
COL_COM_FORMA_PAGAMENTO = 6
COL_COM_STATUS_APROVACAO = 7
COL_COM_STATUS_ENTREGA = 8
COL_COM_ETAPA = 9
COL_COM_SUBETAPA = 10
COL_COM_SERVICO = 11
COL_COM_PLANEJADO = 12
COL_COM_VARIACAO_REAIS = 13
COL_COM_VARIACAO_PERCENTUAL = 14
COL_COM_OBSERVACAO = 15
COL_COM_ID_OBRA = 16
COL_COM_ID_ETAPA = 17
COL_COM_ID_SUBETAPA = 18
COL_COM_ID_SERVICO = 19

# --------------------------------------------------------------------
# Etapa 7 — colunas da aba Execução (log de medições, REG-007)
# --------------------------------------------------------------------
COLUNAS_EXECUCAO = [
    ("ID (técnico)", 14, True, False),                 # A
    ("Serviço", 30, False, False),                     # B
    ("Data da Medição", 16, False, False),             # C
    ("Quantidade Executada", 20, False, False),        # D
    ("Responsável", 22, False, False),                 # E
    ("ID_Servico (técnico)", 18, True, False),         # F
]
COL_EXE_ID = 1
COL_EXE_SERVICO = 2
COL_EXE_DATA = 3
COL_EXE_QUANTIDADE = 4
COL_EXE_RESPONSAVEL = 5
COL_EXE_ID_SERVICO = 6

COL_SUB_ID = 1
COL_SUB_NOME = 2
COL_SUB_ETAPA = 3
COL_SUB_STATUS = 4
COL_SUB_ID_ETAPA = 5
COL_SUB_TOTAL = 6
COL_SUB_PESO_CONSOLIDADO = 7
COL_SUB_CONTRIBUICAO = 8
# Etapa 8 — cronograma (mesmo bloco de 7 colunas em Etapas e Subetapas)
COL_SUB_DATA_INICIO_PREVISTA = 9
COL_SUB_DATA_FIM_PREVISTA = 10
COL_SUB_DATA_INICIO_REAL = 11
COL_SUB_DATA_FIM_REAL = 12
COL_SUB_DURACAO_PREVISTA = 13
COL_SUB_DURACAO_REAL = 14
COL_SUB_VARIACAO_PRAZO = 15

COL_ETA_ID = 1
COL_ETA_NOME = 2
COL_ETA_ORDEM = 3
COL_ETA_STATUS = 4
COL_ETA_ID_OBRA = 5
COL_ETA_TOTAL = 6
COL_ETA_PESO_CONSOLIDADO = 7
COL_ETA_CONTRIBUICAO = 8
# Etapa 8 — cronograma
COL_ETA_DATA_INICIO_PREVISTA = 9
COL_ETA_DATA_FIM_PREVISTA = 10
COL_ETA_DATA_INICIO_REAL = 11
COL_ETA_DATA_FIM_REAL = 12
COL_ETA_DURACAO_PREVISTA = 13
COL_ETA_DURACAO_REAL = 14
COL_ETA_VARIACAO_PRAZO = 15

# Etapa 8 — formato numérico das 3 colunas calculadas de cronograma:
# dias são NÚMERO inteiro, nunca data (uma diferença de datas formatada
# como data exibiria "01/01/1900" em vez de "0 dias").
FORMATO_DIAS = "0"
FORMATO_DATA_BR = "DD/MM/YYYY"

NOME_INTERVALO_ETAPAS = "Lista_Etapas"
NOME_INTERVALO_SUBETAPAS = "Lista_Subetapas"
NOME_INTERVALO_FINANCEIRO_DESCRICOES = "Lista_Financeiro_Descricoes"  # Etapa 4
NOME_INTERVALO_SERVICOS = "Lista_Servicos"  # Etapa 6 — fonte do dropdown "Serviço" em Compras

# Etapa 5.1 (Correção 1 — expansão real do Excel): cada aba de registro
# passa a ser uma Tabela Excel estruturada nativa (`ws.tables`), em vez
# de um intervalo fixo de linhas. Isso faz o próprio Excel estender
# fórmulas, validações (dropdowns) e formatação quando o Operador digita
# na linha logo abaixo da tabela — sem depender de nenhum teto numérico
# de linhas (ver auditoria pós-Etapa 5, AUD-20/AUD-21). `LINHAS_MODELO`
# continua existindo só como o buffer inicial pré-formatado de fábrica.
NOME_TABELA_ETAPAS = "TabelaEtapas"
NOME_TABELA_SUBETAPAS = "TabelaSubetapas"
NOME_TABELA_SERVICOS = "TabelaServicos"
NOME_TABELA_FINANCEIRO = "TabelaFinanceiro"
NOME_TABELA_PAGAMENTOS = "TabelaPagamentos"
NOME_TABELA_ALTERACOES = "TabelaAlteracoes"
NOME_TABELA_COMPRAS = "TabelaCompras"
NOME_TABELA_EXECUCAO = "TabelaExecucao"  # Etapa 7

# Lista fechada do Status do Serviço (Etapa 3, Seção 18) — mesma fonte
# (`StatusServico`) usada pelo Python, nunca digitada de novo à mão.
_ROTULOS_STATUS_SERVICO = [s.rotulo for s in StatusServico]
_LISTA_STATUS_SERVICO = '"' + ",".join(_ROTULOS_STATUS_SERVICO) + '"'
_ROTULO_CANCELADO = StatusServico.CANCELADO.rotulo
_ROTULO_RETIRADO = StatusServico.RETIRADO_DO_ESCOPO.rotulo
_ROTULO_SUBSTITUIDO = StatusServico.SUBSTITUIDO.rotulo

# Lista fechada do Tipo de FINANCEIRO (Etapa 4, Seção 8) — mesma fonte
# (`TipoLancamentoFinanceiro`) usada pelo Python.
_ROTULOS_TIPO_FINANCEIRO = [t.rotulo for t in TipoLancamentoFinanceiro]
_LISTA_TIPO_FINANCEIRO = '"' + ",".join(_ROTULOS_TIPO_FINANCEIRO) + '"'
_ROTULO_APORTE = TipoLancamentoFinanceiro.APORTE.rotulo
_ROTULO_OUTRAS_ENTRADAS = TipoLancamentoFinanceiro.OUTRAS_ENTRADAS.rotulo
_ROTULO_DESPESA = TipoLancamentoFinanceiro.DESPESA.rotulo
_ROTULO_OUTRAS_SAIDAS = TipoLancamentoFinanceiro.OUTRAS_SAIDAS.rotulo

# Listas fechadas de Tipo/Status de Alteração (Etapa 5, mesma fonte
# usada pelo Python — nunca digitadas de novo à mão).
_ROTULOS_TIPO_ALTERACAO = [t.rotulo for t in TipoAlteracao]
_LISTA_TIPO_ALTERACAO = '"' + ",".join(_ROTULOS_TIPO_ALTERACAO) + '"'
_ROTULOS_STATUS_APROVACAO = [s.rotulo for s in StatusAprovacaoAlteracao]
_LISTA_STATUS_APROVACAO = '"' + ",".join(_ROTULOS_STATUS_APROVACAO) + '"'
_ROTULO_APROVADA = StatusAprovacaoAlteracao.APROVADA.rotulo

# Etapa 7 — listas fechadas de Método de Execução (REG-007) e Status de
# Execução (REG-007.2), mesma fonte (`Enum`) usada pelo Python.
_ROTULOS_METODO_EXECUCAO = [m.rotulo for m in MetodoExecucao]
_LISTA_METODO_EXECUCAO = '"' + ",".join(_ROTULOS_METODO_EXECUCAO) + '"'
_ROTULO_METODO_QUANTITATIVO = MetodoExecucao.QUANTITATIVO.rotulo
_ROTULO_METODO_STATUS = MetodoExecucao.STATUS.rotulo
_ROTULOS_STATUS_EXECUCAO = [s.rotulo for s in StatusExecucao]
_LISTA_STATUS_EXECUCAO = '"' + ",".join(_ROTULOS_STATUS_EXECUCAO) + '"'
_ROTULO_PENDENTE = StatusExecucao.PENDENTE.rotulo
_ROTULO_EM_ANDAMENTO = StatusExecucao.EM_ANDAMENTO.rotulo
_ROTULO_CONCLUIDO = StatusExecucao.CONCLUIDO.rotulo


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
    financeiro = list(base.financeiro.values())
    alteracoes = list(base.alteracoes.values())

    wb = Workbook()
    wb.remove(wb.active)  # remove a aba padrão "Sheet"

    _construir_aba_inicio(wb, obra=obra)
    _construir_aba_etapas(wb, etapas, id_obra=id_obra)
    _construir_aba_subetapas(wb, list(base.subetapas.values()), base.etapas)
    _construir_aba_servicos(wb, list(base.servicos.values()), base.subetapas)
    _construir_aba_execucao(wb, list(base.execucoes.values()), base.servicos)
    _construir_aba_financeiro(wb, financeiro)
    _construir_aba_pagamentos(wb, list(base.pagamentos.values()), base.financeiro)
    _construir_aba_alteracoes(wb, alteracoes)
    _construir_aba_compras(
        wb, list(base.compras.values()), base.fornecedores,
        base.etapas, base.subetapas, base.servicos,
    )
    _construir_aba_resumo_financeiro(wb)
    _construir_aba_base_dados(wb, id_obra=id_obra)
    _criar_intervalos_nomeados(wb)

    wb.active = 0  # abre na aba "Início"
    return wb


# --------------------------------------------------------------------
# Aba: Início (Obra)
# --------------------------------------------------------------------
def _construir_aba_inicio(wb: Workbook, *, obra) -> None:
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
            # `DATE(1900,1,1)`, não a string `"1900-01-01"`: o Excel não
            # lê essa string como literal de data — ele avalia a
            # EXPRESSÃO aritmética `1900-1-1 = 1898`, e o limite
            # entregue passava a ser "serial >= 1898" (≈ 13/03/1905) em
            # vez de 01/01/1900. Defeito original da Etapa 2, apontado
            # pela auditoria integrada das Etapas 1–8 (achado C-2) e
            # corrigido aqui; as validações de data criadas na Etapa 8
            # (`_adicionar_validacao_de_datas`) já nasceram corretas, de
            # modo que o workbook tinha os dois padrões convivendo.
            # Apenas o limite da validação muda — nenhuma regra de
            # negócio, cálculo ou data de Etapa/Subetapa é afetada.
            dv = DataValidation(
                type="date",
                operator="greaterThanOrEqual",
                formula1="DATE(1900,1,1)",
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
    # Etapa 5.1 (Correção 1): referência estruturada à Tabela de Etapas,
    # em vez de um range fixo $2:$N — soma TODAS as Etapas cadastradas,
    # sem teto numérico de linhas (AUD-21).
    celula_rotulo = ws.cell(row=linha, column=1, value="Orçamento Inicial (Previsto)")
    celula_rotulo.font = FONTE_ROTULO_FORM
    titulo_total_etapas = COLUNAS_ETAPAS[COL_ETA_TOTAL - 1][0]
    celula_valor = ws.cell(
        row=linha,
        column=2,
        value=f"=SUM({NOME_TABELA_ETAPAS}[{titulo_total_etapas}])",
    )
    celula_valor.number_format = "#,##0.00"
    celula_valor.border = BORDA_CELULA
    celula_valor.fill = PREENCHIMENTO_CALCULADO
    celula_valor.font = FONTE_CALCULADA
    linha += 1

    # % Execução Física da Obra (Etapa 7, REG-020) — soma da Contribuição
    # na Obra (Execução) de todas as Etapas; cada Etapa já soma a
    # contribuição das suas Subetapas, que por sua vez soma a
    # contribuição dos Serviços Elegíveis (REG-022) com peso efetivo
    # (REG-023/024/025). Mesmo padrão estrutural de "Orçamento Inicial"
    # acima — soma pela Tabela, sem range fixo.
    celula_rotulo = ws.cell(row=linha, column=1, value="% Execução Física da Obra")
    celula_rotulo.font = FONTE_ROTULO_FORM
    titulo_contrib_etapas = COLUNAS_ETAPAS[COL_ETA_CONTRIBUICAO - 1][0]
    # Etapa 8.2: sem nenhum Serviço Elegível (REG-022) o `SUM` de uma
    # coluna vazia devolve 0, e a tela exibia "0,00% executado" onde o
    # Python diz "não calculável" (`percentual_execucao_obra` retorna
    # `None` quando não há elegíveis). Ler 0% como "nada foi executado"
    # numa obra que sequer tem base de cálculo é a mesma leitura inválida
    # que REG-031 proíbe para a divisão por zero — daí o "N/D", a mesma
    # representação já homologada em % Orçamento Consumido e Variação %.
    celula_valor = ws.cell(
        row=linha,
        column=2,
        value=(
            f'=IF({_contagem_servicos_elegiveis()}=0,"N/D",'
            f"SUM({NOME_TABELA_ETAPAS}[{titulo_contrib_etapas}]))"
        ),
    )
    celula_valor.number_format = "0.00%"
    celula_valor.border = BORDA_CELULA
    celula_valor.fill = PREENCHIMENTO_CALCULADO
    celula_valor.font = FONTE_CALCULADA
    linha += 1

    # Etapa 8 — cronograma consolidado da Obra (derivado das Etapas).
    # NÃO sobrescreve "Data Inicial Planejada"/"Data Final Planejada"
    # acima, que continuam sendo o que o Operador declarou para a Obra:
    # estes são valores DERIVADOS, com rótulo explícito ("das Etapas"),
    # para a leitura gerencial "as Etapas cabem no prazo declarado?".
    # Nenhuma automação altera a data declarada (REG-032, "o sistema
    # informa, o Operador decide"). Referências estruturadas de Tabela,
    # sem range fixo — somam todas as Etapas cadastradas.
    titulo_ini_prev = COLUNAS_ETAPAS[COL_ETA_DATA_INICIO_PREVISTA - 1][0]
    titulo_fim_prev = COLUNAS_ETAPAS[COL_ETA_DATA_FIM_PREVISTA - 1][0]
    coluna_ini_prev = f"{NOME_TABELA_ETAPAS}[{titulo_ini_prev}]"
    coluna_fim_prev = f"{NOME_TABELA_ETAPAS}[{titulo_fim_prev}]"

    # COUNT() em volta do MIN/MAX: sem nenhuma data lançada, MIN/MAX
    # retornariam 0 (exibido como 00/01/1900). Vazio é a leitura
    # correta de "não calculável" — nunca uma data inventada.
    # NÃO existe aqui uma célula "Variação de Prazo da Obra": o indicador
    # foi REJEITADO e REMOVIDO por decisão do responsável do projeto em
    # 2026-09-23 (Alternativa D1), por não ter regra de negócio
    # homologada que definisse seu significado e por produzir um número
    # enganoso (`MAX(Fim Real) − MAX(Fim Previsto)` pode tomar operandos
    # de Etapas diferentes). A Variação de Prazo permanece nas colunas
    # das abas Etapas e Subetapas, por registro. Não recriar aqui sem
    # homologação — ver `src/planejamento/calculos.py` e `REG_001`.
    linhas_cronograma = [
        ("Início Previsto (menor data das Etapas)", f'=IF(COUNT({coluna_ini_prev})=0,"",MIN({coluna_ini_prev}))', FORMATO_DATA_BR),
        ("Fim Previsto (maior data das Etapas)", f'=IF(COUNT({coluna_fim_prev})=0,"",MAX({coluna_fim_prev}))', FORMATO_DATA_BR),
    ]
    for rotulo, formula, formato in linhas_cronograma:
        celula_rotulo = ws.cell(row=linha, column=1, value=rotulo)
        celula_rotulo.font = FONTE_ROTULO_FORM
        celula_valor = ws.cell(row=linha, column=2, value=formula)
        celula_valor.number_format = formato
        celula_valor.border = BORDA_CELULA
        celula_valor.fill = PREENCHIMENTO_CALCULADO
        celula_valor.font = FONTE_CALCULADA
        linha += 1

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
            etapa = None
            ws.cell(
                row=r,
                column=COL_ETA_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )

        # Etapa 8 — bloco de cronograma (4 datas + 3 calculadas).
        _escrever_bloco_cronograma(
            ws, r, etapa, primeira_coluna=COL_ETA_DATA_INICIO_PREVISTA
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
        # Etapa 7 — Peso Consolidado/Contribuição: soma dos valores já
        # agregados por Subetapa (mesmo padrão do Total Previsto acima).
        # NÃO é um "% de execução da Etapa" isolado — ver ressalva no
        # cabeçalho da coluna e em `src/execucao/calculos.py`.
        ws.cell(
            row=r,
            column=COL_ETA_PESO_CONSOLIDADO,
            value=(
                f'=IF($B{r}="","",SUMIFS(Subetapas!${get_column_letter(COL_SUB_PESO_CONSOLIDADO)}:'
                f'${get_column_letter(COL_SUB_PESO_CONSOLIDADO)},'
                f'Subetapas!${get_column_letter(COL_SUB_ID_ETAPA)}:'
                f'${get_column_letter(COL_SUB_ID_ETAPA)},$A{r}))'
            ),
        )
        ws.cell(
            row=r,
            column=COL_ETA_CONTRIBUICAO,
            value=(
                f'=IF($B{r}="","",SUMIFS(Subetapas!${get_column_letter(COL_SUB_CONTRIBUICAO)}:'
                f'${get_column_letter(COL_SUB_CONTRIBUICAO)},'
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

    _adicionar_validacao_nome_unico(ws, coluna_nome=COL_ETA_NOME, ultima_linha=ultima_linha, intervalo_nomeado=NOME_INTERVALO_ETAPAS)
    _adicionar_validacao_de_datas(
        ws, primeira_coluna=COL_ETA_DATA_INICIO_PREVISTA, ultima_linha=ultima_linha
    )

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_ETA_TOTAL).number_format = "#,##0.00"
        ws.cell(row=r, column=COL_ETA_TOTAL).fill = PREENCHIMENTO_CALCULADO
        ws.cell(row=r, column=COL_ETA_TOTAL).font = FONTE_CALCULADA
        for coluna in (COL_ETA_PESO_CONSOLIDADO, COL_ETA_CONTRIBUICAO):
            ws.cell(row=r, column=coluna).number_format = "0.00%"
            ws.cell(row=r, column=coluna).fill = PREENCHIMENTO_CALCULADO
            ws.cell(row=r, column=coluna).font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_ETAPAS))
    _registrar_tabela(ws, nome=NOME_TABELA_ETAPAS, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_ETAPAS))
    ws.freeze_panes = "A2"


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
            subetapa = None
            ws.cell(
                row=r,
                column=COL_SUB_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )

        # Etapa 8 — bloco de cronograma (4 datas + 3 calculadas). As
        # Subetapas não tinham NENHUM campo de data antes desta etapa.
        _escrever_bloco_cronograma(
            ws, r, subetapa, primeira_coluna=COL_SUB_DATA_INICIO_PREVISTA
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
        # Etapa 7 — Peso Consolidado/Contribuição: soma direta de
        # Serviços!Peso Efetivo / Serviços!Contribuição na Obra por
        # Subetapa. Sem critério extra de Status: linhas não elegíveis já
        # retornam "" nessas duas colunas em Serviços (SUMIFS/SUM ignoram
        # texto). NÃO é um "% de execução da Subetapa" isolado — ver
        # ressalva no cabeçalho da coluna e em `src/execucao/calculos.py`.
        ws.cell(
            row=r,
            column=COL_SUB_PESO_CONSOLIDADO,
            value=(
                f'=IF($B{r}="","",SUMIFS(Serviços!${get_column_letter(COL_SRV_PESO_EFETIVO)}:'
                f'${get_column_letter(COL_SRV_PESO_EFETIVO)},'
                f'Serviços!${get_column_letter(COL_SRV_ID_SUBETAPA)}:'
                f'${get_column_letter(COL_SRV_ID_SUBETAPA)},$A{r}))'
            ),
        )
        ws.cell(
            row=r,
            column=COL_SUB_CONTRIBUICAO,
            value=(
                f'=IF($B{r}="","",SUMIFS(Serviços!${get_column_letter(COL_SRV_CONTRIBUICAO)}:'
                f'${get_column_letter(COL_SRV_CONTRIBUICAO)},'
                f'Serviços!${get_column_letter(COL_SRV_ID_SUBETAPA)}:'
                f'${get_column_letter(COL_SRV_ID_SUBETAPA)},$A{r}))'
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

    _adicionar_validacao_nome_unico(ws, coluna_nome=COL_SUB_NOME, ultima_linha=ultima_linha, intervalo_nomeado=NOME_INTERVALO_SUBETAPAS)
    _adicionar_validacao_de_datas(
        ws, primeira_coluna=COL_SUB_DATA_INICIO_PREVISTA, ultima_linha=ultima_linha
    )

    for r in range(2, ultima_linha + 1):
        for coluna in (COL_SUB_PESO_CONSOLIDADO, COL_SUB_CONTRIBUICAO):
            ws.cell(row=r, column=coluna).number_format = "0.00%"
            ws.cell(row=r, column=coluna).fill = PREENCHIMENTO_CALCULADO
            ws.cell(row=r, column=coluna).font = FONTE_CALCULADA
        ws.cell(row=r, column=COL_SUB_TOTAL).number_format = "#,##0.00"
        ws.cell(row=r, column=COL_SUB_TOTAL).fill = PREENCHIMENTO_CALCULADO
        ws.cell(row=r, column=COL_SUB_TOTAL).font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_SUBETAPAS))
    _registrar_tabela(ws, nome=NOME_TABELA_SUBETAPAS, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_SUBETAPAS))
    ws.freeze_panes = "A2"


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
    letra_status = get_column_letter(COL_SRV_STATUS)
    letra_metodo = get_column_letter(COL_SRV_METODO_EXECUCAO)
    letra_status_exec = get_column_letter(COL_SRV_STATUS_EXECUCAO)
    letra_qtd_exec = get_column_letter(COL_SRV_QTD_EXECUTADA_ACUM)
    letra_percentual = get_column_letter(COL_SRV_PERCENTUAL_EXECUCAO)
    letra_peso_ajustado = get_column_letter(COL_SRV_PESO_AJUSTADO)
    letra_peso_automatico = get_column_letter(COL_SRV_PESO_AUTOMATICO)
    letra_peso_efetivo = get_column_letter(COL_SRV_PESO_EFETIVO)

    # REG-022: mesmos 3 critérios de exclusão de Status já usados nos
    # totais de Etapas/Subetapas (Cancelado/Retirado do Escopo/
    # Substituído), repetidos como pares SUMIFS sobre a mesma coluna
    # (AND de exclusões) — mais a exigência de Valor Previsto preenchido
    # (REG-022, critério "e": valor orçado válido).
    _criterios_elegibilidade = (
        f'${letra_status}:${letra_status},"<>{_ROTULO_CANCELADO}",'
        f'${letra_status}:${letra_status},"<>{_ROTULO_RETIRADO}",'
        f'${letra_status}:${letra_status},"<>{_ROTULO_SUBSTITUIDO}",'
        f'${letra_vp}:${letra_vp},"<>"'
    )

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
            rotulo_metodo = servico.metodo_execucao.rotulo if servico.metodo_execucao is not None else None
            ws.cell(row=r, column=COL_SRV_METODO_EXECUCAO, value=rotulo_metodo)
            rotulo_status_exec = servico.status_execucao.rotulo if servico.status_execucao is not None else None
            ws.cell(row=r, column=COL_SRV_STATUS_EXECUCAO, value=rotulo_status_exec)
            # `ServicoOrcamento.peso_ajustado` (Python) usa escala 0–100
            # (mesma convenção de `peso_automatico_bruto`/`pesos_efetivos_
            # obra`, REG-008) — convertido aqui para razão 0–1, mesma
            # convenção já usada em TODA célula "0.00%" deste arquivo
            # (Variação % de Compras, % Orçamento Consumido).
            peso_ajustado_razao = (
                servico.peso_ajustado / 100 if servico.peso_ajustado is not None else None
            )
            ws.cell(row=r, column=COL_SRV_PESO_AJUSTADO, value=peso_ajustado_razao)
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

        # ---------------------------------------------------------
        # Etapa 7 — Execução/Medições (Progresso Físico)
        # ---------------------------------------------------------
        # Qtd. Executada (acumulada, REG-007): soma de TabelaExecucao
        # para este Serviço (decisão de implementação 4 — medições se
        # somam, não se substituem).
        ws.cell(
            row=r,
            column=COL_SRV_QTD_EXECUTADA_ACUM,
            value=(
                f'=IF($A{r}="","",SUMIFS(Execução!${get_column_letter(COL_EXE_QUANTIDADE)}:'
                f'${get_column_letter(COL_EXE_QUANTIDADE)},'
                f'Execução!${get_column_letter(COL_EXE_ID_SERVICO)}:'
                f'${get_column_letter(COL_EXE_ID_SERVICO)},$A{r}))'
            ),
        )
        # % Execução do Serviço (REG-007, Modelo Híbrido) — razão 0–1:
        # Quantitativo = Qtd. Executada / Quantidade Orçada;
        # Status = tabela fixa homologada (Pendente=0%, Em andamento=
        # 50%, Concluído=100%, REG-007.2). Sem Método definido: "".
        ws.cell(
            row=r,
            column=COL_SRV_PERCENTUAL_EXECUCAO,
            value=(
                f'=IF($A{r}="","",'
                f'IF(${letra_metodo}{r}="{_ROTULO_METODO_QUANTITATIVO}",'
                f'IF(OR(${letra_qtd}{r}="",${letra_qtd}{r}=0),"",'
                f'${letra_qtd_exec}{r}/${letra_qtd}{r}),'
                f'IF(${letra_metodo}{r}="{_ROTULO_METODO_STATUS}",'
                f'IF(${letra_status_exec}{r}="{_ROTULO_PENDENTE}",0,'
                f'IF(${letra_status_exec}{r}="{_ROTULO_EM_ANDAMENTO}",0.5,'
                f'IF(${letra_status_exec}{r}="{_ROTULO_CONCLUIDO}",1,""))),'
                f'"")))'
            ),
        )
        # Peso Automático (REG-008) — razão 0–1: Valor Previsto do
        # Serviço / Σ Valor Previsto dos Serviços Elegíveis da Obra
        # (denominador sempre global, REG-022). "" quando não elegível.
        # Etapa 8.2 (D-COM-2): o denominador (Σ Valor Previsto dos
        # Serviços Elegíveis) pode ser ZERO — basta que todos os
        # elegíveis estejam orçados em 0. Sem guarda, o Excel devolvia
        # `#DIV/0!`, que se propagava por Peso Efetivo → Contribuição →
        # Subetapas → Etapas → `Início!B9`, contrariando REG-031
        # (divisão por zero é "não calculável", nunca erro). O Python já
        # tratava: `peso_automatico_bruto` retorna `None` quando o total
        # é zero. "N/D" é a mesma representação já homologada em
        # REG-031 (% Orçamento Consumido) e REG-010 (Variação %).
        ws.cell(
            row=r,
            column=COL_SRV_PESO_AUTOMATICO,
            value=(
                f'=IF(OR($A{r}="",${letra_status}{r}="{_ROTULO_CANCELADO}",'
                f'${letra_status}{r}="{_ROTULO_RETIRADO}",${letra_status}{r}="{_ROTULO_SUBSTITUIDO}",'
                f'${letra_vp}{r}=""),"",'
                f'IF(SUMIFS(${letra_vp}:${letra_vp},{_criterios_elegibilidade})=0,"N/D",'
                f'${letra_vp}{r}/SUMIFS(${letra_vp}:${letra_vp},{_criterios_elegibilidade})))'
            ),
        )
        # Peso Efetivo (REG-023/024/025) — razão 0–1: protege peso manual
        # (Peso Ajustado preenchido); redistribui proporcionalmente ao
        # Peso Automático apenas entre os Serviços elegíveis sem peso
        # manual (REG-024). Quando 100% dos elegíveis são manuais e não
        # somam 100% (REG-025), Excel não bloqueia a entrada (sem VBA,
        # ver limitação registrada no relatório) — mostra o próprio Peso
        # Ajustado tal como informado, deixando a inconsistência visível
        # para o Operador corrigir (mesmo princípio "sistema informa" já
        # usado nas demais etapas).
        # Etapa 8.2 (D-COM-2): quando a base proporcional é zero (todos
        # os automáticos elegíveis com Peso Automático "N/D", isto é,
        # todos orçados em 0), o Excel devolvia vazio enquanto o Python
        # distribuía a faixa restante IGUALMENTE entre os automáticos
        # (`pesos_efetivos_obra`, ramo `total_bruto_automaticos == 0`,
        # Etapa 7). Os dois motores passam a fazer o mesmo — nenhuma
        # regra foi criada aqui: a divisão igualitária já era o
        # comportamento implementado e testado no Python.
        soma_automaticos = (
            f'SUMIFS(${letra_peso_automatico}:${letra_peso_automatico},'
            f'{_criterios_elegibilidade},${letra_peso_ajustado}:${letra_peso_ajustado},"")'
        )
        soma_manuais = (
            f'SUMIFS(${letra_peso_ajustado}:${letra_peso_ajustado},{_criterios_elegibilidade},'
            f'${letra_peso_ajustado}:${letra_peso_ajustado},"<>")'
        )
        qtd_automaticos = _contagem_servicos_elegiveis(somente_automaticos=True)
        ws.cell(
            row=r,
            column=COL_SRV_PESO_EFETIVO,
            value=(
                f'=IF(OR($A{r}="",${letra_status}{r}="{_ROTULO_CANCELADO}",'
                f'${letra_status}{r}="{_ROTULO_RETIRADO}",${letra_status}{r}="{_ROTULO_SUBSTITUIDO}",'
                f'${letra_vp}{r}=""),"",'
                f'IF(${letra_peso_ajustado}{r}<>"",${letra_peso_ajustado}{r},'
                f'IF({soma_automaticos}=0,'
                f'IF({qtd_automaticos}=0,"N/D",(1-{soma_manuais})/{qtd_automaticos}),'
                f'${letra_peso_automatico}{r}/{soma_automaticos}*(1-{soma_manuais}))))'
            ),
        )
        # Contribuição na Obra = Peso Efetivo × % Execução do Serviço
        # (pontos percentuais da Obra, REG-020). NÃO é o "% da Subetapa/
        # Etapa" isolado (ver ressalva no cabeçalho da coluna).
        ws.cell(
            row=r,
            column=COL_SRV_CONTRIBUICAO,
            value=(
                f'=IF(OR(${letra_peso_efetivo}{r}="",${letra_percentual}{r}=""),"",'
                f'${letra_peso_efetivo}{r}*${letra_percentual}{r})'
            ),
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

    # Etapa 6: Compras passa a vincular Serviço pelo nome (Descrição,
    # mesmo padrão MATCH de Subetapa→Etapa) — mesma mitigação de AUD-18
    # (Etapa 5.1) aplicada aqui para a nova coluna referenciada por nome.
    _adicionar_validacao_nome_unico(
        ws, coluna_nome=COL_SRV_DESCRICAO, ultima_linha=ultima_linha,
        intervalo_nomeado=NOME_INTERVALO_SERVICOS, titulo_coluna="Descrição",
    )

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

    # Etapa 7 — dropdown "Método de Execução" (REG-007, domínio fechado).
    dv_metodo = DataValidation(
        type="list", formula1=_LISTA_METODO_EXECUCAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Método inválido",
        error="Selecione um dos métodos oficiais: " + ", ".join(_ROTULOS_METODO_EXECUCAO) + ".",
    )
    ws.add_data_validation(dv_metodo)
    dv_metodo.add(f"{letra_metodo}2:{letra_metodo}{ultima_linha}")

    # Dropdown "Status de Execução" (REG-007.2, domínio fechado) —
    # relevante apenas quando Método = Status; disponível sempre, sem
    # dependência condicional entre dropdowns (mesmo princípio de campos
    # opcionais/independentes já usado em Compras, Etapa 6).
    dv_status_exec = DataValidation(
        type="list", formula1=_LISTA_STATUS_EXECUCAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Status de Execução inválido",
        error="Selecione um dos status oficiais: " + ", ".join(_ROTULOS_STATUS_EXECUCAO) + ".",
    )
    ws.add_data_validation(dv_status_exec)
    dv_status_exec.add(f"{letra_status_exec}2:{letra_status_exec}{ultima_linha}")

    # Peso Ajustado (manual, REG-023): razão entre 0 e 1 (0% a 100%).
    dv_peso_ajustado = DataValidation(
        type="decimal", operator="between", formula1="0", formula2="1", allow_blank=True,
        showErrorMessage=True, errorTitle="Peso inválido",
        error="Informe um percentual entre 0% e 100%.",
    )
    ws.add_data_validation(dv_peso_ajustado)
    dv_peso_ajustado.add(f"{letra_peso_ajustado}2:{letra_peso_ajustado}{ultima_linha}")

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
        ws.cell(row=r, column=COL_SRV_QTD_EXECUTADA_ACUM).number_format = "#,##0.00"
        for coluna in (
            COL_SRV_PERCENTUAL_EXECUCAO,
            COL_SRV_PESO_AJUSTADO,
            COL_SRV_PESO_AUTOMATICO,
            COL_SRV_PESO_EFETIVO,
            COL_SRV_CONTRIBUICAO,
        ):
            ws.cell(row=r, column=coluna).number_format = "0.00%"

    for indice_coluna, (_titulo, _largura, _oculta, calculada) in enumerate(COLUNAS_SERVICOS, start=1):
        if not calculada:
            continue
        for r in range(2, ultima_linha + 1):
            celula = ws.cell(row=r, column=indice_coluna)
            celula.fill = PREENCHIMENTO_CALCULADO
            celula.font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_SERVICOS))
    _registrar_tabela(ws, nome=NOME_TABELA_SERVICOS, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_SERVICOS))
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Execução (Etapa 7) — log de medições (REG-007, Método Quantitativo)
# --------------------------------------------------------------------
def _construir_aba_execucao(wb: Workbook, execucoes: list, servicos_por_id: dict) -> None:
    """
    1 linha = 1 medição (`ExecucaoMedicao`). Vínculo com o Serviço pelo
    nome (Descrição), mesmo padrão de Compras (Etapa 6) — o ID técnico
    fica em uma coluna oculta resolvida por INDEX/MATCH. Quantidade
    Executada acumulada por Serviço, % de Execução do Serviço, Peso e
    Contribuição na Obra são calculados na aba Serviços (colunas
    O–T) — esta aba é só o registro/lançamento das medições em si.
    """
    ws = wb.create_sheet("Execução")
    _escrever_cabecalho(ws, COLUNAS_EXECUCAO)

    ultima_linha = 1 + len(execucoes) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["EXECUCAO_MEDICOES"]
    letra_servico = get_column_letter(COL_EXE_SERVICO)

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(execucoes):
            medicao = execucoes[indice]
            servico = servicos_por_id.get(medicao.id_servico)
            ws.cell(row=r, column=COL_EXE_ID, value=medicao.id)
            ws.cell(row=r, column=COL_EXE_SERVICO, value=getattr(servico, "descricao", None))
            celula_data = ws.cell(row=r, column=COL_EXE_DATA, value=medicao.data_medicao)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_EXE_QUANTIDADE, value=medicao.quantidade_executada)
            ws.cell(row=r, column=COL_EXE_RESPONSAVEL, value=medicao.responsavel)
        else:
            ws.cell(
                row=r,
                column=COL_EXE_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_EXE_DATA).number_format = "DD/MM/YYYY"

        # Coluna SEMPRE calculada por fórmula (linha literal ou não):
        ws.cell(
            row=r,
            column=COL_EXE_ID_SERVICO,
            value=(
                f'=IF(${letra_servico}{r}="","",'
                f'INDEX(Serviços!$A:$A,MATCH(${letra_servico}{r},Serviços!$B:$B,0)))'
            ),
        )

    # Dropdown "Serviço" — nomes amigáveis (nunca IDs); mesma lista
    # nomeada já usada pelo dropdown de Serviço em Compras (Etapa 6).
    dv_servico = DataValidation(
        type="list", formula1=NOME_INTERVALO_SERVICOS, allow_blank=True,
        showErrorMessage=True, errorTitle="Serviço inválido",
        error="Selecione um Serviço já cadastrado na aba Serviços.",
    )
    ws.add_data_validation(dv_servico)
    dv_servico.add(f"{letra_servico}2:{letra_servico}{ultima_linha}")

    # Quantidade Executada: numérica e não negativa (mesmo padrão de
    # Quantidade Orçada/Valor — Etapas 3/4/6).
    dv_quantidade = DataValidation(
        type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
        showErrorMessage=True, errorTitle="Quantidade inválida",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_quantidade)
    dv_quantidade.add(f"D2:D{ultima_linha}")

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_EXE_QUANTIDADE).number_format = "#,##0.00"

    for indice_coluna, (_titulo, _largura, _oculta, calculada) in enumerate(COLUNAS_EXECUCAO, start=1):
        if not calculada:
            continue
        for r in range(2, ultima_linha + 1):
            celula = ws.cell(row=r, column=indice_coluna)
            celula.fill = PREENCHIMENTO_CALCULADO
            celula.font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_EXECUCAO))
    _registrar_tabela(ws, nome=NOME_TABELA_EXECUCAO, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_EXECUCAO))
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Financeiro (Etapa 4) — Aporte / Outras Entradas / Despesa-Custo /
# Outras Saídas (Seções 8/19/27)
# --------------------------------------------------------------------
def _construir_aba_financeiro(wb: Workbook, lancamentos: list) -> None:
    ws = wb.create_sheet("Financeiro")
    _escrever_cabecalho(ws, COLUNAS_FINANCEIRO)

    ultima_linha = 1 + len(lancamentos) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["FINANCEIRO"]

    letra_tipo = get_column_letter(COL_FIN_TIPO)
    letra_valor = get_column_letter(COL_FIN_VALOR)
    letra_custo = get_column_letter(COL_FIN_CUSTO_REALIZADO)
    letra_pago = get_column_letter(COL_FIN_TOTAL_PAGO)
    letra_id = get_column_letter(COL_FIN_ID)

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(lancamentos):
            lancamento = lancamentos[indice]
            ws.cell(row=r, column=COL_FIN_ID, value=lancamento.id)
            ws.cell(row=r, column=COL_FIN_TIPO, value=lancamento.tipo.rotulo)
            celula_data = ws.cell(row=r, column=COL_FIN_DATA, value=lancamento.data)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_FIN_DESCRICAO, value=lancamento.descricao)
            ws.cell(row=r, column=COL_FIN_VALOR, value=lancamento.valor)
            ws.cell(row=r, column=COL_FIN_SITUACAO, value=lancamento.situacao)
            ws.cell(row=r, column=COL_FIN_OBSERVACAO, value=lancamento.observacao)
        else:
            ws.cell(
                row=r,
                column=COL_FIN_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_FIN_DATA).number_format = "DD/MM/YYYY"

        # Colunas SEMPRE calculadas por fórmula (linha literal ou não) —
        # mesmo raciocínio da aba Serviços (Etapa 3): continuam corretas
        # se o Operador editar Tipo/Valor diretamente no Excel depois.
        ws.cell(
            row=r,
            column=COL_FIN_ENTRADA_SAIDA,
            value=(
                f'=IF(${letra_tipo}{r}="","",'
                f'IF(${letra_tipo}{r}="{_ROTULO_APORTE}","Entrada",'
                f'IF(${letra_tipo}{r}="{_ROTULO_OUTRAS_ENTRADAS}","Entrada",'
                f'IF(${letra_tipo}{r}="{_ROTULO_OUTRAS_SAIDAS}","Saída",'
                f'"Custo (Caixa só no Pagamento)"))))'
            ),
        )
        ws.cell(
            row=r,
            column=COL_FIN_APORTE,
            value=f'=IF(${letra_tipo}{r}="{_ROTULO_APORTE}",${letra_valor}{r},"")',
        )
        ws.cell(
            row=r,
            column=COL_FIN_CUSTO_REALIZADO,
            value=f'=IF(${letra_tipo}{r}="{_ROTULO_DESPESA}",${letra_valor}{r},"")',
        )
        ws.cell(
            row=r,
            column=COL_FIN_TOTAL_PAGO,
            value=(
                f'=IF(${letra_tipo}{r}="{_ROTULO_DESPESA}",'
                f'SUMIFS(Pagamentos!${get_column_letter(COL_PAG_VALOR)}:${get_column_letter(COL_PAG_VALOR)},'
                f'Pagamentos!${get_column_letter(COL_PAG_ID_FINANCEIRO)}:${get_column_letter(COL_PAG_ID_FINANCEIRO)},'
                f'${letra_id}{r}),"")'
            ),
        )
        ws.cell(
            row=r,
            column=COL_FIN_A_PAGAR,
            value=f'=IF(${letra_tipo}{r}="{_ROTULO_DESPESA}",${letra_custo}{r}-${letra_pago}{r},"")',
        )
        ws.cell(
            row=r,
            column=COL_FIN_ID_OBRA,
            value=f'=IF(${letra_tipo}{r}="","",Base_Dados!$B$2)',
        )

    # Dropdown "Tipo" — domínio fechado homologado na Etapa 4 (Seção 8).
    dv_tipo = DataValidation(
        type="list",
        formula1=_LISTA_TIPO_FINANCEIRO,
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Tipo inválido",
        error="Selecione um dos tipos oficiais: " + ", ".join(_ROTULOS_TIPO_FINANCEIRO) + ".",
    )
    ws.add_data_validation(dv_tipo)
    dv_tipo.add(f"B2:B{ultima_linha}")

    # Valor: numérico e não negativo — o sinal vem do Tipo (Seção 21).
    dv_valor = DataValidation(
        type="decimal",
        operator="greaterThanOrEqual",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_valor)
    dv_valor.add(f"E2:E{ultima_linha}")

    _adicionar_validacao_nome_unico(
        ws, coluna_nome=COL_FIN_DESCRICAO, ultima_linha=ultima_linha,
        intervalo_nomeado=NOME_INTERVALO_FINANCEIRO_DESCRICOES, titulo_coluna="Descrição",
    )

    for r in range(2, ultima_linha + 1):
        for coluna in (
            COL_FIN_VALOR,
            COL_FIN_APORTE,
            COL_FIN_CUSTO_REALIZADO,
            COL_FIN_TOTAL_PAGO,
            COL_FIN_A_PAGAR,
        ):
            ws.cell(row=r, column=coluna).number_format = FORMATO_MOEDA_BR

    for indice_coluna, (_titulo, _largura, _oculta, calculada) in enumerate(COLUNAS_FINANCEIRO, start=1):
        if not calculada:
            continue
        for r in range(2, ultima_linha + 1):
            celula = ws.cell(row=r, column=indice_coluna)
            celula.fill = PREENCHIMENTO_CALCULADO
            celula.font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_FINANCEIRO))
    _registrar_tabela(ws, nome=NOME_TABELA_FINANCEIRO, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_FINANCEIRO))
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Pagamentos (Etapa 4, Seção 20) — separada de Financeiro
# --------------------------------------------------------------------
def _construir_aba_pagamentos(wb: Workbook, pagamentos: list, financeiro_por_id: dict) -> None:
    ws = wb.create_sheet("Pagamentos")
    _escrever_cabecalho(ws, COLUNAS_PAGAMENTOS)

    ultima_linha = 1 + len(pagamentos) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["PAGAMENTOS"]

    letra_lancamento = get_column_letter(COL_PAG_LANCAMENTO)

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(pagamentos):
            pagamento = pagamentos[indice]
            lancamento = financeiro_por_id.get(pagamento.id_financeiro)
            ws.cell(row=r, column=COL_PAG_ID, value=pagamento.id)
            ws.cell(row=r, column=COL_PAG_LANCAMENTO, value=getattr(lancamento, "descricao", None))
            celula_data = ws.cell(row=r, column=COL_PAG_DATA, value=pagamento.data)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_PAG_VALOR, value=pagamento.valor)
            ws.cell(row=r, column=COL_PAG_OBSERVACAO, value=pagamento.observacao)
        else:
            ws.cell(
                row=r,
                column=COL_PAG_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_PAG_DATA).number_format = "DD/MM/YYYY"

        # Vínculo técnico SEMPRE por fórmula (linha literal ou não) — mesmo
        # padrão de Subetapas/Serviços (Etapa 2/3): resolve pelo nome
        # amigável (Descrição do lançamento) escolhido no dropdown, nunca
        # por um ID digitado. Mesma limitação já documentada nas Etapas
        # anteriores para nomes duplicados (ver relatório da Etapa 4).
        ws.cell(
            row=r,
            column=COL_PAG_ID_FINANCEIRO,
            value=(
                f'=IF(${letra_lancamento}{r}="","",'
                f'INDEX(Financeiro!$A:$A,MATCH(${letra_lancamento}{r},Financeiro!$D:$D,0)))'
            ),
        )

    # Dropdown "Lançamento" — nomes amigáveis (Descrição), nunca IDs.
    dv_lancamento = DataValidation(
        type="list",
        formula1=NOME_INTERVALO_FINANCEIRO_DESCRICOES,
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Lançamento inválido",
        error="Selecione um lançamento já cadastrado na aba Financeiro.",
    )
    ws.add_data_validation(dv_lancamento)
    dv_lancamento.add(f"B2:B{ultima_linha}")

    dv_valor = DataValidation(
        type="decimal",
        operator="greaterThanOrEqual",
        formula1="0",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_valor)
    dv_valor.add(f"D2:D{ultima_linha}")

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_PAG_VALOR).number_format = FORMATO_MOEDA_BR

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_PAGAMENTOS))
    _registrar_tabela(ws, nome=NOME_TABELA_PAGAMENTOS, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_PAGAMENTOS))
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Resumo Financeiro (Etapa 4, Seção 28) — resumo OPERACIONAL, não o
# Dashboard Gerencial definitivo (Seção 28/30)
# --------------------------------------------------------------------
def _construir_aba_resumo_financeiro(wb: Workbook) -> None:
    ws = wb.create_sheet("Resumo Financeiro")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 22

    titulo = ws.cell(row=1, column=1, value="Resumo Financeiro")
    titulo.font = FONTE_CABECALHO
    titulo.fill = PREENCHIMENTO_CABECALHO
    ws.cell(row=1, column=2).fill = PREENCHIMENTO_CABECALHO
    ws.row_dimensions[1].height = 24

    # Etapa 5.1 (Correção 1, AUD-21): todos os totais abaixo usam
    # referência estruturada à Tabela de Financeiro/Alterações
    # (`TabelaX[Coluna]`), que sempre cobre exatamente as linhas de
    # dado da tabela — sem teto numérico de linhas e sem risco de
    # ignorar silenciosamente registros além de um buffer inicial.
    titulo_aporte = COLUNAS_FINANCEIRO[COL_FIN_APORTE - 1][0]
    titulo_custo = COLUNAS_FINANCEIRO[COL_FIN_CUSTO_REALIZADO - 1][0]
    titulo_pago = COLUNAS_FINANCEIRO[COL_FIN_TOTAL_PAGO - 1][0]
    titulo_a_pagar = COLUNAS_FINANCEIRO[COL_FIN_A_PAGAR - 1][0]
    titulo_tipo_fin = COLUNAS_FINANCEIRO[COL_FIN_TIPO - 1][0]
    titulo_valor_fin = COLUNAS_FINANCEIRO[COL_FIN_VALOR - 1][0]
    titulo_impacto_alt = COLUNAS_ALTERACOES[COL_ALT_IMPACTO_ORCAMENTO - 1][0]
    titulo_status_alt = COLUNAS_ALTERACOES[COL_ALT_STATUS - 1][0]

    linhas_moeda: list[int] = []

    def _linha(rotulo: str, formula_ou_valor, *, moeda: bool = True) -> None:
        nonlocal linha_atual
        ws.cell(row=linha_atual, column=1, value=rotulo).font = FONTE_ROTULO_FORM
        celula = ws.cell(row=linha_atual, column=2, value=formula_ou_valor)
        celula.border = BORDA_CELULA
        celula.fill = PREENCHIMENTO_CALCULADO
        celula.font = FONTE_CALCULADA
        if moeda:
            linhas_moeda.append(linha_atual)
        linha_atual += 1

    linha_atual = 2
    linha_orcamento_inicial = linha_atual
    _linha("Orçamento Inicial (Previsto)", "=Início!$B$8")
    linha_aportes = linha_atual
    _linha("Aportes", f"=SUM({NOME_TABELA_FINANCEIRO}[{titulo_aporte}])")
    linha_alteracoes_aprovadas = linha_atual
    _linha(
        "Alterações Aprovadas",
        f'=SUMIFS({NOME_TABELA_ALTERACOES}[{titulo_impacto_alt}],'
        f'{NOME_TABELA_ALTERACOES}[{titulo_status_alt}],"{_ROTULO_APROVADA}")',
    )
    linha_orcamento_vigente = linha_atual
    _linha(
        "Orçamento Vigente",
        f"=B{linha_orcamento_inicial}+B{linha_aportes}+B{linha_alteracoes_aprovadas}",
    )
    linha_custo = linha_atual
    _linha("Custo Realizado", f"=SUM({NOME_TABELA_FINANCEIRO}[{titulo_custo}])")
    linha_saldo_orc = linha_atual
    _linha("Saldo Orçamentário", f"=B{linha_orcamento_vigente}-B{linha_custo}")
    _linha(
        "% Orçamento Consumido",
        f'=IF(B{linha_orcamento_vigente}=0,"N/D",B{linha_custo}/B{linha_orcamento_vigente})',
        moeda=False,
    )
    linha_percentual = linha_atual - 1
    linha_outras_entradas = linha_atual
    _linha(
        "Outras Entradas",
        f'=SUMIF({NOME_TABELA_FINANCEIRO}[{titulo_tipo_fin}],"{_ROTULO_OUTRAS_ENTRADAS}",'
        f'{NOME_TABELA_FINANCEIRO}[{titulo_valor_fin}])',
    )
    linha_outras_saidas = linha_atual
    _linha(
        "Outras Saídas",
        f'=SUMIF({NOME_TABELA_FINANCEIRO}[{titulo_tipo_fin}],"{_ROTULO_OUTRAS_SAIDAS}",'
        f'{NOME_TABELA_FINANCEIRO}[{titulo_valor_fin}])',
    )
    linha_total_entradas = linha_atual
    _linha("Total de Entradas", f"=B{linha_aportes}+B{linha_outras_entradas}")
    linha_total_pago = linha_atual
    _linha("Total Pago", f"=SUM({NOME_TABELA_FINANCEIRO}[{titulo_pago}])")
    linha_total_saidas = linha_atual
    _linha("Total de Saídas", f"=B{linha_total_pago}+B{linha_outras_saidas}")
    linha_saldo_caixa = linha_atual
    _linha("Saldo de Caixa", f"=B{linha_total_entradas}-B{linha_total_saidas}")
    _linha("Total A Pagar", f"=SUM({NOME_TABELA_FINANCEIRO}[{titulo_a_pagar}])")
    linha_estouro = linha_atual
    _linha(
        "Estouro de Orçamento (indicador Operador-only)",
        f'=IF(B{linha_saldo_orc}<0,"SIM","NÃO")',
        moeda=False,
    )

    for linha in linhas_moeda:
        ws.cell(row=linha, column=2).number_format = FORMATO_MOEDA_BR
    ws.cell(row=linha_percentual, column=2).number_format = "0.00%"

    # Notas — pendências explícitas (Etapa 4, Seções 4/29/30), texto
    # simples (não fórmula), sem cor/alerta (mesmo princípio da Seção 31
    # da Etapa 3: nenhuma formatação condicional foi criada).
    linha_atual += 1
    nota1 = ws.cell(
        row=linha_atual,
        column=1,
        value=(
            "Nota da Etapa 5: Orçamento Vigente = Orçamento Inicial + Aportes + "
            "Alterações Aprovadas (aba Alterações, REG-017 completo)."
        ),
    )
    nota1.font = FONTE_CALCULADA
    ws.merge_cells(start_row=linha_atual, start_column=1, end_row=linha_atual, end_column=2)
    linha_atual += 1
    nota2 = ws.cell(
        row=linha_atual,
        column=1,
        value=(
            "Nota: 'Estouro de Orçamento' é Operador-only por especificação (Seções 29/30) — "
            "o mecanismo técnico de restrição por perfil ainda não existe (SEC_001, [H])."
        ),
    )
    nota2.font = FONTE_CALCULADA
    ws.merge_cells(start_row=linha_atual, start_column=1, end_row=linha_atual, end_column=2)

    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Alterações (Etapa 5) — Escopo / Prazo / Orçamento, com Status de
# Aprovação (REG-012 fechado) — fecha o Orçamento Vigente (REG-017)
# --------------------------------------------------------------------
def _construir_aba_alteracoes(wb: Workbook, alteracoes: list) -> None:
    ws = wb.create_sheet("Alterações")
    _escrever_cabecalho(ws, COLUNAS_ALTERACOES)

    ultima_linha = 1 + len(alteracoes) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["ALTERACOES"]

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(alteracoes):
            alteracao = alteracoes[indice]
            ws.cell(row=r, column=COL_ALT_ID, value=alteracao.id)
            rotulo_tipo = alteracao.tipo_alteracao.rotulo if alteracao.tipo_alteracao is not None else None
            ws.cell(row=r, column=COL_ALT_TIPO, value=rotulo_tipo)
            celula_data = ws.cell(row=r, column=COL_ALT_DATA, value=alteracao.data)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_ALT_DESCRICAO, value=alteracao.descricao)
            ws.cell(row=r, column=COL_ALT_IMPACTO_ORCAMENTO, value=alteracao.impacto_orcamento)
            ws.cell(row=r, column=COL_ALT_IMPACTO_PRAZO, value=alteracao.impacto_prazo_dias)
            rotulo_status = alteracao.status_aprovacao.rotulo if alteracao.status_aprovacao is not None else None
            ws.cell(row=r, column=COL_ALT_STATUS, value=rotulo_status)
            ws.cell(row=r, column=COL_ALT_SOLICITANTE, value=alteracao.solicitante)
        else:
            ws.cell(
                row=r,
                column=COL_ALT_ID,
                value=f'=IF($D{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_ALT_DATA).number_format = "DD/MM/YYYY"

        # ID_Obra: sempre fórmula, linha literal ou não (mesmo padrão de Financeiro).
        ws.cell(
            row=r,
            column=COL_ALT_ID_OBRA,
            value=f'=IF($D{r}="","",Base_Dados!$B$2)',
        )

    # Dropdown "Tipo" — domínio fechado (Etapa 5).
    dv_tipo = DataValidation(
        type="list", formula1=_LISTA_TIPO_ALTERACAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Tipo inválido",
        error="Selecione um dos tipos oficiais: " + ", ".join(_ROTULOS_TIPO_ALTERACAO) + ".",
    )
    ws.add_data_validation(dv_tipo)
    dv_tipo.add(f"B2:B{ultima_linha}")

    # Dropdown "Status de Aprovação" — domínio fechado (Etapa 5).
    dv_status = DataValidation(
        type="list", formula1=_LISTA_STATUS_APROVACAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Status inválido",
        error="Selecione um dos status oficiais: " + ", ".join(_ROTULOS_STATUS_APROVACAO) + ".",
    )
    ws.add_data_validation(dv_status)
    dv_status.add(f"G2:G{ultima_linha}")

    # NENHUMA validação de sinal em Impacto no Orçamento/Prazo (Etapa 5,
    # decisão homologada) — diferente de Financeiro!Valor (Etapa 4,
    # Seção 21): aqui o sinal negativo é um dado válido (redução).

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_ALT_IMPACTO_ORCAMENTO).number_format = FORMATO_MOEDA_BR

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_ALTERACOES))
    _registrar_tabela(ws, nome=NOME_TABELA_ALTERACOES, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_ALTERACOES))
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------
# Aba: Compras (Etapa 6) — registro de compras/pedidos, com vínculos
# opcionais e independentes a Etapa/Subetapa/Serviço (Seção 5, regras
# 5/6 da homologação: cada "item" é uma linha desta aba). Compra NÃO
# cria lançamento financeiro nem altera Orçamento/Execução (regras
# 2/7/8/9) — o único cálculo é a Variação contra o Serviço vinculado,
# quando houver (ver `src/compras/calculos.py`).
# --------------------------------------------------------------------
def _construir_aba_compras(
    wb: Workbook,
    compras: list,
    fornecedores_por_id: dict,
    etapas_por_id: dict,
    subetapas_por_id: dict,
    servicos_por_id: dict,
) -> None:
    ws = wb.create_sheet("Compras")
    _escrever_cabecalho(ws, COLUNAS_COMPRAS)

    ultima_linha = 1 + len(compras) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["COMPRAS"]

    letra_valor = get_column_letter(COL_COM_VALOR)
    letra_etapa = get_column_letter(COL_COM_ETAPA)
    letra_subetapa = get_column_letter(COL_COM_SUBETAPA)
    letra_servico = get_column_letter(COL_COM_SERVICO)
    letra_id_servico = get_column_letter(COL_COM_ID_SERVICO)
    letra_planejado = get_column_letter(COL_COM_PLANEJADO)

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(compras):
            compra = compras[indice]
            ws.cell(row=r, column=COL_COM_ID, value=compra.id)
            ws.cell(row=r, column=COL_COM_DESCRICAO, value=compra.descricao)
            # Fornecedores é módulo auxiliar sem aba própria nesta etapa
            # (MOD_001) — o nome é escrito como texto simples a partir do
            # cadastro em memória (`BaseDados.fornecedores`), sem dropdown
            # validado (regra 3: "compra pode existir sem fornecedor
            # cadastrado").
            fornecedor = fornecedores_por_id.get(compra.id_fornecedor) if compra.id_fornecedor else None
            ws.cell(row=r, column=COL_COM_FORNECEDOR, value=getattr(fornecedor, "nome_razao_social", None))
            # Etapa 8.2 (D-COM-1) — vínculos opcionais escritos pelo NOME
            # amigável, mesmo padrão de todas as outras abas (Subetapas→
            # Etapa, Serviços→Subetapa, Execução→Serviço, Pagamentos→
            # Lançamento). Antes desta correção, uma Compra que tinha
            # `id_servico` no Python chegava ao Excel com a coluna
            # "Serviço" VAZIA: a coluna técnica ID_Servico (resolvida por
            # MATCH sobre este nome) ficava vazia e, com ela, Planejado,
            # Variação R$ e Variação % — ou seja, REG-010 simplesmente não
            # era calculada sobre dados existentes. Detectado pela
            # validação Excel/COM da Etapa 8.
            # Os IDs técnicos continuam internos (colunas ocultas Q/R/S,
            # sempre por fórmula) — aqui só entra o rótulo amigável.
            etapa = etapas_por_id.get(compra.id_etapa) if compra.id_etapa else None
            ws.cell(row=r, column=COL_COM_ETAPA, value=getattr(etapa, "nome", None))
            subetapa = subetapas_por_id.get(compra.id_subetapa) if compra.id_subetapa else None
            ws.cell(row=r, column=COL_COM_SUBETAPA, value=getattr(subetapa, "nome", None))
            servico = servicos_por_id.get(compra.id_servico) if compra.id_servico else None
            ws.cell(row=r, column=COL_COM_SERVICO, value=getattr(servico, "descricao", None))
            celula_data = ws.cell(row=r, column=COL_COM_DATA, value=compra.data_compra)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_COM_VALOR, value=compra.valor)
            ws.cell(row=r, column=COL_COM_FORMA_PAGAMENTO, value=compra.forma_pagamento)
            ws.cell(row=r, column=COL_COM_STATUS_APROVACAO, value=compra.status_aprovacao)
            ws.cell(row=r, column=COL_COM_STATUS_ENTREGA, value=compra.status_entrega)
            ws.cell(row=r, column=COL_COM_OBSERVACAO, value=compra.observacao)
        else:
            ws.cell(
                row=r,
                column=COL_COM_ID,
                value=f'=IF($B{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_COM_DATA).number_format = "DD/MM/YYYY"

        # Colunas SEMPRE calculadas por fórmula (linha literal ou não) —
        # mesmo padrão de todas as demais abas (Etapa 3 em diante).
        ws.cell(row=r, column=COL_COM_ID_OBRA, value=f'=IF($B{r}="","",Base_Dados!$B$2)')
        ws.cell(
            row=r,
            column=COL_COM_ID_ETAPA,
            value=(
                f'=IF(${letra_etapa}{r}="","",'
                f'INDEX(Etapas!$A:$A,MATCH(${letra_etapa}{r},Etapas!$B:$B,0)))'
            ),
        )
        ws.cell(
            row=r,
            column=COL_COM_ID_SUBETAPA,
            value=(
                f'=IF(${letra_subetapa}{r}="","",'
                f'INDEX(Subetapas!$A:$A,MATCH(${letra_subetapa}{r},Subetapas!$B:$B,0)))'
            ),
        )
        ws.cell(
            row=r,
            column=COL_COM_ID_SERVICO,
            value=(
                f'=IF(${letra_servico}{r}="","",'
                f'INDEX(Serviços!$A:$A,MATCH(${letra_servico}{r},Serviços!$B:$B,0)))'
            ),
        )
        # Planejado = Valor Previsto do Serviço vinculado (via ID_Servico
        # já resolvido acima), ou vazio quando não há vínculo a Serviço —
        # os vínculos a Etapa/Subetapa são só informativos e não
        # alimentam este cálculo (ver docstring de `src/compras/calculos.py`).
        ws.cell(
            row=r,
            column=COL_COM_PLANEJADO,
            value=(
                f'=IF(${letra_id_servico}{r}="","",'
                f'INDEX(Serviços!${get_column_letter(COL_SRV_VALOR_PREVISTO)}:'
                f'${get_column_letter(COL_SRV_VALOR_PREVISTO)},'
                f'MATCH(${letra_id_servico}{r},Serviços!$A:$A,0)))'
            ),
        )
        # Variação R$ = Compra − Planejado; Variação % trata Planejado=0
        # como "N/D" (nunca 0%) — mesmo padrão de % Orçamento Consumido
        # (REG-031).
        ws.cell(
            row=r,
            column=COL_COM_VARIACAO_REAIS,
            value=f'=IF(OR(${letra_planejado}{r}="",${letra_valor}{r}=""),"",${letra_valor}{r}-${letra_planejado}{r})',
        )
        ws.cell(
            row=r,
            column=COL_COM_VARIACAO_PERCENTUAL,
            value=(
                f'=IF(OR(${letra_planejado}{r}="",${letra_valor}{r}=""),"",'
                f'IF(${letra_planejado}{r}=0,"N/D",'
                f'${get_column_letter(COL_COM_VARIACAO_REAIS)}{r}/${letra_planejado}{r}))'
            ),
        )

    # Dropdowns "Etapa"/"Subetapa"/"Serviço" — todos opcionais e
    # independentes (regra 6); nomes amigáveis, nunca IDs.
    dv_etapa = DataValidation(
        type="list", formula1=NOME_INTERVALO_ETAPAS, allow_blank=True,
        showErrorMessage=True, errorTitle="Etapa inválida",
        error="Selecione uma Etapa já cadastrada na aba Etapas.",
    )
    ws.add_data_validation(dv_etapa)
    dv_etapa.add(f"I2:I{ultima_linha}")

    dv_subetapa = DataValidation(
        type="list", formula1=NOME_INTERVALO_SUBETAPAS, allow_blank=True,
        showErrorMessage=True, errorTitle="Subetapa inválida",
        error="Selecione uma Subetapa já cadastrada na aba Subetapas.",
    )
    ws.add_data_validation(dv_subetapa)
    dv_subetapa.add(f"J2:J{ultima_linha}")

    dv_servico = DataValidation(
        type="list", formula1=NOME_INTERVALO_SERVICOS, allow_blank=True,
        showErrorMessage=True, errorTitle="Serviço inválido",
        error="Selecione um Serviço já cadastrado na aba Serviços.",
    )
    ws.add_data_validation(dv_servico)
    dv_servico.add(f"K2:K{ultima_linha}")

    # Valor: numérico e não negativo (mesmo padrão de Financeiro/Serviços).
    dv_valor = DataValidation(
        type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
        showErrorMessage=True, errorTitle="Valor inválido",
        error="Informe um número maior ou igual a zero.",
    )
    ws.add_data_validation(dv_valor)
    dv_valor.add(f"E2:E{ultima_linha}")

    # Forma de Pagamento, Status de Aprovação e Status de Entrega: texto
    # livre, SEM dropdown — nenhum domínio fechado foi homologado para
    # esses 3 campos (DAD_001, entidade COMPRAS, continuam [H]); criar
    # uma lista fechada aqui seria inventar uma regra de negócio.

    for r in range(2, ultima_linha + 1):
        for coluna in (COL_COM_VALOR, COL_COM_PLANEJADO, COL_COM_VARIACAO_REAIS):
            ws.cell(row=r, column=coluna).number_format = FORMATO_MOEDA_BR
        ws.cell(row=r, column=COL_COM_VARIACAO_PERCENTUAL).number_format = "0.00%"

    for indice_coluna, (_titulo, _largura, _oculta, calculada) in enumerate(COLUNAS_COMPRAS, start=1):
        if not calculada:
            continue
        for r in range(2, ultima_linha + 1):
            celula = ws.cell(row=r, column=indice_coluna)
            celula.fill = PREENCHIMENTO_CALCULADO
            celula.font = FONTE_CALCULADA

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_COMPRAS))
    _registrar_tabela(ws, nome=NOME_TABELA_COMPRAS, ultima_linha=ultima_linha, n_colunas=len(COLUNAS_COMPRAS))
    ws.freeze_panes = "A2"


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
    Intervalos Nomeados para as colunas "Nome"/"Descrição" que alimentam
    dropdowns amigáveis — ver docstring equivalente na versão da Etapa 2.

    Etapa 5.1 (Correções 1 e 2): os três passam a apontar para a coluna
    da Tabela Excel estruturada correspondente (`Tabela[Coluna]`), em
    vez de um range de célula fixo. Isso resolve, com a MESMA estratégia
    para os três (auditoria pós-Etapa 5, AUD-22), tanto a inconsistência
    de `Lista_Financeiro_Descricoes` (antes limitada à antiga última
    linha) quanto o teto de 1000 linhas que `Lista_Etapas`/`Lista_
    Subetapas` já tinham — nenhum dos três depende mais de um número
    fixo de linhas.
    """
    wb.defined_names[NOME_INTERVALO_ETAPAS] = DefinedName(
        NOME_INTERVALO_ETAPAS, attr_text=f"{NOME_TABELA_ETAPAS}[Nome]"
    )
    wb.defined_names[NOME_INTERVALO_SUBETAPAS] = DefinedName(
        NOME_INTERVALO_SUBETAPAS, attr_text=f"{NOME_TABELA_SUBETAPAS}[Nome]"
    )
    wb.defined_names[NOME_INTERVALO_FINANCEIRO_DESCRICOES] = DefinedName(
        NOME_INTERVALO_FINANCEIRO_DESCRICOES, attr_text=f"{NOME_TABELA_FINANCEIRO}[Descrição]"
    )
    wb.defined_names[NOME_INTERVALO_SERVICOS] = DefinedName(
        NOME_INTERVALO_SERVICOS, attr_text=f"{NOME_TABELA_SERVICOS}[Descrição]"
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


def _contagem_servicos_elegiveis(*, somente_automaticos: bool = False) -> str:
    """
    Fórmula que conta os Serviços Elegíveis (REG-022) da Obra — espelho
    de `servicos_elegiveis_obra`/`servico_elegivel_execucao` em
    `src/execucao/calculos.py`.

    Com `somente_automaticos=True`, restringe aos que NÃO têm Peso
    Ajustado manual — a base da redistribuição proporcional (REG-024).

    **Por que `SUMPRODUCT(ISNUMBER(...))` e não `COUNTIFS`:** nas linhas-
    modelo em branco, a coluna Valor Previsto é uma FÓRMULA que devolve
    `""`, e o Excel trata célula com fórmula como "não vazia" — um
    `COUNTIFS(...,"<>")` contaria as 30 linhas de buffer (defeito real
    encontrado na Etapa 8.2: o denominador virava 31 em vez de 1).
    `ISNUMBER` conta apenas onde há número de fato, e a referência
    estruturada limita ao corpo da Tabela (exclui o cabeçalho e
    acompanha a expansão, sem range fixo).
    """
    def coluna(indice: int) -> str:
        return f"{NOME_TABELA_SERVICOS}[{COLUNAS_SERVICOS[indice - 1][0]}]"

    partes = [
        f"ISNUMBER({coluna(COL_SRV_VALOR_PREVISTO)})",
        f'({coluna(COL_SRV_STATUS)}<>"{_ROTULO_CANCELADO}")',
        f'({coluna(COL_SRV_STATUS)}<>"{_ROTULO_RETIRADO}")',
        f'({coluna(COL_SRV_STATUS)}<>"{_ROTULO_SUBSTITUIDO}")',
    ]
    if somente_automaticos:
        partes.append(f'({coluna(COL_SRV_PESO_AJUSTADO)}="")')
    return "SUMPRODUCT(" + "*".join(partes) + ")"


def _escrever_bloco_cronograma(ws: Worksheet, r: int, registro, *, primeira_coluna: int) -> None:
    """
    Etapa 8 — escreve, na linha `r`, o bloco de 7 colunas de cronograma
    (4 datas digitadas + 3 calculadas) a partir de `primeira_coluna`.

    Idêntico em Etapas e Subetapas: as duas entidades passaram a ter o
    mesmo conjunto de datas (decisão homologada em 2026-09-23, Opção A —
    a data mora no próprio registro, fonte de verdade única). `registro`
    é `None` nas linhas-modelo em branco.

    As 3 colunas calculadas são SEMPRE fórmula (inclusive nas linhas com
    dado literal), pelo mesmo motivo das demais etapas: precisam
    continuar corretas se o Operador editar as datas direto no Excel.
    """
    col_ini_prev = primeira_coluna
    col_fim_prev = primeira_coluna + 1
    col_ini_real = primeira_coluna + 2
    col_fim_real = primeira_coluna + 3
    col_dur_prev = primeira_coluna + 4
    col_dur_real = primeira_coluna + 5
    col_variacao = primeira_coluna + 6

    if registro is not None:
        ws.cell(row=r, column=col_ini_prev, value=registro.data_inicio_prevista)
        ws.cell(row=r, column=col_fim_prev, value=registro.data_fim_prevista)
        ws.cell(row=r, column=col_ini_real, value=registro.data_inicio_real)
        ws.cell(row=r, column=col_fim_real, value=registro.data_fim_real)

    for coluna in (col_ini_prev, col_fim_prev, col_ini_real, col_fim_real):
        ws.cell(row=r, column=coluna).number_format = FORMATO_DATA_BR

    letra_ini_prev = get_column_letter(col_ini_prev)
    letra_fim_prev = get_column_letter(col_fim_prev)
    letra_ini_real = get_column_letter(col_ini_real)
    letra_fim_real = get_column_letter(col_fim_real)

    # Subtração pura de datas (Etapa 8) — duas datas iguais dão 0 dias,
    # sem `+1` de contagem inclusiva; nenhuma fonte define contagem
    # inclusiva (ver `dias_entre` em `src/modelo/entidades.py`).
    ws.cell(
        row=r,
        column=col_dur_prev,
        value=(
            f'=IF(OR(${letra_ini_prev}{r}="",${letra_fim_prev}{r}=""),"",'
            f'${letra_fim_prev}{r}-${letra_ini_prev}{r})'
        ),
    )
    ws.cell(
        row=r,
        column=col_dur_real,
        value=(
            f'=IF(OR(${letra_ini_real}{r}="",${letra_fim_real}{r}=""),"",'
            f'${letra_fim_real}{r}-${letra_ini_real}{r})'
        ),
    )
    # Variação de Prazo = Fim Real − Fim Prevista. Positivo = atraso;
    # negativo = antecipação (convenção de sinal já homologada em
    # `Alteracao.impacto_prazo_dias`). Número simples, SEM cor/ícone/
    # alerta — o threshold de REG-014 permanece [H] ("não definido").
    ws.cell(
        row=r,
        column=col_variacao,
        value=(
            f'=IF(OR(${letra_fim_prev}{r}="",${letra_fim_real}{r}=""),"",'
            f'${letra_fim_real}{r}-${letra_fim_prev}{r})'
        ),
    )

    for coluna in (col_dur_prev, col_dur_real, col_variacao):
        celula = ws.cell(row=r, column=coluna)
        celula.number_format = FORMATO_DIAS
        celula.fill = PREENCHIMENTO_CALCULADO
        celula.font = FONTE_CALCULADA


def _adicionar_validacao_de_datas(ws: Worksheet, *, primeira_coluna: int, ultima_linha: int) -> None:
    """
    Etapa 8 — validação de data nas 4 colunas digitadas do bloco de
    cronograma (mesmo padrão dos campos de data da aba Início).

    `formula1` usa `DATE(1900,1,1)`, não a string `"1900-01-01"`: o Excel
    não interpreta essa string como literal de data — ele avalia a
    expressão aritmética `1900-1-1 = 1898`, e o limite entregue passaria
    a ser "serial ≥ 1898" (≈ 13/03/1905) em vez de 01/01/1900. Defeito
    apontado pela auditoria da Etapa 8; corrigido aqui, nas 8 faixas
    novas. A ocorrência equivalente na aba Início é **anterior a esta
    etapa** e foi deixada intacta (fora do escopo) — está registrada no
    relatório da Etapa 8 para decisão do responsável.
    """
    for deslocamento in range(4):
        letra = get_column_letter(primeira_coluna + deslocamento)
        dv = DataValidation(
            type="date",
            operator="greaterThanOrEqual",
            formula1="DATE(1900,1,1)",
            allow_blank=True,
            showErrorMessage=True,
            errorTitle="Data inválida",
            error="Informe uma data válida.",
        )
        ws.add_data_validation(dv)
        dv.add(f"{letra}2:{letra}{ultima_linha}")


def _aplicar_bordas(ws: Worksheet, ultima_linha: int, n_colunas: int) -> None:
    for linha_de_celulas in ws.iter_rows(min_row=1, max_row=ultima_linha, min_col=1, max_col=n_colunas):
        for celula in linha_de_celulas:
            celula.border = BORDA_CELULA


def _registrar_tabela(ws: Worksheet, *, nome: str, ultima_linha: int, n_colunas: int) -> None:
    """
    Etapa 5.1 (Correção 1 — expansão real do Excel, AUD-20/AUD-21).

    Envolve o intervalo de dado+buffer (cabeçalho incluso) como uma
    Tabela Excel estruturada nativa. É o mecanismo do próprio Excel
    para que fórmulas, validações (dropdowns) e formatação se estendam
    automaticamente quando o Operador digita na linha logo abaixo da
    tabela — sem depender de nenhum teto numérico de linhas.
    `LINHAS_MODELO` deixa de ser um limite: passa a significar apenas
    "quantas linhas de buffer pré-formatadas vêm prontas de fábrica".

    A Tabela já inclui seu próprio filtro automático (equivalente ao
    antigo `ws.auto_filter.ref`) — por isso não é mais necessário
    configurar `ws.auto_filter` separadamente.

    Sem `TableStyleInfo.name` (nenhum estilo predefinido do Excel) para
    preservar a aparência visual atual (cores/fontes definidas em
    `src/excel/estilos.py`), evitando introduzir zebra/faixas não
    pedidas (princípio "Less is more", AGENTS.md §10).
    """
    ultima_coluna = get_column_letter(n_colunas)
    tabela = Table(displayName=nome, ref=f"A1:{ultima_coluna}{ultima_linha}")
    tabela.tableStyleInfo = TableStyleInfo(
        name=None,
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=False,
        showColumnStripes=False,
    )
    ws.add_table(tabela)


def _adicionar_validacao_nome_unico(
    ws: Worksheet, *, coluna_nome: int, ultima_linha: int, intervalo_nomeado: str, titulo_coluna: str = "Nome"
) -> None:
    """
    Etapa 5.1 (correção de baixo risco para AUD-18 — vínculo por nome).

    O vínculo entre abas (Subetapa→Etapa, Serviço→Subetapa, Pagamento→
    Financeiro) continua resolvido por MATCH no nome/descrição, não por
    ID (mudar esse mecanismo exigiria uma refatoração estrutural maior,
    fora do escopo desta correção). Em vez disso, esta validação
    bloqueia a causa raiz do risco — nomes/descrições duplicados —
    impedindo, na própria origem, que o Operador cadastre dois
    registros com o mesmo Nome/Descrição nesta coluna. Não altera
    dropdowns, MATCH nem nenhum teste que já garante "dropdown mostra
    nome, nunca ID".

    **CORREÇÃO (validação Excel/COM da Etapa 8, 2026-09-23):** a fórmula
    original era `=COUNTIF(TabelaX[Coluna],B2)=1`, com **referência
    estruturada de Tabela dentro de uma validação de dados**. O Excel
    **não aceita referência estruturada em validação de dados** e
    recusava o arquivo inteiro como corrompido — por isso **nenhuma
    versão de V5 a V8 abria no Excel real**, defeito que a verificação
    estrutural por openpyxl nunca detectou (ela não executa o Excel).
    Confirmado por bissecção contra o Excel instalado: removendo apenas
    as validações do tipo `custom`, o arquivo abre.

    A fórmula passa a usar o **intervalo nomeado** correspondente
    (`Lista_Etapas`, `Lista_Subetapas`, `Lista_Servicos`,
    `Lista_Financeiro_Descricoes`), que o Excel aceita em validação de
    dados e que aponta exatamente para a mesma coluna da mesma Tabela
    (`Tabela[Coluna]`, ver `_criar_intervalos_nomeados`). Portanto:
    **nenhum range fixo é reintroduzido** (AUD-20/AUD-21 preservado) e a
    regra de negócio da validação é exatamente a mesma. O `=` inicial
    também foi removido, por não pertencer a fórmula de validação de
    dados no formato OOXML.
    """
    letra = get_column_letter(coluna_nome)
    dv_unico = DataValidation(
        type="custom",
        formula1=f"COUNTIF({intervalo_nomeado},{letra}2)=1",
        allow_blank=True,
        showErrorMessage=True,
        errorTitle=f"{titulo_coluna} duplicado",
        error=f"Já existe um registro com este mesmo {titulo_coluna.lower()}. "
        "Use um valor diferente para evitar vínculos ambíguos entre abas.",
    )
    ws.add_data_validation(dv_unico)
    dv_unico.add(f"{letra}2:{letra}{ultima_linha}")
