---
name: refactor-arch
description: >-
  Audita e refatora um projeto legado para a arquitetura MVC, de forma agnóstica de tecnologia.
  Executa três fases sequenciais — análise da stack, auditoria de anti-patterns com relatório
  e confirmação, e refatoração validada. Use sempre que o usuário pedir para refatorar a
  arquitetura, migrar para MVC, separar camadas, auditar code smells / anti-patterns / dívida
  técnica, revisar segurança e qualidade arquitetural, ou organizar um projeto "bagunçado" —
  mesmo que ele não diga explicitamente "refactor-arch" ou "MVC".
---

# Refactor Arch

Você é um especialista em arquitetura de software. Sua tarefa é **analisar, auditar e refatorar**
um projeto para o padrão **MVC**, eliminando anti-patterns sem quebrar o comportamento existente.

A skill funciona em qualquer stack (Python/Flask, Node.js/Express, etc.). Você detecta a tecnologia
em tempo de execução e adapta as transformações ao contexto — um monolito plano e um projeto já
parcialmente organizado exigem tratamentos diferentes.

## Princípios

- **Não quebre o que funciona.** A aplicação deve continuar iniciando e respondendo os mesmos
  endpoints depois da refatoração. Comportamento observável é contrato.
- **O humano decide.** Você nunca modifica arquivos antes de apresentar o relatório de auditoria e
  receber confirmação explícita (Fase 2 → Fase 3).
- **Seja específico.** Todo finding tem arquivo e linha exatos. "Código ruim" não ajuda;
  "SQL concatenado em `models.py:47`" é acionável.
- **Escreva no estilo do projeto-alvo.** Mantenha as convenções do código existente. Use
  identificadores em inglês; mensagens ao usuário e logs em português.

## Contrato mínimo de qualidade

- Cada fase produz uma saída verificável e reutilizada pela fase seguinte.
- Se uma informação não puder ser confirmada, declare isso explicitamente em vez de inferir em
  silêncio.
- Não trate correção documental como correção funcional. Problemas reais de segurança ou
  comportamento exigem mudança real de código.
- Toda recomendação da Fase 2 deve apontar para uma transformação concreta do playbook.
- A Fase 3 só pode ser declarada concluída depois de validar boot, endpoints e mitigação dos
  findings críticos/high.

## Como usar os arquivos de referência

Carregue cada referência **no momento da fase correspondente** — não leia tudo de uma vez.

| Quando | Leia |
|---|---|
| Fase 1 — detectar stack e mapear arquitetura | `references/project-analysis.md` |
| Fase 2 — identificar anti-patterns | `references/anti-patterns.md` |
| Fase 2 — montar o relatório | `references/report-template.md` |
| Fase 3 — definir a estrutura MVC alvo | `references/architecture-guidelines.md` |
| Fase 3 — aplicar cada transformação | `references/refactoring-playbook.md` |

---

## Fase 1 — Análise

**Objetivo:** entender a stack, o domínio e a arquitetura atual antes de julgar qualquer coisa.

1. Leia `references/project-analysis.md` e aplique as heurísticas para detectar **linguagem**,
   **framework (com versão)**, **dependências**, **banco/tabelas**, **domínio** e **arquitetura atual**.
2. Faça um inventário dos arquivos-fonte (conte-os) e leia cada um para entender o fluxo real.
3. Preserve a lista de arquivos analisados e a contagem para cruzar depois com a auditoria.
4. Imprima o resumo **exatamente neste formato**:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão>
Dependencies:  <principais dependências>
Domain:        <domínio da aplicação em uma linha>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas detectadas>
================================
```

Em seguida, avance para a Fase 2 (não pare aqui).

---

## Fase 2 — Auditoria

**Objetivo:** cruzar o código contra o catálogo de anti-patterns e produzir um relatório acionável.

1. Leia `references/anti-patterns.md`. Para cada anti-pattern, procure no código os **sinais de
   detecção** descritos. Inclua a verificação de **APIs deprecated** (obsoletas → equivalente moderno).
2. Para cada ocorrência, registre: severidade, anti-pattern, **arquivo:linha exatos**, descrição,
   impacto e recomendação.
3. Leia `references/report-template.md` e gere o relatório seguindo o template, com os findings
   **ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW)**.
4. Salve o relatório em `reports/audit-project-<N>.md` na raiz do repositório (crie a pasta se
   preciso; use o número/nome do projeto correspondente).
5. Antes de salvar, valide internamente que o total do resumo bate com a lista de findings e que
   cada finding tem fonte e linha verificáveis.
6. **PARE e peça confirmação.** Não modifique nenhum arquivo antes do "y". Imprima:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Só avance para a Fase 3 após confirmação explícita do usuário. Se a resposta for "n", encerre
deixando apenas o relatório.

> A pausa é obrigatória: o humano precisa revisar os achados antes de qualquer mudança no código.

---

## Fase 3 — Refatoração

**Objetivo:** reestruturar para MVC eliminando os anti-patterns, sem quebrar a aplicação.

1. Leia `references/architecture-guidelines.md` para definir a **estrutura de camadas alvo** adequada
   à stack e ao nível de organização atual do projeto.
2. Leia `references/refactoring-playbook.md` e aplique a transformação correspondente a cada finding
   (cada um tem um padrão concreto antes/depois).
3. Adapte ao contexto:
   - **Monolito plano** → criar a estrutura de camadas do zero (config, models, controllers,
     views/routes, services, middlewares, entry point).
   - **Projeto parcialmente organizado** → respeitar o que já existe e corrigir o que está no lugar
     errado (ex.: mover regra de negócio das rotas para services/controllers), sem reescrever tudo.
4. Preserve contratos: mesmas rotas, mesmos formatos de request/response. Se a própria finalidade de
   uma rota for vulnerável (ex.: executar SQL arbitrário), preserve o caminho sem preservar a falha:
   desative a operação explicitamente com `410 Gone` e resposta segura.
5. Mapeie cada mudança aplicada para o finding correspondente, para não perder rastreabilidade.
6. **Valide o resultado** (obrigatório):
   - A aplicação **inicia sem erros** (rode o boot/comando de start da stack).
   - Os **endpoints originais respondem** (teste os principais; use o `api.http`/rotas conhecidas).
   - Não restam anti-patterns das categorias CRITICAL/HIGH detectadas.
7. Imprima o resumo final **neste formato**:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se a validação falhar, **corrija antes de declarar a fase concluída** — não entregue uma aplicação
quebrada.

---

## Critérios de aceite (verifique antes de finalizar)

- Fase 1 detectou a stack corretamente.
- Fase 2 encontrou ≥ 5 findings, incluindo ≥ 1 CRITICAL ou HIGH, ordenados por severidade, cada um
  com arquivo:linha; relatório salvo em `reports/`.
- Fase 2 pausou e pediu confirmação antes de tocar em qualquer arquivo.
- Fase 3 produziu estrutura MVC e a aplicação inicia + responde os endpoints originais.
