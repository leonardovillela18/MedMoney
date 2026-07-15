from datetime import datetime, timedelta, timezone
import hashlib, secrets, jwt
from passlib.context import CryptContext
from app.core.config import get_settings
pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto'); settings=get_settings()
def hash_password(value:str)->str:return pwd_context.hash(value)
def verify_password(value:str,hashed:str)->bool:return pwd_context.verify(value,hashed)
def create_access_token(subject:str)->str:return jwt.encode({'sub':subject,'type':'access','exp':datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)},settings.jwt_secret_key,algorithm='HS256')
def create_refresh_token()->tuple[str,str,datetime]:
    token=secrets.token_urlsafe(48); expiry=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days); return token,hashlib.sha256(token.encode()).hexdigest(),expiry
def decode_access_token(token:str)->str:
    payload=jwt.decode(token,settings.jwt_secret_key,algorithms=['HS256'])
    if payload.get('type')!='access' or not payload.get('sub'): raise jwt.InvalidTokenError
    return payload['sub']
def hash_token(token:str)->str:return hashlib.sha256(token.encode()).hexdigest()
