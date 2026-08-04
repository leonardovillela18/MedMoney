from collections import defaultdict
from datetime import datetime,timedelta
from decimal import Decimal
from app.services.alerts.base import AlertCandidate as A
def alert(tipo,categoria,titulo,descricao,prioridade,acao,url,origem,reference):return A(tipo,categoria,titulo,descricao,prioridade,acao,url,origem,reference)
class ReceivableRule:
 def evaluate(self,c):
  rows=[]
  for x in c.receivables:
   name=c.recurring_incomes.get(x.recurring_income_id) or c.contractors.get(x.contractor_id,'pagamento')
   if x.remaining_balance>0 and x.expected_date<c.today and x.status!='Cancelado':rows.append(alert('Recebimento atrasado','Recebimentos',f'Recebimento de {name} está atrasado',f'Este atraso representa R$ {x.remaining_balance:,.2f} pendentes.','Alta','Cobrar contratante',f'/financeiro','Recebimento',f'overdue:{x.id}'))
   if x.remaining_balance>0 and x.expected_date==c.today:rows.append(alert('Pagamento previsto para hoje','Recebimentos',f'Pagamento de {name} previsto para hoje',f'O valor esperado é R$ {x.remaining_balance:,.2f}.','Média','Registrar recebimento',f'/financeiro','Recebimento',f'due-today:{x.id}'))
   if x.remaining_balance>0 and x.expected_date==c.today+timedelta(days=1):rows.append(alert('Pagamento vencendo amanhã','Recebimentos',f'Pagamento de {name} previsto amanhã',f'O valor esperado é R$ {x.remaining_balance:,.2f}.','Média','Acompanhar pagamento',f'/financeiro','Recebimento',f'due-tomorrow:{x.id}'))
  return rows
class InvoiceRule:
 def evaluate(self,c):
  rows=[];receivable_shifts={x.shift_id for x in c.receivables}
  for x in c.invoices:
   if x.status=='Pendente':rows.append(alert('Nota Fiscal pendente','Notas Fiscais',f'Nota {x.number} está pendente',f'A nota de R$ {x.service_value:,.2f} ainda requer acompanhamento.','Média','Emitir ou revisar Nota Fiscal','/notas-fiscais','Nota Fiscal',f'invoice-pending:{x.id}'))
   if x.shift_id not in receivable_shifts:rows.append(alert('Nota sem recebimento','Notas Fiscais',f'Nota {x.number} não possui recebimento associado',f'O valor de R$ {x.service_value:,.2f} não aparece nos recebimentos.','Alta','Cadastrar recebimento','/financeiro','Nota Fiscal',f'invoice-no-receivable:{x.id}'))
  return rows
class ShiftRule:
 def evaluate(self,c):
  rows=[]
  for x in c.shifts:
   event_at=datetime.combine(x.date,x.start_time);hours=(event_at-datetime.now()).total_seconds()/3600
   if x.status=='Agendado' and 0<=hours<=48:
    surgery=x.type=='Cirurgia';kind='Cirurgia' if surgery else 'Plantão';url=f'/cirurgias/{x.id}' if surgery else f'/plantoes/{x.id}'
    rows.append(alert(f'{kind} nas próximas 48 horas','Agenda',f'{x.title or kind} está próximo',f'{kind} agendado para {x.date.strftime("%d/%m/%Y")} às {x.start_time.strftime("%H:%M")}.','Alta',f'Ver {kind.lower()}',url,kind,f'upcoming-event:{x.id}'))
   if not x.expected_payment_date:rows.append(alert('Plantão sem previsão de pagamento','Plantões',f'{x.title or x.type} sem previsão de pagamento',f'O plantão de R$ {x.gross_value:,.2f} não possui data esperada.','Média','Informar previsão de pagamento',f'/plantoes/{x.id}/editar','Plantão',f'shift-no-payment:{x.id}'))
   if not x.contractor_id:rows.append(alert('Plantão sem contratante','Plantões','Plantão sem contratante',f'O plantão de {x.date} precisa de contratante.','Alta','Atualizar plantão',f'/plantoes/{x.id}/editar','Plantão',f'shift-no-contractor:{x.id}'))
   if x.gross_value<=0:rows.append(alert('Plantão sem valor','Plantões','Plantão sem valor financeiro',f'O plantão de {x.date} não possui valor válido.','Alta','Atualizar valor do plantão',f'/plantoes/{x.id}/editar','Plantão',f'shift-no-value:{x.id}'))
  shift_ids={x.id for x in c.shifts}
  for x in c.receivables:
   if x.shift_id and x.shift_id not in shift_ids:rows.append(alert('Recebimento sem plantão','Recebimentos','Recebimento sem plantão válido',f'O recebimento de R$ {x.expected_value:,.2f} perdeu sua referência operacional.','Crítica','Revisar recebimento','/financeiro','Recebimento',f'receivable-no-shift:{x.id}'))
  return rows
class TaxRule:
 def evaluate(self,c):
  estimated=sum((x.valor_estimado for x in c.taxes if x.status=='Estimado'),Decimal(0));reserved=sum((x.valor_estimado for x in c.taxes if x.status in ('Reservado','Pago')),Decimal(0))
  return [alert('Reserva tributária insuficiente','Tributação','Reserva tributária abaixo da estimativa',f'Faltam R$ {max(Decimal(0),estimated-reserved):,.2f} para cobrir as estimativas atuais.','Alta','Revisar reserva tributária','/impostos','Tributação',f'tax-reserve:{c.today:%Y-%m}')] if estimated>reserved else []
