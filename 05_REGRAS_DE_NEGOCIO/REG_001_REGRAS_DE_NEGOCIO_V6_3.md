# Regras de Negócio — V6.3 (Revisão 10 — Compras)

**Data da revisão:** 2026-09-16
**Motivo da Revisão 1:** `AUDITORIA_PRE_CONSTRUCAO_V1` identificou que nenhuma regra tinha threshold, fórmula ou fluxo documentado além do nome do tema. A Revisão 1 substituiu a versão anterior (3 linhas) por regras formalizadas com ID.
**Motivo da Revisão 2:** o responsável pelo projeto homologou a **Opção B — Vincular Aporte ao Orçamento**, resolvendo o conflito [C] registrado em REG-006 (Revisão 1) entre "Saldo Orçamentário" e "Aportes". REG-005 foi ajustada para usar o novo conceito de Orçamento Vigente/Disponível (REG-017), e REG-006 passou a documentar a regra de vínculo já resolvida.
**Motivo da Revisão 3:** o responsável pelo projeto homologou **SUBETAPAS como entidade própria**, com hierarquia oficial **OBRAS → ETAPAS → SUBETAPAS → SERVIÇOS/ORÇAMENTO** (ver `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001`). Esta revisão ajusta a redação de REG-007 (referências a "Subetapa/Serviço" tornam-se explícitas quanto à hierarquia) e adiciona REG-019, que registra a hierarquia como regra de integridade referencial. **Nenhuma fórmula de peso ou de % de execução foi definida ou alterada** — REG-007 e REG-008 continuam [H], conforme instrução explícita de não inventar regras adicionais.
**Motivo da Revisão 4:** o responsável pelo projeto homologou o **MODELO HÍBRIDO de cálculo do progresso físico**: (a) o % de execução de cada Serviço pode ser apurado por medição quantitativa ou por status/conclusão, conforme a natureza do serviço; (b) o peso de cada Serviço na consolidação é calculado **automaticamente** a partir do seu Valor Orçado; (c) a consolidação segue a hierarquia SERVIÇO → SUBETAPA → ETAPA → OBRA usando esses pesos automáticos; (d) o ajuste manual de peso é admitido apenas como exceção, com rastreabilidade; (e) aporte financeiro **não** altera automaticamente o peso físico. Esta revisão reescreve REG-007 e REG-008 (antes [H]) e adiciona REG-020 e REG-021. Não foram criados thresholds, domínios fechados ou regras de exceção além do explicitamente decidido — o que não foi decidido permanece [H].
**Motivo da Revisão 5:** o responsável pelo projeto homologou a **consolidação completa do motor de progresso físico**, detalhando pontos que a Revisão 4 havia deixado em [H]: (a) fórmula do método quantitativo (Quantidade Executada / Quantidade Planejada/Elegível); (b) tabela fechada do método por status (Pendente = 0%, Em andamento = 50%, Concluído = 100%, sem percentuais adicionais nem intermediário manual); (c) o peso automático é sempre **global**, calculado sobre o total de Serviços Elegíveis da Obra, e **não é renormalizado** por Subetapa/Etapa — os pesos globais são apenas somados por agrupamento na consolidação; (d) critérios de elegibilidade de Serviço para o cálculo físico; (e) ajuste manual de peso não exige obrigatoriamente justificativa nem aprovação prévia, mas o sistema deve preservar o peso automático original e o peso ajustado utilizado; (f) peso manual fica protegido — não sofre redistribuição automática; (g) quando parte dos serviços tem peso automático, a diferença necessária para fechar 100% é redistribuída proporcionalmente somente entre eles; (h) se todos os Serviços Elegíveis estiverem com peso manual e a soma deixar de fechar 100%, o sistema bloqueia o ajuste em vez de redistribuir. Esta revisão detalha REG-007 e REG-008, resolve o item [H] de escopo do denominador em REG-020, e adiciona REG-022 (Serviços Elegíveis), REG-023 (Proteção do Peso Manual), REG-024 (Redistribuição Proporcional) e REG-025 (Bloqueio quando Todos os Pesos são Manuais). Nenhuma decisão anterior foi reaberta; o que não foi explicitamente decidido nesta rodada (arredondamento, tolerância, tratamento de excedente, quantidade planejada zero, lista fechada de serviços por método, campos técnicos definitivos de rastreabilidade, fórmula técnica exata da redistribuição, fluxo de vínculo Aporte↔Serviço) permanece [H].
**Motivo da Revisão 6:** o responsável pelo projeto homologou o módulo/base de **ORÇAMENTO** ("Etapa 3" de construção): (a) Valor Previsto = Quantidade × Valor Unitário (Opção C) como padrão, com possibilidade de Ajuste Manual pelo Operador, preservando sempre o Valor Calculado; (b) Variação do Orçamento = Valor Previsto − Valor Calculado (termo "Variação", nunca "Desvio"); (c) domínio fechado do Status do Serviço/Orçamento (Ativo, Concluído, Cancelado, Retirado do Escopo, Substituído); (d) Serviços Cancelados/Retirados do Escopo/Substituídos não compõem os totais do orçamento corrente, mas continuam existindo na base (nenhum registro é apagado); (e) consolidação do Orçamento Previsto pela hierarquia Serviço → Subetapa → Etapa → Obra, usando o Valor Previsto (REG-003 atualizada). Esta revisão reescreve REG-003 e adiciona REG-026 (Valor Previsto do Serviço), REG-027 (Status do Serviço/Orçamento) e REG-028 (Variação do Orçamento). Conforme instrução explícita da Seção 36 da homologação, **apenas a decisão do Valor Previsto (Opção C) foi tratada como HOMOLOGADA por esta rodada** — as demais decisões registradas aqui (Status do Serviço, Variação) são aplicações diretas de listas/fórmulas fornecidas explicitamente na própria homologação, não invenções; nada além disso foi promovido de [P]/[H] para [D]. Não implementados nesta revisão (permanecem para etapas futuras): Aportes, Alterações Aprovadas, Custo Realizado, Pagamentos, Saldo de Caixa, Orçamento Vigente completo (REG-017), alertas de desvio (REG-013/014/015), variação percentual.
**Motivo da Revisão 7:** o responsável pelo projeto homologou o módulo **FINANCEIRO** ("Etapa 4" de construção, 2026-09-17): (a) domínio fechado do Tipo de FINANCEIRO — Aporte, Outras Entradas, Despesa/Custo, Outras Saídas — fechando o que a Revisão 1 (REG-006) havia deixado parcial; (b) Custo Realizado = Σ Valor dos lançamentos do tipo Despesa/Custo, independentemente de pagamento; (c) Orçamento Vigente = Orçamento Inicial + Σ Aportes **nesta etapa** (a parcela de Alterações Formais Aprovadas de REG-017 permanece [H] — o módulo Alterações não foi construído); (d) Saldo Orçamentário = Orçamento Vigente − Custo Realizado, podendo ser negativo (estouro), sem bloqueio; (e) % Orçamento Consumido = Custo Realizado / Orçamento Vigente × 100, sem limite artificial de 100%, com tratamento explícito de divisão por zero (retorna "não calculável", nunca 0%); (f) separação formal entre MOVIMENTO FINANCEIRO (reconhecimento do custo, em FINANCEIRO) e PAGAMENTO (baixa financeira, nova entidade PAGAMENTOS), com N pagamentos parciais e/ou totais por lançamento; (g) A Pagar = Custo Reconhecido − Total Pago; (h) Saldo de Caixa = (Aportes + Outras Entradas) − (Pagamentos + Outras Saídas) — o reconhecimento de uma Despesa/Custo NÃO reduz o Caixa por si só. Esta revisão reescreve REG-004, REG-005 e REG-018 (de [H]/[P] para [D]); acrescenta uma nota explícita em REG-017 sobre o escopo parcial implementado nesta etapa; e adiciona REG-029 (Pagamento e A Pagar), REG-030 (Tipos de Movimentação Financeira), REG-031 (% Orçamento Consumido e Divisão por Zero) e REG-032 (Estouro de Orçamento Não Bloqueia). **Alterações Formais Aprovadas continuam [H]/fora de escopo** (módulo Alterações não construído) — nenhuma implementação foi inventada para essa parcela.
**Motivo da Revisão 8:** o responsável pelo projeto homologou o módulo **ALTERAÇÕES** ("Etapa 5" de construção, 2026-09-17), fechando as duas últimas lacunas de REG-017: (a) domínio fechado do "Status de Aprovação" — Pendente, Aprovada, Rejeitada — sem workflow multi-etapa, o Operador seleciona o Status diretamente (mesmo princípio "sistema informa, Operador decide" já usado em REG-032); só Aprovada entra no Orçamento Vigente; (b) domínio fechado do "Tipo de Alteração" — Escopo, Prazo, Orçamento — sem automação sobre SERVIÇOS/ORÇAMENTO para Alterações de Escopo (permanece só registro informativo); (c) REG-017 está, a partir desta revisão, **completamente implementado**: Orçamento Vigente = Orçamento Inicial + Aportes + Alterações Formais Aprovadas, validado inclusive com dados reais recalculados em Excel (não apenas texto de fórmula). Esta revisão reescreve REG-012 (de [H] para [D]) e a nota da Revisão 7 em REG-017 (de "escopo parcial" para "completo"). Conforme o mesmo padrão de rigor das rodadas anteriores, os campos "Impacto no Orçamento"/"Impacto no Prazo" de ALTERAÇÕES foram homologados como **aceitando valor negativo** (delta com sinal — uma Alteração pode reduzir orçamento ou antecipar prazo), diferente de FINANCEIRO (REG-030), onde o sinal é sempre dado pelo Tipo. Não implementados nesta revisão (permanecem para etapas futuras): qualquer automação Escopo→Serviços/Orçamento; integração de "Impacto no Prazo" com um módulo de Planejamento/Cronograma (ainda não construído); restrição de perfil sobre quem pode aprovar/rejeitar uma Alteração; domínio de cancelamento/situação de FINANCEIRO (Etapa 4, ainda [H]).
**Motivo da Revisão 9 (Etapa 5.1 — Correções Pós-Auditoria, 2026-09-19):** uma auditoria técnica completa do estado pós-Etapa 5 encontrou uma divergência entre o domínio de "Status de Aprovação" homologado na Revisão 8 (3 valores) e a decisão efetivamente pretendida pelo responsável pelo projeto. O responsável pelo projeto **corrige formalmente REG-012**: o domínio fechado passa a **Em análise, Aprovada, Rejeitada, Cancelada (4 valores)** — "Pendente" é renomeado para "Em análise" e "Cancelada" é adicionada. Nenhuma outra regra desta revisão muda: apenas "Aprovada" continua entrando no Orçamento Vigente (REG-017); os demais 3 status permanecem visíveis na base, nunca apagados. A mesma auditoria também identificou que a "Regra sobre IDs" (REG-001) estava desatualizada: o formato de ID técnico já está de fato homologado e em uso desde a Etapa 1 (`PREFIXO-0000`, ver `config/ids_config.py`) — REG-001 é corrigida de [H] para [D]. A auditoria também identificou um caso de negócio ainda sem decisão — Pagamento cujo Total Pago supera o Custo Reconhecido do lançamento (sobrepagamento) — que permanece **[H]** nesta revisão; nenhuma regra foi inventada para esse caso (ver REG-029, nota adicionada). Esta revisão também corrige, no Excel gerado, o risco de fórmulas de totais (Resumo Financeiro/Início) ignorarem silenciosamente registros além do buffer inicial de linhas — sem impacto em nenhuma regra de negócio documentada aqui, é correção puramente técnica de implementação (ver `13_VERSOES_E_HISTORICO` para o registro da versão V5 do Excel).
**Motivo da Revisão 10 (Etapa 6 — Compras, 2026-09-19):** o responsável pelo projeto homologou o módulo **COMPRAS**: (a) o vínculo Compra→Serviço é opcional, e quando existe alimenta o cálculo de **Variação** (R$ e %, nunca "Desvio"), fechando REG-010 (de [H] para [D]); (b) Planejado = Valor Previsto do Serviço vinculado — vínculos opcionais a Etapa/Subetapa (novos nesta etapa) são só rastreabilidade, não alimentam o cálculo; (c) Planejado ausente ou igual a zero: Variação % é "não calculável" (nunca 0%), mesmo tratamento de REG-031; (d) Compra acima do Planejado não é bloqueada nem corrigida automaticamente, e não altera Orçamento Vigente, Custo Realizado, Saldo de Caixa ou progresso físico — qualquer alteração formal de orçamento continua exclusiva do módulo ALTERAÇÕES; (e) "múltiplos itens" de uma Compra (regra 5 da homologação) são implementados como múltiplos registros `Compra` (mesma granularidade já usada por FINANCEIRO), preservando a aba Excel única "Compras" exigida pela homologação, sem criar uma segunda entidade/aba. Esta revisão reescreve REG-010 (de [H] para [D]). Nenhum domínio fechado foi inventado para Forma de Pagamento, Status de Aprovação ou Status de Entrega — continuam [H]/texto livre. Não implementados nesta revisão (permanecem para etapas futuras): módulo Fornecedores completo (aba própria; é módulo auxiliar, MOD_001); fluxo de aprovação de Compra; domínios fechados de Forma de Pagamento/Status de Aprovação/Status de Entrega.

