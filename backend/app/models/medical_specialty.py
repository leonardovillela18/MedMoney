import uuid
from datetime import datetime
from sqlalchemy import Boolean,DateTime,ForeignKey,String,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class MedicalSpecialty(Base):
    __tablename__='medical_specialties';id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);code:Mapped[str]=mapped_column(String(80),unique=True,index=True);name:Mapped[str]=mapped_column(String(120),unique=True,index=True);active:Mapped[bool]=mapped_column(Boolean,default=True,index=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class UserSpecialty(Base):
    __tablename__='user_specialties';__table_args__=(UniqueConstraint('user_id','priority',name='uq_user_specialty_priority'),UniqueConstraint('user_id','specialty_id',name='uq_user_specialty_pair'))
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);specialty_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('medical_specialties.id'),index=True);priority:Mapped[str]=mapped_column(String(12));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
