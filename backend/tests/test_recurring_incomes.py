from datetime import date
from decimal import Decimal
import uuid
from sqlalchemy import create_engine,func,select
from sqlalchemy.orm import Session
from app.database.session import Base
from app.models.cashflow import CashflowProjection
from app.models.recurring_income import RecurringIncome
from app.models.receivable import Receivable
from app.models.tax import TaxEstimation,TaxSetting
from app.models.user import User
from app.services.recurrence import next_occurrence
from app.services.recurring_income_service import RecurringIncomeService
from app.services.cashflow_service import CashflowService
from types import SimpleNamespace

def session():
    engine=create_engine('sqlite://');Base.metadata.create_all(engine,tables=[User.__table__,RecurringIncome.__table__,Receivable.__table__,CashflowProjection.__table__,TaxSetting.__table__,TaxEstimation.__table__]);return Session(engine)
def payload(kind='CLT',treatment='NON_PJ',amount='10000',percentage=None):return {'description':'Renda mensal','income_type':kind,'amount':Decimal(amount),'frequency':'Mensal','start_date':date(2026,8,1),'end_date':None,'day_of_month':5,'tax_treatment':treatment,'tax_reserve_percentage':Decimal(percentage) if percentage else None,'active':True,'notes':None}
def test_calendar_recurrence_keeps_end_of_month_anchor():
    feb=next_occurrence(date(2026,1,31),'Mensal',31);assert feb==date(2026,2,28);assert next_occurrence(feb,'Mensal',31)==date(2026,3,31)
def test_clt_materializes_one_non_pj_occurrence_idempotently():
    db=session();user=uuid.uuid4();service=RecurringIncomeService(db);rule=service.create(user,payload());service.materialize_next(user,rule.id)
    rows=list(db.scalars(select(Receivable)));assert len(rows)==1 and rows[0].expected_value==Decimal('10000') and rows[0].tax_treatment=='NON_PJ';assert db.scalar(select(func.count()).select_from(TaxEstimation))==0
def test_grants_are_excluded_from_pj_reserve_but_enter_cashflow():
    db=session();user=uuid.uuid4();service=RecurringIncomeService(db)
    service.create(user,payload('RESIDENCY_GRANT','NON_PJ','4000'));service.create(user,payload('RESEARCH_GRANT','NON_PJ','2000'))
    assert db.scalar(select(func.coalesce(func.sum(CashflowProjection.valor),0)))==Decimal('6000');assert db.scalar(select(func.count()).select_from(TaxEstimation))==0
def test_pj_recurring_income_creates_snapshot_tax_reserve_and_full_receivable():
    db=session();user=uuid.uuid4();rule=RecurringIncomeService(db).create(user,payload('PJ_RECURRING','PJ_TAXABLE','5000','15'));receivable=db.scalar(select(Receivable));tax=db.scalar(select(TaxEstimation))
    assert receivable.expected_value==Decimal('5000') and tax.valor_estimado==Decimal('750') and tax.percentual==Decimal('15');assert rule.tax_reserve_percentage==Decimal('15')
def test_deactivation_preserves_occurrence_history():
    db=session();user=uuid.uuid4();service=RecurringIncomeService(db);rule=service.create(user,payload());service.deactivate(user,rule.id)
    assert db.scalar(select(func.count()).select_from(Receivable))==1 and not rule.active
def test_user_isolation():
    db=session();owner=uuid.uuid4();other=uuid.uuid4();rule=RecurringIncomeService(db).create(owner,payload())
    try:RecurringIncomeService(db).get(other,rule.id);assert False
    except Exception as error:assert getattr(error,'status_code',None)==404
def test_clt_and_grants_enter_total_revenue_but_not_pj_reserve_base():
    rows=[SimpleNamespace(expected_value=Decimal('20000'),tax_treatment='PJ_TAXABLE'),SimpleNamespace(expected_value=Decimal('10000'),tax_treatment='NON_PJ'),SimpleNamespace(expected_value=Decimal('4000'),tax_treatment='NON_PJ'),SimpleNamespace(expected_value=Decimal('2000'),tax_treatment='NON_PJ')]
    pj,non_pj=CashflowService.revenue_split(rows);assert pj==Decimal('20000') and non_pj==Decimal('16000') and pj+non_pj==Decimal('36000');assert pj*Decimal('0.15')==Decimal('3000.00')
