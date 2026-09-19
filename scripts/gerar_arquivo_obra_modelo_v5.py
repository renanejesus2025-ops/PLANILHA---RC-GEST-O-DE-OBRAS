"""
DEPRECIADO A PARTIR DA ETAPA 6 — ver `scripts/gerar_arquivo_obra_modelo_v6.py`.

Este script gerou originalmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V5.xlsx`
na Etapa 5.1. `src/excel/construtor_workbook.py` (o mesmo módulo que este
script chama) evoluiu na Etapa 6 ("Compras") — nova aba "Compras", novo
defined name `Lista_Servicos`, e validação de nome único estendida à
coluna Descrição de Serviços — reexecutar este script agora produziria
conteúdo no NOVO formato sob o NOME ANTIGO (`..._V5.xlsx`), o que seria
uma sobrescrita silenciosa e enganosa da versão histórica (mesmo
princípio já aplicado aos scripts da V1 a V4).

Por isso este script agora se recusa a rodar. `dados/GESTAO_DE_OBRAS_
OBRA_MODELO_V5.xlsx` permanece no disco, intocado, como registro de como
a Etapa 5.1 o gerou. Para gerar a versão corrente, use:

    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v6.py
"""

from __future__ import annotations

import sys

MENSAGEM = (
    "Este script está DEPRECIADO desde a Etapa 6 (ver docstring do módulo).\n"
    "Use: .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v6.py\n"
    "O arquivo dados/GESTAO_DE_OBRAS_OBRA_MODELO_V5.xlsx não foi alterado."
)


def main() -> None:
    raise SystemExit(MENSAGEM)


if __name__ == "__main__":
    main()
