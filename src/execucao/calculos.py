"""
Motor de Cálculos do módulo EXECUÇÃO/MEDIÇÕES — Etapa 7 (Progresso Físico).

Implementa exclusivamente as regras já **[D] HOMOLOGADAS** em
`05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md`:

- REG-007 — % de Execução do Serviço (Modelo Híbrido: Quantitativo ou Status).
- REG-008 — Peso Automático do Serviço (baseado no Valor Orçado, Global).
- REG-019 — Hierarquia oficial OBRA → ETAPA → SUBETAPA → SERVIÇO.
- REG-020 — Consolidação Hierárquica do Progresso Físico até a Obra.
- REG-021 — Aporte financeiro não altera peso físico automaticamente
  (garantido por CONSTRUÇÃO: nenhuma função aqui lê `BaseDados.financeiro`).
- REG-022 — Serviços Elegíveis para o cálculo do progresso físico.
- REG-023 — Proteção do Peso Manual.
- REG-024 — Redistribuição Proporcional entre Serviços com Peso Automático.
- REG-025 — Bloqueio quando todos os Serviços Elegíveis têm Peso Manual.

Decisões de implementação desta etapa (não são regras de negócio novas —
ver `relatorios/PLANO_ETAPA_7_EXECUCAO_V1.md`, Seção 5, para a
justificativa de cada uma):

1. Elegibilidade (REG-022) usa `StatusServico.integra_orcamento_corrente`
   como o mesmo domínio já homologado (Etapa 3) para "não excluído do
   escopo vigente" — não inventa um domínio novo.
2. "Valor Orçado" de REG-008 é `servico.valor_previsto` (REG-026).
3. A fórmula técnica de REG-024 ("proporcional") é lida como proporcional
   ao Peso Automático Bruto de cada serviço automático entre si — única
   leitura literal possível sem outra base citada na regra.
4. "Quantidade Executada" do Método Quantitativo é a SOMA de todas as
   medições (`ExecucaoMedicao`) do Serviço — não a última medição.
5. Um Serviço elegível sem % de execução calculável (sem método definido,
   sem medição, ou Status de Execução ausente) entra na consolidação como
   0% — nunca é excluído do denominador do peso (mesmo valor de
   `StatusExecucao.PENDENTE`).
6. REG-009 (medição acima de 100%) não bloqueia — mesma política já
   homologada em REG-010/REG-032 ("o sistema informa, o Operador decide").

Deliberadamente NÃO implementado (permanece [H], REG-020): um "% de
execução isolado" por Subetapa/Etapa. Como o peso é sempre global
(REG-008) e não é renormalizado por grupo, não existe fórmula homologada
para expressar isso como um percentual 0–100% de um grupo isoladamente.
Em vez disso, `peso_consolidado_grupo` e `contribuicao_grupo` expõem
valores diretos e não ambíguos (nunca chamados de "% da Subetapa").
"""

from __future__ import annotations

from typing import Optional

from src.base_dados.repositorio import BaseDados
from src.excecoes import ErroDistribuicaoPesoInvalida
from src.modelo.entidades import ServicoOrcamento
from src.modelo.enums import MetodoExecucao


# ---------------------------------------------------------------------
# REG-022 — Elegibilidade
# ---------------------------------------------------------------------
def servico_elegivel_execucao(base: BaseDados, id_servico: str) -> bool:
    """
    Critérios homologados (REG-022): vínculo válido com Subetapa (REG-019);
    valor orçado válido (necessário para determinar o peso, REG-008);
    não excluído do escopo vigente — mesmo domínio já homologado em
    `StatusServico.integra_orcamento_corrente` (Cancelado, Retirado do
    Escopo e Substituído ficam de fora; os demais, inclusive Status
    ausente, ficam dentro).
    """
    servico = base.servicos.get(id_servico)
    if servico is None:
        return False
    if servico.id_subetapa not in base.subetapas:
        return False
    if servico.valor_previsto is None:
        return False
    if servico.status is not None and not servico.status.integra_orcamento_corrente:
        return False
    return True


def _obra_do_servico(base: BaseDados, servico: ServicoOrcamento) -> Optional[str]:
    subetapa = base.subetapas.get(servico.id_subetapa)
    if subetapa is None:
        return None
    etapa = base.etapas.get(subetapa.id_etapa)
    if etapa is None:
        return None
    return etapa.id_obra


def servicos_elegiveis_obra(base: BaseDados, id_obra: str) -> list[ServicoOrcamento]:
    """Todos os Serviços Elegíveis (REG-022) que pertencem à Obra informada."""
    resultado = []
    for servico in base.servicos.values():
        if not servico_elegivel_execucao(base, servico.id):
            continue
        if _obra_do_servico(base, servico) == id_obra:
            resultado.append(servico)
    return resultado


