# Documentação Mestre — Sistema de Gestão de Obras — V6

**Status:** Fonte oficial da verdade documental.

## 1. Propósito
Documentar e governar o Sistema de Gestão de Obras, da arquitetura à homologação e manutenção.

## 2. Princípio
**Simplicidade na entrada e inteligência na saída.**

## 3. Perfis oficiais
- **Administrador/Operador:** uma única função para administrar e operar o sistema.
- **Cliente:** visão gerencial restrita e predominantemente consultiva.

## 4. Arquitetura
Interface → Base de Dados → Motor de Cálculos → Controle/Proteção → Dashboard → Inteligência → Auditoria.
Perfis de acesso são camada transversal.

## 5. V1 funcional
Obras; Etapas; Serviços/Orçamento; Planejamento; Compras; Financeiro; Execução/Medições; Alterações; Pendências.
Auxiliares: Fornecedores; Atualizações; Documentos/Fotos.

## 6. BI
A primeira entrega é o Excel. A estrutura de dados é BI-agnóstica. Power BI, Looker Studio ou outra plataforma serão definidos posteriormente pelo cliente.

## 7. Qualidade
Construir → Verificar → Auditar → Homologar → Entregar → Manter.

## 8. Regra documental
- Documento formal: DOCX + MD.
- Documento técnico: MD.
- Auxiliar: formato apropriado, fora da contagem de documentos oficiais.

## 9. Regra de organização
Cada documento deve possuir uma pasta temática única. A pasta 00 não funciona como depósito de documentos de outras áreas.

## 10. Controle
Toda nova funcionalidade deve declarar perfil de acesso, permissões, regras de negócio, testes e critérios de homologação.