## Legenda de status

[D] DOCUMENTADO — vem literalmente de fonte já homologada · [P] PROPOSTA — sugestão de regra ainda não homologada · [H] HOMOLOGAR — decisão/threshold em aberto, não definido em nenhuma fonte · [C] CONFLITO — duas fontes/conceitos não conciliados.

**Nenhum threshold numérico foi inventado.** Onde a fonte não define um limite, o campo "Resultado" registra a lacuna e o status é [H].

---

### REG-001 — Identificador único de registro — [D] HOMOLOGADO (corrigido na Revisão 9, 2026-09-19)
- **Descrição:** todo registro de qualquer entidade deve possuir um identificador técnico único e estável.
- **Entrada:** criação de um novo registro em qualquer entidade do DAD_001.
- **Condição:** registro novo, sem ID atribuído.
- **Resultado:** sistema gera um ID único no formato **`PREFIXO-0000`** (3 letras maiúsculas do prefixo da entidade + sequencial de 4 dígitos com zero à esquerda), homologado desde a Etapa 1 (Seção 7, "IDS INTERNOS") e implementado em `config/ids_config.py`/`src/ids/gerador_id.py`. A auditoria pós-Etapa 5 encontrou que REG-001 e a maioria das entidades do DAD_001 ainda marcavam esse formato como [H], apesar de já implementado e em uso consistente — esta revisão corrige a documentação para refletir o que já está homologado e construído, sem alterar o mecanismo de geração.
- **Status:** [D]
- **Teste necessário:** `testes/test_gerador_id.py` (já existente, cobre unicidade, sequencialidade e formato).

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

