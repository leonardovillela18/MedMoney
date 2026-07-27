from datetime import date,datetime,timedelta
from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import operational_user
from app.database.session import get_db
from app.models.contractor import Contractor
from app.models.shift import Shift
from app.models.user import User

router=APIRouter(prefix='/assistant-dashboard',tags=['Painel da auxiliar'])
@router.get('')
def dashboard(owner:User=Depends(operational_user),db:Session=Depends(get_db)):
 now=datetime.now();today=now.date();month=today.replace(day=1)
 items=list(db.scalars(select(Shift).where(Shift.user_id==owner.id,Shift.deleted_at.is_(None),Shift.date>=month).order_by(Shift.date,Shift.start_time)))
 future=[x for x in items if datetime.combine(x.date,x.start_time)>=now]
 contractors={x.id:x.name for x in db.scalars(select(Contractor).where(Contractor.user_id==owner.id,Contractor.deleted_at.is_(None)))}
 def event(x):
  at=datetime.combine(x.date,x.start_time);hours=max(0,(at-now).total_seconds()/3600)
  return {'id':str(x.id),'type':x.type,'title':x.title or x.type,'date':str(x.date),'time':str(x.start_time)[:5],'location':x.hospital_sector or contractors.get(x.contractor_id,'Local não informado'),'hours_until':round(hours,1),'urgency':'24h' if hours<=24 else '48h' if hours<=48 else None}
 upcoming=[event(x) for x in future[:10]]
 return {'doctor_name':owner.name,'summary':{'consultations_done':sum(x.type=='Consulta' and x.status=='Realizado' for x in items),'surgeries_done':sum(x.type=='Cirurgia' and x.status=='Realizado' for x in items),'consultations_scheduled':sum(x.type=='Consulta' for x in future),'surgeries_scheduled':sum(x.type=='Cirurgia' for x in future),'shifts_scheduled':sum(x.type.startswith('Plantão') for x in future)},'urgent':[x for x in upcoming if x['urgency']],'upcoming':upcoming}
