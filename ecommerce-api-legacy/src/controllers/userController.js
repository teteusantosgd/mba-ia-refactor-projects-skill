function createUserController(userService) {
    return {
        async deleteUser(req, res, next) {
            try {
                await userService.deleteUser(req.params.id);
                return res.send('Usuário e dados relacionados removidos com sucesso.');
            } catch (err) {
                return next(err);
            }
        },
    };
}

module.exports = createUserController;
