"""
Motor de Cálculos do módulo PLANEJAMENTO — Etapa 8 (Cronograma da Obra).

Escopo desta camada: **apenas a consolidação no nível da OBRA**. A
duração e a variação de prazo de cada Etapa/Subetapa são propriedades da
própria entidade (`Etapa.duracao_prevista_dias`,
`Subetapa.variacao_prazo_dias` etc., em `src/modelo/entidades.py`),
porque dependem só dela mesma — mesmo critério já usado na Etapa 3 para
`ServicoOrcamento.valor_calculado`/`valor_previsto`.

**Decisão estrutural homologada pelo responsável do projeto em
2026-09-23 (Etapa 8, Opção A):** as datas do cronograma moram nas
próprias ETAPAS/SUBETAPAS (fonte de verdade única por registro). A
entidade PLANEJAMENTO permanece reservada, sem uso como tabela — ver a
docstring de `Planejamento` em `src/modelo/entidades.py` para o registro
completo da duplicidade encontrada e da decisão tomada.

**As datas consolidadas abaixo NÃO sobrescrevem as datas próprias da
OBRA** (`Obra.data_inicio`, `Obra.data_prevista_termino`,
`Obra.data_real_termino`, digitadas pelo Operador). Elas são um valor
DERIVADO das Etapas, exposto sob nome explícito ("menor data das
Etapas"/"maior data das Etapas") para permitir a leitura gerencial
"as Etapas cabem dentro do prazo declarado da Obra?" — mesmo princípio
já usado na Etapa 7, que expôs "Contribuição na Obra" sem inventar um
"% isolado" (REG-020). Nenhuma automação altera a data declarada da
Obra; o sistema informa, o Operador decide (REG-032).

**NÃO EXISTE "Variação de Prazo da Obra" — indicador REJEITADO e
REMOVIDO por decisão do responsável do projeto em 2026-09-23
(Alternativa D1).** Ele havia sido criado durante a Etapa 8, sem regra
de negócio homologada que definisse seu significado, e produzia um
número enganoso: `MAX(Fim Real) − MAX(Fim Previsto)` pode tomar os dois
operandos de **Etapas diferentes**, porque `MAX(Fim Real)` só é o fim
real da Obra quando todas as Etapas previstas terminaram — antes disso é
apenas "a última data concluída até agora". Numa Obra com a Fundação
concluída em 10/05 e a Alvenaria prevista para 31/08 ainda em execução,
a conta dava −113 dias, lido como "113 dias de antecipação" numa obra
atrasada.

A decisão homologada foi **remover o indicador**, e não criar uma regra
nova para decidir quando a Obra está atrasada nem redefinir o indicador
para "Etapas concluídas". A informação de prazo permanece nos níveis em
que tem significado direto e já definido: **Variação de Prazo por Etapa
e por Subetapa** (`Etapa.variacao_prazo_dias` /
`Subetapa.variacao_prazo_dias`), calculada por registro, sempre com os
dois operandos da mesma linha. Ver `05_REGRAS_DE_NEGOCIO/REG_001`, Nota
de Implementação — Etapa 8.

**Fora de escopo, permanece [H] — não inventado aqui:** threshold de
dias que caracteriza alerta de atraso (REG-014, cujo próprio texto diz
"Resultado: não definido"); "Status do Prazo" como domínio fechado
(depende desse threshold); e a lógica de encadeamento/dependência entre
Etapas (tipo Gantt), explicitamente [H] em DAD_001. Por isso este módulo
expõe apenas datas e números — nenhuma classificação, cor ou alerta.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Etapa, dias_entre


def etapas_da_obra(base: BaseDados, id_obra: str) -> list[Etapa]:
    """Todas as Etapas vinculadas à Obra informada (REG-019)."""
    return [e for e in base.etapas.values() if e.id_obra == id_obra]


def _menor_data(datas: list[Optional[date]]) -> Optional[date]:
    """MIN ignorando datas ausentes; `None` quando nenhuma foi informada."""
    informadas = [d for d in datas if d is not None]
    return min(informadas) if informadas else None


def _maior_data(datas: list[Optional[date]]) -> Optional[date]:
    """MAX ignorando datas ausentes; `None` quando nenhuma foi informada."""
    informadas = [d for d in datas if d is not None]
    return max(informadas) if informadas else None


# ---------------------------------------------------------------------
# Consolidação no nível da OBRA (derivada das Etapas — nunca sobrescreve
# as datas próprias da Obra)
# ---------------------------------------------------------------------
def data_inicio_prevista_obra(base: BaseDados, id_obra: str) -> Optional[date]:
    """Menor Data Início Prevista entre as Etapas da Obra. `None` quando
    nenhuma Etapa tem a data informada — nunca uma data inventada."""
    return _menor_data([e.data_inicio_prevista for e in etapas_da_obra(base, id_obra)])


def data_fim_prevista_obra(base: BaseDados, id_obra: str) -> Optional[date]:
    """Maior Data Fim Prevista entre as Etapas da Obra."""
    return _maior_data([e.data_fim_prevista for e in etapas_da_obra(base, id_obra)])


def data_inicio_real_obra(base: BaseDados, id_obra: str) -> Optional[date]:
    """Menor Data Início Real entre as Etapas da Obra."""
    return _menor_data([e.data_inicio_real for e in etapas_da_obra(base, id_obra)])


def data_fim_real_obra(base: BaseDados, id_obra: str) -> Optional[date]:
    """Maior Data Fim Real entre as Etapas da Obra."""
    return _maior_data([e.data_fim_real for e in etapas_da_obra(base, id_obra)])


def duracao_prevista_obra_dias(base: BaseDados, id_obra: str) -> Optional[int]:
    """
    Fim Previsto consolidado − Início Previsto consolidado, em dias.

    Deriva exclusivamente das DUAS datas PREVISTAS consolidadas, ambas
    exibidas na aba Início. Não envolve data real e, por isso, não sofre
    do problema de operandos de Etapas diferentes que levou à remoção do
    indicador "Variação de Prazo da Obra" (ver docstring do módulo).
    """
    return dias_entre(
        data_inicio_prevista_obra(base, id_obra), data_fim_prevista_obra(base, id_obra)
    )


# ---------------------------------------------------------------------
# REMOVIDOS em 2026-09-23 (Alternativa D1 homologada) — não recriar sem
# regra de negócio homologada que defina o significado de "a Obra está
# atrasada":
#   - `variacao_prazo_obra_dias`  (o indicador rejeitado)
#   - `duracao_real_obra_dias`    (mesma fragilidade: `MAX(Fim Real)` só
#                                  é o fim da Obra quando tudo terminou)
#   - `ha_etapa_prevista_nao_concluida` (predicado que existia só para
#                                  suprimir os dois acima — Regra 8.1,
#                                  não homologada)
# A Variação de Prazo permanece por Etapa e por Subetapa, onde os dois
# operandos vêm sempre do mesmo registro.
# ---------------------------------------------------------------------
