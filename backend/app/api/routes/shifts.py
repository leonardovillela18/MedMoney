import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
from app.api.dependencies import operational_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.shift import ShiftCreate, ShiftPage, ShiftResponse, ShiftUpdate
from app.services.shift_service import ShiftService
router=APIRouter(prefix='/shifts',tags=['Plantões'])
def safe(item,request):
 data=ShiftResponse.model_validate(item)
 return data.model_copy(update={'gross_value':0,'estimated_net_value':0,'tax_reserve_percentage':None,'payment_method':None,'expected_payment_date':None}) if getattr(request.state,'is_assistant',False) else data
@router.get('',response_model=ShiftPage)
def list_shifts(request:Request,page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),search:str|None=None,contractor_id:uuid.UUID|None=None,city:str|None=None,specialty:str|None=None,status:str|None=None,type:str|None=None,date_from:date|None=None,date_to:date|None=None,min_value:Decimal|None=None,max_value:Decimal|None=None,order:str='recent',user:User=Depends(operational_user),db:Session=Depends(get_db)):
 items,total=ShiftService(db).list(user.id,page,page_size,locals());return {'items':[safe(x,request) for x in items],'total':total,'page':page,'page_size':page_size}
@router.get('/calendar',response_model=list[ShiftResponse])
def calendar(request:Request,start:date,end:date,user:User=Depends(operational_user),db:Session=Depends(get_db)):
 return [safe(x,request) for x in ShiftService(db).list(user.id,1,1000,{'date_from':start,'date_to':end,'order':'recent'})[0]]
@router.get('/{shift_id}',response_model=ShiftResponse)
def get_shift(request:Request,shift_id:uuid.UUID,user:User=Depends(operational_user),db:Session=Depends(get_db)):return safe(ShiftService(db).get(user.id,shift_id),request)
@router.post('',response_model=ShiftResponse,status_code=201)
def create_shift(request:Request,payload:ShiftCreate,user:User=Depends(operational_user),db:Session=Depends(get_db)):
 data=payload.model_dump()
 if getattr(request.state,'is_assistant',False):data.update(gross_value=0,estimated_net_value=0,payment_method=None,expected_payment_date=None)
 return safe(ShiftService(db).create(user.id,data),request)
@router.put('/{shift_id}',response_model=ShiftResponse)
def update_shift(request:Request,shift_id:uuid.UUID,payload:ShiftUpdate,user:User=Depends(operational_user),db:Session=Depends(get_db)):
 data=payload.model_dump()
 service=ShiftService(db)
 if getattr(request.state,'is_assistant',False):
  current=service.get(user.id,shift_id)
  data.update(gross_value=current.gross_value,estimated_net_value=current.estimated_net_value,tax_reserve_percentage=current.tax_reserve_percentage,tax_treatment=current.tax_treatment,payment_method=current.payment_method,expected_payment_date=current.expected_payment_date)
 return safe(service.update(user.id,shift_id,data),request)
@router.delete('/{shift_id}',status_code=204)
def delete_shift(shift_id:uuid.UUID,user:User=Depends(operational_user),db:Session=Depends(get_db)):ShiftService(db).delete(user.id,shift_id);return Response(status_code=204)
