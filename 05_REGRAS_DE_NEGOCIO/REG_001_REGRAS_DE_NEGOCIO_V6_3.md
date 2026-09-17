# Regras de Negócio — V6.3 (Revisão 6 — Orçamento dos Serviços)

**Data da revisão:** 2026-09-16
**Motivo da Revisão 1:** `AUDITORIA_PRE_CONSTRUCAO_V1` identificou que nenhuma regra tinha threshold, fórmula ou fluxo documentado além do nome do tema. A Revisão 1 substituiu a versão anterior (3 linhas) por regras formalizadas com ID.
**Motivo da Revisão 2:** o responsável pelo projeto homologou a **Opção B — Vincular Aporte ao Orçamento**, resolvendo o conflito [C] registrado em REG-006 (Revisão 1) entre "Saldo Orçamentário" e "Aportes". REG-005 foi ajustada para usar o novo conceito de Orçamento Vigente/Disponível (REG-017), e REG-006 passou a documentar a regra de vínculo já resolvida.
**Motivo da Revisão 3:** o responsável pelo projeto homologou **SUBETAPAS como entidade própria**, com hierarquia oficial **OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO** (ver `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001`). Esta revisão ajusta a redação de REG-007 (referências a "Subetapa/Serviço" tornam-se explícitas quanto à hierarquia) e adiciona REG-019, que registra a hierarquia como regra de integridade referencial. **Nenhuma fórmula de peso ou de % de execução foi definida ou alterada** — REG-007 e REG-008 continuam [H], conforme instrução explícita de não inventar regras adicionais.
**Motivo da Revisão 4:** o responsável pelo projeto homologou o **MODELO HÍBRIDO de cálculo do progresso físico**: (a) o % de execução de cada Serviço pode ser apurado por medição quantitativa ou por status/conclusão, conforme a natureza do serviço; (b) o peso de cada Serviço na consolidação é calculado **automaticamente** a partir do seu Valor Orçado; (c) a consolidação segue a hierarquia SERVIÇO → SUBETAPA → ETAPA → OBRA usando esses pesos automáticos; (d) o ajuste manual de peso é admitido apenas como exceção, com rastreabilidade; (e) aporte financeiro **não** altera automaticamente o peso físico. Esta revisão reescreve REG-007 e REG-008 (antes [H]) e adiciona REG-020 e REG-021. Não foram criados thresholds, domínios fechados ou regras de exceção além do explicitamente decidido — o que não foi decidido permanece [H].
**Motivo da Revisão 5:** o responsável pelo projeto homologou a **consolidação completa do motor de progresso físico**, detalhando pontos que a Revisão 4 havia deixado em [H]: (a) fórmula do método quantitativo (Quantidade Executada / Quantidade Planejada/Elegível); (b) tabela fechada do método por status (Pendente = 0%, Em andamento = 50%, Concluído = 100%, sem percentuais adicionais nem intermediário manual); (c) o peso automático é sempre **global**, calculado sobre o total de Serviços Elegíveis da Obra, e **não é renormalizado** por Subetapa/Etapa — os pesos globais são apenas somados por agrupamento na consolidação; (d) critérios de elegibilidade de Serviço para o cálculo físico; (e) ajuste manual de peso não exige obrigatoriamente justificativa nem aprovação prévia, mas o sistema deve preservar o peso automático original e o peso ajustado utilizado; (f) peso manual fica protegido — não sofre redistribuição automática; (g) quando parte dos serviços tem peso automático, a diferença necessária para fechar 100% é redistribuída proporcionalmente somente entre eles; (h) se todos os Serviços Elegíveis estiverem com peso manual e a soma deixar de fechar 100%, o sistema bloqueia o ajuste em vez de redistribuir. Esta revisão detalha REG-007 e REG-008, resolve o item [H] de escopo do denominador em REG-020, e adiciona REG-022 (Serviços Elegíveis), REG-023 (Proteção do Peso Manual), REG-024 (Redistribuição Proporcional) e REG-025 (Bloqueio quando Todos os Pesos são Manuais). Nenhuma decisão anterior foi reaberta; o que não foi explicitamente decidido nesta rodada (arredondamento, tolerância, tratamento de excedente, quantidade planejada zero, lista fechada de serviços por método, campos técnicos definitivos de rastreabilidade, fórmula técnica exata da redistribuição, fluxo de vínculo Aporte↔Serviço) permanece [H].
**Motivo da Revisão 6:** o responsável pelo projeto homologou o módulo/base de **ORÇAMENTO** ("Etapa 3" de construção): (a) Valor Previsto = Quantidade × Valor Unitário (Opção C) como padrão, com possibilidade de Ajuste Manual pelo Operador, preservando sempre o Valor Calculado; (b) Variação do Orçamento = Valor Previsto − Valor Calculado (termo "Variação", nunca "Desvio"); (c) domínio fechado do Status do Serviço/Orçamento (Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído); (d) Serviços Cancelados/Retirados do Escopo/Substituídos não compõem os totais do orçamento corrente, mas continuam existindo na base (nenhum registro é apagado); (e) consolidação do Orçamento Previsto pela hierarquia Serviço → Subetapa → Etapa → Obra, usando o Valor Previsto (REG-003 atualizada). Esta revisão reescreve REG-003 e adiciona REG-026 (Valor Previsto do Serviço), REG-027 (Status do Serviço/Orçamento) e REG-028 (Variação do Orçamento). Conforme instrução explícita da Seção 36 da homologação, **apenas a decisão do Valor Previsto (Opção C) foi tratada como HOMOLOGADA por esta rodada** — as demais decisões registradas aqui (Status do Serviço, Variação) são aplicações diretas de listas/fórmulas fornecidas explicitamente na própria homologação, não invenções; nada além disso foi promovido de [P]/[H] para [D]. Não implementados nesta revisão (permanecem para etapas futuras): Aportes, Alterações Aprovadas, Custo Realizado, Pagamentos, Saldo de Caixa, Orçamento Vigente completo (REG-017), alertas de desvio (REG-013/014/015), variação percentual.

## Legenda de status

[D] DOCUMENTADO — vem literalmente de fonte já homologada · [P] PROPOSTA — sugestão de regra ainda não homologada · [H] HOMOLOGAR — decisão/threshold em aberto, não definido em nenhuma fonte · [C] CONFLITO — duas fontes/conceitos não conciliados.

**Nenhum threshold numérico foi inventado.** Onde a fonte não define um limite, o campo "Resultado" registra a lacuna e o status é [H].

---

### REG-001 — Identificador único de registro
- **Descrição:** todo registro de qualquer entidade deve possuir um identificador técnico único e estável.
- **Entrada:** criação de um novo registro em qualquer entidade do DAD_001.
- **Condição:** registro novo, sem ID atribuído.
- **Resultado:** sistema gera um ID único. **Formato do ID não definido** (ver DAD_001, seção "Regra sobre IDs").
- **Status:** [H]
- **Teste necessário:** teste unitário de geração de ID (unicidade, não repetição, formato) — só pode ser escrito após homologação do formato.

