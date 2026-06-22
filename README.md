# Refatoração Arquitetural Automatizada — Skill `refactor-arch`

## Análise Manual

### code-smells-project (Python/Flask — E-commerce API)

#### [CRITICAL] SQL Injection em várias queries diferentes

- **Arquivos/Referências:** `models.py:28`, `models.py:47-50`, `models.py:109-111`, `models.py:289-297` (entre outras)
- **Descrição:** As queries são montadas por concatenação de strings com a entrada do usuário, permitindo ler, alterar ou apagar o banco e burlar o login. O caso mais grave é o `login_usuario`, que concatena email e senha direto no `WHERE`.

#### [MEDIUM] Query N+1 ao montar pedidos

- **Arquivos/Referências:** `models.py:187-199` (`get_pedidos_usuario`) e `models.py:219-231` (`get_todos_pedidos`)
- **Descrição:** Para cada pedido é executada uma query de itens e, dentro do loop de itens, mais uma query por produto para buscar o nome, fazendo o número de queries crescer linearmente com pedidos e itens.

#### [MEDIUM] Validação duplicada entre criar e atualizar produto

- **Arquivos/Referências:** `controllers.py:28-54` vs `controllers.py:72-90`
- **Descrição:** As mesmas regras (campos obrigatórios, preço/estoque não negativos, tamanho do nome) estão duplicadas nas funções atualizar_produto e criar_produto. Se algum regra mudar eventualmente, pode acontecer de
apenas 1 método ser atualizado, e outro não.

#### [LOW] Magic numbers nas faixas de desconto

- **Arquivos/Referências:** `models.py:257-262`
- **Descrição:** Os limites `10000`, `5000`, `1000` e os percentuais de desconto estão soltos no cálculo do relatório, sem nome, dificultando a leitura e a manutenção.

#### [LOW] `print()` usado como logging

- **Arquivos/Referências:** `controllers.py:8`, `controllers.py:57`, `controllers.py:208-210` (e outros)
- **Descrição:** Eventos e erros são reportados com `print()`, inclusive "envio de e-mail/SMS" simulado, sem níveis nem estrutura, poluindo o stdout.

### ecommerce-api-legacy (Node.js/Express — LMS API com checkout)

"Frankenstein LMS": uma única classe `AppManager` concentra banco, rotas, regra de negócio,
pagamento e auditoria. Há também estado global mutável e segredos hardcoded.

#### [HIGH] God Class `AppManager`

- **Arquivos/Referências:** `src/AppManager.js:1-141`
- **Descrição:** Uma classe faz tudo: cria/popula o banco (`initDb`), registra todas as rotas (`setupRoutes`), processa pagamento, grava matrícula/pagamento e escreve logs de auditoria — tudo no mesmo arquivo, sem qualquer separação de responsabilidades.

#### [MEDIUM] Relatório financeiro com N+1 e contadores de callback

- **Arquivos/Referências:** `src/AppManager.js:80-129`
- **Descrição:** O endpoint percorre cursos e, para cada um, busca matrículas; para cada matrícula, busca usuário e pagamento em queries separadas, controlando o término com contadores manuais aninhados — ineficiente (N+1) e extremamente frágil.

#### [MEDIUM] Delete sem integridade referencial

- **Arquivos/Referências:** `src/AppManager.js:131-137`
- **Descrição:** Ao deletar um usuário, matrículas e pagamentos relacionados continuam no banco — o próprio retorno admite que "ficaram sujos no banco" — gerando registros órfãos e inconsistência de dados.

#### [LOW] Nomes de variáveis crípticos

