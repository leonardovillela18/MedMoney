import uuid
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException,Request,Response,status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.auth.security import create_access_token,create_refresh_token,hash_password,hash_token,verify_password
from app.core.config import get_settings
from app.database.session import get_db
from app.models.enterprise import Role,UserRole
from app.models.user import RefreshToken,User
from app.schemas.auth import ForgotPasswordRequest,LoginRequest,LogoutRequest,RefreshRequest,RegisterRequest,ResetPasswordRequest,SessionResponse,TokenResponse,UserResponse
from app.services.audit_service import AuditService
from app.services.password_reset import request_password_reset
router=APIRouter(prefix='/auth',tags=['Autenticação']);limiter=Limiter(key_func=get_remote_address)
settings=get_settings()
DEV_ADMIN_EMAIL='admin@medmoney.com'
DEV_ADMIN_PASSWORD='Admin@123'

def ensure_development_admin(payload:LoginRequest,db:Session)->User|None:
 if settings.environment=='production' or payload.email.lower()!=DEV_ADMIN_EMAIL or payload.password!=DEV_ADMIN_PASSWORD:return None
 user=db.scalar(select(User).where(User.email==DEV_ADMIN_EMAIL))
 if not user:
  user=User(name='Administrador MedFinance',crm='ADMIN-001',crm_uf='SP',email=DEV_ADMIN_EMAIL,password_hash=hash_password(DEV_ADMIN_PASSWORD),cnpj='00000000000001',phone='11999999999',city='São Paulo',state='SP',specialty='Administração');db.add(user);db.flush()
 else:
  user.name='Administrador MedFinance';user.password_hash=hash_password(DEV_ADMIN_PASSWORD);user.deleted_at=None
 role=db.scalar(select(Role).where(Role.name=='ADMIN'))
 if role and not db.scalar(select(UserRole).where(UserRole.user_id==user.id,UserRole.role_id==role.id)):db.add(UserRole(user_id=user.id,role_id=role.id))
 db.commit();db.refresh(user);return user

def tokens_for(user:User,db:Session,request:Request,rotated_from=None)->TokenResponse:
 raw,hashed,expires=create_refresh_token();record=RefreshToken(user_id=user.id,token_hash=hashed,expires_at=expires,ip_address=request.client.host if request.client else None,user_agent=request.headers.get('user-agent','')[:500],session_name=request.headers.get('x-device-name','Dispositivo'),last_used_at=datetime.now(timezone.utc),rotated_from_id=rotated_from);db.add(record);db.commit();return TokenResponse(access_token=create_access_token(str(user.id)),refresh_token=raw)
@router.post('/register',response_model=TokenResponse,status_code=status.HTTP_201_CREATED)
def register(request:Request,payload:RegisterRequest,db:Session=Depends(get_db)):
 existing=db.scalar(select(User).where((User.email==payload.email.lower())|(User.cnpj==payload.cnpj)))
 if existing:raise HTTPException(409,'Já existe uma conta com este e-mail ou CNPJ.')
 user=User(**payload.model_dump(exclude={'password'}),email=payload.email.lower(),password_hash=hash_password(payload.password));db.add(user);db.flush();role=db.scalar(select(Role).where(Role.name=='USER'))
 if role:db.add(UserRole(user_id=user.id,role_id=role.id))
 db.commit();db.refresh(user);AuditService.record(db,'REGISTER','User',user.id,user.id,request);return tokens_for(user,db,request)
@router.post('/login',response_model=TokenResponse)
@limiter.limit('5/minute')
def login(request:Request,payload:LoginRequest,db:Session=Depends(get_db)):
 user=ensure_development_admin(payload,db) or db.scalar(select(User).where(User.email==payload.email.lower(),User.deleted_at.is_(None)))
 if not user or not verify_password(payload.password,user.password_hash):raise HTTPException(401,'E-mail ou senha incorretos.')
 AuditService.record(db,'LOGIN','Session',user.id,None,request);return tokens_for(user,db,request)