### REG-004 — Custo Realizado — [D] HOMOLOGADO EM 2026-09-17 (Revisão 7)
- **Descrição:** o Custo Realizado de uma Obra é a soma dos lançamentos de FINANCEIRO do tipo Despesa/Custo vinculados a ela — **independentemente de já terem sido pagos** (ver REG-029 sobre a separação entre reconhecimento do custo e Pagamento).
- **Entrada:** lançamentos de FINANCEIRO do tipo "Despesa/Custo" (REG-030) vinculados à Obra.
- **Condição:** soma de todos os lançamentos do tipo Despesa/Custo registrados na Obra.
- **Resultado (fórmula homologada — Etapa 4, Seção 11/16):** **Custo Realizado = Σ(Valor dos lançamentos do tipo Despesa/Custo).** Não depende de status de pagamento — uma Despesa/Custo lançada e não paga já integra o Custo Realizado (Etapa 4, Seção 11, exemplo explícito: Despesa = 10.000, Pago = 0 → Custo Realizado = 10.000).
- **O que esta decisão NÃO define (permanece [H]):** filtragem por `situacao`/cancelamento (ver REG-023 da Etapa 4 no `DAD_001`, entidade FINANCEIRO) — o domínio de cancelamento não foi homologado nesta rodada; nenhum lançamento é excluído do Custo Realizado por esse campo (ver Etapa 4, Seção 23, e o relatório da Etapa 4, "Pendências").
- **Status:** [D] — fórmula homologada para esta implementação na Etapa 4 (Seções 11/16), substituindo a redação [H] anterior que dependia de uma definição de "confirmado" que nunca foi fixada.
- **Teste necessário:** ver Cenários A–J da homologação da Etapa 4 (`testes/test_financeiro.py`) — cobrem despesa não paga, paga parcialmente, paga totalmente, e a independência do Custo Realizado em relação ao pagamento.

### REG-005 — Saldo Orçamentário — [D] HOMOLOGADO EM 2026-09-17 (Revisão 7)
- **Descrição:** saldo entre o que está disponível para a obra (Orçamento Vigente) e o que foi efetivamente reconhecido como custo.
- **Entrada:** Orçamento Vigente/Disponível (REG-017 — nesta implementação, Orçamento Inicial + Aportes, ver nota em REG-017), Custo Realizado (REG-004).
- **Condição:** sempre calculado; não é um campo editável manualmente.
- **Resultado (fórmula homologada — Etapa 4, Seção 5):** **Saldo Orçamentário = Orçamento Vigente − Custo Realizado.**
- **Regra de não bloqueio (Etapa 4, Seções 2/5, REG-032):** o Saldo Orçamentário **pode ser negativo** (estouro de orçamento) — isso não bloqueia nenhum lançamento nem é corrigido automaticamente; o sistema apenas informa a situação (ver REG-032).
- **Status:** [D] — fórmula homologada para esta implementação na Etapa 4; a subtração passa de proposta ([P], Revisão 1/2) para homologada, com o termo de comparação correto (Orçamento Vigente, não o Orçamento Previsto isolado) já resolvido desde a Revisão 2 (REG-017).
- **Teste necessário:** ver Cenários A, C, F e J da homologação da Etapa 4 (`testes/test_financeiro.py`) — cobrem saldo positivo, saldo após despesa não paga, estouro (saldo negativo) e orçamento zero.

### REG-006 — Vínculo entre Aporte e Orçamento (Opção B) — [D] CONFLITO RESOLVIDO EM 2026-09-16
- **Decisão homologada pelo responsável pelo projeto:** **Opção B — Vincular Aporte ao Orçamento.** Substitui o registro de conflito [C] da Revisão 1 deste documento.
- **Descrição:** todo aporte financeiro destinado à obra representa entrada de recurso para a obra e aumenta o Orçamento Vigente/Disponível da obra (REG-017). O aporte **não** é tratado como despesa, custo executado ou medição.
- **Entrada:** lançamento em FINANCEIRO do tipo "Aporte", vinculado à Obra, com valor, data e origem.
- **Condição:** lançamento de Aporte confirmado.
- **Resultado:** o valor do aporte é somado ao Orçamento Vigente/Disponível da Obra (ver fórmula em REG-017). O aporte permanece registrado individualmente em FINANCEIRO (não é absorvido/apagado ao alimentar o orçamento) — não se cria uma segunda fonte de verdade para o orçamento: o Orçamento Vigente é sempre recalculado a partir de FINANCEIRO (aportes) e ALTERAÇÕES (impacto orçamentário aprovado), nunca editado diretamente.
- **O que esta decisão NÃO define (permanece [H]):** thresholds; fluxo de aprovação do próprio aporte (se há aprovação necessária para registrar um aporte).
- **Nota da Revisão 7 (Etapa 4, Seção 8):** o domínio "Tipo" desta regra, antes parcial (só Aporte/Despesa), foi **fechado** em 2026-09-17 com 4 valores: Aporte, Outras Entradas, Despesa/Custo, Outras Saídas — ver REG-030 (novo). A fórmula do Saldo de Caixa, antes [H], também foi homologada — ver REG-018 (Revisão 7).
- **Status:** [D] — decisão homologada pelo responsável pelo projeto em 2026-09-16; domínio "Tipo" completado em 2026-09-17 (REG-030).
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

### REG-010 — Compra vinculada a orçamento (Variação) — [D] HOMOLOGADO EM 2026-09-19 (Etapa 6)
- **Descrição:** o vínculo entre uma Compra e um Serviço/Orçamento é **opcional**, não obrigatório — quando existe, permite comparar o valor comprado com o valor orçado (Planejado) através do conceito de **Variação** (nunca "Desvio").
- **Entrada:** registro de nova Compra; `id_servico` opcional.
- **Condição:** Compra com ou sem vínculo a um Serviço; Compra cujo valor ultrapassa o Planejado do serviço vinculado.
- **Resultado (domínio homologado — Etapa 6, prompt "ETAPA 6 — COMPRAS", Seção 5):**
  - **Planejado** = Valor Previsto (REG-026) do Serviço vinculado à Compra via `id_servico`. Sem `id_servico`, não há Planejado — Variação não é calculável (`None`, nunca 0). Os vínculos opcionais e independentes a Etapa/Subetapa (regra 6 da homologação) são puramente informativos/de rastreabilidade e **não** alimentam este cálculo — decisão de design explícita para não inventar qual total usar (Etapas!Total Previsto ou Subetapas!Total Previsto) quando só esses níveis estão vinculados.
  - **Variação R$ = Compra (Valor) − Planejado** (regra 15).
  - **Variação % = Variação R$ / Planejado × 100** (regra 16).
  - **Planejado = 0 ou ausente (regra 17):** Variação % retorna "não calculável" (`None`/"N/D" no Excel) — mesmo tratamento já homologado para divisão por zero em `percentual_orcamento_consumido` (REG-031); nunca 0%. Variação R$ com Planejado = 0 continua calculável normalmente (é uma subtração, não uma divisão).
  - **Uma Compra cujo valor ultrapassa o Planejado NÃO é bloqueada, alertada automaticamente ou corrigida** (regras 10/19/20 — mesmo princípio "o sistema informa, o Operador decide" já usado em REG-032, Estouro de Orçamento).
  - **Compra NÃO altera automaticamente** o Orçamento Vigente/Disponível, o Custo Realizado, o Saldo de Caixa nem o progresso físico (regras 2/7/8/9/11/18) — qualquer alteração formal de orçamento decorrente de uma Compra deve passar pelo módulo ALTERAÇÕES, seguindo seu fluxo já homologado (REG-012/REG-017), nunca automaticamente.
