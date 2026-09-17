"""
Domínios fechados já HOMOLOGADOS para os campos de execução física.

Fonte: `05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md`, REG-006 e
REG-007 (Revisões 4 e 5, homologadas em 2026-09-16).

Nenhum outro domínio fechado do DAD_001 (ex.: Status da Obra, Status do
Serviço/Orçamento, Unidade de Medida, Categoria de Fornecedor, Forma de
Pagamento, Tipo de Alteração etc.) foi homologado até esta etapa — por
isso eles NÃO aparecem aqui como Enum e são representados como texto
livre (`Optional[str]`) em `src/modelo/entidades.py`. Criar um Enum para
um domínio ainda [H] seria inventar uma regra de negócio, o que a Seção 2
("Princípio de não-invenção") desta homologação proíbe explicitamente.
"""

from __future__ import annotations

from enum import Enum


class MetodoExecucao(str, Enum):
    """Método de apuração do % de execução de um Serviço (REG-007, [D])."""

    QUANTITATIVO = "quantitativo"
    STATUS = "status"


class StatusExecucao(str, Enum):
    """
    Domínio fechado do método por Status (REG-007, Revisão 5, [D]
    HOMOLOGADO em 2026-09-16).

    Tabela fixa homologada: Pendente = 0%, Em andamento = 50%,
    Concluído = 100%. Enquanto esta decisão estiver vigente, nenhum outro
    valor é válido e não há percentual intermediário informado manualmente.
    """

    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"

    @property
    def percentual(self) -> float:
        """Percentual de execução fixo correspondente a este status (REG-007)."""
        tabela = {
            StatusExecucao.PENDENTE: 0.0,
            StatusExecucao.EM_ANDAMENTO: 50.0,
            StatusExecucao.CONCLUIDO: 100.0,
        }
        return tabela[self]


class TipoLancamentoFinanceiro(str, Enum):
    """
    Valores homologados do domínio "Tipo" de FINANCEIRO (REG-006, [D]
    parcial).

    Apenas Aporte e Despesa estão homologados como valores existentes.
    REG-004 registra que "outros valores possíveis do domínio Tipo além
    de Aporte/Despesa continuam [H]" — este Enum não fecha essa
    possibilidade, apenas representa o que já está homologado hoje.
    """

    APORTE = "aporte"
    DESPESA = "despesa"


class StatusServico(str, Enum):
    """
    Domínio fechado do Status do Serviço/Orçamento — [D] HOMOLOGADO na
    Etapa 3 (Seção 18, 2026-09-16): Ativo, Concluído, Cancelado,
    Retirado do Escopo, Substituído. Resolve o item que estava [H]
    ("Status do Serviço/Orçamento") no `DAD_001`.

    Este domínio é específico do Serviço/Orçamento — não se aplica aos
    campos "Status" (ainda [H]) de OBRAS, ETAPAS, SUBETAPAS ou às demais
    entidades, que continuam texto livre em `src/modelo/entidades.py`.
    Também é distinto de `StatusExecucao` (que descreve o andamento
    físico de um Serviço pelo método "status", REG-007) — este Enum
    descreve o status do REGISTRO orçamentário em si.
    """

    ATIVO = "ativo"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    RETIRADO_DO_ESCOPO = "retirado_do_escopo"
    SUBSTITUIDO = "substituido"

    @property
    def rotulo(self) -> str:
        """Rótulo amigável em português (usado na interface/Excel)."""
        rotulos = {
            StatusServico.ATIVO: "Ativo",
            StatusServico.CONCLUIDO: "Concluído",
            StatusServico.CANCELADO: "Cancelado",
            StatusServico.RETIRADO_DO_ESCOPO: "Retirado do Escopo",
            StatusServico.SUBSTITUIDO: "Substituído",
        }
        return rotulos[self]

    @property
    def integra_orcamento_corrente(self) -> bool:
        """
        False para Cancelado, Retirado do Escopo e Substituído (Etapa 3,
        Seção 19: esses três "não devem ser automaticamente tratados
        como serviços ativos do orçamento corrente"). True para os
        demais (Ativo, Concluído) — um serviço concluído continua parte
        do orçamento realizado/corrente da obra.
        """
        return self not in {
            StatusServico.CANCELADO,
            StatusServico.RETIRADO_DO_ESCOPO,
            StatusServico.SUBSTITUIDO,
        }
