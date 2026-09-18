# Alterações — Implementation Plan (Etapa 5)

> **For agentic workers:** REQUIRED SUB-SKILL: use subagent-driven-development
> (one fresh subagent per task, two-stage review: implement → test → review →
> correct) to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. This project has no CI — "commit" steps below mean
> "leave the working tree ready"; **do NOT run `git commit` or `git push`**
> (Seção 40 do protocolo desta etapa: nenhum commit/push sem autorização
> explícita do responsável pelo projeto).

**Goal:** Fechar REG-017 (Orçamento Vigente = Orçamento Inicial + Aportes +
Alterações Formais Aprovadas) implementando o módulo ALTERAÇÕES: domínio
fechado de Tipo (Escopo/Prazo/Orçamento) e Status de Aprovação
(Pendente/Aprovada/Rejeitada), Motor de Cálculos, aba Excel própria, e
atualização da fórmula de Orçamento Vigente na aba Resumo Financeiro.

**Architecture:** Novo pacote `src/alteracoes/` (mesmo padrão de
`src/orcamento/` e `src/financeiro/` — cada domínio é um pacote próprio,
nunca misturado). `src/financeiro/calculos.py:orcamento_vigente` passa a
importar e somar `src/alteracoes/calculos.py:total_alteracoes_aprovadas`,
criando a dependência `financeiro → alteracoes` (mesmo padrão já existente
`financeiro → orcamento`). Excel: nova aba "Alterações" mirando
byte-a-byte a estrutura da aba "Financeiro" (Etapa 4); a aba "Resumo
Financeiro" ganha uma linha nova e sua fórmula de Orçamento Vigente passa
de 2 para 3 parcelas.

**Tech Stack:** Python 3.14 (`.venv`), `openpyxl`, `pytest` — mesmo stack
das Etapas 1–4. Nenhuma dependência nova.

**Spec:** Design aprovado em chat nesta conversa (brainstorming — ver
histórico da sessão); decisões homologadas nesta rodada (2026-09-17,
"Etapa 5"):
1. Status de Aprovação = domínio fechado `Pendente / Aprovada / Rejeitada`; só `Aprovada` soma no Orçamento Vigente.
2. Sem workflow de aprovação — o Operador seleciona o Status diretamente (mesmo princípio "sistema informa, Operador decide" do Financeiro).
3. Tipo de Alteração = domínio fechado `Escopo / Prazo / Orçamento`; qualquer Tipo com "Impacto no Orçamento" preenchido participa do cálculo (a soma é pelo valor do campo, não pelo Tipo).
4. Nenhuma automação Escopo→Serviços/Orçamento — Alteração de Escopo é só registro informativo.

## Global Constraints

- Sem VBA/macro/ActiveX no Excel (AGENTS.md §10, herdado de todas as etapas).
- Fórmulas em português quando aplicável; nenhuma cor semântica de alerta inventada (DSG_001 Seção C.3, herdado).
- IDs técnicos sempre ocultos; nomes amigáveis na interface (AGENTS.md §11).
- Nenhum teste das Etapas 1–4 pode ser quebrado (162 passed hoje) — apenas `testes/test_excel_construtor.py:ABAS_ESPERADAS` pode precisar de ajuste mecânico (nova aba), mesmo tipo de ajuste já feito nas Etapas 3/4.
- `valor` de FINANCEIRO/PAGAMENTOS continua sempre não negativo (Etapa 4, Seção 21) — **não se aplica** a `impacto_orcamento`/`impacto_prazo_dias` de ALTERAÇÕES, que são deltas com sinal (podem reduzir).
- Nenhum commit/push nesta etapa sem autorização explícita.
- Ambiente de testes: `.venv/Scripts/python.exe -m pytest -v` (Windows, `pytest.ini` com `pythonpath = .`).

---

## Task 1: Domínio (enums + entidade + validador de sinal livre)

**Files:**
- Modify: `src/modelo/enums.py` (adicionar `TipoAlteracao`, `StatusAprovacaoAlteracao`)
- Modify: `src/validacoes/numeros.py` (adicionar `validar_numero`)
- Modify: `src/modelo/entidades.py` (atualizar `Alteracao`)
- Test: `testes/test_alteracoes.py` (criar — seção de domínio/entidade)

**Interfaces:**
- Consumes: nada (task base).
- Produces:
  - `TipoAlteracao` (Enum, valores `ESCOPO`/`PRAZO`/`ORCAMENTO`, propriedade `.rotulo` → "Escopo"/"Prazo"/"Orçamento").
  - `StatusAprovacaoAlteracao` (Enum, valores `PENDENTE`/`APROVADA`/`REJEITADA`, propriedade `.rotulo` → "Pendente"/"Aprovada"/"Rejeitada", propriedade `.integra_orcamento_vigente: bool` — `True` só para `APROVADA`).
  - `validar_numero(valor: object, nome_campo: str) -> None` — levanta `ErroValorNumericoInvalido` se não numérico (mesma exclusão de `bool` de `validar_numero_nao_negativo`), mas **aceita negativo**.
  - `Alteracao` com `tipo_alteracao: Optional[TipoAlteracao]`, `status_aprovacao: Optional[StatusAprovacaoAlteracao]`, `impacto_orcamento: Optional[float]`, `impacto_prazo_dias: Optional[int]` validados por `validar_numero`.

- [ ] **Step 1: Escrever os testes de domínio (devem falhar)**

Criar `testes/test_alteracoes.py`:

```python
"""
Testes do módulo ALTERAÇÕES (Etapa 5).

Cobre o domínio fechado de Tipo/Status (REG-012 fechado nesta etapa), o
Motor de Cálculos (`src/alteracoes/calculos.py`) e a integração com
Orçamento Vigente (REG-017 completo).
"""

from __future__ import annotations

from datetime import date

import pytest

from src.excecoes import ErroValorNumericoInvalido
from src.modelo.entidades import Alteracao
from src.modelo.enums import StatusAprovacaoAlteracao, TipoAlteracao


def test_tres_tipos_de_alteracao_homologados():
    assert {t.rotulo for t in TipoAlteracao} == {"Escopo", "Prazo", "Orçamento"}


def test_tres_status_de_aprovacao_homologados():
    assert {s.rotulo for s in StatusAprovacaoAlteracao} == {"Pendente", "Aprovada", "Rejeitada"}


def test_apenas_status_aprovada_integra_orcamento_vigente():
    for status in StatusAprovacaoAlteracao:
        esperado = status is StatusAprovacaoAlteracao.APROVADA
        assert status.integra_orcamento_vigente is esperado


def test_impacto_no_orcamento_negativo_e_permitido():
    """Diferente de Financeiro (Etapa 4): o sinal aqui é significativo (redução de orçamento)."""
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Redução de escopo",
        tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=-5000,
        status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_orcamento == -5000


def test_impacto_no_prazo_negativo_e_permitido():
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Antecipação de prazo",
        tipo_alteracao=TipoAlteracao.PRAZO, impacto_prazo_dias=-10, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_prazo_dias == -10


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_impacto_no_orcamento_nao_numerico_e_rejeitado(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        Alteracao(
            id="ALT-0001", id_obra="OBR-0001", descricao="X",
            impacto_orcamento=valor_invalido, data=date(2026, 9, 17),
        )


@pytest.mark.parametrize("valor_invalido", ["abc", object(), [1, 2], True])
def test_impacto_no_prazo_nao_numerico_e_rejeitado(valor_invalido):
    with pytest.raises(ErroValorNumericoInvalido):
        Alteracao(
            id="ALT-0001", id_obra="OBR-0001", descricao="X",
            impacto_prazo_dias=valor_invalido, data=date(2026, 9, 17),
        )


def test_alteracao_sem_impacto_informado_e_permitida():
    """Uma Alteração de Escopo pode não ter impacto financeiro nem de prazo (Seção informativa)."""
    alteracao = Alteracao(
        id="ALT-0001", id_obra="OBR-0001", descricao="Troca de acabamento",
        tipo_alteracao=TipoAlteracao.ESCOPO, data=date(2026, 9, 17),
    )
    assert alteracao.impacto_orcamento is None
    assert alteracao.impacto_prazo_dias is None
```

