# Refactoring Playbook — transformações antes/depois (Fase 3)

Padrões concretos de transformação, um para cada anti-pattern do catálogo. Cada um mostra o código
**antes** e **depois**. Os exemplos cobrem Python e Node para reforçar que a skill é agnóstica — aplique
o equivalente na stack do projeto-alvo. Sempre preserve o comportamento (mesmas rotas e respostas).

## Índice

1. SQL Injection → query parametrizada / ORM
2. Hardcoded Secrets → configuração por ambiente
3. Weak Crypto → hashing forte
4. God Class → controllers + services + repositories
5. Business Logic in Controller → service layer
6. N+1 Queries → join / eager loading
7. Duplicated Validation → validador único
8. Global Mutable State → injeção de dependência
9. Broad Error Handling → handler centralizado
10. Deprecated API → equivalente moderno
11. Arbitrary Code / Query Execution → desativação segura ou allowlist

---

## 1. SQL Injection → query parametrizada / ORM

**Antes (Python):**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois (Python):**
```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
    (email, password_hash),
)
```

**Antes (Node):**
```js
db.get(`SELECT * FROM courses WHERE id = ${cid}`, cb);
```
**Depois (Node):**
```js
db.get("SELECT * FROM courses WHERE id = ?", [courseId], cb);
```

> Nunca concatene input em SQL. Use placeholders/bindings ou o ORM. Centralize no model/repository.

---

## 2. Hardcoded Secrets → configuração por ambiente

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
**Depois (`config/settings.py`):**
```python
import os

class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///loja.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```
**Node (`config/index.js`):**
```js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPass: process.env.DB_PASS,
  port: Number(process.env.PORT) || 3000,
};
```

> Mova todo segredo para variáveis de ambiente. Forneça um `.env.example` documentando as chaves.

---

## 3. Weak Crypto → hashing forte

**Antes:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, raw_password):
    self.password = generate_password_hash(raw_password)  # pbkdf2/scrypt

def check_password(self, raw_password):
    return check_password_hash(self.password, raw_password)
```
**Node:**
```js
const bcrypt = require("bcrypt");
const hash = await bcrypt.hash(rawPassword, 12);
const ok = await bcrypt.compare(rawPassword, user.passwordHash);
```

> Nunca armazene senha em texto puro nem com MD5/SHA1. Nunca retorne o hash em respostas da API.

---

## 4. God Class → controllers + services + repositories

**Antes (`AppManager.js`):** uma classe cria o banco, registra rotas, processa pagamento e auditoria.

**Depois:** separe por responsabilidade.
```js
// models/courseRepository.js  → acesso a dados
class CourseRepository {
  constructor(db) { this.db = db; }
  findActiveById(id) { /* SELECT ... WHERE id = ? AND active = 1 */ }
}

// services/checkoutService.js → regra de negócio
class CheckoutService {
  constructor(courseRepo, userRepo, paymentRepo) { /* ... */ }
  async checkout(input) { /* valida, cria usuário, processa pagamento, matricula */ }
}

// controllers/checkoutController.js → fluxo fino
async function checkout(req, res, next) {
  try {
    const result = await checkoutService.checkout(req.body);
    res.status(201).json(result);
  } catch (err) { next(err); }
}

// routes/checkoutRoutes.js
router.post("/api/checkout", checkout);
```

> Cada peça tem uma razão para mudar. O `app.js` vira composition root que monta tudo.

---

## 5. Business Logic in Controller → service layer

**Antes (Flask route):**
```python
@task_bp.route('/tasks/stats')
def task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    # ... cálculo de overdue, completion_rate, etc. tudo aqui
    return jsonify(stats)
```
**Depois:**
```python
# services/task_service.py
class TaskService:
    def __init__(self, task_repository):
        self.tasks = task_repository

    def get_stats(self):
        total = self.tasks.count()
        done = self.tasks.count_by_status('done')
        return {
            "total": total,
            "done": done,
            "completion_rate": percentage(done, total),
        }

# controllers/task_controller.py
def task_stats():
    return jsonify(task_service.get_stats()), 200
```

> O controller fica fino; a regra vira reutilizável e testável fora do HTTP.

---

## 6. N+1 Queries → join / eager loading

**Antes (Flask/SQLAlchemy):**
```python
for t in tasks:
    user = User.query.get(t.user_id)        # 1 query por task
    cat = Category.query.get(t.category_id) # + 1 query por task
```
**Depois:**
```python
from sqlalchemy.orm import joinedload

