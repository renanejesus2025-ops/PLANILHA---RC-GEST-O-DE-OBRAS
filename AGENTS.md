# AGENTS.md
# SISTEMA DE GESTÃO DE OBRAS — RC
# Instruções oficiais para agentes de desenvolvimento

## 1. IDENTIDADE DO PROJETO

Este repositório contém o desenvolvimento do:

**Sistema de Gestão de Obras — RC**

O sistema é um produto profissional de gestão de obras desenvolvido inicialmente em Excel, com arquitetura preparada para integração futura com Google Sheets, Power BI, Looker Studio e outras ferramentas de BI.

O objetivo é transformar o Excel em uma interface operacional semelhante a um sistema de software, mantendo simplicidade para o usuário e inteligência nos cálculos, indicadores, alertas e análises.

Princípio central:

> SIMPLICIDADE NA ENTRADA E INTELIGÊNCIA NA SAÍDA.

---

## 2. FONTE DE VERDADE

A documentação oficial do projeto está organizada nas pastas:

- `00_DOCUMENTACAO_MESTRA`
- `01_ARQUITETURA_DO_SISTEMA`
- `02_MODELO_DE_DADOS_E_DICIONARIO`
- `03_DESIGN_E_IDENTIDADE_VISUAL`
- `04_INTERFACE_E_NAVEGACAO`
- `05_REGRAS_DE_NEGOCIO`
- `06_MODULOS_DO_SISTEMA`
- `07_INTEGRACOES_E_BI`
- `08_SEGURANCA_PROTECAO_E_PERFIS_DE_ACESSO`
- `09_TESTES_E_VALIDACAO`
- `10_HOMOLOGACAO_E_ACEITE`
- `11_MANUAIS`
- `12_MANUTENCAO_E_SUPORTE`
- `13_VERSOES_E_HISTORICO`
- `14_INTELIGENCIA_E_ANALISE`
- `15_AUDITORIA_E_CONTROLE`
- `16_CRONOGRAMA_E_EXECUCAO`
- `17_DICIONARIO_DOCUMENTAL`

A documentação V6.3 é a base documental homologada do projeto.

Antes de implementar uma funcionalidade, o agente deve consultar a documentação relacionada ao assunto.

Não inventar regras de negócio quando houver documentação disponível.

Quando houver conflito entre código e documentação, interromper a implementação e informar o conflito.

---

## 3. REGRA FUNDAMENTAL DE ATUAÇÃO

O agente deve trabalhar seguindo este fluxo:

1. Entender o requisito.
2. Consultar a documentação relacionada.
3. Identificar os arquivos afetados.
4. Explicar o que será alterado.
5. Implementar.
6. Executar testes.
7. Corrigir erros encontrados.
8. Executar regressão.
9. Executar auditoria quando aplicável.
10. Registrar a alteração.
11. Só então considerar a tarefa concluída.

Não considerar uma tarefa concluída apenas porque o código executou sem erro.

---

## 4. MODO DE TRABALHO

O agente deve atuar como:

- engenheiro de software;
- analista de dados;
- analista de sistemas;
- auditor técnico;
- operador de automação;
- mantenedor do projeto.

Porém, o agente não substitui a decisão do responsável pelo projeto.

Quando uma decisão de arquitetura, regra de negócio, segurança ou escopo não estiver definida, apresentar a questão antes de implementar.

---

## 5. NÃO ALTERAR SEM CONTROLE

O agente NÃO deve:

- apagar documentação oficial;
- sobrescrever arquivos históricos;
- remover funcionalidades existentes sem autorização;
- alterar regras de negócio silenciosamente;
- modificar o Design System sem autorização;
- modificar o modelo de dados sem verificar impactos;
- criar novas tecnologias sem justificativa;
- instalar dependências desnecessárias;
- alterar arquivos fora do escopo da tarefa;
- fazer commit ou push destrutivo sem autorização explícita.

---

## 6. GIT

O Git é o sistema oficial de versionamento.

Branch principal:

`main`

Remote principal:

`origin`

Antes de alterações relevantes:

- verificar `git status`;
- entender o estado atual do repositório;
- preservar histórico.

Após alterações:

- executar testes;
- verificar `git diff`;
- verificar `git status`;
- registrar alterações de maneira clara.

Nunca utilizar `git reset --hard`, `git clean`, `git push --force` ou comandos destrutivos sem autorização explícita.