- [ ] **Step 2: Rodar os testes para confirmar a falha**

Run: `.venv/Scripts/python.exe -m pytest testes/test_alteracoes.py -v`
Expected: FAIL — `ImportError: cannot import name 'TipoAlteracao' from 'src.modelo.enums'` (ou equivalente).

- [ ] **Step 3: Adicionar `validar_numero` em `src/validacoes/numeros.py`**

Abrir o arquivo (já contém `validar_numero_nao_negativo`) e acrescentar, no final:

```python
def validar_numero(valor: object, nome_campo: str) -> None:
    """
    Levanta `ErroValorNumericoInvalido` se `valor` não for None e não for
    um número (`int`/`float`, excluindo `bool`) — mesma exclusão de tipo
    de `validar_numero_nao_negativo`, mas SEM exigir não-negatividade.

    Usado por campos que são deltas com sinal significativo (Etapa 5,
    "Impacto no Orçamento"/"Impacto no Prazo" de ALTERAÇÕES) — uma
    Alteração pode reduzir o orçamento ou antecipar um prazo, então o
    sinal negativo é um dado válido, não um erro (diferente de
    `Financeiro.valor`/`Pagamento.valor`, Etapa 4, Seção 21, cujo sinal é
    dado pelo Tipo e por isso nunca pode ser negativo).

    `None` é sempre aceito (campo ainda não preenchido).
    """
    if valor is None:
        return
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErroValorNumericoInvalido(
            f"{nome_campo} deve ser numérico; recebido: {valor!r}."
        )
```

- [ ] **Step 4: Adicionar os 2 Enums em `src/modelo/enums.py`**

Acrescentar no final do arquivo:

```python
class TipoAlteracao(str, Enum):
    """
    Domínio fechado do "Tipo de Alteração" — [D] HOMOLOGADO na Etapa 5
    (2026-09-17), fechando o que o DAD_001 registrava como lista
    proposta ([P]), não homologada: Escopo, Prazo, Orçamento.

    Qualquer Tipo pode ter Impacto no Orçamento preenchido — a soma no
    Motor de Cálculos (`src/alteracoes/calculos.py`) é pelo VALOR do
    campo "Impacto no Orçamento", não pelo Tipo em si (uma Alteração de
    Escopo também pode ter impacto financeiro). Alterações de Escopo NÃO
    disparam nenhuma automação sobre SERVIÇOS/ORÇAMENTO (Etapa 5,
    decisão homologada) — ficam apenas registradas informativamente.
    """

    ESCOPO = "escopo"
    PRAZO = "prazo"
    ORCAMENTO = "orcamento"

    @property
    def rotulo(self) -> str:
        rotulos = {
            TipoAlteracao.ESCOPO: "Escopo",
            TipoAlteracao.PRAZO: "Prazo",
            TipoAlteracao.ORCAMENTO: "Orçamento",
        }
        return rotulos[self]


class StatusAprovacaoAlteracao(str, Enum):
    """
    Domínio fechado do "Status de Aprovação" de ALTERAÇÕES — [D]
    HOMOLOGADO na Etapa 5 (2026-09-17), fechando REG-012 (antes [H]:
    "fluxo de aprovação não definido").

    Decisão homologada: SEM workflow de aprovação multi-etapa — o
    Operador seleciona o Status diretamente (mesmo princípio "sistema
    informa, Operador decide" já usado em Financeiro/Etapa 4). Só
    `APROVADA` integra o Orçamento Vigente (REG-017); `PENDENTE` e
    `REJEITADA` permanecem visíveis na base, nunca apagados (mesmo
    princípio de não-exclusão automática de `StatusServico`, Etapa 3).
    """

    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"

    @property
    def rotulo(self) -> str:
        rotulos = {
            StatusAprovacaoAlteracao.PENDENTE: "Pendente",
            StatusAprovacaoAlteracao.APROVADA: "Aprovada",
            StatusAprovacaoAlteracao.REJEITADA: "Rejeitada",
        }
        return rotulos[self]

    @property
    def integra_orcamento_vigente(self) -> bool:
        """True somente para Aprovada (REG-017)."""
        return self is StatusAprovacaoAlteracao.APROVADA
```

- [ ] **Step 5: Atualizar a dataclass `Alteracao` em `src/modelo/entidades.py`**

Import no topo do arquivo: adicionar `TipoAlteracao, StatusAprovacaoAlteracao` ao
`from src.modelo.enums import (...)` já existente, e `validar_numero` ao
`from src.validacoes.numeros import validar_numero_nao_negativo` (passa a
importar os dois nomes).

Substituir a dataclass `Alteracao` inteira por:

```python
@dataclass
class Alteracao:
    """ENTIDADE: ALTERAÇÕES (DAD_001) — domínio fechado na Etapa 5
    (2026-09-17): Tipo de Alteração e Status de Aprovação, fechando
    REG-012. Fecha também REG-017 (Orçamento Vigente completo — ver
    `src/alteracoes/calculos.py:total_alteracoes_aprovadas`).
    """

    id: str
    id_obra: str  # FK -> Obra.id
    descricao: str  # [P]
    tipo_alteracao: Optional[TipoAlteracao] = None
    # ^ [D] HOMOLOGADO na Etapa 5 — domínio fechado Escopo/Prazo/Orçamento.
    impacto_orcamento: Optional[float] = None
    # ^ [P]. Delta com sinal (pode reduzir o orçamento) — validado por
    # `validar_numero` (numérico, SEM exigir não-negativo; Etapa 5).
    impacto_prazo_dias: Optional[int] = None
    # ^ [P]. Delta com sinal (pode antecipar o prazo) — mesma validação.
    status_aprovacao: Optional[StatusAprovacaoAlteracao] = None
    # ^ [D] HOMOLOGADO na Etapa 5 — domínio fechado Pendente/Aprovada/
    # Rejeitada. Sem workflow: o Operador define diretamente.
    solicitante: Optional[str] = None  # [P]
    data: Optional[date] = None  # [P]

    def __post_init__(self) -> None:
        validar_numero(self.impacto_orcamento, "Impacto no Orçamento")
        validar_numero(self.impacto_prazo_dias, "Impacto no Prazo")
```

- [ ] **Step 6: Rodar os testes novos e a suíte completa**