# ---------------------------------------------------------------------
# REG-007 — % de Execução do Serviço (Modelo Híbrido)
# ---------------------------------------------------------------------
def quantidade_executada_acumulada(base: BaseDados, id_servico: str) -> float:
    """
    Soma de `quantidade_executada` de todas as medições (`ExecucaoMedicao`)
    lançadas para este Serviço (decisão de implementação 4 — ver
    docstring do módulo). Medições sem quantidade informada contam 0.
    """
    return sum(
        (m.quantidade_executada or 0.0)
        for m in base.execucoes.values()
        if m.id_servico == id_servico
    )


def percentual_execucao_servico(base: BaseDados, id_servico: str) -> Optional[float]:
    """
    % de Execução do Serviço (REG-007), em pontos percentuais (0–100).

    - Método Quantitativo: Quantidade Executada Acumulada / Quantidade
      Planejada/Elegível (`servico.quantidade_orcada`) × 100. `None`
      quando a Quantidade Orçada é ausente ou zero (não calculável —
      REG-007 registra este caso como [H]; tratado aqui com o mesmo
      padrão de divisão por zero já homologado em REG-031/REG-010, nunca
      0%, nunca erro).
    - Método por Status: tabela fixa homologada (REG-007.2) —
      `StatusExecucao.percentual` (Pendente=0, Em andamento=50,
      Concluído=100). `None` quando `status_execucao` não foi informado.
    - Sem `metodo_execucao` definido: `None` (não calculável — nenhum
      método foi atribuído a este Serviço).

    Não há arredondamento, tolerância ou tratamento de excedente acima de
    100% (REG-007/REG-009 permanecem [H] nesses pontos) — o valor bruto é
    retornado tal como calculado, podendo superar 100.
    """
    servico = base.servicos.get(id_servico)
    if servico is None:
        return None
    if servico.metodo_execucao is MetodoExecucao.QUANTITATIVO:
        planejada = servico.quantidade_orcada
        if not planejada:
            return None
        executada = quantidade_executada_acumulada(base, id_servico)
        return executada / planejada * 100
    if servico.metodo_execucao is MetodoExecucao.STATUS:
        if servico.status_execucao is None:
            return None
        return servico.status_execucao.percentual
    return None


# ---------------------------------------------------------------------
# REG-008/023/024/025 — Peso Automático, Proteção, Redistribuição, Bloqueio
# ---------------------------------------------------------------------
def peso_automatico_bruto(base: BaseDados, id_servico: str) -> Optional[float]:
    """
    Peso Automático "cru" (REG-008), sem considerar ajustes manuais de
    OUTROS serviços: Valor Orçado do Serviço / Σ Valor Orçado dos
    Serviços Elegíveis da Obra × 100 (denominador sempre global, nunca
    renormalizado por Subetapa/Etapa). `None` quando o serviço não é
    elegível, quando não há Serviços Elegíveis na Obra, ou quando a soma
    dos valores orçados elegíveis é zero (não calculável).
    """
    servico = base.servicos.get(id_servico)
    if servico is None or not servico_elegivel_execucao(base, id_servico):
        return None
    id_obra = _obra_do_servico(base, servico)
    if id_obra is None:
        return None
    elegiveis = servicos_elegiveis_obra(base, id_obra)
    total = sum(s.valor_previsto or 0.0 for s in elegiveis)
    if total == 0:
        return None
    return (servico.valor_previsto or 0.0) / total * 100


def pesos_efetivos_obra(base: BaseDados, id_obra: str) -> dict[str, float]:
    """
    Peso EFETIVO (0–100) de cada Serviço Elegível da Obra, já aplicando:

    - REG-023 (Proteção do Peso Manual): serviço com `peso_ajustado`
      preenchido usa esse valor tal como informado — nunca recalculado.
    - REG-024 (Redistribuição Proporcional): a diferença entre 100% e a
      soma dos pesos manuais protegidos é redistribuída apenas entre os
      Serviços com peso automático, proporcionalmente ao Peso Automático
      Bruto de cada um entre si (decisão de implementação 3).
    - REG-025 (Bloqueio): se TODOS os Serviços Elegíveis tiverem peso
      manual e a soma não totalizar 100%, levanta
      `ErroDistribuicaoPesoInvalida` — nenhum peso é alterado.

    Retorna `{}` quando não há Serviços Elegíveis na Obra.
    """
    elegiveis = servicos_elegiveis_obra(base, id_obra)
    if not elegiveis:
        return {}

    manuais = {s.id: s.peso_ajustado for s in elegiveis if s.peso_ajustado is not None}
    automaticos = [s for s in elegiveis if s.peso_ajustado is None]

    soma_manual = sum(manuais.values())

    if not automaticos:
        # REG-025: 100% dos elegíveis têm peso manual.
        if round(soma_manual, 9) != 100:
            raise ErroDistribuicaoPesoInvalida(
                f"Todos os {len(elegiveis)} Serviço(s) Elegível(is) da Obra "
                f"'{id_obra}' têm Peso Ajustado manualmente e a soma "
                f"({soma_manual}) não totaliza 100%. Nenhum Serviço com "
                "peso automático está disponível para redistribuição "
                "(REG-025) — reajuste os pesos manuais para somar 100%."
            )
        return dict(manuais)

    pesos_brutos = {
        s.id: (peso_automatico_bruto(base, s.id) or 0.0) for s in automaticos
    }
    total_bruto_automaticos = sum(pesos_brutos.values())
    faixa_a_distribuir = 100 - soma_manual

    resultado = dict(manuais)
    if total_bruto_automaticos == 0:
        # Nenhum Serviço automático tem valor orçado válido — distribui
        # igualmente entre eles (não há base proporcional disponível).
        fatia_igual = faixa_a_distribuir / len(automaticos)
        for s in automaticos:
            resultado[s.id] = fatia_igual
        return resultado

    for s in automaticos:
        proporcao = pesos_brutos[s.id] / total_bruto_automaticos
        resultado[s.id] = proporcao * faixa_a_distribuir
    return resultado


