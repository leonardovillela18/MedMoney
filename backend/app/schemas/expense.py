import uuid
from datetime import date,datetime
from decimal import Decimal
from pydantic import BaseModel,Field,model_validator
class CategoryInput(BaseModel):nome:str=Field(min_length=2,max_length=80);cor:str='slate'
class CategoryResponse(CategoryInput):id:uuid.UUID;ativa:bool;model_config={'from_attributes':True}
class ExpenseInput(BaseModel):
 titulo:str=Field(min_length=2,max_length=160);descricao:str|None=None;categoria_id:uuid.UUID;valor:Decimal=Field(gt=0);tipo:str;forma_pagamento:str;fornecedor:str|None=None;competencia:date;data_vencimento:date;data_pagamento:date|None=None;status:str='Pendente';recorrente:bool=False;intervalo_recorrencia:str|None=None;centro_custo:str|None=None;observacoes:str|None=None;comprovante_url:str|None=None
 @model_validator(mode='after')
 def recurrence(self):
  if self.recorrente and not self.intervalo_recorrencia:raise ValueError('Informe o intervalo de recorrência.')
  return self
class ExpenseResponse(ExpenseInput):
 id:uuid.UUID;recurrence_parent_id:uuid.UUID|None=None;created_at:datetime;updated_at:datetime
 model_config={'from_attributes':True}
class ExpensePage(BaseModel):items:list[ExpenseResponse];total:int;page:int;page_size:int
