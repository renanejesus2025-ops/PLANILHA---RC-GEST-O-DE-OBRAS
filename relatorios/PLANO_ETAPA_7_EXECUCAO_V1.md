# PLANO — ETAPA 7 — EXECUÇÃO/MEDIÇÕES (Progresso Físico)
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-23
**Checkpoint de partida:** `97e77c7` — ETAPA 6 - COMPRAS CONCLUIDA (230/230 testes passando).
**Protocolo seguido:** Descoberta documental → Brainstorming → Plano → Implementação → Testes → Excel → Auditoria → Relatório (métodos `/brainstorming`, `/writing-plans`, `/subagent-driven-development` e `/dispatching-parallel-agents` não estão disponíveis neste ambiente — metodologia seguida manualmente, conforme instruído).

---

## 1. Descoberta documental — qual é a Etapa 7

Não havia nenhuma referência textual a "Etapa 7" em nenhum documento. A etapa foi determinada por reconciliação entre:

- `AGENTS.md` §12 e `06_MODULOS_DO_SISTEMA/MOD_001` — lista oficial do Núcleo V1: Obras; Etapas; Serviços/Orçamento; **Planejamento**; Compras; Financeiro; **Execução/Medições**; Alterações; **Pendências** — os três módulos ainda não construídos após a Etapa 6.
- `13_VERSOES_E_HISTORICO` (git log) — ordem real de construção até aqui: Fundação(1) → Base da Obra(2) → Orçamento(3) → Financeiro(4) → Alterações(5, 5.1) → Compras(6). A ordem real já diverge da ordem do MOD_001, então a prioridade não é "a próxima da lista", e sim "o que já está homologado o suficiente para construir sem inventar regra".
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001` — confirma que Planejamento, Execução/Medições e Pendências têm o ID técnico reservado mas o módulo "ainda não construído".
- `05_REGRAS_DE_NEGOCIO/REG_001` — critério decisivo: **REG-007, REG-008, REG-019, REG-020, REG-021, REG-022, REG-023, REG-024, REG-025** (todas **[D] HOMOLOGADO em 2026-09-16**) formam um motor de cálculo de progresso físico já inteiramente especificado, testável e não implementado. Planejamento (REG-014, campo "Dependência"/"Status do Prazo") e Pendências (REG-011 SLA, prioridade, status) têm a maioria dos seus campos ainda **[H]**, sem fórmula nem domínio fechado — construí-los agora exigiria decisões de negócio inexistentes em qualquer fonte.

**Conclusão:** a **Etapa 7 é o módulo Execução/Medições** (Progresso Físico da Obra) — é o único dos três módulos remanescentes do Núcleo V1 cujas regras de cálculo já estão homologadas em detalhe suficiente para implementação sem inventar nada.

---

## 2. Objetivo

Construir o motor de cálculo de progresso físico da obra (Serviço → Subetapa → Etapa → Obra), a entrada de medições, e a exposição correspondente na base técnica, no repositório e no Excel — preservando integralmente as Etapas 1–6.

## 3. Escopo

- `ServicoOrcamento.metodo_execucao` / `status_execucao` (já existentes desde a Etapa 1, nunca antes calculados): % de execução do Serviço (REG-007, Modelo Híbrido).
- Elegibilidade para o cálculo físico (REG-022).
- Peso Automático Global do Serviço, baseado em Valor Orçado (REG-008).
- Proteção do Peso Manual (REG-023), redistribuição proporcional entre pesos automáticos (REG-024), bloqueio quando 100% dos elegíveis têm peso manual (REG-025).
- Consolidação hierárquica do progresso físico até a Obra (REG-020, parte homologada).
- Nova entidade operacional: registro de Medições (`ExecucaoMedicao`, método Quantitativo).
- Excel: nova aba **Execução** (log de medições) e extensão da aba **Serviços** com as colunas de método/peso/percentual.
- Testes unitários, de integração e de regressão.

## 4. Fora de escopo (permanece [H] — não será inventado)

- REG-009 (bloqueio vs. alerta de medição acima de 100%) — resolvido **por precedente**, não por invenção: mesma política já homologada em REG-010/REG-032 ("o sistema informa, o Operador decide"). Lançamento acima de 100% é permitido e apenas informativo.
- REG-011 (SLA de Pendência), REG-013/014/015 (thresholds de alerta), granularidade e "Dependência" de Planejamento — módulos/campos que não fazem parte do escopo desta etapa.
- **% de execução "isolado" por Subetapa/Etapa** — REG-020 marca explicitamente como **[H]** ("fórmula técnica exata... não foi detalhada nem inventada"). Como o Peso Automático é sempre global (REG-008), não renormalizado por grupo, não existe uma forma homologada de expressar "a Subetapa X está Y% pronta" isoladamente. Esta etapa expõe, em vez disso, dois valores informativos e matematicamente diretos (não um % isolado inventado): **Peso Consolidado do Grupo** (Σ peso efetivo dos serviços elegíveis do grupo) e **Contribuição no Progresso da Obra** (Σ peso efetivo × % execução do serviço, dentro do grupo, em pontos percentuais da Obra). Isso preserva o princípio de não-invenção e ainda assim fornece informação gerencial real.
- Domínio fechado de "Status" de Execução/Medição (campo genérico da entidade, distinto de `StatusExecucao`) — continua [H]/texto livre, mesmo tratamento dado a campos [H] equivalentes em Compras (Forma de Pagamento, Status de Entrega).
- Aportes vinculados a Serviço para fins de peso físico (REG-021, mecanismo de vínculo [H]) — não implementado; nenhuma automação entre Aporte e peso físico é criada (regressão obrigatória: Aporte continua sem efeito no progresso físico).

## 5. Decisões resolvidas automaticamente (documentadas, não inventadas)

| Decisão | Como foi resolvida | Precedente |
|---|---|---|
| Elegibilidade REG-022 usa qual domínio de Status? | `StatusServico.integra_orcamento_corrente` (Ativo/Concluído = elegível; Cancelado/Retirado do Escopo/Substituído = excluído) | Já homologado e testado desde a Etapa 3 para o mesmo propósito de exclusão |
| Base do "Valor Orçado" em REG-008 | `servico.valor_previsto` (REG-026, já homologado) | Mesmo campo usado por `total_previsto_*` (Etapa 3) |
| Fórmula técnica de redistribuição proporcional (REG-024) | Proporcional ao **Peso Automático Bruto** de cada serviço automático entre si (única leitura literal de "proporcional" sem outra base mencionada na regra) | Nenhuma alternativa foi citada em nenhuma fonte |
| "Quantidade Executada" do Método Quantitativo (REG-007) quando há múltiplas medições | Soma acumulada de todas as medições do Serviço (prática padrão de medição de obra; nenhuma fonte definiu "última medição substitui a anterior") | Documentado explicitamente no código, como a Etapa 6 fez com decisões de design equivalentes |
| % Execução de Serviço sem medição/status lançado | Tratado como 0% na consolidação (mesmo valor de `StatusExecucao.PENDENTE`), nunca omitido do denominador | REG-007.2 já define Pendente = 0% |
| REG-009 (excedente de medição) | Não bloqueia, apenas informa (soma pode superar 100%) | REG-010 regra 19/20, REG-032 |

## 6. Entidades / Validação

- `src/modelo/entidades.py` — `ExecucaoMedicao.__post_init__` passa a validar `quantidade_executada` com `validar_numero_nao_negativo` (mesmo padrão de todo campo de quantidade/valor desde a Etapa 3).
- `src/excecoes.py` — nova exceção `ErroDistribuicaoPesoInvalida` (REG-025).

## 7. Arquivos a criar

- `src/execucao/__init__.py`
- `src/execucao/calculos.py` — elegibilidade (REG-022), % execução do Serviço (REG-007), peso automático bruto e efetivo com proteção/redistribuição/bloqueio (REG-008/023/024/025), consolidação até a Obra (REG-020), contribuição por grupo (Subetapa/Etapa).
- `src/execucao/movimentos.py` — `registrar_medicao`.
- `testes/test_execucao.py` — regras unitárias + integração/regressão (Execução não altera Orçamento/Financeiro/Compras).
- `testes/test_excel_execucao.py` — estrutura da aba nova e das colunas novas em Serviços.

## 8. Arquivos a modificar

- `src/modelo/entidades.py`, `src/excecoes.py` (validação e exceção acima).
- `src/excel/construtor_workbook.py` — estender `COLUNAS_SERVICOS`/`COL_SRV_*` (Método de Execução, Status de Execução, Peso Ajustado, Peso Automático, Peso Efetivo, % Execução do Serviço); nova aba `Execução`; colunas informativas de "Peso Consolidado"/"Contribuição" em Etapas/Subetapas; célula de "% Execução Física da Obra" na aba Início.
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001` e `05_REGRAS_DE_NEGOCIO/REG_001` — registrar as decisões da Seção 5 (mesmo padrão das revisões anteriores).
- `scripts/gerar_arquivo_obra_modelo_v6.py` (ou novo `_v7`, decisão no passo Excel — ver Seção 9).
- `testes/test_excel_construtor.py`, `testes/test_base_dados.py` se necessário para cobrir a nova aba/coleção.

