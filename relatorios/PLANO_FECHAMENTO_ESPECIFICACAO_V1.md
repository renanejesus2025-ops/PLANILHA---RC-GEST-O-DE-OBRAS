# PLANO DE FECHAMENTO DE ESPECIFICAÇÃO — V1
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-16
**Fase:** Fechamento da Especificação V1 (pós-auditoria, pré-construção).
**Escopo desta fase:** correção e consolidação da documentação corrente. Nenhum Excel, workbook, código Python, dashboard, fórmula de produção, autenticação ou biblioteca foi criado/instalado. Nenhum arquivo do kit de marca ou do histórico foi alterado, movido, renomeado ou apagado.

Este relatório consolida o trabalho feito sobre `AUDITORIA_PRE_CONSTRUCAO_V1.md` e documenta o estado resultante em `DAD_001`, `REG_001`, `SEC_001`, `DSG_001`, `UI_001` e `CRN_001`.

---

## 1. Lacunas encontradas (herdadas da auditoria)

1. Ausência de dicionário de dados executável (campos, tipos, relacionamentos).
2. Ausência de regras de negócio com fórmula e threshold.
3. Matriz de permissões existente apenas no histórico, não promovida ao corrente.
4. Mecanismo de autenticação/proteção do Excel indefinido.
5. DSG_001 atribuía ao manual de marca componentes de UI que ele não contém.
6. Cores/tipografia da marca não transcritas em texto pesquisável.
7. Ambiguidade da palavra "Cronograma" (produto vs. projeto de desenvolvimento).
8. Conceito de "Aportes" citado sem nunca ter sido documentado.

## 2. Lacunas resolvidas documentalmente nesta fase

| Lacuna | Como foi tratada | Resultado |
|---|---|---|
| Dicionário de dados | `DAD_001` reescrito com 13 entidades (OBRAS, ETAPAS, SUBETAPAS, SERVIÇOS/ORÇAMENTO, PLANEJAMENTO, FORNECEDORES, COMPRAS, FINANCEIRO, EXECUÇÃO/MEDIÇÕES, ALTERAÇÕES, PENDÊNCIAS, ATUALIZAÇÕES, DOCUMENTOS), cada uma com finalidade, campos, tipo, obrigatoriedade, origem, calculado/digitado, relacionamento, observação e status [D]/[P]/[H]. | Lacuna **estruturada**, não eliminada — a maior parte dos campos ficou [P] (proposta) ou [H] (a homologar), porque não havia fonte para declará-los [D]. Isso é o resultado correto: a especificação agora é legível e priorizável, não inventada. |
| Regras de negócio | `REG_001` reescrito com 16 regras formais (REG-001 a REG-016), cada uma com Entrada/Condição/Resultado/Status/Teste necessário. | Fórmulas coerentes com o que já era dito em prosa (ex.: Saldo = Previsto − Realizado) foram propostas como [P]; todo threshold numérico (%, dias, valor) ficou [H], sem exceção. |
| Matriz de permissões | `SEC_001` promoveu a matriz do histórico (`PERFIS_DE_ACESSO_E_VISOES_V5`/`_V6`) para o documento corrente, mapeando para VISUALIZAR/EDITAR/SEM ACESSO. | Áreas já presentes no histórico: promovidas como [D]. Áreas ausentes do histórico (Painel Gerencial, Fornecedores, Atualizações): marcadas [H], **sem inventar valor**. |
| Autenticação/proteção | `SEC_001` Seção 4 documenta as limitações reais do Excel puro (proteção de planilha contornável, ausência de login nativo, abas ocultas reversíveis) e lista 4 opções, sem escolher nenhuma. | Marcado explicitamente **[H] MECANISMO DE AUTENTICAÇÃO/PROTEÇÃO**. |
| DSG_001 x manual | `DSG_001` reescrito em 3 blocos: A (Identidade Oficial — só o que está no PDF), B (Proposta de Design do Produto — cards/botões/menus/tabelas/alertas/campos, marcados [P]), C (Itens a Homologar). | O manual deixou de ser citado como fonte de componentes de interface que não possui. |
| Cores/tipografia | `DSG_001` Seção A.5/A.6 transcreve as 4 cores HEX (`#ffffff`, `#abb6ba`, `#5a5f5b`, `#0f1c2c`) e a tipografia (Gravesend Sans) diretamente do PDF. | Valores agora pesquisáveis em texto, não só dentro do PDF/AI/PNG. |
| Ambiguidade "Cronograma" | `UI_001` passa a usar "Cronograma da Obra" (tela do produto); `CRN_001` passa a se chamar "Cronograma de Execução do Projeto" (prazo de desenvolvimento). Pasta `16_CRONOGRAMA_E_EXECUCAO` não foi renomeada nem movida. | Ambiguidade de nomenclatura resolvida na documentação; ambos os documentos agora se referenciam explicitamente. |
| "Aportes" | `DAD_001` (entidade FINANCEIRO) e `REG_001` (REG-006) registram o conceito como **[C] CONFLITO** entre "Saldo Orçamentário" (previsto × realizado) e um possível "Saldo de Caixa" (aportes × despesas pagas), sem escolher uma interpretação. | Conflito **documentado, não resolvido** — decisão pendente do responsável (ver Seção 3). |

