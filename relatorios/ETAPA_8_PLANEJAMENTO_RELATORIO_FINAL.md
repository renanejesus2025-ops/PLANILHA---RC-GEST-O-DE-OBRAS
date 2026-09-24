# RELATÓRIO FINAL — ETAPA 8 — PLANEJAMENTO / CRONOGRAMA DA OBRA
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-23
**Checkpoint de partida:** `a953acc` — ETAPA 7 concluída (277/277 testes, working tree limpo).
**Estado na entrega:** 325/325 testes passando. **Nenhum commit, nenhum push.**

---

## 1. Etapa identificada

**Planejamento / Cronograma da Obra.** Determinada documentalmente (nenhuma fonte cita "Etapa 8"): dos dois módulos do Núcleo V1 ainda não construídos — Planejamento e Pendências — só Planejamento tinha campos centrais construíveis sem inventar regra. Pendências continua bloqueada por três decisões de negócio indefinidas em todas as fontes (SLA/REG-011, domínio de Status, critério de Prioridade).

## 2. Decisão de negócio levada à homologação (não prevista no plano)

O plano concluíra que não havia decisão pendente. Ao abrir o `DAD_001` campo a campo durante a implementação, encontrou-se uma **duplicidade estrutural**: as datas do cronograma estavam modeladas em dois lugares — campos próprios de **ETAPAS** (desde a Revisão 1, presentes no código desde a Etapa 1, nunca expostos) **e** a entidade separada **PLANEJAMENTO** ("1 Etapa → N Planejamento", com o "N" sem significado definido) — enquanto **SUBETAPAS não tinha nenhum campo de data**, apesar de `UI_001` prometer a tela com "datas previstas e reais das Etapas/**Subetapas**".

Nenhuma fonte definia a fonte de verdade. Verificados sem resposta: `DAD_001`, `UI_001`, `REG_001`, `SEC_001`, `MOD_001`, `AGENTS.md`, Documentação Mestra corrente e histórica, e os três documentos históricos de Planejamento (`MOD_004`, `DAD_005`, `REG_004`) — **os três são templates vazios**.

A implementação foi interrompida **antes de qualquer código** e a decisão apresentada. **Homologada a Opção A:** as datas moram nas próprias ETAPAS/SUBETAPAS (fonte de verdade única por registro); PLANEJAMENTO fica preservada e reservada, sem uso como tabela.

## 3. O que foi implementado

- **ETAPAS** — os 4 campos de data existentes passam a ser a fonte de verdade do cronograma, digitáveis no Excel e base dos cálculos.
- **SUBETAPAS** — ganham os mesmos 4 campos de data (novos), opcionais, sem migração.
- **Cálculos por registro** (`@property` em `Etapa`/`Subetapa`): Duração Prevista, Duração Real e Variação de Prazo, em dias.
- **Consolidação por Obra** (`src/planejamento/calculos.py`): menor Início Previsto, maior Fim Previsto, Início/Fim Real consolidados, Duração Prevista/Real e Variação de Prazo da Obra.
- **Excel:** bloco de 7 colunas idêntico nas abas Etapas e Subetapas (4 datas + 3 calculadas) e 3 linhas de cronograma consolidado na aba Início.
- **PLANEJAMENTO** preservada e reservada — `adicionar_planejamento` continua funcional e testado.

## 4. Arquivos

**Criados:** `src/planejamento/{__init__,calculos}.py` · `testes/test_planejamento.py` · `testes/test_excel_planejamento.py` · `scripts/gerar_arquivo_obra_modelo_v8.py` · `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V8.xlsx` · `relatorios/PLANO_ETAPA_8_PLANEJAMENTO_V1.md` · este relatório.

**Modificados:** `src/modelo/entidades.py` · `src/excel/construtor_workbook.py` · `DAD_001` (Revisão 12) · `REG_001` (Nota de Implementação — Etapa 8). **Nenhum arquivo de teste de etapa anterior precisou ser modificado.**

## 5. Regras

**Implementadas:** duração e variação de prazo por Etapa/Subetapa e consolidação por Obra, todas por subtração pura de datas.

**Decisões de implementação (com precedente, não regras novas):** subtração pura sem `+1` de contagem inclusiva (precedente REG-005/REG-010/REG-028); sinal positivo = atraso, negativo = antecipação (precedente `Alteracao.impacto_prazo_dias`); ausência de data = "não calculável", nunca 0 nem data inventada (precedente REG-031); datas invertidas não são bloqueadas (precedente REG-032).