- **O que esta decisão NÃO define (permanece [H]):** domínio fechado de Forma de Pagamento, Status de Aprovação (fluxo de aprovação) e Status de Entrega — continuam texto livre, exatamente como já registrado em DAD_001; nenhum domínio foi inventado nesta rodada.
- **Status:** [D] — Variação R$/%, tratamento de Planejado ausente/zero, e as decisões de não-automação, homologadas pelo responsável pelo projeto em 2026-09-19.
- **Teste necessário:** ver `testes/test_compras.py` e `testes/test_excel_compras.py` (Etapa 6).

### REG-011 — Prazo de Pendência (SLA)
- **Descrição:** toda Pendência deveria ter um prazo de resolução esperado.
- **Entrada:** Data de Abertura da Pendência.
- **Condição:** tempo decorrido desde a abertura.
- **Resultado:** **SLA em dias não definido em nenhuma fonte.**
- **Status:** [H]
- **Teste necessário:** depende do SLA homologado.

### REG-012 — Aprovação de Alteração — [D] HOMOLOGADO EM 2026-09-17 (Revisão 8), CORRIGIDO EM 2026-09-19 (Revisão 9)
- **Descrição:** uma Alteração de escopo, prazo ou orçamento possui um Status de Aprovação que determina se ela impacta os indicadores da Obra — sem workflow multi-etapa: o Operador seleciona o Status diretamente.
- **Entrada:** registro de nova Alteração; Status de Aprovação selecionado pelo Operador.
- **Condição:** Alteração criada ou com Status alterado pelo Operador.
- **Resultado (domínio fechado homologado — corrigido na Revisão 9, 2026-09-19):** **Em análise, Aprovada, Rejeitada, Cancelada.** Nenhum outro valor é válido. (A Revisão 8 havia registrado só 3 valores — Pendente/Aprovada/Rejeitada, sem "Cancelada"; a auditoria pós-Etapa 5 identificou a divergência e o responsável pelo projeto corrigiu o domínio para 4 valores.) Apenas Alterações com Status **Aprovada** entram no cálculo do Orçamento Vigente (REG-017) — Em análise, Rejeitada e Cancelada permanecem visíveis na base, nunca apagadas (mesmo princípio de não-exclusão automática já usado em REG-027, Status do Serviço).
- **Decisão explícita sobre o fluxo (Etapa 5, decisão homologada pelo responsável pelo projeto):** **não existe fluxo de aprovação com múltiplas etapas, aprovador distinto do Operador, ou aprovação automática por valor.** O campo Status de Aprovação é uma seleção manual e direta — mesmo princípio "sistema informa, Operador decide" já usado no Financeiro (REG-032). Nenhuma justificativa é exigida para aprovar, rejeitar ou cancelar.
- **O que esta decisão NÃO define (permanece [H]):** se, no futuro, uma camada de Perfis/Acesso deverá restringir quem pode alterar o Status de Aprovação (hoje qualquer Operador pode) — não tratado nesta rodada, mesma pendência já registrada para o Ajuste Manual de Orçamento (REG-026) e para o indicador de Estouro (REG-032). Também não definido: diferença semântica entre "Rejeitada" (decisão do Operador sobre o mérito) e "Cancelada" (desistência/obsolescência do pedido) — ambas têm hoje exatamente o mesmo efeito (fora do Orçamento Vigente, nunca apagada); qualquer distinção adicional de tratamento entre elas é [H].
- **Status:** [D] — domínio de 4 valores homologado pelo responsável pelo projeto em 2026-09-19 (Revisão 9).
- **Teste necessário:** ver `testes/test_alteracoes.py` — cobre os 4 valores do domínio e a exclusão de Em análise/Rejeitada/Cancelada do Orçamento Vigente.

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
- **Status:** [D] — fórmula homologada pelo responsável pelo projeto em 2026-09-16 (Opção B); **completamente implementada a partir da Revisão 8.**
- **Nota da Revisão 8 (Etapa 5, 2026-09-17):** a parcela de Alterações Formais Aprovadas foi implementada — `src/alteracoes/calculos.py:total_alteracoes_aprovadas` (soma apenas Alterações com Status = Aprovada, REG-012) + `src/financeiro/calculos.py:orcamento_vigente` (agora soma as 3 parcelas). **REG-017 está, a partir desta revisão, completamente implementado** — as 3 parcelas da fórmula homologada em 2026-09-16 somam de fato, em Python e em Excel (aba Resumo Financeiro, linha "Orçamento Vigente" = `=Orçamento Inicial + Aportes + Alterações Aprovadas`). Validado com dados reais em Excel (não apenas texto de fórmula): Orçamento Inicial 100.000 + Aporte 20.000 + Alteração Aprovada 15.000 = Orçamento Vigente 135.000, com uma segunda Alteração (Pendente, 99.999) corretamente excluída da soma.
- **Nota histórica da Revisão 7 (Etapa 4):** entre a Revisão 7 e a Revisão 8, apenas a parcela Orçamento Inicial + Aportes estava implementada — a parcela de Alterações ficava preparada, mas não funcional, porque o módulo ALTERAÇÕES ainda não existia.
- **Teste necessário:** ver `testes/test_alteracoes.py` (Etapa 5) — cobre a soma das 3 parcelas, Alterações Pendentes/Rejeitadas excluídas, e Impacto no Orçamento negativo reduzindo a soma.

### REG-018 — Saldo de Caixa — [D] HOMOLOGADO EM 2026-09-17 (Revisão 7)
- **Descrição:** indicador de disponibilidade efetiva de caixa (recursos financeiros recebidos e não gastos), distinto do Saldo Orçamentário (REG-005), que compara orçamento disponível × custo reconhecido independentemente do status de pagamento (Etapa 4, Seções 3/15/16 — "NÃO confundir ORÇAMENTO com CAIXA").
- **Entrada:** Σ Aportes, Σ Outras Entradas (REG-030), Σ Pagamentos (REG-029), Σ Outras Saídas (REG-030).
- **Condição:** sempre calculado; não é um campo editável manualmente.
- **Resultado (fórmula homologada — Etapa 4, Seção 15):**
  **Saldo de Caixa = (Aportes + Outras Entradas) − (Pagamentos + Outras Saídas).**
  Entradas = Aportes + Outras Entradas. Saídas = Pagamentos + Outras Saídas — **nunca** a Despesa/Custo em si (Seção 16: "o reconhecimento de uma Despesa/Custo NÃO deve reduzir o Caixa automaticamente se nenhum pagamento tiver sido registrado").