### REG-002 — Integridade referencial
- **Descrição:** um registro não pode ser excluído se houver registros dependentes vinculados a ele (ex.: uma Obra com Etapas lançadas).
- **Entrada:** tentativa de exclusão de um registro pai.
- **Condição:** existência de registros filhos vinculados (FK ativa).
- **Resultado:** exclusão deve ser bloqueada ou o tratamento em cascata deve ser definido. **Qual dos dois comportamentos (bloqueio vs. exclusão em cascata) não está definido.**
- **Status:** [H]
- **Teste necessário:** teste de integração — tentar excluir uma Obra/Etapa com dependentes e verificar o comportamento homologado.
- **Ver também:** REG-019, caso específico desta regra aplicado à hierarquia Etapa → Subetapa → Serviço.

### REG-003 — Orçamento Previsto Total (Orçamento Inicial) — [D] HOMOLOGADO EM 2026-09-16 (Revisão 6)
- **Descrição:** o Orçamento Previsto (também chamado de Orçamento Inicial a partir da Revisão 2, ver REG-017) de uma Obra/Etapa é a soma dos **Valores Previstos** (REG-026) dos Serviços/Orçamento elegíveis vinculados — não a soma do Valor Calculado isoladamente, porque um Serviço pode ter Ajuste Manual (REG-026). É o ponto de partida do Orçamento Vigente/Disponível (REG-017) — não é substituído por ele, apenas deixa de ser, sozinho, o termo de comparação do Saldo Orçamentário (REG-005).
- **Entrada:** Valor Previsto (REG-026) de cada Serviço elegível (REG-022, critério físico; reaproveitado aqui como critério de elegibilidade orçamentária — Etapa 3, Seção 19) vinculado à Subetapa/Etapa/Obra.
- **Condição:** soma de todos os registros de SERVIÇOS/ORÇAMENTO elegíveis com o mesmo ID_Subetapa/ID_Etapa/ID_Obra, subindo pela hierarquia oficial (REG-019).
- **Resultado (fórmula homologada na Etapa 3, Seção 36):** Orçamento Previsto (de uma Subetapa/Etapa/Obra) = Σ(Valor Previsto dos Serviços elegíveis vinculados).
- **O que esta decisão NÃO define (permanece [H]):** thresholds de alerta (REG-013), fórmula de variação percentual (ver REG-028), critérios adicionais de elegibilidade orçamentária além dos já usados no cálculo físico (REG-022).
- **Status:** [D] — fórmula homologada para esta implementação na Etapa 3 (Seção 36), substituindo a proposta [P] anterior (que somava apenas o Valor Total Orçado, sem contemplar Ajuste Manual nem exclusão de Serviços Cancelados/Retirados do Escopo/Substituídos).
- **Teste necessário:** teste unitário de soma por Subetapa/Etapa/Obra; teste de regressão ao adicionar/remover serviço; teste de que um Serviço cancelado não entra na soma (ver REG-027).

### REG-004 — Custo Realizado
- **Descrição:** o Custo Realizado de uma Obra/Etapa é a soma dos lançamentos financeiros do tipo despesa vinculados a ela.
- **Entrada:** lançamentos de FINANCEIRO do tipo "Despesa" vinculados à Obra/Etapa.
- **Condição:** soma de todos os lançamentos de despesa confirmados/pagos.
- **Resultado:** Custo Realizado = Σ(Valor dos lançamentos de despesa). **Depende da definição completa do domínio "Tipo" em FINANCEIRO (ver REG-006 — Aporte já está definido como não sendo despesa; outros valores possíveis do domínio "Tipo" além de Aporte/Despesa continuam [H]) e do que conta como "confirmado".**
- **Status:** [H]
- **Teste necessário:** teste unitário de soma condicionada ao status do lançamento.

### REG-005 — Saldo Orçamentário
- **Descrição:** saldo entre o que está disponível para a obra e o que foi efetivamente gasto.
- **Entrada:** Orçamento Vigente/Disponível (REG-017), Custo Realizado (REG-004).
- **Condição:** sempre calculado, atualizado a cada lançamento, aporte ou alteração formal aprovada.
- **Resultado (proposta):** Saldo Orçamentário = Orçamento Vigente/Disponível − Custo Realizado.
- **Status:** [P] — a subtração em si é proposta (consistente com a redação original "Orçamento Previsto, Custo Realizado e Saldo Atual"); o que muda na Revisão 2 é que o termo de comparação deixa de ser apenas o Orçamento Previsto Total (REG-003) e passa a ser o Orçamento Vigente/Disponível (REG-017), que já incorpora aportes e alterações formais, conforme decisão homologada. **A fórmula da subtração em si ainda precisa de homologação formal antes de virar fórmula de planilha; o que já está homologado é apenas que o termo de comparação correto é o Orçamento Vigente, não o Orçamento Previsto isolado.**
- **Teste necessário:** teste unitário da subtração; teste de caso "saldo negativo" (ver REG-015); teste de regressão ao lançar um aporte (o saldo deve aumentar, não diminuir).

### REG-006 — Vínculo entre Aporte e Orçamento (Opção B) — [D] CONFLITO RESOLVIDO EM 2026-09-16
- **Decisão homologada pelo responsável pelo projeto:** **Opção B — Vincular Aporte ao Orçamento.** Substitui o registro de conflito [C] da Revisão 1 deste documento.
- **Descrição:** todo aporte financeiro destinado à obra representa entrada de recurso para a obra e aumenta o Orçamento Vigente/Disponível da obra (REG-017). O aporte **não** é tratado como despesa, custo executado ou medição.
- **Entrada:** lançamento em FINANCEIRO do tipo "Aporte", vinculado à Obra, com valor, data e origem.
- **Condição:** lançamento de Aporte confirmado.
- **Resultado:** o valor do aporte é somado ao Orçamento Vigente/Disponível da Obra (ver fórmula em REG-017). O aporte permanece registrado individualmente em FINANCEIRO (não é absorvido/apagado ao alimentar o orçamento) — não se cria uma segunda fonte de verdade para o orçamento: o Orçamento Vigente é sempre recalculado a partir de FINANCEIRO (aportes) e ALTERAÇÕES (impacto orçamentário aprovado), nunca editado diretamente.
- **O que esta decisão NÃO define (permanece [H]):** thresholds, fluxo de aprovação do próprio aporte (se há aprovação necessária para registrar um aporte), e a fórmula do Saldo de Caixa (ver REG-018) — que continua sendo um conceito distinto do Saldo Orçamentário (REG-005), conforme exigido explicitamente pela decisão homologada.
- **Status:** [D] — decisão homologada pelo responsável pelo projeto em 2026-09-16.
- **Teste necessário:** teste unitário — lançar um Aporte e verificar que (a) o Orçamento Vigente/Disponível aumenta no valor exato do aporte, (b) o Custo Realizado (REG-004) não é afetado, (c) o aporte aparece individualmente listado em FINANCEIRO com seus campos (valor, data, origem).

