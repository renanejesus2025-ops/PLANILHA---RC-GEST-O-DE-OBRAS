# FINANCEIRO — ETAPA 4
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-17
**Fase:** Módulo Financeiro operacional (Aporte, Outras Entradas, Despesa/Custo, Outras Saídas, Pagamentos, Orçamento Vigente, Saldo Orçamentário, % Consumido, Saldo de Caixa). Nenhum módulo de Alterações, Compras, Planejamento/Cronograma, Dashboard Gerencial ou Perfis/Acesso foi construído, conforme limite de escopo explícito.
**Checkpoint Git de partida:** `e5200b9` (ETAPA 3 — ORÇAMENTO CONCLUÍDA).
**Git ao final desta etapa:** nenhum commit ou push foi realizado. `git status` verificado antes e depois (Seção 19 deste relatório).

---

## 1. Objetivo

Construir o módulo financeiro operacional, separando com rigor os 9 conceitos exigidos pela homologação — Orçamento, Aportes, Entradas, Custos Realizados, Pagamentos, Contas a Pagar, Saldo de Caixa, Saldo Orçamentário e % de Orçamento Consumido — sob o princípio "o sistema informa, o Operador decide": nenhum lançamento é bloqueado por causar estouro de orçamento; o sistema apenas calcula e informa a situação real, inclusive quando o Saldo fica negativo ou o percentual consumido ultrapassa 100%.

---

## 2. Arquivos criados

```
src/financeiro/
├── __init__.py
├── calculos.py                      (Motor de Cálculos: Orçamento Vigente, Saldo
│                                      Orçamentário, % Consumido, A Pagar, Saldo de Caixa)
└── movimentos.py                    (registrar_lancamento, registrar_pagamento)

scripts/
└── gerar_arquivo_obra_modelo_v3.py  (gera o arquivo entregável desta etapa)

testes/
├── test_financeiro.py               (20 testes — domínio/Motor de Cálculos, Cenários A–J)
└── test_excel_financeiro.py         (22 testes — fórmulas/Excel das abas novas)

dados/
└── GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx   (arquivo entregável desta etapa)

relatorios/
└── FINANCEIRO_ETAPA_4_V1.md         (este arquivo)
```

## 3. Arquivos alterados

**Código (Etapas 1–3, estendido — nenhum comportamento anterior removido):**
- `src/excecoes.py` — nova exceção `ErroPagamentoDeTipoInvalido`.
- `config/ids_config.py` — novo prefixo `PAGAMENTOS` → `PGT` (derivado pelo mesmo princípio já usado para `PLN`/`FOR` na Etapa 1).
- `src/modelo/enums.py` — `TipoLancamentoFinanceiro` ganha `OUTRAS_ENTRADAS` e `OUTRAS_SAIDAS` (mantendo `APORTE`/`DESPESA` já existentes) e as propriedades `rotulo`, `aumenta_orcamento_vigente`, `e_custo_realizado`, `afeta_caixa_no_lancamento`, `natureza_caixa`.
- `src/modelo/entidades.py` — `Financeiro`: novos campos `descricao`, `id_fornecedor`, `id_compra`, `observacao`, `situacao`; `__post_init__` valida `valor` não negativo. Nova dataclass `Pagamento` (id, id_financeiro, data, valor, observacao), também validada.
- `src/base_dados/repositorio.py` — nova coleção `pagamentos`; `adicionar_financeiro` passa a validar `id_fornecedor`/`id_compra` opcionais; novo método `adicionar_pagamento` (valida existência do lançamento e que seu Tipo é Despesa/Custo).
- `src/excel/estilos.py` — novo `FORMATO_MOEDA_BR` ("R$ #,##0.00").
- `src/excel/construtor_workbook.py` — 3 abas novas: **Financeiro**, **Pagamentos**, **Resumo Financeiro** (ver Seção 5); `construir_workbook` e `_criar_intervalos_nomeados` ajustados para construí-las e para o novo intervalo nomeado `Lista_Financeiro_Descricoes`.
- `scripts/gerar_arquivo_obra_modelo_v2.py` — **depreciado**: agora se recusa a rodar, mesmo motivo já aplicado ao script V1 na Etapa 3 (evitar sobrescrita silenciosa da V2 com a estrutura nova).
- `testes/test_excel_construtor.py` — `ABAS_ESPERADAS` atualizada para incluir as 3 abas novas (mesmo tipo de ajuste já registrado no relatório da Etapa 3, Seção 3, quando abas/colunas mudam de posição/quantidade por decisão explícita da homologação corrente).