- **Status:** [D] — fórmula homologada pelo responsável pelo projeto em 2026-09-17, resolvendo a lacuna que a Revisão 2 havia deliberadamente deixado [H].
- **Teste necessário:** ver Cenários C, G, H e I da homologação da Etapa 4 (`testes/test_financeiro.py`) — cobrem despesa não paga (Caixa não reduz), Outras Entradas, Outras Saídas e a combinação de Pagamento + Outras Saídas.

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

### REG-029 — Pagamento e A Pagar (separação Custo Realizado × Pagamento) — [D] HOMOLOGADO EM 2026-09-17
- **Descrição:** o reconhecimento de uma Despesa/Custo (REG-004) é conceitualmente distinto de sua baixa financeira (Pagamento) — Etapa 4, Seção 20: "separar claramente MOVIMENTO FINANCEIRO de PAGAMENTO". Uma Despesa/Custo pode não estar paga, estar parcialmente paga ou totalmente paga; um mesmo lançamento pode ter múltiplos Pagamentos.
- **Entrada:** Valor do lançamento FINANCEIRO do tipo Despesa/Custo (Custo Reconhecido); Σ Valor de todos os Pagamentos vinculados a esse lançamento (Total Pago).
- **Condição:** todo lançamento do tipo Despesa/Custo pode ter zero, um ou múltiplos Pagamentos (parciais e/ou totais) associados.
- **Resultado (fórmula homologada — Etapa 4, Seção 14):** **A Pagar = Custo Reconhecido − Total Pago.**
- **Regra de integridade técnica (não é regra de negócio nova, é proteção estrutural — mesmo padrão de REG-019):** um registro de PAGAMENTOS só pode referenciar um lançamento de FINANCEIRO do tipo Despesa/Custo — não existe "pagamento" de um Aporte, de Outras Entradas ou de Outras Saídas, por definição dos próprios conceitos (Seção 3: "NÃO confundir CUSTO REALIZADO com PAGAMENTO").
- **Autonomia do Operador (Seção 22):** nenhum bloqueio de exclusão/edição de Pagamento foi criado por já existir um pagamento associado a um custo — essa função de edição/exclusão em si ainda não foi implementada em nenhuma camada (Etapas 1–4), não é uma restrição nova desta regra.
- **Sobrepagamento (registrado na auditoria pós-Etapa 5, Revisão 9, 2026-09-19) — [H]:** o que deve acontecer quando o Total Pago de um lançamento ultrapassa o Custo Reconhecido (A Pagar ficaria negativo) **não está definido em nenhuma fonte homologada.** Hoje o sistema não bloqueia, não alerta e não limita esse caso — `A Pagar` simplesmente fica negativo (`src/financeiro/calculos.py`). Esta lacuna foi encontrada e registrada, não resolvida — nenhuma regra foi inventada. Opções técnicas em aberto para o responsável decidir: (a) permitir e manter A Pagar negativo (comportamento atual, sem indicador); (b) bloquear o registro do Pagamento que ultrapassaria o Custo Reconhecido; (c) permitir mas sinalizar como alerta (mesmo princípio "sistema informa, Operador decide" de REG-032); (d) saturar A Pagar em zero, mantendo o excedente apenas como informação auxiliar.
- **Status:** [D] para a fórmula e separação conceitual (homologadas em 2026-09-17); **[H] para o caso de sobrepagamento** (Revisão 9).
- **Teste necessário:** ver Cenários D, E e I da homologação da Etapa 4 (`testes/test_financeiro.py`) — pagamento parcial, pagamento total e custo com pagamento parcial. Teste de sobrepagamento só pode ser escrito após a decisão de negócio acima.

### REG-030 — Tipos de Movimentação Financeira (domínio fechado) — [D] HOMOLOGADO EM 2026-09-17
- **Descrição:** domínio fechado do campo "Tipo" da entidade FINANCEIRO, fechando o que a Revisão 1 (REG-006) havia deixado parcial (só Aporte/Despesa).
- **Entrada:** Tipo atribuído a um lançamento de FINANCEIRO.
- **Condição:** sempre que um lançamento de FINANCEIRO é criado.
- **Resultado (domínio fechado homologado — Etapa 4, Seção 8):** **Aporte, Outras Entradas, Despesa/Custo, Outras Saídas.** Nenhum outro valor é válido nesta rodada ("não criar outros tipos nesta etapa sem homologação").
- **Comportamento de cada tipo (Seções 9/10/11/12, já refletido em REG-004/REG-006/REG-017/REG-018):**
  | Tipo | Aumenta Orçamento Vigente? | É Custo Realizado? | Efeito no Caixa |
  |---|---|---|---|
  | Aporte | Sim | Não | Entra no Caixa no lançamento |
  | Outras Entradas | Não | Não | Entra no Caixa no lançamento |
  | Despesa/Custo | Não | Sim | Só via Pagamento (REG-029) — nunca no reconhecimento |
  | Outras Saídas | Não | Não | Reduz o Caixa no lançamento |
- **Status:** [D] — domínio fechado homologado pelo responsável pelo projeto em 2026-09-17.
- **Teste necessário:** teste unitário por tipo (os 4 valores) verificando o efeito correto em Orçamento Vigente/Custo Realizado/Caixa — ver `testes/test_financeiro.py`.

### REG-031 — % Orçamento Consumido e Tratamento de Divisão por Zero — [D] HOMOLOGADO EM 2026-09-17
- **Descrição:** percentual do Orçamento Vigente já consumido pelo Custo Realizado.
- **Entrada:** Custo Realizado (REG-004), Orçamento Vigente (REG-017).
- **Condição:** sempre calculado.
- **Resultado (fórmula homologada — Etapa 4, Seção 6):** **% Orçamento Consumido = Custo Realizado / Orçamento Vigente × 100.** Pode ultrapassar 100% (estouro) — nunca é limitado artificialmente (ver REG-032).
- **Divisão por zero (Etapa 4, Seção 7):** quando o Orçamento Vigente é zero, o resultado é **"não calculável"** — representado como `None` em Python e como o texto `"N/D"` na fórmula Excel (`IF(OrçamentoVigente=0,"N/D",...)`) — **nunca como 0%**, que seria uma leitura inválida de uma divisão por zero.
- **Status:** [D] — fórmula e tratamento de divisão por zero homologados pelo responsável pelo projeto em 2026-09-17.
- **Teste necessário:** ver Cenários A, F e J da homologação da Etapa 4 (`testes/test_financeiro.py`) — 0% válido, estouro (>100%) e orçamento zero ("não calculável").

