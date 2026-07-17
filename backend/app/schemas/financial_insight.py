import uuid
from datetime import datetime
from pydantic import BaseModel
class InsightResponse(BaseModel):
 id:uuid.UUID;tipo:str;titulo:str;descricao:str;categoria:str;severidade:str;status:str;prioridade:int;acao_recomendada:str;referencia:str;created_at:datetime;updated_at:datetime;dismissed_at:datetime|None
 model_config={'from_attributes':True}
class InsightPage(BaseModel):items:list[InsightResponse];total:int;page:int;page_size:int
