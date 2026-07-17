from datetime import datetime,timezone
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.services.alerts.channels import CHANNELS
from app.services.alerts.context import AlertContext
from app.services.alerts.rules import RULES
PRIORITY=case((Alert.prioridade=='Crítica',4),(Alert.prioridade=='Alta',3),(Alert.prioridade=='Média',2),else_=1)
class AlertEngine:
 """Deterministic cached rule engine. New rules and delivery channels register without core changes."""
 def __init__(self,db:Session):self.db=db
 def recalculate(self,user_id):
  context=AlertContext(self.db,user_id);candidates=[item for rule in RULES for item in rule.evaluate(context)];keys={(x.tipo,x.origem,x.referencia_id) for x in candidates};existing={(x.tipo,x.origem,x.referencia_id):x for x in self.db.scalars(select(Alert).where(Alert.user_id==user_id))};now=datetime.now(timezone.utc);new_critical=0
  for data in candidates:
   key=(data.tipo,data.origem,data.referencia_id);x=existing.get(key)
   if not x:x=Alert(user_id=user_id,tipo=data.tipo,origem=data.origem,referencia_id=data.referencia_id,status='Novo');self.db.add(x);new_critical+=data.prioridade=='Crítica'
   for field in ('categoria','titulo','descricao','prioridade','acao','url_destino'):setattr(x,field,getattr(data,field))
   if x.status=='Resolvido' and x.resolvido_em and (now-x.resolvido_em).days>=1:x.status='Novo';x.resolvido_em=None;x.lido_em=None
  for key,x in existing.items():
   if key not in keys and x.status not in ('Resolvido','Arquivado'):x.status='Resolvido';x.resolvido_em=now
  self.db.commit()
  for x in self.db.scalars(select(Alert).where(Alert.user_id==user_id,Alert.status=='Novo')):
   for channel in CHANNELS:channel.deliver(x)
  return {'active':len(candidates),'new_critical':new_critical}
 def warm(self,user_id):
  if not self.db.scalar(select(func.count()).select_from(Alert).where(Alert.user_id==user_id)):self.recalculate(user_id)
 def get(self,user,id):
  from fastapi import HTTPException
  x=self.db.scalar(select(Alert).where(Alert.id==id,Alert.user_id==user))
  if not x:raise HTTPException(404,'Alerta não encontrado.')
  return x
 def mark_read(self,user,id):
  x=self.get(user,id)
  if x.status=='Novo':x.status='Lido';x.lido_em=datetime.now(timezone.utc);self.db.commit();self.db.refresh(x)
  return x
 def resolve(self,user,id):x=self.get(user,id);x.status='Resolvido';x.resolvido_em=datetime.now(timezone.utc);self.db.commit();self.db.refresh(x);return x
 def list(self,user,page,size,filters):
  self.warm(user);q=select(Alert).where(Alert.user_id==user)
  for field in ('categoria','prioridade','status','origem'):
   if filters.get(field):q=q.where(getattr(Alert,field)==filters[field])
  if filters.get('date_from'):q=q.where(Alert.created_at>=filters['date_from'])
  if filters.get('date_to'):q=q.where(Alert.created_at<filters['date_to'])
  if filters.get('search'):q=q.where(or_(Alert.titulo.ilike(f"%{filters['search']}%"),Alert.descricao.ilike(f"%{filters['search']}%"),Alert.acao.ilike(f"%{filters['search']}%")))
  q=q.order_by(PRIORITY.desc(),Alert.updated_at.desc());items=list(self.db.scalars(q.offset((page-1)*size).limit(size)));total=self.db.scalar(select(func.count()).select_from(q.subquery())) or 0;unread=self.db.scalar(select(func.count()).select_from(Alert).where(Alert.user_id==user,Alert.status=='Novo')) or 0;return items,total,unread
 def dashboard(self,user):
  self.warm(user);active=list(self.db.scalars(select(Alert).where(Alert.user_id==user,Alert.status.in_(['Novo','Lido'])).order_by(PRIORITY.desc(),Alert.updated_at.desc())));counts={x:sum(1 for a in active if a.prioridade==x) for x in ('Baixa','Média','Alta','Crítica')};return {'unread':sum(1 for x in active if x.status=='Novo'),'active':len(active),'counts':counts,'highlights':active[:5]}
