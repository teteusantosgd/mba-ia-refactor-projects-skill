================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy (domínio real: LMS / cursos com checkout)
Stack:   JavaScript (Node.js) + Express ^4.18.2 + sqlite3 ^5.1.6
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secrets / Credentials
File: src/utils.js:1-7
Description: Credenciais de banco (`dbUser`, `dbPass`), chave de gateway de pagamento de produção (`paymentGatewayKey = "pk_live_..."`) e usuário SMTP estão literais no código-fonte versionado.
Impact: Comprometimento direto de segredos. A chave `pk_live_` permite operações financeiras reais; qualquer pessoa com acesso ao repositório controla o gateway.
Recommendation: Mover todos os segredos para variáveis de ambiente (`process.env`) carregadas em uma camada de configuração (`config/`), com `.env` fora do versionamento. Nunca commitar valores reais.

### [CRITICAL] Weak / Broken Cryptography
File: src/utils.js:17-23 (badCrypto); src/AppManager.js:18,69 (senhas em texto puro)
Description: A função `badCrypto` faz "hash" caseiro com base64 truncado a 10 caracteres — reversível e sem sal. O seed insere senha em texto puro (`'123'`) e o checkout usa `badCrypto` para novos usuários.
Impact: Vazamento do banco compromete todas as senhas instantaneamente; o esquema não resiste a nenhum ataque básico.
Recommendation: Substituir por `bcrypt`/`argon2`/`scrypt` com sal, encapsulado em um serviço de hashing. Nunca armazenar senha em texto puro.

