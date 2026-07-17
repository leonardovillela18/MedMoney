import uuid
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,String,Text,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class Alert(Base):
 __tablename__='alerts';__table_args__=(UniqueConstraint('user_id','tipo','origem','referencia_id',name='uq_alert_rule_reference'),)
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);tipo:Mapped[str]=mapped_column(String(70),index=True);categoria:Mapped[str]=mapped_column(String(40),index=True);titulo:Mapped[str]=mapped_column(String(180));descricao:Mapped[str]=mapped_column(Text);prioridade:Mapped[str]=mapped_column(String(20),index=True);status:Mapped[str]=mapped_column(String(20),default='Novo',index=True);acao:Mapped[str]=mapped_column(String(180));url_destino:Mapped[str]=mapped_column(String(300));referencia_id:Mapped[uuid.UUID]=mapped_column(index=True);origem:Mapped[str]=mapped_column(String(50),index=True);lido_em:Mapped[datetime|None]=mapped_column(DateTime(timezone=True));resolvido_em:Mapped[datetime|None]=mapped_column(DateTime(timezone=True));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
