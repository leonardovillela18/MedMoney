import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class TimestampMixin:
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    deleted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
class User(TimestampMixin,Base):
    __tablename__='users'
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(120)); crm: Mapped[str]=mapped_column(String(30)); crm_uf: Mapped[str]=mapped_column(String(2)); email: Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); cnpj: Mapped[str]=mapped_column(String(18),unique=True); phone: Mapped[str]=mapped_column(String(30)); city: Mapped[str]=mapped_column(String(100)); state: Mapped[str]=mapped_column(String(2)); specialty: Mapped[str]=mapped_column(String(100))
    refresh_tokens: Mapped[list['RefreshToken']]=relationship(back_populates='user',cascade='all, delete-orphan')
class RefreshToken(TimestampMixin,Base):
    __tablename__='refresh_tokens'
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    token_hash: Mapped[str]=mapped_column(String(64),unique=True,index=True); expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True)); revoked_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True); user: Mapped[User]=relationship(back_populates='refresh_tokens')