### [CRITICAL] Sensitive Data Exposure — número de cartão e chave de pagamento em log
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` registra o número completo do cartão (PAN) e a chave de produção do gateway em stdout.
Impact: Violação grave de PCI-DSS e exposição de credenciais; logs costumam ser persistidos/agregados, expondo dados de cartão e segredos.
Recommendation: Nunca logar PAN nem segredos. Remover o log; se necessário, registrar apenas os últimos 4 dígitos mascarados, via logging estruturado, na camada de serviço.

### [HIGH] God Class / God File
File: src/AppManager.js:1-141
Description: `AppManager` cria as tabelas, popula seeds, registra todas as rotas, processa pagamento, cria usuário, faz matrícula e grava auditoria — todas as responsabilidades em uma única classe.
Impact: Nada é testável em isolamento; qualquer mudança afeta tudo; alto acoplamento e baixa coesão.
Recommendation: Quebrar em camadas — `config`, `db` (conexão), `models`/`repositories`, `services`, `controllers`, `routes`, entry point fino. Ver `refactoring-playbook.md`.

### [HIGH] Business Logic in Controller/Routes
File: src/AppManager.js:28-78 (checkout); src/AppManager.js:80-129 (financial-report)
Description: A regra de negócio (decisão de aprovação do pagamento, criação de usuário, matrícula, montagem do relatório e cálculo de receita) vive dentro dos handlers de rota.
Impact: Lógica não reutilizável nem testável; viola o "controller fino" do MVC.
Recommendation: Extrair para `CheckoutService` e `ReportService`; o controller apenas valida entrada, chama o serviço e retorna a resposta.

### [HIGH] Global Mutable State / No Dependency Injection
File: src/utils.js:9-10 (globalCache, totalRevenue); src/AppManager.js:7 (db instanciado no construtor)
Description: `globalCache` e `totalRevenue` são variáveis globais mutáveis compartilhadas entre requests; a conexão do banco é instanciada dentro da classe em vez de injetada.
Impact: Estado compartilhado entre requisições, vazamentos de memória, comportamento imprevisível sob concorrência, impossibilidade de mockar dependências em teste.
Recommendation: Injetar a conexão/repositórios via construtor; eliminar estado global mutável (cache, se necessário, encapsulado e com escopo controlado).

### [HIGH] Missing Layer Separation (sem Model/Service/Repository real)
File: src/AppManager.js (todo o arquivo)
Description: Não existem models, services nem repositories. O SQL cru e o mapeamento de linhas estão espalhados pelos handlers.
Impact: Mudança de schema quebra múltiplos pontos; impossível trocar a fonte de dados ou testar a regra de negócio sem o Express.
Recommendation: Criar repositórios por entidade (`UserRepository`, `CourseRepository`, etc.) que isolam o SQL, e serviços que orquestram a regra de negócio.

### [MEDIUM] N+1 Queries
File: src/AppManager.js:83-128 (financial-report)
Description: Para cada curso, faz uma query de matrículas; para cada matrícula, uma query de usuário e outra de pagamento — tudo via callbacks aninhados com contadores manuais (`coursesPending`, `enrPending`).
Impact: O número de queries cresce linearmente com o volume; performance degrada rápido e o controle manual de contadores é frágil.
Recommendation: Substituir por uma consulta com JOIN/agregação no repositório, ou carregar relações em lote; usar `async/await` + `util.promisify` para eliminar o callback hell.

### [MEDIUM] Missing / Broad Error Handling
File: src/AppManager.js:104-106 (erros ignorados); src/AppManager.js:131-137 (delete ignora err)
Description: Várias callbacks de query ignoram o parâmetro `err`; o `DELETE /api/users/:id` não trata erro e ainda deixa matrículas/pagamentos órfãos (a própria mensagem admite "ficaram sujos no banco").
Impact: Erros mascarados, respostas inconsistentes e integridade referencial quebrada (registros órfãos).
Recommendation: Tratar erros de forma específica, centralizar via middleware de erro do Express, e tratar a remoção de usuário em transação (cascade ou bloqueio quando houver dependências).

### [MEDIUM] Legacy Async / Debug Patterns
File: src/AppManager.js:1 (`require('sqlite3').verbose()`); src/AppManager.js:28-128 (callbacks aninhados de I/O)
Description: Uso de `.verbose()` do driver em runtime (overhead/diagnóstico em produção) e padrão legado de callbacks aninhados de I/O em vez de assíncrono moderno. Essas APIs não estão formalmente deprecated, mas são inadequadas para este contexto.
Impact: Overhead desnecessário e código difícil de manter/encadear; propenso a callback hell e erros silenciosos.
Recommendation: Usar o driver sem `.verbose()`; adotar `async/await` com uma camada Promise para o acesso a dados. A verificação obrigatória de APIs deprecated foi executada e não encontrou ocorrência formalmente deprecated neste projeto.

### [LOW] Poor Naming
File: src/AppManager.js:29-33
Description: Variáveis crípticas `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, courseId e cartão.
Impact: Baixa legibilidade; contraria o guia de estilo (nomes descritivos por extenso).
Recommendation: Renomear para `userName`, `email`, `password`, `courseId`, `card` e mapear o contrato de entrada via DTO.

### [LOW] Magic Numbers
File: src/AppManager.js:46 (`cc.startsWith("4")`); src/utils.js:19-22 (10000, substring(0,2)/(0,10))
Description: Limiares e constantes soltos: aprovação de pagamento baseada no dígito "4", loop de 10000 e cortes de string sem constante nomeada.
Impact: Regra de negócio ilegível e difícil de manter.
Recommendation: Extrair para constantes nomeadas (ex.: `APPROVED_CARD_PREFIX`) e remover a "cripto" caseira em favor de uma biblioteca.

### [LOW] console.log as Logging
File: src/utils.js:13; src/AppManager.js:45,57; src/app.js:13
Description: `console.log` usado para eventos, cache e auditoria, sem níveis nem estrutura.
Impact: Sem observabilidade real; polui stdout e mistura dados sensíveis (ver finding CRITICAL de cartão).
Recommendation: Adotar logging estruturado com níveis (campos nomeados), centralizado.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