### REG-032 — Estouro de Orçamento Não Bloqueia — [D] HOMOLOGADO EM 2026-09-17
- **Descrição:** princípio fundamental do módulo Financeiro (Etapa 4, Seção 2): "o sistema informa, o Operador decide". Nenhum lançamento é impedido por causar ou ampliar um estouro de orçamento.
- **Entrada:** Saldo Orçamentário (REG-005).
- **Condição:** Custo Realizado > Orçamento Vigente (Saldo Orçamentário < 0).
- **Resultado (homologado — Etapa 4, Seções 2/29):** o lançamento **continua permitido**; o Saldo Orçamentário pode ficar negativo; o % Consumido pode ultrapassar 100% (REG-031); o sistema apenas **informa** a situação (indicador textual, sem cor/formatação condicional — mesmo princípio de REG-028/Etapa 3 Seção 31) — nunca bloqueia, apaga ou corrige automaticamente o lançamento.
- **Visibilidade do indicador (Etapa 4, Seções 29/30):** o indicador de estouro é **Operador-only** por especificação explícita — o Cliente não deve ter acesso a ele. **Esta regra de visibilidade por perfil ainda não é tecnicamente aplicada** — não existe, em nenhuma etapa construída até aqui, um mecanismo de restrição de acesso por perfil no Excel (SEC_001, Seção 4, permanece [H]; ver AGENTS.md §9, "Perfis e Acesso" como camada transversal ainda não implementada). Registrado como pendência explícita, não como omissão.
- **Status:** [D] (princípio de não bloqueio; indicador textual sem cor/formatação condicional) / [H] (mecanismo técnico de restrição de visibilidade por perfil, herdado de SEC_001).
- **Teste necessário:** ver Cenário F da homologação da Etapa 4 (`testes/test_financeiro.py`) — lançamento de despesa que ultrapassa o orçamento não levanta exceção; teste de que nenhuma formatação condicional foi criada na aba Resumo Financeiro (`testes/test_excel_financeiro.py`).

### Nota de Implementação — Etapa 7 (2026-09-23, Execução/Medições — Progresso Físico)

REG-007, REG-008, REG-019, REG-020, REG-021, REG-022, REG-023, REG-024 e REG-025 — todas já **[D] HOMOLOGADAS** desde 2026-09-16 (Revisões 4/5) — foram **implementadas em código** nesta etapa (`src/execucao/calculos.py`, `testes/test_execucao.py`, aba Excel "Execução" + colunas novas em "Serviços"). Nenhuma delas foi reaberta ou alterada em conteúdo; apenas construídas. Decisões de implementação necessárias (documentadas em `relatorios/PLANO_ETAPA_7_EXECUCAO_V1.md`, Seção 5, e não regras de negócio novas):
- REG-022 (domínios fechados de elegibilidade em casos-limite): resolvido usando o mesmo domínio já homologado `StatusServico.integra_orcamento_corrente` (Etapa 3).
- REG-024 (fórmula técnica exata da redistribuição proporcional): implementada como proporcional ao Peso Automático Bruto de cada Serviço automático entre si.
- REG-020 (fórmula técnica de exibição do % isolado por Subetapa/Etapa): **permanece [H], não implementada** — expostos em vez disso "Peso Consolidado"/"Contribuição na Obra" (valores de grupo diretos, não um percentual isolado inventado).
- REG-009 (limite de lançamento de medição, bloqueio vs. alerta — ainda [P]/[H] em conteúdo): resolvida na implementação por precedente do princípio já homologado em REG-010/REG-032 ("o sistema informa, o Operador decide") — medição acima de 100% não é bloqueada.
- REG-008 (campos técnicos de rastreabilidade do ajuste manual): `ServicoOrcamento.peso_ajustado`/`peso_automatico_original` (já existentes desde a Etapa 1) passam a ser efetivamente lidos/calculados — nenhum campo novo foi criado.

### Nota de Implementação — Etapa 8 (2026-09-23, Planejamento / Cronograma da Obra)

Construído o módulo de cronograma. **Nenhuma regra existente foi reaberta ou alterada em conteúdo**, e nenhum threshold, alerta ou classificação foi inventado. **Nenhuma regra de negócio nova permanece em vigor** — ver o registro da regra rejeitada abaixo.

**Conflito estrutural encontrado e resolvido (ver `DAD_001`, Revisão 12):** as datas do cronograma estavam modeladas em dois lugares (campos próprios de ETAPAS **e** entidade PLANEJAMENTO, com "1 Etapa → N Planejamento" sem significado definido), enquanto SUBETAPAS não tinha nenhum campo de data. **Decisão homologada pelo responsável do projeto em 2026-09-23 (Opção A):** as datas moram nas próprias ETAPAS/SUBETAPAS (fonte de verdade única); PLANEJAMENTO fica reservada, sem uso como tabela.

Cálculos implementados (`src/modelo/entidades.py` como `@property` de `Etapa`/`Subetapa`; consolidação de Obra em `src/planejamento/calculos.py`; colunas calculadas nas abas Excel "Etapas"/"Subetapas" e cronograma consolidado na aba "Início"):
- **Duração Prevista (dias)** = Data Fim Prevista − Data Início Prevista.
- **Duração Real (dias)** = Data Fim Real − Data Início Real.
- **Variação de Prazo (dias)** = Data Fim Real − Data Fim Prevista.
- **Consolidação da Obra:** menor Data Início Prevista e maior Data Fim Prevista das Etapas. Valores **derivados e rotulados como tal** — não sobrescrevem as datas declaradas da própria OBRA (REG-032).

**INDICADOR REJEITADO E REMOVIDO — "Variação de Prazo da Obra" (decisão do responsável do projeto, 2026-09-23, Alternativa D1).**
- **O que era:** um indicador consolidado no nível da Obra, criado durante a Etapa 8, calculado como `MAX(Fim Real) − MAX(Fim Previsto)` das Etapas. Junto dele existia uma regra de supressão (então chamada "Regra 8.1") que o ocultava enquanto a Obra estivesse em andamento.
- **Por que foi removido:** **não havia regra de negócio homologada que definisse seu significado** — nem o que torna "a Obra como um todo" atrasada. Além disso, o cálculo era defeituoso: `MAX(Fim Previsto)` é sempre o fim previsto da Obra, mas `MAX(Fim Real)` só é o fim real da Obra quando todas as Etapas previstas terminaram — antes disso é apenas "a última data concluída até agora". Os dois operandos podiam vir de **Etapas diferentes**. Numa Obra com a Fundação concluída em 10/05 e a Alvenaria prevista para 31/08 ainda em execução, a conta dava −113 dias, lido como "113 dias de **antecipação**" numa obra **atrasada**.
- **Decisão homologada:** remover o indicador. **Não** foi criada regra nova para determinar quando a Obra está atrasada, **nem** o indicador foi redefinido para "Etapas concluídas". A regra de supressão foi removida junto — ela não existe mais e **não tem mais classificação [H]**, por não ser mais uma regra do sistema.
- **Onde a informação de prazo permanece:** **Variação de Prazo por Etapa e por Subetapa** (`Etapa.variacao_prazo_dias` / `Subetapa.variacao_prazo_dias`), níveis em que o indicador tem significado direto e já definido, com os dois operandos sempre do mesmo registro. As **datas consolidadas da Obra** (menor Início Previsto / maior Fim Previsto) continuam existindo normalmente.
- **Removidos do código:** `variacao_prazo_obra_dias`, `duracao_real_obra_dias` (mesma fragilidade de operando) e `ha_etapa_prevista_nao_concluida` (predicado que existia só para a supressão), além da célula correspondente na aba Início. **Não recriar sem homologação prévia da regra de negócio.**
- **Regressão preservada:** o cenário dos −113 dias permanece na suíte (`test_cenario3_nenhuma_funcao_produz_o_resultado_enganoso_de_113_dias`), agora com a finalidade de provar que nenhuma função produz o número enganoso, que a Etapa concluída reporta corretamente a sua própria variação, e que a Etapa em andamento não gera variação consolidada alguma.

