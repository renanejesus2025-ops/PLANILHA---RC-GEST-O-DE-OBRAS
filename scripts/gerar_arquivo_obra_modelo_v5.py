"""
Gera a versão 5 do arquivo Excel funcional — Etapa 5.1 ("Correções
Pós-Auditoria").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa, serviço, lançamento financeiro ou alteração fictícios
foram inventados. Não introduz nenhuma funcionalidade de negócio nova
em relação à V4: corrige, em `src/excel/construtor_workbook.py`, os
problemas técnicos encontrados na auditoria pós-Etapa 5 (relatório
"AUDITORIA PRÉ-ETAPA 6"):

- as 6 abas de registro (Etapas, Subetapas, Serviços, Financeiro,
  Pagamentos, Alterações) passam a ser Tabelas Excel estruturadas
  nativas, em vez de um intervalo fixo de `LINHAS_MODELO` linhas —
  fórmulas, validações e formatação agora se estendem automaticamente
  quando o Operador adiciona uma linha, sem teto numérico (AUD-20);
- as fórmulas de totais do "Resumo Financeiro" e de `Início!B8` usam
  referência estruturada de Tabela em vez de um range fixo `$2:$N` —
  não ignoram mais silenciosamente registros além de um buffer inicial
  (AUD-21, erro real crítico da auditoria);
- a lista nomeada `Lista_Financeiro_Descricoes` passa a usar a mesma
  estratégia das demais (`Lista_Etapas`/`Lista_Subetapas`), fechando a
  inconsistência apontada (AUD-22);
- validação de unicidade de Nome/Descrição em Etapas, Subetapas e
  Financeiro, mitigando o risco de vínculo ambíguo por nome duplicado
  entre abas (AUD-18), sem alterar o mecanismo de vínculo em si;
- domínio de "Status de Aprovação" de Alterações corrigido para 4
  valores (Em análise, Aprovada, Rejeitada, Cancelada).

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V5.xlsx`)
para preservar a rastreabilidade: V1 a V4 permanecem no disco, intocadas.

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v5.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V5.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
