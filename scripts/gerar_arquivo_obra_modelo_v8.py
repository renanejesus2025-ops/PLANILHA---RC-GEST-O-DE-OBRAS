"""
Gera a versão 8 do arquivo Excel funcional — Etapa 8 ("Planejamento /
Cronograma da Obra").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa, data etc. fictícios foram inventados.

Nesta versão, as abas **Etapas** e **Subetapas** ganham o bloco de
cronograma (Data Início/Fim Prevista, Data Início/Fim Real, Duração
Prevista/Real e Variação de Prazo), e a aba **Início** ganha o
cronograma consolidado da Obra (menor/maior data das Etapas e Variação
de Prazo da Obra). Nenhuma aba nova foi criada: as datas moram nas
próprias Etapas/Subetapas (decisão homologada pelo responsável do
projeto em 2026-09-23, Opção A — fonte de verdade única por registro), e
essas abas já são Tabelas Excel estruturadas que se expandem sozinhas.

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V8.xlsx`)
para preservar a rastreabilidade: V1 a V7 permanecem no disco, intocadas
(mesmo padrão de toda etapa anterior — cada etapa de construção cria seu
próprio arquivo versionado, nunca sobrescreve o anterior).

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v8.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V8.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