- **Arquivos/Referências:** `src/AppManager.js:29-33`
- **Descrição:** O corpo do checkout usa `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, id do curso e cartão, prejudicando a legibilidade e a manutenção.

#### [LOW] `console.log()` usado como logging

- **Arquivos/Referências:** `src/utils.js:13`, `src/AppManager.js:45`, `src/AppManager.js:57`, `src/app.js:13`
- **Descrição:** Eventos, cache e auditoria são escritos com `console.log()`, sem níveis nem estrutura. Um dos logs inclui número completo de cartão e chave de pagamento, misturando observabilidade precária com exposição de dados sensíveis.

### task-manager-api (Python/Flask — Task Manager API)

Projeto parcialmente organizado: já existem pastas `models/`, `routes/`, `services/` e `utils/`. Mas
a separação é superficial — as rotas concentram a regra de negócio e há código duplicado e morto.

#### [HIGH] Regra de negócio concentrada nas rotas (camadas apenas nominais)

- **Arquivos/Referências:** `routes/task_routes.py:11-63`, `routes/task_routes.py:273-299`, `routes/report_routes.py:13-101`
- **Descrição:** As rotas montam dicts manualmente, calculam `overdue`, geram estatísticas e relatórios inteiros, enquanto a pasta `services/` tem só notificação — a estrutura aparenta ter camadas, mas a lógica está toda no roteamento, sem controllers/services para tasks, users ou reports.

#### [MEDIUM] Query N+1 ao listar tasks

- **Arquivos/Referências:** `routes/task_routes.py:41-57`
- **Descrição:** Dentro do loop de tasks, cada iteração faz `User.query.get` e `Category.query.get` para resolver os nomes do usuário e da categoria — uma query por task para cada relação, que degrada com o volume.

#### [MEDIUM] Lógica de "overdue" duplicada e método do model ignorado

- **Arquivos/Referências:** `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-37`
- **Descrição:** A mesma verificação de atraso (data passada + status diferente de done/cancelled) está reescrita em 4+ lugares, embora já exista `Task.is_overdue()` no model, ignorando a abstração existente.

#### [MEDIUM] `except:` nu engolindo erros

- **Arquivos/Referências:** `routes/task_routes.py:62`, `routes/task_routes.py:236`
- **Descrição:** Blocos `except:` sem tipo capturam qualquer exceção e retornam um erro genérico, mascarando bugs e dificultando o diagnóstico.

#### [LOW] Nomes de variáveis crípticos

- **Arquivos/Referências:** `routes/task_routes.py:16`, `routes/report_routes.py:33`, `routes/report_routes.py:55-61`, `models/category.py:14`, `seed.py:78-90`
- **Descrição:** Variáveis de uma letra como `t`, `u`, `c`, `p`, `td`, `n`, `d` e `s` escondem a intenção do código e dificultam manutenção e revisão.

#### [LOW] `print()` usado como logging

- **Arquivos/Referências:** `routes/task_routes.py:149`, `routes/task_routes.py:153`, `routes/task_routes.py:219`, `routes/user_routes.py:83`, `services/notification_service.py:21-24`
- **Descrição:** Eventos e erros são enviados diretamente para stdout com `print()`, sem níveis, contexto estruturado ou integração com a configuração de logging da aplicação.

## Construção da Skill

### Decisões de design

A ideia foi deixar o `SKILL.md` o mais enxuto possível (menos de 500 linhas) e usá-lo só como fio
condutor das 3 fases. Ele não carrega o conhecimento de domínio: cada fase aponta para o arquivo de
referência certo na hora certa, então o modelo lê só o que importa naquele momento
(*progressive disclosure*). O resto do conteúdo ficou em 5 arquivos Markdown, um para cada área que o
desafio pede:


| Arquivo                      | Área                                                    | Usado na |
| ---------------------------- | ------------------------------------------------------- | -------- |
| `project-analysis.md`        | Como detectar linguagem, framework, banco e arquitetura | Fase 1   |
| `anti-patterns.md`           | Catálogo de anti-patterns + APIs deprecated             | Fase 2   |
| `report-template.md`         | Formato padronizado do relatório                        | Fase 2   |
| `architecture-guidelines.md` | Regras do MVC alvo e responsabilidades de cada camada   | Fase 3   |
| `refactoring-playbook.md`    | Transformações concretas com exemplos antes/depois      | Fase 3   |


Tem duas regras que eu não abro mão em nenhuma execução: a Fase 2 sempre para e pede confirmação antes
de mexer em qualquer arquivo, e a Fase 3 só se dá por concluída depois de checar que a aplicação sobe e
os endpoints respondem.

### Catálogo de anti-patterns

O catálogo tem **16 anti-patterns**, cada um com um sinal de detecção que dá para procurar de verdade.
Em vez de "código ruim", a regra é algo como "query SQL concatenada com input" — concreto o suficiente
para o modelo achar no código. Eles cobrem as 4 severidades:


| Severidade   | Anti-patterns                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------- |
| **CRITICAL** | SQL Injection · Hardcoded Secrets · Weak/Broken Crypto · Arbitrary Code/Query Execution            |
| **HIGH**     | God Class · Business Logic in Controller · Global Mutable State / No DI · Missing Layer Separation |
| **MEDIUM**   | N+1 Queries · Duplicated/Missing Validation · Broad Error Handling · Sensitive Data Exposure       |
| **LOW**      | Magic Numbers · Poor Naming · `print()`/`console.log` as Logging                                   |


A lista saiu direto da Análise Manual: peguei cada problema real dos 3 projetos e transformei num
padrão genérico. Também separei uma seção só para **APIs deprecated** (`datetime.utcnow()`,
`Model.query.get()`, `new Buffer()`...), com o substituto moderno de cada uma e distinguindo APIs
formalmente obsoletas de padrões apenas legados.
Além de ser pedido do desafio, é o tipo de coisa que passa batido.

### Funcionar em qualquer stack

Para não amarrar a skill numa stack, ela descobre a tecnologia na hora de rodar: começa pelos
**arquivos de manifesto** (`requirements.txt`, `package.json`...) e confirma olhando os imports do
código. Os arquivos de referência falam de princípios, não de uma linguagem específica, e os exemplos
do playbook cobrem Python **e** Node. As regras de arquitetura são as mesmas; só mudam para as
convenções de cada framework (Blueprints no Flask, Router no Express). Testei nas 3 stacks do desafio,
incluindo o projeto que já vinha meio organizado — nesse caso a skill arruma o que está no lugar errado
em vez de reescrever tudo.

### Desafios encontrados

- **Não acoplar a skill a um projeto.** No começo eu tinha descrito os arquivos exatos do
`code-smells-project`, o que obviamente só funcionaria nele. Troquei por sinais de detecção
genéricos, e fui validando conforme copiava a skill para os outros 2 projetos.
- **Lidar com projetos em níveis diferentes de organização.** O `task-manager-api` já tinha pastas de
camadas, mas era só na aparência. Acabei colocando instruções claras para a skill diferenciar
separação real de separação só no nome, e decidir o que fazer: criar as camadas do zero ou só mover a
regra de negócio para o lugar certo.
- **Manter o `SKILL.md` enxuto.** Jogar o conhecimento de domínio para os arquivos de referência e
carregar cada um por fase foi o que segurou o prompt principal curto e a execução focada.

## Resultados

### Evidências da Fase 1

Os resumos abaixo registram a detecção de stack, domínio e arquitetura feita antes de cada auditoria:

```text
Projeto 1 — code-smells-project
Language:      Python 3
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolito plano em 4 arquivos, com rotas, regras e SQL misturados
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido

