import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class FinancialAccount(Base):
    __tablename__ = 'financial_accounts'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True)
    institution_name: Mapped[str|None] = mapped_column(String(120))
    institution_code: Mapped[str|None] = mapped_column(String(20))
    account_name: Mapped[str] = mapped_column(String(120))
    account_type: Mapped[str] = mapped_column(String(20), index=True)
    last4: Mapped[str|None] = mapped_column(String(4))
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE', index=True)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    integration_provider: Mapped[str|None] = mapped_column(String(50))
    external_account_id: Mapped[str|None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), index=True)


class BankTransaction(Base):
    __tablename__ = 'bank_transactions'
    __table_args__ = (UniqueConstraint('provider', 'external_id', name='uq_bank_transaction_external'),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True)
    financial_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('financial_accounts.id'), index=True)
    provider: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(160), index=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    description: Mapped[str] = mapped_column(String(200))
    raw_description: Mapped[str|None] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    direction: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), index=True)
    matched_cashflow_id: Mapped[uuid.UUID|None] = mapped_column(ForeignKey('cashflow_projection.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
