# PLANO — ETAPA 8 — PLANEJAMENTO (Cronograma da Obra)
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-23 (continuação)
**Checkpoint de partida:** `a953acc` — ETAPA 7 - EXECUCAO E MEDICOES CONCLUIDA (277/277 testes passando, working tree limpo).
**Fase desta entrega:** Descoberta documental + Brainstorming + Plano.

> ⚠️ **ESTE PLANO FOI PARCIALMENTE SUPERADO PELA EXECUÇÃO.** Durante a implementação apareceu uma decisão de negócio indispensável que o plano não previa (duplicidade das datas entre ETAPAS e a entidade PLANEJAMENTO), homologada pelo responsável do projeto como **Opção A**. Em consequência, as **Seções 3, 7 e 8 abaixo descrevem um escopo que não foi entregue** (aba "Planejamento" própria, `movimentos.py`, meta de testes). O que foi efetivamente entregue está na **Seção 11 — Registro de execução**, e o resultado final está em **`relatorios/ETAPA_8_PLANEJAMENTO_RELATORIO_FINAL.md`**. Em caso de divergência, valem aqueles dois.

---

## 1. Descoberta documental — qual é a Etapa 8

Releitura completa: `AGENTS.md`, `00_DOCUMENTACAO_MESTRA`, `01_ARQUITETURA`, `02_MODELO_DE_DADOS` (`DAD_001`), `05_REGRAS_DE_NEGOCIO` (`REG_001`), `06_MODULOS_DO_SISTEMA` (`MOD_001`), `07_INTEGRACOES_E_BI`, `08_SEGURANCA...` (`SEC_001`), `09_TESTES_E_VALIDACAO`, `10_HOMOLOGACAO_E_ACEITE`, `13_VERSOES_E_HISTORICO`, `14_INTELIGENCIA_E_ANALISE`, `15_AUDITORIA_E_CONTROLE`, `16_CRONOGRAMA_E_EXECUCAO`, `04_INTERFACE_E_NAVEGACAO` (`UI_001`), os 3 planos de etapas anteriores (5/6/7), código (`src/`), testes (`testes/`), Excel V7 e histórico Git.

Módulos do Núcleo V1 (`AGENTS.md` §12, `MOD_001`) ainda não construídos após a Etapa 7: **Planejamento** e **Pendências**. Critério de desempate — o mesmo já usado para determinar a Etapa 7 (não "próximo da lista", e sim "o que já está homologado o suficiente para construir sem inventar regra"):

| | Planejamento | Pendências |
|---|---|---|
| Campos centrais homologados? | Datas Início/Fim Previstas e Duração são apenas [P] mas **não conflitantes** — só faltam ser digitadas/calculadas, sem exigir nenhum threshold | SLA (REG-011), Status (domínio fechado) e Prioridade — os 3 campos que definem a entidade — são **todos [H]**, sem nenhuma fórmula ou domínio proposto em nenhuma fonte |
| Matriz de permissões (`SEC_001` §3) | **[D]** — "Planejamento: EDITAR / VISUALIZAR" já promovida do histórico, mesmo nível de Execução/Financeiro/Orçamento (todos já construídos) | **[D] só o princípio** ("Edita" / "Consulta selecionada") — "critério de seleção" de quais Pendências o Cliente vê fica [H] |
| ID técnico reservado | [D] `PLN-` (`config/ids_config.py`) — confirmado | [D] `PEN-` — confirmado |
| Repositório (`BaseDados`) | `adicionar_planejamento` já existe (Etapa 1) | `adicionar_pendencia` já existe (Etapa 1) |
| O que falta para construir | Motor de cálculo simples (duração, variação de prazo) — sem inventar nada | Praticamente toda a entidade (SLA em dias, lista fechada de Status, critério de Prioridade) precisaria ser inventada |

**Conclusão: a Etapa 8 é o módulo Planejamento (tela "Cronograma da Obra")** — é o único dos dois módulos remanescentes do Núcleo V1 com campos centrais construíveis sem inventar regra de negócio. Pendências continua bloqueada por 3 decisões de negócio genuinamente indispensáveis (SLA em dias, domínio de Status, critério de Prioridade) — nenhuma delas está definida em nenhuma fonte, ao contrário do que se encontrou para Execução/Medições na Etapa 7.

---

## 2. Objetivo

Construir o motor de cálculo de cronograma (datas previstas × reais, duração, variação de prazo) por Etapa/Subetapa, o registro de datas, e a exposição correspondente no repositório e no Excel (aba "Planejamento" / tela "Cronograma da Obra") — preservando integralmente as Etapas 1–7.

## 3. Escopo

