# ORÇAMENTO — ETAPA 3
## Sistema de Gestão de Obras — RC

**Data:** 2026-09-16
**Fase:** Módulo/base de Orçamento sobre a hierarquia OBRA → ETAPA → SUBETAPA → SERVIÇO. Nenhum Financeiro completo, pagamentos, Compras, Execução, Alterações completas ou Dashboard foram construídos, conforme limite de escopo explícito.
**Git:** nenhum commit ou push foi realizado. `git status` verificado antes e depois (Seção 17 deste relatório).

---

## 1. Objetivo

Permitir que a obra tenha um orçamento previsto estruturado por Serviço → Subetapa → Etapa → Obra, com o Operador podendo cadastrar/alterar valores sem conhecer IDs técnicos, mantendo "Sistema informa, Operador decide": o sistema calcula Valor Calculado e Valor Previsto automaticamente, mas o Operador pode ajustar manualmente o Valor Previsto quando necessário — sem que isso jamais apague o valor calculado.

---

## 2. Arquivos criados

```
src/validacoes/
├── __init__.py
└── numeros.py                  (validar_numero_nao_negativo)

src/orcamento/
├── __init__.py
├── calculos.py                 (total_previsto_subetapa/_etapa/_obra)
└── servicos.py                 (registrar_servico)

scripts/
└── gerar_arquivo_obra_modelo_v2.py   (gera o arquivo entregável desta etapa)

testes/
├── test_orcamento.py           (35 testes — domínio/entidade)
└── test_excel_orcamento.py     (15 testes — fórmulas/Excel)

dados/
└── GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx   (arquivo entregável desta etapa)

relatorios/
└── ORCAMENTO_ETAPA_3_V1.md     (este arquivo)
```

## 3. Arquivos alterados

**Código (Etapas 1/2, estendido — nenhum comportamento anterior removido):**
- `src/excecoes.py` — nova exceção `ErroValorNumericoInvalido`.
- `src/modelo/enums.py` — novo `StatusServico` (domínio fechado, Seção 18).
- `src/modelo/entidades.py` — `ServicoOrcamento`: campo `status` passa de `Optional[str]` para `Optional[StatusServico]`; renomeada a propriedade `valor_total_orcado` → `valor_calculado`; adicionados `valor_previsto_manual`, `ajuste_manual`, `valor_previsto`, `variacao`, `integra_orcamento_corrente`; `__post_init__` valida Quantidade/Valor Unitário.
- `src/excel/estilos.py` — novo `PREENCHIMENTO_CALCULADO`/`FONTE_CALCULADA` (diferenciação visual entrada × calculado).
- `src/excel/construtor_workbook.py` — reescrito para incluir a base orçamentária completa na aba Serviços e os totais em Subetapas/Etapas/Início (ver Seção 5).
- `scripts/validar_fundacao.py` — ajustado para usar `valor_calculado`/`valor_previsto` (nomes renomeados).
- `scripts/gerar_arquivo_obra_modelo.py` — **depreciado**: agora se recusa a rodar, para não sobrescrever silenciosamente a V1 com a estrutura nova (ver Seção 4).
- `testes/test_entidades.py`, `testes/test_excel_construtor.py` — ajustados para os nomes/posições de coluna novos; nenhum teste da Etapa 1/2 foi removido, apenas atualizado onde a mudança de nome/coluna exigia.

**Documentação formal (Seção 35 desta homologação — atualização feita por ser segura e claramente suportada pela decisão explícita da Seção 36):**
- `05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md` — Revisão 6: REG-003 reescrita; REG-026 (Valor Previsto), REG-027 (Status do Serviço) e REG-028 (Variação) adicionadas.
- `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md` — Revisão 6: entidade SERVIÇOS/ORÇAMENTO atualizada (campo renomeado, 4 campos novos, domínio de Status fechado); lista de domínios pendentes atualizada.
- **Pares DOCX não foram atualizados** — mesma pendência de forma já registrada em rodadas anteriores desta sessão (gerar `.docx` está fora do escopo de "documentação/especificação" sem biblioteca de geração aprovada para isso); registrada aqui novamente conforme pedido pela Seção 35.

---

## 4. Estratégia de versionamento do Excel (Seção 22)

Optou-se por **gerar uma nova versão** (`dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx`) em vez de sobrescrever a V1, para preservar rastreabilidade:

