================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project (API de E-commerce)
Stack:   Python 3 + Flask 3.1.1 (flask-cors 5.0.1), SQLite
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] SQL Injection
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140-166, 174, 188, 220, 224, 279-281, 289-297
Description: Praticamente todas as queries são montadas por concatenação de string com entrada do usuário, sem parametrização. Casos representativos: busca por id (`"... WHERE id = " + str(id)`), criação de produto/usuário (`"INSERT ... VALUES ('" + nome + "'...")`), e a busca dinâmica em `buscar_produtos` (LIKE com `termo` concatenado).
Impact: Permite ler, alterar e apagar todo o banco e burlar regras via payloads maliciosos. É a falha mais grave do projeto e está espalhada por toda a camada de dados.
Recommendation: Substituir 100% das queries por parametrização com placeholders (`?`) e bindings, isolando o acesso em uma camada Repository (ver playbook: SQL Injection / Repository).

### [CRITICAL] Authentication Bypass via SQL Injection
File: models.py:105-111 (login_usuario)
Description: O login concatena email e senha direto no `WHERE` (`"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`). Um payload como `' OR '1'='1` autentica sem credenciais válidas.
Impact: Acesso não autorizado a qualquer conta, inclusive admin. Combinação de SQL Injection com falha de autenticação.
Recommendation: Query parametrizada + comparação por hash (ver finding de Criptografia). Mover a regra para um `AuthService`/`UserService`.

### [CRITICAL] Arbitrary Query Execution & Unprotected Admin Endpoints
File: app.py:47-57 (/admin/reset-db), app.py:59-78 (/admin/query)
Description: `/admin/query` executa SQL arbitrário recebido no corpo da requisição (`cursor.execute(query)`); `/admin/reset-db` apaga todas as tabelas. Nenhum dos dois exige autenticação.
Impact: Qualquer cliente pode executar SQL livre ou destruir o banco — equivale a entregar o servidor.
Recommendation: Preservar o caminho `/admin/query`, mas desativar a operação com `410 Gone`, sem executar SQL recebido do cliente; proteger as demais operações administrativas com autenticação/autorização (ver playbook: Arbitrary Execution).

