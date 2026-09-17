# BASE DA OBRA — ETAPA 2
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-16
**Fase:** Primeiro arquivo Excel funcional ("Base da Obra"). Nenhum módulo completo (Financeiro, Compras, Execução, Alterações, Pendências, Atualizações, Documentos), dashboard, Looker Studio ou autenticação foi construído, conforme limite de escopo explícito.
**Git:** nenhum commit ou push foi realizado. `git status` verificado antes e depois (Seção 9 deste relatório).

---

## 1. Objetivo

Sair da fundação Python (Etapa 1) e fazer o sistema existir fisicamente como um arquivo Excel: um MODELO (template) de uma única obra, com as áreas Início/Obra, Etapas, Subetapas e Serviços/Orçamento, mais uma aba técnica de apoio ("Base técnica"), reutilizando o `GeradorId` e a `BaseDados` já testados na Etapa 1.

---

## 2. Arquivos criados

Nenhum arquivo da Etapa 1 foi alterado. Todos os arquivos abaixo são novos:

```
src/excel/
├── __init__.py
├── estilos.py                 (cores oficiais da marca, sem inventar identidade visual)
└── construtor_workbook.py     (geração das 5 abas do workbook)

scripts/
└── gerar_arquivo_obra_modelo.py   (gera o arquivo entregável)

testes/
└── test_excel_construtor.py       (16 testes novos)

dados/
└── GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx   (arquivo entregável desta etapa)

relatorios/
└── BASE_DA_OBRA_ETAPA_2_V1.md     (este arquivo)
```

Nenhum arquivo de documentação (`00` a `17`) foi criado ou alterado. Nenhum arquivo da Etapa 1 (`src/modelo`, `src/ids`, `src/hierarquia`, `src/base_dados`, `config/ids_config.py`) foi modificado — apenas reutilizado por importação.

---

## 3. Arquivo Excel gerado

**Nome:** `GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx` (nome sugerido na Seção 20, usado sem alteração).
**Local:** `dados/` (pasta oficial de dados do projeto, conforme AGENTS.md §7 — não uma pasta temporária).
**Conteúdo:** um MODELO/template **vazio de dados de negócio** — nenhuma obra, etapa, subetapa ou serviço fictícios foram inventados, coerente com o nome "OBRA_MODELO" e com a Seção 2 da homologação ("posteriormente o mesmo modelo poderá ser duplicado para cada obra"). Cabeçalhos, formatação, validações e fórmulas de ID/vínculo já estão ativos e prontos para uso.

Gerado por: `scripts/gerar_arquivo_obra_modelo.py` (executado com sucesso; ver Seção 7).

---

## 4. Abas criadas

5 abas, correspondendo exatamente às 5 áreas da Seção 4 da homologação — nenhuma aba extra foi criada, seguindo a filosofia "menos é mais" (Seção 11):

| Aba | Área (Seção 4) | Conteúdo |
|---|---|---|
| **Início** | 1. Início/Obra | Formulário vertical amigável (rótulo + valor) para os dados da Obra |
| **Etapas** | 2. Etapas | Tabela: 1 linha = 1 Etapa |
| **Subetapas** | 3. Subetapas | Tabela: 1 linha = 1 Subetapa (vínculo obrigatório com Etapa) |
| **Serviços** | 4. Serviços/Orçamento | Tabela: 1 linha = 1 Serviço (vínculo obrigatório com Subetapa) |
| **Base_Dados** *(oculta)* | 5. Base técnica | Metadados internos (ID técnico da Obra) e tabela de prefixos de ID — não é uma 6ª área de negócio |

`CONFIG` e `CALCULOS` (citados como "exemplo conceitual" na Seção 11) **não foram criados nesta etapa** — não há parâmetro de configuração nem fórmula de cálculo consolidado homologados para ocupá-los ainda (Motor de Cálculos é etapa futura); criar abas vazias contrariaria a própria Seção 11 ("não criar dezenas de abas", "menos é mais"). Registrado como decisão de escopo, não como pendência.

