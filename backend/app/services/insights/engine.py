from datetime import datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.financial_insight import FinancialInsight
from app.services.insights.analyzers import ConcentrationAnalyzer,ExpenseAnalyzer,PaymentAnalyzer,ProfitabilityAnalyzer,ProfitTrendAnalyzer,RecordMonthAnalyzer,RevenueTrendAnalyzer
from app.services.insights.context import InsightContext
ANALYZERS=(RevenueTrendAnalyzer(),ProfitTrendAnalyzer(),ConcentrationAnalyzer(),ProfitabilityAnalyzer(),RecordMonthAnalyzer(),PaymentAnalyzer(),ExpenseAnalyzer())
class FinancialInsightsService:
 """Cached deterministic insight engine. Add rules by registering another analyzer strategy."""
 def __init__(self,db:Session):self.db=db
 def recalculate(self,user_id):
  context=InsightContext(self.db,user_id);candidates=[candidate for analyzer in ANALYZERS for candidate in analyzer.analyze(context)];active_refs={x.referencia for x in candidates};existing={x.referencia:x for x in self.db.scalars(select(FinancialInsight).where(FinancialInsight.user_id==user_id))}
  for data in candidates:
   x=existing.get(data.referencia)
   if not x:x=FinancialInsight(user_id=user_id,referencia=data.referencia);self.db.add(x)
   for key,value in data.__dict__.items():setattr(x,key,value)
   if x.status not in ('Arquivado','Visualizado'):x.status='Novo'
  now=datetime.now(timezone.utc)
  for ref,x in existing.items():
   if ref not in active_refs and x.status!='Arquivado':x.status='Arquivado';x.dismissed_at=now
  self.db.commit();return len(candidates)
 def warm(self,user_id):
  if not self.db.scalar(select(func.count()).select_from(FinancialInsight).where(FinancialInsight.user_id==user_id)):self.recalculate(user_id)
 def get(self,user_id,id):
  x=self.db.scalar(select(FinancialInsight).where(FinancialInsight.id==id,FinancialInsight.user_id==user_id))
  if not x:raise HTTPException(404,'Insight não encontrado.')
  if x.status=='Novo':x.status='Visualizado';self.db.commit();self.db.refresh(x)
  return x
 def list(self,user_id,page,size,filters):
  self.warm(user_id);q=select(FinancialInsight).where(FinancialInsight.user_id==user_id)
  for key in ('categoria','severidade','status'):
   if filters.get(key):q=q.where(getattr(FinancialInsight,key)==filters[key])
  if filters.get('date_from'):q=q.where(FinancialInsight.created_at>=filters['date_from'])
  if filters.get('date_to'):q=q.where(FinancialInsight.created_at<filters['date_to'])
  q=q.order_by(FinancialInsight.prioridade.desc(),FinancialInsight.updated_at.desc());return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
 def dashboard(self,user_id):
  self.warm(user_id);items=list(self.db.scalars(select(FinancialInsight).where(FinancialInsight.user_id==user_id,FinancialInsight.status!='Arquivado').order_by(FinancialInsight.prioridade.desc())));counts={s:sum(1 for x in items if x.severidade==s) for s in ('Informativo','Atenção','Crítico')};categories={}
  for x in items:categories[x.categoria]=categories.get(x.categoria,0)+1
  context=InsightContext(self.db,user_id);elapsed=max(context.today.day,1);revenue=context.revenue(context.month,context.next_month);profit=context.profit(context.month,context.next_month);factor=Decimal(context.next_month.__sub__(context.month).days)/Decimal(elapsed)
  projected_revenue=revenue*factor;projected_profit=profit*factor;previous_revenue=context.revenue(context.previous,context.month);goal=previous_revenue or revenue;goal_progress=float(projected_revenue/goal*100) if goal else 0
  return {'highlights':items[:3],'counts':counts,'total':len(items),'categories':categories,'projections':{'month_revenue':float(projected_revenue),'month_profit':float(projected_profit),'taxes':float(context.tax(context.month,context.next_month)*factor),'cashflow':float(projected_profit),'goal':float(goal),'goal_progress':goal_progress}}
