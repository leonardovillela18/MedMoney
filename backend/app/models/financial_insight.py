import uuid
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,Integer,String,Text,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class FinancialInsight(Base):
 __tablename__='financial_insights';__table_args__=(UniqueConstraint('user_id','referencia',name='uq_financial_insight_reference'),)
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);tipo:Mapped[str]=mapped_column(String(60),index=True);titulo:Mapped[str]=mapped_column(String(180));descricao:Mapped[str]=mapped_column(Text);categoria:Mapped[str]=mapped_column(String(40),index=True);severidade:Mapped[str]=mapped_column(String(20),index=True);status:Mapped[str]=mapped_column(String(20),default='Novo',index=True);prioridade:Mapped[int]=mapped_column(Integer,default=50,index=True);acao_recomendada:Mapped[str]=mapped_column(String(200));referencia:Mapped[str]=mapped_column(String(200));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now());dismissed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