def peso_efetivo_servico(base: BaseDados, id_servico: str) -> Optional[float]:
    """Conveniência: peso efetivo (REG-023/024/025) de um único Serviço."""
    servico = base.servicos.get(id_servico)
    if servico is None:
        return None
    id_obra = _obra_do_servico(base, servico)
    if id_obra is None:
        return None
    return pesos_efetivos_obra(base, id_obra).get(id_servico)


# ---------------------------------------------------------------------
# REG-020 — Consolidação Hierárquica do Progresso Físico
# ---------------------------------------------------------------------
def percentual_execucao_obra(base: BaseDados, id_obra: str) -> Optional[float]:
    """
    % de Execução Física consolidado da Obra (REG-020): Σ (peso efetivo do
    Serviço/100 × % de Execução do Serviço), somado sobre todos os
    Serviços Elegíveis da Obra. Serviço elegível sem % calculável entra
    como 0% (decisão de implementação 5). `None` quando não há Serviço
    Elegível na Obra (não calculável, nunca 0%).
    """
    elegiveis = servicos_elegiveis_obra(base, id_obra)
    if not elegiveis:
        return None
    pesos = pesos_efetivos_obra(base, id_obra)
    total = 0.0
    for servico in elegiveis:
        peso = pesos.get(servico.id, 0.0)
        percentual = percentual_execucao_servico(base, servico.id) or 0.0
        total += peso / 100 * percentual
    return total


def peso_consolidado_grupo(base: BaseDados, servicos_do_grupo: list[ServicoOrcamento]) -> float:
    """
    Σ peso efetivo (0–100, escala da Obra) dos Serviços Elegíveis do
    grupo informado (Subetapa ou Etapa). NÃO é um percentual 0–100% do
    grupo isoladamente — é a fatia do total da Obra que o grupo
    representa (ver docstring do módulo, item "Deliberadamente NÃO
    implementado").
    """
    total = 0.0
    for servico in servicos_do_grupo:
        if not servico_elegivel_execucao(base, servico.id):
            continue
        id_obra = _obra_do_servico(base, servico)
        if id_obra is None:
            continue
        total += pesos_efetivos_obra(base, id_obra).get(servico.id, 0.0)
    return total


def contribuicao_grupo(base: BaseDados, servicos_do_grupo: list[ServicoOrcamento]) -> float:
    """
    Σ (peso efetivo/100 × % de Execução do Serviço) dos Serviços
    Elegíveis do grupo — quanto o grupo já contribuiu, em pontos
    percentuais do total da Obra (0–100), para o progresso físico da
    Obra. Mesma ressalva de `peso_consolidado_grupo`: não é o "%
    executado da Subetapa/Etapa" isoladamente.
    """
    total = 0.0
    for servico in servicos_do_grupo:
        if not servico_elegivel_execucao(base, servico.id):
            continue
        id_obra = _obra_do_servico(base, servico)
        if id_obra is None:
            continue
        peso = pesos_efetivos_obra(base, id_obra).get(servico.id, 0.0)
        percentual = percentual_execucao_servico(base, servico.id) or 0.0
        total += peso / 100 * percentual
    return total


def contribuicao_subetapa(base: BaseDados, id_subetapa: str) -> float:
    servicos_do_grupo = [s for s in base.servicos.values() if s.id_subetapa == id_subetapa]
    return contribuicao_grupo(base, servicos_do_grupo)


def contribuicao_etapa(base: BaseDados, id_etapa: str) -> float:
    ids_subetapas = {s.id for s in base.subetapas.values() if s.id_etapa == id_etapa}
    servicos_do_grupo = [s for s in base.servicos.values() if s.id_subetapa in ids_subetapas]
    return contribuicao_grupo(base, servicos_do_grupo)


def peso_consolidado_subetapa(base: BaseDados, id_subetapa: str) -> float:
    servicos_do_grupo = [s for s in base.servicos.values() if s.id_subetapa == id_subetapa]
    return peso_consolidado_grupo(base, servicos_do_grupo)


def peso_consolidado_etapa(base: BaseDados, id_etapa: str) -> float:
    ids_subetapas = {s.id for s in base.subetapas.values() if s.id_etapa == id_etapa}
    servicos_do_grupo = [s for s in base.servicos.values() if s.id_subetapa in ids_subetapas]
    return peso_consolidado_grupo(base, servicos_do_grupo)
