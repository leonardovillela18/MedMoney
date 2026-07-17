from fastapi import Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.enterprise import Permission,Role,RolePermission,UserRole
def require_roles(*allowed):
 def policy(user=Depends(current_user),db:Session=Depends(get_db)):
  roles=set(db.scalars(select(Role.name).join(UserRole,UserRole.role_id==Role.id).where(UserRole.user_id==user.id)))
  if not roles.intersection(allowed):raise HTTPException(403,'Você não possui permissão para esta operação.')
  return user
 return policy
def require_permission(name):
 def policy(user=Depends(current_user),db:Session=Depends(get_db)):
  permitted=db.scalar(select(Permission.id).join(RolePermission,RolePermission.permission_id==Permission.id).join(UserRole,UserRole.role_id==RolePermission.role_id).where(UserRole.user_id==user.id,Permission.name==name))
  if not permitted:raise HTTPException(403,'Você não possui permissão para esta operação.')
  return user
 return policy
