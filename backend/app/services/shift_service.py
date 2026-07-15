from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
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
 def payload(self,user,data):
  if not self.db.get(Contractor,data['contractor_id']) or not self.db.scalar(__import__('sqlalchemy').select(Contractor).where(Contractor.id==data['contractor_id'],Contractor.user_id==user,Contractor.deleted_at.is_(None))):raise HTTPException(422,'Contratante inválido.')
  data['duration_hours']=data.get('duration_hours') or Decimal((datetime.combine(data['date'],data['end_time'])-datetime.combine(data['date'],data['start_time'])).seconds)/Decimal(3600);data['estimated_net_value']=data.get('estimated_net_value') or data['gross_value'];return data
 def create(self,user,data):return self.repo.save(Shift(user_id=user,**self.payload(user,data)))
 def update(self,user,id,data):
  x=self.get(user,id)
  for k,v in self.payload(user,data).items():setattr(x,k,v)
  return self.repo.save(x)
 def delete(self,user,id):x=self.get(user,id);x.deleted_at=datetime.now(timezone.utc);self.db.commit()
