import uuid
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session
from app.api.dependencies import operational_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.contractor import ContractorCreate, ContractorPage, ContractorResponse, ContractorUpdate
from app.services.contractor_service import ContractorService
router=APIRouter(prefix='/contractors',tags=['Contratantes'])
def safe(item,request):
 data=ContractorResponse.model_validate(item)
 return data.model_copy(update={'default_shift_value':None,'payment_day':None,'payment_term_days':None}) if getattr(request.state,'is_assistant',False) else data
@router.get('',response_model=ContractorPage)
def list_contractors(request:Request,page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),search:str|None=None,city:str|None=None,type:str|None=None,active:bool|None=None,order:str='name',user:User=Depends(operational_user),db:Session=Depends(get_db)):
    items,total=ContractorService(db).list(user.id,page,page_size,search,city,type,active,order);return {'items':[safe(x,request) for x in items],'total':total,'page':page,'page_size':page_size}
@router.get('/{contractor_id}',response_model=ContractorResponse)
def get_contractor(request:Request,contractor_id:uuid.UUID,user:User=Depends(operational_user),db:Session=Depends(get_db)): return safe(ContractorService(db).get(user.id,contractor_id),request)
@router.post('',response_model=ContractorResponse,status_code=status.HTTP_201_CREATED)
def create_contractor(payload:ContractorCreate,user:User=Depends(operational_user),db:Session=Depends(get_db)): return ContractorService(db).create(user.id,payload.model_dump())
@router.put('/{contractor_id}',response_model=ContractorResponse)
def update_contractor(contractor_id:uuid.UUID,payload:ContractorUpdate,user:User=Depends(operational_user),db:Session=Depends(get_db)): return ContractorService(db).update(user.id,contractor_id,payload.model_dump())
@router.delete('/{contractor_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_contractor(contractor_id:uuid.UUID,user:User=Depends(operational_user),db:Session=Depends(get_db)): ContractorService(db).delete(user.id,contractor_id);return Response(status_code=204)