- `GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx` (Etapa 2) **permanece intocado no disco** — mesmo tamanho/data de antes desta etapa (verificado).
- `scripts/gerar_arquivo_obra_modelo.py` (o script que gerou a V1) foi **desativado** (`raise SystemExit(...)` com mensagem explicando o motivo): como ele chama o mesmo `construir_workbook()` que evoluiu nesta etapa, executá-lo de novo produziria conteúdo no formato NOVO sob o nome ANTIGO — exatamente a "sobrescrita silenciosa" que a Seção 22 pede para evitar. Ele foi mantido no repositório (não apagado) como registro de como a V1 foi gerada.
- `scripts/gerar_arquivo_obra_modelo_v2.py` é o gerador corrente a partir de agora.

---

## 5. Abas envolvidas e estrutura implementada

Nenhuma aba nova foi criada (Seção 23: "menos abas, melhor organização"). As mesmas 5 abas da Etapa 2 foram estendidas:

### 5.1 Serviços (base orçamentária completa — Seção 6)
Colunas novas/alteradas em relação à V1: `Valor Calculado` (fórmula, calculada), `Valor Previsto (Ajuste Manual)` (entrada opcional), `Ajuste Manual` (fórmula SIM/NÃO, calculada), `Valor Previsto` (fórmula, calculada), `Variação` (fórmula, calculada), `Status` (agora dropdown de domínio fechado). Todas as colunas calculadas usam preenchimento visual distinto das colunas de entrada (AGENTS.md §10).

### 5.2 Subetapas
Nova coluna `Total Previsto (Serviços)` — soma o Valor Previsto dos Serviços vinculados a esta Subetapa (por ID técnico, nunca por nome — ver Seção 12), excluindo Cancelado/Retirado do Escopo/Substituído.

### 5.3 Etapas
Nova coluna `Total Previsto (Subetapas)` — soma os totais das Subetapas desta Etapa (também por ID técnico).

### 5.4 Início
O campo "Orçamento Inicial (Previsto)", que na Etapa 2 ficava em branco (estrutura pronta, sem fórmula — REG-003 ainda [P]), agora é uma **fórmula ativa**: soma os totais de todas as Etapas. Resolve a pendência registrada no relatório da Etapa 2.

### 5.5 Base_Dados (oculta)
Passou a documentar também os 5 valores de Status do Serviço homologados e se cada um integra ou não o orçamento corrente — apoio de leitura, não uma fórmula.

---

## 6. Cálculo do Valor Calculado

```
Valor Calculado = Quantidade Orçada × Valor Unitário
```
Implementado como `@property` em `ServicoOrcamento.valor_calculado` (Python) e como fórmula Excel `=IF(OR(qtd="",vu=""),"",qtd*vu)`. **Nunca é sobrescrito** por um ajuste manual — permanece sempre acessível, mesmo quando há Valor Previsto manual. Nenhum arredondamento é aplicado ao valor usado em cálculo (Seção 30); a formatação `#,##0.00` é só de exibição.

## 7. Cálculo do Valor Previsto

```
Valor Previsto = Valor Calculado                         (sem Ajuste Manual)
Valor Previsto = valor informado pelo Operador            (com Ajuste Manual)
```
Implementado como `@property` `ServicoOrcamento.valor_previsto` (Python) e como fórmula Excel `=IF(ValorPrevistoManual="",ValorCalculado,ValorPrevistoManual)`.

## 8. Mecanismo de Ajuste Manual

- Campo único de entrada: `valor_previsto_manual` (Python) / coluna "Valor Previsto (Ajuste Manual)" (Excel) — `None`/vazio = sem ajuste.
- Indicador `ajuste_manual` (Python, bool) / coluna "Ajuste Manual" (Excel, fórmula `SIM`/`NÃO`) — sempre consistente com o campo acima por construção (não é um segundo campo independente que possa divergir).
- **Sem justificativa obrigatória, sem aprovação, sem workflow** — exatamente como pedido na Seção 12.
- `Valor Calculado` nunca é apagado nem sobrescrito.

---

## 9. Totais

Implementados em Python (`src/orcamento/calculos.py`, testados diretamente) **e** em Excel (fórmulas `SUMIFS`, testadas quanto ao texto/estrutura da fórmula):

```
total_previsto_subetapa(base, id_subetapa) -> Σ Valor Previsto dos Serviços elegíveis da Subetapa
total_previsto_etapa(base, id_etapa)       -> Σ Valor Previsto dos Serviços elegíveis da Etapa (via Subetapas)
total_previsto_obra(base, id_obra)         -> Σ Valor Previsto dos Serviços elegíveis da Obra
```

**"Elegível" = `servico.integra_orcamento_corrente`** (Seções 18/19): exclui Cancelado, Retirado do Escopo e Substituído; inclui Ativo, Concluído e Status ainda não informado.

