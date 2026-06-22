// Logging estruturado simples (substitui console.log solto).
// Campos nomeados em JSON; nunca registre dados sensíveis (cartão, segredos).
function write(level, event, data = {}) {
    const entry = { level, event, time: new Date().toISOString(), ...data };
    const line = JSON.stringify(entry);
    if (level === 'error') {
        console.error(line);
    } else {
        console.log(line);
    }
}

module.exports = {
    info: (event, data) => write('info', event, data),
    error: (event, data) => write('error', event, data),
};
