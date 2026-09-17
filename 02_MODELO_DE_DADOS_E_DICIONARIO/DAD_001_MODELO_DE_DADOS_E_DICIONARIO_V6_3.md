# Modelo de Dados e Dicionário — V6.3 (Revisão 6 — Orçamento dos Serviços)

**Data da Revisão 1:** 2026-09-16 — `AUDITORIA_PRE_CONSTRUCAO_V1` identificou ausência de dicionário de dados executável. A Revisão 1 substituiu a versão anterior (3 linhas) por uma especificação estruturada por entidade.
**Motivo da Revisão 2:** o responsável pelo projeto homologou a **Opção B — Vincular Aporte ao Orçamento** (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-006/REG-017). A Revisão 2 ajustou apenas as entidades OBRAS e FINANCEIRO.
**Motivo da Revisão 3:** o responsável pelo projeto homologou **SUBETAPAS como entidade própria do modelo de dados**, eliminando o conflito [C] registrado na Revisão 1 ("SUBETAPAS: tabela própria, nível dentro de ETAPAS, ou nível dentro de SERVIÇOS/ORÇAMENTO?"). Hierarquia oficial homologada: **OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO**. Esta revisão ajusta as entidades SUBETAPAS, ETAPAS e SERVIÇOS/ORÇAMENTO; as demais 10 entidades não foram alteradas.
**Motivo da Revisão 4:** o responsável pelo projeto homologou o **MODELO HÍBRIDO de cálculo do progresso físico** (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-007/REG-008/REG-020/REG-021): método de execução do serviço por medição quantitativa ou por status/conclusão; peso automático do serviço a partir do valor orçado; consolidação hierárquica Serviço → Subetapa → Etapa → Obra usando esses pesos; ajuste manual de peso como exceção (campos de rastreabilidade ainda não homologados); e separação obrigatória entre aporte financeiro e peso físico. Esta revisão ajusta as entidades ETAPAS, SUBETAPAS, SERVIÇOS/ORÇAMENTO e FINANCEIRO/OBRAS (nota de separação conceitual); as demais entidades não foram alteradas.
**Motivo da Revisão 5:** o responsável pelo projeto homologou a **consolidação completa do motor de progresso físico** (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-007/REG-008/REG-020/REG-022 a REG-025): fórmula do método quantitativo e tabela fechada do método por status (Pendente 0% / Em andamento 50% / Concluído 100%); peso automático sempre **global** sobre o total de Serviços Elegíveis da Obra, sem renormalização por Subetapa/Etapa; critérios de elegibilidade de Serviço para o cálculo físico; ajuste manual de peso sem exigência obrigatória de justificativa/aprovação prévia, mas com preservação obrigatória do peso automático original e do peso ajustado; proteção do peso manual contra redistribuição automática; redistribuição proporcional restrita aos serviços com peso automático; e bloqueio (em vez de redistribuição) quando todos os Serviços Elegíveis estiverem com peso manual. Esta revisão ajusta as entidades SERVIÇOS/ORÇAMENTO, ETAPAS e SUBETAPAS; as demais entidades não foram alteradas.
**Motivo da Revisão 6:** o responsável pelo projeto homologou o módulo/base de **ORÇAMENTO** (Etapa 3 de construção; ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-003/REG-026/REG-027/REG-028): "Valor Total Orçado" foi renomeado para **Valor Calculado** (Quantidade × Valor Unitário, sempre calculado, nunca sobrescrito); novos campos **Valor Previsto (Ajuste Manual)**, **Ajuste Manual**, **Valor Previsto** e **Variação** na entidade SERVIÇOS/ORÇAMENTO; o campo **Status** de SERVIÇOS/ORÇAMENTO deixa de ser [H] e passa a ter domínio fechado homologado (Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído); REG-003 (Orçamento Previsto) passa a somar o Valor Previsto dos Serviços elegíveis, não mais o Valor Calculado isolado. Esta revisão ajusta apenas a entidade SERVIÇOS/ORÇAMENTO; as demais 12 entidades não foram alteradas.

## Legenda de status

- **[D] DOCUMENTADO** — vem literalmente de uma fonte já homologada (AGENTS.md, MOD_001, ou histórico V5/V6 citado).
- **[P] PROPOSTA** — decisão de modelagem sugerida nesta revisão, ainda sem homologação formal do responsável pelo projeto.
- **[H] HOMOLOGAR** — decisão em aberto; não há informação suficiente nem proposta seria seguro assumir sem validação do responsável.
- **[C] CONFLITO** — duas fontes ou dois conceitos documentados que não se conciliam sem uma decisão explícita.

Nenhum campo, fórmula, threshold ou domínio foi tratado como definitivo sem essa marcação.

## Princípio (mantido do documento anterior) — [D]

A base operacional é a fonte estruturada para interface, cálculos, auditoria e BI futuro. Identificadores técnicos podem existir internamente; o usuário vê nomes reais e claros (AGENTS.md §11).

## Aproveitamento do histórico

- **Aproveitado [D]:** a lista de entidades centrais e auxiliares (AGENTS.md §11/§12, `MOD_001_MODULOS_DO_SISTEMA_V6_3.md`, `00_DOCUMENTACAO_MESTRA_V5.md`/`_V6.md`) e os exemplos de nomenclatura real de serviços/etapas citados em AGENTS.md §11 (Alvenaria, Elétrica, Hidráulica, Fundação, Pintura, Acabamento, Cimento, Cal, Areia fina, Reboco, Chapisco, Assentamento de blocos).
- **Apenas referência, não aproveitado como requisito:** `DAD_001_MODELO_UNIVERSAL.md` e `DAD_002` a `DAD_010` do histórico V1–V6 — são placeholders sem conteúdo de campo (confirmado na auditoria); não continham nenhuma decisão a herdar.
- **Menção que motivou uma entidade nova nesta revisão:** `REG_001_REGRAS_DE_NEGOCIO_V6_3.md` cita "subetapas" ao falar de execução — por isso SUBETAPAS aparece abaixo como entidade candidata, não porque exista um dicionário histórico para ela.

---