Run: `.venv/Scripts/python.exe -m pytest testes/test_alteracoes.py -v`
Expected: 7 passed (os 7 testes do Step 1).

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: 169 passed (162 anteriores + 7 novos), 0 failed. Se algum teste
antigo falhar por causa da mudança de tipo de `tipo_alteracao`/
`status_aprovacao` (de `Optional[str]` para Enum), é porque algum teste
existente construía `Alteracao` com string solta nesses campos —
inspecionar e corrigir o teste antigo para usar o Enum (não inventar
comportamento novo; ver `testes/test_base_dados.py`, que hoje NÃO
constrói nenhum `Alteracao` — confirmar com `grep -rn "Alteracao(" testes/`
antes de assumir que não há nenhum uso a ajustar).

- [ ] **Step 7 (checkpoint — sem commit):** confirmar working tree com `git status` e `git diff --stat` para revisão antes da Task 2.

---

## Task 2: Motor de Cálculos + integração com Orçamento Vigente

**Files:**
- Create: `src/alteracoes/__init__.py` (vazio)
- Create: `src/alteracoes/calculos.py`
- Create: `src/alteracoes/movimentos.py`
- Modify: `src/financeiro/calculos.py` (função `orcamento_vigente`)
- Test: `testes/test_alteracoes.py` (adicionar seção de Motor de Cálculos)

**Interfaces:**
- Consumes: `TipoAlteracao`, `StatusAprovacaoAlteracao`, `Alteracao` (Task 1); `BaseDados` (`base.alteracoes: dict[str, Alteracao]`, já existe desde a Etapa 1 — nenhuma alteração em `src/base_dados/repositorio.py` é necessária, `adicionar_alteracao` já valida `id_obra`).
- Produces:
  - `total_alteracoes_aprovadas(base: BaseDados, id_obra: str) -> float`
  - `registrar_alteracao(base: BaseDados, alteracao: Alteracao) -> Alteracao`
  - `orcamento_vigente` (em `src/financeiro/calculos.py`) passa a somar 3 parcelas em vez de 2.

- [ ] **Step 1: Escrever os testes do Motor de Cálculos (devem falhar)**

Acrescentar ao final de `testes/test_alteracoes.py`:

```python
from src.alteracoes.calculos import total_alteracoes_aprovadas
from src.alteracoes.movimentos import registrar_alteracao
from src.base_dados.repositorio import BaseDados
from src.financeiro.calculos import orcamento_vigente
from src.financeiro.movimentos import registrar_lancamento
from src.modelo.entidades import Etapa, Financeiro, Obra, ServicoOrcamento, Subetapa
from src.modelo.enums import TipoLancamentoFinanceiro


def _obra_com_orcamento(base: BaseDados, valor_orcado: float) -> Obra:
    gid = base.gerador_id
    obra = base.adicionar_obra(Obra(id=gid.gerar("OBRAS"), nome="Obra"))
    etapa = base.adicionar_etapa(Etapa(id=gid.gerar("ETAPAS"), id_obra=obra.id, nome="Alvenaria"))
    subetapa = base.adicionar_subetapa(Subetapa(id=gid.gerar("SUBETAPAS"), id_etapa=etapa.id, nome="Reboco"))
    if valor_orcado:
        base.adicionar_servico(
            ServicoOrcamento(
                id=gid.gerar("SERVICOS_ORCAMENTO"), id_subetapa=subetapa.id, descricao="Serviço",
                quantidade_orcada=1, valor_unitario=valor_orcado,
            )
        )
    return obra


def _alterar(base: BaseDados, id_obra: str, *, impacto: float, status: StatusAprovacaoAlteracao) -> Alteracao:
    return registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=id_obra, descricao="Alteração",
            tipo_alteracao=TipoAlteracao.ORCAMENTO, impacto_orcamento=impacto,
            status_aprovacao=status, data=date(2026, 9, 17),
        ),
    )


def test_soma_apenas_alteracoes_aprovadas():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _alterar(base, obra.id, impacto=10_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.PENDENTE)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.REJEITADA)
    assert total_alteracoes_aprovadas(base, obra.id) == 10_000


def test_alteracao_aprovada_com_impacto_negativo_reduz_a_soma():
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    _alterar(base, obra.id, impacto=10_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=-3_000, status=StatusAprovacaoAlteracao.APROVADA)
    assert total_alteracoes_aprovadas(base, obra.id) == 7_000


def test_alteracao_sem_impacto_no_orcamento_nao_afeta_a_soma():
    """Uma Alteração de Escopo/Prazo sem Impacto no Orçamento não soma nem falha."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 0)
    registrar_alteracao(
        base,
        Alteracao(
            id=base.gerador_id.gerar("ALTERACOES"), id_obra=obra.id, descricao="Só prazo",
            tipo_alteracao=TipoAlteracao.PRAZO, impacto_prazo_dias=5,
            status_aprovacao=StatusAprovacaoAlteracao.APROVADA, data=date(2026, 9, 17),
        ),
    )
    assert total_alteracoes_aprovadas(base, obra.id) == 0


def test_orcamento_vigente_completo_soma_inicial_aportes_e_alteracoes_aprovadas():
    """REG-017 completo: Orçamento Inicial + Aportes + Alterações Formais Aprovadas."""
    base = BaseDados()
    obra = _obra_com_orcamento(base, 100_000)
    registrar_lancamento(
        base,
        Financeiro(
            id=base.gerador_id.gerar("FINANCEIRO"), id_obra=obra.id, tipo=TipoLancamentoFinanceiro.APORTE,
            data=date(2026, 9, 17), valor=20_000,
        ),
    )
    _alterar(base, obra.id, impacto=15_000, status=StatusAprovacaoAlteracao.APROVADA)
    _alterar(base, obra.id, impacto=99_999, status=StatusAprovacaoAlteracao.PENDENTE)
    assert orcamento_vigente(base, obra.id) == 100_000 + 20_000 + 15_000
```

- [ ] **Step 2: Rodar para confirmar a falha**

Run: `.venv/Scripts/python.exe -m pytest testes/test_alteracoes.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.alteracoes'`.

- [ ] **Step 3: Criar `src/alteracoes/__init__.py`** (arquivo vazio, mesmo padrão de `src/orcamento/__init__.py`/`src/financeiro/__init__.py`).

- [ ] **Step 4: Criar `src/alteracoes/calculos.py`**

```python
"""
Motor de Cálculos do módulo ALTERAÇÕES — Etapa 5.

Fecha REG-017 (Orçamento Vigente = Orçamento Inicial + Aportes +
Alterações Formais Aprovadas) — a única parcela que faltava desde a
Etapa 4, onde `orcamento_vigente` só somava Orçamento Inicial + Aportes
(ver `src/financeiro/calculos.py`, nota da Revisão 7 em REG-017).

Elegibilidade (Etapa 5, decisão homologada 2026-09-17): só Alterações
com `status_aprovacao == StatusAprovacaoAlteracao.APROVADA` somam —
Pendente e Rejeitada ficam visíveis na base, nunca excluídas do
repositório, apenas fora da soma (mesmo princípio de não-exclusão já
usado para `StatusServico`, Etapa 3, e para `situacao` de FINANCEIRO,
Etapa 4).

A soma é pelo campo `impacto_orcamento` (que pode ser negativo — uma
Alteração aprovada pode REDUZIR o orçamento), não pelo `tipo_alteracao`
— uma Alteração de Escopo também pode ter impacto financeiro.
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.enums import StatusAprovacaoAlteracao


def total_alteracoes_aprovadas(base: BaseDados, id_obra: str) -> float:
    """Σ Impacto no Orçamento das Alterações Aprovadas da Obra (REG-017)."""
    alteracoes = [
        a
        for a in base.alteracoes.values()
        if a.id_obra == id_obra
        and a.status_aprovacao is not None
        and a.status_aprovacao.integra_orcamento_vigente
    ]
    return sum((a.impacto_orcamento or 0.0) for a in alteracoes)
```

