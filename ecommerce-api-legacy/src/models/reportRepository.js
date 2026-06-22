// Consulta agregada do relatório financeiro em uma única query (resolve o N+1).
// LEFT JOIN preserva cursos sem matrículas; o agrupamento é feito no service.
class ReportRepository {
    constructor(dbClient) {
        this.db = dbClient;
    }

    getFinancialRows() {
        return this.db.all(`
            SELECT c.id           AS course_id,
                   c.title        AS course_title,
                   e.id           AS enrollment_id,
                   u.name         AS student_name,
                   p.amount       AS payment_amount,
                   p.status       AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u       ON u.id = e.user_id
            LEFT JOIN payments p    ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);
    }
}

module.exports = ReportRepository;