Decisões de implementação (não são regras de negócio novas):
- **Subtração pura de datas**, sem `+1` de contagem inclusiva — duas datas iguais dão 0 dias. Nenhuma fonte define contagem inclusiva; a subtração pura é a mesma operação de REG-005/REG-010/REG-028. Contagem inclusiva, se desejada, é item de homologação.
- **Convenção de sinal:** Variação de Prazo positiva = atraso, negativa = antecipação — a mesma já homologada em ALTERAÇÕES/"Impacto no Prazo" (Etapa 5).
- **Ausência de data = "não calculável"** (`None`/célula vazia), nunca 0 nem uma data inventada — mesmo princípio de REG-031/REG-010.
- **Datas invertidas ou duração negativa não são bloqueadas** — o sistema informa, o Operador decide (REG-032/REG-010).

**REG-014 — Alerta de Atraso de Cronograma: permanece integralmente [H], não implementado.** O texto da própria regra diz "Resultado: não definido" e o threshold de dias nunca foi homologado. A Variação de Prazo é exposta como **número simples, sem cor, ícone ou classificação** — mesmo tratamento dado à Variação de REG-028 (Etapa 3) e à ausência de alertas na Etapa 7. Por dependerem desse threshold, também permanecem [H] e não implementados: o campo calculado "Status do Prazo" (DAD_001/PLANEJAMENTO) e a lógica de encadeamento/dependência entre Etapas (tipo Gantt).

---

## Regras citadas na tarefa sem informação suficiente para formalizar

- **Aportes:** **[C] RESOLVIDO em 2026-09-16** — ver REG-006 (vínculo Aporte × Orçamento, Opção B homologada) e REG-017 (fórmula do Orçamento Vigente/Disponível — parcela Orçamento Inicial + Aportes implementada na Etapa 4; parcela de Alterações Aprovadas permanece [H]). O conceito de Saldo de Caixa citado junto com Aportes na Revisão 1 **[D] HOMOLOGADO em 2026-09-17** — ver REG-018 (Revisão 7). A partir da Revisão 4, ver também REG-021 (aporte não altera peso físico automaticamente).
- **Financeiro (Custo Realizado, Pagamentos, Saldo de Caixa, tipos de movimentação):** **[D] HOMOLOGADO em 2026-09-17 (Revisão 7)** — ver REG-004 (Custo Realizado), REG-005 (Saldo Orçamentário), REG-018 (Saldo de Caixa), REG-029 (Pagamento/A Pagar), REG-030 (4 tipos de movimentação), REG-031 (% Consumido/divisão por zero) e REG-032 (estouro não bloqueia). Permanecem [H]/fora de escopo: domínio de cancelamento/situação de FINANCEIRO (Seção 23); mecanismo técnico de restrição de visibilidade por perfil (REG-032, Operador-only).
- **Alterações (Status de Aprovação, Tipo de Alteração, Orçamento Vigente completo):** **[D] HOMOLOGADO em 2026-09-17 (Revisão 8)** — ver REG-012 (Aprovação de Alteração, domínio fechado, sem workflow) e a nota da Revisão 8 em REG-017 (Orçamento Vigente completamente implementado). Permanecem [H]/fora de escopo: automação Escopo→Serviços/Orçamento; integração com Planejamento/Cronograma; restrição de perfil sobre aprovação.
- **Pesos:** **[D] amplamente HOMOLOGADO em 2026-09-16 (Revisões 4 e 5)** — ver REG-008 (peso automático global a partir do valor orçado, sem renormalização por nível), REG-020 (uso do peso na consolidação hierárquica), REG-022 (elegibilidade), REG-023 (proteção do peso manual), REG-024 (redistribuição proporcional entre automáticos) e REG-025 (bloqueio quando todos os pesos são manuais). Permanecem [H]: campos técnicos definitivos de rastreabilidade do ajuste manual (REG-008), domínios fechados que operacionalizam a elegibilidade (REG-022) e fórmula técnica exata da redistribuição proporcional (REG-024).
- **Método de execução do Serviço:** **[D] HOMOLOGADO em 2026-09-16 (Revisão 5)** — ver REG-007 (fórmula do método quantitativo e tabela fechada do método por status: Pendente 0% / Em andamento 50% / Concluído 100%). Permanecem [H]: lista de serviços por método, arredondamento/tolerância, tratamento de excedente e de quantidade planejada zero.
- **Medições — periodicidade:** ver DAD_001 (entidade EXECUÇÃO/MEDIÇÕES) — não definida.
- **Cronograma — onde moram as datas (ETAPAS × entidade PLANEJAMENTO):** **[C] RESOLVIDO em 2026-09-23 (Etapa 8, Opção A)** — as datas moram nas próprias ETAPAS/SUBETAPAS (fonte de verdade única); PLANEJAMENTO fica reservada, sem uso como tabela. Ver `DAD_001` Revisão 12 e a Nota de Implementação — Etapa 8 acima. Permanecem [H]: threshold de atraso (REG-014), "Status do Prazo", encadeamento tipo Gantt e o significado do "N" de "1 Etapa → N Planejamento".
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

## Registro de homologação — Revisão 7

Em 2026-09-17, o responsável pelo projeto homologou o módulo **FINANCEIRO** (Etapa 4 de construção), registrado em:
- **REG-004 (reescrita)** — Custo Realizado = Σ Valor dos lançamentos do tipo Despesa/Custo, independentemente de pagamento;
- **REG-005 (reescrita)** — Saldo Orçamentário = Orçamento Vigente − Custo Realizado, podendo ser negativo, sem bloqueio (ver REG-032);
- **REG-006 (nota)** — domínio "Tipo" completado com 4 valores (ver REG-030);
- **REG-017 (nota)** — apenas a parcela Orçamento Inicial + Aportes está implementada nesta etapa; Alterações Formais Aprovadas permanecem [H]/fora de escopo;
- **REG-018 (reescrita)** — Saldo de Caixa = (Aportes + Outras Entradas) − (Pagamentos + Outras Saídas), resolvendo a lacuna [H] da Revisão 2;
- **REG-029 (nova)** — separação Custo Realizado × Pagamento; A Pagar = Custo Reconhecido − Total Pago; N pagamentos parciais/totais por lançamento;
- **REG-030 (nova)** — domínio fechado do Tipo de FINANCEIRO: Aporte, Outras Entradas, Despesa/Custo, Outras Saídas;
- **REG-031 (nova)** — % Orçamento Consumido = Custo Realizado / Orçamento Vigente × 100, sem limite de 100%; divisão por zero tratada como "não calculável" (nunca 0%);
- **REG-032 (nova)** — estouro de orçamento não bloqueia nenhum lançamento; indicador é Operador-only por especificação (mecanismo técnico de restrição por perfil permanece [H]).