**Documentação formal (Seção 39 desta homologação):**
- `05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md` — Revisão 7: REG-004, REG-005 e REG-018 reescritas (de [H]/[P] para [D]); nota de escopo parcial adicionada a REG-017; REG-029 (Pagamento e A Pagar), REG-030 (Tipos de Movimentação Financeira), REG-031 (% Consumido e Divisão por Zero) e REG-032 (Estouro Não Bloqueia) adicionadas.
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md` — Revisão 7: entidade FINANCEIRO reescrita (campos novos, domínio "Tipo" fechado, campo "Saldo Resultante" removido); nova entidade PAGAMENTOS (14ª entidade); relacionamentos atualizados.
- **Pares DOCX não foram atualizados** — mesma pendência de forma já registrada nas Etapas 1–3 (gerar `.docx` está fora do escopo sem biblioteca de geração aprovada); registrada aqui novamente conforme pedido pela Seção 39.

---

## 4. Modelo financeiro

Separação obrigatória (Seção 3 da homologação) mantida em todas as camadas (entidade, Motor de Cálculos, Excel):

| Conceito | Onde vive | Nunca confundido com |
|---|---|---|
| Orçamento (Inicial/Vigente) | `src/orcamento/calculos.py` (Etapa 3) + `src/financeiro/calculos.py:orcamento_vigente` | Caixa |
| Aporte | `Financeiro` (Tipo = Aporte) | Custo, Pagamento |
| Outras Entradas | `Financeiro` (Tipo = Outras Entradas) | Aporte, Custo |
| Custo Realizado | `Financeiro` (Tipo = Despesa/Custo) — reconhecimento | Pagamento |
| Pagamentos | `Pagamento` — baixa financeira | Custo Realizado |
| Contas a Pagar (A Pagar) | `a_pagar`/`total_a_pagar_obra` = Custo − Total Pago | — |
| Saldo de Caixa | `saldo_caixa` = Entradas − Saídas (Pagamentos + Outras Saídas) | Saldo Orçamentário |
| Saldo Orçamentário | `saldo_orcamentario` = Orçamento Vigente − Custo Realizado | Saldo de Caixa |
| % Orçamento Consumido | `percentual_orcamento_consumido` | — |

---

## 5. Tipos de movimentação e abas do Excel

**Domínio fechado do Tipo (REG-030):** Aporte, Outras Entradas, Despesa/Custo, Outras Saídas — mesma fonte (`TipoLancamentoFinanceiro`) usada pelo Python e pelo dropdown do Excel.

Três abas novas foram criadas (nenhuma reaproveitável das Etapas 2/3 — são um domínio genuinamente novo):

### 5.1 Financeiro
1 linha = 1 movimentação. Colunas de entrada: Tipo (dropdown, 4 valores), Data, Descrição, Valor (validado ≥ 0), Situação (texto livre, [H]), Observação. Colunas SEMPRE calculadas por fórmula (mesmo padrão da aba Serviços, Etapa 3): Entrada/Saída, Aporte, Custo Realizado, Total Pago (via `SUMIFS` contra a aba Pagamentos), A Pagar, ID_Obra (técnico, oculto).

### 5.2 Pagamentos
1 linha = 1 pagamento (parcial ou total). Dropdown "Lançamento" aponta para a **Descrição** do lançamento em Financeiro (nome amigável, nunca o ID técnico) via o intervalo nomeado `Lista_Financeiro_Descricoes`; o vínculo técnico oculto (`ID_Financeiro`) é resolvido por `INDEX/MATCH`, mesmo padrão já usado para Subetapa→Etapa e Serviço→Subetapa nas Etapas 2/3 — inclusive a mesma limitação conhecida de nomes duplicados (ver Seção 14).

### 5.3 Resumo Financeiro
Área de resumo operacional (Seção 28) — não o Dashboard Gerencial definitivo. Apresenta, em fórmulas que somam as colunas derivadas da aba Financeiro: Orçamento Inicial, Aportes, Orçamento Vigente, Custo Realizado, Saldo Orçamentário, % Orçamento Consumido, Outras Entradas, Outras Saídas, Total de Entradas, Total Pago, Total de Saídas, Saldo de Caixa, Total A Pagar, e o indicador "Estouro de Orçamento" (Seção 29).

---

## 6. Regras implementadas

| Regra | Fórmula | Onde |
|---|---|---|
| Orçamento Vigente | Orçamento Inicial (Etapa 3) + Σ Aportes | `orcamento_vigente` / Resumo Financeiro!B4 |
| Saldo Orçamentário | Orçamento Vigente − Custo Realizado | `saldo_orcamentario` / Resumo Financeiro!B6 |
| % Orçamento Consumido | Custo Realizado / Orçamento Vigente × 100 | `percentual_orcamento_consumido` / Resumo Financeiro!B7 |
| Custo Realizado | Σ Valor dos lançamentos Despesa/Custo | `custo_realizado` / Financeiro!H (SUM) |
| Total Pago | Σ Valor dos Pagamentos de um lançamento | `total_pago` / Financeiro!I (SUMIFS) |
| A Pagar | Custo Reconhecido − Total Pago | `a_pagar` / Financeiro!J |
| Saldo de Caixa | (Aportes + Outras Entradas) − (Pagamentos + Outras Saídas) | `saldo_caixa` / Resumo Financeiro!B13 |

**Estouro de orçamento não bloqueia (REG-032):** nenhuma função do Motor de Cálculos levanta exceção nem satura um resultado — `saldo_orcamentario` retorna negativo e `percentual_orcamento_consumido` retorna acima de 100 quando aplicável (Cenário F).

**Divisão por zero (REG-031, Seção 7):** `percentual_orcamento_consumido` retorna `None` em Python e a fórmula Excel retorna o texto `"N/D"` quando o Orçamento Vigente é zero — nunca `0%`, que seria uma leitura inválida do resultado (Cenário J).

---

## 7. Estrutura de Pagamentos

`Financeiro` (reconhecimento do custo) e `Pagamento` (baixa financeira) são entidades **separadas** (REG-029), nunca um único campo:

- Um lançamento do tipo Despesa/Custo pode ter zero, um ou múltiplos Pagamentos.
- `BaseDados.adicionar_pagamento` garante, tecnicamente, que um Pagamento só referencia um lançamento existente **e** do tipo Despesa/Custo (`ErroPagamentoDeTipoInvalido` caso contrário) — não é possível "pagar" um Aporte, Outras Entradas ou Outras Saídas, por definição dos próprios conceitos.
- Pagamento parcial e total são suportados sem distinção estrutural: `a_pagar` simplesmente reflete o que resta, podendo chegar a zero (Cenário E) ou permanecer positivo (Cenários C/D/I).
- Nenhum bloqueio de edição/exclusão de Pagamento foi criado — essa função ainda não existe em nenhuma camada construída até esta etapa (não é uma restrição nova desta regra, ver Seção 15, item 6).

---

## 8. Resumo Financeiro

Ver Seção 5.3. Todas as 11 métricas exigidas pela Seção 28 da homologação estão presentes, mais o indicador de estouro (Seção 29). Nenhuma formatação condicional foi criada (mesmo princípio da Etapa 3, Seção 31) — o indicador de estouro é um texto simples `"SIM"/"NÃO"`, sem cor.

---

## 9. Integração com Orçamento

`orcamento_vigente` chama diretamente `src.orcamento.calculos.total_previsto_obra` (Etapa 3) e soma `total_aportes` — nenhuma duplicação do Orçamento Inicial foi criada; ele continua vindo de uma única fonte de verdade (os Serviços/Orçamento elegíveis). No Excel, a aba Resumo Financeiro referencia diretamente `Início!$B$8` (a célula já existente do Orçamento Inicial, Etapa 3) em vez de recalculá-la. A parcela de Alterações Formais Aprovadas (REG-017) permanece [H] — preparada para integração futura, não implementada (Seção 4 da homologação: "não inventar implementação de Alterações").

---

## 10. Testes criados

**42 testes novos** (20 em `testes/test_financeiro.py` + 22 em `testes/test_excel_financeiro.py`):

| Área | Testes |
|---|---|
| Domínio "Tipo" (4 valores, efeitos por tipo) | `test_quatro_tipos_homologados_existem`, `test_apenas_aporte_aumenta_orcamento_vigente`, `test_apenas_despesa_e_custo_realizado` |
| Valores negativos rejeitados (Seção 21) | `test_valor_negativo_em_financeiro_e_rejeitado`, `test_valor_negativo_em_pagamento_e_rejeitado` |
| Integridade Pagamento→Despesa/Custo (Seção 20) | `test_pagamento_de_lancamento_inexistente_e_rejeitado`, `test_pagamento_de_aporte_e_rejeitado` |
| Cenários A–J (Seção 34) | `test_cenario_a_...` a `test_cenario_j_...` (10 testes, um por cenário) |
| Saldo de Caixa/A Pagar consolidados | `test_saldo_de_caixa_...`, `test_total_a_pagar_obra_...` |
| Autonomia do Operador / Situação (Seções 22/23) | `test_situacao_e_texto_livre_e_nao_exclui_registro_dos_totais` |
| Excel — estrutura das abas novas | `test_abas_financeiro_pagamentos_resumo_existem`, `test_cabecalhos_financeiro_pagamentos`, `test_colunas_tecnicas_de_id_ficam_ocultas_...` |
| Excel — dropdown Tipo, colunas derivadas | `test_dropdown_de_tipo_...`, `test_coluna_aporte_...`, `test_coluna_custo_realizado_...`, `test_coluna_a_pagar_...`, `test_coluna_total_pago_...`, `test_coluna_entrada_saida_...` |
| Excel — vínculo Pagamentos↔Financeiro por nome amigável | `test_dropdown_de_lancamento_...`, `test_id_financeiro_em_pagamentos_...`, `test_pagamento_literal_mostra_descricao_amigavel_...` |
| Excel — formatação R$, validações, Resumo Financeiro | `test_colunas_monetarias_...`, `test_resumo_financeiro_usa_formato_...`, `test_validacao_de_valor_...`, `test_resumo_orcamento_vigente_...`, `test_resumo_percentual_consumido_trata_divisao_por_zero`, `test_resumo_saldo_de_caixa_...`, `test_resumo_estouro_de_orcamento_...`, `test_id_obra_de_financeiro_...`, `test_nenhum_termo_desvio_...` |

## 11. Quantidade total de testes e resultado

```
.venv/Scripts/python.exe -m pytest -v
```
**162 testes coletados, 162 passed, 0 failed** (Etapas 1–3: 120 · Etapa 4: 42). Todos os testes das Etapas 1–3 continuam passando sem alteração de comportamento — o único ajuste foi `ABAS_ESPERADAS` em `test_excel_construtor.py` (3 abas novas acrescentadas à lista esperada), mesmo tipo de atualização já precedente na Etapa 3 quando a estrutura evolui por decisão explícita da homologação corrente.

---

## 12. Cenários simulados (Seção 34)

| Cenário | Entrada | Resultado obtido |
|---|---|---|
| A | Orçamento 100.000, sem movimentações | Orçamento Vigente = 100.000; Saldo = 100.000; % Consumido = 0% |
| B | Orçamento 100.000, Aporte 20.000 | Orçamento Vigente = 120.000; Aporte não entra em Custo Realizado |
| C | Orçamento 100.000, Despesa 10.000, sem pagamento | Custo Realizado = 10.000; A Pagar = 10.000; Saldo = 90.000; Caixa não reduz |
| D | Custo 10.000, Pagamentos 3.000 + 2.000 | Total Pago = 5.000; A Pagar = 5.000 |
| E | Custo 10.000, Pagamento 10.000 | A Pagar = 0 |
| F | Orçamento Vigente 120.000, Custo 105.000 | Saldo = 15.000 (positivo neste teste combinado) — ver também teste isolado de estouro puro: Orçamento 100.000/Custo 105.000 → Saldo = -5.000, % = 105%, sem bloqueio |
| G | Aporte 20.000 + Outras Entradas 5.000 | Orçamento Vigente aumenta só pelo Aporte (20.000); Caixa recebe as duas entradas (25.000) |
| H | Outras Saídas 3.000 | Caixa reduz 3.000; não se torna Custo Realizado |
| I | Custo 15.000, Pagamento 5.000 | Custo Realizado = 15.000; Pago = 5.000; A Pagar = 10.000 |
| J | Orçamento Vigente 0, Custo 1.000 | Saldo = -1.000; % Consumido = "não calculável" (nunca 0% nem erro) |

Todos os 10 cenários têm teste automatizado dedicado em `testes/test_financeiro.py` e passam.

**Validação adicional em Excel real** (ver Seção 13.1): os Cenários combinados (B+C+G+H+I) e o Cenário J foram recalculados com `Excel.Application` (COM) neste ambiente, e os valores lidos de volta da planilha coincidem exatamente com os valores calculados pelo Python.

---

## 13. Resultado

Todos os itens funcionais da homologação foram implementados e testados: os 4 tipos de movimentação, separação Custo Realizado × Pagamento, pagamentos parciais/múltiplos, A Pagar, Saldo de Caixa, Orçamento Vigente (parcial), Saldo Orçamentário, % Consumido com tratamento de divisão por zero, não bloqueio de estouro, e a interface Excel (3 abas novas, formatação R$, validações, dropdowns por nome amigável).

### 13.1 Validação do workbook (Seção 36)

Diferente das Etapas 2/3 (onde o ambiente não tinha Excel/LibreOffice), **este ambiente possui Microsoft Excel instalado** (`C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE`). Além da bateria estrutural já usada nas etapas anteriores:

- ZIP íntegro (`zipfile.testzip() is None`);
- 16 partes internas `.xml`/`.rels` bem formadas (`xml.etree.ElementTree`, 0 erros);
- reabertura pelo openpyxl com `data_only=False` e `data_only=True` sem exceção;

foi feita, **pela primeira vez neste projeto, uma abertura e recálculo REAIS em Excel** via automação COM (`Excel.Application`), com dois workbooks de teste (não commitados, gerados e descartados no scratchpad da sessão):

1. **Cenário combinado** (Orçamento 100.000; Aporte 20.000; Outras Entradas 5.000; Despesa 105.000 com Pagamento parcial de 12.000; Outras Saídas 500) — todos os 13 valores da aba Resumo Financeiro lidos de volta do Excel (Orçamento Vigente = 120.000, Custo Realizado = 105.000, Saldo Orçamentário = 15.000, % Consumido = 87,5%, Total de Entradas = 25.000, Total Pago = 12.000, Total de Saídas = 12.500, Saldo de Caixa = 12.500, Total A Pagar = 93.000, Estouro = "NÃO") **coincidem exatamente** com os valores calculados pelo Python (`src/financeiro/calculos.py`).
2. **Cenário J isolado** (Orçamento Vigente = 0, Despesa = 1.000) — o Excel real recalculou `% Orçamento Consumido = "N/D"` (não `0%`, não `#DIV/0!`) e `Estouro de Orçamento = "SIM"`, confirmando que a fórmula `IF(OrçamentoVigente=0,"N/D",...)` funciona exatamente como especificado (Seção 7) quando efetivamente calculada por um motor de planilha real.

