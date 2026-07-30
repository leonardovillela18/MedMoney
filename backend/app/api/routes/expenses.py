import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter,Depends,File,HTTPException,Query,Response,UploadFile
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.expense import CategoryInput,CategoryResponse,ExpenseInput,ExpensePage,ExpenseResponse
from app.services.expense_service import ExpenseService
from app.infrastructure.storage import get_storage
router=APIRouter(prefix='/expenses',tags=['Gestão Inteligente de Despesas']);ALLOWED={'application/pdf':'.pdf','image/jpeg':'.jpg','image/png':'.png'};MAX_SIZE=5*1024*1024
@router.get('',response_model=ExpensePage)
def list_expenses(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),categoria_id:uuid.UUID|None=None,date_from:date|None=None,date_to:date|None=None,fornecedor:str|None=None,tipo:str|None=None,status:str|None=None,forma_pagamento:str|None=None,min_value:Decimal|None=None,max_value:Decimal|None=None,recorrente:bool|None=None,order:str='recent',user:User=Depends(current_user),db:Session=Depends(get_db)):
 items,total=ExpenseService(db).list(user.id,page,page_size,locals());return {'items':items,'total':total,'page':page,'page_size':page_size}
@router.get('/dashboard')
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).dashboard(user.id)
@router.get('/categories',response_model=list[CategoryResponse])
def categories(user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).categories(user.id)
@router.post('/categories',response_model=CategoryResponse,status_code=201)
def create_category(payload:CategoryInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).add_category(user.id,payload.model_dump())
@router.post('/upload')
async def upload_receipt(file:UploadFile=File(...),user:User=Depends(current_user)):
 if file.content_type not in ALLOWED:raise HTTPException(422,'Formato inválido. Envie PDF, JPG, JPEG ou PNG.')
 content=await file.read(MAX_SIZE+1)
 if len(content)>MAX_SIZE:raise HTTPException(422,'O comprovante deve ter no máximo 5 MB.')
 name=f'{user.id}-{uuid.uuid4()}{ALLOWED[file.content_type]}';get_storage().save(f'receipts/{name}',content);return {'url':f'/api/v1/expenses/receipts/{name}','ocr_status':'not_requested'}
@router.get('/receipts/{name}')
def receipt(name:str,user:User=Depends(current_user)):
 if not name.startswith(f'{user.id}-') or '/' in name or '\\' in name:raise HTTPException(404,'Comprovante não encontrado.')
 storage=get_storage();key=f'receipts/{name}'
 if not storage.exists(key):raise HTTPException(404,'Comprovante não encontrado.')
 media='application/pdf' if name.endswith('.pdf') else 'image/png' if name.endswith('.png') else 'image/jpeg';return Response(storage.read(key),media_type=media,headers={'Content-Disposition':f'inline; filename="{name}"'})
@router.get('/{id}',response_model=ExpenseResponse)
def get_expense(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).get(user.id,id)
@router.post('',response_model=ExpenseResponse,status_code=201)
def create_expense(payload:ExpenseInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).create(user.id,payload.model_dump())
@router.put('/{id}',response_model=ExpenseResponse)
def update_expense(id:uuid.UUID,payload:ExpenseInput,user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).update(user.id,id,payload.model_dump())
@router.post('/{id}/pay',response_model=ExpenseResponse)
def mark_expense_paid(id:uuid.UUID,payment_date:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):return ExpenseService(db).mark_paid(user.id,id,payment_date)
@router.delete('/{id}',status_code=204)
def delete_expense(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):ExpenseService(db).delete(user.id,id);return Response(status_code=204)
