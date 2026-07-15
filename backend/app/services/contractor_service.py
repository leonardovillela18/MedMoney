import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.contractor_repository import ContractorRepository
class ContractorService:
    def __init__(self,db:Session):self.repo=ContractorRepository(db)
    def list(self,*args,**kwargs):return self.repo.list(*args,**kwargs)
    def get(self,user_id:uuid.UUID,item_id:uuid.UUID):
        item=self.repo.get(user_id,item_id)
        if not item:raise HTTPException(status_code=404,detail='Contratante não encontrado.')
        return item
    def create(self,user_id:uuid.UUID,data:dict):return self.repo.create(user_id,data)
    def update(self,user_id:uuid.UUID,item_id:uuid.UUID,data:dict):return self.repo.update(self.get(user_id,item_id),data)
    def delete(self,user_id:uuid.UUID,item_id:uuid.UUID):
        item=self.get(user_id,item_id);item.deleted_at=datetime.now(timezone.utc);self.repo.db.commit()