## ENTIDADE: OBRAS

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** unidade central que agrupa todos os dados de um empreendimento específico. [P]
**1 linha representa:** uma obra. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Obra | Texto/código | Sim | Sistema | Calculado (gerado) | Chave para todas as demais entidades | Formato do ID (sequencial, alfanumérico, por ano) não definido | [H] |
| Nome da Obra | Texto | Sim | Usuário | Digitado | — | Nome real e familiar, visível ao usuário | [P] |
| Cliente/Contratante | Texto | Sim | Usuário | Digitado | Não existe entidade "Cliente" modelada separadamente | Definir se "Cliente" (pessoa) vira entidade própria ou campo texto | [H] |
| Endereço | Texto | Não | Usuário | Digitado | — | — | [P] |
| Data de Início | Data | Sim | Usuário | Digitado | — | — | [P] |
| Data Prevista de Término | Data | Sim | Usuário | Digitado | — | — | [P] |
| Data Real de Término | Data | Não | Usuário | Digitado | Preenchido ao concluir | — | [P] |
| Status da Obra | Domínio | Sim | Sistema | Calculado | — | Lista fechada de status não homologada | [H] |
| Orçamento Inicial (Previsto) | Moeda | Sim | Calculado | Calculado | Soma de SERVIÇOS/ORÇAMENTO | Ver REG-003. Renomeado nesta revisão de "Orçamento Previsto Total" para alinhar com o vocabulário homologado em REG-017 (mesmo valor, nome mais claro) | [P] |
| Orçamento Vigente/Disponível | Moeda | Sim | Sistema | Calculado (Orçamento Inicial + Σ Aportes + Σ Alterações formais aprovadas) | Depende de FINANCEIRO (aportes, ver entidade abaixo) e ALTERAÇÕES (impacto aprovado) | **Campo novo desta revisão.** Fórmula homologada pelo responsável do projeto em 2026-09-16 (Opção B) — ver REG-017. É sempre derivado; não deve existir edição manual que sobrescreva este valor (regra explícita da decisão: não criar segunda fonte de verdade para o orçamento) | [D] |
| Responsável Técnico | Texto | Não | Usuário | Digitado | — | — | [P] |

**Relacionamentos:** 1 Obra → N Etapas; 1 Obra → N Fornecedores (via Compras); 1 Obra → N lançamentos Financeiro; 1 Obra → N Documentos. [P]

---

## ENTIDADE: ETAPAS

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3, DAD_001_V6_3 (versão anterior).
**Finalidade (proposta):** divisão macro do cronograma físico da obra (ex.: Fundação, Alvenaria, Instalações, Acabamento). [P]
**1 linha representa:** uma etapa dentro de uma obra. [P]
**Nomenclatura real de exemplo:** [D] AGENTS.md §11 — Alvenaria, Elétrica, Hidráulica, Fundação, Pintura, Acabamento.

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Etapa | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | Formato não definido | [H] |
| ID_Obra | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [P] |
| Nome da Etapa | Texto | Sim | Usuário | Digitado | — | Lista de nomes reais não é fechada (obra a obra pode variar) | [P] |
| Ordem/Sequência | Número | Sim | Usuário | Digitado | — | — | [P] |
| Peso da Etapa | Número/% | Não (agregado, não é campo primário) | Sistema | Calculado (Σ dos Pesos Automáticos **globais** — REG-008 — dos Serviços Elegíveis vinculados à Etapa via Subetapas) | Usado na exibição do progresso consolidado da Etapa (REG-020) | **Peso automático homologado em 2026-09-16 (REG-008/REG-020, detalhado na Revisão 5):** o peso de cada Serviço é sempre global (denominador = Σ Valor Orçado dos Serviços Elegíveis da Obra); "Peso da Etapa" é apenas a soma dos pesos globais dos Serviços que caem sob essa Etapa — **não é recalculado/renormalizado** dentro da Etapa | [D] |
| Data Início Prevista | Data | Sim | Usuário | Digitado | — | — | [P] |
| Data Fim Prevista | Data | Sim | Usuário | Digitado | — | — | [P] |
| Data Início Real | Data | Não | Usuário | Digitado | — | — | [P] |
| Data Fim Real | Data | Não | Usuário | Digitado | — | — | [P] |
| % Execução Física | % | Sim | Sistema | Calculado (consolidação ponderada dos Serviços da Etapa, via Subetapas, usando o Peso Automático **global** de cada Serviço — REG-008/REG-020) | Depende de SUBETAPAS/SERVIÇOS/EXECUÇÃO-MEDIÇÕES | **Modelo Híbrido homologado em 2026-09-16** (REG-007/REG-020/REG-022): usa o % de execução de cada Serviço (fórmula quantitativa ou tabela fechada de status, ambas [D] desde a Revisão 5) e o peso global de cada Serviço Elegível. Como os pesos são globais (não somam 100% dentro de uma única Etapa), **a fórmula técnica exata para exibir um percentual 0–100% isolado da Etapa permanece [H]** (REG-020) — nenhuma normalização foi inventada aqui | [D] (princípio da consolidação ponderada com pesos globais) / [H] (fórmula técnica de exibição do percentual isolado) |
| Status da Etapa | Domínio | Sim | Sistema | Calculado | — | Lista fechada não homologada | [H] |
| Orçamento Previsto da Etapa | Moeda | Sim | Calculado | Calculado | Soma de SERVIÇOS/ORÇAMENTO de todas as Subetapas da Etapa | Roteamento de soma ajustado nesta revisão: antes somava Serviços diretamente da Etapa; agora soma via Subetapas, conforme hierarquia oficial | [P] |

**Relacionamentos:** 1 Etapa → N Subetapas (relação oficial e obrigatória — hierarquia homologada em 2026-09-16, ver ENTIDADE: SUBETAPAS); 1 Etapa → N Planejamento (datas). **A partir desta revisão, Serviços/Orçamento não se vincula mais diretamente a Etapas — o vínculo passa a ser Etapa → Subetapa → Serviço (ver hierarquia oficial).** [D]

---

## ENTIDADE: SUBETAPAS — [D] HOMOLOGADO EM 2026-09-16

**Existência no escopo V1:** [D] — **CONFLITO ELIMINADO.** Decisão de arquitetura homologada pelo responsável pelo projeto em 2026-09-16: **SUBETAPAS é uma entidade própria do modelo de dados**, e não um campo textual de SERVIÇOS nem um nível implícito dentro de ETAPAS. Isso substitui e encerra o registro de conflito [C] da Revisão 1 ("SUBETAPAS: tabela própria, nível dentro de ETAPAS, ou nível dentro de SERVIÇOS/ORÇAMENTO?").

**Hierarquia oficial homologada:**
```
OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO
```

**Finalidade:** [D] — SUBETAPA representa uma unidade intermediária de organização da execução da obra, entre a Etapa (divisão macro) e o Serviço/Orçamento (item orçamentário específico). Decisão homologada, redação literal da regra 5 desta rodada.
**1 linha representa:** uma subetapa vinculada a uma etapa. [D]

