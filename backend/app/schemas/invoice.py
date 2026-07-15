from datetime import date,datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel,Field
class InvoiceInput(BaseModel):
 shift_id:uuid.UUID;contractor_id:uuid.UUID;number:str=Field(min_length=1,max_length=60);series:str|None=None;verification_code:str|None=None;municipality:str|None=None;provider:str|None=None;customer:str|None=None;issue_date:date|None=None;competence:date;service_value:Decimal=Field(gt=0);net_value:Decimal|None=None;rate:Decimal|None=None;iss:Decimal|None=None;ir:Decimal|None=None;pis:Decimal|None=None;cofins:Decimal|None=None;csll:Decimal|None=None;inss:Decimal|None=None;status:str='Pendente';pdf_url:str|None=None;xml_url:str|None=None;notes:str|None=None
class InvoiceResponse(InvoiceInput):
 id:uuid.UUID;created_at:datetime;updated_at:datetime
 model_config={'from_attributes':True}
class InvoicePage(BaseModel):items:list[InvoiceResponse];total:int;page:int;page_size:int