**Regra 8.1 — REJEITADA; indicador consolidado REMOVIDO (decisão do responsável do projeto, 2026-09-23, Alternativa D1).** Ver Seção 11.

**Nenhuma regra de negócio nova permanece em vigor nesta etapa.**

**Não implementado, permanece [H]:** REG-014 (threshold de atraso — "Resultado: não definido"); "Status do Prazo"; encadeamento/dependência tipo Gantt; significado do "N" de PLANEJAMENTO; relação entre datas de Subetapa e de sua Etapa (registrada como pendência explícita).

## 6. Testes

**325 passando** = 277 herdados + 48 novos (29 em `test_planejamento.py`, 19 em `test_excel_planejamento.py`). Zero regressões; nenhum teste anterior alterado.

## 7. Auditoria independente

Executada por agente separado (AGENTS.md §15: quem constrói não homologa a si mesmo), com veredito inicial **"não apta"** e 2 bloqueantes — **ambos corrigidos**:

| # | Achado | Classe | Tratamento |
|---|---|---|---|
| D-2 | Motor Python e fórmula Excel discordavam: a fórmula comparava CONTAGENS (`COUNT(real)<COUNT(prev)`), não equivalente ao predicado linha a linha. Com uma Etapa "prevista sem real" e outra "real sem prevista", as contagens empatam e a planilha exibia o número enganoso que o guard existia para impedir | BLOQUEANTE | **Corrigido.** Fórmula passou a `SUMPRODUCT((prev<>"")*(real=""))>0`, equivalente ao predicado Python. Contraexemplo travado como teste; teste do Excel agora também **proíbe** a construção defeituosa |
| D-1 | A regra de supressão foi implementada **depois** de a documentação ser fechada e nunca documentada, sob a frase "nenhuma regra de negócio nova foi criada" | BLOQUEANTE | **Corrigido.** Regra documentada em `REG_001` e `DAD_001` como **[H] a homologar**, com precedente citado; a frase falsa foi corrigida |
| D-4 | "A partir da Revisão 1" — erro factual introduzido numa linha pré-existente (correto: Revisão 3) | IMPORTANTE | **Corrigido** |
| D-3 | 5 funções públicas do motor não documentadas; 4 sem saída no produto | IMPORTANTE | **Corrigido** — tabela no `DAD_001` lista as 7 funções e quais 3 aparecem na aba Início |
| M-1 | Relação datas Subetapa × Etapa indefinida e não registrada | MENOR | **Corrigido** — registrada como [H] no `DAD_001` |
| M-3 | Lacunas de cobertura (datas invertidas na entidade, Subetapa `None`) | MENOR | **Corrigido** — 3 testes novos |
| M-5 | `formula1="1900-01-01"` é avaliado pelo Excel como aritmética (1898), não como data | MENOR | **Corrigido nas 8 faixas novas** (`DATE(1900,1,1)`). A ocorrência equivalente na aba Início é **anterior a esta etapa** e foi deixada intacta — ver Seção 9 |
| M-7 | Plano contradizia a entrega; relatório final inexistente | MENOR | **Corrigido** — aviso no topo do plano + este relatório |
| M-2 | Testes verificam texto de fórmula, não resultado | MENOR | Aceito — metodologia do projeto desde a Etapa 2 (sem motor de fórmulas). Ver Seção 9 |
| M-4 | Ordem posicional de `Subetapa` mudou (todas as construções usam kwargs) | MENOR | Aceito, registrado |
| M-6 | Validação cobre linhas 2:31 | MENOR | Aceito — igual a todas as validações pré-existentes |
| M-8 | Título/numeração de revisão do `DAD_001`/`REG_001` duas revisões atrás | MENOR | **Não corrigido** — defeito pré-existente herdado da Etapa 7. Ver Seção 9 |
| M-9 | Obrigatoriedade declarada no `DAD_001` não exercida no produto | MENOR | Aceito — postura já documentada desde a Etapa 1. Ver Seção 9 |

**Íntegros conforme a auditoria:** REG-014 não implementado (zero formatação condicional no workbook inteiro); "Status do Prazo" e Gantt inertes; zero ranges fixos; IDs técnicos ocultos; fórmulas de outras abas intactas (`Início!$B$8` preservada); diff aditivo sem remoção de comportamento; datas não afetam orçamento/financeiro/compras/execução; PLANEJAMENTO preservada.

