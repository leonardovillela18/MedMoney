import uuid
from datetime import datetime
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.financial_insight import InsightPage,InsightResponse
from app.services.insights import FinancialInsightsService
router=APIRouter(prefix='/insights',tags=['Financial Intelligence Engine'])
@router.get('',response_model=InsightPage)
def insights(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),categoria:str|None=None,severidade:str|None=None,status:str|None=None,date_from:datetime|None=None,date_to:datetime|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=FinancialInsightsService(db).list(user.id,page,page_size,locals());return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/dashboard')
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):return FinancialInsightsService(db).dashboard(user.id)
@router.post('/recalculate')
def recalculate(user:User=Depends(current_user),db:Session=Depends(get_db)):return {'updated':FinancialInsightsService(db).recalculate(user.id)}
@router.get('/{id}',response_model=InsightResponse)
def detail(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return FinancialInsightsService(db).get(user.id,id)
