import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base

class Contractor(Base):
    __tablename__='contractors'
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True,nullable=False)
    name: Mapped[str]=mapped_column(String(160),nullable=False,index=True); type: Mapped[str]=mapped_column(String(40),nullable=False,index=True)
    cnpj: Mapped[str|None]=mapped_column(String(18)); email: Mapped[str|None]=mapped_column(String(255)); phone: Mapped[str|None]=mapped_column(String(30)); mobile: Mapped[str|None]=mapped_column(String(30)); site: Mapped[str|None]=mapped_column(String(255))
    zip_code: Mapped[str|None]=mapped_column(String(9)); street: Mapped[str|None]=mapped_column(String(180)); number: Mapped[str|None]=mapped_column(String(20)); neighborhood: Mapped[str|None]=mapped_column(String(100)); city: Mapped[str|None]=mapped_column(String(100),index=True); state: Mapped[str|None]=mapped_column(String(2)); complement: Mapped[str|None]=mapped_column(String(120))
    primary_contact: Mapped[str|None]=mapped_column(String(120)); contact_role: Mapped[str|None]=mapped_column(String(100)); contact_phone: Mapped[str|None]=mapped_column(String(30)); contact_email: Mapped[str|None]=mapped_column(String(255))
    payment_day: Mapped[str|None]=mapped_column(String(40)); payment_term_days: Mapped[int|None]=mapped_column(Integer); notes: Mapped[str|None]=mapped_column(Text); active: Mapped[bool]=mapped_column(Boolean,default=True,server_default='true')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now()); deleted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
