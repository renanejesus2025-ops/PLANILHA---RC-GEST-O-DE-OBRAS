# ALTERAÇÕES — ETAPA 5
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-17
**Fase:** Módulo ALTERAÇÕES (domínio fechado de Tipo e Status de Aprovação) — fecha REG-017 (Orçamento Vigente completo: Orçamento Inicial + Aportes + Alterações Formais Aprovadas). Nenhum módulo de Planejamento, Compras, Execução/Medições, Pendências, Dashboard Gerencial ou Perfis/Acesso foi construído, conforme limite de escopo explícito.
**Metodologia:** protocolo "Superpowers" — brainstorming → plano técnico escrito → implementação por subagentes (uma unidade por task, com revisão do coordenador entre cada uma) → validação → auditoria → relatório. Ver `relatorios/PLANO_ETAPA_5_ALTERACOES_V1.md` para o plano completo (5 tasks, código integral de cada step).
**Checkpoint Git de partida:** árvore de trabalho limpa, sincronizada com `origin/main` (após a Etapa 4).
**Git ao final desta etapa:** nenhum commit ou push foi realizado. `git status` verificado antes e depois (Seção 19 deste relatório).

---

## 1. Objetivo

Fechar as duas lacunas que o relatório da Etapa 4 deixou explicitamente registradas em REG-012 e REG-017: (a) dar ao campo "Status de Aprovação" de ALTERAÇÕES um domínio fechado, sem inventar um fluxo de aprovação que nenhuma fonte definia; (b) completar a fórmula do Orçamento Vigente, que desde a Etapa 4 somava apenas Orçamento Inicial + Aportes, com a terceira parcela — Alterações Formais Aprovadas — mantendo o mesmo princípio "sistema informa, Operador decide" já usado no Financeiro.

---

## 2. Processo desta etapa (brainstorming → plano → subagentes)

Diferente das Etapas 3/4, nesta rodada o escopo da "Etapa 5" **não veio de um prompt de homologação explícito** — foi definido em conjunto com o responsável pelo projeto via um processo de brainstorming (decisão sobre qual módulo construir, entre Alterações/Planejamento/Compras/Perfis-Acesso, e as 4 decisões de negócio que travavam REG-012/REG-017). As decisões homologadas nesse brainstorming estão registradas no cabeçalho do `PLANO_ETAPA_5_ALTERACOES_V1.md` ("Spec") e reproduzidas na Seção 6 deste relatório.

A implementação seguiu um plano técnico escrito antes de qualquer código (5 tasks, cada uma com código completo, sem placeholders) e foi executada por um subagente implementador por task, com revisão direta do coordenador (leitura do diff/arquivos + execução dos testes) entre cada uma — nenhum commit foi feito por nenhum subagente, e nenhuma task avançou sem revisão aprovada.

---

## 3. Arquivos criados

```
src/alteracoes/
├── __init__.py
├── calculos.py                      (total_alteracoes_aprovadas)
└── movimentos.py                    (registrar_alteracao)

scripts/
└── gerar_arquivo_obra_modelo_v4.py  (gera o arquivo entregável desta etapa)

testes/
├── test_alteracoes.py               (18 testes — domínio/entidade/Motor de Cálculos)
└── test_excel_alteracoes.py         (7 testes — fórmulas/Excel)

dados/
└── GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx   (arquivo entregável desta etapa)

relatorios/
├── PLANO_ETAPA_5_ALTERACOES_V1.md   (plano técnico desta etapa)
└── ALTERACOES_ETAPA_5_V1.md         (este arquivo)
```

## 4. Arquivos alterados

