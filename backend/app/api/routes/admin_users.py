import uuid
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import or_,select
from sqlalchemy.orm import Session
from app.api.policies import require_roles
from app.auth.security import hash_password
from app.database.session import get_db
from app.models.enterprise import Role,UserRole
from app.models.user import User
from app.schemas.admin_user import AdminUserCreate,AdminUserResponse,AdminUserUpdate

router=APIRouter(prefix='/admin/users',tags=['Administração de usuários'])
def response(user:User,db:Session):
 roles=set(db.scalars(select(Role.name).join(UserRole,UserRole.role_id==Role.id).where(UserRole.user_id==user.id)));role='ADMIN' if 'ADMIN' in roles else next(iter(roles),'USER')
 return AdminUserResponse(id=user.id,name=user.name,email=user.email,crm=user.crm,crm_uf=user.crm_uf,cnpj=user.cnpj,phone=user.phone,city=user.city,state=user.state,specialty=user.specialty,active=user.deleted_at is None,created_at=user.created_at,role=role)
@router.get('',response_model=list[AdminUserResponse])
def list_users(_:User=Depends(require_roles('ADMIN')),db:Session=Depends(get_db)):
 return [response(item,db) for item in db.scalars(select(User).order_by(User.created_at.desc()))]
@router.get('/{user_id}',response_model=AdminUserResponse)
def get_user(user_id:uuid.UUID,_:User=Depends(require_roles('ADMIN')),db:Session=Depends(get_db)):
 item=db.get(User,user_id)
 if not item:raise HTTPException(404,'Usuário não encontrado.')
 return response(item,db)
@router.post('',response_model=AdminUserResponse,status_code=status.HTTP_201_CREATED)
def create_user(payload:AdminUserCreate,_:User=Depends(require_roles('ADMIN')),db:Session=Depends(get_db)):
 email=payload.email.lower();existing=db.scalar(select(User).where(or_(User.email==email,User.cnpj==payload.cnpj)))
 if existing:raise HTTPException(409,'Já existe um usuário com este e-mail ou CNPJ.')
 item=User(**payload.model_dump(exclude={'password','email'}),email=email,password_hash=hash_password(payload.password));db.add(item);db.flush();role=db.scalar(select(Role).where(Role.name=='USER'))
 if role:db.add(UserRole(user_id=item.id,role_id=role.id))
 db.commit();db.refresh(item);return response(item,db)
@router.put('/{user_id}',response_model=AdminUserResponse)
def update_user(user_id:uuid.UUID,payload:AdminUserUpdate,_:User=Depends(require_roles('ADMIN')),db:Session=Depends(get_db)):
 item=db.get(User,user_id)
 if not item:raise HTTPException(404,'Usuário não encontrado.')
 conflict=db.scalar(select(User).where(User.id!=user_id,or_(User.email==payload.email.lower(),User.cnpj==payload.cnpj)))
 if conflict:raise HTTPException(409,'Já existe outro usuário com este e-mail ou CNPJ.')
 for key,value in payload.model_dump(exclude={'password'}).items():setattr(item,key,value.lower() if key=='email' else value)
 if payload.password:item.password_hash=hash_password(payload.password)
 db.commit();db.refresh(item);return response(item,db)
