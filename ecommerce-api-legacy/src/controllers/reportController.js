function createReportController(reportService) {
    return {
        async financialReport(req, res, next) {
            try {
                const report = await reportService.getFinancialReport();
                return res.json(report);
            } catch (err) {
                return next(err);
            }
        },
    };
}

module.exports = createReportController;