## 3. Decisões ainda pendentes (a homologar pelo responsável do projeto)

1. **Aportes vs. Saldo Orçamentário** — são o mesmo indicador, dois indicadores distintos, ou um financia o outro? (REG-006, DAD_001/FINANCEIRO — [C]).
2. Formato do ID técnico de cada entidade (sequencial? alfanumérico por obra?) — (DAD_001, "Regra sobre IDs").
3. SUBETAPAS: tabela própria, nível dentro de ETAPAS, ou nível dentro de SERVIÇOS/ORÇAMENTO?
4. Método de ponderação de Peso de Etapa/Subetapa (REG-008) e fórmula de % de execução física (REG-007).
5. Thresholds numéricos de alerta: desvio orçamentário (REG-013), atraso de cronograma (REG-014), gradação de saldo negativo (REG-015).
6. SLA de Pendência em dias (REG-011) e critério de prioridade.
7. Fluxos de aprovação de Compra (REG-010) e de Alteração (REG-012).
8. Comportamento de integridade referencial: bloqueio vs. cascata na exclusão (REG-002).
9. Comportamento de medição acima de 100% do orçado: bloqueio vs. alerta (REG-009).
10. Domínios fechados listados em `DAD_001` (Status da Obra, Status da Etapa, Unidade de Medida, Categoria de Fornecedor, Forma de Pagamento, Tipo de Alteração etc.).
11. Mecanismo de autenticação/proteção do Excel (`SEC_001` Seção 4 — 4 opções apresentadas, nenhuma escolhida).
12. Permissões das áreas Painel Gerencial, Fornecedores e Atualizações (ausentes da matriz histórica).
13. Significado operacional de "Protegido" para a área Base/Fórmulas mesmo para o Administrador/Operador.
14. Cores semânticas de alerta (sucesso/erro/aviso), fallback tipográfico para Excel, e conjunto de ícones de interface (`DSG_001` Seção C).
15. Nomenclatura definitiva das abas técnicas internas (BASE/CADASTROS/DOMÍNIOS/CÁLCULOS/CONTROLE/AUDITORIA) — ainda não tratada em nenhum documento corrente.
16. Fronteira entre ATUALIZAÇÕES, PENDÊNCIAS e EXECUÇÃO/MEDIÇÕES (sobreposição conceitual registrada em DAD_001).
17. Mecanismo de armazenamento de arquivos da entidade DOCUMENTOS (local vs. nuvem).

## 4. Conflitos

