from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.security import create_access_token, create_refresh_token, hash_password, hash_token, verify_password
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import RefreshToken, User
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserResponse
from app.services.password_reset import request_password_reset
router=APIRouter(prefix='/auth',tags=['Autenticação']); limiter=Limiter(key_func=get_remote_address)
def tokens_for(user:User,db:Session)->TokenResponse:
    raw,hashed,expires=create_refresh_token(); db.add(RefreshToken(user_id=user.id,token_hash=hashed,expires_at=expires)); db.commit(); return TokenResponse(access_token=create_access_token(str(user.id)),refresh_token=raw)
@router.post('/register',response_model=TokenResponse,status_code=status.HTTP_201_CREATED)
def register(payload:RegisterRequest,db:Session=Depends(get_db)):
    existing=db.scalar(select(User).where((User.email==payload.email.lower())|(User.cnpj==payload.cnpj)))
    if existing: raise HTTPException(status_code=409,detail='Já existe uma conta com este e-mail ou CNPJ.')
    user=User(**payload.model_dump(exclude={'password'}),email=payload.email.lower(),password_hash=hash_password(payload.password)); db.add(user); db.commit(); db.refresh(user); return tokens_for(user,db)
@router.post('/login',response_model=TokenResponse)
@limiter.limit('5/minute')
def login(request:Request,payload:LoginRequest,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower(),User.deleted_at.is_(None)))
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(status_code=401,detail='E-mail ou senha incorretos.')
    return tokens_for(user,db)
@router.get('/me',response_model=UserResponse)
def me(user:User=Depends(current_user)): return UserResponse(id=str(user.id),name=user.name,email=user.email,crm=user.crm,crm_uf=user.crm_uf,specialty=user.specialty,city=user.city,state=user.state)
@router.post('/logout',status_code=204)
def logout(data:dict,db:Session=Depends(get_db)):
    token=data.get('refresh_token',''); record=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==hash_token(token)))
    if record: record.revoked_at=datetime.now(timezone.utc); db.commit()
@router.post('/forgot-password',status_code=204)
def forgot_password(payload:ForgotPasswordRequest,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower(),User.deleted_at.is_(None)))
    if user: request_password_reset(user)
    return None
@router.post('/reset-password',status_code=204)
def reset_password(_:ResetPasswordRequest): return None
