import uuid,jwt
from fastapi import Depends,HTTPException,Request,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.security import decode_access_token
from app.database.session import get_db
from app.models.user import AssistantLink,User
bearer=HTTPBearer()
def current_user(request:Request,credentials:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db))->User:
 try:user_id=uuid.UUID(decode_access_token(credentials.credentials))
 except (jwt.PyJWTError,ValueError):raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Sessão inválida. Entre novamente.')
 user=db.get(User,user_id)
 if not user or user.deleted_at:raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Sessão inválida. Entre novamente.')
 link=db.scalar(select(AssistantLink).where(AssistantLink.assistant_id==user.id))
 request.state.user_id=str(user.id);request.state.is_assistant=bool(link);request.state.owner_id=str(link.doctor_id) if link else str(user.id)
 if link and not any(request.url.path.startswith(prefix) for prefix in ('/api/v1/auth','/api/v1/contractors','/api/v1/shifts','/api/v1/assistant-dashboard')):
  raise HTTPException(status_code=403,detail='A auxiliar não possui acesso às informações financeiras.')
 return user

def operational_user(request:Request,user:User=Depends(current_user),db:Session=Depends(get_db))->User:
 owner_id=getattr(request.state,'owner_id',str(user.id))
 return db.get(User,uuid.UUID(owner_id)) or user
