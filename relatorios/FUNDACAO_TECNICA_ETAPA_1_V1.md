# FUNDAÇÃO TÉCNICA — ETAPA 1
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-16
**Fase:** Fundação técnica (modelo de dados, IDs, relacionamentos, validações estruturais, testes). Nenhum módulo operacional completo, dashboard, Excel, autenticação ou integração de BI foi construído nesta etapa, conforme limite de escopo explícito.
**Git:** nenhum commit ou push foi realizado. `git status` verificado antes e depois da implementação (Seção 8 deste relatório).

---

## 1. Leitura prévia realizada

Antes de qualquer alteração, foram lidos integralmente:

- `AGENTS.md` (573 linhas).
- `00_DOCUMENTACAO_MESTRA/DOC_000_...md`, `01_ARQUITETURA_DO_SISTEMA/ARQ_001_...md`.
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_...md` (Revisão 5, corrente).
- `03_DESIGN_E_IDENTIDADE_VISUAL/DSG_001_...md` (consultado; nenhum elemento visual foi construído nesta etapa).
- `04_INTERFACE_E_NAVEGACAO/UI_001_...md`.
- `05_REGRAS_DE_NEGOCIO/REG_001_...md` (Revisão 5, corrente).
- `06_MODULOS_DO_SISTEMA/MOD_001_...md`.
- `08_SEGURANCA_PROTECAO_E_PERFIS_DE_ACESSO/SEC_001_...md`.
- `09_TESTES_E_VALIDACAO/TST_001_...md`.
- `10_HOMOLOGACAO_E_ACEITE/HML_001_...md`.
- `14_INTELIGENCIA_E_ANALISE/INT_001_...md`.
- `15_AUDITORIA_E_CONTROLE/AUD_001_...md`, `RELATORIO_AUDITORIA_FINAL_V6_3.md`, `TERMO_HOMOLOGACAO_V6_3.md`.
- `16_CRONOGRAMA_E_EXECUCAO/CRN_001_...md`.
- `17_DICIONARIO_DOCUMENTAL/DOC_017_...md`.
- `relatorios/AUDITORIA_PRE_CONSTRUCAO_V1.md` e `relatorios/PLANO_FECHAMENTO_ESPECIFICACAO_V1.md` (histórico imediato desta sessão de trabalho — não tratados como fonte histórica descartável, mas como o estado mais recente de pendências conhecidas antes desta etapa).
- Estado de `src/`, `scripts/`, `testes/`, `config/`, `dados/`, `relatorios/`: todos vazios antes desta etapa (confirmado por `find`/`ls`).
- `requirements.txt` e pacotes efetivamente instalados em `.venv` (openpyxl 3.1.5, pandas 3.0.5, numpy 2.5.3, pytest 9.1.1 — idênticos, nenhuma instalação foi necessária).

Nenhum documento histórico (`13_VERSOES_E_HISTORICO`) foi tratado como homologado.

---

## 2. Arquivos criados

Nenhum arquivo de documentação (`00` a `17`) foi criado ou alterado nesta etapa. Todos os arquivos abaixo são novos:

```
pytest.ini

config/
├── __init__.py
└── ids_config.py

src/
├── __init__.py
├── excecoes.py
├── ids/
│   ├── __init__.py
│   └── gerador_id.py
├── modelo/
│   ├── __init__.py
│   ├── enums.py
│   └── entidades.py
├── hierarquia/
│   ├── __init__.py
│   └── validacoes.py
└── base_dados/
    ├── __init__.py
    └── repositorio.py

scripts/
└── validar_fundacao.py

testes/
├── test_gerador_id.py
├── test_rotulo_amigavel.py
├── test_hierarquia.py
├── test_entidades.py
└── test_base_dados.py

