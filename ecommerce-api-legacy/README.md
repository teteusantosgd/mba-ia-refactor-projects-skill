# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
cp .env.example .env
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.
As variáveis exportadas no shell têm precedência sobre os valores carregados do `.env`.

Exemplos de requisições estão em `api.http`.
