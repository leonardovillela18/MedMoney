import uuid
from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Date,DateTime,ForeignKey,Numeric,String,Text,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class FinancialGoal(Base):
 __tablename__='financial_goals'
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);titulo:Mapped[str]=mapped_column(String(160));descricao:Mapped[str|None]=mapped_column(Text);tipo:Mapped[str]=mapped_column(String(40),index=True);valor_meta:Mapped[Decimal]=mapped_column(Numeric(14,2));valor_atual:Mapped[Decimal]=mapped_column(Numeric(14,2),default=0);percentual:Mapped[Decimal]=mapped_column(Numeric(7,2),default=0);data_inicio:Mapped[date]=mapped_column(Date,index=True);data_final:Mapped[date]=mapped_column(Date,index=True);status:Mapped[str]=mapped_column(String(20),default='Em andamento',index=True);cor:Mapped[str]=mapped_column(String(20),default='blue');icone:Mapped[str]=mapped_column(String(40),default='target');created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now());deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class FinancialGoalSnapshot(Base):
 __tablename__='financial_goal_snapshots';__table_args__=(UniqueConstraint('goal_id','data',name='uq_goal_snapshot_day'),)
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);goal_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('financial_goals.id'),index=True);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);data:Mapped[date]=mapped_column(Date,index=True);valor:Mapped[Decimal]=mapped_column(Numeric(14,2));percentual:Mapped[Decimal]=mapped_column(Numeric(7,2));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
