"""
DEPRECIADO A PARTIR DA ETAPA 4 — ver `scripts/gerar_arquivo_obra_modelo_v3.py`.

Este script gerou originalmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx`
na Etapa 3. `src/excel/construtor_workbook.py` (o mesmo módulo que este
script chama) evoluiu na Etapa 4 com as abas Financeiro/Pagamentos/Resumo
Financeiro — reexecutar este script agora produziria conteúdo no NOVO
formato sob o NOME ANTIGO (`..._V2.xlsx`), o que seria uma sobrescrita
silenciosa e enganosa da versão histórica (mesmo princípio já aplicado ao
script da V1 na Etapa 3; Etapa 4, Seção 36: "NÃO sobrescrever
silenciosamente" V1 nem V2).

Por isso este script agora se recusa a rodar. `dados/GESTAO_DE_OBRAS_
OBRA_MODELO_V2.xlsx` permanece no disco, intocado, como registro de como
a Etapa 3 o gerou. Para gerar a versão corrente, use:

    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v3.py
"""

from __future__ import annotations

import sys

MENSAGEM = (
    "Este script está DEPRECIADO desde a Etapa 4 (ver docstring do módulo).\n"
    "Use: .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v3.py\n"
    "O arquivo dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx não foi alterado."
)


def main() -> None:
    raise SystemExit(MENSAGEM)


if __name__ == "__main__":
    main()