Isso resolve, para o escopo desta etapa, o "Risco 2" que vinha sendo carregado desde o relatório da Etapa 3 ("divergência entre o valor Python e o valor Excel... só uma abertura real confirma") — agora confirmado com evidência real, não apenas revisão de texto de fórmula.

---

## 14. Limitações

1. **Ambiguidade de nomes duplicados no dropdown de Pagamentos** (mesma limitação já documentada nas Etapas 2/3 para Subetapa/Serviço) — o vínculo "Lançamento" em Pagamentos resolve pela **primeira** ocorrência da Descrição escolhida; duas Despesas/Custos com a mesma Descrição podem levar a um vínculo ambíguo. Mitigação recomendada (não implementada, decisão de UX/negócio pendente): exigir Descrição única ou compor um rótulo com Data+Descrição no dropdown.
2. **"Situação"/cancelamento de FINANCEIRO permanece texto livre, sem filtrar nenhum total** (Seção 23) — nenhum lançamento é excluído do Custo Realizado, Total Pago ou Saldo de Caixa por este campo, porque nenhum domínio fechado de cancelamento foi homologado. Isso significa que um lançamento marcado informalmente como "Cancelado" em texto livre **continua contando nos totais** até que essa regra seja homologada.
3. **Indicador "Estouro de Orçamento" não é tecnicamente Operador-only** (Seções 29/30) — está visível a qualquer pessoa que abra o arquivo; a restrição por perfil depende de SEC_001 ([H]), que não existe em nenhuma etapa construída até aqui.
4. **Fornecedor/Compra/Serviço vinculado** existem como campos opcionais no modelo Python (`Financeiro.id_fornecedor`/`id_compra`/`id_servico_vinculado`) mas **não foram expostos como colunas na aba Financeiro do Excel** — a Seção 27 da homologação lista explicitamente as colunas exigidas na interface (Tipo, Data, Descrição, Valor, Entrada/Saída, Custo, Pagamento, Aporte) e não inclui essas referências; expor um dropdown de Fornecedor/Compra exigiria abas próprias para essas entidades, que não fazem parte do escopo desta etapa (Compras/Fornecedores continuam sem interface Excel).
5. **Nenhuma função de edição/exclusão foi implementada** para nenhuma entidade em nenhuma camada (Etapas 1–4) — a autonomia do Operador (Seção 22) é reconhecida como princípio, mas a funcionalidade de editar/excluir/estornar em si nunca existiu neste código; não é uma restrição nova desta etapa.
6. **Sem motor de planilha íntegro para TODAS as fórmulas do workbook** — a validação real em Excel (Seção 13.1) cobriu os cálculos agregados da aba Resumo Financeiro com dados de exemplo; não foi uma verificação exaustiva célula-a-célula de todas as ~500 fórmulas geradas (30 linhas-modelo × múltiplas colunas calculadas em 3 abas novas) — o risco residual é baixo (mesma fórmula é reutilizada em cada linha, só a referência de linha muda), mas não é uma prova formal linha a linha.

