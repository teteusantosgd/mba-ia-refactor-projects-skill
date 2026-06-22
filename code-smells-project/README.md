# code-smells-project

API de E-commerce em Python/Flask, refatorada para arquitetura **MVC em camadas**
(entrada original do desafio `refactor-arch`).

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # ajuste os segredos antes de produção
python app.py
```

A aplicação sobe em `http://localhost:5000` (configurável via `PORT`). O banco SQLite
(`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de
exemplo. As senhas de exemplo são armazenadas com hash; o login segue funcionando com
as credenciais documentadas (ex.: `admin@loja.com` / `admin123`).

## Arquitetura

Fluxo de uma requisição: `Rota → Controller (fino) → Service (regra) → Repository → Banco`.

```
src/
├── config/settings.py          # configuração por ambiente (sem segredos hardcoded)
├── database/connection.py      # conexão escopada por requisição + schema/seed
├── models/                     # repositories (acesso a dados, SQL parametrizado)
│   ├── product_repository.py
│   ├── user_repository.py
│   └── order_repository.py
├── services/                   # regra de negócio
│   ├── product_service.py
│   ├── user_service.py
│   ├── order_service.py
│   ├── report_service.py
│   ├── notification_service.py
│   └── validators.py
├── controllers/                # handlers finos por domínio
├── views/routes.py             # blueprint com as rotas
├── middlewares/error_handler.py# tratamento de erro centralizado
├── container.py                # injeção de dependência (wiring)
└── app.py                      # composition root (factory create_app)
```

O entry point `app.py` (raiz) apenas instancia a app via `create_app()` e sobe o servidor.