@router.post('/refresh',response_model=TokenResponse)
@limiter.limit('20/minute')
def refresh(request:Request,payload:RefreshRequest,db:Session=Depends(get_db)):
 record=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==hash_token(payload.refresh_token)).with_for_update());now=datetime.now(timezone.utc)
 if not record:raise HTTPException(401,'Sessão inválida.')
 expiry=record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
 if record.revoked_at or expiry<=now:
  if record.revoked_at:
   for item in db.scalars(select(RefreshToken).where(RefreshToken.user_id==record.user_id,RefreshToken.revoked_at.is_(None))):item.revoked_at=now
   db.commit()
  raise HTTPException(401,'Sessão expirada ou revogada.')
 record.revoked_at=now;record.last_used_at=now;db.commit();user=db.get(User,record.user_id)
 if not user or user.deleted_at:raise HTTPException(401,'Sessão inválida.')
 return tokens_for(user,db,request,record.id)
@router.get('/me',response_model=UserResponse)
def me(user:User=Depends(current_user),db:Session=Depends(get_db)):
 is_admin=bool(db.scalar(select(UserRole.id).join(Role,Role.id==UserRole.role_id).where(UserRole.user_id==user.id,Role.name=='ADMIN')))
 return UserResponse(id=str(user.id),name=user.name,email=user.email,crm=user.crm,crm_uf=user.crm_uf,specialty=user.specialty,city=user.city,state=user.state,is_admin=is_admin)
@router.post('/logout',status_code=204)
def logout(request:Request,payload:LogoutRequest,db:Session=Depends(get_db)):
 record=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==hash_token(payload.refresh_token)))
 if record and not record.revoked_at:record.revoked_at=datetime.now(timezone.utc);db.commit();AuditService.record(db,'LOGOUT','Session',record.user_id,record.id,request)
 return Response(status_code=204)
@router.post('/logout-all',status_code=204)
def logout_all(request:Request,user:User=Depends(current_user),db:Session=Depends(get_db)):
 now=datetime.now(timezone.utc)
 for item in db.scalars(select(RefreshToken).where(RefreshToken.user_id==user.id,RefreshToken.revoked_at.is_(None))):item.revoked_at=now
 db.commit();AuditService.record(db,'LOGOUT_ALL','Session',user.id,None,request);return Response(status_code=204)
@router.get('/sessions',response_model=list[SessionResponse])
def sessions(user:User=Depends(current_user),db:Session=Depends(get_db)):
 items=db.scalars(select(RefreshToken).where(RefreshToken.user_id==user.id,RefreshToken.revoked_at.is_(None),RefreshToken.expires_at>datetime.now(timezone.utc)).order_by(RefreshToken.created_at.desc()));return [SessionResponse(id=str(x.id),ip_address=x.ip_address,user_agent=x.user_agent,session_name=x.session_name,last_used_at=x.last_used_at.isoformat() if x.last_used_at else None,expires_at=x.expires_at.isoformat()) for x in items]
@router.delete('/sessions/{session_id}',status_code=204)
def revoke_session(session_id:uuid.UUID,request:Request,user:User=Depends(current_user),db:Session=Depends(get_db)):
 item=db.scalar(select(RefreshToken).where(RefreshToken.id==session_id,RefreshToken.user_id==user.id))
 if not item:raise HTTPException(404,'Sessão não encontrada.')
 item.revoked_at=datetime.now(timezone.utc);db.commit();AuditService.record(db,'REVOKE_SESSION','Session',user.id,item.id,request);return Response(status_code=204)
@router.post('/forgot-password',status_code=204)
def forgot_password(payload:ForgotPasswordRequest,db:Session=Depends(get_db)):
 user=db.scalar(select(User).where(User.email==payload.email.lower(),User.deleted_at.is_(None)))
 if user:request_password_reset(user)
 return None
@router.post('/reset-password',status_code=204)
def reset_password(_:ResetPasswordRequest):return None
