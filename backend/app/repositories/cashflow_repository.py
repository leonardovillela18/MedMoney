from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.cashflow import CashflowProjection
class CashflowRepository:
 def __init__(self,db:Session):self.db=db
 def source(self,user,origin,origin_id):return self.db.scalar(select(CashflowProjection).where(CashflowProjection.user_id==user,CashflowProjection.origem==origin,CashflowProjection.origem_id==origin_id,CashflowProjection.deleted_at.is_(None)))
 def query(self,user,filters):
  q=select(CashflowProjection).where(CashflowProjection.user_id==user,CashflowProjection.deleted_at.is_(None))
  for key in ('categoria','origem','tipo','status','account_id','transaction_type'):
   if filters.get(key):q=q.where(getattr(CashflowProjection,key)==filters[key])
  if filters.get('date_from'):q=q.where(CashflowProjection.data>=filters['date_from'])
  if filters.get('date_to'):q=q.where(CashflowProjection.data<=filters['date_to'])
  if filters.get('min_value') is not None:q=q.where(CashflowProjection.valor>=filters['min_value'])
  if filters.get('max_value') is not None:q=q.where(CashflowProjection.valor<=filters['max_value'])
  if filters.get('search'):q=q.where(CashflowProjection.descricao.ilike(f"%{filters['search']}%"))
  return q.order_by(CashflowProjection.data.desc(),CashflowProjection.created_at.desc())
 def list(self,user,page,size,filters):
  q=self.query(user,filters);return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
