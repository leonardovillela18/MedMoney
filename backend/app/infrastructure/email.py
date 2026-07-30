import logging
import smtplib
from email.message import EmailMessage
from html import escape

from app.core.config import get_settings


class ConsoleEmailProvider:
    def send_password_reset(self, recipient: str, link: str, expires_minutes: int) -> None:
        logging.getLogger('crmoney.email').info('Password reset email captured for development recipient=%s', recipient)


class SMTPEmailProvider:
    def __init__(self): self.settings = get_settings()
    def send_password_reset(self, recipient: str, link: str, expires_minutes: int) -> None:
        message=EmailMessage();message['Subject']='Redefinição de senha — CRMoney';message['From']=f'{self.settings.smtp_from_name} <{self.settings.smtp_from}>';message['To']=recipient
        message.set_content(f'Recebemos uma solicitação para redefinir sua senha.\n\nRedefinir senha: {link}\n\nEste link expira em {expires_minutes} minutos. Se você não solicitou a alteração, ignore este e-mail.')
        message.add_alternative(f'<p>Recebemos uma solicitação para redefinir sua senha.</p><p><a href="{escape(link)}">Redefinir senha</a></p><p>Este link expira em {expires_minutes} minutos.</p><p>Se você não solicitou a alteração, ignore este e-mail.</p>',subtype='html')
        with smtplib.SMTP(self.settings.smtp_host,self.settings.smtp_port,timeout=15) as smtp:
            if self.settings.smtp_use_tls:smtp.starttls()
            if self.settings.smtp_user:smtp.login(self.settings.smtp_user,self.settings.smtp_password)
            smtp.send_message(message)


def get_email_provider():
    return SMTPEmailProvider() if get_settings().email_provider == 'smtp' else ConsoleEmailProvider()
