// Controller fino: valida entrada, mapeia o DTO de request, chama o service e
// devolve a resposta. Erros são delegados ao middleware central via next(err).
function createCheckoutController(checkoutService) {
    return {
        async checkout(req, res, next) {
            // Mapeia o contrato de entrada legado para nomes descritivos.
            const name = req.body.usr;
            const email = req.body.eml;
            const password = req.body.pwd;
            const courseId = req.body.c_id;
            const card = req.body.card;

            if (!name || !email || !courseId || !card) {
                return res.status(400).send('Bad Request');
            }

            try {
                const result = await checkoutService.checkout({
                    name,
                    email,
                    password,
                    courseId,
                    card,
                });
                return res.status(200).json(result);
            } catch (err) {
                return next(err);
            }
        },
    };
}

module.exports = createCheckoutController;