Quando for necessário reescrever histórico, explicar primeiro o motivo e o impacto.

---

## 7. ESTRUTURA TÉCNICA

Código:

`src/`

Scripts:

`scripts/`

Testes:

`testes/`

Configurações:

`config/`

Dados:

`dados/`

Relatórios:

`relatorios/`

Documentação:

pastas `00` a `17`.

Não misturar código de produção com documentação.

Não colocar arquivos temporários ou credenciais no repositório.

---

## 8. PYTHON

O projeto utiliza Python como motor técnico.

O ambiente virtual oficial é:

`.venv`

O agente deve utilizar o Python do ambiente virtual quando executar scripts e testes.

Bibliotecas principais:

- OpenPyXL
- Pandas
- NumPy
- Pytest

Outras bibliotecas somente quando houver necessidade técnica documentada.

---

## 9. ARQUITETURA DO SISTEMA

A arquitetura deve preservar as seguintes camadas principais:

1. Interface
2. Base de Dados
3. Motor de Cálculos
4. Controle e Proteção
5. Dashboard
6. Inteligência e Insights
7. Auditoria

### Camada transversal: Perfis e Acesso

**Perfis e Acesso não constitui uma etapa sequencial da arquitetura.**

Trata-se de uma camada transversal que atua sobre as demais camadas do sistema, controlando o que cada perfil pode visualizar, editar, executar ou acessar.

A arquitetura de acesso deve seguir o princípio:

**Perfil → Identificação → Interface → Permissões → Proteção → Dados**

Os perfis oficiais da V1 são:

### Administrador/Operador

É um único perfil.

Pode operar e administrar as funções autorizadas do sistema.

### Cliente

Possui acesso predominantemente gerencial e de consulta.

Não deve editar a base operacional, fórmulas, configurações ou áreas técnicas protegidas.

---
## 10. EXCEL

O Excel é o principal produto operacional da primeira fase.

Requisitos:

- compatibilidade com Excel;
- preparação para Google Sheets;
- fórmulas em português do Brasil quando aplicáveis;
- interface profissional;
- navegação simples;
- proteção de áreas técnicas;
- células de entrada claramente identificadas;
- tabelas estruturadas;
- indicadores;
- alertas;
- validações;
- formatação condicional;
- experiência semelhante a um sistema de software.

Não criar uma planilha visualmente carregada.

Princípio visual:

> LESS IS MORE.

---

## 11. MODELO DE DADOS

O sistema deve utilizar uma base de dados central.

Regra geral:

> uma linha representa um registro.

IDs técnicos podem existir internamente, mas não devem dominar a experiência do usuário.

O usuário deve visualizar nomes reais e familiares da construção civil.

Exemplos:

- Alvenaria
- Elétrica
- Hidráulica
- Fundação
- Pintura
- Acabamento
- Cimento
- Cal
- Areia fina
- Reboco
- Chapisco
- Assentamento de blocos

---

## 12. MÓDULOS PRINCIPAIS

A V1 deve priorizar:

- Obras
- Etapas
- Serviços/Orçamento
- Planejamento
- Compras
- Financeiro
- Execução/Medições
- Alterações
- Pendências

Módulos auxiliares:

- Fornecedores
- Atualizações
- Documentos/Fotos

Não implementar na V1:

- estoque completo;
- folha de pagamento;
- contabilidade;
- fiscal;
- BIM;
- RFI/submittals;
- contratos avançados;
- planejamento avançado.

Qualquer expansão de escopo deve ser previamente identificada.

---

## 13. HIERARQUIA GERENCIAL

A leitura gerencial deve priorizar:

1. Financeiro
2. Tempo/Cronograma
3. Execução física
4. Etapas e subetapas
5. Compras e fornecedores
6. Pendências e alertas

Indicadores importantes incluem:

- previsto;
- executado;
- saldo;
- percentual consumido;
- fluxo de recursos;
- previsto × realizado;
- desvios;
- execução física;
- atrasos;
- alertas de orçamento;
- inconsistências.

---

## 14. INTELIGÊNCIA

O módulo de inteligência deve identificar, quando os dados permitirem:

- desvios financeiros;
- estouro de orçamento;
- atrasos;
- concentração de despesas;
- inconsistências;
- comportamento de fornecedores;
- tendências;
- diferenças entre planejado e realizado;
- situações que mereçam atenção gerencial.