### REG-007 — Método de Execução do Serviço (Modelo Híbrido) — [D] HOMOLOGADO EM 2026-09-16 (Revisão 4) / DETALHADO EM 2026-09-16 (Revisão 5)
- **Descrição:** o percentual de execução de cada SERVIÇO poderá ser determinado conforme sua natureza: **(a) por medição quantitativa**, quando o serviço possuir unidade/quantidade mensurável (ver EXECUÇÃO/MEDIÇÕES, `DAD_001`); ou **(b) por status/conclusão**, quando o serviço for mais adequadamente controlado como atividade concluída/não concluída ou equivalente. Este é o "Modelo Híbrido" homologado pelo responsável pelo projeto.
- **Entrada:** Método de Execução atribuído ao Serviço (Quantitativo ou Status); e, conforme o método, Quantidade Executada (EXECUÇÃO/MEDIÇÕES) ou o Status de Execução do Serviço.
- **Condição:** sempre que houver nova medição ou mudança de status lançada em um Serviço.
- **Resultado (7.1 — Método Quantitativo, fórmula homologada em 2026-09-16):**
  **% Execução do Serviço = Quantidade Executada / Quantidade Planejada/Elegível do Serviço.**
  Arredondamento, tolerância e tratamento de excedente (lançamento que resulte em % acima de 100% — ver também REG-009) **não foram definidos** nesta decisão; assim como o tratamento do caso em que a Quantidade Planejada/Elegível é zero. Permanecem [H].
- **Resultado (7.2 — Método por Status, tabela fechada homologada em 2026-09-16):**
  **Pendente = 0% · Em andamento = 50% · Concluído = 100%.**
  Enquanto esta decisão estiver vigente, não devem ser criados percentuais adicionais nem deve ser permitido percentual intermediário informado manualmente pelo operador para um Serviço no método por Status.
- **O que esta decisão NÃO define (permanece [H]):** (i) a lista fechada de quais serviços usam cada método — a decisão homologada foi explícita em não fixar essa lista agora; (ii) quem atribui o método ao serviço e quando (cadastro do serviço, presumidamente, mas o fluxo não foi detalhado); (iii) arredondamento e tolerância do método quantitativo; (iv) tratamento de execução acima de 100% no método quantitativo; (v) tratamento de Quantidade Planejada/Elegível igual a zero.
- **Status:** [D] (existência do modelo híbrido; fórmula do método quantitativo; tabela fechada do método por status) / [H] (lista de serviços por método, fluxo de atribuição, arredondamento/tolerância, excedente, quantidade planejada zero).
- **Teste necessário:** teste unitário do método quantitativo (Executada/Planejada) e do método por status (tabela fixa 0/50/100); teste de regressão ao trocar o método de um serviço já em execução; casos de excedente e quantidade planejada zero ficam pendentes até homologação.

### REG-008 — Peso Automático do Serviço (baseado no Valor Orçado, Global) — [D] HOMOLOGADO EM 2026-09-16 (Revisão 4) / DETALHADO EM 2026-09-16 (Revisão 5)
- **Descrição:** o peso de cada SERVIÇO Elegível (REG-022) para fins de consolidação do progresso físico (REG-020) é calculado **automaticamente** a partir do seu valor orçado, sempre em relação ao total da **Obra** (peso global) — e não exige preenchimento manual como regra normal.
- **Entrada:** Valor Total Orçado de cada Serviço Elegível (REG-022) da Obra.
- **Condição:** todo cálculo de progresso físico que envolva mais de um Serviço.
- **Resultado (fórmula homologada pelo responsável pelo projeto):**
  **Peso do Serviço = Valor Orçado do Serviço / Σ Valor Orçado dos Serviços Elegíveis da Obra.**
  **Regra de escopo homologada em 2026-09-16 (Revisão 5):** este denominador é sempre **global** (soma de todos os Serviços Elegíveis da Obra) — **não deve ser renormalizado** por Subetapa ou por Etapa. O peso de cada Serviço é único e o mesmo em qualquer nível de consolidação (ver REG-020).
- **Regra de exceção — Ajuste Manual de Peso (detalhada em REG-023/REG-024/REG-025):** o operador poderá ajustar manualmente o peso de um Serviço, como **exceção**; o ajuste manual não substitui o cálculo automático como comportamento padrão, nem substitui conceitualmente o peso automático original. **Não é exigida obrigatoriamente** justificativa nem aprovação prévia para o ajuste manual (decisão homologada em 2026-09-16, Revisão 5). O sistema deve **preservar** o Peso Automático original e o Peso Ajustado utilizado — **os campos técnicos definitivos para essa rastreabilidade ainda não foram homologados** (ver DAD_001, entidade SERVIÇOS/ORÇAMENTO).
- **O que esta decisão NÃO define (permanece [H]):** (i) os domínios fechados que operacionalizam os critérios de elegibilidade em casos-limite (ver REG-022); (ii) os campos técnicos definitivos de rastreabilidade do ajuste manual (nomes, tipos, obrigatoriedade de responsável/data); (iii) se há restrição de perfil para quem pode fazer o ajuste manual (a decisão dispensou apenas justificativa e aprovação prévia, não tratou de perfil/permissão).
- **Status:** [D] (fórmula do peso automático; escopo global do denominador; princípio de que ajuste manual é exceção, não padrão; dispensa de justificativa/aprovação prévia; obrigação de preservar os dois valores) / [H] (campos de rastreabilidade, casos-limite de elegibilidade, restrição de perfil para ajuste).
- **Teste necessário:** teste unitário da fórmula do peso automático (soma dos pesos = 100% dentro do conjunto elegível da Obra); teste de regressão ao adicionar/remover Serviço elegível; teste de que o peso de um Serviço não muda ao mover/reorganizar Subetapas/Etapas (peso é global); teste de preservação do peso automático original ao lado do peso ajustado, assim que os campos forem homologados.

### REG-009 — Limite de lançamento de medição
- **Descrição:** uma medição de execução não deveria, em princípio, ultrapassar 100% do quantitativo orçado do serviço correspondente.
- **Entrada:** Quantidade/% Executado lançado em EXECUÇÃO/MEDIÇÕES.
- **Condição:** soma acumulada de execuções do mesmo serviço > quantidade orçada.
- **Resultado (proposta):** sistema deveria sinalizar/alertar quando a soma ultrapassar 100%, mas **não há definição se isso deve ser bloqueio (impedir o lançamento) ou apenas alerta visual (permitir e destacar)** — casos reais de retrabalho/glosa podem exigir lançamento acima de 100%.
- **Status:** [P] — princípio proposto, comportamento exato [H].
- **Teste necessário:** teste funcional com lançamento igual, abaixo e acima de 100%.

