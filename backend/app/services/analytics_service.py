import json
from collections import defaultdict
from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
from app.models.expense import Expense,ExpenseCategory
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
from app.infrastructure.cache import get_cache
def invalidate_analytics(user_id):
 get_cache().delete_prefix(f'analytics:{user_id}:')
class AnalyticsService:
 """Read-only statistical service. Operational modules only invalidate its bounded cache."""
 def __init__(self,db:Session,user_id,filters=None):self.db=db;self.user_id=user_id;self.filters=filters or {};self.contractors={x.id:x.name for x in db.scalars(select(Contractor).where(Contractor.user_id==user_id,Contractor.deleted_at.is_(None)))};self.categories={x.id:x.nome for x in db.scalars(select(ExpenseCategory).where(ExpenseCategory.user_id==user_id,ExpenseCategory.deleted_at.is_(None)))}
 def cached(self,name,builder):
  filters=json.dumps({k:str(v) for k,v in self.filters.items() if v is not None},sort_keys=True,separators=(',',':'))
  key=f'analytics:{self.user_id}:{name}:{filters}';cache=get_cache();hit=cache.get(key)
  if hit is not None:return hit
  value=builder();cache.set(key,value,60);return value
 def shifts(self):
  q=select(Shift).where(Shift.user_id==self.user_id,Shift.deleted_at.is_(None));f=self.filters
  if f.get('date_from'):q=q.where(Shift.date>=f['date_from'])
  if f.get('date_to'):q=q.where(Shift.date<=f['date_to'])
  for key in ('contractor_id','specialty','city','type','status'):
   if f.get(key):q=q.where(getattr(Shift,key)==f[key])
  return list(self.db.scalars(q))
 def expenses(self):
  q=select(Expense).where(Expense.user_id==self.user_id,Expense.deleted_at.is_(None),Expense.status!='Cancelado');f=self.filters
  if f.get('date_from'):q=q.where(Expense.competencia>=f['date_from'])
  if f.get('date_to'):q=q.where(Expense.competencia<=f['date_to'])
  if f.get('category_id'):q=q.where(Expense.categoria_id==f['category_id'])
  if f.get('status'):q=q.where(Expense.status==f['status'])
  return list(self.db.scalars(q))
 def receivables(self):
  q=select(Receivable).where(Receivable.user_id==self.user_id,Receivable.deleted_at.is_(None));f=self.filters
  if f.get('date_from'):q=q.where(Receivable.expected_date>=f['date_from'])
  if f.get('date_to'):q=q.where(Receivable.expected_date<=f['date_to'])
  if f.get('contractor_id'):q=q.where(Receivable.contractor_id==f['contractor_id'])
  if f.get('status'):q=q.where(Receivable.status==f['status'])
  return list(self.db.scalars(q))
 def taxes(self):
  q=select(TaxEstimation).where(TaxEstimation.user_id==self.user_id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado');f=self.filters
  if f.get('date_from'):q=q.where(TaxEstimation.competencia>=f['date_from'])
  if f.get('date_to'):q=q.where(TaxEstimation.competencia<=f['date_to'])
  return list(self.db.scalars(q))
 @staticmethod
 def series(items,date_field,value_field):
  rows=defaultdict(Decimal)
  for x in items:
   value=getattr(x,date_field)
   if value:rows[value.strftime('%Y-%m')]+=Decimal(getattr(x,value_field) or 0)
  return [{'label':k,'value':float(v)} for k,v in sorted(rows.items())]
 @staticmethod
 def rank(rows,limit=10):return [{'name':str(k),'value':float(v)} for k,v in sorted(rows.items(),key=lambda x:x[1],reverse=True)[:limit]]
 def revenue(self):
  def build():
   shifts=self.shifts();rec=self.receivables();group=lambda fn:self.rank(self.accumulate(shifts,fn,lambda x:x.gross_value));expected=sum((x.remaining_balance for x in rec),Decimal(0));received=sum((x.received_value for x in rec),Decimal(0));overdue=sum((x.remaining_balance for x in rec if x.expected_date<date.today() and x.status!='Recebido'),Decimal(0));monthly=self.series(rec,'received_date','received_value');acc=Decimal(0);accum=[]
   for x in monthly:acc+=Decimal(str(x['value']));accum.append({'label':x['label'],'value':float(acc)})
   years=defaultdict(Decimal)
   for x in rec:
    if x.received_date:years[str(x.received_date.year)]+=x.received_value
   return {'monthly':monthly,'annual':self.rank(years,20),'accumulated':accum,'by_hospital':group(lambda x:self.contractors.get(x.contractor_id,'Contratante')),'by_city':group(lambda x:x.city or 'Não informado'),'by_specialty':group(lambda x:x.specialty or 'Não informado'),'by_type':group(lambda x:x.type),'expected':float(expected),'received':float(received),'overdue':float(overdue),'top_receivables':self.rank({f'{self.contractors.get(x.contractor_id,"Contratante")} · {x.expected_date}':x.expected_value for x in rec})}
  return self.cached('revenue',build)
 def shifts_analysis(self):
  def build():
   shifts=self.shifts();hour=lambda x:Decimal(x.duration_hours or 0);heat=defaultdict(lambda:{'value':Decimal(0),'hours':Decimal(0),'count':0})
   for x in shifts:
    key=f'{x.date.weekday()}-{x.start_time.hour}';heat[key]['value']+=x.gross_value;heat[key]['hours']+=hour(x);heat[key]['count']+=1
   return {'count':len(shifts),'hours':float(sum((hour(x) for x in shifts),Decimal(0))),'by_hospital':self.rank(self.accumulate(shifts,lambda x:self.contractors.get(x.contractor_id,'Contratante'),lambda x:1)),'by_city':self.rank(self.accumulate(shifts,lambda x:x.city or 'Não informado',lambda x:1)),'by_weekday':self.rank(self.accumulate(shifts,lambda x:x.date.strftime('%A'),lambda x:1)),'by_hour':self.rank(self.accumulate(shifts,lambda x:f'{x.start_time.hour:02d}h',lambda x:1)),'day':sum(1 for x in shifts if 6<=x.start_time.hour<18),'night':sum(1 for x in shifts if x.start_time.hour<6 or x.start_time.hour>=18),'cancelled':sum(1 for x in shifts if x.status=='Cancelado'),'received':sum(1 for x in shifts if x.status in ('Recebido','Pago')),'heatmap':[{'day':int(k.split('-')[0]),'hour':int(k.split('-')[1]),'value':float(v['value']/v['hours']) if v['hours'] else 0,'count':v['count']} for k,v in heat.items()],'top':self.rank({str(x.id):x.gross_value for x in shifts})}
  return self.cached('shifts',build)
 def expense_analysis(self):
  def build():
   items=self.expenses();total=sum((x.valor for x in items),Decimal(0));return {'total':float(total),'fixed':float(sum((x.valor for x in items if x.tipo=='Fixa'),Decimal(0))),'variable':float(sum((x.valor for x in items if x.tipo=='Variável'),Decimal(0))),'by_category':self.rank(self.accumulate(items,lambda x:self.categories.get(x.categoria_id,'Outros'),lambda x:x.valor)),'by_supplier':self.rank(self.accumulate(items,lambda x:x.fornecedor or 'Não informado',lambda x:x.valor)),'monthly':self.series(items,'competencia','valor'),'top':self.rank({x.titulo:x.valor for x in items})}
  return self.cached('expenses',build)
 def profit(self):
  def build():
   revenue=self.revenue()['monthly'];expenses=self.expense_analysis()['monthly'];taxes=self.series(self.taxes(),'competencia','valor_estimado');keys=sorted(set(x['label'] for rows in (revenue,expenses,taxes) for x in rows));maps=[{x['label']:Decimal(str(x['value'])) for x in rows} for rows in (revenue,expenses,taxes)];monthly=[]
   for k in keys:
    gross=maps[0].get(k,0);expense=maps[1].get(k,0);tax=maps[2].get(k,0);net=gross-expense-tax;monthly.append({'label':k,'gross':float(gross),'expenses':float(expense),'taxes':float(tax),'net':float(net),'margin':float(net/gross*100) if gross else 0})
   gross=sum((Decimal(str(x['value'])) for x in revenue),Decimal(0));expense=sum((Decimal(str(x['value'])) for x in expenses),Decimal(0));tax=sum((Decimal(str(x['value'])) for x in taxes),Decimal(0));net=gross-expense-tax;return {'gross':float(gross),'net':float(net),'net_margin':float(net/gross*100) if gross else 0,'operating_margin':float((gross-expense)/gross*100) if gross else 0,'monthly':monthly}
  return self.cached('profit',build)
 def contractors_analysis(self):
  def build():
   shifts=self.shifts();rec=self.receivables();gross=self.accumulate(shifts,lambda x:x.contractor_id,lambda x:x.gross_value);counts=self.accumulate(shifts,lambda x:x.contractor_id,lambda x:1);delays=defaultdict(list)
   for x in rec:
    if x.received_date:delays[x.contractor_id].append((x.received_date-x.expected_date).days)
   total=sum(gross.values(),Decimal(0));rows=[]
   for key,value in gross.items():rows.append({'id':str(key),'name':self.contractors.get(key,'Contratante'),'revenue':float(value),'shifts':int(counts[key]),'average_ticket':float(value/counts[key]),'average_delay':sum(delays[key])/len(delays[key]) if delays[key] else None,'share':float(value/total*100) if total else 0})
   return {'ranking':sorted(rows,key=lambda x:x['revenue'],reverse=True)[:10]}
  return self.cached('contractors',build)
 def executive(self):
  def build():
   shifts=self.shifts();revenue=self.revenue();expenses=self.expense_analysis();profit=self.profit();hours=sum((x.duration_hours for x in shifts),Decimal(0));gross=sum((x.gross_value for x in shifts),Decimal(0));specialties=self.accumulate(shifts,lambda x:x.specialty or 'Não informado',lambda x:x.gross_value);contractors=self.accumulate(shifts,lambda x:self.contractors.get(x.contractor_id,'Contratante'),lambda x:x.gross_value);taxes=self.taxes();return {'kpis':{'gross_revenue':float(gross),'net_revenue':float(gross-sum((x.valor_estimado for x in taxes),Decimal(0))),'profit':profit['net'],'margin':profit['net_margin'],'shifts':len(shifts),'hours':float(hours),'average_hour':float(gross/hours) if hours else 0,'average_shift':float(gross/len(shifts)) if shifts else 0,'largest_revenue':max((x.gross_value for x in shifts),default=Decimal(0)),'largest_expense':max((x.valor for x in self.expenses()),default=Decimal(0)),'largest_contractor':max(contractors,key=contractors.get) if contractors else 'Sem dados','largest_specialty':max(specialties,key=specialties.get) if specialties else 'Sem dados'},'revenue':revenue,'expenses':expenses,'profit':profit,'tax':{'estimated':float(sum((x.valor_estimado for x in taxes),Decimal(0))),'reserved':float(sum((x.valor_estimado for x in taxes if x.status in ('Reservado','Pago')),Decimal(0))),'effective_percentage':float(sum((x.valor_estimado for x in taxes),Decimal(0))/gross*100) if gross else 0,'monthly':self.series(taxes,'competencia','valor_estimado')},'comparisons':self.comparisons()}
  return self.cached('executive',build)
 def comparisons(self):
  today=date.today();periods=[('Hoje',today,today),('7 dias',today-timedelta(days=6),today),('30 dias',today-timedelta(days=29),today),('90 dias',today-timedelta(days=89),today),('Este mês',today.replace(day=1),today),('Mês passado',(today.replace(day=1)-timedelta(days=1)).replace(day=1),today.replace(day=1)-timedelta(days=1)),('Ano anterior',today.replace(year=today.year-1,day=1),today.replace(year=today.year-1))];result=[]
  for label,start,end in periods:
   shifts=[x for x in self.shifts() if start<=x.date<=end];result.append({'label':label,'revenue':float(sum((x.gross_value for x in shifts),Decimal(0))),'shifts':len(shifts),'hours':float(sum((x.duration_hours for x in shifts),Decimal(0)))})
  return result
 @staticmethod
 def accumulate(items,key,value):
  rows=defaultdict(Decimal)
  for x in items:rows[key(x)]+=Decimal(value(x))
  return rows