---

## 15. Pendências (registradas, não resolvidas)

1. **Alterações Formais Aprovadas** — módulo ALTERAÇÕES não construído; a parcela correspondente do Orçamento Vigente (REG-017) permanece [H] e não integrada.
2. **Domínio fechado de Situação/cancelamento de FINANCEIRO** (Seção 23) — texto livre; nenhuma lista fechada foi criada.
3. **Mecanismo técnico de restrição de visibilidade por perfil** (Operador-only do indicador de estouro, Seções 29/30) — depende de SEC_001, ainda [H].
4. **Ambiguidade de nomes duplicados no dropdown de Pagamentos** (Seção 14, item 1) — decisão de UX/negócio pendente, mesma natureza da pendência já registrada na Etapa 3 para Subetapas.
5. **Interface Excel de Fornecedores/Compras** — essas entidades continuam sem aba própria; os vínculos opcionais de FINANCEIRO a elas existem só no modelo Python.
6. **Fluxo de edição/exclusão/estorno de lançamentos e pagamentos** (Seção 22) — não implementado em nenhuma camada.
7. **Regra de arredondamento de exibição** além da formatação de moeda "R$ 0,00" — não definida (mesma pendência já registrada na Etapa 3 para valores de orçamento).

---

## 16. Riscos

1. **Vínculo incorreto por Descrição duplicada** (Limitação 1) — mesmo padrão de risco já aceito nas Etapas 2/3 para nomes de Subetapa/Serviço; recomenda-se tratamento de UX unificado para todos os dropdowns baseados em nome amigável antes de uso em obra real com muitos lançamentos.
2. **Situação/cancelamento sem efeito nos totais** (Limitação 2) — se o Operador usar o campo "Situação" informalmente para indicar cancelamento, os totais financeiros **não refletirão** essa intenção até que um domínio fechado seja homologado; risco de relatório financeiro divergente da intenção do Operador se este campo for usado sem essa ressalva ser comunicada a ele.
3. **Indicador de estouro visível ao Cliente** (Limitação 3) — se o arquivo for compartilhado com o Cliente antes de existir controle de acesso por perfil, o indicador "Operador-only" ficará visível a ele, contrariando a Seção 30 da especificação. Recomenda-se não compartilhar o arquivo com o Cliente até a camada de Perfis/Acesso (SEC_001) ser construída.

