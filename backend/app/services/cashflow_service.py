from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.cashflow import CashflowProjection
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
from app.repositories.cashflow_repository import CashflowRepository

INFLOWS={'Receita Prevista','Receita Recebida'}
class CashflowService:
 """Read-only financial forecast derived from domain events; never accepts manual ledger entries."""
 def __init__(self,db:Session):self.db=db;self.repo=CashflowRepository(db)
 def sync_source(self,user,origin,origin_id,when,kind,description,category,value,status='Previsto'):
  x=self.repo.source(user,origin,origin_id)
  if not x:x=CashflowProjection(user_id=user,origem=origin,origem_id=origin_id);self.db.add(x)
  x.data=when;x.tipo=kind;x.descricao=description;x.categoria=category;x.valor=Decimal(value);x.status=status;self.db.flush();return x
 def reconcile(self,user):
  shifts=self.db.scalars(select(Shift).where(Shift.user_id==user,Shift.deleted_at.is_(None)))
  for x in shifts:self.sync_source(user,'Plantão',x.id,x.expected_payment_date or x.date,'Receita Prevista',x.title or x.type,'Plantões',x.gross_value,'Previsto')
  receivables=self.db.scalars(select(Receivable).where(Receivable.user_id==user,Receivable.deleted_at.is_(None),Receivable.received_value>0))
  for x in receivables:self.sync_source(user,'Plantão',x.shift_id,x.received_date or x.expected_date,'Receita Recebida','Recebimento de plantão','Recebimentos',x.received_value,'Confirmado')
  taxes=self.db.scalars(select(TaxEstimation).where(TaxEstimation.user_id==user,TaxEstimation.deleted_at.is_(None),TaxEstimation.status.in_(['Reservado','Pago'])))
  for x in taxes:self.sync_source(user,'Reserva Tributária',x.id,x.competencia,'Reserva Tributária',f'Reserva sugerida — {x.tipo}','Impostos',-abs(x.valor_estimado),'Confirmado')
  self.db.commit();self.recalculate(user)
 def recalculate(self,user):
  items=list(self.db.scalars(self.repo.query(user,{})));balance=Decimal(0)
  for x in items:
   if x.status!='Cancelado':balance+=x.valor
   x.saldo_projetado=balance
  self.db.commit();return items
 def list(self,user,page,size,filters):self.reconcile(user);return self.repo.list(user,page,size,filters)
 def projection(self,user,days=180):
  self.reconcile(user);today=date.today();items=list(self.db.scalars(self.repo.query(user,{'date_to':today+timedelta(days=days)})));current=sum((x.valor for x in items if x.data<=today and x.status=='Confirmado'),Decimal(0));month=today.replace(day=1);month_items=[x for x in items if x.data>=month and x.data<(month.replace(year=month.year+(month.month==12),month=1 if month.month==12 else month.month+1))]
  incoming=sum((x.valor for x in month_items if x.tipo in INFLOWS),Decimal(0));outgoing=-sum((x.valor for x in month_items if x.tipo not in INFLOWS),Decimal(0));reserved=-sum((x.valor for x in items if x.tipo=='Reserva Tributária'),Decimal(0));future=sum((x.valor for x in items if x.data<=today+timedelta(days=days) and x.status!='Cancelado'),Decimal(0));negative=next((x for x in items if x.saldo_projetado<0 and x.data>=today),None)
  horizons=[7,15,30,60,90,180];forecasts=[{'days':d,'balance':float(sum((x.valor for x in items if x.data<=today+timedelta(days=d) and x.status!='Cancelado'),Decimal(0)))} for d in horizons]
  daily={}
  for x in items:
   b=daily.setdefault(str(x.data),{'inflow':Decimal(0),'outflow':Decimal(0),'balance':x.saldo_projetado});b['inflow' if x.valor>=0 else 'outflow']+=abs(x.valor);b['balance']=x.saldo_projetado
  insights=[f'Você ficará com saldo negativo em {(negative.data-today).days} dias.' if negative else 'Seu fluxo projetado permanece positivo no período analisado.']
  return {'summary':{'current_balance':float(current),'forecast_balance':float(future),'month_inflows':float(incoming),'month_outflows':float(outgoing),'net_result':float(incoming-outgoing),'tax_reserve':float(reserved),'available':float(future)},'forecasts':forecasts,'series':[{'date':k,**{n:float(v) for n,v in b.items()}} for k,b in daily.items()],'insights':insights,'alerts':self.alerts(user,items,today)}
 def alerts(self,user,items,today):
  alerts=[]
  if any(x.saldo_projetado<0 and x.data>=today for x in items):alerts.append('Alerta de saldo projetado negativo.')
  if any(x.tipo=='Receita Prevista' and x.data<today and x.status=='Previsto' for x in items):alerts.append('Há recebimento previsto em atraso.')
  expenses=[abs(x.valor) for x in items if x.tipo in ('Despesa Prevista','Despesa Paga')]
  if expenses and max(expenses)>sum(expenses)/len(expenses)*Decimal(2):alerts.append('Foi identificada uma despesa acima da média.')
  estimated=Decimal(self.db.scalar(select(func.coalesce(func.sum(TaxEstimation.valor_estimado),0)).where(TaxEstimation.user_id==user,TaxEstimation.status=='Estimado',TaxEstimation.deleted_at.is_(None))) or 0)
  if estimated>0:alerts.append('A reserva tributária ainda não cobre todos os impostos estimados.')
  contractor_totals={}
  for shift in self.db.scalars(select(Shift).where(Shift.user_id==user,Shift.deleted_at.is_(None))):contractor_totals[shift.contractor_id]=contractor_totals.get(shift.contractor_id,Decimal(0))+shift.gross_value
  total=sum(contractor_totals.values(),Decimal(0))
  if total and max(contractor_totals.values())/total>Decimal('0.5'):alerts.append('Mais de 50% da receita está concentrada em um contratante.')
  return alerts
 def calendar(self,user,start,end):
  self.reconcile(user);items=list(self.db.scalars(self.repo.query(user,{'date_from':start,'date_to':end})));days={}
  for x in items:days.setdefault(str(x.data),[]).append({'id':str(x.id),'description':x.descricao,'value':float(x.valor),'balance':float(x.saldo_projetado),'status':x.status})
  return days
 def simulate(self,user,data):
  result=self.projection(user,data['horizon_days']);impact=Decimal(data['extra_shifts'])*Decimal(data['shift_value'])-Decimal(data['extra_expenses']);delayed=Decimal(0)
  if data.get('delayed_origin_id'):
   x=self.repo.source(user,'Plantão',data['delayed_origin_id']);delayed=x.valor if x and x.data+timedelta(days=data['delay_days'])>date.today()+timedelta(days=data['horizon_days']) else Decimal(0)
  baseline=Decimal(str(result['summary']['forecast_balance']));return {'baseline':float(baseline),'simulated_balance':float(baseline+impact-delayed),'impact':float(impact-delayed),'horizon_days':data['horizon_days'],'persisted':False}
