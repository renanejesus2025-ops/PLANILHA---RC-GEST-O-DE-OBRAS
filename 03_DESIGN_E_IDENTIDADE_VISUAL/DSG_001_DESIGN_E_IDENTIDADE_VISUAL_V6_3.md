# Design e Identidade Visual — V6.3 (Revisão 1 — Fechamento de Especificação V1)

**Data da revisão:** 2026-09-16
**Motivo da revisão:** `AUDITORIA_PRE_CONSTRUCAO_V1` identificou que este documento atribuía ao manual de marca elementos que ele não contém (componentes, espaçamento, cards, tabelas, estados) e não transcrevia os valores reais (cores HEX, nome da tipografia) já existentes no manual. Esta revisão separa claramente o que é **identidade oficial da marca** do que é **proposta de design do produto**.

**Fonte primária:** `03_DESIGN_E_IDENTIDADE_VISUAL/02_KIT_DE_MARCA/Rafael Xonchim.pdf` (17 páginas, lido integralmente). Nenhum arquivo do kit de marca foi alterado nesta revisão.

## Legenda de status

[D] DOCUMENTADO (vem literalmente do manual) · [P] PROPOSTA DE DESIGN DO PRODUTO (decisão de UI ainda não homologada, não é requisito do manual) · [H] HOMOLOGAR

---

## A. IDENTIDADE OFICIAL DA MARCA — [D]

Tudo nesta seção vem diretamente do manual em PDF. Nada foi inferido ou completado.

### A.1 Logotipo
Ícone monograma "R/C" + wordmark "GESTÃO DE OBRAS". Duas variações de cor documentadas no manual: aplicação clara (sobre fundo escuro `#5a5f5b`) e aplicação escura (sobre fundo claro/`#0f1c2c`).

### A.2 Marca d'água
Versão translúcida do logotipo, com as mesmas duas variações de cor.

### A.3 Submarca
Selo circular com o texto "GESTÃO DE OBRAS" disposto ao redor do ícone central, com as mesmas duas variações de cor.

### A.4 Ícone
Monograma isolado (sem o wordmark), com as mesmas duas variações de cor.

### A.5 Paleta de cores — 4 cores exatas
| HEX | Papel observado no manual |
|---|---|
| `#ffffff` | Branco — fundo/contraste claro |
| `#abb6ba` | Cinza-azulado claro — aplicação sobre fundo escuro |
| `#5a5f5b` | Cinza-esverdeado escuro — cor de fundo dominante da marca |
| `#0f1c2c` | Azul-marinho escuro — variação de cor de fundo |

**Não há, no manual, cores semânticas de alerta/sucesso/erro/aviso.** A paleta é inteiramente neutra. (Ver Seção C.)

### A.6 Tipografia
**Gravesend Sans** — única fonte nomeada no manual, exemplificada com "AA BB CC 12345". O manual não especifica pesos (regular/bold/light) nem tamanhos de uso.

### A.7 Destaques (pictogramas de marca)
4 ícones temáticos: monograma da marca, aperto de mãos (parceria), prancheta/projeto (planejamento), alvenaria com colher de pedreiro (execução). **Estes são pictogramas de marca/institucionais, não um conjunto de ícones de interface** (ver Seção C).

### A.8 Templates
2 modelos de aplicação em papelaria/mídia social, fundo `#5a5f5b`, logotipo aplicado em posição de rodapé ou cabeçalho. **Não há, no manual, nenhum template de aplicação em planilha/Excel ou em tela de sistema.**

### A.9 Moodboard
3 fotografias de referência de obra (capacete, alvenaria em execução, aperto de mãos em canteiro). É referência de atmosfera/tom visual, não um elemento a ser replicado literalmente na interface.

---

## B. PROPOSTA DE DESIGN DO PRODUTO — [P]

Nada nesta seção existe no manual de marca. São decisões de design de interface **propostas para homologação**, derivadas apenas do princípio geral "aparência de sistema profissional" (`AGENTS.md` §19) e do estilo visual da marca (paleta neutra, traços finos, tipografia geométrica) — não são requisitos do kit de marca.

- **Cards** — blocos de indicador (ex.: Orçamento Previsto, Saldo) com cor de fundo neutra da paleta e destaque numérico. [P]
- **Botões** — ação primária/secundária. Nenhuma cor de ação (ex.: botão de confirmação) está definida na paleta neutra da marca — precisaria de extensão de paleta (ver Seção C). [P]
- **Menus/navegação** — barra ou painel lateral com as áreas de `UI_001`. [P]
- **Tabelas estruturadas** — cabeçalho com a cor escura da marca (`#5a5f5b` ou `#0f1c2c`), linhas em branco/cinza claro alternado. [P]
- **Alertas visuais** — indicadores de desvio, atraso, saldo negativo (exigidos por `REG_001`). **Cor de alerta não existe na paleta da marca** — proposta de extensão a homologar (ver Seção C). [P]
- **Campos de entrada** — células de entrada do usuário claramente diferenciadas de células calculadas/protegidas (exigido por `AGENTS.md` §10). Convenção visual (cor de preenchimento, borda) ainda não definida. [P]

**Nenhum destes itens deve ser tratado como requisito do manual de marca.** São propostas de design de produto, sujeitas à homologação do responsável antes da construção.

---

## C. ITENS A HOMOLOGAR — [H]

1. **Transcrição formal dos tokens visuais** para uso técnico (já feita na Seção A desta revisão — recomenda-se manter este documento, não o PDF, como referência rápida de HEX/fonte para quem for construir o Excel).
2. **Fallback tipográfico para Excel.** "Gravesend Sans" não é uma fonte padrão do Windows/Office; se não estiver instalada na máquina do usuário, o Excel substitui silenciosamente por outra fonte. Nenhuma fonte de fallback foi definida.
3. **Cores semânticas de alerta** (sucesso/erro/aviso/atenção) — inexistentes na paleta de marca (4 cores neutras). Necessárias para atender `REG_001` (REG-013 a REG-015) e `AGENTS.md` §10 (formatação condicional, alertas). Precisam ser definidas como extensão da paleta, não como substituição dela.
4. **Conjunto de ícones de interface** (editar, bloquear, alerta, calendário, gráfico, anexo etc.) — distinto dos 4 pictogramas de marca (Seção A.7), que são temáticos/institucionais e insuficientes para navegação de sistema.
5. **Grid de espaçamento, especificação de cards/tabelas/estados (hover, foco, erro, desabilitado)** — não existem no manual nem em nenhum documento anterior; são o conteúdo da Seção B, ainda como proposta, não como padrão homologado.
6. **Aplicação da marca em ambiente de planilha** — o manual só cobre papelaria/mídia social; a forma de aplicar o logotipo dentro do próprio arquivo Excel (cabeçalho de aba "Início", marca d'água de fundo, rodapé) não foi definida.

---

## Aproveitamento do histórico — registro

- **Aproveitado [D]:** todo o conteúdo da Seção A vem do manual original (`Rafael Xonchim.pdf`), não do histórico documental.
- **Apenas referência, não aproveitado como requisito:** `DSG_001_DESIGN_SYSTEM.md`, `DSG_002_KIT_DE_MARCA.md`, `DSG_003_PALETA_E_TIPOGRAFIA.md` a `DSG_009_COMPATIBILIDADE_VISUAL.md` do histórico V1–V6 — confirmados na auditoria como templates sem conteúdo (nenhum chegou a transcrever HEX ou nome de fonte); não continham nenhuma decisão a herdar.