---

## 17. Próximo passo

Conforme a ordem já registrada em relatórios anteriores, esta etapa completa a base operacional do módulo Financeiro (Aporte/Outras Entradas/Despesa-Custo/Outras Saídas, Pagamentos, Orçamento Vigente parcial, Saldo Orçamentário, % Consumido, Saldo de Caixa). Antes de avançar, recomenda-se:

1. Homologar o domínio fechado de "Situação"/cancelamento de FINANCEIRO (Limitação 2/Pendência 2) antes de um uso real que dependa dessa distinção nos totais.
2. Homologar a mitigação de nomes duplicados nos dropdowns baseados em nome amigável (Subetapas, Serviços e agora Lançamentos Financeiros) — pendência acumulada desde a Etapa 3.
3. Só então iniciar, mediante nova autorização, o módulo Alterações (para completar o Orçamento Vigente, REG-017) ou a camada de Perfis/Acesso (para tornar o indicador de estouro efetivamente Operador-only).

Conforme a Seção 42 da homologação desta etapa: **CONSTRUIR → TESTAR → AUDITAR → CORRIGIR → RELATAR → PARAR.** Nenhum módulo adicional (Planejamento, Cronograma, Execução, Compras, Alterações, Dashboard, Looker Studio, interface final completa) foi iniciado.