**Preservado, não reaberto:** todas as decisões das Revisões 1–6 (Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia oficial; Modelo Híbrido de progresso físico; Valor Previsto/Status do Serviço/Variação do Orçamento da Etapa 3). **Permanecem [H]/fora de escopo, não inventados nesta rodada:** domínio fechado de `situacao`/cancelamento em FINANCEIRO (Etapa 4, Seção 23); mecanismo técnico de restrição de visibilidade por perfil (REG-032, SEC_001); vínculo Aporte→Serviço executável (REG-021, inalterado); Compras e Fornecedores como módulos com interface Excel própria (existem apenas como entidades/FKs opcionais no modelo Python, Etapa 4, Seções 24/25); fluxo de edição/exclusão de lançamentos e pagamentos (Etapa 4, Seção 22 — autonomia do Operador reconhecida, mas a função em si não foi implementada em nenhuma camada até esta etapa).

## Registro de homologação — Revisão 8

Em 2026-09-17, o responsável pelo projeto homologou o módulo **ALTERAÇÕES** (Etapa 5 de construção), registrado em:
- **REG-012 (reescrita)** — domínio fechado do Status de Aprovação (Pendente/Aprovada/Rejeitada), sem workflow multi-etapa — o Operador seleciona o Status diretamente;
- **REG-017 (nota da Revisão 8)** — a parcela de Alterações Formais Aprovadas foi implementada; REG-017 está completamente implementado (3 parcelas), validado com dados reais recalculados em Excel;
- **Domínio fechado do Tipo de Alteração** (Escopo/Prazo/Orçamento) — registrado na entidade ALTERAÇÕES do `DAD_001` (Revisão 8), sem REG numerado próprio por não introduzir fórmula nova além da já registrada em REG-017.

**Decisão explícita de não-automação:** uma Alteração de Escopo não dispara nenhuma mudança automática em SERVIÇOS/ORÇAMENTO — fica apenas registrada informativamente, mesmo princípio já usado para Compra→Financeiro (Etapa 4, Seção 25: "não criar automação").

**Preservado, não reaberto:** todas as decisões das Revisões 1–7 (Aporte × Orçamento = Opção B; SUBETAPAS como entidade própria; hierarquia oficial; Modelo Híbrido de progresso físico; Valor Previsto/Status do Serviço/Variação do Orçamento da Etapa 3; domínio de Financeiro/Pagamentos/Saldo de Caixa/Estouro da Etapa 4). **Permanecem [H]/fora de escopo, não inventados nesta rodada:** domínio fechado de `situacao`/cancelamento em FINANCEIRO (Etapa 4, Seção 23); mecanismo técnico de restrição de visibilidade por perfil (REG-032, SEC_001) — inclusive sobre quem pode aprovar/rejeitar uma Alteração; automação Escopo→Serviços/Orçamento; integração de "Impacto no Prazo" com um módulo de Planejamento/Cronograma (ainda não construído); Compras e Fornecedores como módulos com interface Excel própria; fluxo de edição/exclusão de lançamentos, pagamentos e alterações.

## Registro de homologação — Revisão 9

Em 2026-09-19, uma auditoria técnica completa do estado pós-Etapa 5 ("ETAPA 5.1 — Correções Pós-Auditoria") encontrou uma divergência entre o domínio de Status de Aprovação registrado na Revisão 8 e a decisão pretendida pelo responsável pelo projeto, e uma documentação desatualizada sobre o formato de ID. O responsável pelo projeto corrigiu formalmente:
- **REG-012 (corrigida)** — domínio fechado do Status de Aprovação passa de 3 para **4 valores: Em análise, Aprovada, Rejeitada, Cancelada** ("Pendente" renomeado para "Em análise"; "Cancelada" adicionada). Regra de impacto no Orçamento Vigente inalterada: só Aprovada soma.
- **REG-001 (corrigida)** — formato de ID técnico (`PREFIXO-0000`) reconhecido como já homologado desde a Etapa 1 e em uso consistente; documentação estava [H] por desatualização, não por ausência de decisão real.
- **REG-029 (nota adicionada)** — o caso de sobrepagamento (Total Pago > Custo Reconhecido) foi identificado pela auditoria e registrado como **[H]**, sem regra inventada.

**Também corrigido nesta rodada, sem alterar nenhuma regra de negócio:** os ranges fixos de fórmula no Excel gerado (Resumo Financeiro/Início) que ignoravam silenciosamente registros além do buffer inicial de linhas passam a usar referências estruturadas de Tabela Excel, sem teto numérico — ver `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V5.xlsx` e `13_VERSOES_E_HISTORICO`.

**Preservado, não reaberto:** todas as decisões das Revisões 1–8, incluindo Valor Previsto por substituição/Opção C (REG-026) — a auditoria verificou explicitamente que essa regra não tem divergência real entre documentação, código e Excel, e não foi alterada. **Permanecem [H], não inventados nesta rodada:** sobrepagamento (REG-029, acima); domínio de `situacao`/cancelamento em FINANCEIRO; mecanismo técnico de restrição de visibilidade por perfil; vínculo entre abas do Excel por ID técnico em vez de nome/descrição (risco técnico documentado, mitigado nesta rodada apenas por validação de unicidade de nome, sem mudar o mecanismo de vínculo).

## Registro de homologação — Revisão 10

Em 2026-09-19, o responsável pelo projeto homologou o módulo **COMPRAS** ("Etapa 6" de construção), refletido em:
- **REG-010 (reescrita, de [H] para [D])** — vínculo Compra→Serviço opcional; Planejado = Valor Previsto do Serviço vinculado; Variação R$ = Compra − Planejado; Variação % = Variação R$ / Planejado × 100; Planejado ausente/zero → "não calculável" (mesmo tratamento de REG-031); Compra acima do Planejado não bloqueia nem altera automaticamente Orçamento/Financeiro/Execução.
- **Cálculo (não é campo de nenhuma entidade — vive em `src/compras/calculos.py`):** `planejado`, `variacao_reais`, `variacao_percentual`.
- **Modelo de dados (`src/modelo/entidades.py`, `Compra`):** 3 campos novos — `descricao` (obrigatório; preenche uma lacuna do modelo original, que não tinha nenhum campo para "o que foi comprado"), `id_etapa` e `id_subetapa` (opcionais, independentes entre si e de `id_servico` — puramente informativos, não alimentam a Variação). Validação de `valor` não negativo adicionada (`__post_init__`, mesmo padrão de FINANCEIRO/PAGAMENTOS).
- **Decisão de design (não é regra de negócio nova, é interpretação arquitetural):** "múltiplos itens" de uma Compra (Seção 5, regra 5 da homologação) são implementados como múltiplos registros `Compra` — a mesma granularidade "1 linha = 1 registro" já usada por FINANCEIRO —, preservando a aba Excel única "Compras" exigida pela homologação (Seção 8: "não criar outra nomenclatura concorrente"), sem introduzir uma segunda entidade/aba "Itens de Compra".

**Preservado, não reaberto:** todas as decisões das Revisões 1–9. **Permanecem [H], não inventados nesta rodada:** Forma de Pagamento, Status de Aprovação (fluxo) e Status de Entrega de COMPRAS (continuam texto livre, exatamente como já registrado em DAD_001); módulo Fornecedores completo com aba/interface própria (é módulo auxiliar — MOD_001; nesta etapa, Fornecedor aparece em Compras como texto simples, sem dropdown validado contra uma base que ainda não existe); sobrepagamento (REG-029); domínio de `situacao`/cancelamento em FINANCEIRO; mecanismo técnico de restrição de visibilidade por perfil.