- Datas Início/Fim **Previstas** (já existem no modelo, nunca antes calculadas/expostas).
- **Lacuna documental encontrada e resolvida por completude, não por invenção** (ver Seção 4): Datas Início/Fim **Reais** — `UI_001` ("datas previstas e reais das Etapas/Subetapas"), `REG-014` ("Data Fim Prevista vs. data atual/**Data Fim Real**") e o próprio docstring de `Planejamento` em `src/modelo/entidades.py` ("Datas previstas/**reais**") já pressupõem esses campos; só a tabela de campos do `DAD_001` nunca os listou. Serão adicionados como [P], mesmo padrão de todo campo proposto nesta série de etapas.
- Duração Prevista/Real (calculada: Fim − Início).
- Variação de Prazo (Real − Previsto, em dias) — mesmo princípio já usado em REG-028 (Variação, nunca "Desvio"; sem cor/alerta) e REG-020 (valor calculado exposto, sem inventar threshold de alerta).
- Consolidação de datas por Obra (Data Início Prevista da Obra = MIN das Etapas; Data Fim Prevista da Obra = MAX das Etapas) — mesmo princípio de roll-up bottom-up já usado em Orçamento (SUM) e Execução (peso/contribuição), adaptado para MIN/MAX (operação natural para datas, não uma soma).
- Excel: aba **Planejamento** (1 linha = 1 item de cronograma, vínculo opcional e independente a Etapa OU Subetapa — mesmo padrão de Compras/Execução) + colunas informativas de consolidação em Etapas/Subetapas/Início.
- Testes unitários, de integração e de regressão.

## 4. Fora de escopo (permanece [H] — não será inventado)

- **REG-014 (threshold de dias de atraso que caracteriza alerta):** [H], "Resultado: não definido" no próprio texto da regra. Variação de Prazo (Real − Previsto) é exposta como **número simples**, sem cor/ícone/alerta — mesmo tratamento dado à Variação de REG-028 (Etapa 3) e à ausência de alertas em REG-013/015.
- **Dependência (predecessora)/encadeamento tipo Gantt:** [H] — "lógica de encadeamento não definida". Não será criado nenhum mecanismo de sequenciamento automático entre Etapas/Subetapas.
- **Status do Prazo (campo calculado da entidade):** [H] — depende do threshold de REG-014, que não existe. Não será inventado um domínio fechado (ex.: "No prazo/Atrasado/Concluído") sem fonte.
- Granularidade obrigatória (Etapa **ou** Subetapa, nunca ambos): a entidade já modela os dois vínculos como opcionais e independentes — mesma decisão de design já usada em Compras (Etapa 6), não uma regra de negócio nova a inventar.
- Pendências, SLA, domínios de Status/Prioridade de Pendências — módulo inteiro fora do escopo desta etapa (ver Seção 1).

## 5. Dependências

- Hierarquia OBRA → ETAPA → SUBETAPA (REG-019, já implementada) — Planejamento se vincula a ela, não a recria.
- Nenhuma dependência de Financeiro/Compras/Execução — Planejamento é uma camada de datas independente (mesmo princípio de separação conceitual já reforçado em REG-021 para Execução × Financeiro).

## 6. Decisões necessárias (nenhuma indispensável encontrada)

Nenhuma decisão de negócio genuinamente indispensável e indefinida foi encontrada para o escopo proposto (Seção 3). As únicas lacunas identificadas (Datas Reais ausentes da tabela do `DAD_001`; fórmula de consolidação MIN/MAX da Obra) são resolvidas por precedente/completude, não por invenção, e serão registradas como decisões de implementação no relatório final — mesmo padrão já usado nas Etapas 6 e 7. **Não há necessidade de interromper para perguntar nada nesta fase.**

## 7. Arquivos que provavelmente serão criados/modificados

**Criar:**
- `src/planejamento/__init__.py`, `calculos.py` (duração, variação de prazo, consolidação MIN/MAX por Obra), `movimentos.py` (`registrar_planejamento`)
- `testes/test_planejamento.py`, `testes/test_excel_planejamento.py`
- `scripts/gerar_arquivo_obra_modelo_v8.py` → `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V8.xlsx` (V7 preservado, mesmo padrão da Etapa 7)
- `relatorios/PLANO_ETAPA_8_PLANEJAMENTO_V1.md` (este arquivo, já criado)