**Princípio de simplicidade (regra 7/8 da decisão) — [D]:** a estrutura técnica (IDs de Subetapa) deve permanecer invisível ao usuário final sempre que possível; o operador trabalha com nomes reais. Exemplo oficial dado na decisão:
| Nível | Exemplo |
|---|---|
| Etapa | Alvenaria |
| Subetapa | Alvenaria interna |
| Serviço | Reboco |

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Subetapa | Texto/código | Sim | Sistema | Calculado | Chave própria da entidade | Formato do ID não definido por esta decisão (mesma lacuna geral de formato de ID já registrada para as demais entidades) | [H] |
| ID_Etapa | Texto/código | Sim | Sistema | Calculado | FK → ETAPAS (obrigatória, regra 2 da decisão) | Toda Subetapa deve estar vinculada a uma Etapa | [D] |
| Nome da Subetapa | Texto | Sim | Usuário | Digitado | — | Nome real e familiar (ver exemplo "Alvenaria interna") | [P] |
| Peso da Subetapa | Número/% | Não (agregado, não é campo primário) | Sistema | Calculado (Σ dos Pesos Automáticos **globais** — REG-008 — dos Serviços Elegíveis vinculados à Subetapa) | Usado na exibição do progresso consolidado da Subetapa (REG-020) | **Peso automático homologado em 2026-09-16 (Revisão 4), escopo global definido na Revisão 5 (REG-008/REG-020):** cada Serviço tem um único peso global (denominador = Σ Valor Orçado dos Serviços Elegíveis da Obra); "Peso da Subetapa" é apenas a soma desses pesos globais — não é recalculado/renormalizado dentro da Subetapa. Ajuste manual de peso é admitido como exceção e fica protegido (REG-023); campos técnicos de rastreabilidade permanecem [H] (ver ENTIDADE: SERVIÇOS/ORÇAMENTO) | [D] |
| % Execução | % | Sim | Sistema | Calculado (consolidação ponderada dos Serviços da Subetapa, usando o Peso Automático **global** de cada Serviço — REG-008/REG-020) | Depende de EXECUÇÃO/MEDIÇÕES e do Método de Execução (REG-007) dos Serviços da Subetapa | **Modelo Híbrido homologado em 2026-09-16** (REG-007/REG-020/REG-022) — % de execução por Serviço e pesos globais já definidos [D]; a fórmula técnica exata para exibir um percentual 0–100% isolado da Subetapa (dado que os pesos são globais) permanece [H] (REG-020) | [D] (princípio) / [H] (fórmula técnica de exibição do percentual isolado) |
| Status | Domínio | Sim | Sistema | Calculado | — | Lista fechada não homologada | [H] |

**Relacionamentos oficiais — [D]:**
- N Subetapas → 1 Etapa (obrigatório).
- 1 Subetapa → N Serviços/Orçamento (novo nesta revisão — ver ENTIDADE: SERVIÇOS/ORÇAMENTO).

**Consolidação futura de indicadores (regra 9 da decisão) — [D] (princípio, com fórmulas de peso e execução por Serviço já homologadas nas Revisões 4/5) / [H] (fórmulas específicas restantes):** a hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO foi desenhada para permitir consolidar indicadores de execução, planejamento, orçamento e dashboard em cada um dos 4 níveis (obra, etapa, subetapa, serviço). As fórmulas de peso automático (REG-008), método de execução (REG-007) e consolidação hierárquica com pesos globais (REG-020) já foram homologadas; permanecem [H] apenas os detalhes pontuais listados em cada regra (ver REG-007/REG-008/REG-020/REG-022 a REG-025) e a fórmula de REG-003 (orçamento).

---

