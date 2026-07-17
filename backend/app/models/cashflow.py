import uuid
from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Date,DateTime,ForeignKey,Numeric,String,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base

class CashflowProjection(Base):
    __tablename__='cashflow_projection'
    __table_args__=(UniqueConstraint('user_id','origem','origem_id',name='uq_cashflow_source'),)
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True)
    data:Mapped[date]=mapped_column(Date,index=True);tipo:Mapped[str]=mapped_column(String(30),index=True)
    origem:Mapped[str]=mapped_column(String(30),index=True);origem_id:Mapped[uuid.UUID]=mapped_column(index=True)
    descricao:Mapped[str]=mapped_column(String(200));categoria:Mapped[str]=mapped_column(String(80),index=True)
    valor:Mapped[Decimal]=mapped_column(Numeric(12,2));saldo_projetado:Mapped[Decimal]=mapped_column(Numeric(14,2),default=0)
    status:Mapped[str]=mapped_column(String(20),default='Previsto',index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now());deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