Projeto 2 — ecommerce-api-legacy
Language:      JavaScript / Node.js
Framework:     Express 4.18.2
Dependencies:  express, sqlite3
Domain:        LMS API (cursos, checkout, matrículas e pagamentos)
Architecture:  God Class centralizando banco, rotas, negócio e auditoria
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs

Projeto 3 — task-manager-api
Language:      Python 3
Framework:     Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors, marshmallow, requests, python-dotenv
Domain:        Task Manager API (usuários, categorias, tasks e relatórios)
Architecture:  Parcialmente organizada, mas com separação de camadas apenas nominal
Source files:  15 files analyzed
DB tables:     users, categories, tasks
```

### Resumo dos relatórios de auditoria

Os relatórios completos estão em [reports/](reports/). Os números de findings por severidade:


| Projeto              | CRITICAL | HIGH | MEDIUM | LOW | Total  |
| -------------------- | -------- | ---- | ------ | --- | ------ |
| code-smells-project  | 4        | 3    | 4      | 3   | **14** |
| ecommerce-api-legacy | 3        | 4    | 3      | 3   | **13** |
| task-manager-api     | 2        | 3    | 5      | 3   | **13** |


Os 3 passaram nos critérios de aceite: pelo menos 5 findings e pelo menos 1 CRITICAL ou HIGH em cada.

### Comparação antes/depois

**code-smells-project** — de monolito plano para MVC em camadas:

```
ANTES                                  DEPOIS
app.py          (rotas + admin)        src/
controllers.py  (validação+regra)      ├── config/settings.py
models.py       (SQL cru concatenado)  ├── database/connection.py
database.py     (conexão global)       ├── models/        (repositories, SQL parametrizado)
                                       ├── services/      (regra + validators + notification)
                                       ├── controllers/   (handlers finos por domínio)
                                       ├── views/routes.py
                                       ├── middlewares/error_handler.py
                                       ├── container.py
                                       └── app.py         (entry + composition root)
