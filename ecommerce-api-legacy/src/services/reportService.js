// Regra de negócio do relatório financeiro: agrupa as linhas (já carregadas em
// uma única query) por curso, somando a receita apenas dos pagamentos PAID.
class ReportService {
    constructor({ reportRepository }) {
        this.reportRepository = reportRepository;
    }

    async getFinancialReport() {
        const rows = await this.reportRepository.getFinancialRows();
        const reportByCourse = new Map();

        for (const row of rows) {
            if (!reportByCourse.has(row.course_id)) {
                reportByCourse.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: [],
                });
            }

            const courseData = reportByCourse.get(row.course_id);

            // Curso sem matrículas: mantém students vazio e revenue zero.
            if (row.enrollment_id == null) continue;

            if (row.payment_status === 'PAID') {
                courseData.revenue += row.payment_amount;
            }

            courseData.students.push({
                student: row.student_name || 'Unknown',
                paid: row.payment_amount != null ? row.payment_amount : 0,
            });
        }

        return Array.from(reportByCourse.values());
    }
}

module.exports = ReportService;