## ENTIDADE: SERVIÇOS/ORÇAMENTO

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** item orçamentário/serviço específico vinculado a uma etapa/subetapa, com quantidade e valor. [P]
**1 linha representa:** um item de serviço ou insumo orçado. [P]
**Nomenclatura real de exemplo:** [D] AGENTS.md §11 — Cimento, Cal, Areia fina, Reboco, Chapisco, Assentamento de blocos.

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Servico | Texto/código | Sim | Sistema | Calculado | FK → SUBETAPAS | — | [H] |
| ID_Subetapa | Texto/código | Sim | Sistema | Calculado | FK → SUBETAPAS (obrigatória) | **Decisão homologada em 2026-09-16:** todo Serviço vincula-se a uma Subetapa — não mais diretamente a uma Etapa. Hierarquia oficial: OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO. O vínculo com a Etapa é obtido indiretamente via a Subetapa (ID_Etapa da Subetapa). | [D] |
| Descrição do Serviço | Texto | Sim | Usuário | Digitado | — | Nome real da construção civil | [P] |
| Unidade de Medida | Domínio | Sim | Usuário | Digitado | — | Lista (m², m³, kg, un., vb.) não homologada | [H] |
| Quantidade Orçada | Número | Sim | Usuário | Digitado | — | Usada como "Quantidade Planejada/Elegível" no denominador do Método Quantitativo (REG-007) quando o Método de Execução do Serviço for Quantitativo | [P] |
| Valor Unitário | Moeda | Sim | Usuário | Digitado | — | — | [P] |
| Valor Calculado | Moeda | Sim | Sistema | Calculado (Qtd × Valor Unit., REG-026) | — | **Renomeado de "Valor Total Orçado" na Etapa 3 (Revisão 6)** para alinhar com a terminologia homologada. Continua sendo a base do Peso Automático do Serviço (REG-008). NUNCA é sobrescrito por um Ajuste Manual (ver "Valor Previsto" abaixo) | [D] (fórmula, Etapa 3 Seção 36) |
| Valor Previsto (Ajuste Manual) | Moeda | Não | Usuário | Digitado | Substitui, quando preenchido, o Valor Calculado como Valor Previsto — apenas como exceção (REG-026) | **Homologado na Etapa 3 (Revisão 6):** não exige justificativa nem aprovação prévia. Campo novo desta revisão | [D] |
| Ajuste Manual (do Valor Previsto) | Booleano (SIM/NÃO) | Sim | Sistema | Calculado (Valor Previsto (Ajuste Manual) preenchido → SIM) | — | **Homologado na Etapa 3 (REG-026).** Distinto do "Peso Ajustado" (progresso físico, REG-008) — são dois ajustes manuais conceitualmente diferentes | [D] |
| Valor Previsto | Moeda | Sim | Sistema | Calculado (= Valor Calculado, salvo Ajuste Manual → usa o valor manual — REG-026) | Base do Orçamento Previsto consolidado (REG-003) | **Homologado na Etapa 3 (Revisão 6).** Campo novo; antes desta revisão não existia distinção entre "calculado" e "previsto" | [D] |
| Variação | Moeda | Não | Sistema | Calculado (Valor Previsto − Valor Calculado, REG-028) | — | **Homologado na Etapa 3.** Termo "Variação", nunca "Desvio" (reservado a REG-013/014/015). Variação percentual e formatação de alerta permanecem [H]/fora de escopo | [D] (variação absoluta) / [H] (percentual, alerta) |
| Fornecedor Previsto | Texto/FK | Não | Usuário | Digitado | FK → FORNECEDORES | — | [P] |
| Status | Domínio fechado | Sim | Usuário | Digitado | — | **Domínio fechado HOMOLOGADO na Etapa 3 (REG-027):** Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído. Distinto do campo "Status de Execução" abaixo (que trata do andamento físico, REG-007) — este "Status" trata do ciclo de vida/escopo do registro orçamentário, usado nos critérios de elegibilidade (REG-022) e de composição do orçamento corrente (REG-003/027) | [D] |
| Elegível para Cálculo Físico | Booleano | Sim | Sistema | Calculado (a partir de Status, vínculo com Subetapa, escopo vigente e Valor Calculado — REG-022) | Determina se o Serviço entra no denominador do Peso Automático (REG-008) e na consolidação (REG-020) | **Critérios de elegibilidade homologados em 2026-09-16 (REG-022):** representa execução física real; possui vínculo válido com Subetapa; pertence ao escopo vigente da Obra; está ativo para execução; possui Valor Calculado válido quando necessário para o peso. Excluídos: cancelados, fora de escopo, sem valor orçado válido quando aplicável. Serviços de ALTERAÇÕES aprovadas e incorporadas ao escopo vigente são elegíveis. **Atualização Etapa 3:** o domínio "Status" agora é fechado (REG-027) — "ativo para execução" mapeia para Status ∈ {Ativo, Concluído} (o mesmo critério usa REG-027 para excluir Cancelado/Retirado do Escopo/Substituído tanto do cálculo físico quanto do orçamento corrente). "Pertence ao escopo vigente" continua [H] (depende de ALTERAÇÕES, ainda não implementado) | [D] (critérios; e agora também o domínio fechado que operacionaliza "ativo") / [H] (escopo vigente via ALTERAÇÕES) |
| Método de Execução | Domínio (Quantitativo / Status) | Sim | Usuário | Digitado | — | **Modelo Híbrido homologado em 2026-09-16 (REG-007).** Define se o % Execução do Serviço é apurado por medição quantitativa (usa Quantidade Orçada e EXECUÇÃO/MEDIÇÕES) ou por status/conclusão (usa o campo "Status de Execução" abaixo). Não existe lista fechada de quais serviços usam cada método — atribuição caso a caso, não homologada em bloco. Quem atribui e em que momento do cadastro permanece [H] | [D] (existência do campo/dos dois métodos) / [H] (regra de atribuição) |
| Status de Execução | Domínio fechado (Pendente / Em andamento / Concluído) | Condicional (obrigatório quando Método de Execução = Status) | Usuário | Digitado | — | **Tabela fechada homologada em 2026-09-16 (REG-007, Revisão 5):** Pendente = 0%, Em andamento = 50%, Concluído = 100%. Enquanto esta decisão estiver vigente, não há percentuais adicionais nem percentual intermediário informado manualmente. Campo distinto do "Status" genérico acima | [D] |
| % Execução do Serviço | % | Sim | Sistema | Calculado — Método Quantitativo: Quantidade Executada / Quantidade Orçada (REG-007, fórmula homologada); Método Status: conforme tabela fechada do campo "Status de Execução" (REG-007) | Depende de EXECUÇÃO/MEDIÇÕES (Quantitativo) ou de "Status de Execução" (Status) | **Fórmulas homologadas em 2026-09-16 (REG-007, Revisão 5)** para os dois métodos. Permanecem [H]: arredondamento/tolerância, tratamento de execução acima de 100% (ver também REG-009) e tratamento de Quantidade Orçada = 0 | [D] (fórmula por método) / [H] (arredondamento, excedente, quantidade zero) |
| Peso Automático do Serviço | Número/% | Sim | Sistema | Calculado (Valor Calculado do Serviço / Σ Valor Calculado dos Serviços Elegíveis **da Obra**) | Usado em REG-020 (consolidação hierárquica) | **Fórmula homologada em 2026-09-16 (REG-008); escopo do denominador resolvido na Revisão 5.** Campo de referência renomeado de "Valor Total Orçado" para "Valor Calculado" na Revisão 6 (Etapa 3) — mesmo campo, mesma fórmula, sem reabrir REG-008: o denominador é sempre a soma de todos os Serviços Elegíveis da Obra inteira — **não é renormalizado** por Subetapa ou Etapa. Não exige preenchimento manual como regra normal | [D] |
| Peso Ajustado (manual) | Número/% | Não | Usuário | Digitado | Substitui, quando preenchido, o Peso Automático no cálculo — apenas como exceção; fica **protegido** contra alteração automática (REG-023) | Ajuste manual admitido como **exceção** (REG-008), não como padrão. **Homologado em 2026-09-16 (Revisão 5):** não exige obrigatoriamente justificativa nem aprovação prévia; o Peso Automático original não é substituído conceitualmente e deve continuar preservado ao lado do Peso Ajustado (ver campo abaixo). Nome/formato técnico definitivo do campo **não homologado** | [D] (exceção sem justificativa/aprovação obrigatória; proteção) / [H] (nome/formato técnico do campo) |
| Peso Automático Original (preservado) | Número/% | Condicional (preenchido quando houver Peso Ajustado) | Sistema | Calculado (cópia do Peso Automático no momento do ajuste manual) | — | **Preservação exigida pela decisão homologada em 2026-09-16 (Revisão 5, REG-008):** o sistema deve manter o valor do peso automático original mesmo após um ajuste manual, para rastreabilidade mínima. Nome/formato técnico definitivo do campo **não homologado** | [D] (obrigação de preservar o valor) / [H] (nome/formato técnico do campo) |
| Justificativa do Ajuste | Texto | Não — **dispensada como obrigatória pela decisão homologada em 2026-09-16 (Revisão 5)** | Usuário | Digitado | — | Campo continua disponível como opção de rastreabilidade, mas não é exigido; nome/formato técnico definitivo **não homologado** | [H] |
| Responsável pelo Ajuste | Texto/FK | Não definido — obrigatoriedade **não tratada** pela decisão (esta apenas dispensou justificativa e aprovação prévia) | Sistema | Calculado (usuário logado) | Depende do mecanismo de identificação (ver SEC_001) | Campo ainda **não homologado**; permanece [H] se deve ou não ser obrigatório | [H] |
| Data do Ajuste | Data | Não definido — obrigatoriedade **não tratada** pela decisão | Sistema | Calculado | — | Campo ainda **não homologado** | [H] |

