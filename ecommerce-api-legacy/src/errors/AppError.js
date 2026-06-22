// Erro de domínio "esperado": carrega o status HTTP e a mensagem ao usuário.
// O middleware de erro envia esses casos diretamente; demais erros viram 500 genérico.
class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.name = 'AppError';
        this.status = status;
        this.expose = true;
    }
}

module.exports = AppError;
