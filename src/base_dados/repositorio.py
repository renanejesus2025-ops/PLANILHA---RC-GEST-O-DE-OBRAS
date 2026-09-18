"""
Base de Dados em memória — fundação técnica (Etapa 1), estendida na
Etapa 4 (Financeiro) com a entidade PAGAMENTOS.

`BaseDados` mantém as 14 entidades do DAD_001 (13 da Etapa 1 + PAGAMENTOS,
novo na Etapa 4) para UMA obra (1 arquivo Excel = 1 obra, Seção 5 da
homologação da Etapa 1) e garante, em cada inserção:

- unicidade de ID (REG-001/teste 2);
- existência da referência (FK) apontada (REG-002, teste 5/7);
- respeito à hierarquia oficial OBRA → ETAPA → SUBETAPA → SERVIÇO
  (REG-019, teste 6);
- (Etapa 4) um PAGAMENTO só referencia um lançamento FINANCEIRO do tipo
  Despesa/Custo (Seções 13/14/20).

Não implementa o Motor de Cálculos de execução física (peso automático,
% de execução consolidado etc.) — isso pertence a uma camada
arquitetural separada (AGENTS.md §9, item 3), fora do escopo desta
etapa. O Motor de Cálculos FINANCEIRO (Orçamento Vigente, Saldo
Orçamentário, % Consumido, Saldo de Caixa, A Pagar) vive em
`src/financeiro/calculos.py` (Etapa 4).
"""

from __future__ import annotations

from src.excecoes import ErroIdDuplicado, ErroPagamentoDeTipoInvalido, ErroReferenciaInvalida
from src.ids.gerador_id import GeradorId
from src.modelo.entidades import (
    Alteracao,
    Atualizacao,
    Compra,
    Documento,
    Etapa,
    ExecucaoMedicao,
    Financeiro,
    Fornecedor,
    Obra,
    Pagamento,
    Pendencia,
    Planejamento,
    ServicoOrcamento,
    Subetapa,
)
from src.modelo.enums import TipoLancamentoFinanceiro


