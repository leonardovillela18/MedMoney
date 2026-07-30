from datetime import date,datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel,Field
class ReceiveRequest(BaseModel):value:Decimal=Field(gt=0);date:date;method:str;notes:str|None=None;receipt_url:str|None=None
class ReceivableResponse(BaseModel):
 id:uuid.UUID;user_id:uuid.UUID;shift_id:uuid.UUID|None;recurring_income_id:uuid.UUID|None=None;contractor_id:uuid.UUID|None;expected_value:Decimal;received_value:Decimal;remaining_balance:Decimal;expected_date:date;competence:date;tax_treatment:str;tax_reserve_percentage:Decimal|None;received_date:date|None;status:str;receipt_method:str|None;receipt_url:str|None;notes:str|None;created_at:datetime
 model_config={'from_attributes':True}
class ReceivablePage(BaseModel):items:list[ReceivableResponse];total:int;page:int;page_size:int