### REG-010 — Compra vinculada a orçamento
- **Descrição:** toda Compra deveria estar vinculada a um Serviço/Orçamento existente, para permitir comparação entre valor comprado e valor orçado.
- **Entrada:** registro de nova Compra.
- **Condição:** Compra sem vínculo a um Serviço/Orçamento, ou Compra cujo valor ultrapassa o saldo do serviço vinculado.
- **Resultado:** **não definido** se a vinculação é obrigatória, nem se há bloqueio/alerta quando o valor da compra ultrapassa o saldo orçado do serviço.
- **Status:** [H]
- **Teste necessário:** depende da regra homologada.

### REG-011 — Prazo de Pendência (SLA)
- **Descrição:** toda Pendência deveria ter um prazo de resolução esperado.
- **Entrada:** Data de Abertura da Pendência.
- **Condição:** tempo decorrido desde a abertura.
- **Resultado:** **SLA em dias não definido em nenhuma fonte.**
- **Status:** [H]
- **Teste necessário:** depende do SLA homologado.

### REG-012 — Aprovação de Alteração
- **Descrição:** uma Alteração de escopo, prazo ou orçamento deveria passar por um fluxo de aprovação antes de impactar os indicadores da Obra.
- **Entrada:** registro de nova Alteração.
- **Condição:** Alteração criada, aguardando decisão.
- **Resultado:** **fluxo de aprovação não definido** (quem aprova, quantas etapas, se há aprovação automática para valores pequenos).
- **Status:** [H]
- **Teste necessário:** depende do fluxo homologado.

### REG-013 — Alerta de Desvio Orçamentário
- **Descrição:** o sistema deve sinalizar quando o Custo Realizado se aproxima ou ultrapassa o Orçamento Previsto.
- **Entrada:** Saldo Orçamentário (REG-005).
- **Condição:** **percentual de desvio que caracteriza alerta não definido** (ex.: alertar a partir de 80% do orçamento consumido? 90%? 100%?).
- **Resultado:** não definido.
- **Status:** [H]
- **Teste necessário:** depende do threshold homologado.

### REG-014 — Alerta de Atraso de Cronograma
- **Descrição:** o sistema deve sinalizar quando uma Etapa/Subetapa está atrasada em relação ao Planejamento.
- **Entrada:** Data Fim Prevista (Planejamento) vs. data atual/Data Fim Real.
- **Condição:** **quantidade de dias de atraso que caracteriza alerta não definida.**
- **Resultado:** não definido.
- **Status:** [H]
- **Teste necessário:** depende do threshold homologado.

### REG-015 — Alerta de Saldo Negativo
- **Descrição:** o sistema deve sinalizar quando o Saldo Orçamentário (REG-005) fica negativo.
- **Entrada:** Saldo Orçamentário.
- **Condição:** Saldo Orçamentário < 0. **O ponto de disparo (zero) é a única condição implícita já coerente com a redação existente ("saldo negativo") — mas os níveis de severidade/gradação antes de chegar a zero (ex.: aviso ao chegar a 10% do saldo) não estão definidos.**
- **Resultado:** alerta visual, nível/cor não homologado (depende também de DSG_001 — cores semânticas ainda não definidas).
- **Status:** [P] (disparo em zero) / [H] (gradação e formato visual)
- **Teste necessário:** teste unitário com saldo positivo, zero e negativo.

### REG-016 — Auditoria de Integridade
- **Descrição:** verificações automatizadas de integridade dos dados.
- **Entrada:** base de dados completa.
- **Condição:** execução periódica ou sob demanda do módulo de auditoria.
- **Resultado (lista de verificações já documentada [D] em AGENTS.md §15):** integridade dos dados, campos obrigatórios, duplicidades, referências quebradas, registros órfãos, regras de negócio, cálculos, fórmulas, estrutura, relacionamentos, testes, regressões, proteção, permissões, consistência financeira. **Critério de severidade e de bloqueio automático (o que impede a homologação vs. o que é apenas aviso) não está definido.**
- **Status:** [D] (lista de verificações) / [H] (critério de severidade)
- **Teste necessário:** um teste por tipo de verificação, a ser detalhado quando os critérios de severidade forem homologados.

### REG-017 — Orçamento Vigente/Disponível — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** valor de orçamento efetivamente disponível para a obra em um dado momento, distinto do Orçamento Inicial (REG-003), pois incorpora aportes recebidos e alterações formais aprovadas.
- **Entrada:** Orçamento Inicial/Previsto (REG-003), soma dos Aportes confirmados em FINANCEIRO (REG-006), soma do Impacto no Orçamento das ALTERAÇÕES formalmente aprovadas (REG-012).
- **Condição:** recalculado a cada novo aporte confirmado, alteração aprovada com impacto orçamentário, ou revisão do orçamento inicial.
- **Resultado (fórmula homologada pelo responsável pelo projeto):**
  **Orçamento Vigente/Disponível = Orçamento Inicial + Σ(Aportes) + Σ(Alterações formais aprovadas com impacto no orçamento).**
- **Regra de fonte única:** o Orçamento Vigente é sempre **derivado/calculado** a partir de Orçamento Inicial + FINANCEIRO (aportes) + ALTERAÇÕES (impacto aprovado). Não deve existir um campo editável manualmente que sobrescreva esse cálculo — não se cria uma segunda fonte de verdade para o orçamento (decisão explícita do responsável pelo projeto).
- **Status:** [D] — fórmula homologada pelo responsável pelo projeto em 2026-09-16 (Opção B).
- **Teste necessário:** teste unitário da soma; teste de regressão ao adicionar aporte, ao aprovar alteração com impacto orçamentário, e ao combinar os dois no mesmo período.

### REG-018 — Saldo de Caixa (conceito distinto, fórmula não definida) — [H]
- **Descrição:** possível indicador de disponibilidade efetiva de caixa (recursos financeiros recebidos e não gastos), distinto do Saldo Orçamentário (REG-005), que compara orçamento disponível × custo realizado independentemente do status de pagamento.
- **Entrada:** não definida.
- **Condição:** não definida.
- **Resultado:** **não definido.** A decisão homologada em 2026-09-16 (REG-006/REG-017) resolveu como o Aporte se relaciona com o Orçamento Vigente, mas **exige explicitamente que Saldo de Caixa continue sendo tratado como um conceito conceitualmente distinto** do Saldo Orçamentário — sem, no entanto, definir sua fórmula. Nenhuma fórmula foi inventada aqui para preencher essa lacuna.
- **Status:** [H]
- **Teste necessário:** não pode ser escrito até a definição conceitual (se este indicador será implementado na V1) ser homologada.

