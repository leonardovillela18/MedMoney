from datetime import date,timedelta
from decimal import Decimal
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.cashflow import CashflowPage,CashflowSimulation
from app.services.cashflow_service import CashflowService
router=APIRouter(prefix='/cashflow',tags=['Fluxo de Caixa Inteligente'])
@router.get('',response_model=CashflowPage)
def cashflow(page:int=Query(1,ge=1),page_size:int=Query(50,ge=1,le=200),date_from:date|None=None,date_to:date|None=None,categoria:str|None=None,origem:str|None=None,tipo:str|None=None,status:str|None=None,min_value:Decimal|None=None,max_value:Decimal|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=CashflowService(db).list(user.id,page,page_size,locals());return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/projection')
def projection(days:int=Query(180,ge=7,le=365),user:User=Depends(current_user),db:Session=Depends(get_db)):return CashflowService(db).projection(user.id,days)
@router.get('/calendar')
def calendar(start:date|None=None,end:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 start=start or date.today().replace(day=1);end=end or start+timedelta(days=42);return CashflowService(db).calendar(user.id,start,end)
@router.post('/simulate')
def simulate(payload:CashflowSimulation,user:User=Depends(current_user),db:Session=Depends(get_db)):return CashflowService(db).simulate(user.id,payload.model_dump())