tasks = (Task.query
         .options(joinedload(Task.user), joinedload(Task.category))
         .all())
for t in tasks:
    user = t.user      # já carregado, sem query extra
    cat = t.category
```
**Antes (SQL cru, montagem de pedido):** loop com `SELECT` por item.
**Depois:** uma query com `JOIN` retornando itens + nome do produto de uma vez.

> Resolva relações na camada de dados, fora do loop.

---

## 7. Duplicated Validation → validador único

**Antes:** as mesmas regras em `criar_produto` e `atualizar_produto`.
**Depois:**
```python
# services/validators.py
VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

def validate_produto(data):
    if not data.get("nome") or len(data["nome"]) < 2:
        return "Nome inválido"
    if data.get("preco", 0) < 0:
        return "Preço não pode ser negativo"
    if data.get("categoria", "geral") not in VALID_CATEGORIES:
        return "Categoria inválida"
    return None  # ok

# controller
error = validate_produto(data)
if error:
    return jsonify({"erro": error}), 400
```

> Padrão "retorna erro, ou `None` quando válido". Uma fonte de verdade para a regra.

---

## 8. Global Mutable State → injeção de dependência

**Antes (`utils.js`):**
```js
let globalCache = {};
let totalRevenue = 0;
function logAndCache(key, data) { globalCache[key] = data; }
```
**Depois:**
```js
class CacheService {
  constructor() { this.store = new Map(); }
  set(key, value) { this.store.set(key, value); }
  get(key) { return this.store.get(key); }
}
// instanciado no composition root e injetado em quem precisa
```
**Python (conexão global → fábrica/escopo):**
```python
# antes: db_connection = None (singleton global mutável)
# depois: criar a conexão no app factory e injetar via contexto/repo
```

> Estado compartilhado vira dependência explícita, com ciclo de vida controlado.

---

## 9. Broad Error Handling → handler centralizado

**Antes:**
```python
try:
    ...
except:                      # engole tudo
    return jsonify({'error': 'Erro interno'}), 500
```
**Depois (Flask):**
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"erro": str(e)}), 400

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno"}), 500
```
**Express:**
```js
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
  req.log?.error(err);
  res.status(err.status || 500).json({ erro: err.publicMessage || "Erro interno" });
}
app.use(errorHandler);
```

> Captura específica + um handler global. Nada de `except:` nu; logue o erro real.

---

## 10. Deprecated API → equivalente moderno

**Antes:**
```python
created_at = datetime.utcnow()          # deprecated no Python 3.12+
user = User.query.get(user_id)          # legado no Flask-SQLAlchemy 3+
```
**Depois:**
```python
from datetime import datetime, UTC
created_at = datetime.now(UTC)
user = db.session.get(User, user_id)
```
**Node:**
```js
// antes
const buf = new Buffer(data);           // deprecated
// depois
const buf = Buffer.from(data);
```

> Consulte a tabela de APIs deprecated em `anti-patterns.md` e troque pelo equivalente atual.

---

## 11. Arbitrary Code / Query Execution → desativação segura ou allowlist

Quando a finalidade do endpoint é executar código ou SQL recebido do cliente, não preserve a
vulnerabilidade para manter compatibilidade. Preserve o caminho e desative a operação explicitamente.

**Antes (Flask):**
```python
@app.post("/admin/query")
def execute_query():
    cursor.execute(request.json["sql"])
    return {"sucesso": True}
```
**Depois (Flask):**
```python
@app.post("/admin/query")
def retired_query_endpoint():
    return {
        "erro": "Operação descontinuada por segurança",
        "sucesso": False,
    }, 410
```

> Se consultas administrativas forem indispensáveis, exponha operações predefinidas por allowlist,
> com autenticação/autorização e parâmetros tipados. Nunca aceite SQL ou código arbitrário no request.

---

## Itens menores (LOW), aplicar junto

- **Magic numbers:** extrair para constantes nomeadas (`REVENUE_TIER_HIGH = 10000`).
- **Poor naming:** renomear `u/e/cc/cid` para `user/email/card/courseId`.
- **`print`/`console.log`:** trocar por logger estruturado (`app.logger`, `pino`/`winston`).

## Checklist da transformação

Ao final, confirme: SQL parametrizado, segredos em config, senhas com hash forte, camadas separadas,
regra de negócio em services, sem N+1 nas listagens, validação única, sem estado global, erro
centralizado, APIs atualizadas — e a **aplicação inicia e responde os endpoints originais**.
