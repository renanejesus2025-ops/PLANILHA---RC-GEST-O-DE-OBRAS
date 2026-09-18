"""
Gera a versão 3 do arquivo Excel funcional — Etapa 4 ("Financeiro").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa, serviço ou lançamento financeiro fictícios foram
inventados — agora com as abas Financeiro, Pagamentos e Resumo
Financeiro (Aporte, Outras Entradas, Despesa/Custo, Outras Saídas,
Orçamento Vigente, Saldo Orçamentário, % Consumido, Saldo de Caixa,
Total Pago, Total A Pagar).

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx`)
para preservar a rastreabilidade: a V1 (Etapa 2) e a V2 (Etapa 3)
permanecem no disco, intocadas (Etapa 4, Seção 36).

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v3.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