## 9. Excel — V6 preservado, V7 criado

**Correção durante a implementação:** a Seção 9 original desta versão do plano presumia, incorretamente, que um único gerador `_v6` era reutilizado entre etapas. A inspeção de `scripts/` mostrou o padrão real e já estabelecido desde a Etapa 2: **cada etapa de construção cria seu próprio script versionado** (`gerar_arquivo_obra_modelo_v2.py` … `_v6.py`), e `dados/` acumula um arquivo `.xlsx` por versão (V1 a V6, todos preservados, nenhum sobrescrito). Esta é também a convenção pedida pelo prompt da Etapa 7 ("Se for necessário criar V7: V6 permanece intacto; V7 passa a ser a nova versão").

Seguido, portanto, o padrão real: criado `scripts/gerar_arquivo_obra_modelo_v7.py` (novo arquivo, script V6 intocado) gerando `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V7.xlsx`. V1–V6 permanecem no disco, byte-a-byte intocados (confirmado por `git status`/`git diff` — nenhuma alteração nos arquivos V1–V6). Tabelas estruturadas, dropdowns por nome, Design System e ausência de ranges fixos são preservados (mesmos helpers `_registrar_tabela`/`_aplicar_bordas`/estilos já existentes).

## 10. Testes

- Unitários: elegibilidade, peso automático bruto (soma 100%), proteção de peso manual, redistribuição proporcional, bloqueio REG-025, % execução por método (quantitativo e status), consolidação da Obra.
- Integração/regressão: registrar Execução não altera Orçamento Previsto/Vigente, Financeiro, Compras (mesmo padrão de `test_compras.py`); hierarquia e IDs permanecem íntegros.
- Meta: **230 (herdados) + novos, todos passando.**

## 11. Critérios de aceite

1. Todas as regras [D] da Seção 3 implementadas e testadas.
2. Nenhuma regra [H] inventada — Seção 4 registrada e respeitada.
3. 230/230 testes anteriores continuam passando + novos testes passando.
4. Excel gerado sem erro, com tabela estruturada, sem ranges fixos, sem IDs expostos.
5. Nenhuma alteração destrutiva em Etapas 1–6.
6. Nenhum commit/push realizado.

## 12. Riscos

1. Risco de leitura da fórmula de redistribuição proporcional (REG-024) — mitigado documentando a interpretação adotada como decisão de implementação, não como fato homologado.
2. Risco de a aba Serviços ficar densa — mitigado mantendo "menos abas" (reaproveitar Serviços em vez de nova aba de pesos).
3. Risco de a "Contribuição por grupo" ser mal-interpretada como "% da Subetapa" — mitigado com rótulo explícito e nota no relatório final.
4. Excel/COM pode não estar disponível neste ambiente para validação de fórmulas ao vivo — se ocorrer, será registrado como limitação (AGENTS.md, mesmo padrão de "Excel/COM não disponível" já usado em etapas anteriores).
