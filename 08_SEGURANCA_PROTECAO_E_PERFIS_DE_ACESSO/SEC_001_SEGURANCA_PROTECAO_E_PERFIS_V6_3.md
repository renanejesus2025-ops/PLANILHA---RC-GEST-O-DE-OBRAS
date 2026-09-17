# Segurança, Proteção e Perfis de Acesso — V6.3 (Revisão 1 — Fechamento de Especificação V1)

**Data da revisão:** 2026-09-16
**Motivo da revisão:** `AUDITORIA_PRE_CONSTRUCAO_V1` identificou que a matriz de permissões por área existia apenas no histórico (`PERFIS_DE_ACESSO_E_VISOES_V5.md`/`_V6.md`) e não havia sido promovida ao documento corrente. Esta revisão promove essa matriz, sem inventar novas permissões, e documenta explicitamente o que ainda não está definido sobre autenticação.

## Legenda de status

[D] DOCUMENTADO · [P] PROPOSTA · [H] HOMOLOGAR · [C] CONFLITO

---

## 1. Perfis oficiais V1 — [D]

Fonte: AGENTS.md §9, histórico `PERFIS_DE_ACESSO_E_VISOES_V5.md`/`_V6.md`, `00_DOCUMENTACAO_MESTRA_V5.md`/`_V6.md`. Não há divergência entre as fontes.

1. **Administrador/Operador** — perfil único. Administra e opera as funções autorizadas do sistema: cadastra, lança, corrige, acompanha, configura o que estiver autorizado e executa auditorias.
2. **Cliente** — perfil predominantemente consultivo/gerencial. Não edita a base operacional, fórmulas, configurações ou áreas técnicas protegidas.

Nenhum terceiro perfil existe em qualquer fonte, corrente ou histórica.

## 2. Arquitetura transversal de acesso — [D]

```
Perfil → Identificação → Interface → Permissões → Proteção → Dados
```

Fonte: AGENTS.md §9/§17, `00_DOCUMENTACAO_MESTRA_V6.md`. Perfis e Acesso **não é uma etapa sequencial da arquitetura de 7 camadas** — é uma camada transversal que atua sobre todas as demais.

## 3. Matriz de permissões por área

A matriz abaixo **promove** a matriz já registrada no histórico (`PERFIS_DE_ACESSO_E_VISOES_V6.md`, idêntica em essência à V5) para o documento corrente, convertendo a redação original para as três categorias pedidas nesta revisão (VISUALIZAR / EDITAR / SEM ACESSO). Onde a redação histórica trazia uma nuance que não cabe integralmente em uma das três categorias, a nuance foi preservada na coluna Observação em vez de ser descartada. **Nenhuma permissão nova foi criada** para as áreas que já existiam no histórico.

| Área | Administrador/Operador | Cliente | Observação | Status |
|---|---|---|---|---|
| Início/Obra | EDITAR | VISUALIZAR | Histórico: "Edita" / "Consulta" | [D] |
| Painel Gerencial | — | — | **Não existe no histórico** (a matriz V5/V6 não lista esta área separadamente). Presumível apenas por analogia ao princípio geral do Cliente, mas não foi promovida — precisa ser definida e homologada, não inventada aqui. | [H] |
| Planejamento | EDITAR | VISUALIZAR | Histórico: "Edita" / "Consulta" | [D] |
| Orçamento | EDITAR | VISUALIZAR (parcial) | Histórico: "Edita" / "Indicadores autorizados" — Cliente não vê o orçamento completo, só indicadores específicos. Quais indicadores exatamente não está detalhado. | [D] (princípio) / [H] (lista exata de indicadores) |
| Fornecedores | — | — | **Não existe no histórico** como área própria da matriz. Não promovido — precisa ser definido e homologado. | [H] |
| Financeiro | EDITAR | VISUALIZAR (parcial) | Histórico: "Edita" / "Visão autorizada" — mesma ressalva do Orçamento. | [D] (princípio) / [H] (escopo exato) |
| Execução | EDITAR | VISUALIZAR | Histórico: "Edita" / "Consulta" | [D] |
| Alterações | EDITAR | VISUALIZAR (parcial) | Histórico: "Edita" / "Consulta autorizada" | [D] (princípio) / [H] (escopo exato) |
| Pendências | EDITAR | VISUALIZAR (parcial) | Histórico: "Edita" / "Consulta selecionada" — sugere que nem toda pendência é visível ao Cliente; critério de seleção não definido. | [D] (princípio) / [H] (critério de seleção) |
| Atualizações | — | — | **Não existe no histórico** como área própria da matriz. Não promovido. | [H] |
| Auditoria | EDITAR (executa) | SEM ACESSO | Histórico: "Executa" / "Sem acesso técnico". Nota: "Executa" é uma ação específica de rodar a auditoria, não uma edição de dados livre — ver observação de nuance abaixo. | [D] |
| Configurações | EDITAR | SEM ACESSO | Histórico: "Edita" / "Sem acesso" | [D] |
| Base/Fórmulas | **PROTEGIDO** (não é EDITAR livre) | SEM ACESSO | Histórico V5: "Protegido por regras" (para o próprio Administrador/Operador); histórico V6: "Protegido". Ou seja, **mesmo o Administrador/Operador não tem edição livre desta área** — o texto histórico não classifica isso como EDITAR simples. O que exatamente "protegido" significa em nível operacional (edição mediante desbloqueio? só via processo formal de alteração? nunca editável em uso normal?) não está definido. | [D] (princípio de que é protegido) / [H] (mecanismo exato) |

