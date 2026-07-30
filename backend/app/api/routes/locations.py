from fastapi import APIRouter,Depends,Query
from app.api.dependencies import current_user
from app.models.user import User
from app.services.location_service import STATES,municipalities,normalize_text,validate_state
router=APIRouter(prefix='/locations',tags=['Localidades'])
@router.get('/states')
def states(_:User=Depends(current_user)):return [{'uf':uf,'name':name} for uf,name in STATES.items()]
@router.get('/cities')
def cities(state:str,search:str='',limit:int=Query(50,ge=1,le=100),_:User=Depends(current_user)):
    uf=validate_state(state);term=normalize_text(search);items=[x for x in municipalities() if x['state']==uf and (not term or term in x['normalized_name'])][:limit];return [{'ibge_code':x['ibge_code'],'name':x['name'],'state':x['state']} for x in items]
