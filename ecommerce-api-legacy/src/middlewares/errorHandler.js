const AppError = require('../errors/AppError');
const logger = require('../utils/logger');

// Tratamento de erro centralizado. Erros de domínio (AppError) preservam o
// status e a mensagem originais; erros inesperados são logados e respondem 500
// genérico, sem vazar stack trace ao cliente.
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.status).send(err.message);
    }

    logger.error('unhandled_error', { path: req.path, message: err.message });
    return res.status(500).send('Erro interno');
}

module.exports = errorHandler;