## 18. Checklist de conclusão da Etapa 4

- [x] estrutura financeira criada
- [x] Aporte implementado
- [x] Outras Entradas implementadas
- [x] Despesa/Custo implementado
- [x] Outras Saídas implementadas
- [x] Custo Realizado separado de Pagamento
- [x] pagamentos parciais suportados
- [x] múltiplos pagamentos suportados
- [x] A Pagar calculado
- [x] Saldo de Caixa calculado
- [x] Orçamento Vigente calculado (parcial: Inicial + Aportes; Alterações [H])
- [x] Saldo Orçamentário calculado
- [x] % Consumido calculado
- [x] estouro de orçamento não bloqueia
- [x] divisão por zero tratada
- [x] Operador mantém autonomia (nenhum bloqueio artificial de cancelamento/edição foi criado)
- [x] Cliente não acessa financeiro operacional (nenhuma interface para Cliente foi construída; restrição técnica por perfil permanece pendência registrada — Seção 15, item 3)
- [x] IDs técnicos permanecem internos (colunas ocultas)
- [x] workbook V3 criado
- [x] V1 e V2 preservados (hashes MD5 confirmados idênticos antes/depois)
- [x] testes anteriores continuam passando (162 passed, 0 failed no total)
- [x] testes financeiros criados (42 novos)
- [x] cenários A–J executados
- [x] workbook validado (estrutural + **abertura real em Excel via COM**, Seção 13.1)
- [x] relatório criado (este arquivo)
- [x] pendências registradas (Seção 15)
- [x] nenhuma regra não homologada foi inventada
- [x] git status verificado (Seção 19)
- [x] nenhum commit/push realizado

---

## 19. Git — estado final

`git status` antes desta etapa mostrava a árvore de trabalho limpa (branch `main`, sincronizada com `origin/main`, checkpoint `e5200b9`). Após a implementação, `git status` mostra os arquivos novos/alterados desta etapa (código em `src/financeiro/`, `config/`, `src/modelo/`, `src/base_dados/`, `src/excel/`, `src/excecoes.py`; testes novos em `testes/`; script novo/depreciado em `scripts/`; workbook novo em `dados/`; este relatório em `relatorios/`; e as edições em `DAD_001`/`REG_001`). **Nenhum commit ou push foi realizado.** A decisão de commit/push permanece com o responsável pelo projeto, conforme a Seção 40 desta homologação.
