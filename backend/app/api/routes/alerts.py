import uuid
from datetime import datetime
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.alert import AlertPage,AlertResponse
from app.services.alerts import AlertEngine
router=APIRouter(prefix='/alerts',tags=['Central Inteligente de Alertas'])
@router.get('',response_model=AlertPage)
def alerts(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),categoria:str|None=None,prioridade:str|None=None,status:str|None=None,origem:str|None=None,date_from:datetime|None=None,date_to:datetime|None=None,search:str|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total,unread=AlertEngine(db).list(user.id,page,page_size,locals());return {'items':items,'total':total,'page':page,'page_size':page_size,'unread':unread}
@router.get('/dashboard')
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):return AlertEngine(db).dashboard(user.id)
@router.post('/recalculate')
def recalculate(user:User=Depends(current_user),db:Session=Depends(get_db)):return AlertEngine(db).recalculate(user.id)
@router.get('/{id}',response_model=AlertResponse)
def detail(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return AlertEngine(db).get(user.id,id)
@router.patch('/{id}/read',response_model=AlertResponse)
def read(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return AlertEngine(db).mark_read(user.id,id)
@router.patch('/{id}/resolve',response_model=AlertResponse)
def resolve(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return AlertEngine(db).resolve(user.id,id)