**Nenhum destes totais soma:** Aportes, Alterações Aprovadas, Custo Realizado, Pagamentos ou Saldo de Caixa (Seção 14) — verificado por teste automatizado (`test_totais_nao_somam_aportes_alteracoes_ou_custo_realizado`) que varre toda fórmula do workbook em busca desses termos.

**Chave técnica, nunca nome** (ver Seção 12 sobre o risco de nomes duplicados): as fórmulas `SUMIFS` casam pelo ID técnico oculto (`ID_Subetapa`/`ID_Etapa`), não pelo nome amigável — isso já reduz o risco de ambiguidade nos TOTAIS (o risco na SELEÇÃO do dropdown persiste, ver Seção 12 abaixo).

---

## 10. Validações implementadas

| Validação | Onde | Mecanismo |
|---|---|---|
| Quantidade numérica, ≥ 0 | `ServicoOrcamento.__post_init__` (Python) | `validar_numero_nao_negativo` — levanta `ErroValorNumericoInvalido` |
| Valor Unitário numérico, ≥ 0 | idem | idem |
| Quantidade/Valor Unitário ≥ 0 no Excel | Serviços!E, Serviços!F | `DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0")` |
| Status restrito ao domínio fechado | Serviços!Status (Excel) | `DataValidation(type="list")` com os 5 rótulos exatos de `StatusServico` |
| Subetapa/Etapa só entre as já cadastradas | Serviços!Subetapa, Subetapas!Etapa | Dropdown por Intervalo Nomeado (herdado da Etapa 2) |
| "Campo obrigatório" (indireto) | Todas as tabelas | Uma linha sem Nome/Descrição não recebe ID nem entra em nenhuma fórmula de vínculo — herdado da Etapa 2, sem mudança |
| Nenhuma cor/alerta na Variação | Serviços!Variação | Testado que não há `ConditionalFormatting` na aba (Seção 31) |

---

## 11. Testes criados

**50 testes novos** (35 em `testes/test_orcamento.py` + 15 em `testes/test_excel_orcamento.py`), cobrindo item a item a Seção 27 e os Cenários A–H da Seção 29:

| # (Seção 27) | Item | Teste(s) |
|---|---|---|
| 1 | Quantidade × Valor Unitário calcula corretamente | `test_valor_calculado_quantidade_vezes_valor_unitario` (10×100, 100×50, 25×12,50) |
| 2/5 | Valor Calculado é preservado (antes/depois do ajuste) | `test_valor_calculado_e_preservado_antes_do_ajuste`, `test_valor_calculado_continua_preservado_apos_ajuste_manual` |
| 3 | Sem ajuste, Previsto = Calculado | `test_sem_ajuste_manual_valor_previsto_igual_ao_calculado` |
| 4 | Com ajuste, Previsto usa o valor informado | `test_com_ajuste_manual_valor_previsto_usa_valor_informado` |
| 6 | Ajuste Manual identificável | `test_ajuste_manual_e_identificavel_como_sim_ou_nao` |
| 7 | Quantidade negativa rejeitada | `test_quantidade_negativa_e_rejeitada`, `test_cenario_d_...` |
| 8 | Valor Unitário negativo rejeitado | `test_valor_unitario_negativo_e_rejeitado`, `test_cenario_e_...` |
| 9 | Valores não numéricos rejeitados | `test_valores_nao_numericos_sao_rejeitados_na_quantidade/no_valor_unitario` |
| 10/11 | Vínculo Serviço→Subetapa→Etapa preservado | `test_servico_mantem_vinculo_com_subetapa`, `test_subetapa_mantem_vinculo_com_etapa` |
| 12/13/14 | Totais por Subetapa/Etapa/Obra | `test_total_por_subetapa_e_consistente_cenario_f`, `..._etapa_..._cenario_g`, `..._obra_..._cenario_h` |
| 15 | Serviços fora da base ativa não entram no total | `test_integra_orcamento_corrente_por_status`, `test_servico_cancelado_nao_entra_no_total_da_subetapa` |
| 16/17 | IDs internos / nomes amigáveis na interface | `test_id_tecnico_e_distinto_do_rotulo_amigavel_do_servico`, `test_status_amigavel_no_dropdown_nao_e_um_id_tecnico` |
| 18/19/20 | Workbook criado/reaberto/XML íntegro | já cobertos por `testes/test_excel_construtor.py` (Etapa 2, ainda passando); reforçado por `test_excel_orcamento.py` |

Cenários A–E têm teste dedicado (`test_cenario_a_...` a `test_cenario_e_...`); F/G/H são os testes de totais acima.

## 12. Quantidade total de testes e resultado

