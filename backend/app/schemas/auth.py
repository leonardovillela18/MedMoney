from pydantic import BaseModel, EmailStr, Field, field_validator
from app.auth.security import validate_password_strength
class RegisterRequest(BaseModel):
    name:str=Field(min_length=3,max_length=120); crm:str=Field(min_length=3,max_length=30); crm_uf:str=Field(min_length=2,max_length=2); email:EmailStr; password:str; cnpj:str=Field(min_length=14,max_length=18); phone:str=Field(min_length=10,max_length=30); city:str=Field(min_length=2,max_length=100); state:str=Field(min_length=2,max_length=2); specialty:str=Field(min_length=2,max_length=100)
    @field_validator('password')
    @classmethod
    def strong_password(cls,v:str):
        return validate_password_strength(v)
    @field_validator('state','crm_uf')
    @classmethod
    def valid_state(cls,v:str):
        from app.services.location_service import validate_state
        return validate_state(v)
class LoginRequest(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class TokenResponse(BaseModel): access_token:str; refresh_token:str; token_type:str='bearer'
class RefreshRequest(BaseModel): refresh_token:str=Field(min_length=20,max_length=500)
class LogoutRequest(RefreshRequest): reason:str|None=Field(None,pattern='^idle$')
class SessionResponse(BaseModel):
    id:str; ip_address:str|None; user_agent:str|None; session_name:str|None; last_used_at:str|None; expires_at:str; current:bool=False
class UserResponse(BaseModel):
    id:str; name:str; email:EmailStr; crm:str; crm_uf:str; specialty:str; city:str; state:str; is_admin:bool=False; is_assistant:bool=False; doctor_name:str|None=None
    model_config={'from_attributes':True}
class ForgotPasswordRequest(BaseModel): email:EmailStr
class ResetPasswordRequest(BaseModel):
    token:str=Field(min_length=32,max_length=500)
    password:str
    _password=field_validator('password')(validate_password_strength)
class ChangePasswordRequest(BaseModel):
    current_password:str=Field(min_length=1,max_length=128)
    new_password:str
    _password=field_validator('new_password')(validate_password_strength)
class PublicMessage(BaseModel):message:str
