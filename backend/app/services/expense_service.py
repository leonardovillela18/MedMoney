from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.expense import Expense,ExpenseCategory
from app.repositories.expense_repository import ExpenseRepository
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
 def list(self,*args):return self.repo.list(*args)
 def get(self,user,id):
  x=self.repo.get(user,id)
  if not x:raise HTTPException(404,'Despesa não encontrada.')
  if x.status=='Pendente' and x.data_vencimento<date.today():x.status='Atrasado';self.db.commit()
  return x
 def create(self,user,data):
  self.validate(user,data);x=Expense(user_id=user,**data);self.db.add(x);self.db.commit();self.db.refresh(x);self.sync(x)
  if x.recorrente:self.generate_recurrence(x)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user)
  return x
 def update(self,user,id,data):
  x=self.get(user,id);self.validate(user,data)
  for k,v in data.items():setattr(x,k,v)
  self.db.commit();self.db.refresh(x);self.sync(x)
  from app.services.insights.events import refresh_insights
  refresh_insights(self.db,user);return x
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
  increments={'Semanal':7,'Mensal':30,'Trimestral':91,'Semestral':182,'Anual':365};step=increments[parent.intervalo_recorrencia]
  existing=self.db.scalar(select(func.count()).select_from(Expense).where(Expense.recurrence_parent_id==parent.id)) or 0
  for i in range(existing+1,13):
   due=parent.data_vencimento+timedelta(days=step*i);x=Expense(user_id=parent.user_id,titulo=parent.titulo,descricao=parent.descricao,categoria_id=parent.categoria_id,valor=parent.valor,tipo=parent.tipo,forma_pagamento=parent.forma_pagamento,fornecedor=parent.fornecedor,competencia=due.replace(day=1),data_vencimento=due,status='Pendente',recorrente=True,intervalo_recorrencia=parent.intervalo_recorrencia,recurrence_parent_id=parent.id,centro_custo=parent.centro_custo,observacoes=parent.observacoes);self.db.add(x);self.db.flush();self.sync(x)
  self.db.commit()
 def dashboard(self,user):
  today=date.today();start=today.replace(day=1);prev=(start-timedelta(days=1)).replace(day=1);items=list(self.db.scalars(select(Expense).where(Expense.user_id==user,Expense.deleted_at.is_(None),Expense.status!='Cancelado')));month=[x for x in items if x.competencia>=start];previous=[x for x in items if prev<=x.competencia<start];total=sum((x.valor for x in month),Decimal(0));fixed=sum((x.valor for x in month if x.tipo=='Fixa'),Decimal(0));variable=total-fixed;cats={};suppliers={}
  names={x.id:x.nome for x in self.categories(user)}
  for x in month:cats[names.get(x.categoria_id,'Outros')]=cats.get(names.get(x.categoria_id,'Outros'),Decimal(0))+x.valor;suppliers[x.fornecedor or 'Não informado']=suppliers.get(x.fornecedor or 'Não informado',Decimal(0))+x.valor
  prev_total=sum((x.valor for x in previous),Decimal(0));economy=max(Decimal(0),prev_total-total);largest=max(cats,key=cats.get) if cats else 'Sem despesas';change=float((total-prev_total)/prev_total*100) if prev_total else 0;insights=[f'{largest} é sua maior categoria de despesas.']
  if prev_total:insights.append(f'Suas despesas variaram {change:.0f}% em relação ao mês anterior.')
  return {'total_month':float(total),'fixed':float(fixed),'variable':float(variable),'largest_category':largest,'estimated_savings':float(economy),'categories':[{'name':k,'value':float(v)} for k,v in sorted(cats.items(),key=lambda x:x[1],reverse=True)],'suppliers':[{'name':k,'value':float(v)} for k,v in sorted(suppliers.items(),key=lambda x:x[1],reverse=True)[:5]],'monthly_change':change,'insights':insights}