class CashflowRule:
 def evaluate(self,c):
  events=[]
  for x in c.receivables:
   if x.remaining_balance>0:events.append((x.expected_date,x.remaining_balance))
  for x in c.expenses:
   if x.status!='Pago':events.append((x.data_vencimento,-x.valor))
  balance=Decimal(0)
  for when,value in sorted(events,key=lambda x:x[0]):
   balance+=value
   if when>=c.today and balance<0:return [alert('Fluxo de caixa negativo previsto','Fluxo de Caixa','Saldo negativo previsto',f'O saldo projetado chega a R$ {balance:,.2f} em {when.strftime("%d/%m/%Y")}.','Crítica','Revisar fluxo de caixa','/fluxo-de-caixa','Fluxo de Caixa',f'negative-cashflow:{when}')]
  return []
class GoalRule:
 def evaluate(self,c):
  rows=[]
  for x in c.goals:
   if x.status=='Concluída':rows.append(alert('Meta concluída','Metas',f'Meta concluída: {x.titulo}',f'A meta atingiu {x.percentual:.1f}% com dados reais.','Baixa','Revisar resultado da meta',f'/metas/{x.id}','Meta',f'goal-complete:{x.id}'))
   elif x.status=='Atrasada' or (x.data_final>=c.today and x.percentual<Decimal(50) and (x.data_final-c.today).days<=7):rows.append(alert('Meta em risco','Metas',f'Meta em risco: {x.titulo}',f'Progresso atual de {x.percentual:.1f}% com {(x.data_final-c.today).days} dias restantes.','Alta','Revisar Meta',f'/metas/{x.id}','Meta',f'goal-risk:{x.id}'))
  return rows
class ExpenseRule:
 def evaluate(self,c):
  rows=[];values=[x.valor for x in c.expenses];average=sum(values,Decimal(0))/len(values) if values else Decimal(0)
  for x in c.expenses:
   if average and x.valor>average*2:rows.append(alert('Despesa acima da média','Despesas',f'Despesa elevada: {x.titulo}',f'R$ {x.valor:,.2f} representa mais que o dobro da média de R$ {average:,.2f}.','Alta','Revisar despesa',f'/despesas/{x.id}','Despesa',f'high-expense:{x.id}'))
   if x.status in ('Pendente','Atrasado') and x.data_vencimento<=c.today+timedelta(days=3):
    days=(x.data_vencimento-c.today).days;when='está atrasada' if days<0 else 'vence hoje' if days==0 else f'vence em {days} dias'
    rows.append(alert('Despesa aguardando pagamento','Despesas',f'{x.titulo} {when}',f'Confirme se a despesa de R$ {x.valor:,.2f} foi paga. Ela permanecerá nas notificações até a confirmação.','Alta' if days<0 else 'Média','Marcar como pago',f'/despesas/{x.id}','Despesa',f'expense-due:{x.id}'))
  return rows
class ContractorRule:
 def evaluate(self,c):
  rows=[];totals=defaultdict(Decimal)
  for x in c.shifts:totals[x.contractor_id]+=x.gross_value
  total=sum(totals.values(),Decimal(0))
  for key,value in totals.items():
   if total and value/total>Decimal('.5'):rows.append(alert('Dependência de contratante','Contratantes',f'{c.contractors.get(key,"Contratante")} concentra a receita',f'Esse contratante representa {value/total*100:.0f}% da receita de plantões.','Alta','Diversificar contratantes','/contratantes','Contratante',f'contractor-concentration:{key}'))
  delays=defaultdict(list)
  for x in c.receivables:
   if x.received_date:delays[x.contractor_id].append((x.received_date-x.expected_date).days)
  for key,items in delays.items():
   average=sum(items)/len(items)
   if average>7:rows.append(alert('Hospital com histórico de atrasos','Contratantes',f'{c.contractors.get(key,"Contratante")} costuma atrasar',f'O atraso médio registrado é de {average:.0f} dias.','Alta','Negociar prazo de pagamento','/contratantes','Contratante',f'contractor-delay:{key}'))
  return rows
class FinancialInsightRule:
 TYPES={'Receita caiu':('Receita caiu','Recebimentos','Alta','Revisar recebimentos','/insights'),'Lucro caiu':('Lucro caiu','Fluxo de Caixa','Alta','Revisar despesas e margem','/insights'),'Categoria que mais cresce':('Despesas cresceram','Despesas','Média','Revisar despesas','/despesas/relatorios')}
 def evaluate(self,c):
  rows=[]
  for x in c.insights:
   if x.tipo in self.TYPES:
    tipo,category,priority,action,url=self.TYPES[x.tipo];rows.append(alert(tipo,category,x.titulo,x.descricao,priority,action,url,'Financial Insights',f'financial-insight:{x.id}'))
  return rows
class ProfileRule:
 def evaluate(self,c):
  required=('name','crm','crm_uf','email','cnpj','phone','city','state','specialty');missing=[x for x in required if not getattr(c.user,x,None)]
  return [alert('Cadastro incompleto','Sistema','Cadastro profissional incompleto',f'Campos pendentes: {", ".join(missing)}.','Média','Atualizar Cadastro','/perfil','Sistema',f'incomplete-profile:{c.user_id}')] if missing else []
RULES=(ReceivableRule(),InvoiceRule(),ShiftRule(),TaxRule(),CashflowRule(),GoalRule(),ExpenseRule(),ContractorRule(),FinancialInsightRule(),ProfileRule())