```

**ecommerce-api-legacy** — de God Class para camadas com injeção de dependência:

```
ANTES                                  DEPOIS
src/                                   src/
├── app.js                             ├── config/index.js
├── AppManager.js (db+rotas+           ├── db/index.js        (cliente sqlite com async/await)
│   pagamento+auditoria)               ├── models/            (repositories por entidade)
└── utils.js     (segredos +           ├── services/          (checkout, report, user, password, cache)
    estado global + badCrypto)         ├── controllers/
                                       ├── routes/index.js
                                       ├── middlewares/errorHandler.js
                                       ├── errors/AppError.js
                                       ├── utils/logger.js
                                       └── app.js             (composition root)
```

**task-manager-api** — de camadas só no nome para camadas de verdade:

```
ANTES                                  DEPOIS (adiciona)
app.py · database.py · seed.py         config/settings.py
models/{task,user,category}.py         controllers/   (task, user, category, report, auth)
routes/  (regra de negócio dentro)     services/      (task, user, category, report, auth, notification)
services/notification (nem usado)      repositories/  (task, user, category)
utils/helpers (validador morto)        serializers.py (DTOs sem campos sensíveis)
                                       middlewares/error_handler.py
                                       shared/        (clock, constants, errors)
                                       container.py
                                       routes/  agora só roteamento
```

### Checklist de validação

As Fases 1 e 2 eu conferi nos próprios relatórios; na Fase 3 subi cada app e testei os endpoints.


| Item                                          | P1  | P2  | P3  |
| --------------------------------------------- | --- | --- | --- |
| **Fase 1** — Linguagem detectada              | ✅   | ✅   | ✅   |
| **Fase 1** — Framework detectado              | ✅   | ✅   | ✅   |
| **Fase 1** — Domínio descrito                 | ✅   | ✅   | ✅   |
| **Fase 1** — Nº de arquivos condiz            | ✅   | ✅   | ✅   |
| **Fase 2** — Relatório segue o template       | ✅   | ✅   | ✅   |
| **Fase 2** — Cada finding com arquivo e linha | ✅   | ✅   | ✅   |
| **Fase 2** — Ordenado por severidade          | ✅   | ✅   | ✅   |
| **Fase 2** — Mínimo de 5 findings             | ✅   | ✅   | ✅   |
| **Fase 2** — APIs deprecated verificadas      | ✅   | ✅ (N/A) | ✅   |
| **Fase 2** — Pausa e pede confirmação         | ✅   | ✅   | ✅   |
| **Fase 3** — Estrutura segue MVC              | ✅   | ✅   | ✅   |
| **Fase 3** — Config sem segredos hardcoded    | ✅   | ✅   | ✅   |
| **Fase 3** — Models abstraem os dados         | ✅   | ✅   | ✅   |
| **Fase 3** — Views/Routes separadas           | ✅   | ✅   | ✅   |
| **Fase 3** — Controllers concentram o fluxo   | ✅   | ✅   | ✅   |
| **Fase 3** — Error handling centralizado      | ✅   | ✅   | ✅   |
| **Fase 3** — Entry point claro                | ✅   | ✅   | ✅   |
| **Fase 3** — Aplicação inicia sem erros       | ✅   | ✅   | ✅   |
| **Fase 3** — Endpoints originais respondem    | ✅   | ✅   | ✅   |


### Logs / evidências

Subi os 3 apps refatorados, e testei os endpoints principais. Seguem os logs reais das execuçoes:

**code-smells-project** (Flask) — boot + endpoints

```
INFO __main__ Servidor iniciado em http://localhost:5055
 * Running on http://127.0.0.1:5055
INFO src.services.product_service Produtos listados
127.0.0.1 - - "GET /produtos HTTP/1.1" 200 -
INFO src.services.user_service Login bem-sucedido
127.0.0.1 - - "POST /login HTTP/1.1" 200 -
INFO src.services.notification_service Notificação de pedido criado enviada
127.0.0.1 - - "POST /pedidos HTTP/1.1" 201 -
127.0.0.1 - - "GET /relatorios/vendas HTTP/1.1" 200 -

