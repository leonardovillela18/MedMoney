import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.shift import ShiftCreate, ShiftPage, ShiftResponse, ShiftUpdate
from app.services.shift_service import ShiftService
router=APIRouter(prefix='/shifts',tags=['Plantões'])
@router.get('',response_model=ShiftPage)
def list_shifts(page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),search:str|None=None,contractor_id:uuid.UUID|None=None,city:str|None=None,specialty:str|None=None,status:str|None=None,type:str|None=None,date_from:date|None=None,date_to:date|None=None,min_value:Decimal|None=None,max_value:Decimal|None=None,order:str='recent',user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=ShiftService(db).list(user.id,page,page_size,locals());return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/calendar',response_model=list[ShiftResponse])
def calendar(start:date,end:date,user:User=Depends(current_user),db:Session=Depends(get_db)):
 return ShiftService(db).list(user.id,1,1000,{'date_from':start,'date_to':end,'order':'recent'})[0]
@router.get('/{shift_id}',response_model=ShiftResponse)
def get_shift(shift_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return ShiftService(db).get(user.id,shift_id)
@router.post('',response_model=ShiftResponse,status_code=201)
def create_shift(payload:ShiftCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):return ShiftService(db).create(user.id,payload.model_dump())
@router.put('/{shift_id}',response_model=ShiftResponse)
def update_shift(shift_id:uuid.UUID,payload:ShiftUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):return ShiftService(db).update(user.id,shift_id,payload.model_dump())
@router.delete('/{shift_id}',status_code=204)
def delete_shift(shift_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):ShiftService(db).delete(user.id,shift_id);return Response(status_code=204)
