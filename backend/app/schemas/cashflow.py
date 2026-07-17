from datetime import date,datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel,Field
class CashflowResponse(BaseModel):
 id:uuid.UUID;data:date;tipo:str;origem:str;origem_id:uuid.UUID;descricao:str;categoria:str;valor:Decimal;saldo_projetado:Decimal;status:str;created_at:datetime;updated_at:datetime
 model_config={'from_attributes':True}
class CashflowPage(BaseModel):items:list[CashflowResponse];total:int;page:int;page_size:int
class CashflowSimulation(BaseModel):
 delayed_origin_id:uuid.UUID|None=None;delay_days:int=Field(0,ge=0,le=365);extra_shifts:int=Field(0,ge=0,le=100);shift_value:Decimal=Field(0,ge=0);extra_expenses:Decimal=Field(0,ge=0);horizon_days:int=Field(90,ge=7,le=365)