### REG-019 — Hierarquia Oficial de Organização da Execução (OBRA → ETAPA → SUBETAPA → SERVIÇO) — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** a organização da execução da obra segue uma hierarquia fixa de 4 níveis: OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO. SUBETAPAS é entidade própria do modelo de dados (não um campo textual de Serviços nem um nível implícito de Etapas) — decisão de arquitetura homologada pelo responsável pelo projeto, eliminando o conflito [C] anteriormente registrado em `DAD_001` sobre a existência de Subetapas como entidade.
- **Entrada:** criação de registro em ETAPAS, SUBETAPAS ou SERVIÇOS/ORÇAMENTO.
- **Condição:** (a) toda SUBETAPA deve estar vinculada a uma ETAPA; (b) todo SERVIÇO/ORÇAMENTO deve estar vinculado a uma SUBETAPA (nunca diretamente a uma Etapa).
- **Resultado:** a hierarquia em si é regra fixa e homologada — não é uma proposta. O **mecanismo de validação/bloqueio** de um registro que viole a hierarquia (ex.: tentativa de criar um Serviço sem Subetapa) segue a mesma indefinição já registrada em REG-002 (bloqueio vs. outro tratamento) — **não foi definido nem inventado nesta revisão.**
- **Objetivo declarado da hierarquia (não é uma fórmula nova):** permitir consolidar indicadores de execução, planejamento, orçamento e dashboard nos 4 níveis (obra, etapa, subetapa, serviço). As fórmulas de consolidação em si são governadas por REG-003 (orçamento, [P]), REG-007/REG-008/REG-020 (execução física e peso — homologados nas Revisões 4 e 5, com detalhes pontuais ainda [H] conforme registrado em cada regra) — não alteradas por esta regra.
- **Status:** [D] (existência da entidade e da hierarquia) / [H] (mecanismo de validação, herdado de REG-002)
- **Teste necessário:** teste de integridade referencial — criar Subetapa sem Etapa válida (deve falhar/alertar) e criar Serviço sem Subetapa válida (deve falhar/alertar), conforme o comportamento que vier a ser homologado em REG-002.

### REG-020 — Consolidação Hierárquica do Progresso Físico (Serviço → Subetapa → Etapa → Obra) — [D] HOMOLOGADO EM 2026-09-16 (Revisão 4) / DETALHADO EM 2026-09-16 (Revisão 5)
- **Descrição:** o progresso físico é consolidado subindo pela hierarquia oficial (REG-019): SERVIÇO → SUBETAPA → ETAPA → OBRA, utilizando os pesos **globais** de cada Serviço (REG-008) e o % de execução de cada serviço apurado conforme seu método (REG-007).
- **Entrada:** % Execução de cada Serviço (REG-007); Peso automático global (ou, por exceção, peso ajustado protegido — REG-023) de cada Serviço Elegível (REG-008/REG-022); estrutura hierárquica Serviço → Subetapa → Etapa → Obra (REG-019).
- **Condição:** sempre que houver nova medição/mudança de status em um Serviço, ou alteração no valor orçado/peso/elegibilidade de um Serviço.
- **Resultado:** o % de execução de cada nível (Subetapa, Etapa, Obra) é obtido consolidando os pesos **globais** (já calculados sobre o total da Obra, REG-008) dos Serviços pertencentes a cada agrupamento — o peso de um Serviço não é recalculado nem renormalizado dentro de sua Subetapa ou Etapa; ele é apenas somado/agregado conforme o nível de consolidação desejado.
- **Regra de escopo homologada em 2026-09-16 (Revisão 5) — resolve o item antes [H]:** os pesos são sempre globais em relação ao total de Serviços Elegíveis da Obra (REG-008); **não há renormalização por Subetapa ou por Etapa** em nenhum nível da hierarquia.
- **O que esta decisão NÃO define (permanece [H]):** fórmula técnica exata de implementação da agregação (ex.: representação de "% de execução de uma Subetapa" isoladamente, fora do contexto de consolidação até a Obra, quando os pesos são globais e não somam 100% dentro da própria Subetapa) — não foi detalhada nem inventada aqui.
- **Status:** [D] (existência da consolidação hierárquica; uso de pesos globais, não renormalizados por nível) / [H] (fórmula técnica de exibição do % isolado por Subetapa/Etapa quando os pesos são globais).
- **Teste necessário:** teste de consolidação com pesos globais até o nível Obra (soma final = 100%); teste de que o peso de um Serviço não muda ao ser reorganizado entre Subetapas/Etapas.

### REG-022 — Serviços Elegíveis para o Cálculo do Progresso Físico — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** define quais Serviços integram a base de cálculo do progresso físico (REG-007/REG-008/REG-020).
- **Entrada:** atributos do Serviço (vínculo com Subetapa, escopo, status de ativação) e histórico de ALTERAÇÕES aprovadas.
- **Condição:** todo cálculo de peso automático (REG-008) ou de consolidação de progresso físico (REG-020).
- **Resultado — critérios de elegibilidade (homologados):** um Serviço é elegível quando: (a) representa execução física real; (b) possui vínculo válido com uma Subetapa (REG-019); (c) pertence ao escopo vigente da Obra; (d) está ativo para execução; (e) possui valor orçado válido, quando esse valor for necessário para determinar seu peso (REG-008).
- **Resultado — exclusões (homologadas):** ficam fora do cálculo físico: serviços cancelados; serviços excluídos do escopo; registros que não representam execução física; registros sem valor orçado válido quando não for possível determinar seu peso.
- **Incorporação via Alterações:** Serviços provenientes de Alterações formalmente aprovadas (REG-012) e incorporados ao escopo vigente passam a integrar a base elegível.
- **O que esta decisão NÃO define (permanece [H]):** os domínios fechados que operacionalizam os critérios acima — por exemplo, a lista fechada de valores de "Status do Serviço" que caracteriza "ativo para execução", e o que exatamente conta como "registro que não representa execução física". Ver "Domínios pendentes de homologação" em DAD_001.
- **Status:** [D] (critérios de elegibilidade e exclusão; incorporação via Alterações aprovadas) / [H] (domínios fechados que operacionalizam esses critérios).
- **Teste necessário:** teste de composição da base elegível — incluir/excluir um Serviço por cada critério e verificar que o peso automático (REG-008) é recalculado corretamente e a soma dos pesos elegíveis permanece 100%.

### REG-023 — Proteção do Peso Manual — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** quando um Serviço recebe ajuste manual de peso (REG-008), esse peso fica protegido: o sistema não deve modificá-lo automaticamente.
- **Entrada:** Peso Ajustado (manual) de um Serviço.
- **Condição:** existência de ao menos um Serviço com peso ajustado manualmente dentro da base elegível (REG-022).
- **Resultado:** o peso manual não é recalculado nem sobrescrito por nenhum processo automático — inclusive pela redistribuição proporcional (REG-024). Somente Serviços que permanecerem com peso automático participam de qualquer redistribuição.
- **Status:** [D]
- **Teste necessário:** alterar o valor orçado de outro Serviço elegível e verificar que o peso do Serviço com ajuste manual permanece inalterado.

