import uuid
from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base
class Shift(Base):
    __tablename__='shifts'
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True); contractor_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('contractors.id'),index=True)
    title:Mapped[str|None]=mapped_column(String(160)); type:Mapped[str]=mapped_column(String(40)); specialty:Mapped[str|None]=mapped_column(String(100)); hospital_sector:Mapped[str|None]=mapped_column(String(160)); city:Mapped[str|None]=mapped_column(String(100),index=True); state:Mapped[str|None]=mapped_column(String(2)); date:Mapped[date]=mapped_column(Date,index=True); start_time:Mapped[time]=mapped_column(Time); end_time:Mapped[time]=mapped_column(Time); duration_hours:Mapped[Decimal]=mapped_column(Numeric(6,2)); gross_value:Mapped[Decimal]=mapped_column(Numeric(12,2)); estimated_net_value:Mapped[Decimal]=mapped_column(Numeric(12,2)); status:Mapped[str]=mapped_column(String(20),default='Agendado',index=True); payment_method:Mapped[str|None]=mapped_column(String(30)); expected_payment_date:Mapped[date|None]=mapped_column(Date); notes:Mapped[str|None]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now()); deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