| Conflito | Onde está registrado | Natureza |
|---|---|---|
| Saldo Orçamentário × "Aportes"/Saldo de Caixa | `REG_001` REG-006, `DAD_001`/FINANCEIRO | Conceitual — dois indicadores financeiros possivelmente distintos, nunca reconciliados em nenhuma fonte |
| `ARQ_002_ARQUITETURA_DO_SISTEMA.md` (histórico, 5 camadas) × arquitetura corrente (7 camadas) | Já registrado na auditoria; não requereu ação nesta fase porque a documentação corrente já prevalece e o histórico não foi alterado | Já resolvido de fato pela documentação corrente — mantido como nota histórica |

Nenhum conflito foi resolvido unilateralmente pelo agente. Ambos permanecem sinalizados para decisão humana.

## 5. Itens [D] DOCUMENTADO (resumo)

- Arquitetura em 7 camadas + perfis como camada transversal.
- Dois perfis oficiais (Administrador/Operador, Cliente).
- Lista de entidades centrais e auxiliares (nomes).
- Exemplos reais de etapas/serviços (Alvenaria, Elétrica, Cimento, Reboco etc.).
- Identidade visual oficial completa: logo, submarca, ícone, variações, 4 cores HEX, tipografia Gravesend Sans, destaques, templates, moodboard.
- Matriz de permissões por área para as 10 áreas presentes no histórico (com nuances preservadas em observação).
- Princípio "abas ocultas não são segurança suficiente".
- Lista de verificações de auditoria (REG-016).

## 6. Itens [P] PROPOSTA (resumo)

- Todos os campos de todas as 13 entidades do `DAD_001` (finalidade, tipo, obrigatoriedade etc.) que não vinham literalmente de uma fonte.
- Fórmulas de REG-003 (Orçamento Previsto), REG-004 (Custo Realizado, parcial), REG-005 (Saldo Orçamentário), REG-009 (limite de medição, princípio).
- Componentes de UI do produto (cards, botões, menus, tabelas, alertas, campos) — `DSG_001` Seção B.
- Nomenclatura "Cronograma da Obra".

## 7. Itens [H] HOMOLOGAR (resumo)

Ver lista completa na Seção 3 (17 decisões pendentes). Resumo por documento:
- `DAD_001`: formato de ID, existência de SUBETAPAS como entidade, todos os domínios fechados, mecanismo de armazenamento de Documentos.
- `REG_001`: todos os thresholds numéricos, todos os fluxos de aprovação, comportamento de integridade referencial.
- `SEC_001`: mecanismo de autenticação/proteção, permissões de 3 áreas ausentes do histórico, significado operacional de "Protegido".
- `DSG_001`: cores semânticas, fallback de fonte, ícones de interface, grid/espaçamento/estados.
- `UI_001`/`CRN_001`: nomenclatura das abas técnicas internas (ainda não tratada).

## 8. Riscos

1. **Risco de escopo:** homologar as 17 decisões pendentes é, em si, um esforço não trivial — subestimar esse tempo pode pressionar o prazo de 21 dias do `CRN_001` (Cronograma de Execução do Projeto).
2. **Risco de segurança:** qualquer construção da camada de proteção antes da decisão da Seção 4 do `SEC_001` corre o risco de fixar uma solução frágil (ex.: senha única de planilha) como se fosse definitiva.
3. **Risco de retrabalho de dados:** iniciar a base técnica do Excel antes de homologar formato de ID e a decisão sobre SUBETAPAS pode obrigar a refazer chaves e relacionamentos.
4. **Risco financeiro-conceitual:** construir o módulo Financeiro sem resolver o conflito Aportes × Saldo Orçamentário pode gerar um indicador que não reflete a realidade de caixa do cliente.
5. **Risco de fonte:** publicar o Excel com "Gravesend Sans" sem fallback definido pode quebrar a identidade visual em máquinas onde a fonte não está instalada.
6. **Risco de governança documental:** os pares DOCX das 5 seções revisadas (`DAD_001`, `REG_001`, `SEC_001`, `DSG_001`, `UI_001`, `CRN_001`) **ficaram desatualizados em relação ao novo conteúdo dos `.md`** — esta fase não gerou os `.docx` correspondentes porque isso exigiria geração de arquivo binário fora do escopo de "somente documentação de especificação" e sem instalar bibliotecas (proibido nesta fase). É uma pendência de forma, não de conteúdo, mas deve ser resolvida antes de uma nova rodada formal de homologação estrutural (como a que gerou `TERMO_HOMOLOGACAO_V6_3.md`).

