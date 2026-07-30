import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.contractor_repository import ContractorRepository
class ContractorService:
    def __init__(self,db:Session):self.db=db;self.repo=ContractorRepository(db)
    def list(self,*args,**kwargs):return self.repo.list(*args,**kwargs)
    def get(self,user_id:uuid.UUID,item_id:uuid.UUID):
        item=self.repo.get(user_id,item_id)
        if not item:raise HTTPException(status_code=404,detail='Contratante não encontrado.')
        return item
    def normalize(self,data,current=None):
        from app.services.location_service import validate_location
        if data.get('city') and not data.get('city_ibge_code') and not current:raise HTTPException(422,'Selecione uma cidade válida da lista.')
        if current and data.get('city')==current.city and not data.get('city_ibge_code'):data['city_ibge_code']=current.city_ibge_code
        if data.get('state') or data.get('city_ibge_code'):
            data['state'],data['city'],data['city_ibge_code']=validate_location(data.get('state'),data.get('city'),data.get('city_ibge_code'))
        return data
    def create(self,user_id:uuid.UUID,data:dict):return self.repo.create(user_id,self.normalize(data))
    def update(self,user_id:uuid.UUID,item_id:uuid.UUID,data:dict):
        item=self.get(user_id,item_id);return self.repo.update(item,self.normalize(data,item))
    def delete(self,user_id:uuid.UUID,item_id:uuid.UUID):
        item=self.get(user_id,item_id);item.deleted_at=datetime.now(timezone.utc);self.repo.db.commit()
