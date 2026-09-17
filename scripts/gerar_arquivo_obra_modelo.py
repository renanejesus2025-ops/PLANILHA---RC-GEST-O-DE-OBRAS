"""
DEPRECIADO A PARTIR DA ETAPA 3 — ver `scripts/gerar_arquivo_obra_modelo_v2.py`.

Este script gerou originalmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx`
na Etapa 2. `src/excel/construtor_workbook.py` (o mesmo módulo que este
script chama) evoluiu na Etapa 3 com a base orçamentária completa —
reexecutar este script agora produziria conteúdo no NOVO formato sob o
NOME ANTIGO (`..._V1.xlsx`), o que seria uma sobrescrita silenciosa e
enganosa da versão histórica (Etapa 3, Seção 22: "Não sobrescrever
silenciosamente a versão anterior").

Por isso este script agora se recusa a rodar. `dados/GESTAO_DE_OBRAS_
OBRA_MODELO_V1.xlsx` permanece no disco, intocado, como registro de como
a Etapa 2 o gerou. Para gerar a versão corrente, use:

    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v2.py
"""

from __future__ import annotations

import sys

MENSAGEM = (
    "Este script está DEPRECIADO desde a Etapa 3 (ver docstring do módulo).\n"
    "Use: .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v2.py\n"
    "O arquivo dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx não foi alterado."
)


def main() -> None:
    raise SystemExit(MENSAGEM)


if __name__ == "__main__":
    main()
