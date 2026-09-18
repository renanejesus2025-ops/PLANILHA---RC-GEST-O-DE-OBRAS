"""
DEPRECIADO A PARTIR DA ETAPA 5 — ver `scripts/gerar_arquivo_obra_modelo_v4.py`.

Este script gerou originalmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx`
na Etapa 4. `src/excel/construtor_workbook.py` (o mesmo módulo que este
script chama) evoluiu na Etapa 5 com a aba Alterações (e a atualização do
Resumo Financeiro para considerar as Alterações Aprovadas no Orçamento
Vigente) — reexecutar este script agora produziria conteúdo no NOVO
formato sob o NOME ANTIGO (`..._V3.xlsx`), o que seria uma sobrescrita
silenciosa e enganosa da versão histórica (mesmo princípio já aplicado aos
scripts da V1 e da V2; Etapa 4, Seção 36: "NÃO sobrescrever
silenciosamente" V1 nem V2).

Por isso este script agora se recusa a rodar. `dados/GESTAO_DE_OBRAS_
OBRA_MODELO_V3.xlsx` permanece no disco, intocado, como registro de como
a Etapa 4 o gerou. Para gerar a versão corrente, use:

    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v4.py
"""

from __future__ import annotations

import sys

MENSAGEM = (
    "Este script está DEPRECIADO desde a Etapa 5 (ver docstring do módulo).\n"
    "Use: .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v4.py\n"
    "O arquivo dados/GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx não foi alterado."
)


def main() -> None:
    raise SystemExit(MENSAGEM)


if __name__ == "__main__":
    main()
