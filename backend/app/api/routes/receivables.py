import uuid
from fastapi import APIRouter,Depends,Query,Response
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.receivable import ReceivablePage,ReceivableResponse,ReceiveRequest
from app.services.receivable_service import ReceivableService
router=APIRouter(prefix='/receivables',tags=['Recebimentos'])
@router.get('',response_model=ReceivablePage)
def list_receivables(page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),status:str|None=None,search:str|None=None,overdue:bool=False,user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=ReceivableService(db).list(user.id,page,page_size,status,search,overdue);return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/{id}',response_model=ReceivableResponse)
def get_receivable(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return ReceivableService(db).get(user.id,id)
@router.post('/{id}/receive',response_model=ReceivableResponse)
def receive(id:uuid.UUID,payload:ReceiveRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):return ReceivableService(db).receive(user.id,id,payload.model_dump())
@router.delete('/{id}',status_code=204)
def delete(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):ReceivableService(db).delete(user.id,id);return Response(status_code=204)
