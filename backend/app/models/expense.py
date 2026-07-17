import uuid
from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Boolean,Date,DateTime,ForeignKey,Numeric,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class ExpenseCategory(Base):
 __tablename__='expense_categories'
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);nome:Mapped[str]=mapped_column(String(80));cor:Mapped[str]=mapped_column(String(20),default='slate');ativa:Mapped[bool]=mapped_column(Boolean,default=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class Expense(Base):
 __tablename__='expenses'
 id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);titulo:Mapped[str]=mapped_column(String(160));descricao:Mapped[str|None]=mapped_column(Text);categoria_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('expense_categories.id'),index=True);valor:Mapped[Decimal]=mapped_column(Numeric(12,2));tipo:Mapped[str]=mapped_column(String(20),index=True);forma_pagamento:Mapped[str]=mapped_column(String(20));fornecedor:Mapped[str|None]=mapped_column(String(160),index=True);competencia:Mapped[date]=mapped_column(Date,index=True);data_vencimento:Mapped[date]=mapped_column(Date,index=True);data_pagamento:Mapped[date|None]=mapped_column(Date);status:Mapped[str]=mapped_column(String(20),index=True);recorrente:Mapped[bool]=mapped_column(Boolean,default=False);intervalo_recorrencia:Mapped[str|None]=mapped_column(String(20));recurrence_parent_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('expenses.id'),index=True);centro_custo:Mapped[str|None]=mapped_column(String(60));observacoes:Mapped[str|None]=mapped_column(Text);comprovante_url:Mapped[str|None]=mapped_column(String(500));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now());deleted_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
