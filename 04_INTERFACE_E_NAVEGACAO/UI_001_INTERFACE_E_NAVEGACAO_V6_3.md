# Interface e Navegação — V6.3 (Revisão 1 — Fechamento de Especificação V1)

**Data da revisão:** 2026-09-16
**Motivo da revisão:** `AUDITORIA_PRE_CONSTRUCAO_V1` identificou ambiguidade no uso da palavra "Cronograma" (aba do produto vs. cronograma do próprio projeto de desenvolvimento, pasta `16_CRONOGRAMA_E_EXECUCAO`). Esta revisão resolve a nomenclatura, sem alterar a lista de áreas em si.

## Áreas — [D]/[P]

Início/Obra; Painel Gerencial; Planejamento; **Cronograma da Obra**; Orçamento; Fornecedores; Financeiro; Execução; Alterações; Pendências; Atualizações.

- Lista de áreas em si: [D] — consistente com a versão anterior deste documento e com `AGENTS.md` §12/§13, à exceção do nome "Cronograma", corrigido abaixo.
- **Nomenclatura "Cronograma da Obra" (antes apenas "Cronograma"): [P]** — decisão de nomenclatura desta revisão, conforme instrução de fechamento de especificação. Deve ser homologada junto com o restante da nomenclatura de abas.

## Nota terminológica — resolução da ambiguidade "Cronograma" — [P]

Duas coisas diferentes usavam a mesma palavra na documentação:

1. **Cronograma da Obra** — tela/módulo funcional do produto, que exibe as datas previstas e reais das Etapas/Subetapas (entidade `PLANEJAMENTO` no `DAD_001`). É uma área de uso do Administrador/Operador e do Cliente (consulta).
2. **Cronograma de Execução do Projeto** — o prazo do próprio desenvolvimento do sistema (21 dias planejados dentro de um total de 30, ver `16_CRONOGRAMA_E_EXECUCAO/CRN_001`). Não é uma tela do produto; é um artefato de gestão do projeto de software.

A partir desta revisão:
- **"Cronograma da Obra"** é o termo oficial para a tela do produto.
- **"Cronograma de Execução do Projeto"** é o termo oficial para o prazo de desenvolvimento (pasta 16).
- A pasta `16_CRONOGRAMA_E_EXECUCAO` **não foi movida nem renomeada**, conforme instrução explícita — apenas o texto do `CRN_001` foi ajustado para usar o termo completo (ver aquele documento).

## Cliente — [D]

Visão gerencial limpa e restrita, sem acesso técnico. Ver matriz de permissões detalhada em `SEC_001_SEGURANCA_PROTECAO_E_PERFIS_V6_3.md`.

## Pendência de homologação — [H]

A definição de quais campos exatos aparecem em cada área/tela depende do `DAD_001` (campos por entidade) e do `DSG_001` (Seção B — proposta de componentes de UI), ambos ainda com itens [H]. Este documento define apenas a navegação (nomes de área), não o conteúdo de cada tela.