**Relacionamentos:** N Serviços → 1 Subetapa (obrigatório, hierarquia oficial homologada — [D]); 1 Serviço → N registros em EXECUÇÃO/MEDIÇÕES; 1 Serviço → N COMPRAS. [D] (vínculo com Subetapa) / [P] (demais vínculos)

**[D] HOMOLOGADO EM 2026-09-16 — Modelo Híbrido de Progresso Físico, consolidado nas Revisões 4 e 5 (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-007/REG-008/REG-020/REG-022 a REG-025):**
- O % de execução de cada Serviço é apurado por medição quantitativa (Quantidade Executada / Quantidade Orçada) **ou** por status/conclusão (tabela fechada Pendente=0%/Em andamento=50%/Concluído=100%), conforme o Método de Execução atribuído. Não foi criada lista fechada de quais serviços usam qual método.
- O peso de cada Serviço é calculado **automaticamente** e é sempre **global** — Valor Calculado do Serviço / Σ Valor Calculado dos Serviços Elegíveis **da Obra inteira** — nunca renormalizado por Subetapa/Etapa. (Campo renomeado de "Valor Total Orçado" para "Valor Calculado" na Revisão 6 — mesmo campo, sem reabrir REG-008.)
- Um Serviço só entra nesse cálculo se for **Elegível** (REG-022): representa execução física real, vinculado a Subetapa, no escopo vigente, ativo, com valor orçado válido quando necessário.
- O ajuste manual de peso é admitido como **exceção**, sem exigir obrigatoriamente justificativa ou aprovação prévia; o peso manual fica **protegido** e não é alterado automaticamente (REG-023); o sistema deve preservar o peso automático original ao lado do peso ajustado.
- Quando há mistura de pesos manuais (protegidos) e automáticos, a diferença para fechar 100% é redistribuída **proporcionalmente apenas entre os automáticos** (REG-024); se **todos** os Serviços Elegíveis estiverem com peso manual e a soma deixar de fechar 100%, o sistema **bloqueia** o ajuste em vez de redistribuir (REG-025).
- Os campos técnicos definitivos de rastreabilidade do ajuste (nomes/formatos, obrigatoriedade de responsável/data) **permanecem [H]** — não foram homologados nesta rodada.

---

## ENTIDADE: PLANEJAMENTO

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Nota terminológica [P]:** este documento trata "Planejamento" como o **módulo de dados** (datas previstas/reais por etapa). A tela de interface correspondente passa a se chamar **"Cronograma da Obra"** (ver Seção 6 do `PLANO_FECHAMENTO_ESPECIFICACAO_V1` e `UI_001`), para não colidir com "Cronograma de Execução do Projeto" (pasta `16_CRONOGRAMA_E_EXECUCAO`, que trata do prazo do próprio desenvolvimento do sistema).

**Finalidade (proposta):** cronograma de datas planejadas por etapa/subetapa/serviço. [P]
**1 linha representa:** um item de planejamento (data prevista) vinculado a uma etapa ou subetapa. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Planejamento | Texto/código | Sim | Sistema | Calculado | FK → ETAPAS/SUBETAPAS | — | [H] |
| Data Início Prevista | Data | Sim | Usuário | Digitado | — | — | [P] |
| Data Fim Prevista | Data | Sim | Usuário | Digitado | — | — | [P] |
| Duração Prevista (dias) | Número | Sim | Sistema | Calculado | — | — | [P] |
| Dependência (predecessora) | FK | Não | Usuário | Digitado | Autorreferência a outra Etapa/Subetapa | Lógica de encadeamento (tipo Gantt) não definida | [H] |
| Status do Prazo | Domínio | Sim | Sistema | Calculado | — | Threshold de atraso não definido (ver REG-014) | [H] |

---

## ENTIDADE: FORNECEDORES

**Existência no escopo V1:** [D] — AGENTS.md §12 (módulo auxiliar), MOD_001_V6_3.
**Finalidade (proposta):** cadastro de fornecedores e prestadores de serviço. [P]
**1 linha representa:** um fornecedor. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Fornecedor | Texto/código | Sim | Sistema | Calculado | FK ← COMPRAS, SERVIÇOS/ORÇAMENTO | — | [H] |
| Nome/Razão Social | Texto | Sim | Usuário | Digitado | — | — | [P] |
| CNPJ/CPF | Texto | Não | Usuário | Digitado | — | — | [P] |
| Contato | Texto | Não | Usuário | Digitado | — | — | [P] |
| Categoria de Fornecimento | Domínio | Não | Usuário | Digitado | — | Lista não homologada (material, mão de obra, serviço) | [H] |
| Avaliação/Histórico | Texto/Número | Não | Sistema | Calculado | — | AGENTS.md §14 cita "comportamento de fornecedores" como insight, mas não define métrica | [H] |
| Status | Domínio | Sim | Sistema | Calculado | — | Ativo/Inativo — não homologado formalmente | [H] |

---

## ENTIDADE: COMPRAS

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** registro de pedidos/compras de materiais e serviços junto a fornecedores. [P]
**1 linha representa:** uma compra/pedido. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Compra | Texto/código | Sim | Sistema | Calculado | FK → OBRAS, FORNECEDORES, SERVIÇOS/ORÇAMENTO | — | [H] |
| Data da Compra | Data | Sim | Usuário | Digitado | — | — | [P] |
| Valor | Moeda | Sim | Usuário | Digitado | — | — | [P] |
| Forma de Pagamento | Domínio | Não | Usuário | Digitado | — | Não definido | [H] |
| Status de Aprovação | Domínio | Sim | Sistema | Calculado | — | **Fluxo de aprovação não definido em nenhuma fonte** | [H] |
| Status de Entrega | Domínio | Não | Usuário | Digitado | — | Não homologado | [H] |

---

