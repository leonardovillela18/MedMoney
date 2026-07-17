import uuid
from fastapi import APIRouter,Depends,Query,Response
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.goal import GoalInput,GoalPage,GoalResponse,GoalSimulation
from app.services.goal_service import GoalService
from app.services.insights.events import refresh_insights
router=APIRouter(prefix='/goals',tags=['Metas Financeiras Inteligentes'])
@router.get('',response_model=GoalPage)
def goals(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),status:str|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=GoalService(db).list(user.id,page,page_size,status);return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/dashboard')
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):return GoalService(db).dashboard(user.id)
@router.post('/simulate')
def simulate(payload:GoalSimulation,user:User=Depends(current_user),db:Session=Depends(get_db)):return GoalService(db).simulate(user.id,payload.model_dump())
@router.get('/{id}')
def detail(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return GoalService(db).detail(user.id,id)
@router.post('',response_model=GoalResponse,status_code=201)
def create(payload:GoalInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
 x=GoalService(db).create(user.id,payload.model_dump());refresh_insights(db,user.id);return x
@router.put('/{id}',response_model=GoalResponse)
def update(id:uuid.UUID,payload:GoalInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
 x=GoalService(db).update(user.id,id,payload.model_dump());refresh_insights(db,user.id);return x
@router.delete('/{id}',status_code=204)
def delete(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):GoalService(db).delete(user.id,id);refresh_insights(db,user.id);return Response(status_code=204)