**Áreas ausentes da matriz histórica (Painel Gerencial, Fornecedores, Atualizações): marcadas [H] — não foram inventadas permissões para elas nesta revisão, conforme instrução explícita.**

## 4. [H] MECANISMO DE AUTENTICAÇÃO/PROTEÇÃO

**Nenhum mecanismo de autenticação foi escolhido nesta revisão.** Este documento apresenta as opções conhecidas e suas limitações, para que o responsável pelo projeto decida — o agente não decide sozinho, conforme instrução explícita.

### O que já está definido (princípio, não mecanismo) — [D]
- "Abas ocultas não são segurança suficiente" (AGENTS.md §17, histórico SEC_001/PERFIS V5-V6).
- A cadeia conceitual Perfil → Identificação → Interface → Permissões → Proteção → Dados deve existir, mas a etapa **Identificação** nunca foi detalhada em nenhuma fonte.

### Limitações conhecidas do Excel puro (informativo, não é decisão de mecanismo)
- **Proteção de planilha/pasta de trabalho por senha** (recurso nativo do Excel) é facilmente contornável: um arquivo `.xlsx` é um contêiner ZIP, e a senha de proteção de estrutura/planilha pode ser removida editando o XML interno sem ferramentas sofisticadas. Não deve ser tratada como controle de acesso forte — apenas como controle de uso acidental.
- **Excel não tem sistema nativo de login por usuário.** Ele não sabe "quem" abriu o arquivo, exceto pelo nome de usuário do Windows/Office registrado no sistema operacional, que não é uma autenticação confiável nem controlável pelo dono da planilha.
- **Ocultar planilhas ou fórmulas** não impede acesso: qualquer pessoa com o arquivo pode reexibir abas ocultas ou remover a proteção pelos métodos acima.
- **Separar em arquivos distintos por perfil** (um arquivo "Administrador" completo e um arquivo "Cliente" com dados filtrados/protegidos) é tecnicamente mais robusto do que proteger um único arquivo com múltiplos níveis de acesso, mas introduz o problema de **manter os dois arquivos sincronizados** — mecanismo de sincronização não definido.
- **Controle real de acesso** hoje só é efetivamente reforçável pelo **ambiente de armazenamento** (permissões de pasta/link no Google Drive, OneDrive ou SharePoint — ex.: "somente visualização" para o Cliente), não pelo arquivo Excel em si. Isso já é mencionado como princípio em `AGENTS.md`/histórico ("permissões do ambiente de armazenamento"), mas nenhuma fonte especifica qual ambiente será usado nem como a permissão será configurada.
- **VBA/macro com prompt de senha** poderia simular um login, mas introduz dependência de macros habilitadas (que muitos ambientes corporativos bloqueiam por política de segurança) e não foi cogitado em nenhuma fonte como solução oficial.

### Opções em aberto (nenhuma escolhida) — [H]
1. Arquivo único com proteção de planilha/estrutura por senha + ocultamento de abas técnicas (mais simples, mais fraco).
2. Arquivos separados por perfil, gerados a partir de uma base comum (mais robusto, exige processo de geração/sincronização a definir).
3. Controle via permissão do ambiente de armazenamento (Google Drive/OneDrive) combinado com proteção básica do Excel (depende de decisão sobre qual ambiente hospedará o arquivo).
4. Um mecanismo de login via VBA/macro (não recomendado como única camada, mas citável como complemento).

**Nenhuma destas opções foi adotada. Decisão do responsável pelo projeto antes da construção da camada de proteção.**

## 5. Aproveitamento do histórico — registro

- **Aproveitado [D]:** matriz de permissões por área (`PERFIS_DE_ACESSO_E_VISOES_V5.md`/`_V6.md`), promovida na Seção 3 acima, sem invenção de novas permissões.
- **Aproveitado [D]:** os dois perfis oficiais e o princípio "abas ocultas não são segurança suficiente".
- **Apenas referência, não aproveitado como requisito:** `SEC_001_PROTECAO.md`, `SEC_002_CAMPOS_EDITAVEIS.md`, `SEC_003_DADOS_INTERNOS.md`, `SEC_004_BACKUP_E_VERSIONAMENTO.md`, `SEC_005_RECUPERACAO.md` do histórico V1–V6 — confirmados na auditoria como templates sem conteúdo de mecanismo; não continham nenhuma decisão a herdar sobre autenticação, backup ou recuperação.