## ENTIDADE: FINANCEIRO

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3, REG_001_V6_3 (cita Orçamento Previsto, Custo Realizado, Saldo Atual).
**Finalidade (proposta):** lançamentos financeiros da obra (entradas e saídas). [P]
**1 linha representa:** um lançamento financeiro. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Lancamento | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [H] |
| Tipo (Aporte/Despesa) | Domínio | Sim | Usuário | Digitado | — | **Ver decisão homologada abaixo.** Aporte = entrada de recurso que incrementa o Orçamento Vigente/Disponível da Obra (REG-006/REG-017); não é despesa/custo executado/medição. Lista completa de valores do domínio (se existem tipos além de Aporte/Despesa) segue não homologada. | [P] |
| Data | Data | Sim | Usuário | Digitado | — | — | [P] |
| Valor | Moeda | Sim | Usuário | Digitado | Para lançamentos do tipo Aporte, este valor alimenta o cálculo de Orçamento Vigente/Disponível em OBRAS (REG-017) | — | [P] |
| Categoria | Domínio | Não | Usuário | Digitado | — | Lista não homologada | [H] |
| Origem/Destino | Texto | Não | Usuário | Digitado | Pode referenciar FORNECEDORES ou Cliente | Para Aportes, registra a origem do recurso (ex.: cliente) | [P] |
| Status de Pagamento | Domínio | Não | Usuário | Digitado | — | Não homologado | [H] |
| Saldo Resultante | Moeda | Sim | Sistema | Calculado | — | Campo mantido em aberto: não representa o Saldo Orçamentário (que é calculado no nível da Obra — REG-005/REG-017) nem tem fórmula própria definida. Se este campo permanecer no modelo, ele se aproxima do conceito de **Saldo de Caixa (REG-018)**, cuja fórmula **não foi definida** pela decisão homologada. | [H] |

**[D] CONFLITO RESOLVIDO EM 2026-09-16 — decisão homologada pelo responsável pelo projeto (Opção B — Vincular Aporte ao Orçamento):**
- Todo aporte financeiro destinado à obra é registrado individualmente aqui, em FINANCEIRO, com seus campos (valor, data, origem).
- O aporte **aumenta o Orçamento Vigente/Disponível** da Obra (campo novo em OBRAS, ver acima) — não é tratado como despesa, custo executado ou medição.
- O consumo do orçamento continua determinado pelo Custo Realizado (REG-004), não pelos aportes.
- O Orçamento Vigente é sempre **derivado** de Orçamento Inicial + Aportes + Alterações formais aprovadas — não existe (nem deve ser criado) um campo de orçamento editável manualmente que sirva de segunda fonte de verdade.
- Ver fórmula completa em `05_REGRAS_DE_NEGOCIO/REG_001` REG-017, e a regra de vínculo em REG-006.
- **O que permanece [H], não resolvido por esta decisão:** a fórmula do **Saldo de Caixa** (REG-018) — conceito que a própria decisão homologada exige manter distinto do Saldo Orçamentário, mas cuja fórmula não foi definida nem inventada aqui.

**[D] HOMOLOGADO EM 2026-09-16 — Separação entre Aporte Financeiro e Peso Físico (REG-021, sem reabrir a decisão acima):**
- A decisão de Aporte × Orçamento (Opção B, acima) permanece integralmente válida: o aporte aumenta o Orçamento Vigente/Disponível da Obra.
- Porém, **aporte financeiro não aumenta automaticamente o peso físico da obra** (ver ENTIDADE: SERVIÇOS/ORÇAMENTO, "Peso Automático do Serviço", e REG-008/REG-020/REG-021). Um aporte só influencia a composição do progresso físico se estiver efetivamente associado a um Serviço executável que integre a base elegível do cálculo físico.
- O Orçamento Vigente/Disponível **não deve ser usado diretamente como denominador do peso físico** quando existirem valores de aporte sem Serviço executável correspondente.
- **Separação conceitual obrigatória** entre: Orçamento Vigente/Disponível (REG-017); recurso financeiro/aporte (REG-006); Custo Realizado (REG-004); progresso físico (REG-007/REG-020); peso físico (REG-008). Valor financeiro disponível não é convertido automaticamente em percentual físico.
- **O que permanece [H]:** o mecanismo exato de vínculo entre um Aporte e um Serviço executável (obrigatoriedade, forma de registro) — não definido nem inventado nesta decisão.

---

## ENTIDADE: EXECUÇÃO/MEDIÇÕES

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** registro periódico do avanço físico executado por etapa/subetapa/serviço. [P]
**1 linha representa:** uma medição registrada em uma data. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Medicao | Texto/código | Sim | Sistema | Calculado | FK → ETAPAS/SUBETAPAS/SERVIÇOS | — | [H] |
| Data da Medição | Data | Sim | Usuário | Digitado | — | Periodicidade (semanal/por marco) não definida | [H] |
| Quantidade/% Executado | Número/% | Sim | Usuário | Digitado | — | — | [P] |
| Responsável pela Medição | Texto | Não | Usuário | Digitado | — | — | [P] |
| Evidência (foto/documento) | FK | Não | Usuário | Digitado | FK → DOCUMENTOS | — | [P] |
| Status | Domínio | Sim | Sistema | Calculado | — | Não homologado | [H] |

---

## ENTIDADE: ALTERAÇÕES

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** registro de mudanças de escopo, orçamento ou prazo em relação ao planejado original. [P]
**1 linha representa:** uma alteração. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Alteracao | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [H] |
| Tipo de Alteração | Domínio | Sim | Usuário | Digitado | — | Lista (Escopo/Prazo/Orçamento) proposta, não homologada | [H] |
| Descrição | Texto | Sim | Usuário | Digitado | — | — | [P] |
| Impacto no Orçamento | Moeda | Não | Sistema | Calculado | — | — | [P] |
| Impacto no Prazo | Número (dias) | Não | Sistema | Calculado | — | — | [P] |
| Status de Aprovação | Domínio | Sim | Sistema | Calculado | — | **Fluxo de aprovação não definido** | [H] |
| Solicitante | Texto | Não | Usuário | Digitado | — | — | [P] |
| Data | Data | Sim | Usuário | Digitado | — | — | [P] |

---

## ENTIDADE: PENDÊNCIAS

