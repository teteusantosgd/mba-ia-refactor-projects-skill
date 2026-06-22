const express = require('express');

const config = require('./config');
const logger = require('./utils/logger');
const { createDbClient, initializeDatabase } = require('./db');

const passwordService = require('./services/passwordService');
const CacheService = require('./services/cacheService');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const UserService = require('./services/userService');

const UserRepository = require('./models/userRepository');
const CourseRepository = require('./models/courseRepository');
const EnrollmentRepository = require('./models/enrollmentRepository');
const PaymentRepository = require('./models/paymentRepository');
const AuditLogRepository = require('./models/auditLogRepository');
const ReportRepository = require('./models/reportRepository');

const createCheckoutController = require('./controllers/checkoutController');
const createReportController = require('./controllers/reportController');
const createUserController = require('./controllers/userController');
const createRouter = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

// Composition root: cria a conexão, instancia e injeta as dependências de cada
// camada, monta o roteamento e sobe a aplicação.
async function bootstrap() {
    const dbClient = createDbClient();
    await initializeDatabase(dbClient, { passwordService });

    const userRepository = new UserRepository(dbClient);
    const courseRepository = new CourseRepository(dbClient);
    const enrollmentRepository = new EnrollmentRepository(dbClient);
    const paymentRepository = new PaymentRepository(dbClient);
    const auditLogRepository = new AuditLogRepository(dbClient);
    const reportRepository = new ReportRepository(dbClient);

    const cacheService = new CacheService();
    const checkoutService = new CheckoutService({
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        passwordService,
        cacheService,
    });
    const reportService = new ReportService({ reportRepository });
    const userService = new UserService({
        dbClient,
        userRepository,
        enrollmentRepository,
        paymentRepository,
    });

    const checkoutController = createCheckoutController(checkoutService);
    const reportController = createReportController(reportService);
    const userController = createUserController(userService);

    const app = express();
    app.use(express.json());
    app.use(createRouter({ checkoutController, reportController, userController }));
    app.use(errorHandler);

    app.listen(config.port, () => {
        logger.info('server_started', {
            port: config.port,
            message: `Servidor rodando na porta ${config.port}...`,
        });
    });
}

bootstrap().catch((err) => {
    logger.error('bootstrap_failed', { message: err.message });
    process.exit(1);
});