relatorios/
└── FUNDACAO_TECNICA_ETAPA_1_V1.md   (este arquivo)
```

## 3. Arquivos alterados

**Nenhum.** Nenhum arquivo pré-existente (documentação ou código) foi modificado nesta etapa. As modificações em `02_MODELO_DE_DADOS_E_DICIONARIO`, `03_DESIGN_E_IDENTIDADE_VISUAL`, `04_INTERFACE_E_NAVEGACAO`, `05_REGRAS_DE_NEGOCIO`, `08_SEGURANCA_PROTECAO_E_PERFIS_DE_ACESSO` e `16_CRONOGRAMA_E_EXECUCAO` que aparecem em `git status` são **anteriores** a esta etapa (homologações de progresso físico e fechamento de especificação registradas em rodadas de trabalho anteriores desta mesma sessão) e não foram tocadas aqui.

---

## 4. Estrutura implementada

### 4.1 Configuração (`config/`)
- `ids_config.py` — mapa `PREFIXOS_ID` (nome de entidade → prefixo de 3 letras) e `LARGURA_SEQUENCIAL = 4`, conforme o padrão homologado na Seção 7 desta etapa.

### 4.2 IDs técnicos (`src/ids/gerador_id.py`)
- `GeradorId`: gera IDs sequenciais e estáveis por entidade (`gerar("ETAPAS")` → `"ETA-0001"`, `"ETA-0002"`, ...). Uma instância corresponde a uma obra (1 arquivo Excel = 1 obra, Seção 5).
- `eh_formato_de_id(valor)`: reconhece se uma string tem forma de ID técnico.
- `validar_formato_id(valor, entidade=None)`: valida formato e, opcionalmente, o prefixo esperado.
- `obter_prefixo(entidade)`: consulta o prefixo homologado de uma entidade.

### 4.3 Modelo de dados (`src/modelo/`)
- `enums.py` — **apenas** os domínios fechados já homologados: `MetodoExecucao` (Quantitativo/Status — REG-007), `StatusExecucao` (Pendente=0%/Em andamento=50%/Concluído=100% — REG-007 Rev. 5) e `TipoLancamentoFinanceiro` (Aporte/Despesa — REG-006). Nenhum outro domínio fechado do DAD_001 foi transformado em Enum (ver Seção 6, Pendências).
- `entidades.py` — 13 `@dataclass` correspondentes às 13 entidades da Seção 9 desta etapa e do `DAD_001`: `Obra`, `Etapa`, `Subetapa`, `ServicoOrcamento`, `Planejamento`, `Fornecedor`, `Compra`, `Financeiro`, `ExecucaoMedicao`, `Alteracao`, `Pendencia`, `Atualizacao`, `Documento`. Cada campo traz comentário citando a fonte e o status ([D]/[P]/[H]) no `DAD_001`. Campos calculados pelo Motor de Cálculos (Orçamento Vigente, Peso Automático, % Execução consolidado, Saldo Orçamentário) **não** são atributos de entrada — ficam para uma camada futura.

### 4.4 Validações estruturais (`src/hierarquia/validacoes.py`)
- `validar_referencia_existente` — FK aponta para registro existente.
- `validar_prefixo_da_entidade` — prefixo do ID bate com a entidade esperada.
- `validar_nome_nao_e_id_tecnico` — impede que um ID técnico seja usado como rótulo amigável (AGENTS.md §11).
- `validar_cadeia_obra_etapa_subetapa_servico` — valida a cadeia completa da hierarquia oficial (REG-019).

### 4.5 Base de dados em memória (`src/base_dados/repositorio.py`)
- `BaseDados` — agregador com uma coleção por entidade (dict `id → objeto`), um `GeradorId` embutido, e um método `adicionar_<entidade>()` por entidade que valida unicidade de ID e toda FK relevante antes de inserir (levanta `ErroIdDuplicado` ou `ErroReferenciaInvalida`).

### 4.6 Exceções (`src/excecoes.py`)
- Hierarquia de exceções específicas: `ErroFundacaoTecnica` (base), `ErroPrefixoDesconhecido`, `ErroFormatoIdInvalido`, `ErroIdDuplicado`, `ErroReferenciaInvalida`, `ErroHierarquiaInvalida`.

### 4.7 Script de fumaça (`scripts/validar_fundacao.py`)
- Constrói a cadeia Obra → Etapa → Subetapa → Serviço de ponta a ponta usando a API acima, imprime o resultado, e demonstra a rejeição de uma violação de hierarquia. Executado manualmente com sucesso (Seção 7).

### 4.8 Configuração de testes (`pytest.ini`)
- `pythonpath = .` e `testpaths = testes`, para permitir `import src...`/`import config...` sem empacotar o projeto (fora do escopo desta etapa).

---

## 5. Testes criados

25 casos de teste diretos + 20 variações parametrizadas = **45 testes**, cobrindo explicitamente os 8 itens mínimos exigidos na Seção 14 desta etapa:

| # | Item exigido | Arquivo | Teste(s) representativo(s) |
|---|---|---|---|
| 1 | Geração de ID | `test_gerador_id.py` | `test_gera_id_com_prefixo_e_sequencial_homologados`, `test_gera_ids_sequenciais_e_estaveis_por_entidade` |
| 2 | Unicidade de ID | `test_gerador_id.py`, `test_base_dados.py` | `test_ids_sao_unicos_mesmo_entre_entidades_diferentes`, `test_ids_unicos_id_duplicado_e_rejeitado` |
| 3 | Formato de ID | `test_gerador_id.py` | `test_formato_de_id_e_reconhecido_corretamente` (7 variações), `test_validar_formato_id_rejeita_formato_invalido` |
| 4 | Relacionamento válido | `test_hierarquia.py` | `test_relacionamento_valido_etapa_pertence_a_obra` |
| 5 | Relacionamento inválido | `test_hierarquia.py` | `test_relacionamento_invalido_subetapa_com_etapa_de_outra_obra` |
| 6 | Hierarquia Obra → Etapa → Subetapa → Serviço | `test_hierarquia.py`, `test_base_dados.py` | `test_hierarquia_completa_obra_etapa_subetapa_valida`, `test_constroi_hierarquia_obra_etapa_subetapa_servico_end_to_end` |
| 7 | Referência inexistente | `test_hierarquia.py`, `test_base_dados.py` | `test_referencia_para_obra_inexistente_e_rejeitada`, `test_etapa_com_obra_inexistente_e_rejeitada` |
| 8 | ID técnico não usado como rótulo amigável | `test_rotulo_amigavel.py` | `test_ids_tecnicos_nao_podem_ser_usados_como_nome_amigavel`, `test_entidades_construidas_com_ids_gerados_mantem_nomes_amigaveis_distintos` |

Testes adicionais em `test_entidades.py` e `test_base_dados.py` cobrem os domínios homologados nas rodadas anteriores desta sessão (Modelo Híbrido de progresso físico: `MetodoExecucao`, `StatusExecucao` com a tabela fixa 0%/50%/100%, preservação do peso automático original, e a separação Aporte × Peso Físico — REG-021/REG-022, garantindo que um Aporte sem Serviço vinculado é aceito mas não afeta a base física).

## 6. Testes executados e resultado

Comando executado com o Python do ambiente virtual do projeto:

```
.venv/Scripts/python.exe -m pytest -v
```

**Resultado: 45 passed, 0 failed, 0 erros** (0,06–0,28s de execução).

Durante o desenvolvimento, 1 teste falhou por um defeito no próprio teste (dois `GeradorId()` independentes geravam os mesmos IDs "OBR-0001"/"ETA-0001" para obras diferentes, mascarando a violação que o teste tentava provocar). O teste foi corrigido para compartilhar um único `GeradorId` entre as duas cadeias construídas, e voltou a passar. Nenhum defeito foi encontrado no código de produção (`src/`).

O script de fumaça `scripts/validar_fundacao.py` também foi executado manualmente e produziu o resultado esperado, incluindo a rejeição correta de um Serviço apontando para uma Subetapa inexistente.

---

## 7. Decisões utilizadas (já homologadas — nenhuma nova foi tomada)

- **Padrão de ID técnico** (Seção 7 desta homologação): `<PREFIXO-3-LETRAS>-<sequencial 4 dígitos>`. Os 11 prefixos citados literalmente (OBR, ETA, SUB, SRV, FIN, COM, EXE, ALT, PEN, ATU, DOC) foram usados exatamente como informados.
- **1 arquivo Excel = 1 obra** (Seção 5): refletido no design do `GeradorId`/`BaseDados` — uma instância por obra, sem seletor multiobra.
- **Hierarquia oficial OBRA → ETAPA → SUBETAPA → SERVIÇO** (REG-019, DAD_001): implementada como regra estrutural obrigatória em `BaseDados` e `validacoes.py` — não é possível inserir uma Subetapa sem Etapa válida, nem um Serviço sem Subetapa válida.
- **"Código para a máquina. Nome para o usuário."** (AGENTS.md §11): todo `id` de entidade é tecnicamente distinto do campo de nome amigável (`nome`, `descricao`, `nome_razao_social`), e `validar_nome_nao_e_id_tecnico` está disponível para a futura camada de interface se proteger de exibir um ID por engano.
- **Modelo Híbrido de progresso físico** (REG-007/REG-008, homologado em rodadas anteriores desta sessão): `MetodoExecucao` (Quantitativo/Status) e `StatusExecucao` (tabela fixa Pendente=0%/Em andamento=50%/Concluído=100%) implementados como Enum; `peso_ajustado` e `peso_automatico_original` presentes em `ServicoOrcamento` para suportar a exigência de preservação (REG-008, Revisão 5), sem implementar o cálculo em si (Motor de Cálculos, fora de escopo).
- **Separação Aporte × Peso Físico** (REG-021): `Financeiro.id_servico_vinculado` é opcional — um Aporte existe em FINANCEIRO independentemente de estar vinculado a um Serviço; o vínculo é o que decidiria, numa camada futura, se ele entra na base de peso físico.
- **Ambiente Python**: usado o `.venv` já existente e as bibliotecas já previstas em `requirements.txt` (nenhuma instalação nova; o código de produção desta etapa não usa openpyxl/pandas/numpy — só biblioteca padrão — porque ainda não há geração de Excel nem análise de dados nesta etapa).

## 8. Pendências encontradas (registradas, não resolvidas)

Nenhuma regra de negócio foi inventada. Os pontos abaixo foram identificados durante a implementação e **não bloquearam** a fundação técnica (todos contornados com uma postura conservadora — texto livre opcional, sem impor domínio):

1. **Prefixos de ID de PLANEJAMENTO e FORNECEDORES não constavam na lista literal da Seção 7.** Foram derivados como `PLN` e `FOR`, aplicando a instrução explícita "outras entidades devem seguir o mesmo princípio" (3 letras, sem colisão). Recomenda-se confirmar formalmente esses dois prefixos e, se aprovados, promover a decisão ao `DAD_001` (hoje o "Regra sobre IDs" do `DAD_001` continua [H] porque essa homologação não chegou a essa etapa do trabalho).
2. **Domínios fechados ainda [H]** (Status da Obra/Etapa/Subetapa/Serviço, Unidade de Medida, Categoria de Fornecedor, Forma de Pagamento, Status de Aprovação de Compra/Alteração, Tipo de Alteração, Status/Prioridade de Pendência, Status do Prazo): representados como `Optional[str]` (texto livre) em vez de `Enum`, para não inventar valores de domínio. Nenhum destes é obrigatório em runtime nesta etapa, mesmo quando o `DAD_001` os marca como "Obrigatório: Sim" — impor obrigatoriedade sem um domínio homologado forçaria a invenção de um valor. Ver decisão de postura registrada no topo de `src/modelo/entidades.py`.
3. **Caso-limite do contador de ID acima de 9999** não foi homologado (o `GeradorId` continua funcionando, apenas deixa de gerar exatamente 4 dígitos).
4. **Campos técnicos definitivos de rastreabilidade do ajuste manual de peso** (nomes/formatos de "Justificativa do Ajuste", "Responsável pelo Ajuste", "Data do Ajuste") continuam [H] (REG-008) — não foram criados como campos na entidade `ServicoOrcamento`; apenas `peso_ajustado` e `peso_automatico_original`, que são os dois valores cuja preservação já está homologada.
5. **Motor de Cálculos, Interface, Dashboard, Inteligência/Insights, Auditoria e Controle/Proteção** (demais camadas de AGENTS.md §9) não foram construídos — são, por definição, o objeto de etapas futuras.
6. **Mecanismo de autenticação/proteção do Excel** continua [H] (`SEC_001` Seção 4) — não impactou esta etapa porque nenhuma proteção foi implementada aqui.

Nenhuma dessas pendências impediu a fundação técnica: cada uma foi contornada com campos opcionais/texto livre, nunca com um valor de domínio inventado.

## 9. Riscos

1. **Retrabalho de prefixo de ID:** se PLANEJAMENTO/FORNECEDORES vierem a ser homologados com prefixos diferentes de `PLN`/`FOR`, será necessário atualizar `config/ids_config.py` — impacto baixo (um único arquivo de configuração, sem lógica espalhada).
2. **Campos [H] como texto livre:** enquanto os domínios fechados não forem homologados, nada impede que dados inconsistentes (ex.: "Status" com valores diferentes por registro) sejam inseridos na fundação atual — aceitável nesta etapa (não há tela de entrada ainda), mas deve ser endereçado antes da Interface operar sobre esses campos.
3. **Ausência de persistência:** `BaseDados` é inteiramente em memória (sem gravação em `dados/` ou Excel) — esperado para esta etapa, mas é a próxima dependência real antes de gerar qualquer arquivo `.xlsx`.
4. **Sem Motor de Cálculos:** os campos que dependem de cálculo consolidado (Peso Automático, % Execução Física, Orçamento Vigente, Saldo Orçamentário) não têm nenhuma implementação ainda — só os dados de entrada estão modelados.

## 10. Próximo passo recomendado

Seguindo a ordem já registrada em `CRN_001`/`AUDITORIA_PRE_CONSTRUCAO_V1` ("Fundação documental → ambiente → dados → Excel → integração → painéis → inteligência/auditoria → testes → homologação → entrega"), esta etapa completa "dados" no nível estrutural. O próximo passo recomendado (Etapa 2, mediante nova autorização) é:

1. Confirmar os prefixos `PLN`/`FOR` (pendência 1 acima) e formalizar no `DAD_001` a homologação do formato de ID (hoje ainda [H] no documento, embora já aplicado no código por instrução direta desta etapa).
2. Construir o **Motor de Cálculos** sobre esta fundação (peso automático, consolidação hierárquica, saldo orçamentário), respeitando as fórmulas já homologadas em REG-003/REG-005/REG-008/REG-017/REG-020.
3. Só então iniciar a camada de persistência/Excel (`openpyxl`) e a interface operacional.

---

## 11. Checklist de conclusão da Etapa 1

- [x] AGENTS.md foi lido
- [x] documentação atual foi analisada
- [x] arquitetura foi respeitada (apenas camada de Base de Dados construída)
- [x] modelo base foi estruturado (13 entidades, `src/modelo/entidades.py`)
- [x] IDs internos foram implementados (`src/ids/gerador_id.py`, `config/ids_config.py`)
- [x] IDs não fazem parte da camada amigável (`validar_nome_nao_e_id_tecnico`, testado)
- [x] relacionamentos básicos foram estruturados (`BaseDados`, FKs por entidade)
- [x] validações estruturais existem (`src/hierarquia/validacoes.py`)
- [x] testes foram criados (45 testes em 5 arquivos)
- [x] pytest foi executado
- [x] resultado dos testes foi registrado (45 passed, 0 failed — Seção 6)
- [x] nenhum módulo futuro foi implementado prematuramente
- [x] nenhuma regra de negócio não homologada foi inventada (Seção 8 lista as pendências, todas contornadas sem inventar valor)
- [x] git status foi verificado (antes: Seção "Git" acima; depois: Seção 8 abaixo)
- [x] relatório da etapa foi criado (este arquivo)

---

## 12. Git — estado final

`git status` após a implementação mostra apenas arquivos **novos e não rastreados**:

```
config/
pytest.ini
scripts/
src/
testes/
```

(além de `relatorios/` já não rastreado desde a etapa anterior, agora contendo também este relatório). Nenhum arquivo de documentação foi alterado por esta etapa. **Nenhum commit ou push foi realizado.** A decisão de commit/push fica com o responsável pelo projeto.
