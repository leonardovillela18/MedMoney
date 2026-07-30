from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
from app.models.expense import Expense
from app.models.invoice import Invoice
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
from app.services.cashflow_service import CashflowService

class TodayService:
 """Builds the personal finance briefing exclusively from persisted domain data."""
 def __init__(self,db:Session):self.db=db
 @staticmethod
 def month_bounds(value):
  start=value.replace(day=1);end=start.replace(year=start.year+(start.month==12),month=1 if start.month==12 else start.month+1);return start,end
 def sum(self,column,*where):return Decimal(self.db.scalar(select(func.coalesce(func.sum(column),0)).where(*where)) or 0)
 def build(self,user):
  today=date.today();month,end=self.month_bounds(today);prev_start,_=self.month_bounds(month-timedelta(days=1));year_start=month.replace(year=month.year-1);year_end=end.replace(year=end.year-1)
  active_shift=[Shift.user_id==user.id,Shift.deleted_at.is_(None)];active_rec=[Receivable.user_id==user.id,Receivable.deleted_at.is_(None)];active_exp=[Expense.user_id==user.id,Expense.deleted_at.is_(None),Expense.status!='Cancelado'];active_tax=[TaxEstimation.user_id==user.id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado']
  pending=self.sum(Receivable.remaining_balance,*active_rec);received=self.sum(Receivable.received_value,*active_rec,Receivable.received_date>=month,Receivable.received_date<end);expenses=self.sum(Expense.valor,*active_exp,Expense.competencia>=month,Expense.competencia<end);taxes=self.sum(TaxEstimation.valor_estimado,*active_tax,TaxEstimation.competencia>=month,TaxEstimation.competencia<end);reserved=self.sum(TaxEstimation.valor_estimado,*active_tax,TaxEstimation.status.in_(['Reservado','Pago']));net=received-taxes-expenses
  future_shifts=list(self.db.scalars(select(Shift).where(*active_shift,Shift.date>=today).order_by(Shift.date,Shift.start_time).limit(5)));contractors={x.id:x.name for x in self.db.scalars(select(Contractor).where(Contractor.user_id==user.id,Contractor.deleted_at.is_(None)))}
  payments=list(self.db.scalars(select(Receivable).where(*active_rec,Receivable.remaining_balance>0,Receivable.status!='Cancelado').order_by(Receivable.expected_date).limit(5)))
  month_shifts=list(self.db.scalars(select(Shift).where(*active_shift,Shift.date>=month,Shift.date<end)));prev_shifts=list(self.db.scalars(select(Shift).where(*active_shift,Shift.date>=prev_start,Shift.date<month)));year_shifts=list(self.db.scalars(select(Shift).where(*active_shift,Shift.date>=year_start,Shift.date<year_end)))
  comparisons=[self.comparison('Este mês',month_shifts,received,net),self.comparison('Mês anterior',prev_shifts,self.sum(Receivable.received_value,*active_rec,Receivable.received_date>=prev_start,Receivable.received_date<month),self.period_net(user.id,prev_start,month)),self.comparison('Mesmo mês ano passado',year_shifts,self.sum(Receivable.received_value,*active_rec,Receivable.received_date>=year_start,Receivable.received_date<year_end),self.period_net(user.id,year_start,year_end))]
  cash=CashflowService(self.db).projection(user.id);alerts=list(cash['alerts']);actions=[]
  if self.db.scalar(select(func.count()).select_from(Invoice).where(Invoice.user_id==user.id,Invoice.status=='Pendente',Invoice.deleted_at.is_(None))):actions.append({'label':'Emitir ou revisar Nota Fiscal','href':'/notas-fiscais'})
  if any(x.expected_date<=today for x in payments):actions.append({'label':'Registrar recebimento pendente','href':'/financeiro'})
  if not self.db.scalar(select(func.count()).select_from(Expense).where(Expense.user_id==user.id,Expense.competencia>=month,Expense.competencia<end,Expense.deleted_at.is_(None))):actions.append({'label':'Cadastrar despesas do mês','href':'/despesas/nova'})
  if reserved<taxes:alerts.append('A reserva tributária está abaixo da estimativa do mês.');actions.append({'label':'Revisar reserva tributária','href':'/impostos'})
  alerts=alerts[:5];insights=self.insights(user.id,received,prev_start,month,month_shifts,contractors,net);activity=self.activity(user.id);calendar=self.calendar(future_shifts,payments,user.id,today)
  goal_value=self.sum(Receivable.received_value,*active_rec,Receivable.received_date>=prev_start,Receivable.received_date<month);goal_value=goal_value or received;progress=float(received/goal_value*100) if goal_value else 0
  return {'date':str(today),'summary':{'receivable':float(pending),'tax_reserve_suggested':float(taxes),'estimated_net':float(pending-taxes-expenses)},'indicators':{'month_revenue':float(received),'net_profit':float(net),'completed_shifts':sum(1 for x in month_shifts if x.date<=today),'next_payment':float(payments[0].remaining_balance) if payments else 0,'next_shift':str(future_shifts[0].date) if future_shifts else None,'month_expenses':float(expenses),'tax_reserved':float(reserved)},'agenda':[{'id':str(x.id),'date':str(x.date),'time':str(x.start_time)[:5],'hospital':contractors.get(x.contractor_id,'Contratante'),'specialty':x.specialty,'value':float(x.gross_value)} for x in future_shifts],'payments':[{'id':str(x.id),'contractor':contractors.get(x.contractor_id,'Contratante'),'value':float(x.remaining_balance),'date':str(x.expected_date),'days':(x.expected_date-today).days} for x in payments],'actions':actions[:4] or [{'label':'Nenhuma pendência importante hoje','href':'/dashboard'}],'alerts':alerts,'insights':insights,'comparisons':comparisons,'goal':{'target':float(goal_value),'current':float(received),'progress':progress,'source':'Referência baseada na receita recebida do mês anterior.'},'calendar':calendar,'charts':{'revenue':[{'label':x['label'],'value':x['revenue']} for x in comparisons[::-1]],'profit':[{'label':x['label'],'value':x['profit']} for x in comparisons[::-1]],'cashflow':cash['series'][-30:]},'activity':activity,'message':self.message(net,progress,alerts)}
 def period_net(self,user,start,end):
  revenue=self.sum(Receivable.received_value,Receivable.user_id==user,Receivable.received_date>=start,Receivable.received_date<end,Receivable.deleted_at.is_(None));expenses=self.sum(Expense.valor,Expense.user_id==user,Expense.competencia>=start,Expense.competencia<end,Expense.deleted_at.is_(None),Expense.status!='Cancelado');taxes=self.sum(TaxEstimation.valor_estimado,TaxEstimation.user_id==user,TaxEstimation.competencia>=start,TaxEstimation.competencia<end,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado');return revenue-expenses-taxes
 @staticmethod
 def comparison(label,shifts,revenue,profit):return {'label':label,'revenue':float(revenue),'profit':float(profit),'hours':float(sum((x.duration_hours for x in shifts),Decimal(0))),'shifts':len(shifts)}
 def insights(self,user,revenue,prev_start,month,shifts,contractors,net):
  previous=self.sum(Receivable.received_value,Receivable.user_id==user,Receivable.received_date>=prev_start,Receivable.received_date<month,Receivable.deleted_at.is_(None));items=[]
  if previous:items.append(f'Seu faturamento variou {(revenue-previous)/previous*100:.0f}% em relação ao mês anterior.')
  totals={}
  for x in shifts:totals[x.contractor_id]=totals.get(x.contractor_id,Decimal(0))+x.gross_value
  total=sum(totals.values(),Decimal(0))
  if total and totals:
   key=max(totals,key=totals.get);items.append(f'{contractors.get(key,"Seu principal contratante")} representa {totals[key]/total*100:.0f}% da receita prevista em plantões deste mês.')
  if net>0:items.append('Seu resultado líquido estimado do mês permanece positivo.')
  return items[:4] or ['Registre movimentações para receber comparativos financeiros úteis.']
 def activity(self,user):
  rows=[]
  sources=[('Plantão cadastrado',Shift,Shift.title),('Recebimento registrado',Receivable,Receivable.status),('Nota Fiscal registrada',Invoice,Invoice.number),('Despesa criada',Expense,Expense.titulo)]
  for kind,model,label in sources:
   for x in self.db.scalars(select(model).where(model.user_id==user,model.deleted_at.is_(None)).order_by(model.created_at.desc()).limit(3)):rows.append({'type':kind,'description':str(getattr(x,label.key) or kind),'at':x.created_at.isoformat()})
  return sorted(rows,key=lambda x:x['at'],reverse=True)[:6]
 def calendar(self,shifts,payments,user,today):
  events=[{'date':str(x.date),'type':'Plantão','label':x.title or x.type} for x in shifts]+[{'date':str(x.expected_date),'type':'Recebimento','label':f'R$ {x.remaining_balance}'} for x in payments]
  for x in self.db.scalars(select(Expense).where(Expense.user_id==user,Expense.data_vencimento>=today,Expense.data_vencimento<=today+timedelta(days=31),Expense.deleted_at.is_(None),Expense.status!='Cancelado').limit(20)):events.append({'date':str(x.data_vencimento),'type':'Despesa','label':x.titulo})
  return events
 @staticmethod
 def message(net,progress,alerts):
  if not alerts and net>0:return 'Seu fluxo financeiro está saudável neste mês.'
  if progress>=80:return 'Você está próximo da sua referência mensal de receita.'
  if net>0:return 'Seu resultado permanece positivo; acompanhe as pendências destacadas.'
  return 'Há pontos financeiros que merecem sua atenção hoje.'
