from datetime import date,timedelta
from decimal import Decimal,ROUND_HALF_UP
from typing import Protocol
from copy import copy
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.models.financial_goal import FinancialGoal,FinancialGoalSnapshot
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
class GoalContext:
 def __init__(self,db:Session,user_id):
  self.shifts=list(db.scalars(select(Shift).where(Shift.user_id==user_id,Shift.deleted_at.is_(None))));self.receivables=list(db.scalars(select(Receivable).where(Receivable.user_id==user_id,Receivable.deleted_at.is_(None))));self.expenses=list(db.scalars(select(Expense).where(Expense.user_id==user_id,Expense.deleted_at.is_(None),Expense.status!='Cancelado')));self.taxes=list(db.scalars(select(TaxEstimation).where(TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado')))
 @staticmethod
 def between(items,field,goal):return [x for x in items if getattr(x,field) is not None and goal.data_inicio<=getattr(x,field)<=goal.data_final]
class GoalStrategy(Protocol):
 def calculate(self,goal:FinancialGoal,context:GoalContext)->Decimal:...
class RevenueStrategy:
 def calculate(self,g,c):return sum((x.received_value for x in c.between(c.receivables,'received_date',g)),Decimal(0))
class ProfitStrategy:
 def calculate(self,g,c):return RevenueStrategy().calculate(g,c)-sum((x.valor for x in c.between(c.expenses,'competencia',g)),Decimal(0))-sum((x.valor_estimado for x in c.between(c.taxes,'competencia',g)),Decimal(0))
class ShiftCountStrategy:
 def calculate(self,g,c):return Decimal(len(c.between(c.shifts,'date',g)))
class HoursStrategy:
 def calculate(self,g,c):return sum((x.duration_hours for x in c.between(c.shifts,'date',g)),Decimal(0))
class HourValueStrategy:
 def calculate(self,g,c):
  items=c.between(c.shifts,'date',g);hours=sum((x.duration_hours for x in items),Decimal(0));return sum((x.gross_value for x in items),Decimal(0))/hours if hours else Decimal(0)
class TaxReserveStrategy:
 def calculate(self,g,c):return sum((x.valor_estimado for x in c.between([x for x in c.taxes if x.status in ('Reservado','Pago')],'competencia',g)),Decimal(0))
class SavingsStrategy:
 def calculate(self,g,c):
  current=sum((x.valor for x in c.between(c.expenses,'competencia',g)),Decimal(0));days=(g.data_final-g.data_inicio).days+1;previous_start=g.data_inicio-timedelta(days=days);previous=sum((x.valor for x in c.expenses if previous_start<=x.competencia<g.data_inicio),Decimal(0));return max(Decimal(0),previous-current)
class MaxExpenseStrategy:
 def calculate(self,g,c):return sum((x.valor for x in c.between(c.expenses,'competencia',g)),Decimal(0))
class CustomStrategy:
 def calculate(self,g,c):return g.valor_atual
STRATEGIES={'Receita Mensal':RevenueStrategy(),'Receita Anual':RevenueStrategy(),'Lucro Líquido':ProfitStrategy(),'Quantidade de Plantões':ShiftCountStrategy(),'Horas Trabalhadas':HoursStrategy(),'Valor por Hora':HourValueStrategy(),'Reserva Tributária':TaxReserveStrategy(),'Economia':SavingsStrategy(),'Despesas Máximas':MaxExpenseStrategy(),'Recebimentos':RevenueStrategy(),'Meta Personalizada':CustomStrategy()}
class GoalEngine:
 """Central goal calculator. New goal types require only another registered strategy."""
 def __init__(self,db:Session):self.db=db
 def update_all(self,user_id):
  goals=list(self.db.scalars(select(FinancialGoal).where(FinancialGoal.user_id==user_id,FinancialGoal.deleted_at.is_(None),FinancialGoal.status!='Cancelada')));context=GoalContext(self.db,user_id)
  for goal in goals:self.update(goal,context,commit=False)
  self.db.commit();return len(goals)
 def update(self,goal,context=None,commit=True):
  context=context or GoalContext(self.db,goal.user_id);value=STRATEGIES[goal.tipo].calculate(goal,context);goal.valor_atual=value;goal.percentual=min(Decimal(100),max(Decimal(0),(value/goal.valor_meta*100 if goal.valor_meta else Decimal(0)))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP);today=date.today()
  if goal.tipo=='Despesas Máximas':goal.status='Atrasada' if value>goal.valor_meta else 'Concluída' if today>goal.data_final else 'Em andamento'
  else:goal.status='Concluída' if value>=goal.valor_meta else 'Atrasada' if today>goal.data_final else 'Em andamento'
  snapshot=self.db.scalar(select(FinancialGoalSnapshot).where(FinancialGoalSnapshot.goal_id==goal.id,FinancialGoalSnapshot.data==today))
  if not snapshot:snapshot=FinancialGoalSnapshot(goal_id=goal.id,user_id=goal.user_id,data=today);self.db.add(snapshot)
  snapshot.valor=value;snapshot.percentual=goal.percentual
  if commit:self.db.commit();self.db.refresh(goal)
  return goal
 def forecast(self,goal):
  elapsed=max(1,(date.today()-goal.data_inicio).days+1);pace=goal.valor_atual/Decimal(elapsed);remaining=max(Decimal(0),goal.valor_meta-goal.valor_atual);days=int((remaining/pace).to_integral_value(rounding='ROUND_CEILING')) if pace>0 else None;forecast=date.today()+timedelta(days=days) if days is not None else None;required=max(Decimal(0),(goal.valor_meta-goal.valor_atual)/Decimal(max(1,(goal.data_final-date.today()).days+1)));return {'remaining':float(remaining),'days_remaining':max(0,(goal.data_final-date.today()).days),'forecast_date':str(forecast) if forecast else None,'forecast_days':days,'daily_pace':float(pace),'required_daily_pace':float(required),'on_track':bool(forecast and forecast<=goal.data_final)}
 def insight(self,goal):
  forecast=self.forecast(goal);remaining=Decimal(str(forecast['remaining']))
  if goal.status=='Concluída':return 'Meta concluída com base nos dados registrados.'
  if goal.tipo=='Quantidade de Plantões':return f'Faltam {int(remaining)} plantões para atingir a meta.'
  if forecast['on_track']:return f'No ritmo atual, você atingirá a meta em {forecast["forecast_days"]} dias.'
  if forecast['daily_pace']>0:return f'É necessário elevar o ritmo diário em {max(0,(forecast["required_daily_pace"]/forecast["daily_pace"]-1)*100):.0f}%.'
  return 'Ainda não há dados suficientes para prever a conclusão.'
 def comparisons(self,goal):
  context=GoalContext(self.db,goal.user_id);strategy=STRATEGIES[goal.tipo];days=(goal.data_final-goal.data_inicio).days+1;previous=copy(goal);previous.data_final=goal.data_inicio-timedelta(days=1);previous.data_inicio=previous.data_final-timedelta(days=days-1);year=copy(goal);year.data_inicio=goal.data_inicio.replace(year=goal.data_inicio.year-1);year.data_final=goal.data_final.replace(year=goal.data_final.year-1);return [{'label':'Meta atual','value':float(goal.valor_atual)},{'label':'Período anterior','value':float(strategy.calculate(previous,context))},{'label':'Mesmo período ano passado','value':float(strategy.calculate(year,context))}]
