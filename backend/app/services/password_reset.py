import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password, hash_token
from app.core.config import get_settings
from app.infrastructure.email import get_email_provider
from app.models.user import PasswordResetToken, RefreshToken, User
from app.services.audit_service import AuditService

GENERIC_MESSAGE='Se existir uma conta associada a este e-mail, enviaremos instruções para redefinir sua senha.'


def request_password_reset(db:Session,user:User,request:Request)->None:
    now=datetime.now(timezone.utc)
    for old in db.scalars(select(PasswordResetToken).where(PasswordResetToken.user_id==user.id,PasswordResetToken.used_at.is_(None),PasswordResetToken.revoked_at.is_(None))):old.revoked_at=now
    raw=secrets.token_urlsafe(48);settings=get_settings();record=PasswordResetToken(user_id=user.id,token_hash=hash_token(raw),expires_at=now+timedelta(minutes=settings.password_reset_token_expire_minutes),request_ip=request.client.host if request.client else None,user_agent=request.headers.get('user-agent','')[:500]);db.add(record);db.commit()
    link=f"{settings.frontend_url.rstrip('/')}/redefinir-senha?token={raw}"
    get_email_provider().send_password_reset(user.email,link,settings.password_reset_token_expire_minutes)
    AuditService.record(db,'PASSWORD_RESET_REQUESTED','PasswordResetToken',user.id,record.id,request)


def reset_password(db:Session,raw_token:str,new_password:str,request:Request)->None:
    now=datetime.now(timezone.utc);record=db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash==hash_token(raw_token)).with_for_update())
    if not record:raise HTTPException(422,'Link inválido ou expirado.')
    expiry=record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
    if record.used_at or record.revoked_at or expiry<=now:raise HTTPException(422,'Link inválido ou expirado.')
    user=db.get(User,record.user_id)
    if not user or user.deleted_at:raise HTTPException(422,'Link inválido ou expirado.')
    user.password_hash=hash_password(new_password);record.used_at=now
    for other in db.scalars(select(PasswordResetToken).where(PasswordResetToken.user_id==user.id,PasswordResetToken.id!=record.id,PasswordResetToken.used_at.is_(None),PasswordResetToken.revoked_at.is_(None))):other.revoked_at=now
    for session in db.scalars(select(RefreshToken).where(RefreshToken.user_id==user.id,RefreshToken.revoked_at.is_(None))):session.revoked_at=now
    db.commit();AuditService.record(db,'PASSWORD_RESET_COMPLETED','User',user.id,user.id,request)