**Código (Etapas 1–4, estendido — nenhum comportamento anterior removido):**
- `src/validacoes/numeros.py` — nova função `validar_numero` (numérico, SEM exigir não-negativo — diferente de `validar_numero_nao_negativo`).
- `src/modelo/enums.py` — novos `TipoAlteracao` (Escopo/Prazo/Orçamento) e `StatusAprovacaoAlteracao` (Pendente/Aprovada/Rejeitada, com `.integra_orcamento_vigente`).
- `src/modelo/entidades.py` — `Alteracao`: `tipo_alteracao`/`status_aprovacao` passam de `Optional[str]` para os Enums fechados; `impacto_orcamento`/`impacto_prazo_dias` validados por `validar_numero` em `__post_init__`.
- `src/financeiro/calculos.py` — `orcamento_vigente` passa a somar 3 parcelas (antes 2); import de `total_alteracoes_aprovadas`; docstring do módulo atualizada.
- `src/excel/construtor_workbook.py` — nova aba "Alterações"; aba "Resumo Financeiro" ganha a linha "Alterações Aprovadas" e a fórmula de "Orçamento Vigente" evolui de 2 para 3 parcelas.
- `scripts/gerar_arquivo_obra_modelo_v3.py` — **depreciado**: mesmo padrão já aplicado aos scripts V1/V2 nas Etapas 3/4 (evitar sobrescrita silenciosa da V3 com a estrutura nova).
- `testes/test_excel_construtor.py` — `ABAS_ESPERADAS` ganha `"Alterações"` (entre "Pagamentos" e "Resumo Financeiro").
- `testes/test_excel_financeiro.py` — 3 testes que fixavam números de linha literais do Resumo Financeiro foram reescritos usando busca por rótulo (mesmo padrão que o 4º teste do arquivo já usava) — a numeração de linha mudou por causa da linha nova "Alterações Aprovadas".

