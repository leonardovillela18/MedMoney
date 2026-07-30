from datetime import datetime, timedelta, timezone
import hashlib, secrets, jwt
import re
from passlib.context import CryptContext
from app.core.config import get_settings
pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto'); settings=get_settings()
def hash_password(value:str)->str:return pwd_context.hash(value)
def verify_password(value:str,hashed:str)->bool:return pwd_context.verify(value,hashed)
def create_access_token(subject:str,role:str='USER')->str:return jwt.encode({'sub':subject,'role':role,'type':'access','iat':datetime.now(timezone.utc),'exp':datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)},settings.jwt_secret_key,algorithm='HS256')
def create_refresh_token()->tuple[str,str,datetime]:
    token=secrets.token_urlsafe(48); expiry=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days); return token,hashlib.sha256(token.encode()).hexdigest(),expiry
def decode_access_token(token:str)->str:
    payload=jwt.decode(token,settings.jwt_secret_key,algorithms=['HS256'])
    if payload.get('type')!='access' or not payload.get('sub'): raise jwt.InvalidTokenError
    return payload['sub']
def hash_token(token:str)->str:return hashlib.sha256(token.encode()).hexdigest()
def validate_password_strength(value:str)->str:
    if len(value)<8 or len(value)>128 or not re.search('[A-Z]',value) or not re.search('[0-9]',value) or not re.search('[^A-Za-z0-9]',value):raise ValueError('A senha não atende aos requisitos de segurança.')
    return value