class BaseDados:
    """Agregador in-memory de todas as entidades de uma obra."""

    def __init__(self) -> None:
        self.gerador_id = GeradorId()
        self.obras: dict[str, Obra] = {}
        self.etapas: dict[str, Etapa] = {}
        self.subetapas: dict[str, Subetapa] = {}
        self.servicos: dict[str, ServicoOrcamento] = {}
        self.planejamentos: dict[str, Planejamento] = {}
        self.fornecedores: dict[str, Fornecedor] = {}
        self.compras: dict[str, Compra] = {}
        self.financeiro: dict[str, Financeiro] = {}
        self.pagamentos: dict[str, Pagamento] = {}
        self.execucoes: dict[str, ExecucaoMedicao] = {}
        self.alteracoes: dict[str, Alteracao] = {}
        self.pendencias: dict[str, Pendencia] = {}
        self.atualizacoes: dict[str, Atualizacao] = {}
        self.documentos: dict[str, Documento] = {}

    # -- infraestrutura genérica ------------------------------------------
    @staticmethod
    def _registrar(colecao: dict, entidade) -> None:
        if entidade.id in colecao:
            raise ErroIdDuplicado(f"ID '{entidade.id}' já existe nesta coleção.")
        colecao[entidade.id] = entidade

    # -- Obra --------------------------------------------------------------
    def adicionar_obra(self, obra: Obra) -> Obra:
        self._registrar(self.obras, obra)
        return obra

    # -- Etapa (depende de Obra, REG-019) -----------------------------------
    def adicionar_etapa(self, etapa: Etapa) -> Etapa:
        if etapa.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Etapa '{etapa.id}' referencia Obra inexistente '{etapa.id_obra}'."
            )
        self._registrar(self.etapas, etapa)
        return etapa

    # -- Subetapa (depende de Etapa, REG-019) -------------------------------
    def adicionar_subetapa(self, subetapa: Subetapa) -> Subetapa:
        if subetapa.id_etapa not in self.etapas:
            raise ErroReferenciaInvalida(
                f"Subetapa '{subetapa.id}' referencia Etapa inexistente "
                f"'{subetapa.id_etapa}'."
            )
        self._registrar(self.subetapas, subetapa)
        return subetapa

    # -- Serviço/Orçamento (depende de Subetapa, REG-019) -------------------
    def adicionar_servico(self, servico: ServicoOrcamento) -> ServicoOrcamento:
        if servico.id_subetapa not in self.subetapas:
            raise ErroReferenciaInvalida(
                f"Serviço '{servico.id}' referencia Subetapa inexistente "
                f"'{servico.id_subetapa}'."
            )
        self._registrar(self.servicos, servico)
        return servico

    # -- Planejamento (Etapa e/ou Subetapa opcionais, granularidade [H]) ----
    def adicionar_planejamento(self, item: Planejamento) -> Planejamento:
        if item.id_etapa is not None and item.id_etapa not in self.etapas:
            raise ErroReferenciaInvalida(
                f"Planejamento '{item.id}' referencia Etapa inexistente '{item.id_etapa}'."
            )
        if item.id_subetapa is not None and item.id_subetapa not in self.subetapas:
            raise ErroReferenciaInvalida(
                f"Planejamento '{item.id}' referencia Subetapa inexistente "
                f"'{item.id_subetapa}'."
            )
        self._registrar(self.planejamentos, item)
        return item

    # -- Fornecedor (sem FK obrigatória) -------------------------------------
    def adicionar_fornecedor(self, fornecedor: Fornecedor) -> Fornecedor:
        self._registrar(self.fornecedores, fornecedor)
        return fornecedor

    # -- Compra (depende de Obra; Fornecedor/Serviço opcionais) --------------
    def adicionar_compra(self, compra: Compra) -> Compra:
        if compra.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Compra '{compra.id}' referencia Obra inexistente '{compra.id_obra}'."
            )
        if compra.id_fornecedor is not None and compra.id_fornecedor not in self.fornecedores:
            raise ErroReferenciaInvalida(
                f"Compra '{compra.id}' referencia Fornecedor inexistente "
                f"'{compra.id_fornecedor}'."
            )
        if compra.id_servico is not None and compra.id_servico not in self.servicos:
            raise ErroReferenciaInvalida(
                f"Compra '{compra.id}' referencia Serviço inexistente '{compra.id_servico}'."
            )
        self._registrar(self.compras, compra)
        return compra

    # -- Financeiro (depende de Obra; Serviço/Fornecedor/Compra opcionais) --
    def adicionar_financeiro(self, lancamento: Financeiro) -> Financeiro:
        if lancamento.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Financeiro '{lancamento.id}' referencia Obra inexistente "
                f"'{lancamento.id_obra}'."
            )
        if (
            lancamento.id_servico_vinculado is not None
            and lancamento.id_servico_vinculado not in self.servicos
        ):
            raise ErroReferenciaInvalida(
                f"Financeiro '{lancamento.id}' referencia Serviço inexistente "
                f"'{lancamento.id_servico_vinculado}'."
            )
        if lancamento.id_fornecedor is not None and lancamento.id_fornecedor not in self.fornecedores:
            raise ErroReferenciaInvalida(
                f"Financeiro '{lancamento.id}' referencia Fornecedor inexistente "
                f"'{lancamento.id_fornecedor}'."
            )
        if lancamento.id_compra is not None and lancamento.id_compra not in self.compras:
            raise ErroReferenciaInvalida(
                f"Financeiro '{lancamento.id}' referencia Compra inexistente "
                f"'{lancamento.id_compra}'."
            )
        self._registrar(self.financeiro, lancamento)
        return lancamento

    # -- Pagamento (depende de Financeiro do tipo Despesa/Custo, Etapa 4 Seção 20) --
    def adicionar_pagamento(self, pagamento: Pagamento) -> Pagamento:
        lancamento = self.financeiro.get(pagamento.id_financeiro)
        if lancamento is None:
            raise ErroReferenciaInvalida(
                f"Pagamento '{pagamento.id}' referencia lançamento financeiro "
                f"inexistente '{pagamento.id_financeiro}'."
            )
        if lancamento.tipo is not TipoLancamentoFinanceiro.DESPESA:
            raise ErroPagamentoDeTipoInvalido(
                f"Pagamento '{pagamento.id}' só pode referenciar um lançamento do "
                f"tipo 'Despesa/Custo' (Etapa 4, Seções 13/14/20); o lançamento "
                f"'{pagamento.id_financeiro}' é do tipo '{lancamento.tipo.rotulo}'."
            )
        self._registrar(self.pagamentos, pagamento)
        return pagamento

    # -- Execução/Medição (depende de Serviço) -------------------------------
    def adicionar_execucao(self, execucao: ExecucaoMedicao) -> ExecucaoMedicao:
        if execucao.id_servico not in self.servicos:
            raise ErroReferenciaInvalida(
                f"Execução '{execucao.id}' referencia Serviço inexistente "
                f"'{execucao.id_servico}'."
            )
        self._registrar(self.execucoes, execucao)
        return execucao

    # -- Alteração (depende de Obra) ------------------------------------------
    def adicionar_alteracao(self, alteracao: Alteracao) -> Alteracao:
        if alteracao.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Alteração '{alteracao.id}' referencia Obra inexistente "
                f"'{alteracao.id_obra}'."
            )
        self._registrar(self.alteracoes, alteracao)
        return alteracao

    # -- Pendência (depende de Obra) -------------------------------------------
    def adicionar_pendencia(self, pendencia: Pendencia) -> Pendencia:
        if pendencia.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Pendência '{pendencia.id}' referencia Obra inexistente "
                f"'{pendencia.id_obra}'."
            )
        self._registrar(self.pendencias, pendencia)
        return pendencia

    # -- Atualização (depende de Obra) -----------------------------------------
    def adicionar_atualizacao(self, atualizacao: Atualizacao) -> Atualizacao:
        if atualizacao.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Atualização '{atualizacao.id}' referencia Obra inexistente "
                f"'{atualizacao.id_obra}'."
            )
        self._registrar(self.atualizacoes, atualizacao)
        return atualizacao

    # -- Documento (depende de Obra) -------------------------------------------
    def adicionar_documento(self, documento: Documento) -> Documento:
        if documento.id_obra not in self.obras:
            raise ErroReferenciaInvalida(
                f"Documento '{documento.id}' referencia Obra inexistente "
                f"'{documento.id_obra}'."
            )
        self._registrar(self.documentos, documento)
        return documento
