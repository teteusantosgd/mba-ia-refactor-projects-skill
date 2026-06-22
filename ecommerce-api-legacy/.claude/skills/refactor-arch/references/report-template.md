# Report Template — relatório de auditoria (Fase 2)

Formato padronizado do relatório da Fase 2. Use **exatamente** esta estrutura ao imprimir o resultado
e ao salvar em `reports/audit-project-<N>.md`. Os findings devem vir **ordenados por severidade**
(CRITICAL → HIGH → MEDIUM → LOW) e cada um precisa de **arquivo:linha exatos**.

## Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern>
File: <arquivo:linha(s)>
Description: <o que está errado, objetivamente>
Impact: <consequência prática>
Recommendation: <como corrigir — aponta para o playbook>

### [HIGH] <Nome do anti-pattern>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Nome do anti-pattern>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <Nome do anti-pattern>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

- **Ordenação:** sempre CRITICAL primeiro, LOW por último. Dentro da mesma severidade, agrupe por
  arquivo quando fizer sentido.
- **File:** use caminho relativo ao projeto + linha ou intervalo (`models.py:47-50`,
  `src/AppManager.js:1-141`). Se o mesmo problema aparece em vários pontos, liste os principais.
- **Description:** uma a duas frases, factuais. Sem floreio.
- **Impact:** por que isso importa na prática (segurança, performance, manutenção).
- **Recommendation:** a transformação correspondente do `refactoring-playbook.md`.
- **Summary:** os números devem bater com a contagem real de findings listados.
- **APIs deprecated:** quando houver, inclua como findings normais, citando o equivalente moderno na
  Recommendation.
- **Consistency check:** antes de salvar, confirme que o total do resumo = número real de findings e
  que cada finding citado no relatório tem evidência verificável no código.

## Exemplo (trecho)

```
### [CRITICAL] SQL Injection
File: models.py:109-111
Description: A query de login concatena email e senha direto no WHERE, sem parametrização.
Impact: Permite burlar a autenticação e ler/alterar o banco.
Recommendation: Usar queries parametrizadas (placeholders) ou ORM na camada de dados.
```

> O relatório é o ponto de decisão do humano. Ele deve ser legível por si só: alguém que não viu o
> código entende o que há de errado, onde, e o que será feito.