### REG-024 — Redistribuição Proporcional entre Serviços com Peso Automático — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** quando a presença de peso(s) manual(is) fizer a soma dos pesos deixar de totalizar 100%, a diferença necessária é redistribuída **proporcionalmente** apenas entre os Serviços que permanecem com peso automático — os pesos manuais permanecem protegidos (REG-023).
- **Entrada:** Peso(s) Ajustado(s) manualmente (protegidos); pesos automáticos correntes dos demais Serviços elegíveis (REG-008/REG-022).
- **Condição:** soma dos pesos (manuais protegidos + automáticos correntes) ≠ 100%, havendo ao menos um Serviço elegível com peso automático disponível para redistribuição.
- **Resultado:** a diferença necessária para fechar 100% é distribuída proporcionalmente somente entre os Serviços com peso automático, de modo que o total final (pesos manuais protegidos + pesos automáticos redistribuídos) permaneça em 100%. **O sistema não pode alterar silenciosamente um peso definido manualmente** (reforça REG-023).
- **O que esta decisão NÃO define (permanece [H]):** a fórmula técnica exata da proporcionalidade (a base de cálculo numérica usada para distribuir a diferença entre os automáticos) não foi detalhada — apenas o princípio (proporcional, restrito aos automáticos, fechando em 100%) foi homologado.
- **Status:** [D] (princípio da redistribuição proporcional restrita aos automáticos, com total final em 100% e pesos manuais protegidos) / [H] (fórmula técnica exata).
- **Teste necessário:** cenário com mistura de pesos manuais e automáticos — validar que a soma final é 100% e que nenhum peso manual é alterado.

### REG-025 — Bloqueio quando Todos os Serviços Elegíveis Têm Peso Manual — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** caso específico de REG-024 em que não existe nenhum Serviço com peso automático disponível para absorver a redistribuição.
- **Entrada:** conjunto de Serviços Elegíveis (REG-022) todos com peso ajustado manualmente; evento que altera a soma dos pesos (ex.: novo Serviço elegível, exclusão de Serviço, mudança de valor orçado).
- **Condição:** 100% dos Serviços Elegíveis estão com peso manual **e** a soma dos pesos deixa de totalizar 100% em decorrência do evento.
- **Resultado:** o sistema **não** redistribui automaticamente nenhum peso, **não** altera nenhum peso manual existente, e **bloqueia** o ajuste/evento que resultaria em distribuição inválida, informando ao operador que a distribuição precisa ser readequada manualmente para totalizar 100%.
- **Status:** [D]
- **Teste necessário:** cenário com todos os Serviços Elegíveis em peso manual — forçar um evento que desbalanceie a soma e verificar que o sistema bloqueia em vez de redistribuir ou alterar pesos manuais.

### REG-021 — Separação entre Aporte Financeiro e Peso Físico — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** preserva a decisão já homologada sobre Aporte × Orçamento (REG-006/REG-017: Orçamento Vigente/Disponível = Orçamento Inicial + Σ Aportes + Σ Alterações Formais Aprovadas), mas estabelece que **aporte financeiro não aumenta automaticamente o peso físico da obra**. Um aporte só pode influenciar a composição do progresso físico caso esteja efetivamente associado a Serviços executáveis que façam parte da base elegível do cálculo físico (REG-008).
- **Entrada:** lançamento de Aporte em FINANCEIRO (REG-006); base de Serviços elegíveis para o cálculo de peso físico (REG-008).
- **Condição:** todo lançamento de Aporte, no momento de avaliar se ele deve refletir no cálculo do progresso físico.
- **Resultado:** o Orçamento Vigente/Disponível (REG-017) **não deve ser usado diretamente como denominador do peso físico** quando existirem valores de aporte sem Serviço executável correspondente. Um aporte só entra na base de peso físico se, e somente se, estiver vinculado a um Serviço/Orçamento elegível (REG-008).
- **Separação conceitual obrigatória:** permanecem conceitualmente distintos — orçamento vigente/disponível (REG-017); recurso financeiro/aporte (REG-006); custo realizado (REG-004); progresso físico (REG-007/REG-020); peso físico (REG-008). Valor financeiro disponível não é convertido automaticamente em percentual físico.
- **O que esta decisão NÃO define (permanece [H]):** o mecanismo exato de vínculo entre um Aporte e um Serviço executável (se obrigatório, se opcional, como é registrado) — não foi definido nem inventado nesta revisão.
- **Status:** [D] (separação conceitual e regra de que aporte não altera peso físico automaticamente) / [H] (mecanismo de vínculo Aporte↔Serviço).
- **Teste necessário:** teste de regressão — lançar um Aporte sem Serviço vinculado e verificar que o progresso físico da Obra **não se altera**; teste com Aporte vinculado a Serviço elegível assim que o mecanismo de vínculo for homologado.

### REG-026 — Valor Previsto do Serviço (Opção C) — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** o Valor Previsto de cada Serviço/Orçamento é, por padrão, calculado automaticamente a partir de Quantidade × Valor Unitário; o Operador pode substituí-lo manualmente quando necessário, sem que isso apague o valor calculado.
- **Entrada:** Quantidade Orçada, Valor Unitário; opcionalmente, Valor Previsto informado manualmente pelo Operador.
- **Condição:** todo Serviço com Quantidade e Valor Unitário preenchidos.
- **Resultado (fórmula homologada — Etapa 3, Seções 3/10/11/12):**
  **Valor Calculado = Quantidade Orçada × Valor Unitário** (sempre calculado; nunca sobrescrito).
  **Valor Previsto = Valor Calculado**, salvo **Ajuste Manual** do Operador, caso em que **Valor Previsto = valor informado pelo Operador**.
  **Ajuste Manual (SIM/NÃO)** é identificável a partir da presença de um valor manual — não exige justificativa nem aprovação prévia (Seção 12), diferentemente do que ocorre com REG-008 (peso físico), que é um conceito distinto.
- **Precisão:** os valores usados no cálculo não são arredondados prematuramente (Etapa 3, Seção 30); arredondamento só ocorre na apresentação (formatação de moeda), nunca no valor armazenado/usado em soma.
- **O que esta decisão NÃO define (permanece [H]):** regra de arredondamento específica para exibição além do formato de moeda padrão; workflow de aprovação do ajuste manual (explicitamente não exigido — Seção 12); tratamento de Quantidade ou Valor Unitário ausentes além de retornar "sem valor calculado".
- **Status:** [D] — única decisão desta rodada tratada como HOMOLOGADA por instrução explícita (Etapa 3, Seção 36).
- **Teste necessário:** ver Cenários A–H da homologação da Etapa 3 (`testes/test_orcamento.py`) — cobrem cálculo simples, ajuste manual, preservação do Valor Calculado, quantidade/valor zero, quantidade/valor negativo (rejeitados) e totais por Subetapa/Etapa/Obra.

