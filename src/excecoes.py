"""Exceções específicas da fundação técnica do Sistema de Gestão de Obras."""

from __future__ import annotations


class ErroFundacaoTecnica(Exception):
    """Classe-base para erros da camada de fundação técnica (IDs/dados)."""


class ErroPrefixoDesconhecido(ErroFundacaoTecnica):
    """O nome de entidade informado não possui prefixo em config/ids_config.py."""


class ErroFormatoIdInvalido(ErroFundacaoTecnica):
    """A string não corresponde ao padrão '<PREFIXO>-<dígitos>' homologado."""


class ErroIdDuplicado(ErroFundacaoTecnica):
    """Tentativa de registrar um ID técnico que já existe na base de dados."""


class ErroReferenciaInvalida(ErroFundacaoTecnica):
    """Uma FK aponta para um registro que não existe na base (REG-002/REG-019)."""


class ErroHierarquiaInvalida(ErroFundacaoTecnica):
    """Violação da hierarquia oficial OBRA → ETAPA → SUBETAPA → SERVIÇO (REG-019)."""


class ErroValorNumericoInvalido(ErroFundacaoTecnica):
    """
    Um campo numérico de orçamento recebeu um valor não numérico ou
    negativo (Etapa 3, Seções 8 e 9: Quantidade Orçada e Valor Unitário
    devem ser numéricos e não podem ser negativos; zero é permitido).
    """