## 8. Excel — validação e comparação V8 × V7

- **Mesmas 11 abas**; só Etapas e Subetapas mudaram (8 → 15 colunas); **zero colunas removidas**; nenhuma aba criada ou renomeada.
- **Zero ranges fixos** em todo o workbook; tabelas estruturadas (`TabelaEtapas`/`TabelaSubetapas` de `A1:H31` para `A1:O31` automaticamente).
- **19 colunas de ID técnico** continuam ocultas; nenhum dropdown expõe ID.
- **Zero regras de formatação condicional** — REG-014 intacto.
- **V1–V7 preservados**: V7 confirmado byte-a-byte idêntico ao commit `a953acc` (`git diff` vazio); apenas o V8 é novo.

**Atualização (2026-09-23):** a limitação acima foi **superada** — ver Seção 12, validação com o Excel real via COM.

## 9. Riscos remanescentes

1. ~~Regra de supressão aguardando confirmação~~ — **resolvido:** regra rejeitada e indicador removido (Seção 11).
2. **Equivalência Python × Excel é garantida por construção, não por execução.** Foi exatamente aí que o defeito D-2 nasceu. Enquanto não houver um motor de fórmulas autorizado no ambiente, esse risco permanece para toda fórmula não trivial. (A remoção do indicador reduziu a superfície: a fórmula mais complexa da aba Início deixou de existir.)
3. **`formula1="1900-01-01"` na aba Início** (pré-existente, Etapa 2) continua entregando um limite de data errado. Fora do escopo desta etapa; corrigir exige autorização para tocar código de etapa anterior.
4. **Título/numeração de revisão do `DAD_001` e `REG_001`** estão duas revisões atrás do conteúdo (herdado da Etapa 7).
5. **Obrigatoriedade das datas** é declarada no `DAD_001` mas não exercida no Excel nem no dataclass — é essa folga que tornava o defeito D-2 alcançável.
6. **Fronteira Subetapa × Etapa** indefinida: uma Subetapa pode ter data fora da janela da sua Etapa sem aviso.
7. **Pendências** segue bloqueada por três decisões de negócio indefinidas — é o que resta do Núcleo V1.

## 10. Estado do Git

Working tree com as alterações da Etapa 8, **sem commit e sem push**.

---

## 11. Adendo — Regra 8.1 rejeitada e indicador consolidado removido (2026-09-23)

**Decisão do responsável do projeto:** a Regra 8.1 **não foi homologada**, e a simples remoção da proteção também não foi autorizada — o contraexemplo dos −113 dias é válido. Homologada a **Alternativa D1: remover o indicador consolidado "Variação de Prazo da Obra"**.

**Motivo registrado:** o indicador foi criado durante a Etapa 8 e **não possui regra de negócio previamente homologada que defina seu significado**. Não se criou agora uma regra para determinar quando a Obra como um todo está atrasada, nem se redefiniu o indicador para "Etapas concluídas".

**Causa técnica que sustenta a decisão:** `MAX(Fim Previsto)` é sempre o fim previsto da Obra, mas `MAX(Fim Real)` só é o fim real da Obra quando todas as Etapas previstas terminaram — antes disso é "a última data concluída até agora". Os dois operandos podiam vir de **Etapas diferentes**, e era isso que produzia os −113 dias.

**Removido:**
- Célula "Variação de Prazo da Obra (dias)" da aba Início.
- `variacao_prazo_obra_dias`, `duracao_real_obra_dias` e `ha_etapa_prevista_nao_concluida` (`src/planejamento/calculos.py`).
- A regra de supressão 8.1 e sua classificação `[H]` — deixou de ser regra do sistema.

**Preservado:** datas consolidadas da Obra (menor Início Previsto / maior Fim Previsto, ambas exibidas); Duração Prevista/Real de Etapa e Subetapa; **Variação de Prazo por Etapa e por Subetapa**; toda a Etapa 8 restante; Etapas 1–7 intactas.