---

## 5. Estrutura criada, por aba

### 5.1 Início (Obra)
Campos literais da Seção 5, mapeados ao `DAD_001`: Nome da Obra, Cliente/Contratante, Endereço, Responsável Técnico, Data Inicial Planejada, Data Final Planejada, Orçamento Inicial (Previsto). Nenhum campo adicional foi inventado. O ID técnico da Obra **não aparece nesta aba** (fica só na aba técnica oculta) — atende literalmente "não mostrar IDs técnicos como informação principal" (Seção 5).

### 5.2 Etapas
Colunas: `ID (técnico)` *(oculta)*, `Nome`, `Ordem`, `Status`, `ID_Obra (técnico)` *(oculta)*. "Status" existe como campo (documentado no `DAD_001`), mas sem domínio fechado — texto livre, porque a lista de valores continua [H] (ver Seção 8). Campos de data (Planejamento) não foram incluídos aqui: pertencem a uma entidade/módulo diferente (`PLANEJAMENTO`/Cronograma), fora do objetivo desta etapa (Seção 4 não lista Planejamento entre as áreas a construir).

### 5.3 Subetapas
Colunas: `ID (técnico)` *(oculta)*, `Nome`, `Etapa` *(dropdown com nomes amigáveis)*, `Status`, `ID_Etapa (técnico)` *(oculta, calculada por fórmula a partir da Etapa escolhida)*.

### 5.4 Serviços
Colunas: `ID (técnico)` *(oculta)*, `Descrição`, `Subetapa` *(dropdown com nomes amigáveis)*, `Unidade de Medida`, `Quantidade Orçada`, `Valor Unitário`, `Valor Previsto`, `Status`, `ID_Subetapa (técnico)` *(oculta, calculada por fórmula)*. Todos os 4 campos pedidos na Seção 9 (quantidade planejada, unidade, valor unitário, valor previsto) estão presentes. "Fornecedor Previsto" (campo existente no `DAD_001`) **não foi incluído** — o módulo Fornecedores não está entre as 5 áreas desta etapa (Seção 4); decisão de escopo, não pendência.

### 5.5 Base_Dados (oculta)
ID técnico da Obra (`OBR-0001`, atribuído pelo `GeradorId`) e uma tabela de referência dos 13 prefixos homologados na Etapa 1. Aba oculta (`sheet_state = "hidden"`), **não protegida por senha** — o mecanismo de proteção do Excel continua [H] (`SEC_001` Seção 4); ocultar sem proteger não prejudica desenvolvimento/testes (Seção 4 da Etapa 2 permite isso explicitamente).

---

## 6. Entidades implementadas nesta etapa

Reaproveitadas integralmente da Etapa 1, sem alteração: `Obra`, `Etapa`, `Subetapa`, `ServicoOrcamento` (via `src.modelo.entidades`), `BaseDados` (via `src.base_dados.repositorio`) e `GeradorId` (via `src.ids.gerador_id`). Nenhuma entidade nova foi criada — esta etapa é a camada de **apresentação/geração Excel** sobre o modelo já existente.

---

## 7. Uso do GeradorId (Seção 10) e geração de ID no Excel

Duas situações, pela mesma configuração (`config/ids_config.py`), nunca divergentes:

1. **Linhas escritas pelo Python** (quando `construir_workbook()` recebe uma `BaseDados` já povoada — usado nos testes): o ID já foi atribuído pelo `GeradorId` da Etapa 1 e é gravado como **valor literal**.
2. **Linhas em branco do modelo** (as que o Operador vai preencher direto no Excel — é o caso do arquivo entregue, que está vazio de dados): uma **fórmula de planilha** replica o mesmo padrão `PREFIXO-0000`, usando `TEXT(ROW()-1,"0000")` e o prefixo de `config/ids_config.py`, sem VBA/macro (compatível com a Seção 17 — migração futura para Google Sheets).

