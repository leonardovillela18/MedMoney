import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.shift import Shift
class ShiftRepository:
 def __init__(self,db:Session):self.db=db
 def list(self,user_id:uuid.UUID,page:int,size:int,filters:dict):
  q=select(Shift).where(Shift.user_id==user_id,Shift.deleted_at.is_(None))
  for field in ('contractor_id','city','specialty','status','type'):
   if filters.get(field):q=q.where(getattr(Shift,field)==filters[field])
  if filters.get('search'):q=q.where(Shift.title.ilike(f"%{filters['search']}%"))
  if filters.get('date_from'):q=q.where(Shift.date>=filters['date_from'])
  if filters.get('date_to'):q=q.where(Shift.date<=filters['date_to'])
  if filters.get('min_value') is not None:q=q.where(Shift.gross_value>=filters['min_value'])
  if filters.get('max_value') is not None:q=q.where(Shift.gross_value<=filters['max_value'])
  sort={'recent':Shift.date.desc(),'oldest':Shift.date.asc(),'value_desc':Shift.gross_value.desc(),'value_asc':Shift.gross_value.asc(),'duration':Shift.duration_hours.desc()}.get(filters.get('order','recent'),Shift.date.desc());q=q.order_by(sort)
  return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
 def get(self,user_id,item_id):return self.db.scalar(select(Shift).where(Shift.id==item_id,Shift.user_id==user_id,Shift.deleted_at.is_(None)))
 def save(self,item):self.db.add(item);self.db.commit();self.db.refresh(item);return item
