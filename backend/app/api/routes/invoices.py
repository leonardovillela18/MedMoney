import uuid
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException,Query,Response
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.invoice import Invoice
from app.models.shift import Shift
from app.models.user import User
from app.schemas.invoice import InvoiceInput,InvoicePage,InvoiceResponse
router=APIRouter(prefix='/invoices',tags=['Notas Fiscais'])
def owned(db,user,id):
 x=db.scalar(select(Invoice).where(Invoice.id==id,Invoice.user_id==user,Invoice.deleted_at.is_(None)))
 if not x:raise HTTPException(404,'Nota Fiscal não encontrada.')
 return x
@router.get('',response_model=InvoicePage)
def list_invoices(page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),status:str|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
 q=select(Invoice).where(Invoice.user_id==user.id,Invoice.deleted_at.is_(None));q=q.where(Invoice.status==status) if status else q;q=q.order_by(Invoice.competence.desc());return {'items':list(db.scalars(q.offset((page-1)*page_size).limit(page_size))),'total':db.scalar(select(func.count()).select_from(q.subquery())) or 0,'page':page,'page_size':page_size}
@router.get('/{id}',response_model=InvoiceResponse)
def get_invoice(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):return owned(db,user.id,id)
@router.post('',response_model=InvoiceResponse,status_code=201)
def create_invoice(data:InvoiceInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
 shift=db.scalar(select(Shift).where(Shift.id==data.shift_id,Shift.user_id==user.id,Shift.deleted_at.is_(None)))
 if not shift:raise HTTPException(422,'Plantão inválido.')
 x=Invoice(user_id=user.id,**data.model_dump());db.add(x);db.commit();db.refresh(x);return x
@router.put('/{id}',response_model=InvoiceResponse)
def update_invoice(id:uuid.UUID,data:InvoiceInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
 x=owned(db,user.id,id)
 for k,v in data.model_dump().items():setattr(x,k,v)
 db.commit();db.refresh(x);return x
@router.delete('/{id}',status_code=204)
def delete_invoice(id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):x=owned(db,user.id,id);x.deleted_at=datetime.now(timezone.utc);db.commit();return Response(status_code=204)
