import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
class ContractorRepository:
    def __init__(self,db:Session):self.db=db
    def list(self,user_id:uuid.UUID,page:int,page_size:int,search:str|None,city:str|None,kind:str|None,active:bool|None,order:str):
        query=select(Contractor).where(Contractor.user_id==user_id,Contractor.deleted_at.is_(None))
        if search: query=query.where(Contractor.name.ilike(f'%{search}%'))
        if city: query=query.where(Contractor.city==city)
        if kind: query=query.where(Contractor.type==kind)
        if active is not None: query=query.where(Contractor.active==active)
        column={'name':Contractor.name,'created_at':Contractor.created_at,'city':Contractor.city}.get(order.lstrip('-'),Contractor.name); query=query.order_by(column.desc() if order.startswith('-') else column.asc())
        total=self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        return list(self.db.scalars(query.offset((page-1)*page_size).limit(page_size))),total
    def get(self,user_id:uuid.UUID,item_id:uuid.UUID): return self.db.scalar(select(Contractor).where(Contractor.id==item_id,Contractor.user_id==user_id,Contractor.deleted_at.is_(None)))
    def create(self,user_id:uuid.UUID,data:dict): item=Contractor(user_id=user_id,**data);self.db.add(item);self.db.commit();self.db.refresh(item);return item
    def update(self,item:Contractor,data:dict):
        for key,value in data.items():setattr(item,key,value)
        self.db.commit();self.db.refresh(item);return item
