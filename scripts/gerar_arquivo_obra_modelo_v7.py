"""
Gera a versão 7 do arquivo Excel funcional — Etapa 7 ("Execução/Medições").

Produz um MODELO (template) vazio de dados de negócio — nenhuma obra,
etapa, subetapa, serviço, medição etc. fictícios foram inventados.
Acrescenta a aba **Execução** (log de medições, REG-007 Método
Quantitativo) e as colunas de Progresso Físico na aba Serviços (Método/
Status de Execução, % Execução do Serviço, Peso Automático/Ajustado/
Efetivo, Contribuição na Obra — REG-007/008/020/022/023/024/025), além
das colunas informativas de "Peso Consolidado"/"Contribuição na Obra" em
Etapas/Subetapas e da célula "% Execução Física da Obra" em Início.

Gerado como uma NOVA versão (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V7.xlsx`)
para preservar a rastreabilidade: V1 a V6 permanecem no disco, intocadas
(mesmo padrão de toda etapa anterior — cada etapa de construção cria seu
próprio arquivo versionado, nunca sobrescreve o anterior).

Uso:
    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v7.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DO_PROJETO))

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import construir_workbook

NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V7.xlsx"
CAMINHO_SAIDA = RAIZ_DO_PROJETO / "dados" / NOME_ARQUIVO


def main() -> None:
    workbook = construir_workbook(BaseDados())  # base vazia -> modelo/template, sem dado inventado
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(CAMINHO_SAIDA)
    print(f"Arquivo gerado em: {CAMINHO_SAIDA}")
    print(f"Abas: {workbook.sheetnames}")


if __name__ == "__main__":
    main()