## 9. Dependências para construção

Ordem de dependência real (nenhuma etapa pode começar de forma sólida sem a anterior):

1. Homologar as 17 decisões da Seção 3.
2. Fechar os domínios fechados (listas de status/categorias) do `DAD_001`.
3. Fechar os thresholds do `REG_001`.
4. Escolher o mecanismo de autenticação/proteção do `SEC_001`.
5. Fechar os itens [H] do `DSG_001` (cores semânticas, fallback, ícones).
6. Só então: construção da base técnica, motor de cálculos, interface, proteção, dashboard, inteligência, auditoria e testes — na ordem já recomendada em `AUDITORIA_PRE_CONSTRUCAO_V1` Seção 12.I e em `CRN_001`.

## 10. Checklist de prontidão

| Item | Pronto? |
|---|---|
| Arquitetura conceitual definida sem conflito | ✅ Sim |
| Perfis oficiais definidos | ✅ Sim |
| Identidade visual oficial transcrita (cores/tipografia) | ✅ Sim (Seção A do DSG_001) |
| Modelo de dados com entidades nomeadas | ✅ Sim |
| Modelo de dados com campos/tipos/relacionamentos homologados | ❌ Não — segue [P]/[H] |
| Regras de negócio com fórmula proposta | 🟡 Parcial — fórmulas propostas [P], thresholds [H] |
| Regras de negócio com thresholds homologados | ❌ Não |
| Matriz de permissões promovida ao corrente | 🟡 Parcial — 10 de 13 áreas |
| Mecanismo de autenticação/proteção escolhido | ❌ Não |
| Design system de produto (componentes de UI) homologado | ❌ Não — está em [P] |
| Ambiguidade "Cronograma" resolvida | ✅ Sim |
| Conflito Aportes × Saldo resolvido | ❌ Não — [C] em aberto |
| Nomenclatura de abas técnicas internas definida | ❌ Não |
| Pares DOCX atualizados | ❌ Não — pendência de forma registrada na Seção 8 |
| Excel/código/dashboard construídos | ❌ Não (fora do escopo desta fase, corretamente) |

**Conclusão do checklist:** a especificação está **consolidada e legível**, mas **não está homologada em conteúdo** — ainda restam 17 decisões de negócio/técnicas antes de iniciar a construção, consistente com a instrução de não transformar proposta em requisito.

---

## Validação executada

- Referências a `Rafael Xonchim.pdf` e a `PERFIS_DE_ACESSO_E_VISOES_V5/V6.md` conferidas contra o sistema de arquivos — caminhos existem, sem referência quebrada.
- Nenhuma duplicidade de conteúdo entre os 6 documentos revisados: cada um trata do seu próprio domínio; os cruzamentos (ex.: `DAD_001` citando `SEC_001` para autenticação de "Autor" em Atualizações) são referências, não repetição de conteúdo.
- Consistência cruzada verificada manualmente entre `DAD_001` ↔ `REG_001` (toda entidade calculada em REG_001 existe no DAD_001), `DAD_001`/`REG_001` ↔ `SEC_001` (perfis e áreas citados são os mesmos dois perfis oficiais), `DSG_001` ↔ `UI_001` (nomenclatura "Cronograma da Obra" idêntica nos dois documentos).
- `git diff --check`: sem erros de espaço em branco (apenas avisos informativos de conversão de fim de linha LF→CRLF, esperado no Windows).
- `git status`: ver Seção "Resultado final" abaixo.
