import uuid
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException,Response,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.auth.security import hash_password
from app.database.session import get_db
from app.models.enterprise import Role,UserRole
from app.models.user import AssistantLink,RefreshToken,User
from app.schemas.assistant import AssistantCreate,AssistantInput,AssistantResponse

router=APIRouter(prefix='/assistants',tags=['Auxiliares'])
def ensure_doctor(user,db):
 if db.scalar(select(AssistantLink.id).where(AssistantLink.assistant_id==user.id)):raise HTTPException(403,'Apenas o médico pode gerenciar auxiliares.')
def response(user):return AssistantResponse(id=user.id,name=user.name,email=user.email,phone=user.phone,active=user.deleted_at is None,created_at=user.created_at)
@router.get('',response_model=list[AssistantResponse])
def list_items(user:User=Depends(current_user),db:Session=Depends(get_db)):
 ensure_doctor(user,db);ids=select(AssistantLink.assistant_id).where(AssistantLink.doctor_id==user.id);return [response(x) for x in db.scalars(select(User).where(User.id.in_(ids)).order_by(User.created_at.desc()))]
@router.post('',response_model=AssistantResponse,status_code=status.HTTP_201_CREATED)
def create(payload:AssistantCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
 ensure_doctor(user,db);email=payload.email.lower()
 if db.scalar(select(User.id).where(User.email==email)):raise HTTPException(409,'Já existe um usuário com este e-mail.')
 marker=uuid.uuid4().hex
 item=User(name=payload.name,email=email,password_hash=hash_password(payload.password),phone=payload.phone,crm=f'AUX-{marker[:8]}',crm_uf=user.crm_uf,cnpj=marker[:14],city=user.city,state=user.state,specialty='Auxiliar médica')
 db.add(item);db.flush();db.add(AssistantLink(assistant_id=item.id,doctor_id=user.id));role=db.scalar(select(Role).where(Role.name=='ASSISTENTE'))
 if role:db.add(UserRole(user_id=item.id,role_id=role.id))
 db.commit();db.refresh(item);return response(item)
@router.put('/{assistant_id}',response_model=AssistantResponse)
def update(assistant_id:uuid.UUID,payload:AssistantInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
 link=db.scalar(select(AssistantLink).where(AssistantLink.assistant_id==assistant_id,AssistantLink.doctor_id==user.id));item=db.get(User,assistant_id)
 if not link or not item:raise HTTPException(404,'Auxiliar não encontrada.')
 conflict=db.scalar(select(User.id).where(User.email==payload.email.lower(),User.id!=assistant_id))
 if conflict:raise HTTPException(409,'Já existe um usuário com este e-mail.')
 item.name=payload.name;item.email=payload.email.lower();item.phone=payload.phone
 if payload.password:item.password_hash=hash_password(payload.password)
 db.commit();db.refresh(item);return response(item)
@router.patch('/{assistant_id}/status',response_model=AssistantResponse)
def status_change(assistant_id:uuid.UUID,active:bool,user:User=Depends(current_user),db:Session=Depends(get_db)):
 link=db.scalar(select(AssistantLink).where(AssistantLink.assistant_id==assistant_id,AssistantLink.doctor_id==user.id));item=db.get(User,assistant_id)
 if not link or not item:raise HTTPException(404,'Auxiliar não encontrada.')
 item.deleted_at=None if active else datetime.now(timezone.utc)
 if not active:
  for token in db.scalars(select(RefreshToken).where(RefreshToken.user_id==item.id,RefreshToken.revoked_at.is_(None))):token.revoked_at=datetime.now(timezone.utc)
 db.commit();db.refresh(item);return response(item)