**Existência no escopo V1:** [D] — AGENTS.md §12, MOD_001_V6_3.
**Finalidade (proposta):** registro de itens em aberto que requerem ação ou decisão. [P]
**1 linha representa:** uma pendência. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Pendencia | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [H] |
| Descrição | Texto | Sim | Usuário | Digitado | — | — | [P] |
| Responsável | Texto | Não | Usuário | Digitado | — | — | [P] |
| Data de Abertura | Data | Sim | Usuário | Digitado | — | — | [P] |
| Prazo (SLA) | Data/Número | Não | Usuário | Digitado | — | **SLA não homologado** | [H] |
| Status | Domínio | Sim | Sistema | Calculado | — | Lista fechada não homologada | [H] |
| Prioridade | Domínio | Não | Usuário | Digitado | — | Critério de priorização não definido | [H] |
| Vínculo | FK | Não | Sistema | Calculado | FK opcional → ETAPAS/COMPRAS/FINANCEIRO | — | [P] |

---

## ENTIDADE: ATUALIZAÇÕES

**Existência no escopo V1:** [D] — AGENTS.md §12 (módulo auxiliar), MOD_001_V6_3.
**Finalidade (proposta):** registro de comunicações/avisos gerais da obra, direcionados inclusive ao Cliente. [P]
**1 linha representa:** uma atualização/comunicado. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Atualizacao | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [H] |
| Data | Data | Sim | Usuário | Digitado | — | — | [P] |
| Autor | Texto | Sim | Sistema | Calculado (usuário logado) | — | Depende do mecanismo de identificação (ver SEC_001) | [H] |
| Texto/Descrição | Texto | Sim | Usuário | Digitado | — | — | [P] |
| Anexo | FK | Não | Usuário | Digitado | FK → DOCUMENTOS | — | [P] |
| Visível para Cliente | Booleano | Sim | Usuário | Digitado | — | Regra de visibilidade por perfil no nível de registro não definida | [H] |

**Observação [H]:** há sobreposição conceitual entre ATUALIZAÇÕES, PENDÊNCIAS e EXECUÇÃO/MEDIÇÕES (todas podem registrar "o que aconteceu na obra"). A fronteira entre os três não está definida em nenhuma fonte — precisa de homologação para evitar duplicidade de lançamento.

---

## ENTIDADE: DOCUMENTOS

**Existência no escopo V1:** [D] — AGENTS.md §12 cita "Documentos/Fotos" como módulo auxiliar.
**Finalidade (proposta):** repositório de arquivos e fotos vinculados à obra. [P]
**1 linha representa:** um documento/arquivo. [P]

| Campo | Tipo | Obrigatório | Origem | Calc./Digitado | Relacionamento | Observação | Status |
|---|---|---|---|---|---|---|---|
| ID_Documento | Texto/código | Sim | Sistema | Calculado | FK → OBRAS | — | [H] |
| Vínculo | FK | Não | Sistema | Calculado | FK opcional → ETAPAS/MEDIÇÕES/COMPRAS/ALTERAÇÕES | — | [P] |
| Tipo de Arquivo | Domínio | Não | Sistema | Calculado | — | — | [P] |
| Data de Upload | Data | Sim | Sistema | Calculado | — | — | [P] |
| Descrição | Texto | Não | Usuário | Digitado | — | — | [P] |
| Caminho/Link do Arquivo | Texto | Sim | Sistema | Calculado | — | **Mecanismo de armazenamento não definido** — Excel não é um bom repositório de binários; local vs. nuvem (Google Drive/OneDrive) não decidido | [H] |

---

## Domínios pendentes de homologação (consolidado)

Nenhum destes domínios (listas fechadas de valores) foi inventado; todos precisam de decisão do responsável antes da construção:

- Status da Obra
- Status da Etapa / Subetapa
- Unidade de Medida (lista fechada)
- Categoria de Fornecedor
- Forma de Pagamento
- Status de Aprovação de Compra
- Tipo de Alteração
- Status de Aprovação de Alteração
- Status/Prioridade de Pendência
- Status do Prazo (Planejamento)
- Lista fechada de quais Serviços usam o método Quantitativo e quais usam o método Status — REG-007
- Regra de atribuição do Método de Execução por Serviço (quem atribui, quando) — REG-007
- Arredondamento e tolerância do Método Quantitativo; tratamento de execução acima de 100%; tratamento de Quantidade Orçada = 0 — REG-007/REG-009
- Domínios fechados que operacionalizam os critérios de elegibilidade de Serviço (ex.: valores de "Status" que configuram "ativo para execução") — REG-022
- Campos técnicos definitivos de rastreabilidade do Ajuste Manual de Peso (nomes/formatos; obrigatoriedade de Responsável e Data — a decisão de 2026-09-16 dispensou apenas Justificativa e aprovação prévia) — REG-008
- Fórmula técnica exata da redistribuição proporcional entre Serviços com peso automático — REG-024
- Fórmula técnica de exibição de um percentual de execução isolado por Subetapa/Etapa, dado que os pesos dos Serviços são globais (não somam 100% dentro de cada nível) — REG-020
- Restrição de perfil (quem pode fazer) para o Ajuste Manual de Peso — REG-008
- Mecanismo de vínculo entre um Aporte e um Serviço executável elegível — REG-021
- Fluxo de transição entre valores de Status do Serviço/Orçamento (quem pode marcar Substituído, vínculo obrigatório com o substituto) — REG-027
- Regra de arredondamento de exibição do Valor Previsto/Variação além do formato de moeda padrão — REG-026/REG-028
- Variação percentual e formatação de alerta sobre a Variação do Orçamento — REG-028 (fora de escopo, ver REG-013/014/015)

**Resolvido nesta rodada (Revisão 5), não mais pendente:** fórmula de conversão de status em percentual do Método por Status (Pendente/Em andamento/Concluído = 0%/50%/100%, REG-007); escopo do denominador do Peso Automático — sempre global, sobre toda a Obra, nunca renormalizado por nível (REG-008/REG-020).

**Resolvido nesta rodada (Revisão 6), não mais pendente:** Status do Serviço/Orçamento — domínio fechado Ativo/Concluído/Cancelado/Retirado do Escopo/Substituído (REG-027); fórmula de Valor Previsto/Valor Calculado/Ajuste Manual (REG-026); fórmula da Variação absoluta (REG-028); fórmula de consolidação do Orçamento Previsto por Subetapa/Etapa/Obra usando o Valor Previsto (REG-003).

## Relacionamentos gerais — [D] (hierarquia OBRAS→ETAPAS→SUBETAPAS→SERVIÇOS, homologada em 2026-09-16) / [P] (demais vínculos)