**Cenário 3 preservado com nova finalidade** (`test_cenario3_nenhuma_funcao_produz_o_resultado_enganoso_de_113_dias`): prova que nenhuma função do motor produz −113; que a Fundação continua reportando corretamente a sua própria variação (+10 dias); que a Etapa em andamento não gera variação consolidada; e que as datas consolidadas continuam disponíveis. Somado a `test_excel_nao_tem_indicador_de_variacao_de_prazo_da_obra`, que impede o indicador de voltar à planilha por descuito.

**Testes após a alteração: 324 passando.** A suíte caiu de 325 para 324 porque dois testes que exercitavam exclusivamente a regra removida saíram e um teste de regressão mais abrangente entrou — **não houve redução de cobertura do comportamento vigente**: nenhuma função ou coluna existente ficou sem teste.

---

## 12. Validação com o Excel real (COM) — 2026-09-23

Autorizada a instalação do `pywin32` **exclusivamente** como ponte Python → Excel. Nenhum outro pacote instalado; nenhuma versão de biblioteca homologada alterada. `pywin32-312`, Excel 16.0 (Office16).

### 12.1 Defeito CRÍTICO encontrado e corrigido — nenhuma versão de V5 a V8 abria no Excel

Ao tentar a primeira abertura real, o Excel **recusou o arquivo**. Bissecção contra o Excel instalado:

- **V1, V2, V3, V4 abrem.** **V5, V6, V7 e V8 não abriam** — nem com `xlRepairFile`.
- Causa isolada por eliminação: as **validações de dados do tipo `custom`** — a validação de "nome único" introduzida na **Etapa 5.1** (AUD-18), cuja fórmula era `=COUNTIF(TabelaX[Coluna],B2)=1`.
- **O Excel não aceita referência estruturada de Tabela dentro de validação de dados** e rejeita o arquivo inteiro como corrompido. Confirmado em teste controlado: com referência estruturada falha; com **intervalo nomeado** abre.

**Por que passou despercebido por 4 etapas:** toda a verificação anterior era feita com openpyxl, que **não executa o Excel** — ela lê o XML e o considera válido. O defeito só é observável abrindo o arquivo no Excel real.

**Correção aplicada** (defeito técnico claramente contrário ao AGENTS.md §10, "compatibilidade com Excel"): `_adicionar_validacao_nome_unico` passa a usar o **intervalo nomeado** correspondente (`Lista_Etapas`, `Lista_Subetapas`, `Lista_Servicos`, `Lista_Financeiro_Descricoes`), que aponta para a **mesma coluna da mesma Tabela** — portanto **sem reintroduzir range fixo** (AUD-20/AUD-21 preservado) e **sem alterar a regra de negócio** da validação. O `=` inicial, que não pertence a fórmula de validação em OOXML, também foi removido.

**Resultado:** **o V8 agora abre no Excel real**, com as 11 abas, tabelas estruturadas íntegras e a validação de nome único ativa (`CONT.SE(Lista_Etapas;B2)=1`, `Validation.Type=7`).

**V5, V6 e V7 não foram regerados** — são versões históricas preservadas e continuam intactas (hashes conferidos). Elas permanecem sem abrir no Excel; o defeito está registrado aqui.

### 12.2 Validação de valores Python × Excel

Workbook populado com cenário abrangente (obra concluída/em andamento/sem datas, serviços por método quantitativo e por status, ajuste manual de valor, serviço cancelado, peso manual, medições, aportes, despesa com pagamento parcial, outras saídas, alterações aprovada e em análise, compras com e sem vínculo). O Excel recalculou (`CalculateFullRebuild`) e os valores foram lidos e comparados com o motor Python.

**110 casos comparados — 107 equivalentes, 3 divergências** (todas a mesma causa raiz).

Também validados no Excel real: **expansão além das 30 linhas** (35 Etapas → `TabelaEtapas` em `A1:O66`, nenhum registro ignorado, totais e MAX de datas corretos — AUD-20/AUD-21 comprovado contra o Excel, não só por leitura de XML); tratamento de zero, células vazias, datas, percentuais e `"N/D"` de divisão por zero em % Orçamento Consumido (REG-031).

### 12.3 Divergências registradas — NÃO corrigidas (código de etapas anteriores)

