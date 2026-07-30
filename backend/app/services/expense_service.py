from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.expense import Expense,ExpenseCategory
from app.repositories.expense_repository import ExpenseRepository
from app.services.recurrence import next_occurrence
DEFAULT_CATEGORIES=['Contabilidade','Impostos','Combustível','Pedágio','Estacionamento','Alimentação','Hospedagem','Cursos','Congressos','Livros','Softwares','Internet','Telefone','Equipamentos','Marketing','Secretária','Plano de Saúde','Seguro','Consultório','Aluguel','Material Médico','Outros']
class ExpenseService:
 """Owns expense rules, recurrence and integrations; receipt extraction remains replaceable for future OCR."""
 def __init__(self,db:Session):self.db=db;self.repo=ExpenseRepository(db)
 def categories(self,user):
  if not self.db.scalar(select(func.count()).select_from(ExpenseCategory).where(ExpenseCategory.user_id==user)):
   self.db.add_all([ExpenseCategory(user_id=user,nome=x) for x in DEFAULT_CATEGORIES]);self.db.commit()
  return list(self.db.scalars(select(ExpenseCategory).where(ExpenseCategory.user_id==user,ExpenseCategory.deleted_at.is_(None),ExpenseCategory.ativa.is_(True)).order_by(ExpenseCategory.nome)))
 def add_category(self,user,data):x=ExpenseCategory(user_id=user,**data);self.db.add(x);self.db.commit();self.db.refresh(x);return x
 def validate(self,user,data):
  if data['tipo'] not in ('Fixa','Variável'):raise HTTPException(422,'Tipo inválido.')
  if data['status'] not in ('Pendente','Pago','Atrasado','Cancelado'):raise HTTPException(422,'Status inválido.')
  if data['forma_pagamento'] not in ('PIX','TED','Cartão','Boleto','Débito','Dinheiro','Outro'):raise HTTPException(422,'Forma de pagamento inválida.')
  if data.get('intervalo_recorrencia') not in (None,'Mensal','Semanal','Anual','Trimestral','Semestral'):raise HTTPException(422,'Recorrência inválida.')
  if not self.db.scalar(select(ExpenseCategory).where(ExpenseCategory.id==data['categoria_id'],ExpenseCategory.user_id==user,ExpenseCategory.deleted_at.is_(None))):raise HTTPException(422,'Categoria inválida.')
 def list(self,*args):
  items,total=self.repo.list(*args)
  changed=False
  for x in items:
   status=self.effective_status(x.status,x.data_vencimento)
   if status!=x.status:x.status=status;changed=True
  if changed:self.db.commit()
  return items,total
 def get(self,user,id):
  x=self.repo.get(user,id)
  if not x:raise HTTPException(404,'Despesa não encontrada.')
  if x.status=='Pendente' and x.data_vencimento<date.today():x.status='Atrasado';self.db.commit()
  return x
 @staticmethod
 def next_month(value):
  return date(value.year+(value.month==12),1 if value.month==12 else value.month+1,1)
 @classmethod
 def in_month(cls,value,month_start):return month_start<=value<cls.next_month(month_start)
 @staticmethod
 def next_recurrence(value,frequency,anchor_day=None):
  return next_occurrence(value,frequency,anchor_day)
 @staticmethod
 def effective_status(status,due,today=None):
  today=today or date.today()
  if status in ('Pago','Cancelado'):return status
  return 'Atrasado' if due<today else 'Pendente'
 def refresh_status(self,x):
  status=self.effective_status(x.status,x.data_vencimento)
  if status!=x.status:x.status=status;self.db.commit()
  return x
 def create(self,user,data):
  self.validate(user,data)
  if data['status']=='Pago' and not data.get('data_pagamento'):raise HTTPException(422,'Confirme o pagamento pela aÃ§Ã£o Marcar como pago.')
  data['status']=self.effective_status(data['status'],data['data_vencimento'])
  x=Expense(user_id=user,**data);self.db.add(x);self.db.commit();self.db.refresh(x);self.sync(x)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user)
  return x
 def update(self,user,id,data):
  x=self.get(user,id);self.validate(user,data)
  if x.status=='Pago' and (Decimal(data['valor'])!=x.valor or data['data_vencimento']!=x.data_vencimento):raise HTTPException(409,'Uma despesa paga nÃ£o pode ter valor ou vencimento alterados sem um ajuste explÃ­cito.')
  if data['status']=='Pago' and x.status!='Pago':raise HTTPException(422,'Use a aÃ§Ã£o Marcar como pago.')
  data['status']=self.effective_status(data['status'],data['data_vencimento'])
  for k,v in data.items():setattr(x,k,v)
  self.db.commit();self.db.refresh(x);self.sync(x)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user);return x
 def mark_paid(self,user,id,payment_date=None):
  x=self.get(user,id)
  if x.status=='Cancelado':raise HTTPException(422,'Uma despesa cancelada nÃ£o pode ser paga.')
  if x.status=='Pago':return x
  x.status='Pago';x.data_pagamento=payment_date or date.today();self.db.commit();self.db.refresh(x);self.sync(x)
  from app.services.audit_service import AuditService
  AuditService.record(self.db,'EXPENSE_MARKED_PAID','Expense',user_id=user,entity_id=x.id)
  return x
 def delete(self,user,id):
  x=self.get(user,id);x.deleted_at=datetime.now(timezone.utc);self.db.commit()
  from app.services.cashflow_service import CashflowService
  flow=CashflowService(self.db);flow.sync_source(user,'Despesa',x.id,x.data_vencimento,'Despesa Prevista',x.titulo,'Despesas',-x.valor,'Cancelado');self.db.commit();flow.recalculate(user)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user)
 def sync(self,x):
  from app.services.cashflow_service import CashflowService
  kind='Despesa Paga' if x.status=='Pago' else 'Despesa Prevista';when=x.data_pagamento if x.status=='Pago' and x.data_pagamento else x.data_vencimento;status='Confirmado' if x.status=='Pago' else 'Cancelado' if x.status=='Cancelado' else 'Previsto';flow=CashflowService(self.db);flow.sync_source(x.user_id,'Despesa',x.id,when,kind,x.titulo,'Despesas',-x.valor,status);self.db.commit();flow.recalculate(x.user_id)
 def generate_recurrence(self,parent):
  """Materialize at most the next occurrence, when explicitly invoked by a job."""
  latest=self.db.scalar(select(Expense).where(Expense.recurrence_parent_id==parent.id,Expense.deleted_at.is_(None)).order_by(Expense.data_vencimento.desc()))
  base=latest or parent;due=self.next_recurrence(base.data_vencimento,parent.intervalo_recorrencia,parent.data_vencimento.day)
  existing=self.db.scalar(select(Expense).where(Expense.user_id==parent.user_id,Expense.recurrence_parent_id==parent.id,Expense.data_vencimento==due,Expense.deleted_at.is_(None)))
  if existing:return existing
  x=Expense(user_id=parent.user_id,titulo=parent.titulo,descricao=parent.descricao,categoria_id=parent.categoria_id,valor=parent.valor,tipo=parent.tipo,forma_pagamento=parent.forma_pagamento,fornecedor=parent.fornecedor,competencia=due.replace(day=1),data_vencimento=due,status='Pendente',recorrente=True,intervalo_recorrencia=parent.intervalo_recorrencia,recurrence_parent_id=parent.id,centro_custo=parent.centro_custo,observacoes=parent.observacoes);self.db.add(x);self.db.flush();self.sync(x);self.db.commit();return x
 def dashboard(self,user):
  today=date.today();start=today.replace(day=1);prev=(start-timedelta(days=1)).replace(day=1);items=list(self.db.scalars(select(Expense).where(Expense.user_id==user,Expense.deleted_at.is_(None),Expense.status!='Cancelado')));month=[x for x in items if self.in_month(x.competencia,start)];previous=[x for x in items if self.in_month(x.competencia,prev)];total=sum((x.valor for x in month),Decimal(0));fixed=sum((x.valor for x in month if x.tipo=='Fixa'),Decimal(0));variable=total-fixed;cats={};suppliers={}
  names={x.id:x.nome for x in self.categories(user)}
  for x in month:cats[names.get(x.categoria_id,'Outros')]=cats.get(names.get(x.categoria_id,'Outros'),Decimal(0))+x.valor;suppliers[x.fornecedor or 'Não informado']=suppliers.get(x.fornecedor or 'Não informado',Decimal(0))+x.valor
  prev_total=sum((x.valor for x in previous),Decimal(0));economy=max(Decimal(0),prev_total-total);largest=max(cats,key=cats.get) if cats else 'Sem despesas';change=float((total-prev_total)/prev_total*100) if prev_total else 0;insights=[f'{largest} é sua maior categoria de despesas.']
  if prev_total:insights.append(f'Suas despesas variaram {change:.0f}% em relação ao mês anterior.')
  return {'total_month':float(total),'fixed':float(fixed),'variable':float(variable),'largest_category':largest,'estimated_savings':float(economy),'categories':[{'name':k,'value':float(v)} for k,v in sorted(cats.items(),key=lambda x:x[1],reverse=True)],'suppliers':[{'name':k,'value':float(v)} for k,v in sorted(suppliers.items(),key=lambda x:x[1],reverse=True)[:5]],'monthly_change':change,'insights':insights}
