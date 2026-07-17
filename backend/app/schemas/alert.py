import uuid
from datetime import datetime
from pydantic import BaseModel
class AlertResponse(BaseModel):
 id:uuid.UUID;tipo:str;categoria:str;titulo:str;descricao:str;prioridade:str;status:str;acao:str;url_destino:str;referencia_id:uuid.UUID;origem:str;lido_em:datetime|None;resolvido_em:datetime|None;created_at:datetime;updated_at:datetime
 model_config={'from_attributes':True}
class AlertPage(BaseModel):items:list[AlertResponse];total:int;page:int;page_size:int;unread:int