**D-COM-1 — Compras: vínculo com Serviço não é escrito na planilha (Etapa 6)**
- Fórmula Python: `planejado()` → Valor Previsto do Serviço via `id_servico` (REG-010).
- Fórmula Excel: `L = IF($S="","",INDEX(Serviços!$J:$J,MATCH($S,Serviços!$A:$A,0)))`, com `S = IF($K="","",...)`.
- Entrada: Compra "Cimento CP-II" com `id_servico` preenchido no Python.
- Python: `Planejado=2400`, `Variação R$=400`, `Variação %=16,67%`. Excel: **vazio nos três**.
- Causa: `_construir_aba_compras` **não escreve os nomes de Etapa/Subetapa/Serviço** (colunas I/J/K) para registros existentes. É a **única aba** que não escreve o nome amigável do seu vínculo — Subetapas, Serviços, Execução e Pagamentos todas escrevem.
- Fonte que deveria prevalecer: **REG-010 (homologada)** — com a coluna vazia, a Variação homologada não é calculada sobre dados existentes.
- **Não afeta o arquivo entregue** (V8 é template vazio, sem linhas de dados). É defeito latente do construtor.

**D-COM-2 — Peso Automático: divisão por zero vaza `#DIV/0!` até a tela principal (Etapa 7)**
- Fórmula Python: `peso_automatico_bruto()` com guarda explícita `if total == 0: return None`.
- Fórmula Excel: `R = J/SUMIFS(J:J, <elegíveis>)` — **sem guarda de denominador zero**.
- Entrada: único Serviço elegível com Valor Previsto = 0.
- Python: `peso_automatico_bruto=None`, `percentual_execucao_obra=0.0`. Excel: `#DIV/0!` em Peso Automático → Peso Efetivo → Contribuição → Subetapas → Etapas → **`Início!B9 % Execução Física da Obra`**.
- Fonte que deveria prevalecer: **REG-031 (homologada)** — divisão por zero deve ser "não calculável" (`"N/D"` no Excel), **nunca um erro**. A própria Etapa 7 cita REG-031 como precedente que segue.
- Correção provável: envolver o denominador com a mesma guarda já usada em `% Orçamento Consumido`.

Ambas estão em código de etapas anteriores (6 e 7), protegido pela sua instrução. **Registradas, não corrigidas** — aguardam sua decisão.

---

## 13. Etapa 8.2 — Correções pós-validação Excel/COM (2026-09-23)

Autorizadas **exclusivamente** as duas divergências registradas na Seção 12.3. Nenhuma regra de negócio foi criada ou alterada; a regra homologada prevaleceu em ambos os casos.

### 13.1 D-COM-1 — Compras não escrevia o vínculo com Serviço

**Antes:** `_construir_aba_compras` não escrevia os nomes de Etapa/Subetapa/Serviço (colunas I/J/K). Uma Compra com `id_servico` no Python chegava ao Excel sem vínculo; a coluna técnica ID_Servico (resolvida por MATCH sobre esse nome) ficava vazia e, com ela, **Planejado, Variação R$ e Variação % — REG-010 não era calculada sobre dados existentes.** Era a única aba que não escrevia o nome amigável do seu vínculo.

**Depois:** os três vínculos passam a ser escritos pelo **nome amigável**, mesmo padrão de Subetapas→Etapa, Serviços→Subetapa, Execução→Serviço e Pagamentos→Lançamento. Confirmado no Excel real: `Serviço="Chapisco"` → `Planejado=2.400` → `Variação R$=400` → `Variação %=16,67%`, idênticos ao Python.

**Preservados:** IDs técnicos internos (colunas ocultas, sempre por fórmula); nome amigável ao usuário (nunca ID); estrutura da Tabela; ausência de ranges fixos; regra de cálculo (REG-010, intocada); independência Compras × Financeiro; ausência de efeitos automáticos sobre Orçamento/Execução — este último com teste de regressão negativa explícito.

### 13.2 D-COM-2 — Divisão por zero vazava como `#DIV/0!`

**Antes:** `Peso Automático = Valor Previsto / Σ Valor Previsto dos Elegíveis`, **sem guarda de denominador zero**. Com todos os elegíveis orçados em 0, o Excel devolvia `#DIV/0!`, que se propagava por Peso Efetivo → Contribuição → Subetapa → Etapa → Obra → `Início!B9`. Contrariava REG-031 (divisão por zero é "não calculável", nunca erro).

