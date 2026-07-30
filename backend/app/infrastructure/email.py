import logging
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

from app.core.config import get_settings


logger = logging.getLogger("crmoney.email")


class ConsoleEmailProvider:
    def send_password_reset(
        self,
        recipient: str,
        link: str,
        expires_minutes: int,
    ) -> None:
        logger.info(
            "Password reset email captured for development recipient=%s",
            recipient,
        )


class UnconfiguredEmailProvider:
    def send_password_reset(
        self,
        recipient: str,
        link: str,
        expires_minutes: int,
    ) -> None:
        raise RuntimeError(
            "Password reset email provider is not configured for production"
        )


class SMTPEmailProvider:
    def __init__(self):
        self.settings = get_settings()

    def send_password_reset(
        self,
        recipient: str,
        link: str,
        expires_minutes: int,
    ) -> None:
        message = self._build_password_reset_message(
            recipient=recipient,
            link=link,
            expires_minutes=expires_minutes,
        )

        if self.settings.smtp_use_ssl:
            self._send_with_ssl(message)
        else:
            self._send_with_starttls_or_plain(message)

    def _build_password_reset_message(
        self,
        recipient: str,
        link: str,
        expires_minutes: int,
    ) -> EmailMessage:
        message = EmailMessage()

        message["Subject"] = "Redefinição de senha — CRMoney"
        message["From"] = (
            f"{self.settings.smtp_from_name} "
            f"<{self.settings.smtp_from}>"
        )
        message["To"] = recipient

        message.set_content(
            "Recebemos uma solicitação para redefinir sua senha.\n\n"
            f"Redefinir senha: {link}\n\n"
            f"Este link expira em {expires_minutes} minutos.\n\n"
            "Se você não solicitou a alteração, ignore este e-mail."
        )

        safe_link = escape(link, quote=True)

        message.add_alternative(
            f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <body>
                <p>
                    Recebemos uma solicitação para redefinir sua senha
                    no CRMoney.
                </p>

                <p>
                    <a href="{safe_link}">
                        Redefinir senha
                    </a>
                </p>

                <p>
                    Este link expira em {expires_minutes} minutos.
                </p>

                <p>
                    Se você não solicitou esta alteração,
                    ignore este e-mail.
                </p>
            </body>
            </html>
            """,
            subtype="html",
        )

        return message

    def _send_with_ssl(
        self,
        message: EmailMessage,
    ) -> None:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            self.settings.smtp_host,
            self.settings.smtp_port,
            timeout=15,
            context=context,
        ) as smtp:
            self._authenticate_and_send(
                smtp=smtp,
                message=message,
            )

    def _send_with_starttls_or_plain(
        self,
        message: EmailMessage,
    ) -> None:
        with smtplib.SMTP(
            self.settings.smtp_host,
            self.settings.smtp_port,
            timeout=15,
        ) as smtp:
            if self.settings.smtp_use_tls:
                context = ssl.create_default_context()

                smtp.starttls(
                    context=context,
                )

            self._authenticate_and_send(
                smtp=smtp,
                message=message,
            )

    def _authenticate_and_send(
        self,
        smtp,
        message: EmailMessage,
    ) -> None:
        if self.settings.smtp_user:
            smtp.login(
                self.settings.smtp_user,
                self.settings.smtp_password,
            )

        smtp.send_message(message)


def get_email_provider():
    settings = get_settings()

    if settings.email_provider == "smtp":
        required_settings = (
            settings.smtp_host,
            settings.smtp_user,
            settings.smtp_password,
            settings.smtp_from,
        )

        if not all(required_settings):
            return UnconfiguredEmailProvider()

        return SMTPEmailProvider()

    if settings.environment == "production":
        return UnconfiguredEmailProvider()

    return ConsoleEmailProvider()