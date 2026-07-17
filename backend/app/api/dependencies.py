import uuid,jwt
from fastapi import Depends,HTTPException,Request,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy.orm import Session
from app.auth.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
bearer=HTTPBearer()
def current_user(request:Request,credentials:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db))->User:
 try:user_id=uuid.UUID(decode_access_token(credentials.credentials))
 except (jwt.PyJWTError,ValueError):raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Sessão inválida. Entre novamente.')
 user=db.get(User,user_id)
 if not user or user.deleted_at:raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Sessão inválida. Entre novamente.')
 request.state.user_id=str(user.id);return user
