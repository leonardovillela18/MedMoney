import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database.session import Base
from app.models.enterprise import AuditLog
from app.models.user import PasswordResetToken, RefreshToken, User
from app.schemas.auth import ResetPasswordRequest
from app.services.password_reset import GENERIC_MESSAGE, request_password_reset, reset_password
from app.auth.security import hash_password, hash_token, verify_password


class CaptureProvider:
    def __init__(self): self.link = ''
    def send_password_reset(self, recipient, link, expires_minutes): self.link = link


def database():
    engine=create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine,tables=[User.__table__,RefreshToken.__table__,PasswordResetToken.__table__,AuditLog.__table__])
    return Session(engine)


def request(): return Request({'type':'http','method':'POST','path':'/auth/forgot-password','headers':[(b'user-agent',b'pytest')],'client':('127.0.0.1',1234),'state':{}})


def user(db):
    item=User(name='Teste Seguro',crm='12345',crm_uf='SP',email=f'{uuid.uuid4()}@example.com',password_hash=hash_password('OldPass@1'),cnpj=str(uuid.uuid4().int)[:14],phone='11999999999',city='São Paulo',state='SP',specialty='Clínica Médica');db.add(item);db.commit();return item


def issue(monkeypatch,db,item):
    capture=CaptureProvider();monkeypatch.setattr('app.services.password_reset.get_email_provider',lambda:capture)
    request_password_reset(db,item,request());raw=capture.link.split('token=')[1]
    return raw,db.query(PasswordResetToken).order_by(PasswordResetToken.created_at.desc()).first()


def test_forgot_response_is_always_generic():
    assert 'Se existir uma conta' in GENERIC_MESSAGE


def test_request_creates_only_token_hash(monkeypatch):
    db=database();raw,record=issue(monkeypatch,db,user(db))
    assert record.token_hash==hash_token(raw) and raw not in record.token_hash


def test_new_request_revokes_previous_token(monkeypatch):
    db=database();item=user(db);_,old=issue(monkeypatch,db,item);issue(monkeypatch,db,item);db.refresh(old)
    assert old.revoked_at is not None


def test_valid_token_changes_password_is_single_use_and_revokes_sessions(monkeypatch):
    db=database();item=user(db);raw,record=issue(monkeypatch,db,item);session=RefreshToken(user_id=item.id,token_hash=hash_token('refresh-token-value'),expires_at=datetime.now(timezone.utc)+timedelta(days=1));db.add(session);db.commit()
    reset_password(db,raw,'NewPass@2',request());db.refresh(item);db.refresh(record);db.refresh(session)
    assert verify_password('NewPass@2',item.password_hash) and record.used_at and session.revoked_at
    with pytest.raises(HTTPException):reset_password(db,raw,'Another@3',request())


def test_expired_token_is_rejected(monkeypatch):
    db=database();raw,record=issue(monkeypatch,db,user(db));record.expires_at=datetime.now(timezone.utc)-timedelta(minutes=1);db.commit()
    with pytest.raises(HTTPException):reset_password(db,raw,'NewPass@2',request())


def test_unknown_token_is_rejected():
    with pytest.raises(HTTPException):reset_password(database(),'x'*64,'NewPass@2',request())


def test_weak_reset_password_is_rejected_by_shared_policy():
    with pytest.raises(ValidationError):ResetPasswordRequest(token='x'*64,password='weakpass')
