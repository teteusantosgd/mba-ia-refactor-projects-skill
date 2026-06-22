// Acesso a dados de auditoria.
class AuditLogRepository {
    constructor(dbClient) {
        this.db = dbClient;
    }

    create(action) {
        return this.db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action],
        );
    }
}

module.exports = AuditLogRepository;
