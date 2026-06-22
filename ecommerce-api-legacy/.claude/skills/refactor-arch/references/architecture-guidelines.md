# Architecture Guidelines — o MVC alvo (Fase 3)

Regras da arquitetura para a qual refatoramos. O alvo é um **MVC em camadas com inversão de
dependência**. Siga as convenções de código já presentes no projeto-alvo.

## Fluxo de uma requisição

```
Rota/View → Controller (fino) → Service (regra de negócio) → Repository/Model (dados) → Banco
```

Cada camada só conhece a camada imediatamente abaixo. A dependência aponta para **abstrações**, não
para implementações concretas.

## Responsabilidades de cada camada

| Camada | Faz | NÃO faz |
|---|---|---|
| **View / Routes** | Define endpoints, recebe request, devolve response, delega ao controller | Regra de negócio, acesso a banco |
| **Controller** | Valida entrada, mapeia DTO, chama service/repository, monta a resposta | Montar SQL, regra de domínio pesada |
| **Service** | Regra de negócio, orquestração, validações de domínio, transações | Lidar com HTTP, montar SQL cru |
| **Model / Repository** | Acesso a dados, queries, abstração da fonte de dados | Regra de negócio, formatação de resposta |
| **Config** | Configuração por ambiente (sem segredos hardcoded) | Lógica |
| **Middlewares** | Tratamento centralizado de erros, auth, CORS, logging | Regra de negócio |

> **Controller fino:** valida → mapeia → chama service/repo → retorna. Nada além disso. A regra de
> negócio mora no **service**; o acesso a dados, no **repository/model**.

## Estrutura de diretórios alvo

Adapte os nomes à convenção da stack, mantendo a separação de camadas.

### Python / Flask

```
src/
├── config/settings.py            # configuração por ambiente (env), sem segredos hardcoded
├── models/                       # entidades + acesso a dados (ORM ou repository)
│   ├── produto_model.py
│   └── usuario_model.py
├── controllers/                  # fluxo da aplicação por domínio
│   ├── produto_controller.py
│   └── pedido_controller.py
├── services/                     # regra de negócio (ex.: criação de pedido, notificações)
├── views/                        # blueprints/rotas
│   └── routes.py
├── middlewares/error_handler.py  # tratamento de erro centralizado
└── app.py                        # composition root (entry point + wiring)
```

### Node.js / Express

```
src/
├── config/index.js               # configuração por ambiente (process.env)
├── models/                       # acesso a dados (repositories)
├── controllers/                  # handlers finos por domínio
├── services/                     # regra de negócio (checkout, relatórios)
├── routes/                       # express.Router por domínio
├── middlewares/errorHandler.js   # error handling centralizado
└── app.js / server.js            # composition root
```

## Princípios obrigatórios na refatoração

1. **Configuração externalizada:** todo segredo/config sai do código para `config/` lendo variáveis
   de ambiente. Nada de `SECRET_KEY = "..."` no fonte.
2. **Models para abstrair dados:** acesso ao banco isolado em models/repositories; nada de SQL cru
   espalhado em controllers/rotas. Queries sempre parametrizadas.
3. **Views/Routes separadas:** roteamento isolado da lógica (Blueprints no Flask, Router no Express).
4. **Controllers concentram o fluxo:** orquestram, mas delegam regra ao service.
5. **Services para regra de negócio:** lógica reutilizável e testável fora do controller.
6. **Error handling centralizado:** um middleware/handler único; sem `except:` nu.
7. **Entry point claro (composition root):** um único lugar que monta as dependências e sobe a app.
8. **Injeção de dependência:** componentes recebem suas dependências; sem estado global mutável nem
   `new`/instanciação escondida dentro das funções.

## Adaptação ao contexto

- **Monolito plano** → criar todas as camadas do zero, distribuindo o que estava num arquivo só.
- **Projeto parcialmente organizado** → preservar a estrutura boa e corrigir o que está no lugar
  errado. Ex.: se já há `models/` e `routes/`, **extrair a regra de negócio das rotas para
  `services/` e `controllers/`**, reaproveitar abstrações já existentes (ex.: um `is_overdue()` no
  model), e eliminar duplicação — sem reescrever o que já está correto.
- Não troque a tecnologia (mesmo framework, mesmo banco) a menos que o objetivo seja corrigir uma API
  deprecated; o foco é arquitetura, não reescrita de stack.

## Convenções de código

- Identificadores em **inglês**; mensagens ao usuário e logs em **português**.
- Nomes descritivos e por extenso; sem abreviações crípticas.
- **Guard clauses / early return**; magic numbers viram constantes nomeadas.
- Validação centralizada (padrão "retorna erro, ou ok quando válido").
- Logging estruturado em vez de `print`/`console.log`.
- Preservar contratos: mesmas rotas e mesmos formatos de request/response.