A inteligência deve apoiar decisões.

Não deve inventar dados.

Toda conclusão deve ser rastreável aos dados utilizados.

---

## 15. AUDITORIA

O projeto possui um modo formal de auditoria.

O auditor deve verificar, quando aplicável:

- integridade dos dados;
- campos obrigatórios;
- duplicidades;
- referências quebradas;
- registros órfãos;
- regras de negócio;
- cálculos;
- fórmulas;
- estrutura;
- relacionamentos;
- testes;
- regressões;
- proteção;
- permissões;
- consistência financeira.

Regra:

> BUILD → VERIFY → AUDIT → HOMOLOGATE

O agente que constrói uma funcionalidade não deve considerar sua própria implementação automaticamente homologada.

---

## 16. TESTES

O projeto deve utilizar testes:

- unitários;
- integração;
- funcionais;
- regressão;
- dados inválidos;
- resistência;
- compatibilidade;
- visuais, quando aplicável;
- homologação.

Sempre que uma regra importante for criada ou corrigida, considerar a criação ou atualização de teste correspondente.

---

## 17. SEGURANÇA

Nunca armazenar no repositório:

- senhas;
- tokens;
- chaves privadas;
- credenciais;
- arquivos `.env` reais;
- informações secretas.

Não tratar abas ocultas do Excel como mecanismo suficiente de segurança.

O controle de acesso deve considerar:

Perfil → Identificação → Interface → Permissões → Proteção → Dados

---

## 18. GOOGLE SHEETS E BI

A arquitetura deve permanecer independente da ferramenta de BI.

A primeira prioridade é concluir o Excel operacional.

Integrações com:

- Google Sheets;
- Looker Studio;
- Power BI;

devem ser tratadas como camadas posteriores.

Não criar dependência obrigatória de Power BI para que o sistema funcione.

---

## 19. DESIGN SYSTEM

O Design System oficial deve ser baseado no kit de marca fornecido pelo cliente.

O agente deve consultar:

`03_DESIGN_E_IDENTIDADE_VISUAL/02_KIT_DE_MARCA/`

Antes de criar elementos visuais importantes.

Não escolher cores, fontes, logos ou estilos aleatoriamente quando existir definição no kit de marca.

---

## 20. DOCUMENTAÇÃO

Toda alteração arquitetural ou funcional relevante deve atualizar a documentação correspondente.

Documentos formais devem manter, quando aplicável:

- versão DOCX;
- versão Markdown.

A documentação histórica deve ser preservada.

Não substituir histórico por documentação nova.

---

## 21. CONTROLE DE ESCOPO

Antes de desenvolver uma funcionalidade, o agente deve identificar:

- requisito;
- módulo;
- regra de negócio;
- dados envolvidos;
- interface;
- permissões;
- testes;
- auditoria;
- documentação afetada.

Se algum desses pontos não estiver definido, sinalizar antes de implementar.

---

## 22. PRINCÍPIO DE DESENVOLVIMENTO

Priorizar:

- simplicidade;
- estabilidade;
- rastreabilidade;
- manutenção;
- compatibilidade;
- segurança;
- testes;
- clareza;
- experiência do usuário.

Evitar:

- complexidade desnecessária;
- abstrações prematuras;
- dependências desnecessárias;
- código duplicado;
- soluções frágeis;
- funcionalidades fora do escopo.

---

## 23. REGRA PARA DECISÕES

Quando houver mais de uma solução tecnicamente válida:

1. apresentar as opções;
2. explicar impactos;
3. indicar a opção tecnicamente mais adequada com justificativa;
4. aguardar decisão quando a escolha alterar arquitetura, segurança, escopo ou custo.

---

## 24. ESTADO ATUAL DO PROJETO

Base documental oficial:

**V6.3**

Git:

**main**

Ambiente Python:

**.venv**

O projeto está em fase de preparação técnica para desenvolvimento.

A próxima prioridade é estruturar o código e os mecanismos de desenvolvimento, testes e auditoria antes da construção definitiva do Excel.

---

## 25. REGRA FINAL

Nunca assumir que "funcionou" significa "está pronto".

Uma funcionalidade somente deve ser considerada concluída quando:

- foi implementada;
- foi testada;
- passou pela validação correspondente;
- não introduziu regressões;
- está documentada quando necessário;
- e foi considerada apta para homologação.