### REG-027 — Status do Serviço/Orçamento — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** domínio fechado do campo "Status" da entidade SERVIÇOS/ORÇAMENTO, resolvendo o item que estava [H] desde a Revisão 1 do `DAD_001`.
- **Entrada:** Status atribuído a um Serviço/Orçamento.
- **Condição:** sempre que o Status de um Serviço for definido ou alterado.
- **Resultado (domínio fechado homologado — Etapa 3, Seção 18):** Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído. Nenhum outro valor é válido.
- **Regra de composição do orçamento corrente (Etapa 3, Seção 19):** Serviços com Status Cancelado, Retirado do Escopo ou Substituído **não** compõem os totais do orçamento corrente (REG-003); os demais (Ativo, Concluído, e Status ainda não informado) compõem. **Nenhum registro é apagado automaticamente** ao mudar de status — o histórico é preservado (Seção 19).
- **Distinção de outros domínios:** este Status é específico do REGISTRO orçamentário do Serviço — não se confunde com `StatusExecucao` (REG-007, andamento físico) nem com os campos "Status" ainda [H] de OBRAS/ETAPAS/SUBETAPAS (domínios distintos, não tratados por esta regra).
- **O que esta decisão NÃO define (permanece [H]):** fluxo de transição entre status (ex.: quem pode marcar um Serviço como Substituído, se há vínculo obrigatório com o Serviço substituto) — não foi definido nem inventado.
- **Status:** [D] (domínio fechado e regra de composição do orçamento corrente) / [H] (fluxo de transição entre status).
- **Teste necessário:** teste unitário por status (os 5 valores) verificando inclusão/exclusão do total; teste de que um Serviço cancelado permanece no repositório (não é removido).

### REG-028 — Variação do Orçamento — [D] HOMOLOGADO EM 2026-09-16
- **Descrição:** diferença entre o Valor Previsto e o Valor Calculado de um Serviço, exposta com o termo "Variação" (nunca "Desvio" — termo reservado aos alertas de REG-013/014/015, ainda [H]).
- **Entrada:** Valor Previsto (REG-026), Valor Calculado (REG-026).
- **Condição:** sempre que ambos os valores estiverem disponíveis.
- **Resultado (fórmula homologada — Etapa 3, Seção 13):** **Variação = Valor Previsto − Valor Calculado.** É zero quando não há Ajuste Manual (Valor Previsto = Valor Calculado).
- **O que esta decisão NÃO define (permanece [H]):** variação **percentual** — deliberadamente não implementada nesta rodada por poder colidir com os thresholds de alerta de desvio orçamentário ainda não homologados (REG-013); nenhuma formatação condicional (cor/ícone) foi criada para a Variação (Etapa 3, Seção 31: alertas completos pertencem a etapa futura).
- **Status:** [D] (fórmula da variação absoluta, em R$) / [H] (variação percentual, formatação de alerta).
- **Teste necessário:** teste unitário da subtração; teste de que a Variação é `None`/vazia quando faltam dados; teste de que nenhuma cor/ícone de alerta é aplicado à coluna.

---

## Regras citadas na tarefa sem informação suficiente para formalizar

- **Aportes:** **[C] RESOLVIDO em 2026-09-16** — ver REG-006 (vínculo Aporte × Orçamento, Opção B homologada) e REG-017 (fórmula do Orçamento Vigente/Disponível). O conceito de Saldo de Caixa citado junto com Aportes na Revisão 1 permanece [H] — ver REG-018. A partir da Revisão 4, ver também REG-021 (aporte não altera peso físico automaticamente).
- **Pesos:** **[D] amplamente HOMOLOGADO em 2026-09-16 (Revisões 4 e 5)** — ver REG-008 (peso automático global a partir do valor orçado, sem renormalização por nível), REG-020 (uso do peso na consolidação hierárquica), REG-022 (elegibilidade), REG-023 (proteção do peso manual), REG-024 (redistribuição proporcional entre automáticos) e REG-025 (bloqueio quando todos os pesos são manuais). Permanecem [H]: campos técnicos definitivos de rastreabilidade do ajuste manual (REG-008), domínios fechados que operacionalizam a elegibilidade (REG-022) e fórmula técnica exata da redistribuição proporcional (REG-024).
- **Método de execução do Serviço:** **[D] HOMOLOGADO em 2026-09-16 (Revisão 5)** — ver REG-007 (fórmula do método quantitativo e tabela fechada do método por status: Pendente 0% / Em andamento 50% / Concluído 100%). Permanecem [H]: lista de serviços por método, arredondamento/tolerância, tratamento de excedente e de quantidade planejada zero.
- **Medições — periodicidade:** ver DAD_001 (entidade EXECUÇÃO/MEDIÇÕES) — não definida.
- **Subetapas como entidade própria:** **[C] RESOLVIDO em 2026-09-16** — ver REG-019 (hierarquia oficial OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO) e `DAD_001` (entidade SUBETAPAS).
- **Orçamento previsto dos serviços:** **[D] HOMOLOGADO em 2026-09-16 (Revisão 6)** — ver REG-003 (atualizada), REG-026 (Valor Previsto/Valor Calculado/Ajuste Manual) e REG-028 (Variação). Permanecem [H]/fora de escopo: Orçamento Vigente completo (REG-017), variação percentual, alertas de desvio.
- **Status do Serviço/Orçamento:** **[D] HOMOLOGADO em 2026-09-16 (Revisão 6)** — ver REG-027 (domínio fechado Ativo/Concluído/Cancelado/Retirado do Escopo/Substituído). Permanece [H]: fluxo de transição entre status.

## Registro de homologação — Revisão 2

Em 2026-09-16, o responsável pelo projeto homologou a **Opção B — Vincular Aporte ao Orçamento**, resolvendo o conflito [C] registrado na Revisão 1 entre "Saldo Orçamentário" e "Aportes". Esta decisão está registrada em REG-006 e REG-017. Nenhum threshold, fluxo de aprovação de aporte ou fórmula de Saldo de Caixa foi definido junto — esses pontos continuam [H], conforme instrução explícita de não inventar o que não foi necessário para registrar a decisão homologada.

## Registro de homologação — Revisão 3

Em 2026-09-16, o responsável pelo projeto homologou **SUBETAPAS como entidade própria do modelo de dados**, com hierarquia oficial **OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO**, resolvendo o conflito [C] registrado na Revisão 1 sobre a natureza de Subetapas. Esta decisão está registrada em REG-019 e em `DAD_001` (entidade SUBETAPAS, e ajustes nas entidades ETAPAS e SERVIÇOS/ORÇAMENTO). **Nenhuma fórmula de peso, de % de execução física, ou threshold foi criada** — REG-007 e REG-008 permanecem [H], exatamente como antes desta decisão, conforme instrução explícita de não inventar regras adicionais além do necessário para registrar a decisão de arquitetura.