**Documentação formal:**
- `05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md` — Revisão 8: REG-012 reescrita (de [H] para [D]); nota da Revisão 7 em REG-017 substituída (de "escopo parcial" para "completo"); nova nota em REG-006.
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md` — Revisão 8: entidade ALTERAÇÕES reescrita (domínios fechados, obrigatoriedade corrigida para refletir a implementação real).
- **Pares DOCX não foram atualizados** — mesma pendência de forma já registrada nas Etapas 1–4.

---

## 5. Modelo de dados

`Alteracao` (já existia desde a Etapa 1) passa de campos texto-livre para domínios fechados nos dois campos que travavam REG-012/REG-017:

| Campo | Antes (Etapa 4) | Agora (Etapa 5) |
|---|---|---|
| `tipo_alteracao` | `Optional[str]` | `Optional[TipoAlteracao]` (Escopo/Prazo/Orçamento) |
| `status_aprovacao` | `Optional[str]` | `Optional[StatusAprovacaoAlteracao]` (Pendente/Aprovada/Rejeitada) |
| `impacto_orcamento` | `Optional[float]`, sem validação | `Optional[float]`, validado por `validar_numero` (numérico, sinal livre) |
| `impacto_prazo_dias` | `Optional[int]`, sem validação | `Optional[int]`, mesma validação |

---

## 6. Decisões homologadas nesta rodada (brainstorming)

1. **Status de Aprovação = domínio fechado Pendente/Aprovada/Rejeitada** — só Aprovada soma no Orçamento Vigente.
2. **Sem workflow de aprovação** — o Operador seleciona o Status diretamente, sem múltiplas etapas, sem aprovador distinto, sem justificativa obrigatória (mesmo princípio "sistema informa, Operador decide" já usado no Financeiro, REG-032).
3. **Tipo de Alteração = domínio fechado Escopo/Prazo/Orçamento** — qualquer Tipo pode ter Impacto no Orçamento preenchido; a soma é pelo valor do campo, não pelo Tipo.
4. **Nenhuma automação Escopo→Serviços/Orçamento** — uma Alteração de Escopo é só registro informativo (mesmo princípio já usado para Compra→Financeiro na Etapa 4).

Nenhuma outra decisão [P]/[H] pré-existente foi promovida a [D] por extensão.

---

## 7. Regras implementadas

| Regra | Fórmula | Onde |
|---|---|---|
| Alterações Aprovadas | Σ Impacto no Orçamento onde Status = Aprovada | `total_alteracoes_aprovadas` / Resumo Financeiro (SUMIFS) |
| Orçamento Vigente (completo) | Orçamento Inicial + Aportes + Alterações Aprovadas | `orcamento_vigente` / Resumo Financeiro!Orçamento Vigente |

**Impacto com sinal (diferente de Financeiro):** `impacto_orcamento`/`impacto_prazo_dias` aceitam valores negativos — uma Alteração aprovada pode **reduzir** o orçamento ou **antecipar** um prazo. Validado apenas quanto a ser numérico (`validar_numero`), nunca quanto ao sinal — ao contrário de `Financeiro.valor`/`Pagamento.valor` (Etapa 4, REG-030), cujo sinal é sempre dado pelo Tipo.

**Não-exclusão automática:** Alterações Pendentes/Rejeitadas permanecem na base, visíveis na aba Excel, apenas fora da soma — mesmo princípio já usado para Serviços Cancelados (Etapa 3) e para `situacao` de Financeiro (Etapa 4).

---

## 8. Motor de Cálculos

`src/alteracoes/calculos.py:total_alteracoes_aprovadas(base, id_obra)` — Σ `impacto_orcamento` das Alterações da Obra com `status_aprovacao is StatusAprovacaoAlteracao.APROVADA`, tratando `impacto_orcamento is None` como 0.

`src/financeiro/calculos.py:orcamento_vigente` — evoluiu de `total_previsto_obra + total_aportes` para `total_previsto_obra + total_aportes + total_alteracoes_aprovadas`, sem alterar nenhuma outra função do módulo Financeiro (confirmado por `git diff` isolado a essa função + import + docstring).

---

## 9. Integração com Orçamento Vigente (REG-017 completo)

Esta é a entrega central da etapa: **REG-017 estava parcialmente implementado desde a Etapa 4** (nota explícita na Revisão 7: "apenas a parcela Orçamento Inicial + Aportes está implementada"). A partir desta etapa, a fórmula homologada em 2026-09-16 soma de fato as 3 parcelas — validado não apenas por teste unitário Python, mas por **recálculo real em Excel** (Seção 12).

No Excel, a aba Resumo Financeiro ganhou uma linha "Alterações Aprovadas" (fórmula `SUMIFS` sobre a aba Alterações, filtrando por Status = "Aprovada") entre "Aportes" e "Orçamento Vigente"; a fórmula de "Orçamento Vigente" passou de `=B{inicial}+B{aportes}` para `=B{inicial}+B{aportes}+B{alteracoes_aprovadas}`.

---

## 10. Interface Excel

Nova aba **Alterações**, mesmo padrão estrutural das abas Financeiro/Pagamentos (Etapa 4): colunas de entrada (Tipo — dropdown de 3 valores; Data; Descrição; Impacto no Orçamento — moeda, **sem** validação de sinal; Impacto no Prazo — dias, sem validação de sinal; Status de Aprovação — dropdown de 3 valores; Solicitante) e ID/ID_Obra ocultos por fórmula (mesmo padrão de vínculo técnico sempre-fórmula das demais abas).

---

## 11. Testes criados

**25 testes novos** (18 em `testes/test_alteracoes.py` + 7 em `testes/test_excel_alteracoes.py`):

| Área | Testes |
|---|---|
| Domínio (3 tipos, 3 status, elegibilidade) | `test_tres_tipos_de_alteracao_homologados`, `test_tres_status_de_aprovacao_homologados`, `test_apenas_status_aprovada_integra_orcamento_vigente` |
| Sinal livre nos campos de impacto | `test_impacto_no_orcamento_negativo_e_permitido`, `test_impacto_no_prazo_negativo_e_permitido` |
| Validação numérica (rejeita não-numérico, aceita negativo) | `test_impacto_no_orcamento_nao_numerico_e_rejeitado`, `test_impacto_no_prazo_nao_numerico_e_rejeitado` (4 casos cada) |
| Alteração sem impacto informado | `test_alteracao_sem_impacto_informado_e_permitida` |
| Motor de Cálculos | `test_soma_apenas_alteracoes_aprovadas`, `test_alteracao_aprovada_com_impacto_negativo_reduz_a_soma`, `test_alteracao_sem_impacto_no_orcamento_nao_afeta_a_soma`, `test_orcamento_vigente_completo_soma_inicial_aportes_e_alteracoes_aprovadas` |
| Excel — aba Alterações e Resumo Financeiro | `test_aba_alteracoes_existe`, `test_cabecalho_da_aba_alteracoes`, `test_dropdown_de_tipo_de_alteracao_tem_3_valores`, `test_dropdown_de_status_de_aprovacao_tem_3_valores`, `test_impacto_no_orcamento_aceita_negativo_sem_validacao_de_sinal`, `test_resumo_financeiro_orcamento_vigente_soma_3_parcelas`, `test_resumo_financeiro_alteracoes_aprovadas_usa_sumifs_por_status` |

## 12. Quantidade total de testes e resultado

```
.venv/Scripts/python.exe -m pytest -v
```
**187 testes coletados, 187 passed, 0 failed** (Etapas 1–4: 162 · Etapa 5: 25). Todos os testes das Etapas 1–4 continuam passando — os únicos ajustados foram os 3 de `test_excel_financeiro.py` que dependiam de números de linha do Resumo Financeiro, agora usando busca por rótulo (mesmo tipo de ajuste mecânico já registrado nas Etapas 3/4 quando a estrutura evolui por decisão explícita da homologação corrente).

### 12.1 Validação real em Excel (não apenas texto de fórmula)

Este ambiente possui Microsoft Excel instalado (confirmado também na Etapa 4). Foi montado um cenário combinado via `BaseDados`/`construir_workbook` — Orçamento Inicial 100.000; Aporte 20.000; Alteração tipo Orçamento **Aprovada** com impacto +15.000; Alteração tipo Orçamento **Pendente** com impacto +99.999 — salvo em arquivo temporário no scratchpad da sessão (nunca no repositório), aberto via automação COM (`Excel.Application`), recalculado (`CalculateFullRebuild`) e lido de volta:

| Célula (Resumo Financeiro) | Esperado (Python) | Lido do Excel real |
|---|---|---|
| Orçamento Inicial | 100.000 | 100.000 |
| Aportes | 20.000 | 20.000 |
| **Alterações Aprovadas** | 15.000 | **15.000** (a Pendente de 99.999 corretamente excluída) |
| **Orçamento Vigente** | 135.000 | **135.000** |
| Saldo Orçamentário | 135.000 | 135.000 |
| Saldo de Caixa | 20.000 | 20.000 |
| Estouro de Orçamento | NÃO | NÃO |

Todos os valores conferem exatamente. O processo Excel aberto pela automação foi encerrado corretamente ao final (`Quit`/`ReleaseComObject`), sem afetar um processo `EXCEL.EXE` pré-existente e alheio a esta tarefa que já estava rodando no ambiente; o arquivo de teste temporário foi apagado do scratchpad.

---

## 13. Resultado

Todos os itens da Seção 6 (decisões homologadas) foram implementados e testados: domínio fechado de Status de Aprovação sem workflow, domínio fechado de Tipo de Alteração, campos de impacto com sinal livre, e nenhuma automação sobre Serviços/Orçamento. REG-012 e REG-017 estão, a partir desta etapa, completamente [D] (documentados/homologados) para o que foi pedido nesta rodada.

---

## 14. Limitações

1. **Nenhuma restrição de perfil sobre quem pode aprovar/rejeitar uma Alteração** — qualquer pessoa com acesso ao arquivo pode alterar o Status. Mesma pendência estrutural já registrada para o indicador de Estouro de Orçamento (Etapa 4) e para o Ajuste Manual de Orçamento (Etapa 3) — depende de uma camada de Perfis/Acesso que ainda não foi construída em nenhuma etapa.
2. **"Impacto no Prazo" é puramente informativo** — não há módulo de Planejamento/Cronograma para consumir esse dado; nenhuma consolidação de prazo foi criada.
3. **Nenhuma validação de que uma Alteração de Escopo referencie um Serviço específico** — o campo não existe no modelo (decisão homologada explicitamente nesta etapa: nenhuma automação Escopo→Serviços). Uma Alteração de Escopo hoje é só texto (Descrição) + Impacto opcional.
4. **Sem motor de planilha para TODAS as fórmulas do workbook** — a validação real em Excel (Seção 12.1) cobriu o cálculo agregado do Resumo Financeiro com um cenário de exemplo; não foi uma verificação exaustiva célula-a-célula das ~30 linhas-modelo da aba Alterações.

---

## 15. Pendências (registradas, não resolvidas)

1. **Mecanismo técnico de restrição de perfil** sobre aprovação de Alterações, ajuste manual de orçamento e indicador de estouro — depende de SEC_001, ainda [H] (herdada das Etapas 3/4).
2. **Domínio fechado de Situação/cancelamento de FINANCEIRO** (Etapa 4, Seção 23) — ainda [H], não tocado nesta etapa.
3. **Integração de "Impacto no Prazo" com Planejamento/Cronograma** — módulo de Planejamento ainda não construído.
4. **Automação Escopo→Serviços/Orçamento** — deliberadamente não implementada (decisão homologada nesta rodada); permanece como possível evolução futura, mediante nova homologação.
5. **Ambiguidade de nomes duplicados nos dropdowns** (herdada das Etapas 3/4, Subetapas/Lançamentos Financeiros) — não se aplica aqui porque a aba Alterações não usa dropdown de nome amigável para vínculo (referencia só a própria Obra via `ID_Obra` técnico, sem seleção manual de vínculo).

---

## 16. Riscos

1. **Qualquer Operador pode aprovar/rejeitar uma Alteração de qualquer valor** (Limitação 1) — em uma obra real com múltiplos usuários, isso pode gerar aprovações não intencionais até que a camada de Perfis/Acesso exista. Recomenda-se tratar isso como prioridade antes de um uso multiusuário real.
2. **Divergência entre a intenção do Operador e o campo "Situação" de Financeiro** (risco já registrado na Etapa 4, inalterado) — segue sem solução nesta etapa.
3. **Uso indevido do campo "Impacto no Orçamento" para fins de Escopo/Prazo** — como a soma no Orçamento Vigente é pelo VALOR do campo, não pelo Tipo, um Operador que preencha esse campo em uma Alteração de Escopo/Prazo por engano ainda afetará o Orçamento Vigente. Isso é intencional (decisão homologada: "qualquer Tipo pode ter Impacto no Orçamento"), mas vale reforçar essa nuance no treinamento do Operador.

---

## 17. Próximo passo

Conforme a ordem já registrada nos relatórios anteriores, esta etapa fecha o Orçamento Vigente completo (REG-017). Antes de avançar, recomenda-se:

1. Priorizar a camada de Perfis/Acesso (SEC_001) — ela já acumula 3 pendências estruturais (Ajuste Manual de Orçamento, Estouro de Orçamento, Aprovação de Alteração) que dependem exclusivamente dela para se tornarem tecnicamente restritas, não apenas convenções de especificação.
2. Só então iniciar, mediante nova autorização e novo brainstorming, o próximo módulo — candidatos já identificados no brainstorming desta etapa: **Planejamento** (próximo na ordem de prioridade do AGENTS.md §12) ou **Compras** (que traz Fornecedores consigo).

## 18. Checklist de conclusão da Etapa 5

- [x] domínio fechado do Tipo de Alteração implementado
- [x] domínio fechado do Status de Aprovação implementado (sem workflow)
- [x] Impacto no Orçamento aceita valor negativo (delta com sinal)
- [x] Impacto no Prazo aceita valor negativo
- [x] nenhuma Alteração é excluída da base (Pendente/Rejeitada permanecem)
- [x] Orçamento Vigente completo (3 parcelas) calculado em Python
- [x] Orçamento Vigente completo calculado em Excel (fórmula + validado com dados reais)
- [x] nenhuma automação Escopo→Serviços/Orçamento foi criada
- [x] aba Alterações criada no Excel
- [x] Resumo Financeiro atualizado
- [x] workbook V4 criado
- [x] V1, V2 e V3 preservados (hash MD5 idêntico)
- [x] testes anteriores continuam passando (187 passed, 0 failed no total)
- [x] testes novos criados (25)
- [x] workbook validado (estrutural + real em Excel via COM)
- [x] relatório criado (este arquivo)
- [x] plano técnico criado e seguido (`PLANO_ETAPA_5_ALTERACOES_V1.md`)
- [x] implementação por subagentes, com revisão entre cada task
- [x] pendências registradas (Seção 15)
- [x] nenhuma regra não homologada foi inventada
- [x] git status verificado (Seção 19)
- [x] nenhum commit/push realizado

---

## 19. Git — estado final

`git status` antes desta etapa mostrava a árvore de trabalho limpa (sincronizada com `origin/main`, após a Etapa 4). Após a implementação, `git status --short` mostra:

```
 M 02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md
 M 05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md
 M scripts/gerar_arquivo_obra_modelo_v3.py
 M src/excel/construtor_workbook.py
 M src/financeiro/calculos.py
 M src/modelo/entidades.py
 M src/modelo/enums.py
 M src/validacoes/numeros.py
 M testes/test_excel_construtor.py
 M testes/test_excel_financeiro.py
?? dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx
?? relatorios/PLANO_ETAPA_5_ALTERACOES_V1.md
?? scripts/gerar_arquivo_obra_modelo_v4.py
?? src/alteracoes/
?? testes/test_alteracoes.py
?? testes/test_excel_alteracoes.py
```

Exatamente os arquivos esperados (Seções 3/4 deste relatório) — nada além disso. **Nenhum commit ou push foi realizado.** A decisão de commit/push permanece com o responsável pelo projeto.
