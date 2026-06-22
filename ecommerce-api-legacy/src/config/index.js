require('dotenv').config();

// Configuração por ambiente. Nenhum segredo fica hardcoded no código:
// todos os valores sensíveis vêm de variáveis de ambiente (ver .env.example).
module.exports = {
    port: Number(process.env.PORT) || 3000,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    db: {
        user: process.env.DB_USER || '',
        pass: process.env.DB_PASS || '',
    },
};
