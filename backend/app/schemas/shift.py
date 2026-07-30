from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
import uuid
from pydantic import BaseModel, Field, model_validator
ShiftStatus=Literal['Agendado','Realizado','Recebido','Cancelado','Atrasado']; ShiftType=Literal['Plantão Presencial','Plantão Sobreaviso','Telemedicina','Consulta','Cirurgia','Outro']
class ShiftBase(BaseModel):
    contractor_id:uuid.UUID; title:str|None=Field(default=None,max_length=160); type:ShiftType;specialty_id:uuid.UUID|None=None;specialty:str|None=None; hospital_sector:str|None=None; city:str|None=None;city_ibge_code:str|None=None;state:str|None=Field(default=None,max_length=30); date:date; start_time:time; end_time:time; duration_hours:Decimal|None=Field(default=None,gt=0); gross_value:Decimal=Field(ge=0); estimated_net_value:Decimal|None=Field(default=None,ge=0); tax_reserve_percentage:Decimal|None=Field(default=None,ge=0,le=100);tax_treatment:Literal['PJ_TAXABLE','NON_PJ','CUSTOM']='PJ_TAXABLE';status:ShiftStatus='Agendado'; payment_method:str|None=None; expected_payment_date:date|None=None; notes:str|None=Field(default=None,max_length=2000)
    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_time<=self.start_time: raise ValueError('A hora final deve ser maior que a hora inicial')
        if self.expected_payment_date and self.expected_payment_date<self.date: raise ValueError('A data prevista deve ser igual ou posterior ao plantão')
        return self
class ShiftCreate(ShiftBase): pass
class ShiftUpdate(ShiftBase): pass
class ShiftResponse(ShiftBase):
    id:uuid.UUID; created_at:datetime; updated_at:datetime
    model_config={'from_attributes':True}
class ShiftPage(BaseModel):items:list[ShiftResponse];total:int;page:int;page_size:int
