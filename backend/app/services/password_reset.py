"""Boundary for password-reset delivery; plug an e-mail provider here in production."""
from app.models.user import User

def request_password_reset(_: User) -> None:
    # Deliberately does not reveal whether an account exists. Delivery provider is
    # configured in the deployment layer, keeping domain logic independent.
    return None
