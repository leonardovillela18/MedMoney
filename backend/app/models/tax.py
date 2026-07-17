import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base

class TaxEstimation(Base):
    __tablename__ = 'tax_estimations'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True)
    shift_id: Mapped[uuid.UUID|None] = mapped_column(ForeignKey('shifts.id'), index=True)
    invoice_id: Mapped[uuid.UUID|None] = mapped_column(ForeignKey('invoices.id'), index=True)
    receivable_id: Mapped[uuid.UUID|None] = mapped_column(ForeignKey('receivables.id'), index=True)
    base_calculo: Mapped[Decimal] = mapped_column(Numeric(12,2))
    percentual: Mapped[Decimal] = mapped_column(Numeric(6,3))
    valor_estimado: Mapped[Decimal] = mapped_column(Numeric(12,2))
    tipo: Mapped[str] = mapped_column(String(20), default='Outro', index=True)
    competencia: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20), default='Estimado', index=True)
    observacoes: Mapped[str|None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True))

class TaxSetting(Base):
    __tablename__ = 'tax_settings'
    __table_args__ = (UniqueConstraint('user_id', name='uq_tax_settings_user'),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True)
    default_percentage: Mapped[Decimal] = mapped_column(Numeric(6,3), default=18)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
