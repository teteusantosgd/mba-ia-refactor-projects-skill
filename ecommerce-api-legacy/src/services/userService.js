// Regra de negócio de usuários. A remoção é transacional e elimina os dados
// relacionados (pagamentos e matrículas), corrigindo o problema de registros
// órfãos da versão legada.
class UserService {
    constructor({ dbClient, userRepository, enrollmentRepository, paymentRepository }) {
        this.db = dbClient;
        this.userRepository = userRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
    }

    async deleteUser(id) {
        await this.db.exec('BEGIN');
        try {
            await this.paymentRepository.deleteByUserId(id);
            await this.enrollmentRepository.deleteByUserId(id);
            await this.userRepository.deleteById(id);
            await this.db.exec('COMMIT');
        } catch (err) {
            await this.db.exec('ROLLBACK');
            throw err;
        }
    }
}

module.exports = UserService;
