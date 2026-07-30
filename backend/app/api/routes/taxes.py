import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.tax import SettingInput, SimulationInput, TaxInput, TaxPage, TaxResponse, TaxUpdate
from app.services.tax_service import TaxService

router=APIRouter(prefix='/taxes',tags=['Inteligência Tributária'])
@router.get('',response_model=TaxPage)
def list_taxes(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),status:str|None=None,competence:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    items,total=TaxService(db).list(user.id,page,page_size,status,competence);return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.post('',response_model=TaxResponse,status_code=201)
def create_tax(payload:TaxInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return TaxService(db).create(user.id,payload.model_dump())
@router.get('/dashboard')
def tax_dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):return TaxService(db).dashboard(user.id)
@router.post('/simulate')
def simulate(payload:SimulationInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
    reserve,available=TaxService.calculate_reserve(payload.receita,payload.percentual);return {'receita':float(payload.receita),'percentual':float(payload.percentual),'reserva_sugerida':float(reserve),'disponivel_apos_reserva':float(available),'disclaimer':'Simulação informativa para planejamento. Não representa apuração tributária oficial.'}
@router.get('/settings')
def settings(user:User=Depends(current_user),db:Session=Depends(get_db)):return TaxService(db).setting(user.id)
@router.put('/settings')
def update_settings(payload:SettingInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return TaxService(db).save_setting(user.id,payload.model_dump())
@router.put('/{tax_id}',response_model=TaxResponse)
def update_tax(tax_id:uuid.UUID,payload:TaxUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):return TaxService(db).update(user.id,tax_id,payload.model_dump())
