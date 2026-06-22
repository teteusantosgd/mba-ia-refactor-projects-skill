# Anti-patterns — catálogo de detecção (Fase 2)

Catálogo de anti-patterns com **sinais de detecção acionáveis** e severidade. Para cada um, procure os
sinais no código e registre arquivo:linha exatos. A severidade segue a escala do desafio (baseada em
MVC e SOLID); use o playbook (`refactoring-playbook.md`) para corrigir cada caso.

## Escala de severidade

| Nível | Critério |
|---|---|
| **CRITICAL** | Falha grave de arquitetura/segurança: expõe dados sensíveis, permite ataque, ou viola completamente a separação de responsabilidades. |
| **HIGH** | Forte violação de MVC/SOLID que dificulta muito manutenção e testes (regra de negócio no controller, acoplamento sem DI, estado global mutável). |
| **MEDIUM** | Padronização, duplicação ou performance moderada (N+1, validação ausente/duplicada, middleware inadequado). |
| **LOW** | Legibilidade, nomenclatura ruim, magic numbers. |

---

## Índice

1. SQL Injection — **CRITICAL**
2. Hardcoded Secrets / Credentials — **CRITICAL**
3. Weak / Broken Cryptography — **CRITICAL**
4. Arbitrary Code / Query Execution — **CRITICAL**
5. God Class / God File — **HIGH**
6. Business Logic in Controller/Routes — **HIGH**
7. Global Mutable State / No Dependency Injection — **HIGH**
8. Missing Layer Separation (sem Model/Service real) — **HIGH**
9. N+1 Queries — **MEDIUM**
10. Duplicated / Missing Validation — **MEDIUM**
11. Missing / Broad Error Handling — **MEDIUM**
12. Sensitive Data Exposure in Response — **MEDIUM**
13. Magic Numbers — **LOW**
14. Poor Naming — **LOW**
15. `print()` / `console.log` as Logging — **LOW**
16. Deprecated APIs — **severidade conforme o caso**

---

## CRITICAL

### 1. SQL Injection
- **Sinais:** queries montadas por **concatenação de string** ou interpolação com entrada do usuário
  (`"... WHERE id = " + str(id)`, `` `... WHERE email = '${email}'` ``, f-strings em SQL). Ausência de
  parâmetros (`?`, `%s`, bindings).
- **Impacto:** ler/alterar/apagar o banco, burlar autenticação.

### 2. Hardcoded Secrets / Credentials
- **Sinais:** `SECRET_KEY`, senhas de banco, tokens, chaves de API/pagamento literais no código
  (`pk_live_...`, `password = "..."`, credenciais SMTP). Pior ainda se versionado.
- **Impacto:** comprometimento de segredos; com chave de pagamento/produção, dano financeiro direto.

### 3. Weak / Broken Cryptography
- **Sinais:** senha em **texto puro**; hashing com `md5`/`sha1`; "cripto" caseira (ex.: base64
  truncado). Comparação de senha sem hash.
- **Impacto:** vazamento do banco compromete todas as senhas.

### 4. Arbitrary Code / Query Execution
- **Sinais:** endpoint que executa SQL recebido no request, `eval()`/`exec()` sobre input,
  `/admin/query` sem autenticação.
- **Impacto:** execução arbitrária — equivale a entregar o servidor.

## HIGH

### 5. God Class / God File
- **Sinais:** uma classe/arquivo que cria o banco **e** registra rotas **e** processa regra de
  negócio **e** loga auditoria. Arquivos com centenas de linhas e múltiplas responsabilidades.
- **Impacto:** nada testável em isolamento; qualquer mudança afeta tudo.

### 6. Business Logic in Controller/Routes
- **Sinais:** cálculos, montagem manual de dicts, regras de domínio e orquestração de
  notificações **dentro** do handler de rota/controller. Services inexistentes ou vazios.
- **Impacto:** lógica não reutilizável nem testável; viola o "controller fino" do MVC.

