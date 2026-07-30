from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
from app.models.shift import Shift
from app.repositories.shift_repository import ShiftRepository
class ShiftService:
 def __init__(self,db:Session):self.db=db;self.repo=ShiftRepository(db)
 def list(self,*args):return self.repo.list(*args)
 def get(self,user,id):
  x=self.repo.get(user,id)
  if not x:raise HTTPException(404,'Plantão não encontrado.')
  return x
 def payload(self,user,data,current=None):
  if not self.db.get(Contractor,data['contractor_id']) or not self.db.scalar(__import__('sqlalchemy').select(Contractor).where(Contractor.id==data['contractor_id'],Contractor.user_id==user,Contractor.deleted_at.is_(None))):raise HTTPException(422,'Contratante inválido.')
  from app.services.location_service import validate_location
  if data.get('city') and not data.get('city_ibge_code') and not current:raise HTTPException(422,'Selecione uma cidade válida da lista.')
  if current and data.get('city')==current.city and not data.get('city_ibge_code'):data['city_ibge_code']=current.city_ibge_code
  if data.get('state') or data.get('city_ibge_code'):data['state'],data['city'],data['city_ibge_code']=validate_location(data.get('state'),data.get('city'),data.get('city_ibge_code'))
  if data.get('specialty_id'):
   from app.models.medical_specialty import MedicalSpecialty
   specialty=self.db.scalar(select(MedicalSpecialty).where(MedicalSpecialty.id==data['specialty_id'],MedicalSpecialty.active.is_(True)))
   if not specialty:raise HTTPException(422,'Especialidade inexistente ou inativa.')
   data['specialty']=specialty.name
  data['duration_hours']=data.get('duration_hours') or Decimal((datetime.combine(data['date'],data['end_time'])-datetime.combine(data['date'],data['start_time'])).seconds)/Decimal(3600);data['estimated_net_value']=current.estimated_net_value if current else data['gross_value']
  if data.get('tax_reserve_percentage') is None:
   data['tax_reserve_percentage']=current.tax_reserve_percentage if current else __import__('app.services.tax_service',fromlist=['TaxService']).TaxService(self.db).percentage(user)
  return data
 def create(self,user,data):
  x=self.repo.save(Shift(user_id=user,**self.payload(user,data)))
  from app.services.receivable_service import ReceivableService
  ReceivableService(self.db).sync_shift(x)
  from app.services.tax_service import TaxService
  TaxService(self.db).sync(user,x.gross_value,x.date,shift_id=x.id,percentage=x.tax_reserve_percentage,tax_treatment=x.tax_treatment)
  from app.services.cashflow_service import CashflowService
  cashflow=CashflowService(self.db);cashflow.sync_source(user,'Plantão',x.id,x.expected_payment_date or x.date,'Receita Prevista',x.title or x.type,'Plantões',x.gross_value);self.db.commit();cashflow.recalculate(user)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user);return x
 def update(self,user,id,data):
  x=self.get(user,id)
  from app.models.receivable import Receivable
  receivable=self.db.scalar(select(Receivable).where(Receivable.user_id==user,Receivable.shift_id==x.id,Receivable.deleted_at.is_(None)))
  payload=self.payload(user,data,x)
  if receivable and receivable.received_value>0 and (Decimal(payload['gross_value'])!=x.gross_value or payload.get('expected_payment_date')!=x.expected_payment_date):
   raise HTTPException(409,'Dados financeiros de um plantao com recebimento confirmado exigem ajuste explicito.')
  for k,v in payload.items():setattr(x,k,v)
  x=self.repo.save(x)
  from app.services.receivable_service import ReceivableService
  ReceivableService(self.db).sync_shift(x)
  from app.services.tax_service import TaxService
  TaxService(self.db).sync(user,x.gross_value,x.date,shift_id=x.id,percentage=x.tax_reserve_percentage,tax_treatment=x.tax_treatment)
  from app.services.cashflow_service import CashflowService
  cashflow=CashflowService(self.db);cashflow.sync_source(user,'Plantão',x.id,x.expected_payment_date or x.date,'Receita Prevista',x.title or x.type,'Plantões',x.gross_value);self.db.commit();cashflow.recalculate(user)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user);return x
 def delete(self,user,id):
  x=self.get(user,id)
  from app.models.receivable import Receivable
  receivable=self.db.scalar(select(Receivable).where(Receivable.user_id==user,Receivable.shift_id==x.id,Receivable.deleted_at.is_(None)))
  if receivable and receivable.received_value>0:raise HTTPException(409,'Plantao com recebimento confirmado nao pode ser excluido.')
  x.deleted_at=datetime.now(timezone.utc)
  if receivable:receivable.deleted_at=x.deleted_at
  from app.services.cashflow_service import CashflowService
  flow=CashflowService(self.db);flow.sync_source(user,'Plantão',x.id,x.expected_payment_date or x.date,'Receita Prevista',x.title or x.type,'Plantões',x.gross_value,'Cancelado');self.db.commit();flow.recalculate(user)
