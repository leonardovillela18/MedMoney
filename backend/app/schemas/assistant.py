import re,uuid
from datetime import datetime
from pydantic import BaseModel,EmailStr,Field,field_validator

class AssistantInput(BaseModel):
 name:str=Field(min_length=3,max_length=120);email:EmailStr;phone:str=Field(min_length=10,max_length=30);password:str|None=Field(default=None,min_length=8,max_length=128)
 @field_validator('password')
 @classmethod
 def strong_password(cls,value):
  if value and (not re.search('[A-Z]',value) or not re.search('[0-9]',value) or not re.search('[^A-Za-z0-9]',value)):raise ValueError('Use letra maiúscula, número e caractere especial.')
  return value
class AssistantCreate(AssistantInput):
 password:str=Field(min_length=8,max_length=128)
class AssistantResponse(BaseModel):
 id:uuid.UUID;name:str;email:EmailStr;phone:str;active:bool;created_at:datetime
