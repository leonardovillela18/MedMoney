import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import Base
from app.models.cashflow import CashflowProjection
from app.models.financial import BankTransaction, FinancialAccount
from app.services.financial_service import FinancialService


def movement(value, status='Confirmado', kind='OPERATING'):
    return SimpleNamespace(valor=Decimal(value), status=status, transaction_type=kind)


@pytest.mark.parametrize(('items','current','forecast'), [
    ([movement('1000')], '1000', '1000'),
    ([movement('1000','Previsto')], '0', '1000'),
    ([movement('-300')], '-300', '-300'),
    ([movement('-300','Previsto')], '0', '-300'),
    ([movement('1000'),movement('-300')], '700', '700'),
    ([movement('1000'),movement('-300'),movement('500','Previsto')], '700', '1200'),
    ([movement('1000'),movement('-300'),movement('500','Previsto'),movement('-200','Previsto')], '700', '1000'),
])
def test_real_and_forecast_balances(items, current, forecast):
    assert FinancialService.calculate_balances(items) == (Decimal(current), Decimal(forecast))


def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine, tables=[FinancialAccount.__table__, CashflowProjection.__table__, BankTransaction.__table__])
    return Session(engine)


def test_opening_balance_is_an_auditable_adjustment():
    db = session(); user = uuid.uuid4()
    FinancialService(db).create_account(user, {'account_name':'Conta PJ','institution_name':'Banco','account_type':'CHECKING','last4':'1234','opening_balance':Decimal('10000'),'opening_date':date(2026,1,1),'is_default':True})
    item = db.query(CashflowProjection).one()
    assert item.transaction_type == 'ADJUSTMENT' and item.valor == Decimal('10000') and item.status == 'Confirmado'


def test_transfer_keeps_global_balance_and_is_not_operational_result():
    db = session(); user = uuid.uuid4(); service = FinancialService(db)
    a = FinancialAccount(user_id=user, account_name='A', account_type='CHECKING'); b = FinancialAccount(user_id=user, account_name='B', account_type='CHECKING'); db.add_all([a,b]); db.commit()
    service.transfer(user, {'from_account_id':a.id,'to_account_id':b.id,'amount':Decimal('1000'),'transaction_date':date.today(),'description':'Transferência'})
    items = db.query(CashflowProjection).all()
    assert sum(x.valor for x in items) == 0
    assert FinancialService.calculate_balances(items) == (0, 0)
    assert len({x.transfer_group_id for x in items}) == 1


def test_tax_reserve_does_not_reduce_current_balance():
    assert FinancialService.calculate_balances([movement('1000'), movement('-150','Confirmado','RESERVE')]) == (Decimal('1000'), Decimal('1000'))


def test_other_users_account_is_hidden():
    db = session(); account = FinancialAccount(user_id=uuid.uuid4(), account_name='Privada', account_type='CHECKING'); db.add(account); db.commit()
    with pytest.raises(HTTPException) as error: FinancialService(db).account(uuid.uuid4(), account.id)
    assert error.value.status_code == 404


def test_external_bank_transaction_is_idempotent_by_provider_and_external_id():
    db = session(); user = uuid.uuid4(); account = FinancialAccount(user_id=user, account_name='Conta', account_type='CHECKING'); db.add(account); db.flush()
    values = dict(user_id=user, financial_account_id=account.id, provider='open-finance-provider', external_id='external-1', transaction_date=date.today(), description='Crédito', amount=Decimal('10'), direction='INFLOW', status='POSTED')
    db.add(BankTransaction(**values)); db.commit(); db.add(BankTransaction(**values))
    with pytest.raises(IntegrityError): db.commit()
