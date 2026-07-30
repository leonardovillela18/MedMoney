from unittest.mock import MagicMock, patch

import pytest

from app.core.config import get_settings
from app.infrastructure.email import SMTPEmailProvider


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def configure_smtp(monkeypatch, *, use_ssl, use_tls):
    monkeypatch.setenv("EMAIL_PROVIDER", "smtp")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "465" if use_ssl else "587")
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("SMTP_FROM", "test@example.com")
    monkeypatch.setenv("SMTP_FROM_NAME", "CRMoney")
    monkeypatch.setenv(
        "SMTP_USE_SSL",
        "true" if use_ssl else "false",
    )
    monkeypatch.setenv(
        "SMTP_USE_TLS",
        "true" if use_tls else "false",
    )

    get_settings.cache_clear()


def test_smtp_ssl_uses_smtp_ssl(monkeypatch):
    configure_smtp(
        monkeypatch,
        use_ssl=True,
        use_tls=False,
    )

    smtp_instance = MagicMock()
    smtp_context = MagicMock()
    smtp_context.__enter__.return_value = smtp_instance

    with patch(
        "app.infrastructure.email.smtplib.SMTP_SSL",
        return_value=smtp_context,
    ) as smtp_ssl:
        provider = SMTPEmailProvider()

        provider.send_password_reset(
            "user@example.com",
            "https://example.com/reset?token=test",
            30,
        )

        smtp_ssl.assert_called_once()

        smtp_instance.login.assert_called_once_with(
            "test@example.com",
            "test-password",
        )

        smtp_instance.send_message.assert_called_once()


def test_smtp_starttls(monkeypatch):
    configure_smtp(
        monkeypatch,
        use_ssl=False,
        use_tls=True,
    )

    smtp_instance = MagicMock()
    smtp_context = MagicMock()
    smtp_context.__enter__.return_value = smtp_instance

    with patch(
        "app.infrastructure.email.smtplib.SMTP",
        return_value=smtp_context,
    ) as smtp:
        provider = SMTPEmailProvider()

        provider.send_password_reset(
            "user@example.com",
            "https://example.com/reset?token=test",
            30,
        )

        smtp.assert_called_once()

        smtp_instance.starttls.assert_called_once()

        smtp_instance.login.assert_called_once_with(
            "test@example.com",
            "test-password",
        )

        smtp_instance.send_message.assert_called_once()


def test_ssl_and_starttls_cannot_be_enabled_together(
    monkeypatch,
):
    configure_smtp(
        monkeypatch,
        use_ssl=True,
        use_tls=True,
    )

    with pytest.raises(
        ValueError,
        match="SMTP_USE_SSL and SMTP_USE_TLS cannot both be true",
    ):
        get_settings()