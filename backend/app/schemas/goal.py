import uuid
from datetime import date,datetime
from decimal import Decimal
from pydantic import BaseModel,Field,model_validator
GOAL_TYPES={'Receita Mensal','Receita Anual','Lucro Líquido','Quantidade de Plantões','Horas Trabalhadas','Valor por Hora','Reserva Tributária','Economia','Despesas Máximas','Recebimentos','Meta Personalizada'}
class GoalInput(BaseModel):
 titulo:str=Field(min_length=2,max_length=160);descricao:str|None=None;tipo:str;valor_meta:Decimal=Field(gt=0);valor_atual:Decimal|None=Field(None,ge=0);data_inicio:date;data_final:date;cor:str='blue';icone:str='target'
 @model_validator(mode='after')
 def validate_goal(self):
  if self.tipo not in GOAL_TYPES:raise ValueError('Tipo de meta inválido.')
  if self.data_final<self.data_inicio:raise ValueError('A data final deve ser posterior ao início.')
  if self.tipo!='Meta Personalizada' and self.valor_atual is not None:raise ValueError('O valor atual é calculado automaticamente para este tipo de meta.')
  return self
class GoalResponse(BaseModel):
 id:uuid.UUID;titulo:str;descricao:str|None;tipo:str;valor_meta:Decimal;valor_atual:Decimal;percentual:Decimal;data_inicio:date;data_final:date;status:str;cor:str;icone:str;created_at:datetime;updated_at:datetime
 model_config={'from_attributes':True}
class GoalPage(BaseModel):items:list[GoalResponse];total:int;page:int;page_size:int
class GoalSimulation(BaseModel):goal_id:uuid.UUID;extra_shifts:int=Field(0,ge=0,le=100);shift_value:Decimal=Field(0,ge=0);extra_revenue:Decimal=Field(0,ge=0);expense_reduction:Decimal=Field(0,ge=0)
