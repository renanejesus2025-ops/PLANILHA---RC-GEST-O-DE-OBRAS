"""
Gera a versão 6 do arquivo Excel funcional — Etapa 6 ("Compras").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa, serviço, lançamento financeiro, alteração ou compra
fictícios foram inventados. Acrescenta a aba **Compras** (registro de
compras/pedidos, com vínculos opcionais e independentes a Etapa/
Subetapa/Serviço, e o cálculo de Variação R$/% contra o Serviço
vinculado, quando houver) — sem criar nenhuma automação sobre
Financeiro, Orçamento ou Execução (prompt de homologação "ETAPA 6 —
COMPRAS", Seção 5).

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V6.xlsx`)
para preservar a rastreabilidade: V1 a V5 permanecem no disco, intocadas.

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v6.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V6.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
