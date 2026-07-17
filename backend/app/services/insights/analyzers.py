from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from app.services.insights.base import InsightCandidate as C
def candidate(tipo,title,description,category,severity,priority,action,reference):return C(tipo,title,description,category,severity,priority,action,reference)
class RevenueTrendAnalyzer:
 def analyze(self,c):
  current,previous=c.revenue(c.month,c.next_month),c.revenue(c.previous,c.month)
  if not previous:return []
  change=(current-previous)/previous*100;direction='cresceu' if change>=0 else 'caiu';severity='Informativo' if change>=0 else 'Atenção';return [candidate(f'Receita {direction}',f'Receita {direction} {abs(change):.0f}%',f'O faturamento recebido foi de R$ {current:,.2f}, contra R$ {previous:,.2f} no mês anterior.','Receita',severity,70 if change<0 else 45,'Revisar recebimentos' if change<0 else 'Manter estratégia de receita',f'revenue-trend:{c.month}')]
class ProfitTrendAnalyzer:
 def analyze(self,c):
  current,previous=c.profit(c.month,c.next_month),c.profit(c.previous,c.month)
  if not previous:return []
  change=(current-previous)/abs(previous)*100;direction='cresceu' if change>=0 else 'caiu';reason=' devido ao aumento das despesas' if change<0 and c.expense(c.month,c.next_month)>c.expense(c.previous,c.month) else '';return [candidate(f'Lucro {direction}',f'Lucro {direction} {abs(change):.0f}%',f'O lucro líquido estimado passou de R$ {previous:,.2f} para R$ {current:,.2f}{reason}.','Lucro','Informativo' if change>=0 else 'Atenção',80 if change<0 else 50,'Revisar despesas' if change<0 else 'Acompanhar margem',f'profit-trend:{c.month}')]