## Regra fundamental mantida

Nenhum threshold numérico (%, dias, valor) foi definido nesta revisão, exceto o que estava explicitamente contido na decisão homologada (a fórmula de composição do Orçamento Vigente, REG-017). Todos os demais pontos que exigiriam um número ou uma definição adicional continuam marcados **[H] HOMOLOGAR**, conforme instrução explícita do responsável pelo projeto.

## Registro de homologação — Revisão 4

Em 2026-09-16, o responsável pelo projeto homologou o **MODELO HÍBRIDO de cálculo do progresso físico**, registrado em:
- **REG-007** — método de execução do serviço (quantitativo ou status/conclusão), sem lista fechada de quais serviços usam cada método;
- **REG-008** — peso automático do serviço a partir do valor orçado (Peso do Serviço = Valor Orçado do Serviço / Soma dos Valores Orçados dos Serviços Elegíveis), com ajuste manual admitido apenas como exceção;
- **REG-020** — consolidação hierárquica do progresso físico (Serviço → Subetapa → Etapa → Obra) usando os pesos automáticos;
- **REG-021** — separação entre aporte financeiro e peso físico: aporte não aumenta automaticamente o peso físico da obra, salvo quando vinculado a um Serviço executável elegível.

As decisões já homologadas anteriormente foram preservadas e não reabertas: Aporte × Orçamento = Opção B (REG-006/REG-017); SUBETAPAS como entidade própria (REG-019); hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO. **Não foram criados thresholds, fórmulas adicionais, domínios fechados ou regras de exceção além do explicitamente definido pela decisão.** Os campos definitivos de rastreabilidade do ajuste manual de peso (peso automático, peso ajustado, justificativa, responsável, data) **não foram homologados nesta rodada** e permanecem [H] — ver DAD_001, entidade SERVIÇOS/ORÇAMENTO.

## Registro de homologação — Revisão 5

Em 2026-09-16, o responsável pelo projeto homologou a **consolidação completa do motor de progresso físico**, registrada em:
- **REG-007** — fórmula do método quantitativo (Quantidade Executada / Quantidade Planejada/Elegível) e tabela fechada do método por status (Pendente = 0%, Em andamento = 50%, Concluído = 100%, sem percentuais adicionais nem intermediário manual enquanto vigente);
- **REG-008** — peso automático sempre **global** (denominador = Σ Valor Orçado dos Serviços Elegíveis da Obra, nunca renormalizado por Subetapa/Etapa); ajuste manual não exige obrigatoriamente justificativa nem aprovação prévia, mas o sistema deve preservar o peso automático original e o peso ajustado utilizado;
- **REG-020** — a consolidação hierárquica (Serviço → Subetapa → Etapa → Obra) usa os pesos globais sem renormalização em nenhum nível, resolvendo o item que estava [H] desde a Revisão 4;
- **REG-022** (nova) — critérios de elegibilidade e exclusão de Serviços para o cálculo físico, incluindo a incorporação de Serviços de Alterações formalmente aprovadas;
- **REG-023** (nova) — peso manual fica protegido: o sistema não o modifica automaticamente;
- **REG-024** (nova) — quando há mistura de pesos manuais e automáticos, a diferença para fechar 100% é redistribuída proporcionalmente somente entre os automáticos, sem tocar nos manuais;
- **REG-025** (nova) — se todos os Serviços Elegíveis estiverem com peso manual e a soma deixar de fechar 100%, o sistema bloqueia o ajuste em vez de redistribuir ou alterar pesos manuais.

**Preservado, não reaberto:** Aporte × Orçamento = Opção B (REG-006/REG-017); SUBETAPAS como entidade própria (REG-019); hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO; peso automático baseado no valor orçado (REG-008, Revisão 4); separação entre orçamento financeiro e progresso físico (REG-021). **Permanecem [H], não inventados nesta rodada:** lista fechada de serviços por método quantitativo/status; responsável e momento de atribuição do método; regras de arredondamento e tolerância; tratamento de execução acima de 100%; tratamento de quantidade planejada igual a zero; domínios fechados que operacionalizam os critérios de elegibilidade (REG-022); campos técnicos definitivos de rastreabilidade do ajuste manual; fórmula técnica final da redistribuição proporcional (REG-024); fluxo técnico de vínculo Aporte ↔ Serviço (REG-021).

## Registro de homologação — Revisão 6

Em 2026-09-16, o responsável pelo projeto homologou o módulo/base de **ORÇAMENTO** (Etapa 3 de construção), registrado em:
- **REG-003 (atualizada)** — Orçamento Previsto de Subetapa/Etapa/Obra = Σ Valor Previsto (não mais Σ Valor Total Orçado isolado) dos Serviços elegíveis;
- **REG-026 (nova)** — Valor Previsto do Serviço: Valor Calculado = Quantidade × Valor Unitário (sempre calculado, nunca sobrescrito); Valor Previsto = Valor Calculado, salvo Ajuste Manual do Operador (sem exigência de justificativa/aprovação);
- **REG-027 (nova)** — Status do Serviço/Orçamento: domínio fechado Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído; os três últimos não compõem o orçamento corrente, mas nenhum registro é apagado;
- **REG-028 (nova)** — Variação do Orçamento = Valor Previsto − Valor Calculado (termo "Variação", nunca "Desvio"); variação percentual e alertas visuais permanecem [H]/fora de escopo.

Conforme instrução explícita da Seção 36 da homologação da Etapa 3, **apenas a decisão do Valor Previsto (REG-026, Opção C) foi tratada como HOMOLOGADA** — o Status do Serviço (REG-027) e a Variação (REG-028) são registrados como [D] por serem aplicações diretas de listas/fórmulas fornecidas explicitamente na própria homologação (Seções 13 e 18), não interpretações ou invenções do agente; nenhuma outra proposta [P]/[H] pré-existente foi promovida a [D] por extensão.

**Preservado, não reaberto:** Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO; Modelo Híbrido de progresso físico e peso automático (Revisões 4/5); separação entre orçamento financeiro e progresso físico (REG-021). **Permanecem [H]/fora de escopo, não inventados nesta rodada:** Orçamento Vigente completo (Orçamento Inicial + Aportes + Alterações Aprovadas, REG-017); Custo Realizado, Pagamentos, Saldo de Caixa; Alterações aprovadas modificando orçamento/escopo; alertas de desvio orçamentário (REG-013/014/015) e variação percentual; fluxo de transição entre status do Serviço (REG-027); regra de arredondamento de exibição além da formatação de moeda padrão (REG-026); mecanismo de proteção do Excel (SEC_001).
