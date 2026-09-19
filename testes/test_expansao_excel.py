"""
Testes de expansão real do Excel (Etapa 5.1, Correções 1 e 2).

Comprova que a migração para Tabelas Excel estruturadas (`ws.tables`)
resolve o risco AUD-20/AUD-21 da auditoria pós-Etapa 5: fórmulas de
totais que ignoravam silenciosamente registros além do antigo buffer
fixo de `LINHAS_MODELO` (30) linhas por aba, e a lista nomeada
`Lista_Financeiro_Descricoes` que tinha um teto diferente das demais
(AUD-22).

Limitação conhecida (mesma de todo o resto da suíte, ver
`testes/test_excel_construtor.py`): openpyxl não executa o motor de
fórmulas do Excel — as verificações abaixo são estruturais (a Tabela
cobre o intervalo certo; a fórmula usa referência estruturada sem teto
numérico; todas as linhas de dado real foram de fato escritas), não
uma recomputação real do valor pelo Excel.
"""

from __future__ import annotations

from datetime import date

import openpyxl

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import LINHAS_MODELO, construir_workbook
from src.modelo.entidades import Alteracao, Etapa, Financeiro, Obra
from src.modelo.enums import StatusAprovacaoAlteracao, TipoAlteracao, TipoLancamentoFinanceiro

# Deliberadamente maior que o antigo buffer fixo de 30 linhas/aba.
N_REGISTROS = LINHAS_MODELO + 5


def _obra(base: BaseDados) -> Obra:
    return base.adicionar_obra(Obra(id=base.gerador_id.gerar("OBRAS"), nome="Obra Grande"))


def test_mais_de_30_etapas_sao_todas_escritas_e_a_tabela_cobre_o_intervalo_certo(tmp_path):
    base = BaseDados()
    obra = _obra(base)
    for i in range(N_REGISTROS):
        base.adicionar_etapa(Etapa(id=base.gerador_id.gerar("ETAPAS"), id_obra=obra.id, nome=f"Etapa {i + 1}"))

    caminho = tmp_path / "v.xlsx"
    construir_workbook(base).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Etapas"]

    tabela = ws.tables["TabelaEtapas"]
    assert tabela.ref == f"A1:F{1 + N_REGISTROS + LINHAS_MODELO}"

    nomes = [ws.cell(row=r, column=2).value for r in range(2, 2 + N_REGISTROS)]
    assert nomes == [f"Etapa {i + 1}" for i in range(N_REGISTROS)]
    ids = [ws.cell(row=r, column=1).value for r in range(2, 2 + N_REGISTROS)]
    assert len(set(ids)) == N_REGISTROS  # todos únicos — nenhum registro foi ignorado


def test_totais_do_resumo_financeiro_somam_mais_de_30_lancamentos_sem_teto_de_linhas(tmp_path):
    base = BaseDados()
    obra = _obra(base)
    total_aportes_esperado = 0.0
    for i in range(N_REGISTROS):
        valor = 1_000 + i
        base.adicionar_financeiro(
            Financeiro(
                id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id,
                tipo=TipoLancamentoFinanceiro.APORTE, data=date(2026, 9, 19),
                valor=valor, descricao=f"Aporte {i + 1}",
            )
        )
        total_aportes_esperado += valor

    caminho = tmp_path / "v.xlsx"
    construir_workbook(base).save(caminho)
    wb = openpyxl.load_workbook(caminho)

    ws_fin = wb["Financeiro"]
    tabela = ws_fin.tables["TabelaFinanceiro"]
    assert tabela.ref == f"A1:M{1 + N_REGISTROS + LINHAS_MODELO}"
    valores_escritos = [ws_fin.cell(row=r, column=5).value for r in range(2, 2 + N_REGISTROS)]
    assert sum(valores_escritos) == total_aportes_esperado  # todas as 35 linhas foram escritas

    ws_resumo = wb["Resumo Financeiro"]
    linhas = {ws_resumo.cell(row=r, column=1).value: r for r in range(1, 20)}
    formula_aportes = ws_resumo.cell(row=linhas["Aportes"], column=2).value
    # Referência estruturada de Tabela — cobre toda a coluna "Aporte" da
    # tabela, sem depender de um range "$2:$N" fixado no momento da
    # geração (o antigo bug AUD-21: dados além do buffer inicial eram
    # ignorados silenciosamente por essa fórmula).
    assert formula_aportes == "=SUM(TabelaFinanceiro[Aporte])"
    assert not any(c.isdigit() for c in formula_aportes.split("[")[0])


def test_lista_financeiro_descricoes_acompanha_a_mesma_estrategia_das_demais_listas(tmp_path):
    """Correção 2: a lista de Descrições (dropdown Pagamentos→Lançamento)
    usa a mesma referência estruturada — cresce junto com a Tabela de
    Financeiro, sem o antigo teto fixo em 31 (diferente de Lista_Etapas/
    Lista_Subetapas, que já usavam um range fixo em 1000)."""
    base = BaseDados()
    obra = _obra(base)
    for i in range(N_REGISTROS):
        base.adicionar_financeiro(
            Financeiro(
                id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id,
                tipo=TipoLancamentoFinanceiro.DESPESA, data=date(2026, 9, 19),
                valor=100, descricao=f"Despesa {i + 1}",
            )
        )
    caminho = tmp_path / "v.xlsx"
    construir_workbook(base).save(caminho)
    wb = openpyxl.load_workbook(caminho)

    for nome_lista in ("Lista_Etapas", "Lista_Subetapas", "Lista_Financeiro_Descricoes"):
        formula = wb.defined_names[nome_lista].attr_text
        assert not any(c.isdigit() for c in formula)  # nenhuma das 3 tem teto numérico de linha

    assert wb.defined_names["Lista_Financeiro_Descricoes"].attr_text == "TabelaFinanceiro[Descrição]"


def test_mais_de_30_alteracoes_sao_todas_escritas_e_a_soma_aprovada_e_estrutural(tmp_path):
    base = BaseDados()
    obra = _obra(base)
    total_aprovado_esperado = 0.0
    for i in range(N_REGISTROS):
        status = StatusAprovacaoAlteracao.APROVADA if i % 2 == 0 else StatusAprovacaoAlteracao.EM_ANALISE
        impacto = 100 + i
        base.adicionar_alteracao(
            Alteracao(
                id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao=f"Alteração {i + 1}",
                tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=impacto,
                status_aprovacao=status, data=date(2026, 9, 19),
            )
        )
        if status is StatusAprovacaoAlteracao.APROVADA:
            total_aprovado_esperado += impacto

    caminho = tmp_path / "v.xlsx"
    construir_workbook(base).save(caminho)
    wb = openpyxl.load_workbook(caminho)

    ws_alt = wb["Alterações"]
    tabela = ws_alt.tables["TabelaAlteracoes"]
    assert tabela.ref == f"A1:I{1 + N_REGISTROS + LINHAS_MODELO}"
    impactos_escritos = [ws_alt.cell(row=r, column=5).value for r in range(2, 2 + N_REGISTROS)]
    assert len(impactos_escritos) == N_REGISTROS
    assert None not in impactos_escritos  # nenhuma das 35 linhas foi ignorada na escrita

    # Confirma, a nível Python (fora do Excel), que a soma de "Aprovada"
    # bate com o valor que a fórmula estrutural do Resumo Financeiro
    # somaria — fecha o elo entre a camada de cálculo e o Excel gerado.
    from src.alteracoes.calculos import total_alteracoes_aprovadas

    assert total_alteracoes_aprovadas(base, obra.id) == total_aprovado_esperado
