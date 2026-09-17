"""
Gera a versão 2 do arquivo Excel funcional — Etapa 3 ("Orçamento").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa ou serviço fictícios foram inventados — agora com a base
orçamentária completa (Quantidade, Valor Unitário, Valor Calculado,
Ajuste Manual, Valor Previsto, Variação, Status, Totais por Subetapa/
Etapa/Obra).

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx`)
para preservar a rastreabilidade: a V1 (Etapa 2) permanece no disco,
intocada (Etapa 3, Seção 22).

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
