import re
import uuid
from datetime import datetime
from pydantic import BaseModel,EmailStr,Field,field_validator

class AdminUserBase(BaseModel):
 name:str=Field(min_length=3,max_length=120);email:EmailStr;crm:str=Field(min_length=3,max_length=30);crm_uf:str=Field(min_length=2,max_length=2);cnpj:str=Field(min_length=14,max_length=18);phone:str=Field(min_length=10,max_length=30);city:str=Field(min_length=2,max_length=100);state:str=Field(min_length=2,max_length=2);specialty:str=Field(min_length=2,max_length=100)
class AdminUserCreate(AdminUserBase):
 password:str=Field(min_length=8,max_length=128)
 @field_validator('password')
 @classmethod
 def password_strength(cls,value):
  if not re.search('[A-Z]',value) or not re.search('[0-9]',value) or not re.search('[^A-Za-z0-9]',value):raise ValueError('Use letra maiúscula, número e caractere especial.')
  return value
class AdminUserUpdate(AdminUserBase):
 password:str|None=Field(default=None,min_length=8,max_length=128)
 @field_validator('password')
 @classmethod
 def password_strength(cls,value):
  if value and (not re.search('[A-Z]',value) or not re.search('[0-9]',value) or not re.search('[^A-Za-z0-9]',value)):raise ValueError('Use letra maiúscula, número e caractere especial.')
  return value
class AdminUserResponse(AdminUserBase):
 id:uuid.UUID;active:bool;created_at:datetime;role:str='USER'

