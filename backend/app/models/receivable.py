import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base
class Receivable(Base):
 __tablename__='receivables'
 __table_args__=(UniqueConstraint('recurring_income_id','expected_date',name='uq_receivable_recurring_date'),)
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);shift_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('shifts.id'),index=True);recurring_income_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('recurring_incomes.id'),index=True);contractor_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('contractors.id'),index=True);expected_value:Mapped[Decimal]=mapped_column(Numeric(12,2));received_value:Mapped[Decimal]=mapped_column(Numeric(12,2),default=0);remaining_balance:Mapped[Decimal]=mapped_column(Numeric(12,2));expected_date:Mapped[date]=mapped_column(Date);competence:Mapped[date]=mapped_column(Date,index=True);tax_treatment:Mapped[str]=mapped_column(String(20),default='PJ_TAXABLE',index=True);tax_reserve_percentage:Mapped[Decimal|None]=mapped_column(Numeric(6,3));received_date:Mapped[date|None]=mapped_column(Date);status:Mapped[str]=mapped_column(String(30),default='A Receber',index=True);receipt_method:Mapped[str|None]=mapped_column(String(30));receipt_url:Mapped[str|None]=mapped_column(String(500));notes:Mapped[str|None]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now());deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
