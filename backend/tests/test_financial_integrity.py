from datetime import date
from decimal import Decimal
from types import SimpleNamespace
import uuid

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.session import Base
from app.models.cashflow import CashflowProjection
from app.models.contractor import Contractor  # register referenced tables
from app.models.receivable import Receivable
from app.models.recurring_income import RecurringIncome
from app.models.shift import Shift
from app.models.user import User  # register referenced tables
from app.services.cashflow_service import CashflowService
from app.services.expense_service import ExpenseService
from app.services.receivable_service import ReceivableService


def month_total(items, month):
    return sum((item.valor for item in items if ExpenseService.in_month(item.competencia, month)), Decimal(0))


def test_monthly_competence_excludes_future_months():
    items = [SimpleNamespace(competencia=date(2026, 8, 1), valor=Decimal('300')),
             SimpleNamespace(competencia=date(2026, 9, 1), valor=Decimal('300'))]
    assert month_total(items, date(2026, 8, 1)) == Decimal('300')


def test_each_month_has_only_its_own_expense():
    items = [SimpleNamespace(competencia=date(2026, month, 1), valor=Decimal('300')) for month in (8, 9, 10)]
    for month in (8, 9, 10):
        assert month_total(items, date(2026, month, 1)) == Decimal('300')


def test_monthly_recurrence_preserves_last_valid_day_and_anchor():
    february = ExpenseService.next_recurrence(date(2026, 1, 31), 'Mensal', 31)
    march = ExpenseService.next_recurrence(february, 'Mensal', 31)
    assert february == date(2026, 2, 28)
    assert march == date(2026, 3, 31)


def test_expense_status_never_becomes_paid_from_date():
    today = date(2026, 8, 10)
    assert ExpenseService.effective_status('Pendente', date(2026, 8, 11), today) == 'Pendente'
    assert ExpenseService.effective_status('Pendente', today, today) == 'Pendente'
    assert ExpenseService.effective_status('Pendente', date(2026, 8, 9), today) == 'Atrasado'
    assert ExpenseService.effective_status('Pago', date(2026, 8, 1), today) == 'Pago'


def financial_session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine, tables=[User.__table__, Contractor.__table__, Shift.__table__, RecurringIncome.__table__, Receivable.__table__, CashflowProjection.__table__])
    return Session(engine)


def test_shift_financial_sync_is_idempotent_and_updates_values():
    db = financial_session(); user_id = uuid.uuid4(); shift_id = uuid.uuid4(); contractor_id = uuid.uuid4()
    shift = SimpleNamespace(id=shift_id, user_id=user_id, contractor_id=contractor_id,
                            gross_value=Decimal('1000'), expected_payment_date=date(2026, 8, 20),
                            date=date(2026, 8, 10), status='Agendado')
    service = ReceivableService(db); service.sync_shift(shift)
    shift.gross_value=Decimal('1200');shift.expected_payment_date=date(2026, 8, 25);service.sync_shift(shift)
    rows=list(db.scalars(select(Receivable)))
    assert len(rows)==1 and rows[0].expected_value==Decimal('1200')
    assert rows[0].remaining_balance==Decimal('1200') and rows[0].expected_date==date(2026, 8, 25)


def test_cashflow_source_is_updated_instead_of_duplicated():
    db=financial_session();user_id=uuid.uuid4();shift_id=uuid.uuid4();service=CashflowService(db)
    service.sync_source(user_id,'Plantão',shift_id,date(2026,8,20),'Receita Prevista','Cirurgia','Plantões',Decimal('5000'))
    service.sync_source(user_id,'Plantão',shift_id,date(2026,8,25),'Receita Prevista','Cirurgia','Plantões',Decimal('5200'))
    assert db.scalar(select(func.count()).select_from(CashflowProjection))==1
    row=db.scalar(select(CashflowProjection));assert row.valor==Decimal('5200') and row.data==date(2026,8,25)
