from datetime import datetime
from decimal import Decimal
from typing import Literal
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
ContractorType=Literal['Hospital','Clínica','UPA','Santa Casa','Consultório','Prefeitura','Cooperativa','Empresa','Plano de Saúde','Outro']
class ContractorBase(BaseModel):
    name:str=Field(min_length=2,max_length=160); type:ContractorType; cnpj:str|None=None; email:EmailStr|None=None; phone:str|None=None; mobile:str|None=None; site:str|None=None
    zip_code:str|None=None; street:str|None=None; number:str|None=None; neighborhood:str|None=None; city:str|None=None; state:str|None=None; complement:str|None=None
    primary_contact:str|None=None; contact_role:str|None=None; contact_phone:str|None=None; contact_email:EmailStr|None=None; payment_day:str|None=None; payment_term_days:int|None=Field(default=None,gt=0); default_shift_value:Decimal|None=Field(default=None,ge=0); notes:str|None=Field(default=None,max_length=2000); active:bool=True
    @field_validator('cnpj')
    @classmethod
    def valid_cnpj(cls,value):
        if not value:return value
        digits=re.sub(r'\D','',value)
        if len(digits)!=14 or digits==digits[0]*14: raise ValueError('CNPJ inválido')
        def digit(base):
            weights=[5,4,3,2,9,8,7,6,5,4,3,2] if len(base)==12 else [6,5,4,3,2,9,8,7,6,5,4,3,2]
            total=sum(int(n)*w for n,w in zip(base,weights)); return '0' if total%11<2 else str(11-total%11)
        if digits[-2:]!=digit(digits[:12])+digit(digits[:13]): raise ValueError('CNPJ inválido')
        return digits
    @field_validator('phone','mobile','contact_phone')
    @classmethod
    def valid_phone(cls,value):
        if value and len(re.sub(r'\D','',value))<10: raise ValueError('Telefone inválido')
        return value
class ContractorCreate(ContractorBase): pass
class ContractorUpdate(ContractorBase): pass
class ContractorResponse(ContractorBase):
    id:uuid.UUID; created_at:datetime; updated_at:datetime
    model_config={'from_attributes':True}
class ContractorPage(BaseModel): items:list[ContractorResponse]; total:int; page:int; page_size:int