```
OBRAS (1) ──< ETAPAS (1) ──< SUBETAPAS (1) ──< SERVIÇOS/ORÇAMENTO   [hierarquia oficial homologada]
SERVIÇOS/ORÇAMENTO (1) ──< EXECUÇÃO/MEDIÇÕES
ETAPAS/SUBETAPAS (1) ──< PLANEJAMENTO   [granularidade não definida pela decisão — permanece [H]]
OBRAS (1) ──< COMPRAS (N) >── FORNECEDORES (1)
SERVIÇOS/ORÇAMENTO (1) ──< COMPRAS
OBRAS (1) ──< FINANCEIRO
OBRAS (1) ──< ALTERAÇÕES
OBRAS (1) ──< PENDÊNCIAS
OBRAS (1) ──< ATUALIZAÇÕES
OBRAS (1) ──< DOCUMENTOS
```

## Regra sobre IDs — [H]

Nenhuma fonte define o formato de ID técnico (sequencial numérico, código alfanumérico por obra, UUID). AGENTS.md §11 apenas estabelece o princípio de que IDs técnicos podem existir mas não devem dominar a experiência do usuário. **Formato de ID: [H] HOMOLOGAR.**

## Registro de homologação — Revisão 4

Em 2026-09-16, o responsável pelo projeto homologou o **MODELO HÍBRIDO de cálculo do progresso físico** (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-007/REG-008/REG-020/REG-021), refletido nas entidades:
- **ETAPAS** e **SUBETAPAS** — campos "Peso da Etapa"/"Peso da Subetapa" passam de [H] para [D] (peso automático a partir do valor orçado); "% Execução Física"/"% Execução" passam a refletir a consolidação hierárquica ponderada.
- **SERVIÇOS/ORÇAMENTO** — novos campos: Método de Execução (Quantitativo/Status) [D]; % Execução do Serviço [D] (princípio) / [H] (fórmula de conversão de status); Peso Automático do Serviço [D]; e, como proposta de estrutura ainda **não homologada** [H], Peso Ajustado (manual), Justificativa do Ajuste, Responsável pelo Ajuste e Data do Ajuste.
- **FINANCEIRO** — nota de separação entre Aporte Financeiro e Peso Físico, sem reabrir a decisão Opção B (REG-006/REG-017) já homologada.

**Preservado, não reaberto:** Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO. Nenhuma lista fechada de serviços por método, campo definitivo de rastreabilidade do ajuste manual, ou escopo de recálculo do denominador do peso por nível foi inventado — todos permanecem **[H] HOMOLOGAR**.

## Registro de homologação — Revisão 5

Em 2026-09-16, o responsável pelo projeto homologou a **consolidação completa do motor de progresso físico** (ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-007/REG-008/REG-020/REG-022 a REG-025), refletida nas entidades:
- **SERVIÇOS/ORÇAMENTO** — campos "% Execução do Serviço" e "Peso Automático do Serviço" passam de parcialmente [H] para [D] (fórmulas dos dois métodos de execução e escopo global do peso resolvidos); novos campos "Status de Execução" (domínio fechado Pendente/Em andamento/Concluído = 0%/50%/100%) [D] e "Elegível para Cálculo Físico" [D] (critérios) / [H] (domínios que os operacionalizam); campo "Peso Automático Original (preservado)" [D] adicionado para atender à exigência de preservação; "Justificativa do Ajuste" passa a [H]/não obrigatória (antes condicional); "Responsável pelo Ajuste" e "Data do Ajuste" permanecem [H] quanto à obrigatoriedade.
- **ETAPAS** e **SUBETAPAS** — campos "Peso da Etapa"/"Peso da Subetapa" passam de [D]/[H] misto para [D] pleno, redefinidos como soma de pesos globais (não recalculados por nível); campos "% Execução Física"/"% Execução" mantêm [D] no princípio da consolidação ponderada e ficam [H] apenas quanto à fórmula técnica de exibição de um percentual isolado por nível (pesos globais não somam 100% dentro de uma única Etapa/Subetapa).

**Preservado, não reaberto:** Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO; peso automático baseado no valor orçado; separação entre orçamento financeiro e progresso físico. **Permanecem [H], não inventados nesta rodada:** lista fechada de serviços por método; regras de arredondamento/tolerância/excedente/quantidade zero; domínios fechados de elegibilidade; campos técnicos definitivos de rastreabilidade do ajuste manual (nomes/formatos; obrigatoriedade de responsável/data); fórmula técnica exata da redistribuição proporcional; fórmula de exibição do percentual isolado por Subetapa/Etapa; restrição de perfil para ajuste manual; mecanismo de vínculo Aporte↔Serviço.

## Registro de homologação — Revisão 6

Em 2026-09-16, o responsável pelo projeto homologou o módulo/base de **ORÇAMENTO** (Etapa 3 de construção; ver `05_REGRAS_DE_NEGOCIO/REG_001`, REG-003/REG-026/REG-027/REG-028), refletido na entidade **SERVIÇOS/ORÇAMENTO**:
- **"Valor Total Orçado" renomeado para "Valor Calculado"** — mesma fórmula (Qtd × Valor Unitário), sem reabrir REG-008 (referências de peso físico atualizadas para o novo nome do mesmo campo).
- **Novos campos [D]:** "Valor Previsto (Ajuste Manual)" (entrada opcional do Operador), "Ajuste Manual" (indicador SIM/NÃO calculado), "Valor Previsto" (= Valor Calculado, salvo Ajuste Manual) e "Variação" (= Valor Previsto − Valor Calculado, variação absoluta apenas).
- **"Status" passa de [H] para [D]** — domínio fechado Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído (REG-027); Cancelado/Retirado do Escopo/Substituído deixam de compor o orçamento corrente (REG-003), sem que o registro seja apagado.
- **"Elegível para Cálculo Físico"** — atualizado para refletir que o domínio "Status" agora é fechado; o critério "ativo para execução" mapeia diretamente para Status ∈ {Ativo, Concluído}.

**Preservado, não reaberto:** Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO; Modelo Híbrido de progresso físico e peso automático (Revisões 4/5); separação entre orçamento financeiro e progresso físico. Conforme a Seção 36 da homologação da Etapa 3, apenas a decisão do Valor Previsto (Opção C) foi tratada como explicitamente HOMOLOGADA — Status do Serviço e Variação são registrados como [D] por serem aplicações diretas de listas/fórmulas já fornecidas na própria homologação (Seções 13/18), não interpretações do agente. **Permanecem [H]/fora de escopo, não inventados nesta rodada:** Orçamento Vigente completo (REG-017); Custo Realizado, Pagamentos, Saldo de Caixa; módulo Alterações; variação percentual e alertas de desvio (REG-013/014/015); fluxo de transição entre status do Serviço; regra de arredondamento de exibição além do formato de moeda; mecanismo de proteção do Excel (SEC_001).
