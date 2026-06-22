const AppError = require('../errors/AppError');
const logger = require('../utils/logger');

// Regra de negócio do checkout. Dependências injetadas via construtor.
const APPROVED_CARD_PREFIX = '4';
const DEFAULT_PASSWORD = '123456';

class CheckoutService {
    constructor({
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        passwordService,
        cacheService,
    }) {
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
        this.auditLogRepository = auditLogRepository;
        this.passwordService = passwordService;
        this.cacheService = cacheService;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseRepository.findActiveById(courseId);
        if (!course) throw new AppError(404, 'Curso não encontrado');

        const userId = await this.resolveUserId({ name, email, password });

        // Decisão de aprovação do pagamento (regra de negócio).
        // Nunca logamos o número do cartão nem a chave do gateway.
        const status = card.startsWith(APPROVED_CARD_PREFIX) ? 'PAID' : 'DENIED';
        logger.info('checkout_payment_processed', { userId, courseId, status });
        if (status === 'DENIED') throw new AppError(400, 'Pagamento recusado');

        const enrollmentId = await this.enrollmentRepository.create({ userId, courseId });
        await this.paymentRepository.create({ enrollmentId, amount: course.price, status });
        await this.auditLogRepository.create(`Checkout curso ${courseId} por ${userId}`);
        this.cacheService.set(`last_checkout_${userId}`, course.title);

        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }

    // Reusa o usuário existente (por email) ou cria um novo com senha já hasheada.
    async resolveUserId({ name, email, password }) {
        const existingUser = await this.userRepository.findByEmail(email);
        if (existingUser) return existingUser.id;

        const passwordHash = this.passwordService.hash(password || DEFAULT_PASSWORD);
        return this.userRepository.create({ name, email, passwordHash });
    }
}

module.exports = CheckoutService;
