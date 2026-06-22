// Acesso a dados da entidade User. Apenas queries parametrizadas; sem regra de negócio.
class UserRepository {
    constructor(dbClient) {
        this.db = dbClient;
    }

    findByEmail(email) {
        return this.db.get('SELECT id FROM users WHERE email = ?', [email]);
    }

    async create({ name, email, passwordHash }) {
        const result = await this.db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
        );
        return result.lastID;
    }

    deleteById(id) {
        return this.db.run('DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = UserRepository;
