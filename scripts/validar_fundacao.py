"""
Script de fumaça (smoke test) manual da fundação técnica — Etapa 1.

Não substitui os testes automatizados em `testes/` (execute-os com
`pytest`); serve apenas para uma verificação rápida e legível de que a
API básica funciona de ponta a ponta, útil também como exemplo de uso
para quem for construir a próxima camada (Motor de Cálculos).

Uso:
    .venv/Scripts/python.exe scripts/validar_fundacao.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite `import src...`/`import config...` ao rodar este script
# diretamente (`python scripts/validar_fundacao.py`), sem precisar
# instalar o projeto como pacote — mesmo raciocínio do `pythonpath = .`
# em pytest.ini.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroFundacaoTecnica
from src.modelo.entidades import Etapa, Obra, ServicoOrcamento, Subetapa
from src.modelo.enums import MetodoExecucao


def main() -> None:
    base = BaseDados()

    obra = base.adicionar_obra(
        Obra(id=base.gerador_id.gerar("OBRAS"), nome="Residencial Jardim das Flores")
    )
    etapa = base.adicionar_etapa(
        Etapa(id=base.gerador_id.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria")
    )
    subetapa = base.adicionar_subetapa(
        Subetapa(id=base.gerador_id.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Alvenaria interna")
    )
    servico = base.adicionar_servico(
        ServicoOrcamento(
            id=base.gerador_id.gerar("SERVICOS_ORCAMENTO"),
            id_subetapa=subetapa.id,
            descricao="Reboco",
            quantidade_orcada=120.0,
            valor_unitario=18.5,
            metodo_execucao=MetodoExecucao.QUANTITATIVO,
        )
    )

    print("Hierarquia construída com sucesso:")
    print(f"  Obra:     {obra.id:10s} -> {obra.nome}")
    print(f"  Etapa:    {etapa.id:10s} -> {etapa.nome}")
    print(f"  Subetapa: {subetapa.id:10s} -> {subetapa.nome}")
    print(f"  Serviço:  {servico.id:10s} -> {servico.descricao}")
    print(f"  Valor Calculado do Serviço: {servico.valor_calculado}")
    print(f"  Valor Previsto do Serviço: {servico.valor_previsto} (Ajuste Manual: {servico.ajuste_manual})")

    print("\nTentando violar a hierarquia (Serviço direto sem Subetapa válida)...")
    try:
        base.adicionar_servico(
            ServicoOrcamento(id="SRV-9999", id_subetapa="SUB-9999", descricao="Inválido")
        )
    except ErroFundacaoTecnica as erro:
        print(f"  Rejeitado corretamente: {erro}")

    print("\nFundação técnica validada (smoke test concluído).")


if __name__ == "__main__":
    main()