**Depois:** auditada **toda** a cadeia de fórmulas do workbook — foram localizadas todas as divisões e verificado que apenas essa estava desprotegida (as demais já tratavam vazio/zero). Duas correções:
1. **Peso Automático** passa a devolver `"N/D"` quando o denominador é zero — mesma representação já homologada em REG-031 (% Orçamento Consumido) e REG-010 (Variação %). Espelha o `None` do Python.
2. **Peso Efetivo**, no ramo sem base proporcional, passa a **dividir a faixa restante igualmente** entre os automáticos elegíveis — espelhando o ramo `total_bruto_automaticos == 0` de `pesos_efetivos_obra` (Etapa 7). Nenhuma regra nova: a divisão igualitária já era o comportamento implementado e testado no Python; o Excel é que devolvia vazio.

**Defeito secundário encontrado durante a própria correção:** a primeira versão contava os automáticos com `COUNTIFS(...,"<>")` sobre Valor Previsto — e o Excel conta célula **com fórmula que devolve `""`** como não vazia, de modo que as 30 linhas-modelo entravam no denominador (peso de 1/31 em vez de 100%). Corrigido com `SUMPRODUCT(ISNUMBER(...))` sobre referência estruturada, que conta apenas valores numéricos reais e acompanha a expansão da Tabela sem range fixo. **Só apareceu porque os 9 cenários foram executados no Excel real** — a suíte estrutural não o pegaria.

**Os 9 cenários exigidos, validados no Excel real:** único elegível com valor 0 → 100% · todos com valor 0 → 50%/50% · sem elegíveis → vazio · mistura zero+positivo → 0%/100% · peso manual 25% + base zero → 25%/75% · cancelado · retirado do escopo · obra em andamento · obra concluída. **Python e Excel idênticos nos nove; nenhum `#DIV/0!`.**

### 13.3 Resultado

| | Antes da 8.2 | Depois da 8.2 |
|---|---|---|
| Python × Excel (110 casos) | 107 equivalentes, 3 divergências | **110 equivalentes, 0 divergências** |
| Células com erro Excel em qualquer aba | `#DIV/0!` propagado até `Início!B9` | **0** |
| Testes | 325 | **336** |

V8 regerado. V1–V7 intactos (hashes conferidos). Abas e colunas do V8 inalteradas em relação à 8.1 — as correções mudaram apenas conteúdo de células e fórmulas.

### 13.4 Item 11.1 — `% Execução Física da Obra` sem base de cálculo (corrigido)

Última divergência Python × Excel, corrigida com autorização explícita por tocar código da Etapa 7.

**Antes:** `Início!B9 = SUM(TabelaEtapas[Contribuição na Obra (Execução)])`. Sem nenhum Serviço Elegível (REG-022), o `SUM` de coluna vazia devolve 0 e a tela exibia **"0,00% executado"** — enquanto `percentual_execucao_obra` (Python) devolve `None`, "não calculável". Ler 0% onde não existe base de cálculo é a mesma leitura inválida que REG-031 proíbe para a divisão por zero.

**Depois:** `=IF(<contagem de elegíveis>=0,"N/D",SUM(...))`, com a contagem feita por `SUMPRODUCT(ISNUMBER(...))` sobre referência estruturada, aplicando os mesmos três critérios de exclusão de REG-022 (Cancelado / Retirado do Escopo / Substituído). Sem range fixo. A lógica de contagem foi extraída para `_contagem_servicos_elegiveis()`, reutilizada pela redistribuição de peso — uma única definição de "Serviço Elegível" no gerador.

**Validado no Excel real, 7 cenários:** obra vazia · só cancelado · só sem valor · só retirado do escopo → **"N/D"** (Python `None`); elegível sem método · elegível com valor 0 → **0%** (Python `0.0`); elegível concluído → **100%**. **Equivalência total.** A distinção que importa ficou preservada: "N/D" = não há base de cálculo; "0%" = há base e nada foi executado.

### 13.5 Estado final da Etapa 8

| | Valor |
|---|---|
| Testes | **338 passando** |
| Python × Excel (110 casos) | **110 equivalentes, 0 divergências** |
| Cenários de borda validados no Excel real | 9 (divisão por zero) + 7 (base de cálculo) + expansão >30 linhas |
| Células com erro Excel | **0** |
| Ranges fixos · formatação condicional · IDs visíveis · DV com ref. estruturada | **0 · 0 · 0 · 0** |
| V1–V7 | intactos (hashes conferidos) |
| V8 | abre e recalcula no Excel real |