O vínculo técnico (FK) de Subetapas→Etapa e de Serviços→Subetapa é sempre uma **fórmula oculta** (`INDEX`/`MATCH`) calculada a partir do nome escolhido no dropdown — nunca um ID digitado manualmente pelo Operador.

---

## 8. Validações implementadas

| Validação (Seção 13) | Onde | Mecanismo |
|---|---|---|
| Seleção de Etapa existente | Subetapas!Etapa | Dropdown (lista suspensa) restrito a `Etapas!Nome`, via Intervalo Nomeado `Lista_Etapas` |
| Seleção de Subetapa existente | Serviços!Subetapa | Dropdown restrito a `Subetapas!Nome`, via Intervalo Nomeado `Lista_Subetapas` |
| Referências consistentes (FK) | Subetapas, Serviços | Coluna técnica oculta calculada por `INDEX/MATCH` a partir do nome escolhido |
| Datas válidas | Início!Data Inicial/Final Planejada | `DataValidation(type="date", >= 1900-01-01)` |
| Formatos numéricos | Etapas!Ordem (inteiro > 0); Serviços!Quantidade Orçada, Valor Unitário, Valor Previsto (decimal ≥ 0) | `DataValidation(type="whole"/"decimal")` |
| Campos obrigatórios | Todas as tabelas | Não há um mecanismo nativo de "campo obrigatório" no Excel sem VBA; a estratégia usada foi indireta e sem macro: o ID técnico de uma linha só é calculado (`IF($B{linha}<>"", ...)`) quando o campo de Nome/Descrição está preenchido — uma linha incompleta nunca recebe um ID e não é tratada como um registro válido pelas fórmulas de vínculo |
| Não mostrar IDs técnicos como rótulo (Seção 14) | Subetapas!Etapa, Serviços!Subetapa | Dropdown lê da coluna "Nome" (`$B$`), nunca da coluna "ID" (`$A$`) — verificado por teste automatizado |

**Validação de formulário obrigatório mais rígida (bloqueio de digitação livre fora da lista) não foi implementada** para os dropdowns além do padrão `DataValidation(type="list")` do próprio Excel (que já impede, na interface do Excel, digitar um valor fora da lista, mas não impede colar/importar um valor inválido por fora da interface — limitação conhecida do formato, não uma omissão).

---

## 9. Testes criados e executados

16 testes novos em `testes/test_excel_construtor.py`, cobrindo exatamente os 10 itens da Seção 18:

| # | Item | Teste(s) |
|---|---|---|
| 1 | Arquivo Excel é criado | `test_arquivo_e_criado_e_pode_ser_reaberto_pelo_openpyxl` |
| 2 | Arquivo pode ser aberto pelo openpyxl | idem + `test_reabertura_com_data_only_nao_gera_erro` |
| 3 | Abas esperadas existem | `test_abas_esperadas_existem`, `test_aba_base_dados_fica_oculta` |
| 4 | Estrutura de cabeçalhos existe | `test_cabecalhos_das_tabelas_existem` (3 abas), `test_colunas_tecnicas_de_id_ficam_ocultas` |
| 5 | IDs são únicos | `test_ids_literais_sao_unicos_no_arquivo_gerado`, `test_formulas_de_id_das_linhas_modelo_sao_unicas_por_construcao` |
| 6 | Hierarquia Obra → Etapa → Subetapa → Serviço é válida | `test_hierarquia_completa_e_refletida_no_arquivo_com_nomes_amigaveis` |
| 7 | Serviço não pode existir sem Subetapa | `test_servico_nao_pode_ser_adicionado_a_base_sem_subetapa_valida` |
| 8 | Subetapa não pode existir sem Etapa | `test_subetapa_nao_pode_ser_adicionada_a_base_sem_etapa_valida` |
| 9 | Dropdowns não expõem IDs técnicos como rótulo | `test_dropdowns_apontam_para_coluna_de_nome_nao_para_coluna_de_id`, `test_valores_exibidos_nas_colunas_de_dropdown_nao_sao_ids_tecnicos` |
| 10 | Arquivo não apresenta corrupção estrutural | `test_arquivo_gerado_nao_apresenta_corrupcao_estrutural` |