class ConcentrationAnalyzer:
 def analyze(self,c):
  totals=defaultdict(Decimal)
  for x in c.period(c.shifts,'date',c.month,c.next_month):totals[x.contractor_id]+=x.gross_value
  total=sum(totals.values(),Decimal(0))
  if not total:return []
  key=max(totals,key=totals.get);share=totals[key]/total*100;tier=max((x for x in (30,40,50,60,70) if share>=x),default=0)
  if not tier:return []
  severity='Crítico' if tier>=60 else 'Atenção';name=c.contractors.get(key,'Um contratante');return [candidate('Dependência de contratante',f'{share:.0f}% da receita depende de {name}',f'{name} concentra R$ {totals[key]:,.2f} da receita prevista em plantões neste mês.','Contratantes',severity,60+tier//2,'Diversificar contratantes',f'concentration:{c.month}:{key}')]
class ProfitabilityAnalyzer:
 def analyze(self,c):
  shifts=[x for x in c.shifts if x.gross_value>0]
  if not shifts:return []
  results=[];best=max(shifts,key=lambda x:x.gross_value/(x.duration_hours or Decimal(1)));results.append(candidate('Plantão mais rentável','Plantão com maior retorno por hora',f'{best.title or best.type} gerou R$ {best.gross_value/(best.duration_hours or Decimal(1)):,.2f} por hora.','Plantões','Informativo',35,'Priorizar plantões com melhor retorno',f'best-shift:{best.id}'))
  def grouped(key,title,tipo,ref):
   groups=defaultdict(lambda:[Decimal(0),Decimal(0)])
   for x in shifts:groups[key(x)][0]+=x.gross_value;groups[key(x)][1]+=x.duration_hours or Decimal(0)
   valid={k:v[0]/v[1] for k,v in groups.items() if k and v[1]};
   if not valid:return None
   k=max(valid,key=valid.get);return candidate(tipo,title.format(k=k),f'O retorno médio é de R$ {valid[k]:,.2f} por hora.','Plantões','Informativo',30,'Considerar disponibilidade nesse perfil',f'{ref}:{k}')
  for x in [grouped(lambda s:s.specialty,'{k} é a especialidade mais rentável','Especialidade mais lucrativa','best-specialty'),grouped(lambda s:s.date.strftime('%A'),'{k} é o dia mais rentável','Dia mais lucrativo','best-weekday'),grouped(lambda s:f'{s.start_time.hour:02d}h','Plantões iniciados às {k} são os mais rentáveis','Horário mais lucrativo','best-hour')]:
   if x:results.append(x)
  weeks=defaultdict(Decimal)
  for x in shifts:weeks[f'{x.date.isocalendar().year}-W{x.date.isocalendar().week:02d}']+=x.gross_value
  if weeks:
   k=max(weeks,key=weeks.get);results.append(candidate('Semana mais lucrativa',f'{k} foi a semana mais lucrativa',f'Os plantões dessa semana somaram R$ {weeks[k]:,.2f}.','Plantões','Informativo',25,'Comparar escala semanal',f'best-week:{k}'))
  contractor=defaultdict(Decimal)
  for x in shifts:contractor[x.contractor_id]+=x.gross_value
  k=max(contractor,key=contractor.get);results.append(candidate('Hospital mais lucrativo',f'{c.contractors.get(k,"Contratante")} lidera a receita',f'Os plantões somam R$ {contractor[k]:,.2f}.','Contratantes','Informativo',40,'Avaliar continuidade da parceria',f'best-contractor:{k}'));return results
class RecordMonthAnalyzer:
 def analyze(self,c):
  months=defaultdict(Decimal)
  for x in c.receivables:
   if x.received_date:months[x.received_date.strftime('%Y-%m')]+=x.received_value
  key=c.month.strftime('%Y-%m')
  if len(months)>1 and months.get(key,0)>=max(months.values()):return [candidate('Mês recorde','O mês atual bateu o recorde de receita',f'A receita recebida chegou a R$ {months[key]:,.2f}.','Receita','Informativo',55,'Acompanhar sustentabilidade do crescimento',f'record-month:{key}')]
  return []
class PaymentAnalyzer:
 def analyze(self,c):
  delays=defaultdict(list)
  for x in c.receivables:
   if x.received_date:delays[x.contractor_id].append((x.received_date-x.expected_date).days)
  if not delays:return []
  averages={k:sum(v)/len(v) for k,v in delays.items()};fast=min(averages,key=averages.get);slow=max(averages,key=averages.get);all_delays=[d for v in delays.values() for d in v];return [candidate('Tempo médio para pagamento',f'Pagamento leva em média {sum(all_delays)/len(all_delays):.0f} dias além do previsto',f'O maior atraso registrado foi de {max(all_delays)} dias.','Recebimentos','Atenção' if max(all_delays)>0 else 'Informativo',65,'Negociar prazo com contratantes atrasados',f'payment-delay:{c.month}'),candidate('Pontualidade de contratantes',f'{c.contractors.get(fast,"Contratante")} é o mais pontual',f'{c.contractors.get(slow,"Outro contratante")} possui a maior média de atraso.','Contratantes','Informativo',40,'Priorizar relações com bom histórico',f'payment-performance:{fast}:{slow}')]
class ExpenseAnalyzer:
 def analyze(self,c):
  current,previous=defaultdict(Decimal),defaultdict(Decimal)
  for x in c.expenses:
   target=current if c.month<=x.competencia<c.next_month else previous if c.previous<=x.competencia<c.month else None
   if target is not None:target[c.categories.get(x.categoria_id,'Outros')]+=x.valor
  results=[]
  growth={k:(v-previous[k])/previous[k]*100 for k,v in current.items() if previous[k]}
  if growth:
   k=max(growth,key=growth.get);results.append(candidate('Categoria que mais cresce',f'{k} aumentou {growth[k]:.0f}%',f'O gasto passou de R$ {previous[k]:,.2f} para R$ {current[k]:,.2f}.','Despesas','Atenção' if growth[k]>20 else 'Informativo',70,'Revisar despesas da categoria',f'expense-growth:{c.month}:{k}'))
  total=sum(current.values(),Decimal(0))
  if total:
   k=max(current,key=current.get);results.append(candidate('Maior despesa',f'{k} consome {current[k]/total*100:.0f}% das despesas',f'A categoria soma R$ {current[k]:,.2f} neste mês.','Despesas','Informativo',50,'Revisar maior categoria',f'top-expense:{c.month}:{k}'))
  suppliers=defaultdict(Decimal)
  for x in c.expenses:
   if x.fornecedor:suppliers[x.fornecedor]+=x.valor
  if suppliers:
   k=max(suppliers,key=suppliers.get);results.append(candidate('Fornecedor mais caro',f'{k} é o fornecedor de maior custo',f'O total registrado é R$ {suppliers[k]:,.2f}.','Despesas','Informativo',35,'Negociar condições com fornecedor',f'top-supplier:{k}'))
  recurring=sum(1 for x in c.expenses if x.recorrente)
  if recurring:results.append(candidate('Despesas recorrentes',f'{recurring} despesas recorrentes ativas',f'Esses compromissos impactam as projeções futuras de caixa.','Despesas','Informativo',30,'Revisar assinaturas e contratos',f'recurring-expenses:{c.month}'))
  return results