```
.venv/Scripts/python.exe -m pytest -v
```
**120 testes coletados, 120 passed, 0 failed** (Etapa 1: 45 · Etapa 2: 25 · Etapa 3: 50). Todos os testes das Etapas 1 e 2 continuam passando — os únicos ajustados foram os que dependiam de nomes/posições de coluna que mudaram (`valor_total_orcado`→`valor_calculado`; posição do vínculo técnico oculto em Serviços), nunca de comportamento removido.

O arquivo `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx` foi verificado com a mesma bateria estrutural da Etapa 2 (Seção 28): ZIP íntegro (`zipfile.testzip() is None`), os 13 arquivos internos `.xml`/`.rels` bem formados (`xml.etree.ElementTree`, 0 erros), reabertura pelo openpyxl com `data_only=False` e `data_only=True` sem exceção. **Este ambiente continua sem Excel/LibreOffice instalado** (verificado novamente) — nenhuma "abertura real" foi realizada nem afirmada, conforme a Seção 28 exige explicitamente.

---

## 13. Cenários simulados (Seção 29)

| Cenário | Entrada | Resultado obtido |
|---|---|---|
| A | Qtd 100, VU 50, sem ajuste | Calculado = 5.000; Previsto = 5.000 |
| B | Qtd 100, VU 50, ajuste manual 5.300 | Calculado = 5.000 (preservado); Previsto = 5.300; Variação = 300 |
| C | Qtd 0, VU 50 | Calculado = 0; Previsto = 0 — nenhuma regra adicional inventada |
| D | Qtd -10 | Rejeitado (`ErroValorNumericoInvalido`) |
| E | VU -50 | Rejeitado (`ErroValorNumericoInvalido`) |
| F | 2 serviços em 1 Subetapa (1.200 + 1.800) | Total da Subetapa = 3.000 |
| G | 2 Subetapas em 1 Etapa (1.000 + 1.000) | Total da Etapa = 2.000 |
| H | 2 Etapas (1.000 + 1.000) | Total da Obra = 2.000 |

Todos os 8 cenários têm teste automatizado correspondente e passam.

---

## 14. Limitações

1. **Sem motor de planilha no ambiente** (mesma limitação da Etapa 2) — fórmulas verificadas por texto/estrutura, não por valor calculado ao vivo.
2. **Risco de nomes duplicados na SELEÇÃO do dropdown (Seção 21) — não resolvido definitivamente, preservado e documentado, conforme instruído:**
   - O comportamento atual (herdado da Etapa 2) permanece: o vínculo técnico é resolvido por `INDEX/MATCH` contra o **nome** escolhido no dropdown, que localiza a **primeira** ocorrência daquele nome. Se duas Subetapas em Etapas diferentes tiverem o mesmo nome (ex.: "Pintura" em "Acabamento Interno" e em "Acabamento Externo"), um Serviço pode ser vinculado à Subetapa errada sem aviso.
   - **Mitigação já aplicada nesta etapa:** os TOTAIS (Seção 9) não herdam essa ambiguidade da mesma forma, porque agregam por **ID técnico**, não por nome — uma vez que o vínculo é resolvido (corretamente ou não), a soma em si não introduz um segundo ponto de erro.
   - **Proposta técnica para homologação futura** (não implementada — decisão de negócio/UX, não do agente): exibir o nome da Subetapa já qualificado com a Etapa no dropdown (ex.: "Alvenaria › Pintura" em vez de só "Pintura"), o que exigiria uma coluna auxiliar de rótulo composto em Subetapas/Etapas. Isso reduziria a ambiguidade visual e, combinado com nomes únicos por Etapa, eliminaria o risco de vínculo incorreto — mas **muda a experiência do dropdown** e por isso não foi aplicado sem homologação (Seção 21: "não invente uma decisão de negócio").
3. **"Campo obrigatório" continua indireto** (herdado da Etapa 2) — nada impede uma linha com Descrição preenchida mas Quantidade/Valor Unitário vazios.
4. **Domínio de "Unidade de Medida" continua texto livre** (Seção 7, [H]) — nenhuma lista fechada foi criada.

---

## 15. Pendências (registradas, não resolvidas)

Nenhum [P]/[H]/[C] foi transformado em decisão definitiva além do que a Seção 36 autorizou explicitamente (Valor Previsto/Opção C) mais as duas aplicações diretas já fornecidas na própria homologação (Status do Serviço — Seção 18; termo/fórmula da Variação — Seção 13):

