import uuid
from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Boolean,Date,DateTime,ForeignKey,Numeric,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base

class RecurringIncome(Base):
    __tablename__='recurring_incomes'
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True)
    description:Mapped[str]=mapped_column(String(160))
    income_type:Mapped[str]=mapped_column(String(30),index=True)
    amount:Mapped[Decimal]=mapped_column(Numeric(12,2))
    frequency:Mapped[str]=mapped_column(String(20))
    start_date:Mapped[date]=mapped_column(Date)
    end_date:Mapped[date|None]=mapped_column(Date)
    day_of_month:Mapped[int|None]
    next_occurrence_date:Mapped[date]=mapped_column(Date,index=True)
    tax_treatment:Mapped[str]=mapped_column(String(20),index=True)
    tax_reserve_percentage:Mapped[Decimal|None]=mapped_column(Numeric(6,3))
    active:Mapped[bool]=mapped_column(Boolean,default=True,index=True)
    notes:Mapped[str|None]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),index=True)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
