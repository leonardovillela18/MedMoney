from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.tax import TaxEstimation, TaxSetting

class TaxRepository:
    def __init__(self, db:Session): self.db=db
    def setting(self,user_id): return self.db.scalar(select(TaxSetting).where(TaxSetting.user_id==user_id))
    def get(self,user_id,item_id): return self.db.scalar(select(TaxEstimation).where(TaxEstimation.id==item_id,TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None)))
    def list(self,user_id,page,size,status=None,competence=None):
        q=select(TaxEstimation).where(TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None))
        if status:q=q.where(TaxEstimation.status==status)
        if competence:q=q.where(TaxEstimation.competencia>=competence,TaxEstimation.competencia<self.next_month(competence))
        q=q.order_by(TaxEstimation.competencia.desc(),TaxEstimation.created_at.desc())
        return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
    @staticmethod
    def next_month(value): return value.replace(year=value.year+(value.month==12),month=1 if value.month==12 else value.month+1,day=1)
