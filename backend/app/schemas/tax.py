import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
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
class SettingInput(BaseModel):
    simples_nacional:bool|None=None
    simples_annex:Literal['III','V','OTHER','UNKNOWN']='UNKNOWN'
    fator_r:Decimal|None=Field(None,ge=0,le=100)
    rbt12:Decimal|None=Field(None,ge=0)
    das_effective_percentage:Decimal|None=Field(None,ge=0,le=100)
    iss_effective_percentage:Decimal|None=Field(None,ge=0,le=100)
    has_separate_darfs:bool=False
    separate_darfs:list[Literal['IRRF','INSS','CSLL','PIS','COFINS','OUTRO']]=Field(default_factory=list)
    recommended_reserve_percentage:Decimal=Field(default=15,ge=0,le=100)
    effective_from:date|None=None
    accountant_notes:str|None=Field(None,max_length=4000)