**Comando executado:** `.venv/Scripts/python.exe -m pytest -v`
**Resultado: 61 passed, 0 failed** — 45 da Etapa 1 (inalterados, continuam passando) + 16 novos desta etapa.

### 9.1 Teste de abertura real (Seção 19)

Este ambiente **não tem Excel nem LibreOffice instalados** (verificado: nenhum executável `soffice`/`libreoffice` encontrado), portanto não foi possível abrir o arquivo em um motor de planilha real para calcular as fórmulas ao vivo. Na ausência dessa ferramenta, a integridade foi verificada com o que estava disponível:

- **Reabertura pelo openpyxl** (padrão e com `data_only=True`) sem exceções.
- **Integridade do ZIP**: `zipfile.testzip()` no `.xlsx` gerado — **sem membros corrompidos**.
- **Boa formação XML**: os 13 arquivos internos (`.xml`/`.rels`) foram parseados individualmente com `xml.etree.ElementTree` — **nenhum erro de parsing**.
- **Correção das fórmulas por construção**: como não há motor de cálculo disponível, a unicidade dos IDs das linhas-modelo foi verificada na própria string da fórmula (cada linha embute `ROW()` e a própria referência de linha, garantindo resultado distinto quando calculada).
- Presença de abas, cabeçalhos, validações e nomes definidos foi confirmada por inspeção direta via openpyxl (Seção 3 do log de verificação; reproduzível rodando os testes).

Esta é uma limitação do ambiente, não do arquivo — fica registrada como item a reexecutar em um ambiente com Excel/LibreOffice antes da entrega final ao cliente (ver Seção 12).

---

## 10. Limitações

1. **Sem motor de planilha no ambiente** (Seção 9.1) — a avaliação viva das fórmulas (ID, INDEX/MATCH, dropdowns) não pôde ser confirmada além do nível estrutural/sintático.
2. **Nomes amigáveis não são garantidamente únicos.** O vínculo técnico via `INDEX/MATCH` localiza a **primeira** ocorrência de um nome igual. Se dois Serviços em Subetapas diferentes tiverem, por coincidência, o mesmo nome de Subetapa (ex.: duas Etapas distintas com uma Subetapa "Reboco" cada), o `MATCH` pode resolver para a Subetapa errada. Isso não é uma regra de negócio inventada — é uma limitação técnica da abordagem "dropdown por nome" pedida na Seção 14, registrada aqui como pendência de UX/validação (ver Seção 11, item 1).
3. **"Campo obrigatório" é indireto** (Seção 8) — nada impede uma linha com Nome preenchido mas outros campos vazios; apenas garante que uma linha sem Nome nunca recebe ID nem entra na hierarquia.
4. **"Valor Previsto" e "Orçamento Inicial" ficam sem fórmula ativa** (ver Seção 11, item 2) — apenas estrutura e formatação de moeda prontas.
5. **30 linhas-modelo por tabela** (`LINHAS_MODELO`) — número arbitrário de conveniência (não uma regra de negócio); se o Operador precisar de mais linhas, basta arrastar a fórmula da última linha para baixo no próprio Excel.

---

## 11. Decisões ainda pendentes (registradas, não resolvidas)

Nenhum [P]/[H]/[C] foi transformado em decisão definitiva (Seção 22). Pendências identificadas nesta etapa:

1. **Unicidade de nomes amigáveis** (Limitação 2 acima) — não há, em nenhuma fonte, uma regra homologada exigindo que nomes de Etapa/Subetapa sejam únicos dentro do seu escopo. Recomenda-se homologar essa exigência antes de um uso real com muitas Subetapas de nomes repetidos.
2. **Fórmula de "Valor Previsto" (Quantidade × Valor Unitário) e de "Orçamento Inicial" (Σ Valor Previsto)** — `REG-003`/`DAD_001` marcam essas fórmulas como **[P] Proposta**, nunca [D] Homologada; a própria Seção 9 desta etapa pediu a estrutura pronta, não a fórmula ativa. A estrutura (colunas, formatação de moeda) está pronta; a fórmula em si não foi ativada.
3. **Domínio fechado de "Unidade de Medida"** (`DAD_001`: m², m³, kg, un., vb. — citados como exemplo, "não homologada") — implementado como texto livre, sem dropdown, para não promover um exemplo a domínio definitivo.
4. **Domínio fechado de "Status"** (Etapas/Subetapas/Serviços) — continua [H]; implementado como texto livre.
5. **Mecanismo de proteção do Excel** (`SEC_001` Seção 4) — a aba `Base_Dados` está oculta, mas não protegida por senha; nenhuma decisão de autenticação/proteção foi tomada nesta etapa.
6. **Ambiente sem Excel/LibreOffice** (Seção 9.1) — recomenda-se repetir o "teste de abertura" em uma máquina com Excel instalado antes de considerar o arquivo pronto para uso por um Operador real.

---

## 12. Próximo passo recomendado

1. Reabrir e revisar visualmente `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx` em uma máquina com Excel (ou LibreOffice) para confirmar que os dropdowns e fórmulas funcionam como esperado na prática — item que este ambiente não permitiu verificar ao vivo.
2. Homologar as pendências da Seção 11 antes de ativar qualquer fórmula financeira (Valor Previsto/Orçamento Inicial) ou de fechar os domínios de Status/Unidade de Medida.
3. Só então avançar para o **Motor de Cálculos** (peso automático, consolidação hierárquica, saldo orçamentário) e para os módulos ainda não iniciados (Financeiro, Compras, Execução, Alterações, Pendências, Atualizações, Documentos), sempre mediante nova autorização explícita, uma etapa por vez.

---

## 13. Checklist de conclusão da Etapa 2

- [x] arquivo Excel foi realmente gerado (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx`)
- [x] arquivo pode ser aberto (openpyxl, com e sem `data_only`; zip e XML íntegros — Excel/LibreOffice reais indisponíveis neste ambiente, ver Seção 9.1)
- [x] estrutura Obra foi criada (aba Início)
- [x] estrutura Etapas foi criada
- [x] estrutura Subetapas foi criada
- [x] estrutura Serviços foi criada
- [x] hierarquia foi respeitada (Serviço exige Subetapa; Subetapa exige Etapa — reforçado pela `BaseDados` da Etapa 1)
- [x] IDs técnicos foram implementados (literal via `GeradorId` + fórmula de planilha com o mesmo padrão)
- [x] nomes amigáveis foram preservados (dropdowns mostram Nome, nunca ID — testado)
- [x] validações estruturais foram implementadas (Seção 8)
- [x] testes foram criados (16 novos, Seção 9)
- [x] pytest foi executado
- [x] resultado foi registrado (61 passed, 0 failed)
- [x] relatório foi criado (este arquivo)
- [x] nenhuma regra não homologada foi inventada (Seção 11 lista as pendências)
- [x] git status foi verificado (antes e depois — Seção 14)
- [x] nenhum commit/push foi realizado

---

## 14. Git — estado final

`git status` após a implementação mostra apenas arquivos **novos e não rastreados** adicionados por esta etapa (`src/excel/`, `scripts/gerar_arquivo_obra_modelo.py`, `testes/test_excel_construtor.py`, `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx`, este relatório), além do que já estava não rastreado ao final da Etapa 1. Nenhum arquivo de documentação foi alterado por esta etapa. **Nenhum commit ou push foi realizado.** A decisão de commit/push permanece com o responsável pelo projeto.