# POST /pedidos → {"dados":{"pedido_id":1,"total":6179.79},"sucesso":true}
# GET /usuarios → não retorna mais o campo "senha"
```



**ecommerce-api-legacy** (Express) — boot + checkout (sem vazar cartão)

```
{"level":"info","event":"server_started","port":3000,"message":"Servidor rodando na porta 3000..."}
{"level":"info","event":"checkout_payment_processed","userId":2,"courseId":2,"status":"PAID"}
{"level":"info","event":"checkout_payment_processed","userId":3,"courseId":1,"status":"DENIED"}

# POST /api/checkout (cartão 4111...) → 200 {"msg":"Sucesso","enrollment_id":2}
# POST /api/checkout (cartão 5111...) → 400 "Pagamento recusado"
# DELETE /api/users/1 → 200 "Usuário e dados relacionados removidos com sucesso."
# o log NÃO contém número de cartão nem pk_live (vazamento corrigido)
```



**task-manager-api** (Flask + SQLAlchemy) — seed + boot + endpoints

```
# python seed.py → 3 usuários, 4 categorias, 10 tasks
 * Running on http://127.0.0.1:5056
127.0.0.1 - - "GET /tasks/stats HTTP/1.1" 200 -
127.0.0.1 - - "GET /tasks HTTP/1.1" 200 -
127.0.0.1 - - "GET /users HTTP/1.1" 200 -
127.0.0.1 - - "POST /login HTTP/1.1" 200 -
127.0.0.1 - - "GET /reports/summary HTTP/1.1" 200 -

# GET /tasks/stats → {"total":10,"done":1,"overdue":2,"completion_rate":10.0,...}
# GET /users → não retorna mais o campo "password"
# POST /login → retorna JWT HS256 assinado, com expiração configurável
```



### Comportamento em stacks diferentes

- **code-smells-project (monolito plano):** o caso mais "do zero". A skill criou toda a estrutura
`src/` e separou o que estava em 4 arquivos. O ponto mais sensível foi a segurança — SQL Injection
espalhado e senhas em texto puro —, resolvido junto com a quebra em repositories e services.
- **ecommerce-api-legacy (God Class em Node):** stack diferente, mesma receita. A skill quebrou o
`AppManager` em camadas e, de quebra, trocou os callbacks aninhados por `async/await` e parou de
logar dados de cartão. Provou que as referências não estavam presas a Python.
- **task-manager-api (já parcialmente organizado):** aqui a skill não reescreveu tudo — ela
aproveitou as pastas que já existiam e moveu a regra de negócio das rotas para `services/` e
`controllers/`, criou `repositories/` e `serializers.py`, e reusou abstrações que já existiam no
model (ex.: `Task.is_overdue()`). É a prova de que ela se adapta ao nível de organização do projeto.

## Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (a skill está em `.claude/skills/refactor-arch/`).
- Para rodar as apps depois da refatoração: **Python 3.11+** (projetos 1 e 3) e **Node.js 18+**
(projeto 2).

### Comandos

A skill já está copiada dentro dos 3 projetos. Para executá-la, entre na pasta do projeto e invoque:

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill roda as 3 fases em sequência: faz a análise, mostra o relatório de auditoria e **para pedindo
confirmação** antes de refatorar. Responda `y` para seguir para a Fase 3. O relatório de cada execução
fica em [reports/](reports/).

### Validação

Para conferir que a refatoração não quebrou nada, suba cada app e teste os endpoints. Cada projeto tem
um `.env.example` — copie para `.env` antes de subir (ou exporte as variáveis na mão).

```bash
# Projeto 1 — Flask (http://localhost:5000)
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/python app.py
# em outro terminal: curl http://localhost:5000/produtos

# Projeto 2 — Express (http://localhost:3000)
cd ../ecommerce-api-legacy
npm install
cp .env.example .env
node src/app.js
# em outro terminal: use o api.http ou
#   curl -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' \
#     -d '{"usr":"Ana","eml":"ana@x.com","pwd":"123","c_id":2,"card":"4111222233334444"}'

# Projeto 3 — Flask + SQLAlchemy (http://localhost:5000)
cd ../task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/python seed.py     # popula o banco — rode antes do primeiro boot
.venv/bin/python app.py
# em outro terminal: curl http://localhost:5000/tasks
```

> Os projetos 1 e 3 sobem na porta 5000 por padrão; rode um de cada vez ou ajuste a `PORT` no `.env`.
