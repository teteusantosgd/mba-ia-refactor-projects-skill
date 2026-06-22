import logging
import smtplib

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de notificações por e-mail.

    As credenciais SMTP são injetadas via configuração (sem segredos hardcoded) e não há mais
    estado mutável em memória — cada chamada é independente.
    """

    def __init__(self, settings):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.user, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception:
            logger.exception("Erro ao enviar email para %s", to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        return self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        return self.send_email(user.email, subject, body)
