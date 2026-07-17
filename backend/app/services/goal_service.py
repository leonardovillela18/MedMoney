from datetime import datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.financial_goal import FinancialGoal,FinancialGoalSnapshot
from app.services.goals.engine import GoalEngine
class GoalService:
 def __init__(self,db:Session):self.db=db;self.engine=GoalEngine(db)
 def get(self,user,id):
  x=self.db.scalar(select(FinancialGoal).where(FinancialGoal.id==id,FinancialGoal.user_id==user,FinancialGoal.deleted_at.is_(None)))
  if not x:raise HTTPException(404,'Meta não encontrada.')
  return x
 def list(self,user,page,size,status=None):
  q=select(FinancialGoal).where(FinancialGoal.user_id==user,FinancialGoal.deleted_at.is_(None));q=q.where(FinancialGoal.status==status) if status else q;q=q.order_by(FinancialGoal.created_at.desc());return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
 def create(self,user,data):
  current=data.pop('valor_atual',None);x=FinancialGoal(user_id=user,valor_atual=current or 0,percentual=0,status='Em andamento',**data);self.db.add(x);self.db.commit();self.db.refresh(x);return self.engine.update(x)
 def update(self,user,id,data):
  x=self.get(user,id);current=data.pop('valor_atual',None)
  for k,v in data.items():setattr(x,k,v)
  if x.tipo=='Meta Personalizada' and current is not None:x.valor_atual=current
  self.db.commit();return self.engine.update(x)
 def delete(self,user,id):x=self.get(user,id);x.deleted_at=datetime.now(timezone.utc);self.db.commit()
 def detail(self,user,id):
  x=self.get(user,id);history=list(self.db.scalars(select(FinancialGoalSnapshot).where(FinancialGoalSnapshot.goal_id==x.id,FinancialGoalSnapshot.user_id==user).order_by(FinancialGoalSnapshot.data)));return {'goal':x,'forecast':self.engine.forecast(x),'insight':self.engine.insight(x),'comparisons':self.engine.comparisons(x),'history':[{'date':str(h.data),'value':float(h.valor),'percentage':float(h.percentual)} for h in history]}
 def dashboard(self,user):
  self.engine.update_all(user);items=list(self.db.scalars(select(FinancialGoal).where(FinancialGoal.user_id==user,FinancialGoal.deleted_at.is_(None))));active=[x for x in items if x.status=='Em andamento'];completed=[x for x in items if x.status=='Concluída'];closest=max(active,key=lambda x:x.percentual,default=None);farthest=min(active,key=lambda x:x.percentual,default=None);return {'active':len(active),'completed':len(completed),'closest':closest,'farthest':farthest,'goals':active[:8]}
 def simulate(self,user,data):
  x=self.get(user,data['goal_id']);shift_income=Decimal(data['extra_shifts'])*Decimal(data['shift_value']);revenue=Decimal(data['extra_revenue']);reduction=Decimal(data['expense_reduction'])
  if x.tipo=='Quantidade de Plantões':simulated=x.valor_atual+Decimal(data['extra_shifts'])
  elif x.tipo=='Despesas Máximas':simulated=max(Decimal(0),x.valor_atual-reduction)
  elif x.tipo in ('Receita Mensal','Receita Anual','Recebimentos'):simulated=x.valor_atual+shift_income+revenue
  else:simulated=x.valor_atual+shift_income+revenue+reduction
  percentage=min(Decimal(100),simulated/x.valor_meta*100);elapsed=max(1,(datetime.now().date()-x.data_inicio).days+1);pace=simulated/Decimal(elapsed);remaining=max(Decimal(0),x.valor_meta-simulated);days=int((remaining/pace).to_integral_value(rounding='ROUND_CEILING')) if pace else None;return {'current':float(x.valor_atual),'simulated':float(simulated),'percentage':float(percentage),'remaining':float(remaining),'forecast_days':days,'persisted':False}
