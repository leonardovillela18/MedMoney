import uuid
from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,Field,model_validator

IncomeType=Literal['CLT','RESIDENCY_GRANT','RESEARCH_GRANT','ACADEMIC_GRANT','PRO_LABORE','RENTAL_INCOME','PJ_RECURRING','OTHER']
TaxTreatment=Literal['PJ_TAXABLE','NON_PJ','CUSTOM']
Frequency=Literal['Semanal','Mensal','Trimestral','Semestral','Anual']
NON_PJ_TYPES={'CLT','RESIDENCY_GRANT','RESEARCH_GRANT','ACADEMIC_GRANT','PRO_LABORE','RENTAL_INCOME'}
class RecurringIncomeInput(BaseModel):
    description:str=Field(min_length=2,max_length=160);income_type:IncomeType;amount:Decimal=Field(gt=0);frequency:Frequency;start_date:date;end_date:date|None=None;day_of_month:int|None=Field(None,ge=1,le=31);tax_treatment:TaxTreatment='NON_PJ';tax_reserve_percentage:Decimal|None=Field(None,ge=0,le=100);active:bool=True;notes:str|None=Field(None,max_length=2000)
    @model_validator(mode='after')
    def validate_rule(self):
        if self.end_date and self.end_date<self.start_date:raise ValueError('A data final deve ser posterior à inicial.')
        if self.income_type in NON_PJ_TYPES and self.tax_treatment!='NON_PJ':raise ValueError('Este tipo não entra na reserva tributária PJ.')
        if self.tax_treatment=='PJ_TAXABLE' and self.tax_reserve_percentage is not None and not 0<=self.tax_reserve_percentage<=100:raise ValueError('Percentual inválido.')
        return self
class RecurringIncomeResponse(RecurringIncomeInput):
    id:uuid.UUID;user_id:uuid.UUID;next_occurrence_date:date;created_at:datetime;updated_at:datetime
    model_config={'from_attributes':True}
class RecurringIncomePage(BaseModel):items:list[RecurringIncomeResponse];total:int;page:int;page_size:int