1. **Ambiguidade de nomes duplicados no dropdown** (Seção 14 acima) — decisão de UX/negócio pendente.
2. **Variação percentual e alertas visuais sobre a Variação** — deliberadamente não implementados (Seção 13/31); dependem de thresholds de REG-013/014/015, ainda [H].
3. **Orçamento Vigente completo** (Orçamento Inicial + Aportes + Alterações Aprovadas, REG-017) — esta etapa entrega apenas o orçamento previsto dos serviços; a integração com Aportes/Alterações é de etapa futura (Seções 15/16/17).
4. **Fluxo de transição entre valores de Status do Serviço** (ex.: quem pode marcar "Substituído", se exige vínculo com o serviço substituto) — não definido.
5. **Regra de arredondamento de exibição** além do formato de moeda padrão (`#,##0.00`) — não definida.
6. **Restrição de perfil para o Ajuste Manual** (quem pode ajustar) — não tratada; a Etapa 3 só dispensou justificativa/aprovação, não tratou de permissão por perfil.
7. **Mecanismo de proteção do Excel** (`SEC_001` Seção 4) — segue [H]; nenhuma proteção nova foi adicionada nesta etapa.

---

## 16. Riscos

1. **Vínculo incorreto por nome duplicado** (Seção 14/Limitação 2) é o risco mais concreto herdado e ainda não resolvido — recomenda-se priorizar a homologação da Seção 21 antes de uma obra real com Subetapas de nomes repetidos entre Etapas.
2. **Divergência entre o valor Python e o valor Excel** enquanto não houver um motor de cálculo real testando o arquivo: as fórmulas foram escritas e revisadas com cuidado (e testadas quanto à sua estrutura/sintaxe), mas só uma abertura real em Excel/LibreOffice confirma que produzem exatamente os mesmos números que `ServicoOrcamento.valor_calculado`/`valor_previsto`/`variacao` em Python.
3. **Renomeação de campo** (`Valor Total Orçado` → `Valor Calculado`) é uma mudança de nome, não de fórmula — baixo risco, mas qualquer integração futura que já esperasse o nome antigo precisa ser ajustada (nenhuma integração externa existe ainda, então o impacto é zero nesta fase).

---

## 17. Próximo passo

Conforme a ordem já registrada em `CRN_001`/relatórios anteriores, esta etapa completa a base do orçamento previsto dos serviços. Antes de avançar, recomenda-se:

1. Abrir `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx` em uma máquina com Excel/LibreOffice real para confirmar visualmente as fórmulas (pendência herdada da Etapa 2, reforçada aqui).
2. Homologar a Seção 21 (nomes duplicados) antes de usar o arquivo com uma obra real de estrutura complexa.
3. Só então iniciar, mediante nova autorização, o módulo Financeiro completo (Aportes, Custo Realizado, Orçamento Vigente — REG-017) ou o módulo de Execução (ligando as medições físicas já modeladas na Etapa 1 a este orçamento).

## 18. Checklist de conclusão da Etapa 3

- [x] orçamento foi implementado
- [x] quantidade existe
- [x] unidade existe
- [x] valor unitário existe
- [x] Valor Calculado funciona
- [x] Valor Previsto funciona
- [x] ajuste manual funciona
- [x] Valor Calculado é preservado
- [x] totais funcionam (Subetapa/Etapa/Obra, Python e Excel)
- [x] hierarquia é preservada
- [x] IDs permanecem internos
- [x] nomes amigáveis permanecem na interface
- [x] validações existem
- [x] testes foram criados (50 novos)
- [x] testes anteriores continuam passando (120 passed, 0 failed no total)
- [x] workbook foi validado (ZIP/XML íntegros; openpyxl com e sem `data_only`; Excel/LibreOffice reais indisponíveis — não afirmado)
- [x] cenários foram simulados (A–H, Seção 13)
- [x] relatório foi criado (este arquivo)
- [x] pendências foram registradas (Seção 15)
- [x] nenhuma regra não homologada foi inventada (Status do Serviço e Variação são aplicações diretas do texto da homologação, não interpretações)
- [x] git status foi verificado (Seção 19)
- [x] nenhum commit/push foi realizado

---

## 19. Git — estado final

`git status` após a implementação mostra os mesmos diretórios não rastreados já existentes desde a Etapa 1/2 (`config/`, `dados/`, `pytest.ini`, `relatorios/`, `scripts/`, `src/`, `testes/` — agora com os arquivos novos desta etapa dentro deles) e as mesmas modificações em documentos oficiais já registradas em rodadas anteriores desta sessão, mais as edições desta etapa em `DAD_001` e `REG_001` (Seção 3). **Nenhum commit ou push foi realizado.** A decisão de commit/push permanece com o responsável pelo projeto.
