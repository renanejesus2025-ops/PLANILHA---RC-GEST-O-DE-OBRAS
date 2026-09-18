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
    Domínio fechado do "Tipo" de FINANCEIRO — [D] HOMOLOGADO na Etapa 4
    (Seção 8, 2026-09-17): Aporte, Outras Entradas, Despesa/Custo, Outras
    Saídas. Fecha o domínio que a Etapa 1 (REG-006) havia deixado
    parcial (só Aporte/Despesa) — "não criar outros tipos nesta etapa
    sem homologação" (Seção 8).

    O membro `DESPESA` foi mantido com esse nome (compatibilidade com
    `Financeiro`/testes já existentes da Etapa 1) — seu rótulo amigável
    passa a ser "Despesa/Custo" (ver `rotulo`), termo usado pela Etapa 4.
    """

    APORTE = "aporte"
    OUTRAS_ENTRADAS = "outras_entradas"
    DESPESA = "despesa"
    OUTRAS_SAIDAS = "outras_saidas"

    @property
    def rotulo(self) -> str:
        """Rótulo amigável em português (dropdown do Excel/interface)."""
        rotulos = {
            TipoLancamentoFinanceiro.APORTE: "Aporte",
            TipoLancamentoFinanceiro.OUTRAS_ENTRADAS: "Outras Entradas",
            TipoLancamentoFinanceiro.DESPESA: "Despesa/Custo",
            TipoLancamentoFinanceiro.OUTRAS_SAIDAS: "Outras Saídas",
        }
        return rotulos[self]

    @property
    def aumenta_orcamento_vigente(self) -> bool:
        """
        Só Aporte aumenta o Orçamento Vigente (Etapa 4, Seções 4/9/10).
        Outras Entradas, Despesa/Custo e Outras Saídas NÃO alteram o
        Orçamento Vigente.
        """
        return self is TipoLancamentoFinanceiro.APORTE

    @property
    def e_custo_realizado(self) -> bool:
        """
        Só Despesa/Custo compõe o Custo Realizado (Etapa 4, Seções
        11/16) — independentemente de já ter sido pago (Seção 11: "isso
        ocorre independentemente de a despesa já ter sido paga").
        """
        return self is TipoLancamentoFinanceiro.DESPESA

    @property
    def afeta_caixa_no_lancamento(self) -> bool:
        """
        True para Aporte, Outras Entradas e Outras Saídas — o Caixa é
        afetado no momento do próprio lançamento (Etapa 4, Seções 9/10/
        12). False para Despesa/Custo: o reconhecimento do custo NÃO
        reduz o Caixa por si só (Seção 16) — o Caixa só é afetado quando
        há Pagamento (`Pagamento`, Seção 13/14/20).
        """
        return self is not TipoLancamentoFinanceiro.DESPESA

    @property
    def natureza_caixa(self) -> str:
        """
        'entrada' ou 'saida' para os tipos com efeito direto no Caixa no
        momento do lançamento (Aporte/Outras Entradas -> 'entrada';
        Outras Saídas -> 'saida'); 'custo' para Despesa/Custo, cujo
        efeito no Caixa é indireto — via `Pagamento` (Etapa 4, Seção 16),
        nunca no reconhecimento do lançamento em si.
        """
        if self in (TipoLancamentoFinanceiro.APORTE, TipoLancamentoFinanceiro.OUTRAS_ENTRADAS):
            return "entrada"
        if self is TipoLancamentoFinanceiro.OUTRAS_SAIDAS:
            return "saida"
        return "custo"


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
