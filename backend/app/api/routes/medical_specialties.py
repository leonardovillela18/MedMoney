import uuid
from pydantic import BaseModel,model_validator
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.medical_specialty import MedicalSpecialty,UserSpecialty
from app.models.user import User
class UserSpecialtiesInput(BaseModel):
    primary_id:uuid.UUID;secondary_id:uuid.UUID|None=None
    @model_validator(mode='after')
    def distinct(self):
        if self.secondary_id==self.primary_id:raise ValueError('A especialidade secundária deve ser diferente da principal.')
        return self
router=APIRouter(tags=['Especialidades Médicas'])
@router.get('/medical-specialties')
def list_specialties(active:bool=True,_:User=Depends(current_user),db:Session=Depends(get_db)):
    q=select(MedicalSpecialty)
    if active:q=q.where(MedicalSpecialty.active.is_(True))
    return [{'id':x.id,'code':x.code,'name':x.name,'active':x.active} for x in db.scalars(q.order_by(MedicalSpecialty.name))]
@router.get('/users/me/specialties')
def mine(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=list(db.execute(select(UserSpecialty,MedicalSpecialty).join(MedicalSpecialty,MedicalSpecialty.id==UserSpecialty.specialty_id).where(UserSpecialty.user_id==user.id)))
    return {row.UserSpecialty.priority.lower():{'id':row.MedicalSpecialty.id,'name':row.MedicalSpecialty.name} for row in rows}
@router.put('/users/me/specialties')
def save(payload:UserSpecialtiesInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
    ids=[payload.primary_id]+([payload.secondary_id] if payload.secondary_id else []);items=list(db.scalars(select(MedicalSpecialty).where(MedicalSpecialty.id.in_(ids),MedicalSpecialty.active.is_(True))))
    if len(items)!=len(ids):raise HTTPException(422,'Especialidade inexistente ou inativa.')
    for row in db.scalars(select(UserSpecialty).where(UserSpecialty.user_id==user.id)):db.delete(row)
    db.flush();db.add(UserSpecialty(user_id=user.id,specialty_id=payload.primary_id,priority='PRIMARY'))
    if payload.secondary_id:db.add(UserSpecialty(user_id=user.id,specialty_id=payload.secondary_id,priority='SECONDARY'))
    user.specialty=next(x.name for x in items if x.id==payload.primary_id);db.commit();return mine(user,db)
