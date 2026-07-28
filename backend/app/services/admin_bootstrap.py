import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.enterprise import Role, UserRole
from app.models.user import User


def provision_admin(db: Session, email: str, password: str) -> User:
    """Create or update the emergency production administrator."""
    if len(password) < 12 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[^A-Za-z0-9]', password):
        raise ValueError('A senha administrativa deve ter 12 caracteres, maiuscula, numero e caractere especial.')

    normalized_email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is None:
        user = User(
            name='Administrador CRMoney',
            crm='ADMIN-PROD',
            crm_uf='SP',
            email=normalized_email,
            password_hash=hash_password(password),
            cnpj='00000000000002',
            phone='11999999999',
            city='Sao Paulo',
            state='SP',
            specialty='Administracao',
        )
        db.add(user)
        db.flush()
    else:
        user.password_hash = hash_password(password)
        user.deleted_at = None

    admin_role = db.scalar(select(Role).where(Role.name == 'ADMIN'))
    if admin_role is None:
        raise RuntimeError('A role ADMIN nao existe. Execute as migracoes antes do bootstrap.')
    assignment = db.scalar(select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == admin_role.id))
    if assignment is None:
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))

    db.commit()
    db.refresh(user)
    return user