### [CRITICAL] Hardcoded Secrets & Plaintext Passwords
File: app.py:7 (SECRET_KEY), database.py:76-78 (seed de senhas), models.py:126-129 (criar_usuario), controllers.py:289 (secret_key no /health)
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` está versionada no código; senhas são armazenadas e comparadas em texto puro; o endpoint `/health` devolve a própria `secret_key`.
Impact: Vazamento do banco compromete todas as senhas imediatamente; o segredo da aplicação é público. Falha grave de segurança e de criptografia.
Recommendation: Mover segredos para variáveis de ambiente/config; aplicar hashing forte (bcrypt/argon2) na criação e verificação de senha; remover dados sensíveis das respostas (ver playbook: Secrets / Cryptography).

### [HIGH] Business Logic in Controller
File: controllers.py:24-62 (validação/criação), 188-220 (criar_pedido + notificações), 237-255 (atualizar_status_pedido)
Description: Os controllers concentram validação de domínio, montagem de respostas e orquestração de notificações (envio de "email/SMS/push" via `print`). A regra de negócio de pedido e status vive parte no controller, parte no model — não há camada Service.
Impact: Lógica não reutilizável nem testável em isolamento; viola o "controller fino" do MVC.
Recommendation: Extrair regra de negócio para `ProductService`/`OrderService`/`UserService`; controller só valida entrada, chama o service e formata a resposta (ver playbook: Service Layer).

### [HIGH] Global Mutable State / No Dependency Injection
File: database.py:4-11 (db_connection global), usado em todo controllers.py e models.py
Description: A conexão é um singleton global mutável (`db_connection = None` + `global`), instanciado dentro de `get_db()` e importado diretamente pelas demais camadas, sem injeção de dependência.
Impact: Estado compartilhado entre requisições, risco de concorrência (`check_same_thread=False`) e acoplamento que impede testar/trocar a fonte de dados.
Recommendation: Centralizar a criação da conexão e injetá-la nos repositories (composition root); separar criação de schema/seed do acesso runtime (ver playbook: DI / Connection).

### [HIGH] Missing Layer Separation (sem Model/Service real)
File: models.py:1-315 (arquivo inteiro)
Description: O "models.py" é apenas um conjunto de funções com SQL cru e mapeamento manual de linha→dict repetido em ~6 funções. Regra de negócio (cálculo de desconto em `relatorio_vendas`, baixa de estoque em `criar_pedido`) está misturada ao acesso a dados. Não existem entidades nem services.
Impact: Mudança de schema quebra N pontos; impossível trocar a fonte de dados ou testar a regra isoladamente.
Recommendation: Separar em Repository (SQL), Service (regra) e Model/DTO (entidade/contrato); mapeamento centralizado (ver playbook: Layer Separation).

### [MEDIUM] N+1 Queries
File: models.py:171-201 (get_pedidos_usuario), 203-233 (get_todos_pedidos)
Description: Para cada pedido faz uma query de itens e, para cada item, mais uma query buscando o nome do produto. O número de queries cresce linearmente com pedidos × itens.
Impact: Degradação de performance proporcional ao volume de dados.
Recommendation: Substituir por JOINs ou busca em lote (`IN (...)`) na camada Repository (ver playbook: N+1).

### [MEDIUM] Duplicated / Missing Validation
File: controllers.py:28-54 (criar_produto) vs 72-90 (atualizar_produto)
Description: As mesmas regras de validação de produto (campos obrigatórios, preço/estoque ≥ 0, limites de nome) estão duplicadas entre criação e atualização; `atualizar_produto` ainda perde a validação de categoria e de tamanho de nome.
Impact: Regras divergem com o tempo; dados inválidos entram pela rota de update.
Recommendation: Centralizar validação em um único ponto (DTO/validador no service) reutilizado por create e update (ver playbook: Validation).

### [MEDIUM] Broad Error Handling Leaking Internals
File: controllers.py:10-12, 21-22, 60-62, 95-96 (e demais handlers); padrão `except Exception as e: return jsonify({"erro": str(e)})`
Description: Todo handler captura `Exception` genérica e devolve `str(e)` ao cliente, expondo detalhes internos; não há tratamento centralizado nem diferenciação de tipos de erro.
Impact: Vazamento de detalhes de implementação, respostas inconsistentes e mascaramento de bugs.
Recommendation: Tratamento de erro específico + handler de erros centralizado (errorhandler do Flask); logar internamente, responder mensagem genérica (ver playbook: Error Handling).

### [MEDIUM] Sensitive Data Exposure in Response
File: models.py:72-87 (get_todos_usuarios), 89-103 (get_usuario_por_id), controllers.py:276-290 (/health)
Description: As listagens/buscas de usuário incluem o campo `senha` na resposta; `/health` devolve `secret_key`, `debug` e `db_path`.
Impact: Vazamento de credenciais e configuração sensível pela própria API.
Recommendation: Usar DTO/Resource de saída que nunca inclui senha/segredos; enxugar o `/health` (ver playbook: DTO / Sensitive Data).

### [LOW] Magic Numbers
File: models.py:256-262 (faixas de desconto 10000/5000/1000 e 0.1/0.05/0.02), controllers.py:47-50 (limites 2/200)
Description: Limiares e fatores de regra de negócio aparecem como números soltos, sem constantes nomeadas.
Impact: Regra de negócio ilegível e difícil de manter.
Recommendation: Extrair para constantes nomeadas no service (ver playbook: Magic Numbers).

### [LOW] print() as Logging
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 161, 179, 182, 208-210, 219, 248-250
Description: Eventos e erros são registrados com `print(...)`, sem níveis nem estrutura.
Impact: Sem observabilidade real; polui stdout e mistura log com "notificação".
Recommendation: Usar `logging` estruturado com níveis; separar notificação real de log (ver playbook: Logging).

### [LOW] Poor Naming / Shadowing
File: models.py e controllers.py — parâmetro `id` (shadow do builtin) em várias funções; `e` em todos os `except`
Description: Uso de `id` como nome de parâmetro sombreia o builtin do Python; identificadores pouco descritivos nos handlers de erro.
Impact: Baixa legibilidade e risco de confusão.
Recommendation: Renomear para nomes descritivos (`product_id`, `error`) seguindo o guia de estilo (ver playbook: Naming).

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
