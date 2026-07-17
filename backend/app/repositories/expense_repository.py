from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.expense import Expense
class ExpenseRepository:
 def __init__(self,db:Session):self.db=db
 def get(self,user,id):return self.db.scalar(select(Expense).where(Expense.id==id,Expense.user_id==user,Expense.deleted_at.is_(None)))
 def query(self,user,f):
  q=select(Expense).where(Expense.user_id==user,Expense.deleted_at.is_(None))
  for k in ('categoria_id','fornecedor','tipo','status','forma_pagamento','recorrente'):
   if f.get(k) is not None:q=q.where(getattr(Expense,k)==f[k])
  if f.get('date_from'):q=q.where(Expense.competencia>=f['date_from'])
  if f.get('date_to'):q=q.where(Expense.competencia<=f['date_to'])
  if f.get('min_value') is not None:q=q.where(Expense.valor>=f['min_value'])
  if f.get('max_value') is not None:q=q.where(Expense.valor<=f['max_value'])
  sort={'value_desc':Expense.valor.desc(),'value_asc':Expense.valor,'oldest':Expense.competencia,'recent':Expense.competencia.desc()}.get(f.get('order'),Expense.competencia.desc());return q.order_by(sort,Expense.created_at.desc())
 def list(self,user,page,size,f):
  q=self.query(user,f);return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