**Modificar:**
- `src/modelo/entidades.py` (campos Data Início/Fim Real + validação/propriedades de duração/variação em `Planejamento`)
- `src/excel/construtor_workbook.py` (nova aba "Planejamento"; colunas informativas de consolidação em Etapas/Subetapas/Início — mesmo padrão da Etapa 7)
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001...md` e `05_REGRAS_DE_NEGOCIO/REG_001...md` (registro de homologação/nota de implementação)
- Possivelmente `testes/test_excel_construtor.py`/`test_excel_orcamento.py`/`test_expansao_excel.py` (deslocamento de posições de coluna, mesmo tipo de ajuste feito na Etapa 7)

## 8. Estratégia de testes

Mesma metodologia da Etapa 7: unitários para cada cálculo (duração, variação, consolidação MIN/MAX, casos sem data real ainda lançada → "não calculável", nunca inventar uma data), regressão (Planejamento não altera Orçamento/Financeiro/Execução/Compras), estrutural para Excel (openpyxl, sem motor de fórmulas — mesma limitação já registrada desde a Etapa 2). Meta: **277 (herdados) + novos, todos passando.**

## 9. Estratégia de validação do Excel

Estrutural (texto de fórmula, tabelas, dropdowns, ausência de range fixo e de ID exposto) — mesmo padrão de toda etapa anterior. Excel/COM e LibreOffice continuam indisponíveis neste ambiente (limitação já registrada desde a Etapa 2); não será instalado nada para contornar isso sem autorização explícita.

## 10. Riscos

1. Risco de a "Variação de Prazo" ser mal-interpretada como um alerta — mitigado mantendo-a como número simples, sem formatação condicional (mesmo texto de ressalva já usado em REG-028/REG-020).
2. Risco de reabrir a granularidade Etapa×Subetapa como se fosse uma decisão nova — mitigado citando o precedente já usado em Compras.
3. Risco de a consolidação MIN/MAX da Obra ficar vazia quando nenhuma Etapa tem data lançada — tratado como "não calculável" (célula vazia), nunca uma data inventada (mesmo princípio de REG-031/REG-010 para divisão por zero, adaptado a MIN/MAX sobre conjunto vazio).
4. Impacto em etapas anteriores: nenhum esperado — Planejamento é aditivo (nova aba + campos novos numa entidade que hoje não é lida por nenhum outro módulo).

---

## 11. Registro de execução — desvios em relação a este plano

Registrados aqui para auditoria; todos justificados e nenhum silencioso.

| # | Desvio | Motivo |
|---|---|---|
| 1 | **Uma decisão de negócio indispensável apareceu durante a implementação** (o plano dizia que não havia nenhuma). Ao abrir o `DAD_001` campo a campo, encontrou-se que ETAPAS já possuía os 4 campos de data **e** PLANEJAMENTO era uma entidade separada com as mesmas datas ("1 Etapa → N Planejamento", com "N" sem significado definido), enquanto SUBETAPAS não tinha nenhuma data. | A implementação foi **interrompida antes de qualquer código** e a decisão foi apresentada ao responsável do projeto, que homologou a **Opção A** (datas nas próprias Etapas/Subetapas). Nenhuma fonte — corrente ou histórica — resolvia isso; os 3 documentos históricos de Planejamento são templates vazios. |
| 2 | **Não foi criada uma aba "Planejamento"/"Cronograma da Obra"**; as 7 colunas de cronograma foram para as próprias abas Etapas e Subetapas. | Uma aba-espelho montada por fórmulas teria buffer fixo de linhas e voltaria a ignorar silenciosamente registros além dele — exatamente o defeito AUD-20/AUD-21 corrigido na Etapa 5.1, e contra a exigência explícita de "ausência de ranges fixos". As abas Etapas/Subetapas já são Tabelas estruturadas que se expandem sozinhas. A decisão homologada (datas no próprio registro) é integralmente respeitada. |
| 3 | **`src/planejamento/movimentos.py` não foi criado.** | Com a Opção A não existe entidade nova a registrar — as datas são campos de Etapa/Subetapa, que já têm seus próprios `adicionar_*`. Um módulo de orquestração vazio seria abstração prematura (AGENTS.md §22). |
| 4 | **SUBETAPAS ganhou 4 campos de data novos** (não previsto explicitamente no plano). | Consequência direta da Opção A: `UI_001` exige a tela exibindo datas "das Etapas/**Subetapas**", e SUBETAPAS não tinha nenhum campo de data. |
| 5 | **Defeito encontrado e corrigido durante a validação funcional:** a Variação de Prazo da Obra comparava `MAX(Fim Real)` com `MAX(Fim Previsto)` e, numa obra em andamento, reportava "113 dias de antecipação" onde havia atraso. | Corrigido nos DOIS motores (Python e fórmula Excel): enquanto houver Etapa prevista não concluída, o resultado é "não calculável" — mesmo princípio de REG-031 (divisão por zero nunca vira 0%). Travado por 3 testes novos. |
| 6 | Total de testes maior que o previsto (322 em vez de "277 + novos" estimados). | 45 testes novos: 26 em `test_planejamento.py` + 19 em `test_excel_planejamento.py`. |