- [ ] **Step 5: Criar `src/alteracoes/movimentos.py`**

```python
"""
Orquestração de alto nível para registrar uma Alteração.

Mesmo raciocínio de `src/orcamento/servicos.py` (Etapa 3) e
`src/financeiro/movimentos.py` (Etapa 4): `Alteracao.__post_init__` já
garante que `impacto_orcamento`/`impacto_prazo_dias` são numéricos
(Etapa 5) — esta função não repete a validação, só delega o registro
para `BaseDados.adicionar_alteracao` (Etapa 1), responsável pela
integridade referencial (Obra existente).
"""

from __future__ import annotations

from src.base_dados.repositorio import BaseDados
from src.modelo.entidades import Alteracao


def registrar_alteracao(base: BaseDados, alteracao: Alteracao) -> Alteracao:
    """Registra uma Alteração já validada (ver docstring do módulo) na base."""
    return base.adicionar_alteracao(alteracao)
```

- [ ] **Step 6: Atualizar `orcamento_vigente` em `src/financeiro/calculos.py`**

No topo do arquivo, adicionar ao bloco de imports:
```python
from src.alteracoes.calculos import total_alteracoes_aprovadas
```

Substituir a função `orcamento_vigente` (hoje soma 2 parcelas) por:

```python
def orcamento_vigente(base: BaseDados, id_obra: str) -> float:
    """
    ORÇAMENTO VIGENTE = ORÇAMENTO INICIAL (Etapa 3) + APORTES (Etapa 4)
    + ALTERAÇÕES FORMAIS APROVADAS (Etapa 5) — REG-017 completo.

    Antes da Etapa 5, esta função somava apenas as 2 primeiras parcelas
    (ver relatório da Etapa 4, "Limitações"/REG-017 nota da Revisão 7) —
    a parcela de Alterações estava preparada, mas não implementada.
    """
    return (
        total_previsto_obra(base, id_obra)
        + total_aportes(base, id_obra)
        + total_alteracoes_aprovadas(base, id_obra)
    )
```

Também atualizar a docstring do módulo (topo do arquivo) removendo a
frase "A parcela de Alterações Formais Aprovadas está deliberadamente
ausente" — substituir por uma nota de que a Etapa 5 completou essa
parcela (mesmo padrão de nota histórica usado em outros módulos do
projeto ao evoluir uma decisão).

- [ ] **Step 7: Rodar os testes novos e a suíte completa**

