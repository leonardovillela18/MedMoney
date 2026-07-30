import uuid
from fastapi import APIRouter,Depends,Query,Response
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.recurring_income import RecurringIncomeInput,RecurringIncomePage,RecurringIncomeResponse
from app.services.recurring_income_service import RecurringIncomeService

router=APIRouter(prefix='/recurring-incomes',tags=['Recebimentos Recorrentes'])
@router.get('',response_model=RecurringIncomePage)
def list_items(page:int=Query(1,ge=1),page_size:int=Query(50,ge=1,le=100),active:bool|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    items,total=RecurringIncomeService(db).list(user.id,page,page_size,active);return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.post('',response_model=RecurringIncomeResponse,status_code=201)
def create(payload:RecurringIncomeInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return RecurringIncomeService(db).create(user.id,payload.model_dump())
@router.get('/{item_id}',response_model=RecurringIncomeResponse)
def get(item_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return RecurringIncomeService(db).get(user.id,item_id)
@router.put('/{item_id}',response_model=RecurringIncomeResponse)
def update(item_id:uuid.UUID,payload:RecurringIncomeInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return RecurringIncomeService(db).update(user.id,item_id,payload.model_dump())
@router.post('/{item_id}/deactivate',response_model=RecurringIncomeResponse)
def deactivate(item_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return RecurringIncomeService(db).deactivate(user.id,item_id)
@router.delete('/{item_id}',status_code=204)
def delete(item_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):RecurringIncomeService(db).delete(user.id,item_id);return Response(status_code=204)
