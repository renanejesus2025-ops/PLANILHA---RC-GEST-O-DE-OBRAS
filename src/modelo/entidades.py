"""
Entidades do modelo de dados — fundação técnica (Etapa 1).

Fonte de verdade: `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md`
(Revisão 5, 2026-09-16). Cada campo abaixo é comentado com o status
registrado lá: [D] Documentado/Homologado, [P] Proposta, [H] a Homologar.

Postura adotada nesta etapa para campos [H] sem domínio fechado
homologado (ex.: Status da Obra, Unidade de Medida, Forma de Pagamento):
são representados como texto livre (`Optional[str] = None`). Nenhum
valor de domínio foi inventado; a obrigatoriedade "Sim" do DAD_001 não
foi imposta em runtime quando o domínio em si ainda não foi homologado
(forçar um valor obrigatório sem domínio definido equivaleria a inventar
um valor). Isso é uma postura de implementação desta etapa, registrada
no relatório correspondente — não uma regra de negócio nova.

Regra AGENTS.md §11: "Código para a máquina. Nome para o usuário." — o
atributo `id` de cada entidade é técnico/interno; qualquer camada de
interface (fora do escopo desta etapa) deve sempre exibir o campo de
nome amigável (`nome`, `descricao`, `nome_razao_social` etc.), nunca `id`.

Os campos explicitamente CALCULADOS pelo Motor de Cálculos (Orçamento
Vigente/Disponível, Peso Automático, % Execução Física consolidado,
Saldo Orçamentário etc. — REG-005/REG-008/REG-017/REG-020) NÃO são
atributos de entrada aqui: essa camada é posterior a esta etapa (ver
AGENTS.md §9, item 3 "Motor de Cálculos"). Os campos calculados que
dependem apenas da própria entidade (Valor Calculado, Valor Previsto,
Ajuste Manual, Variação — REG-003, Opção C, [D] HOMOLOGADO na Etapa 3)
são expostos como `@property` em `ServicoOrcamento`, não como campo de
entrada; a agregação por Subetapa/Etapa/Obra vive em `src/orcamento/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.modelo.enums import (
    MetodoExecucao,
    StatusAprovacaoAlteracao,
    StatusExecucao,
    StatusServico,
    TipoAlteracao,
    TipoLancamentoFinanceiro,
)
from src.validacoes.numeros import validar_numero, validar_numero_nao_negativo


@dataclass
class Obra:
    """ENTIDADE: OBRAS (DAD_001). 1 linha = 1 obra.

    1 arquivo Excel = 1 obra (Seção 5 desta homologação) — esta entidade
    representa a obra do próprio arquivo; nenhum seletor de múltiplas
    obras é necessário nesta etapa.
    """

    id: str  # ID_Obra — técnico/interno (formato homologado na Seção 7)
    nome: str  # Nome da Obra — [P] — rótulo amigável, NUNCA o `id`
    cliente_contratante: Optional[str] = None  # [P]
    endereco: Optional[str] = None  # [P]
    data_inicio: Optional[date] = None  # [P]
    data_prevista_termino: Optional[date] = None  # [P]
    data_real_termino: Optional[date] = None  # [P]
    status: Optional[str] = None  # [H] domínio fechado não homologado
    responsavel_tecnico: Optional[str] = None  # [P]


@dataclass
class Etapa:
    """ENTIDADE: ETAPAS (DAD_001). N Etapas por Obra."""

    id: str
    id_obra: str  # FK -> Obra.id
    nome: str  # [P] — rótulo amigável (ex.: "Alvenaria")
    ordem: Optional[int] = None  # Ordem/Sequência — [P]
    data_inicio_prevista: Optional[date] = None  # [P]
    data_fim_prevista: Optional[date] = None  # [P]
    data_inicio_real: Optional[date] = None  # [P]
    data_fim_real: Optional[date] = None  # [P]
    status: Optional[str] = None  # Status da Etapa — [H]


@dataclass
class Subetapa:
    """ENTIDADE: SUBETAPAS (DAD_001, [D] HOMOLOGADO em 2026-09-16).

    N Subetapas por Etapa (REG-019, vínculo obrigatório).
    """

    id: str
    id_etapa: str  # FK -> Etapa.id (obrigatória, REG-019)
    nome: str  # [P] — rótulo amigável (ex.: "Alvenaria interna")
    status: Optional[str] = None  # [H] domínio fechado não homologado


@dataclass
class ServicoOrcamento:
    """ENTIDADE: SERVIÇOS/ORÇAMENTO (DAD_001).

    N Serviços por Subetapa (REG-019, vínculo obrigatório — nunca
    diretamente a uma Etapa).
    """

    id: str
    id_subetapa: str  # FK -> Subetapa.id (obrigatória, REG-019)
    descricao: str  # [P] — nome real da construção civil; rótulo amigável
    unidade_medida: Optional[str] = None  # [H] domínio fechado não homologado — texto livre (Etapa 3, Seção 7)
    quantidade_orcada: Optional[float] = None
    # ^ [P]. Também é a "Quantidade Planejada/Elegível" usada como
    # denominador do Método Quantitativo (REG-007). Numérica e não
    # negativa (Etapa 3, Seção 8) — validado em `__post_init__`.
    valor_unitario: Optional[float] = None
    # ^ [P]. Numérico e não negativo (Etapa 3, Seção 9) — validado em `__post_init__`.
    fornecedor_previsto_id: Optional[str] = None  # FK -> Fornecedor.id — [P]
    status: Optional[StatusServico] = None
    # ^ [D] HOMOLOGADO na Etapa 3 (Seção 18) — ver `StatusServico`. Antes
    # [H]/texto livre; resolvido nesta etapa com a lista fechada Ativo,
    # Concluído, Cancelado, Retirado do Escopo, Substituído.
    metodo_execucao: Optional[MetodoExecucao] = None  # [D] (REG-007) — não há lista fechada de qual serviço usa qual método
    status_execucao: Optional[StatusExecucao] = None  # [D] (REG-007) — só relevante quando metodo_execucao == STATUS
    peso_ajustado: Optional[float] = None
    # ^ Peso Ajustado (manual) — [D] admitido como exceção; NÃO exige
    # justificativa nem aprovação prévia obrigatórias (REG-008, Revisão 5).
    # Trata do PESO FÍSICO (progresso) — não confundir com o ajuste
    # manual do VALOR PREVISTO (orçamento) abaixo, que é um conceito
    # diferente, homologado separadamente na Etapa 3.
    peso_automatico_original: Optional[float] = None
    # ^ Preservado quando há `peso_ajustado`, conforme exigência explícita
    # de rastreabilidade mínima da decisão homologada (REG-008).
    valor_previsto_manual: Optional[float] = None
    # ^ Ajuste Manual do VALOR PREVISTO (orçamento) — [D] HOMOLOGADO na
    # Etapa 3 (Seções 3, 11, 12): quando preenchido, `valor_previsto`
    # passa a retornar este valor em vez de `valor_calculado`. Não exige
    # justificativa nem aprovação (Seção 12). `None` = sem ajuste manual.

    def __post_init__(self) -> None:
        validar_numero_nao_negativo(self.quantidade_orcada, "Quantidade Orçada")
        validar_numero_nao_negativo(self.valor_unitario, "Valor Unitário")

    @property
    def valor_calculado(self) -> Optional[float]:
        """
        Valor Calculado = Quantidade Orçada × Valor Unitário.

        REG-003, Opção C — [D] HOMOLOGADO na Etapa 3 (Seção 3/10). Este
        valor NUNCA é sobrescrito por um ajuste manual (Seção 3: "NUNCA
        substituir silenciosamente o Valor Calculado") — o ajuste manual
        afeta apenas `valor_previsto`. Retorna None se Quantidade ou
        Valor Unitário ainda não foram informados.
        """
        if self.quantidade_orcada is None or self.valor_unitario is None:
            return None
        return self.quantidade_orcada * self.valor_unitario

    @property
    def ajuste_manual(self) -> bool:
        """
        SIM/NÃO (Etapa 3, Seção 12) — True quando o Operador definiu um
        Valor Previsto manualmente (`valor_previsto_manual` não é None).
        """
        return self.valor_previsto_manual is not None

    @property
    def valor_previsto(self) -> Optional[float]:
        """
        Valor Previsto — [D] HOMOLOGADO na Etapa 3 (Seção 11):
        = Valor Previsto Manual, quando há Ajuste Manual;
        = Valor Calculado, caso contrário.
        """
        if self.ajuste_manual:
            return self.valor_previsto_manual
        return self.valor_calculado

    @property
    def variacao(self) -> Optional[float]:
        """
        Variação do Orçamento = Valor Previsto − Valor Calculado (Etapa 3,
        Seção 13). O termo "Variação" é usado deliberadamente — não
        "Desvio" (reservado a REG-013/REG-014/REG-015, ainda [H]).
        Variação percentual NÃO é exposta aqui: registrada como
        pendência (Etapa 3, Seção 13) por poder colidir com os
        thresholds de alerta ainda não homologados.
        Retorna None quando não há base suficiente para calcular.
        """
        previsto = self.valor_previsto
        calculado = self.valor_calculado
        if previsto is None or calculado is None:
            return None
        return previsto - calculado

    @property
    def integra_orcamento_corrente(self) -> bool:
        """
        True se este Serviço deve compor os totais do orçamento corrente
        (Etapa 3, Seções 18/19). Cancelado, Retirado do Escopo e
        Substituído são excluídos; os demais — inclusive Status ainda
        não informado (`None`) — permanecem incluídos por padrão (a
        ausência de status não é tratada como cancelamento).
        """
        if self.status is None:
            return True
        return self.status.integra_orcamento_corrente


@dataclass
class Planejamento:
    """ENTIDADE: PLANEJAMENTO (DAD_001). Datas previstas/reais por Etapa/Subetapa.

    Granularidade exata (só Etapa? só Subetapa? ambos?) é [H] — por isso
    os dois vínculos são opcionais aqui.
    """

    id: str
    id_etapa: Optional[str] = None  # FK -> Etapa.id — [H] granularidade
    id_subetapa: Optional[str] = None  # FK -> Subetapa.id — [H] granularidade
    data_inicio_prevista: Optional[date] = None  # [P]
    data_fim_prevista: Optional[date] = None  # [P]
    duracao_prevista_dias: Optional[int] = None  # [P]
    dependencia_id: Optional[str] = None  # autorreferência — [H] lógica de encadeamento
    status_prazo: Optional[str] = None  # [H] threshold de atraso não definido (REG-014)


@dataclass
class Fornecedor:
    """ENTIDADE: FORNECEDORES (DAD_001)."""

    id: str
    nome_razao_social: str  # [P] — rótulo amigável
    cnpj_cpf: Optional[str] = None  # [P]
    contato: Optional[str] = None  # [P]
    categoria_fornecimento: Optional[str] = None  # [H] domínio não homologado
    status: Optional[str] = None  # [H]


@dataclass
class Compra:
    """ENTIDADE: COMPRAS (DAD_001) — completada na Etapa 6.

    "1 linha representa uma compra" (DAD_001) — no vocabulário do prompt
    de homologação da Etapa 6, cada registro `Compra` já É um "item":
    múltiplos itens de um mesmo pedido são simplesmente múltiplos
    registros `Compra` (mesma granularidade de FINANCEIRO). Cada um pode,
    independentemente, referenciar Etapa, Subetapa e/ou Serviço (Seção 5,
    regra 6 da homologação) — vínculos puramente informativos/de
    rastreabilidade, exceto o vínculo a Serviço, que também alimenta o
    cálculo de Variação (`src/compras/calculos.py`).

    Compra NÃO cria automaticamente lançamento financeiro, NÃO altera o
    Orçamento Vigente nem o progresso físico (Seção 5, regras 2/7/8/9) —
    "o sistema informa, o Operador decide" (regras 19/20).
    """

    id: str
    id_obra: str  # FK -> Obra.id
    descricao: str  # [P] — o que foi comprado (Etapa 6; lacuna do modelo original)
    id_fornecedor: Optional[str] = None  # FK -> Fornecedor.id
    id_etapa: Optional[str] = None  # FK -> Etapa.id — informativo (Etapa 6)
    id_subetapa: Optional[str] = None  # FK -> Subetapa.id — informativo (Etapa 6)
    id_servico: Optional[str] = None  # FK -> ServicoOrcamento.id — alimenta a Variação
    data_compra: Optional[date] = None  # [P]
    valor: Optional[float] = None  # [P] — sempre não negativo (Etapa 6, mesmo padrão de FINANCEIRO)
    forma_pagamento: Optional[str] = None  # [H] domínio não homologado
    status_aprovacao: Optional[str] = None  # [H] fluxo de aprovação não definido (REG-010)
    status_entrega: Optional[str] = None  # [H]
    observacao: Optional[str] = None  # [P] (Etapa 6, mesmo padrão de Financeiro/Alterações)

    def __post_init__(self) -> None:
        validar_numero_nao_negativo(self.valor, "Valor da Compra")


@dataclass
class Financeiro:
    """ENTIDADE: FINANCEIRO (DAD_001) — estendida na Etapa 4 (Seções 8/19).

    Representa uma MOVIMENTAÇÃO FINANCEIRA: Aporte, Outras Entradas,
    Despesa/Custo ou Outras Saídas (`TipoLancamentoFinanceiro`, [D]
    HOMOLOGADO na Etapa 4, Seção 8). Deliberadamente DISTINTA de
    `Pagamento` (Etapa 4, Seção 20): o reconhecimento de uma Despesa/
    Custo (este registro) é independente de sua baixa financeira —
    ver `Pagamento` e `src/financeiro/calculos.py`.

    Aporte × Orçamento = Opção B (REG-006/REG-017, [D] HOMOLOGADO). Um
    Aporte só influencia o progresso físico se vinculado a um Serviço
    executável elegível (REG-021/REG-022) — `id_servico_vinculado` é o
    ponto de extensão previsto para isso; o mecanismo exato de vínculo
    é [H].
    """

    id: str
    id_obra: str  # FK -> Obra.id
    tipo: TipoLancamentoFinanceiro  # [D] HOMOLOGADO na Etapa 4 (Seção 8)
    data: date
    valor: float
    # ^ Sempre não negativo (Etapa 4, Seção 21: "o sinal já é
    # representado pelo TIPO da movimentação") — validado em
    # `__post_init__`. Ex.: Aporte = 10000, nunca -10000.
    descricao: Optional[str] = None  # [P] — rótulo amigável do lançamento (Etapa 4, Seção 19)
    categoria: Optional[str] = None  # [H] domínio não homologado
    origem_destino: Optional[str] = None  # [P]
    status_pagamento: Optional[str] = None  # [H] — herdado da Etapa 1; ver `situacao` (Etapa 4) para cancelamento/controle
    id_servico_vinculado: Optional[str] = None  # FK -> ServicoOrcamento.id — ver docstring
    id_fornecedor: Optional[str] = None  # FK -> Fornecedor.id — opcional (Etapa 4, Seção 24: "não obrigar fornecedor")
    id_compra: Optional[str] = None  # FK -> Compra.id — opcional (Etapa 4, Seção 25); nenhuma automação Compra→Financeiro foi criada
    observacao: Optional[str] = None  # [P] (Etapa 4, Seção 19)
    situacao: Optional[str] = None
    # ^ [H] — domínio de cancelamento/controle ainda não homologado
    # (Etapa 4, Seção 23: "não inventar um domínio fechado; preparar a
    # estrutura e registrar a pendência"). Texto livre; um cancelamento
    # NUNCA se transforma automaticamente em exclusão do registro.

    def __post_init__(self) -> None:
        validar_numero_nao_negativo(self.valor, "Valor do Lançamento Financeiro")


@dataclass
class Pagamento:
    """ENTIDADE: PAGAMENTOS — nova na Etapa 4 (Seção 20, [D] HOMOLOGADO
    em 2026-09-17: "separar claramente MOVIMENTO FINANCEIRO de
    PAGAMENTO. Não esconder pagamentos dentro do mesmo campo de custo").

    Um Pagamento é a BAIXA financeira de um lançamento `Financeiro` do
    tipo Despesa/Custo — nunca o próprio reconhecimento do custo. A
    estrutura permite N Pagamentos por lançamento (parciais e/ou totais,
    Seções 13/14/20); `BaseDados.adicionar_pagamento` garante que
    `id_financeiro` existe e é, de fato, um lançamento do tipo
    Despesa/Custo (ver `ErroPagamentoDeTipoInvalido`).
    """

    id: str
    id_financeiro: str  # FK -> Financeiro.id (o lançamento de Despesa/Custo amortizado)
    data: date  # [P] — data do pagamento (distinta da data do lançamento/reconhecimento do custo)
    valor: float  # sempre não negativo (Etapa 4, Seção 21) — validado em __post_init__
    observacao: Optional[str] = None  # [P] (Etapa 4, Seção 19)

    def __post_init__(self) -> None:
        validar_numero_nao_negativo(self.valor, "Valor do Pagamento")


@dataclass
class ExecucaoMedicao:
    """ENTIDADE: EXECUÇÃO/MEDIÇÕES (DAD_001). Motor de cálculo em
    `src/execucao/calculos.py` (Etapa 7)."""

    id: str
    id_servico: str  # FK -> ServicoOrcamento.id
    data_medicao: date  # [P] — periodicidade não homologada
    quantidade_executada: Optional[float] = None
    # ^ usado no Método Quantitativo (REG-007). Numérica e não negativa —
    # validada em `__post_init__` (Etapa 7, mesmo padrão de Quantidade
    # Orçada/Valor Unitário desde a Etapa 3). Múltiplas medições do mesmo
    # Serviço são ACUMULADAS (somadas), não substituídas — decisão de
    # implementação da Etapa 7 (nenhuma fonte definiu o contrário; é a
    # prática padrão de medição de obra), documentada em
    # `src/execucao/calculos.py:quantidade_executada_acumulada`.
    responsavel: Optional[str] = None  # [P]
    evidencia_documento_id: Optional[str] = None  # FK -> Documento.id
    status: Optional[str] = None  # [H]

    def __post_init__(self) -> None:
        validar_numero_nao_negativo(self.quantidade_executada, "Quantidade Executada")


@dataclass
class Alteracao:
    """ENTIDADE: ALTERAÇÕES (DAD_001) — domínio fechado na Etapa 5
    (2026-09-17): Tipo de Alteração e Status de Aprovação, fechando
    REG-012. Fecha também REG-017 (Orçamento Vigente completo — ver
    `src/alteracoes/calculos.py:total_alteracoes_aprovadas`).
    """

    id: str
    id_obra: str  # FK -> Obra.id
    descricao: str  # [P]
    tipo_alteracao: Optional[TipoAlteracao] = None
    # ^ [D] HOMOLOGADO na Etapa 5 — domínio fechado Escopo/Prazo/Orçamento.
    impacto_orcamento: Optional[float] = None
    # ^ [P]. Delta com sinal (pode reduzir o orçamento) — validado por
    # `validar_numero` (numérico, SEM exigir não-negativo; Etapa 5).
    impacto_prazo_dias: Optional[int] = None
    # ^ [P]. Delta com sinal (pode antecipar o prazo) — mesma validação.
    status_aprovacao: Optional[StatusAprovacaoAlteracao] = None
    # ^ [D] HOMOLOGADO na Etapa 5 — domínio fechado Pendente/Aprovada/
    # Rejeitada. Sem workflow: o Operador define diretamente.
    solicitante: Optional[str] = None  # [P]
    data: Optional[date] = None  # [P]

    def __post_init__(self) -> None:
        validar_numero(self.impacto_orcamento, "Impacto no Orçamento")
        validar_numero(self.impacto_prazo_dias, "Impacto no Prazo")


@dataclass
class Pendencia:
    """ENTIDADE: PENDÊNCIAS (DAD_001)."""

    id: str
    id_obra: str  # FK -> Obra.id
    descricao: str  # [P]
    responsavel: Optional[str] = None  # [P]
    data_abertura: Optional[date] = None  # [P]
    prazo_sla: Optional[date] = None  # [H] SLA em dias não homologado (REG-011)
    status: Optional[str] = None  # [H]
    prioridade: Optional[str] = None  # [H] critério de priorização não definido
    vinculo_id: Optional[str] = None  # FK opcional -> Etapa/Compra/Financeiro


@dataclass
class Atualizacao:
    """ENTIDADE: ATUALIZAÇÕES (DAD_001)."""

    id: str
    id_obra: str  # FK -> Obra.id
    data: date  # [P]
    texto: str  # [P]
    autor: Optional[str] = None  # [H] depende do mecanismo de identificação (SEC_001, ainda não homologado)
    anexo_documento_id: Optional[str] = None  # FK -> Documento.id
    visivel_para_cliente: Optional[bool] = None  # [H] regra de visibilidade por registro não definida


@dataclass
class Documento:
    """ENTIDADE: DOCUMENTOS (DAD_001)."""

    id: str
    id_obra: str  # FK -> Obra.id
    vinculo_id: Optional[str] = None  # FK opcional -> Etapa/Medição/Compra/Alteração
    tipo_arquivo: Optional[str] = None  # [P]
    data_upload: Optional[date] = None  # [P]
    descricao: Optional[str] = None  # [P]
    caminho_arquivo: Optional[str] = None  # [H] mecanismo de armazenamento não definido