Run: `.venv/Scripts/python.exe -m pytest testes/test_alteracoes.py -v`
Expected: 11 passed (7 da Task 1 + 4 desta task).

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: 173 passed, 0 failed (169 da Task 1 + 4 novos — **exceto** se
algum teste de Financeiro (Etapa 4) fixava um valor literal de
`orcamento_vigente` assumindo só 2 parcelas SEM Alteração nenhuma na
base — nesse caso o resultado não muda (não há Alteração cadastrada
naqueles testes, `total_alteracoes_aprovadas` retorna 0), então nenhum
teste antigo deve quebrar. Se algo quebrar, é sinal de que algum teste
antigo criava uma `Alteracao` "por engano" no mesmo `BaseDados` usado no
assert de `orcamento_vigente` — investigar e corrigir o teste, nunca a
fórmula nova.

- [ ] **Step 8 (checkpoint — sem commit):** revisar `git diff` de
`src/financeiro/calculos.py` para confirmar que só a função
`orcamento_vigente` e o import mudaram — nenhuma outra função do módulo
Financeiro foi tocada.

---

## Task 3: Interface Excel (aba Alterações + atualização do Resumo Financeiro)

**Files:**
- Modify: `src/excel/construtor_workbook.py` (nova aba + atualização de `_construir_aba_resumo_financeiro`, `construir_workbook`, `_criar_intervalos_nomeados` se necessário)
- Modify: `testes/test_excel_construtor.py` (`ABAS_ESPERADAS`)
- Modify: `testes/test_excel_financeiro.py` (ajustar os testes que verificam a fórmula de Orçamento Vigente/linhas do Resumo Financeiro, já que a numeração de linha muda)
- Test: `testes/test_excel_alteracoes.py` (criar)

**Interfaces:**
- Consumes: `TipoAlteracao`, `StatusAprovacaoAlteracao` (Task 1); `total_alteracoes_aprovadas` (Task 2, usado só em Python/testes, não em fórmula Excel — a soma no Excel é feita por `SUMIFS` direto na aba Alterações, mesmo padrão de Financeiro).
- Produces: aba "Alterações" (colunas `COL_ALT_*`, lista `COLUNAS_ALTERACOES`); linha nova "Alterações Aprovadas" no Resumo Financeiro; fórmula de "Orçamento Vigente" com 3 termos.

- [ ] **Step 1: Ler a estrutura atual para confirmar os números de linha do Resumo Financeiro antes de editar**

Run: `.venv/Scripts/python.exe -c "from src.base_dados.repositorio import BaseDados; from src.excel.construtor_workbook import construir_workbook; wb = construir_workbook(BaseDados()); ws = wb['Resumo Financeiro']; [print(r, ws.cell(row=r,column=1).value) for r in range(1,20)]"`

Confirmar que hoje: linha 2 = Orçamento Inicial, linha 3 = Aportes, linha
4 = Orçamento Vigente, linha 5 = Custo Realizado, linha 6 = Saldo
Orçamentário, linha 7 = % Consumido, linha 8 = Outras Entradas, linha 9 =
Outras Saídas, linha 10 = Total de Entradas, linha 11 = Total Pago,
linha 12 = Total de Saídas, linha 13 = Saldo de Caixa, linha 14 = Total A
Pagar, linha 15 = Estouro de Orçamento — **se a saída for diferente
disso, ajustar todos os números de linha abaixo de acordo com a saída
real antes de continuar** (não assumir — confirmar).

- [ ] **Step 2: Escrever os testes de Excel (devem falhar)**

Criar `testes/test_excel_alteracoes.py`:

```python
"""
Testes da aba Alterações e da atualização do Resumo Financeiro (Etapa 5).

Mesmo raciocínio de `testes/test_excel_financeiro.py` (Etapa 4): sem
motor de planilha neste ambiente por padrão — verificação pelo TEXTO da
fórmula. Ver também Task 4 deste plano para validação real via Excel COM
quando disponível.
"""

from __future__ import annotations

import openpyxl
import pytest

from src.base_dados.repositorio import BaseDados
from src.excel.construtor_workbook import (
    COL_ALT_IMPACTO_ORCAMENTO,
    COL_ALT_STATUS,
    COL_ALT_TIPO,
    COLUNAS_ALTERACOES,
    construir_workbook,
)
from src.modelo.enums import StatusAprovacaoAlteracao, TipoAlteracao


def test_aba_alteracoes_existe(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    wb = openpyxl.load_workbook(caminho)
    assert "Alterações" in wb.sheetnames


def test_cabecalho_da_aba_alteracoes(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Alterações"]
    titulos_esperados = [titulo for titulo, _l, _o, _c in COLUNAS_ALTERACOES]
    titulos_no_arquivo = [ws.cell(row=1, column=i + 1).value for i in range(len(COLUNAS_ALTERACOES))]
    assert titulos_no_arquivo == titulos_esperados


def test_dropdown_de_tipo_de_alteracao_tem_3_valores(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Alterações"]
    letra_tipo = ws.cell(row=1, column=COL_ALT_TIPO).column_letter
    dvs = [dv for dv in ws.data_validations.dataValidation if str(dv.sqref).startswith(f"{letra_tipo}2")]
    assert len(dvs) == 1
    for tipo in TipoAlteracao:
        assert tipo.rotulo in dvs[0].formula1
    assert dvs[0].formula1.count(",") == 2  # exatamente 3 itens


def test_dropdown_de_status_de_aprovacao_tem_3_valores(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Alterações"]
    letra_status = ws.cell(row=1, column=COL_ALT_STATUS).column_letter
    dvs = [dv for dv in ws.data_validations.dataValidation if str(dv.sqref).startswith(f"{letra_status}2")]
    assert len(dvs) == 1
    for status in StatusAprovacaoAlteracao:
        assert status.rotulo in dvs[0].formula1
    assert dvs[0].formula1.count(",") == 2


def test_impacto_no_orcamento_aceita_negativo_sem_validacao_de_sinal(tmp_path):
    """Diferente de Financeiro!Valor (Etapa 4) — aqui NÃO há DataValidation de >= 0."""
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Alterações"]
    letra = ws.cell(row=1, column=COL_ALT_IMPACTO_ORCAMENTO).column_letter
    dvs_de_sinal = [
        dv for dv in ws.data_validations.dataValidation
        if str(dv.sqref).startswith(f"{letra}2") and dv.operator == "greaterThanOrEqual"
    ]
    assert dvs_de_sinal == []


def test_resumo_financeiro_orcamento_vigente_soma_3_parcelas(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Resumo Financeiro"]
    linhas = {ws.cell(row=r, column=1).value: r for r in range(1, 20)}
    linha_vigente = linhas["Orçamento Vigente"]
    formula = ws.cell(row=linha_vigente, column=2).value
    assert formula.count("+") == 2  # 3 parcelas = 2 somas
    assert "Alterações Aprovadas" in linhas


def test_resumo_financeiro_alteracoes_aprovadas_usa_sumifs_por_status(tmp_path):
    caminho = tmp_path / "v.xlsx"
    construir_workbook(BaseDados()).save(caminho)
    ws = openpyxl.load_workbook(caminho)["Resumo Financeiro"]
    linhas = {ws.cell(row=r, column=1).value: r for r in range(1, 20)}
    linha = linhas["Alterações Aprovadas"]
    formula = ws.cell(row=linha, column=2).value
    assert "SUMIFS(" in formula
    assert "Alterações!" in formula
    assert StatusAprovacaoAlteracao.APROVADA.rotulo in formula
```

- [ ] **Step 3: Rodar para confirmar a falha**

Run: `.venv/Scripts/python.exe -m pytest testes/test_excel_alteracoes.py -v`
Expected: FAIL — `ImportError: cannot import name 'COL_ALT_IMPACTO_ORCAMENTO'`.

- [ ] **Step 4: Adicionar as constantes de coluna em `src/excel/construtor_workbook.py`**

No topo do arquivo, no bloco de import de enums, trocar:
```python
from src.modelo.enums import StatusServico, TipoLancamentoFinanceiro
```
por:
```python
from src.modelo.enums import StatusAprovacaoAlteracao, StatusServico, TipoAlteracao, TipoLancamentoFinanceiro
```

Logo após o bloco `COLUNAS_PAGAMENTOS`/`COL_PAG_*` (Etapa 4), acrescentar:

```python
# --------------------------------------------------------------------
# Etapa 5 — colunas da aba Alterações
# --------------------------------------------------------------------
COLUNAS_ALTERACOES = [
    ("ID (técnico)", 14, True, False),        # A
    ("Tipo", 16, False, False),                # B
    ("Data", 14, False, False),                # C
    ("Descrição", 34, False, False),           # D
    ("Impacto no Orçamento", 20, False, False),# E
    ("Impacto no Prazo (dias)", 20, False, False), # F
    ("Status de Aprovação", 18, False, False), # G
    ("Solicitante", 22, False, False),         # H
    ("ID_Obra (técnico)", 16, True, False),    # I
]
COL_ALT_ID = 1
COL_ALT_TIPO = 2
COL_ALT_DATA = 3
COL_ALT_DESCRICAO = 4
COL_ALT_IMPACTO_ORCAMENTO = 5
COL_ALT_IMPACTO_PRAZO = 6
COL_ALT_STATUS = 7
COL_ALT_SOLICITANTE = 8
COL_ALT_ID_OBRA = 9
```

Logo após o bloco `_ROTULO_OUTRAS_SAIDAS = ...` (lista de rótulos de
Financeiro), acrescentar:

```python
# Listas fechadas de Tipo/Status de Alteração (Etapa 5, mesma fonte
# usada pelo Python — nunca digitadas de novo à mão).
_ROTULOS_TIPO_ALTERACAO = [t.rotulo for t in TipoAlteracao]
_LISTA_TIPO_ALTERACAO = '"' + ",".join(_ROTULOS_TIPO_ALTERACAO) + '"'
_ROTULOS_STATUS_APROVACAO = [s.rotulo for s in StatusAprovacaoAlteracao]
_LISTA_STATUS_APROVACAO = '"' + ",".join(_ROTULOS_STATUS_APROVACAO) + '"'
_ROTULO_APROVADA = StatusAprovacaoAlteracao.APROVADA.rotulo
```

- [ ] **Step 5: Adicionar `_construir_aba_alteracoes`**

Inserir a função logo antes de `# Aba técnica oculta: Base_Dados`
(mesma posição relativa das abas de Financeiro/Pagamentos/Resumo
Financeiro criadas na Etapa 4):

```python
# --------------------------------------------------------------------
# Aba: Alterações (Etapa 5) — Escopo / Prazo / Orçamento, com Status de
# Aprovação (REG-012 fechado) — fecha o Orçamento Vigente (REG-017)
# --------------------------------------------------------------------
def _construir_aba_alteracoes(wb: Workbook, alteracoes: list) -> None:
    ws = wb.create_sheet("Alterações")
    _escrever_cabecalho(ws, COLUNAS_ALTERACOES)

    ultima_linha = 1 + len(alteracoes) + LINHAS_MODELO
    prefixo = PREFIXOS_ID["ALTERACOES"]

    for r in range(2, ultima_linha + 1):
        indice = r - 2
        if indice < len(alteracoes):
            alteracao = alteracoes[indice]
            ws.cell(row=r, column=COL_ALT_ID, value=alteracao.id)
            rotulo_tipo = alteracao.tipo_alteracao.rotulo if alteracao.tipo_alteracao is not None else None
            ws.cell(row=r, column=COL_ALT_TIPO, value=rotulo_tipo)
            celula_data = ws.cell(row=r, column=COL_ALT_DATA, value=alteracao.data)
            celula_data.number_format = "DD/MM/YYYY"
            ws.cell(row=r, column=COL_ALT_DESCRICAO, value=alteracao.descricao)
            ws.cell(row=r, column=COL_ALT_IMPACTO_ORCAMENTO, value=alteracao.impacto_orcamento)
            ws.cell(row=r, column=COL_ALT_IMPACTO_PRAZO, value=alteracao.impacto_prazo_dias)
            rotulo_status = alteracao.status_aprovacao.rotulo if alteracao.status_aprovacao is not None else None
            ws.cell(row=r, column=COL_ALT_STATUS, value=rotulo_status)
            ws.cell(row=r, column=COL_ALT_SOLICITANTE, value=alteracao.solicitante)
        else:
            ws.cell(
                row=r,
                column=COL_ALT_ID,
                value=f'=IF($D{r}="","","{prefixo}-"&TEXT(ROW()-1,"0000"))',
            )
            ws.cell(row=r, column=COL_ALT_DATA).number_format = "DD/MM/YYYY"

        # ID_Obra: sempre fórmula, linha literal ou não (mesmo padrão de Financeiro).
        ws.cell(
            row=r,
            column=COL_ALT_ID_OBRA,
            value=f'=IF($D{r}="","",Base_Dados!$B$2)',
        )

    # Dropdown "Tipo" — domínio fechado (Etapa 5).
    dv_tipo = DataValidation(
        type="list", formula1=_LISTA_TIPO_ALTERACAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Tipo inválido",
        error="Selecione um dos tipos oficiais: " + ", ".join(_ROTULOS_TIPO_ALTERACAO) + ".",
    )
    ws.add_data_validation(dv_tipo)
    dv_tipo.add(f"B2:B{ultima_linha}")

    # Dropdown "Status de Aprovação" — domínio fechado (Etapa 5).
    dv_status = DataValidation(
        type="list", formula1=_LISTA_STATUS_APROVACAO, allow_blank=True,
        showErrorMessage=True, errorTitle="Status inválido",
        error="Selecione um dos status oficiais: " + ", ".join(_ROTULOS_STATUS_APROVACAO) + ".",
    )
    ws.add_data_validation(dv_status)
    dv_status.add(f"G2:G{ultima_linha}")

    # NENHUMA validação de sinal em Impacto no Orçamento/Prazo (Etapa 5,
    # decisão homologada) — diferente de Financeiro!Valor (Etapa 4,
    # Seção 21): aqui o sinal negativo é um dado válido (redução).

    for r in range(2, ultima_linha + 1):
        ws.cell(row=r, column=COL_ALT_IMPACTO_ORCAMENTO).number_format = FORMATO_MOEDA_BR

    _aplicar_bordas(ws, ultima_linha, len(COLUNAS_ALTERACOES))
    _aplicar_filtro_e_congelamento(ws, ultima_linha, len(COLUNAS_ALTERACOES))
```

- [ ] **Step 6: Registrar `"ALTERACOES": "ALT"` — já existe**

Confirmar em `config/ids_config.py` que `PREFIXOS_ID["ALTERACOES"] ==
"ALT"` (já existe desde a Etapa 1) — **nenhuma alteração necessária**
neste arquivo.

- [ ] **Step 7: Chamar a nova aba em `construir_workbook`**

Em `construir_workbook`, logo após a linha que chama
`_construir_aba_resumo_financeiro(...)`, inserir a chamada à nova aba
**antes** da chamada a `_construir_aba_resumo_financeiro` (a aba
Alterações precisa existir antes de a fórmula do Resumo Financeiro
referenciá-la — mesma ordem lógica já usada para Financeiro/Pagamentos):

```python
    _construir_aba_financeiro(wb, financeiro)
    _construir_aba_pagamentos(wb, list(base.pagamentos.values()), base.financeiro)
    _construir_aba_alteracoes(wb, list(base.alteracoes.values()))
    _construir_aba_resumo_financeiro(wb, ultima_linha_financeiro=ultima_linha_financeiro, ultima_linha_alteracoes=ultima_linha_alteracoes)
```

Antes desse trecho, calcular `ultima_linha_alteracoes` do mesmo jeito que
`ultima_linha_financeiro` já é calculado:

```python
    alteracoes = list(base.alteracoes.values())
    ultima_linha_alteracoes = 1 + len(alteracoes) + LINHAS_MODELO
```//

- [ ] **Step 8: Atualizar `_construir_aba_resumo_financeiro`**

Alterar a assinatura da função para aceitar o novo parâmetro:

```python
def _construir_aba_resumo_financeiro(wb: Workbook, *, ultima_linha_financeiro: int, ultima_linha_alteracoes: int) -> None:
```

Dentro da função, definir a letra da coluna de impacto:
```python
    letra_impacto_alt = get_column_letter(COL_ALT_IMPACTO_ORCAMENTO)
    letra_status_alt = get_column_letter(COL_ALT_STATUS)
    ul_alt = ultima_linha_alteracoes
```

Inserir uma nova linha "Alterações Aprovadas" **entre** "Aportes" e
"Orçamento Vigente" (ou seja, imediatamente depois do bloco
`_linha("Aportes", ...)` e antes do bloco `linha_orcamento_vigente = ...`):

```python
    linha_alteracoes_aprovadas = linha_atual
    _linha(
        "Alterações Aprovadas",
        f'=SUMIFS(Alterações!${letra_impacto_alt}$2:${letra_impacto_alt}${ul_alt},'
        f'Alterações!${letra_status_alt}$2:${letra_status_alt}${ul_alt},"{_ROTULO_APROVADA}")',
    )
    linha_orcamento_vigente = linha_atual
    _linha(
        "Orçamento Vigente",
        f"=B{linha_orcamento_inicial}+B{linha_aportes}+B{linha_alteracoes_aprovadas}",
    )
```

(Remover a linha antiga `_linha("Orçamento Vigente", f"=B{linha_orcamento_inicial}+B{linha_aportes}")` — ela é substituída pela versão de 3 parcelas acima.)

**Nenhuma outra linha do Resumo Financeiro muda de fórmula** — apenas os
números de linha subsequentes (Custo Realizado em diante) deslocam +1;
como o código usa variáveis (`linha_atual`, `linha_custo` etc.), isso é
automático — não editar mais nada nessa função.

- [ ] **Step 9: Atualizar a chamada em `construir_workbook`**

Confirmar que a chamada feita no Step 7 já passa `ultima_linha_alteracoes` corretamente.

- [ ] **Step 10: Atualizar `ABAS_ESPERADAS` em `testes/test_excel_construtor.py`**

```python
ABAS_ESPERADAS = [
    "Início",
    "Etapas",
    "Subetapas",
    "Serviços",
    "Financeiro",
    "Pagamentos",
    "Alterações",
    "Resumo Financeiro",
    "Base_Dados",
]
```

(Inserir `"Alterações"` entre `"Pagamentos"` e `"Resumo Financeiro"` —
mesma ordem em que as abas são criadas em `construir_workbook`.)

- [ ] **Step 11: Ajustar `testes/test_excel_financeiro.py`**

Os testes `test_resumo_orcamento_vigente_soma_inicial_e_aportes`,
`test_resumo_percentual_consumido_trata_divisao_por_zero`,
`test_resumo_saldo_de_caixa_nao_usa_custo_realizado_diretamente` e
`test_resumo_estouro_de_orcamento_nao_bloqueia_apenas_informa` fixam
números de linha literais (`row=2`, `row=4`, `row=7`, `row=6` etc.) que
agora deslocam. Reabrir cada um desses 4 testes e:
1. Onde o teste usa `ws.cell(row=<N>, column=2).value` com um número
   fixo, trocar por busca pelo rótulo (mesmo padrão já usado em
   `test_resumo_estouro_de_orcamento_nao_bloqueia_apenas_informa`, que já
   usa `linhas_rotulo = {...}` — replicar esse padrão nos outros 3 testes
   em vez de manter números fixos).
2. `test_resumo_orcamento_vigente_soma_inicial_e_aportes`: renomear para
   `test_resumo_orcamento_vigente_soma_inicial_aportes_e_alteracoes` e
   trocar o assert de `== "=B2+B3"` por `.count("+") == 2` (a asserção
   exata de 2 termos já não é mais válida — a Task 3 introduziu a
   3ª parcela; **não deixar as duas asserções conflitantes** — este teste
   deve validar apenas que a fórmula referencia `B` da linha de
   Alterações Aprovadas, sem fixar a fórmula inteira literal, já que ela
   depende de 3 números de linha que podem variar).
3. Rodar `.venv/Scripts/python.exe -m pytest testes/test_excel_financeiro.py -v` e
   corrigir cada falha por rótulo, não por posição fixa — repetir até
   os 22 testes desse arquivo passarem de novo.

- [ ] **Step 12: Rodar os testes novos e a suíte completa**

Run: `.venv/Scripts/python.exe -m pytest testes/test_excel_alteracoes.py testes/test_excel_construtor.py testes/test_excel_financeiro.py -v`
Expected: todos passando (7 novos + 16 + 22 ajustados).

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: 180 passed, 0 failed (173 da Task 2 + 7 novos desta task).

- [ ] **Step 13 (checkpoint — sem commit):** `git diff --stat` para
confirmar que só os arquivos listados no cabeçalho desta task foram
tocados.

---

## Task 4: Geração do workbook V4, validação estrutural e (se disponível) validação real em Excel

**Files:**
- Create: `scripts/gerar_arquivo_obra_modelo_v4.py`
- Modify: `scripts/gerar_arquivo_obra_modelo_v3.py` (depreciar, mesmo padrão das Etapas 3/4)
- Create: `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx` (gerado pelo script, não escrito à mão)

**Interfaces:**
- Consumes: `construir_workbook` (Task 3).
- Produces: arquivo `.xlsx` V4 no disco.

- [ ] **Step 1: Depreciar `scripts/gerar_arquivo_obra_modelo_v3.py`**

Substituir o conteúdo pelo mesmo padrão de
`scripts/gerar_arquivo_obra_modelo_v2.py` (Etapa 4), adaptando os nomes:
docstring "DEPRECIADO A PARTIR DA ETAPA 5", mensagem apontando para
`gerar_arquivo_obra_modelo_v4.py`, motivo: `construir_workbook` evoluiu
com a aba Alterações.

- [ ] **Step 2: Criar `scripts/gerar_arquivo_obra_modelo_v4.py`**

Copiar `scripts/gerar_arquivo_obra_modelo_v3.py` (versão pré-depreciação,
antes do Step 1 — ou copiar de `gerar_arquivo_obra_modelo_v2.py` como
molde) trocando `NOME_ARQUIVO = "GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx"` e
o texto da docstring para "Etapa 5 (Alterações)".

- [ ] **Step 3: Registrar hash/tamanho de V1, V2 e V3 ANTES de gerar V4**

Run (PowerShell ou `certutil`/`md5sum`, o que estiver disponível):
```
md5sum dados/GESTAO_DE_OBRAS_OBRA_MODELO_V1.xlsx dados/GESTAO_DE_OBRAS_OBRA_MODELO_V2.xlsx dados/GESTAO_DE_OBRAS_OBRA_MODELO_V3.xlsx
```
Guardar a saída para comparação no Step 5.

- [ ] **Step 4: Gerar V4**

Run: `.venv/Scripts/python.exe scripts/gerar_arquivo_obra_modelo_v4.py`
Expected: imprime o caminho e a lista de 9 abas (incluindo "Alterações").

- [ ] **Step 5: Confirmar que V1/V2/V3 não mudaram**

Repetir o comando do Step 3 e comparar hash a hash — devem ser
idênticos aos do Step 3.

- [ ] **Step 6: Validação estrutural (ZIP/XML/openpyxl)**

Run:
```
.venv/Scripts/python.exe -c "
import zipfile, xml.etree.ElementTree as ET
import openpyxl
caminho = 'dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx'
with zipfile.ZipFile(caminho) as z:
    assert z.testzip() is None
    for nome in [n for n in z.namelist() if n.endswith('.xml') or n.endswith('.rels')]:
        ET.fromstring(z.read(nome))
openpyxl.load_workbook(caminho, data_only=False)
openpyxl.load_workbook(caminho, data_only=True)
print('OK')
"
```
Expected: `OK`, sem exceção.

- [ ] **Step 7: Validação REAL em Excel (só se `EXCEL.EXE` existir no
ambiente — verificar antes com** `find "/c/Program Files/Microsoft Office" -iname "EXCEL.EXE" 2>/dev/null` **ou equivalente)**

Se Excel estiver disponível: montar (via script Python temporário, salvo
no diretório de scratchpad da sessão — nunca no repositório) um
`BaseDados` de exemplo com pelo menos: 1 Serviço orçado em 100.000; 1
Aporte de 20.000; 2 Alterações do tipo Orçamento — uma Aprovada com
impacto +15.000, outra Pendente com impacto +99.999 (para confirmar que
NÃO entra na soma); salvar via `construir_workbook`; abrir com
`New-Object -ComObject Excel.Application`, `CalculateFullRebuild()`, ler
`Resumo Financeiro!B2:B16` e confirmar que "Orçamento Vigente" =
135.000 (100.000 + 20.000 + 15.000) e "Alterações Aprovadas" = 15.000.
Fechar o workbook sem salvar e finalizar o processo Excel
(`$excel.Quit()`), depois confirmar via `tasklist` que nenhum `EXCEL.EXE`
ficou residual (matar com `taskkill` se necessário). Apagar o arquivo de
teste do scratchpad ao final.

Se Excel NÃO estiver disponível: registrar a limitação no relatório
final (Task 5) exatamente como nas Etapas 2/3 — não afirmar uma
abertura real que não ocorreu.

- [ ] **Step 8 (checkpoint — sem commit):** `git status` — confirmar que
apenas os arquivos esperados desta task (script novo, script
depreciado, `dados/GESTAO_DE_OBRAS_OBRA_MODELO_V4.xlsx`) aparecem como
novos/modificados, e que V1/V2/V3 não aparecem como modificados.

---

## Task 5: Documentação formal + relatório final + auditoria de checklist

**Files:**
- Modify: `05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md` (Revisão 8: REG-012 e REG-017 fechados)
- Modify: `02_MODELO_DE_DADOS_E_DICIONARIO/DAD_001_MODELO_DE_DADOS_E_DICIONARIO_V6_3.md` (Revisão 8: entidade ALTERAÇÕES)
- Create: `relatorios/ALTERACOES_ETAPA_5_V1.md`

**Interfaces:**
- Consumes: resultado final de testes/validação das Tasks 1–4 (números exatos de teste, resultado da validação em Excel real ou sua ausência).
- Produces: nada consumido por outra task (última task do plano).

- [ ] **Step 1: Reler REG-012 e REG-017 (versão atual, pós-Revisão 7) antes de editar**

Run (para não reescrever "no escuro"): abrir
`05_REGRAS_DE_NEGOCIO/REG_001_REGRAS_DE_NEGOCIO_V6_3.md` e localizar as
seções `### REG-012` e `### REG-017` — copiar o texto atual antes de
substituir, para poder citar "antes/depois" no relatório final.

- [ ] **Step 2: Reescrever REG-012 (Aprovação de Alteração) para [D]**

Trocar o cabeçalho `### REG-012 — Aprovação de Alteração` (hoje [H]) por
`### REG-012 — Aprovação de Alteração — [D] HOMOLOGADO EM 2026-09-17
(Revisão 8)` e o corpo por uma versão que registre: domínio fechado
Pendente/Aprovada/Rejeitada; decisão explícita de NÃO criar workflow
multi-etapa (o Operador seleciona o Status diretamente, mesmo princípio
de REG-032 do Financeiro); nenhuma exigência de justificativa/aprovador
distinto foi inventada. Seguir o mesmo formato de seção (Descrição /
Entrada / Condição / Resultado / Status / Teste necessário) das demais
regras do documento — usar REG-004 (Revisão 7) como modelo de estrutura.

- [ ] **Step 3: Reescrever a nota de REG-017 removendo a ressalva de escopo parcial**

A Revisão 7 acrescentou uma nota em REG-017: "apenas a parcela Orçamento
Inicial + Aportes está implementada nesta etapa". Substituir essa nota
por: "**Nota da Revisão 8:** a parcela de Alterações Formais Aprovadas
foi implementada — `src/alteracoes/calculos.py:total_alteracoes_aprovadas`
+ `src/financeiro/calculos.py:orcamento_vigente`. REG-017 está, a partir
desta revisão, **completamente implementado** — as 3 parcelas da
fórmula homologada em 2026-09-16 (Orçamento Inicial + Aportes +
Alterações Formais Aprovadas) somam de fato."

- [ ] **Step 4: Adicionar o parágrafo "Motivo da Revisão 8" no topo do arquivo**

Seguir o padrão exato dos parágrafos "Motivo da Revisão N" já existentes
(ver Revisão 7 como modelo mais recente) — trocar o título do documento
de "Revisão 7 — Financeiro" para "Revisão 8 — Alterações".

- [ ] **Step 5: Adicionar "Registro de homologação — Revisão 8" ao final do arquivo**

Seguir o padrão exato das seções "Registro de homologação — Revisão N"
já existentes (mesmo formato da Revisão 7).

- [ ] **Step 6: Atualizar `DAD_001` — entidade ALTERAÇÕES**

Reescrever a tabela de campos da entidade ALTERAÇÕES: "Tipo de
Alteração" e "Status de Aprovação" passam de [H]/domínio proposto para
[D] domínio fechado (citando os 3 valores de cada); "Impacto no
Orçamento"/"Impacto no Prazo" ganham observação sobre aceitar valores
negativos (delta com sinal, diferente de FINANCEIRO). Atualizar o título
do documento para "Revisão 8 — Alterações" e adicionar "Registro de
homologação — Revisão 8" ao final, seguindo o mesmo padrão das revisões
anteriores.

- [ ] **Step 7: Rodar a suíte completa uma última vez antes do relatório**

Run: `.venv/Scripts/python.exe -m pytest -v`
Anotar o número exato de testes coletados/passados para citar no
relatório (não estimar — copiar o número real da saída).

- [ ] **Step 8: Escrever `relatorios/ALTERACOES_ETAPA_5_V1.md`**

Seguir EXATAMENTE a mesma estrutura de 19 seções de
`relatorios/FINANCEIRO_ETAPA_4_V1.md` (Objetivo; Arquivos criados;
Arquivos alterados; Modelo de dados; Tipos/domínios; Regras
implementadas; Motor de Cálculos; Integração com Orçamento Vigente;
Testes criados; Quantidade total de testes e resultado; Cenários
simulados; Resultado; Limitações; Pendências; Riscos; Próximo passo;
Checklist de conclusão; Git — estado final), adaptando o conteúdo para
Alterações. Incluir explicitamente:
- Que REG-017 está agora 100% implementado (as 3 parcelas).
- Que REG-012 foi fechado com domínio simples, sem workflow.
- O resultado real da validação em Excel (Task 4, Step 7) — com números
  exatos se Excel estava disponível, ou a limitação registrada se não.
- Pendências herdadas que **não** foram resolvidas nesta etapa: nenhuma
  automação Escopo→Serviços; nenhuma integração com Planejamento/
  Cronograma para "Impacto no Prazo"; domínio de cancelamento de
  FINANCEIRO (Etapa 4, ainda [H]); Perfis/Acesso (ainda não construído).

- [ ] **Step 9: Auditoria final (checklist, sem subagente — conferência direta)**

Conferir, um a um, contra o resultado real (não assumir):
- [ ] todos os testes das Etapas 1–4 continuam passando;
- [ ] todos os testes novos desta etapa passam;
- [ ] `ABAS_ESPERADAS` reflete as 9 abas reais do workbook gerado;
- [ ] V1/V2/V3 preservados (hash idêntico);
- [ ] V4 gerado e validado estruturalmente (e em Excel real, se disponível);
- [ ] nenhum termo "Desvio" foi introduzido (grep na aba nova, mesmo teste de regressão do padrão de Financeiro);
- [ ] `git status` mostra exatamente os arquivos esperados, nada além disso;
- [ ] nenhum commit/push foi realizado.

- [ ] **Step 10 (checkpoint final — sem commit):** apresentar ao
responsável pelo projeto o relatório, os riscos e pendências, e parar
(mesma "Regra de Parada" já usada nas Etapas 3/4) — não iniciar
automaticamente uma "Etapa 6".

---

## Self-Review Notes (preenchido durante a escrita deste plano)

- **Cobertura da spec:** as 4 decisões homologadas no brainstorming (Status de Aprovação fechado, sem workflow, Tipo de Alteração fechado, sem automação de Escopo) têm task/step correspondente (Task 1 Steps 4–5; Task 1 Step 4/decisão 2; Task 1 Step 4; ausência deliberada de qualquer step que edite `src/orcamento/`).
- **Consistência de tipos:** `total_alteracoes_aprovadas(base, id_obra) -> float` é o mesmo nome/assinatura usado em Task 2 (produzido) e Task 2 Step 6 (consumido em `orcamento_vigente`) — confirmado sem divergência de nome entre tasks.
- **Placeholders:** nenhum "TBD"/"similar to Task N sem código" — todo Step de código tem o código completo inline.