### 7. Global Mutable State / No Dependency Injection
- **Sinais:** variáveis globais mutáveis (`globalCache = {}`, conexão singleton global,
  `totalRevenue`), dependências instanciadas dentro das funções em vez de injetadas.
- **Impacto:** estado compartilhado entre requests, vazamentos, concorrência imprevisível.

### 8. Missing Layer Separation (sem Model/Service real)
- **Sinais:** "models" que são só funções com SQL cru; mapeamento manual de linhas para dict repetido
  em todo lugar; ausência de abstração de dados/serviço.
- **Impacto:** mudança de schema quebra N pontos; impossível trocar a fonte de dados.

## MEDIUM

### 9. N+1 Queries
- **Sinais:** query dentro de loop; para cada registro, novas queries para buscar relações
  (`for item: SELECT ... WHERE id = item.x`). Contadores manuais de callbacks aninhados (Node).
- **Impacto:** número de queries cresce linearmente; performance degrada com o volume.

### 10. Duplicated / Missing Validation
- **Sinais:** mesmas regras de validação copiadas em create e update; ou ausência de validação nas
  rotas (campos obrigatórios não checados).
- **Impacto:** regras divergem com o tempo; dados inválidos entram no sistema.

### 11. Missing / Broad Error Handling
- **Sinais:** `except:` nu / `catch (e) {}` vazio; erros engolidos; ausência de handler centralizado;
  vazamento de stack trace ao cliente.
- **Impacto:** mascara bugs, dificulta diagnóstico, respostas inconsistentes.

### 12. Sensitive Data Exposure in Response
- **Sinais:** `to_dict()`/serializer que inclui `password`/hash; segredos no `/health`; dados de
  cartão logados.
- **Impacto:** vazamento de dados sensíveis pela própria API.

## LOW

### 13. Magic Numbers
- **Sinais:** números/limiares soltos em regras (`if faturamento > 10000`), sem constante nomeada.
- **Impacto:** regra de negócio ilegível e difícil de manter.

### 14. Poor Naming
- **Sinais:** variáveis crípticas (`u`, `e`, `cc`, `cid`), nomes que não revelam intenção.
- **Impacto:** baixa legibilidade e manutenção custosa.

### 15. `print()` / `console.log` as Logging
- **Sinais:** `print(...)`/`console.log(...)` para eventos e erros, sem níveis nem estrutura.
- **Impacto:** sem observabilidade real; polui stdout.

---

## 16. Deprecated APIs (detecção obrigatória)

Identifique uso de APIs obsoletas e **recomende o equivalente moderno**. A severidade depende do
impacto (segurança/quebra futura = mais alta; estilo = LOW).

| API deprecated / legada | Stack | Equivalente moderno recomendado |
|---|---|---|
| `datetime.utcnow()` | Python 3.12+ | `datetime.now(datetime.UTC)` (timezone-aware) |
| `Model.query.get(id)` | Flask-SQLAlchemy 3+ | `db.session.get(Model, id)` |
| `@app.before_first_request` | Flask 2.3+ | inicialização explícita / factory |
| `werkzeug url_encode/url_decode` | Werkzeug 2.3+ | `urllib.parse` |
| `new Buffer(...)` | Node | `Buffer.from(...)` |
| `crypto` com `createCipher` | Node | `createCipheriv` |
| `request` (npm) | Node | `fetch` nativo / `axios` / `undici` |
| `body-parser` separado | Express 4.16+ | `express.json()` / `express.urlencoded()` |
| `md5`/`sha1` para senha | qualquer | `bcrypt` / `argon2` / `scrypt` |

> Procure também por avisos do tipo `DeprecationWarning` no boot da aplicação — eles apontam o caminho.
> Não classifique automaticamente APIs suportadas como deprecated. `.verbose()` do `sqlite3` e
> callbacks de I/O podem ser inadequados ou legados, mas não são APIs formalmente obsoletas.

## Cobertura mínima

O catálogo cobre as 4 severidades. Em qualquer projeto, garanta **≥ 5 findings**, com **≥ 1 CRITICAL
ou HIGH**, e rode a checagem de **APIs deprecated** sempre que aplicável.
