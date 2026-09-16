# Documentação Mestre — Sistema de Gestão de Obras — V5

## Status
Fonte oficial da verdade documental para o desenvolvimento do sistema.

## Princípio
**Simplicidade na entrada e inteligência na saída.**

## Perfis oficiais
1. **Administrador/Operador** — perfil único, responsável por administrar e operar o sistema.
2. **Cliente** — perfil predominantemente consultivo, com acesso somente às informações autorizadas.

## Regra DOCX × Markdown
- **DOCX:** documentação formal, editável e destinada principalmente a pessoas.
- **Markdown:** documentação técnica, versionável e destinada a pessoas, Git, VS Code, Python e agentes.
- Cada documento formal deve existir em **DOCX + MD**.
- Arquivos puramente técnicos podem existir apenas em **MD**.
- Arquivos auxiliares não são contabilizados como documentos oficiais.

## Arquitetura
Interface → Base de Dados → Motor de Cálculos → Controle/Proteção → Dashboard → Inteligência → Auditoria.
Perfis de acesso são uma camada transversal.

## Ciclo de qualidade
**Construir → Verificar → Auditar → Homologar → Entregar → Manter.**

## BI
O Excel é a primeira etapa e deve permanecer BI-agnóstico. Power BI, Looker Studio ou outra plataforma são etapas posteriores, conforme escolha do cliente.

## V1
Núcleo: Obras, Etapas, Serviços/Orçamento, Planejamento, Compras, Financeiro, Execução/Medições, Alterações e Pendências.
Auxiliares: Fornecedores, Atualizações e Documentos/Fotos.
