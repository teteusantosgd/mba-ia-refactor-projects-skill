# Project Analysis — heurísticas de detecção (Fase 1)

Como detectar stack, banco, domínio e arquitetura de qualquer projeto, sem assumir uma tecnologia.
A ideia é olhar primeiro os **arquivos de manifesto** (declaram a stack) e depois o **código-fonte**
(confirma o uso real).

## 1. Linguagem e gerenciador de pacotes

Procure, na raiz, o arquivo de manifesto. Ele revela linguagem e dependências de uma vez:

| Arquivo encontrado | Linguagem | Onde ler dependências |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | o próprio arquivo |
| `package.json` | Node.js / JavaScript | `dependencies` / `devDependencies` |
| `pom.xml`, `build.gradle` | Java | `<dependencies>` / `dependencies {}` |
| `go.mod` | Go | `require` |
| `Gemfile` | Ruby | o próprio arquivo |
| `composer.json` | PHP | `require` |

Como fallback, conte as extensões dos arquivos-fonte (`.py`, `.js`, `.ts`, `.java`, ...) e use a
predominante.

## 2. Framework (com versão)

Cruze as dependências do manifesto com os imports do código:

| Sinal no manifesto | Sinal no código | Framework |
|---|---|---|
| `flask` | `from flask import Flask` | Flask (Python) |
| `django` | `urls.py`, `settings.py`, `manage.py` | Django (Python) |
| `fastapi` | `from fastapi import FastAPI` | FastAPI (Python) |
| `express` | `require('express')` / `import express` | Express (Node) |
| `@nestjs/core` | decorators `@Module`, `@Controller` | NestJS (Node) |
| `spring-boot` | `@SpringBootApplication` | Spring Boot (Java) |

Pegue a **versão** do próprio manifesto (ex.: `flask==3.1.1`, `"express": "^4.18.2"`).

## 3. Banco de dados e tabelas

- **ORM declarativo** (SQLAlchemy, Sequelize, TypeORM, Mongoose): cada model/classe de entidade é uma
  tabela/coleção. Procure `db.Model`, `__tablename__`, `sequelize.define`, `@Entity`, `Schema(...)`.
- **SQL cru**: extraia os nomes de `CREATE TABLE`, `INSERT INTO`, `FROM`, `UPDATE`, `DELETE FROM`.
- **Driver/engine**: `sqlite3`, `psycopg2`/`pg`, `mysql`/`pymysql`, `mongodb` indicam o banco.
- Identifique também **onde a conexão é criada** (string de conexão, singleton global, pool) — isso
  importa para a Fase 3.

## 4. Domínio da aplicação

Infira o domínio a partir de:

- **Nomes das tabelas/models** (`produtos`, `pedidos`, `usuarios` → e-commerce; `tasks`, `users`,
  `categories` → gerenciador de tarefas; `courses`, `enrollments`, `payments` → LMS/educação).
- **Rotas registradas** (`/checkout`, `/orders`, `/tasks`, `/login`).
- **README do projeto-alvo**, se existir.

Descreva o domínio em **uma linha**, ex.: `E-commerce API (produtos, pedidos, usuários)`.

## 5. Arquitetura atual

Classifique para guiar a estratégia da Fase 3:

- **Monolito plano:** poucos arquivos na raiz, sem pastas de camadas; lógica, SQL e rotas misturados.
  Ex.: `app.py` + `controllers.py` + `models.py` na raiz.
- **God Class/God File:** uma classe/arquivo concentra banco + rotas + regra de negócio.
- **Parcialmente organizado:** já existem pastas (`models/`, `routes/`, `services/`), mas a separação
  pode ser superficial (regra de negócio vazada para as rotas, services vazios).
- **Em camadas:** separação real de responsabilidades (caso raro nos legados).

Verifique se a separação é **real ou apenas nominal**: abra as pastas existentes e cheque se a
responsabilidade de cada uma é respeitada (ex.: uma pasta `services/` que só tem notificação enquanto
as rotas calculam tudo = nominal).

## 6. Inventário de arquivos

Liste e **conte** os arquivos-fonte relevantes (exclua `node_modules/`, `venv/`, build artifacts,
migrations geradas). Esse número vai no resumo da Fase 1 (`Source files: N files analyzed`) e deve
condizer com a realidade.

## Saída esperada

Os dados coletados aqui alimentam exatamente o bloco `PHASE 1: PROJECT ANALYSIS` do `SKILL.md`.
