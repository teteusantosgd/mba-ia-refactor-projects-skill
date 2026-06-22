// Acesso a dados da entidade Enrollment.
class EnrollmentRepository {
    constructor(dbClient) {
        this.db = dbClient;
    }

    async create({ userId, courseId }) {
        const result = await this.db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        );
        return result.lastID;
    }

    deleteByUserId(userId) {
        return this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    }
}

module.exports = EnrollmentRepository;
