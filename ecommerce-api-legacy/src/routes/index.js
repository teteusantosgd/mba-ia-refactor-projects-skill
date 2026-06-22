const express = require('express');

// Roteamento isolado da lógica: define os endpoints e delega aos controllers.
// As rotas e os contratos são idênticos aos da versão legada.
function createRouter({ checkoutController, reportController, userController }) {
    const router = express.Router();

    router.post('/api/checkout', checkoutController.checkout);
    router.get('/api/admin/financial-report', reportController.financialReport);
    router.delete('/api/users/:id', userController.deleteUser);

    return router;
}

module.exports = createRouter;
