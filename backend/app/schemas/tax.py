import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

TYPES={'ISS','IRPJ','CSLL','PIS','COFINS','INSS','Outro'}
STATUSES={'Estimado','Reservado','Pago','Ignorado'}
class TaxInput(BaseModel):
    shift_id:uuid.UUID|None=None;invoice_id:uuid.UUID|None=None;receivable_id:uuid.UUID|None=None
    base_calculo:Decimal=Field(ge=0);percentual:Decimal=Field(ge=0,le=100);tipo:str='Outro';competencia:date;status:str='Estimado';observacoes:str|None=None
class TaxUpdate(BaseModel):
    percentual:Decimal|None=Field(None,ge=0,le=100);tipo:str|None=None;competencia:date|None=None;status:str|None=None;observacoes:str|None=None
class TaxResponse(TaxInput):
    id:uuid.UUID;valor_estimado:Decimal;created_at:datetime;updated_at:datetime
    model_config={'from_attributes':True}
class TaxPage(BaseModel):items:list[TaxResponse];total:int;page:int;page_size:int
class SimulationInput(BaseModel):receita:Decimal=Field(ge=0);percentual:Decimal=Field(ge=0,le=100)
class SettingInput(BaseModel):default_percentage:Decimal=Field(ge=0,le=100)
