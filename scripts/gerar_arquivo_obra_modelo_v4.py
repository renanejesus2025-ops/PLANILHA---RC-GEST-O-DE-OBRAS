"""
DEPRECIADO A PARTIR DA ETAPA 5.1 — ver `scripts/gerar_arquivo_obra_modelo_v5.py`.

Este script gerou originalmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx`
na Etapa 5. `src/excel/construtor_workbook.py` (o mesmo módulo que este
script chama) evoluiu na Etapa 5.1 ("Correções Pós-Auditoria") — as 6
abas de registro passaram a ser Tabelas Excel estruturadas, o Resumo
Financeiro e `Início!B8` passaram a usar referência estruturada sem
teto de linhas, e o domínio de Status de Aprovação de Alterações foi
corrigido para 4 valores — reexecutar este script agora produziria
conteúdo no NOVO formato sob o NOME ANTIGO (`..._V4.xlsx`), o que seria
uma sobrescrita silenciosa e enganosa da versão histórica (mesmo
princípio já aplicado aos scripts da V1, V2 e V3).

Por isso este script agora se recusa a rodar. `dados/GESTAO_DE_OBRAS_
OBRA_MODELO_V4.xlsx` permanece no disco, intocado, como registro de como
a Etapa 5 o gerou. Para gerar a versão corrente, use:

    .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v5.py
"""

from __future__ import annotations

import sys

MENSAGEM = (
    "Este script está DEPRECIADO desde a Etapa 5.1 (ver docstring do módulo).\n"
    "Use: .venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v5.py\n"
    "O arquivo dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx não foi alterado."
)


def main() -> None:
    raise SystemExit(MENSAGEM)


if __name__ == "__main__":
    main()
