================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api (Projeto 3)
Stack:   Python 3 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0)
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secrets / Credentials
File: app.py:13 | services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` está literal no código, e o `NotificationService`
carrega host, usuário e senha SMTP em texto puro (`email_password = 'senha123'`). Tudo versionado.
Impact: Qualquer um com acesso ao repositório obtém os segredos; a SECRET_KEY fraca permite forjar
sessões/tokens e as credenciais SMTP permitem abuso da conta de e-mail.
Recommendation: Mover todos os segredos para variáveis de ambiente (`os.environ` / `python-dotenv`,
já presente). Centralizar em uma camada de config (`config.py`) lida no entry point; nunca commitar
valores reais — usar `.env.example`.

### [CRITICAL] Weak / Broken Cryptography
File: models/user.py:29 | models/user.py:32
Description: A senha é hasheada com MD5 (`hashlib.md5`) em `set_password`/`check_password`. MD5 é
quebrado e sem salt.
Impact: Vazamento do banco compromete todas as senhas imediatamente (rainbow tables, brute force).
Recommendation: Trocar por um algoritmo de hashing de senha forte com salt — `werkzeug.security`
(`generate_password_hash`/`check_password_hash`) ou `bcrypt`/`argon2`. Encapsular no model/serviço de
usuário sem alterar a interface `set_password`/`check_password`.

### [HIGH] Business Logic in Controller/Routes
File: routes/task_routes.py:11-63, 273-299 | routes/report_routes.py:12-101, 103-155
Description: Os handlers de rota concentram regra de negócio: cálculo de "overdue" repetido em 4
lugares, montagem manual de dicts, agregações de estatísticas (`stats`, `summary`, `user_report`) e
cálculos de produtividade — tudo dentro das views, sem camada de serviço.
Impact: Lógica não reutilizável nem testável em isolamento; viola o "controller fino" do MVC; regras
divergem entre endpoints (ex.: cada rota recalcula "overdue" à mão).
Recommendation: Extrair para uma camada `services/` (`TaskService`, `ReportService`, `UserService`).
Controller só valida entrada, chama o service e retorna resposta. Mover a regra "overdue" para o
model `Task.is_overdue()` (já existe) e reutilizá-la.

### [HIGH] Missing Layer Separation (sem Service/Repository real)
File: routes/*.py | services/ (apenas notification_service.py)
Description: A separação de camadas é nominal. As rotas falam direto com `db.session` e `Model.query`;
não há camada de serviço de domínio nem repositório. `services/` contém só notificação — e o
`NotificationService` nem é referenciado pelas rotas.
Impact: Mudança de schema/fonte de dados quebra N pontos; impossível testar regra de negócio sem
subir Flask + banco; acoplamento direto controller→ORM em toda a aplicação.
Recommendation: Introduzir camada de serviço (regra de negócio) e, opcionalmente, repositórios por
entidade que isolam o acesso a dados. Controllers passam a depender dos serviços, não do ORM
diretamente. Seguir o fluxo do guia: Rota → Controller fino → Service → acesso a dados → Banco.

### [HIGH] Global Mutable State / No Dependency Injection
File: services/notification_service.py:5-10, 31-36
Description: `NotificationService` guarda notificações numa lista em memória (`self.notifications`)
usada como armazenamento de estado, e instancia suas dependências/credenciais hardcoded dentro da
própria classe, sem injeção. Não há composition root.
Impact: Estado em memória se perde a cada restart e não escala entre processos; dependências fixas
impedem testes (não dá para mockar o SMTP); configuração espalhada.
Recommendation: Injetar config/cliente de e-mail via construtor; persistir notificações no banco (ou
fila) em vez de lista em memória; registrar dependências num único lugar (factory `create_app`).

### [MEDIUM] N+1 Queries
File: routes/task_routes.py:41-57 | routes/report_routes.py:53-68, 157-165
Description: `get_tasks` faz `User.query.get` e `Category.query.get` dentro do loop de tasks; o
relatório resumo itera usuários disparando `Task.query.filter_by(user_id=...)` por usuário; a
listagem de categorias roda um `count()` por categoria.
Impact: Número de queries cresce linearmente com o volume; performance degrada conforme a base cresce.
Recommendation: Usar eager loading (`joinedload`/`selectinload`) das relações `user`/`category` (já
mapeadas no model) e agregações no banco (`group_by`/`count`) em vez de loops em Python.

### [MEDIUM] Duplicated / Missing Validation
File: routes/task_routes.py:96-114 vs 166-184 | routes/user_routes.py:61 vs 106 | utils/helpers.py:57-108
Description: As regras de validação de título/status/prioridade estão duplicadas entre `create_task` e
`update_task`; o regex de e-mail aparece duplicado em criar/atualizar usuário; e `process_task_data`
em `helpers.py` é um validador paralelo que nunca é usado.
Impact: Regras divergem com o tempo; manutenção em N lugares; dados inválidos entram dependendo do
caminho.
Recommendation: Centralizar validação em schemas (marshmallow já está nas dependências) ou em
validadores no service, reutilizados por create e update. Remover o `process_task_data` morto.

### [MEDIUM] Missing / Broad Error Handling
File: routes/task_routes.py:62, 236 | routes/user_routes.py:130, 149 | routes/report_routes.py:186-188, 207-208, 221-222
Description: Vários `try/except:` nus engolem qualquer exceção e retornam um 500 genérico, sem log
estruturado nem distinção de causa.
Impact: Mascara bugs reais (ex.: erro de validação vira "Erro interno"), dificulta diagnóstico e
produz respostas inconsistentes.
Recommendation: Capturar exceções específicas, logar com logging estruturado e centralizar o
tratamento via error handlers do Flask (`@app.errorhandler`). Nada de `except:` nu.

### [MEDIUM] Sensitive Data Exposure in Response
File: models/user.py:16-25 | routes/user_routes.py:185-211
Description: `User.to_dict()` inclui o campo `password` (hash) na serialização; ele é devolvido em
`GET /users/<id>`, `POST /users` e na resposta de `/login`. O token de login é um placeholder fixo
(`'fake-jwt-token-' + id`).
Impact: A própria API vaza o hash de senha dos usuários; o "token" não oferece segurança real.
Recommendation: Remover `password` do DTO de saída (criar um `UserResource` sem campos sensíveis).
Não retornar hash em nenhuma resposta; substituir o token fake por JWT real quando autenticação for
implementada.

### [MEDIUM] Deprecated APIs
File: models/*.py (default=datetime.utcnow) | routes/*.py (datetime.utcnow()) | Model.query.get em routes/*.py
Description: Uso disseminado de `datetime.utcnow()` (deprecated no Python 3.12+, naive) e do padrão
legado `Model.query.get(id)` (Flask-SQLAlchemy 3+).
Impact: Quebra futura ao atualizar runtime/lib; datetimes naive geram bugs de timezone.
Recommendation: Migrar para `datetime.now(datetime.UTC)` (timezone-aware) e `db.session.get(Model, id)`.

### [LOW] Magic Numbers
File: routes/task_routes.py:96-100, 113 | routes/user_routes.py:64-65, 115 | utils/helpers.py:110-116
Description: Limites de regra (título 3/200, prioridade 1-5, senha mínima 4) aparecem como números
soltos espalhados, apesar de já existirem constantes nomeadas em `helpers.py` que não são usadas.
Impact: Regra de negócio ilegível e difícil de manter consistente.
Recommendation: Usar as constantes nomeadas (`MIN_TITLE_LENGTH`, `MAX_TITLE_LENGTH`,
`MIN_PASSWORD_LENGTH`, etc.) a partir de um único módulo de constantes/config.

### [LOW] Poor Naming
File: routes/task_routes.py:16 | routes/report_routes.py:33, 55-61 | models/category.py:14 | seed.py
Description: Variáveis de uma letra sem intenção: `t`, `u`, `c`, `cat`, `p`, `td`, `n`, `d`, `s`.
Impact: Baixa legibilidade; contraria a convenção de nomes descritivos do guia de estilo.
Recommendation: Renomear para nomes por extenso (`task`, `user`, `category`, `priority`,
`task_data`), conforme o guia de estilo do projeto.

### [LOW] print() as Logging
File: routes/task_routes.py:149, 153, 219, 234 | routes/user_routes.py:83, 89, 147 | services/notification_service.py:21, 24 | utils/helpers.py:39-41
Description: Eventos e erros são reportados com `print(...)`, sem níveis nem estrutura.
Impact: Sem observabilidade real; polui stdout; impossível filtrar por severidade em produção.
Recommendation: Usar o módulo `logging` com logger nomeado e níveis (info/warning/error) e mensagens
estruturadas em português.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
