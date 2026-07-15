import uuid
from datetime import date,datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.receivable import Receivable
class ReceivableService:
 def __init__(self,db:Session):self.db=db
 def list(self,user,page,size,status=None,search=None,overdue=False):
  q=select(Receivable).where(Receivable.user_id==user,Receivable.deleted_at.is_(None))
  if status:q=q.where(Receivable.status==status)
  if overdue:q=q.where(Receivable.status=='Atrasado')
  q=q.order_by(Receivable.expected_date.desc());return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
 def get(self,user,id):
  x=self.db.scalar(select(Receivable).where(Receivable.id==id,Receivable.user_id==user,Receivable.deleted_at.is_(None)))
  if not x:raise HTTPException(404,'Recebimento não encontrado.')
  if x.status=='A Receber' and x.expected_date<date.today():x.status='Atrasado';self.db.commit()
  return x
 def receive(self,user,id,data):
  x=self.get(user,id)
  if x.status in ('Cancelado','Recebido'):raise HTTPException(422,'Este recebimento não pode receber pagamentos.')
  if data['value']>x.remaining_balance:raise HTTPException(422,'O valor é maior que o saldo restante.')
  if data['date']<x.expected_date.replace(year=x.expected_date.year) and data['date']>date.today():raise HTTPException(422,'Data de recebimento inválida.')
  x.received_value+=data['value'];x.remaining_balance-=data['value'];x.received_date=data['date'];x.receipt_method=data['method'];x.notes=data.get('notes') or x.notes;x.receipt_url=data.get('receipt_url') or x.receipt_url;x.status='Recebido' if x.remaining_balance==0 else 'Recebido Parcialmente';self.db.commit();self.db.refresh(x);return x
 def delete(self,user,id):x=self.get(user,id);x.deleted_at=datetime.now(timezone.utc);self.db.commit()
