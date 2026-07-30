import uuid
from datetime import date,datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select,update
from sqlalchemy.orm import Session
from app.models.receivable import Receivable
class ReceivableService:
 def __init__(self,db:Session):self.db=db
 def list(self,user,page,size,status=None,search=None,overdue=False):
  self.db.execute(update(Receivable).where(Receivable.user_id==user,Receivable.deleted_at.is_(None),Receivable.status=='A Receber',Receivable.expected_date<date.today(),Receivable.remaining_balance>0).values(status='Atrasado'));self.db.commit()
  q=select(Receivable).where(Receivable.user_id==user,Receivable.deleted_at.is_(None))
  if status:q=q.where(Receivable.status==status)
  if overdue:q=q.where(Receivable.status=='Atrasado')
  q=q.order_by(Receivable.expected_date.desc());return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
 def get(self,user,id):
  x=self.db.scalar(select(Receivable).where(Receivable.id==id,Receivable.user_id==user,Receivable.deleted_at.is_(None)))
  if not x:raise HTTPException(404,'Recebimento não encontrado.')
  if x.status=='A Receber' and x.expected_date<date.today():x.status='Atrasado';self.db.commit()
  return x
 def sync_shift(self,shift):
  x=self.db.scalar(select(Receivable).where(Receivable.user_id==shift.user_id,Receivable.shift_id==shift.id,Receivable.deleted_at.is_(None)))
  if not x:
   x=Receivable(user_id=shift.user_id,shift_id=shift.id,contractor_id=shift.contractor_id,received_value=Decimal(0));self.db.add(x)
  if x.received_value>0:return x
  x.contractor_id=shift.contractor_id;x.expected_value=shift.gross_value;x.remaining_balance=shift.gross_value;x.expected_date=shift.expected_payment_date or shift.date;x.competence=x.expected_date.replace(day=1);x.tax_treatment=getattr(shift,'tax_treatment','PJ_TAXABLE');x.tax_reserve_percentage=getattr(shift,'tax_reserve_percentage',None)
  x.status='Cancelado' if shift.status=='Cancelado' else 'Atrasado' if x.expected_date<date.today() else 'A Receber'
  self.db.commit();self.db.refresh(x);return x
 def receive(self,user,id,data):
  x=self.get(user,id)
  if x.status in ('Cancelado','Recebido'):raise HTTPException(422,'Este recebimento não pode receber pagamentos.')
  if data['value']>x.remaining_balance:raise HTTPException(422,'O valor é maior que o saldo restante.')
  if data['date']<x.expected_date.replace(year=x.expected_date.year) and data['date']>date.today():raise HTTPException(422,'Data de recebimento inválida.')
  x.received_value+=data['value'];x.remaining_balance-=data['value'];x.received_date=data['date'];x.receipt_method=data['method'];x.notes=data.get('notes') or x.notes;x.receipt_url=data.get('receipt_url') or x.receipt_url;x.status='Recebido' if x.remaining_balance==0 else 'Recebido Parcialmente';self.db.commit();self.db.refresh(x)
  if x.status=='Recebido':
   from app.models.shift import Shift
   shift=self.db.get(Shift,x.shift_id)
   if shift:shift.status='Recebido';self.db.commit()
  from app.services.tax_service import TaxService
  from app.models.shift import Shift
  shift=self.db.get(Shift,x.shift_id) if x.shift_id else None
  if x.tax_treatment!='NON_PJ':TaxService(self.db).sync(user,x.received_value,x.received_date,shift_id=x.shift_id,receivable_id=x.id,percentage=x.tax_reserve_percentage,tax_treatment=x.tax_treatment)
  from app.services.cashflow_service import CashflowService
  origin='Plantão' if x.shift_id else 'Recebimento Recorrente';origin_id=x.shift_id or x.id;description='Recebimento de plantão' if x.shift_id else 'Recebimento recorrente'
  cashflow=CashflowService(self.db);cashflow.sync_source(user,origin,origin_id,x.received_date,'Receita Recebida',description,'Recebimentos',x.received_value,'Confirmado');self.db.commit();cashflow.recalculate(user)
  if x.recurring_income_id:
   from app.services.recurring_income_service import RecurringIncomeService
   RecurringIncomeService(self.db).materialize_next(user,x.recurring_income_id)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user);return x
 def delete(self,user,id):x=self.get(user,id);x.deleted_at=datetime.now(timezone.utc);self.db.commit()
