// Acesso a dados da entidade Course.
class CourseRepository {
    constructor(dbClient) {
        this.db = dbClient;
    }

    findActiveById(id) {
        return this.db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    }
}

module.exports = CourseRepository;
