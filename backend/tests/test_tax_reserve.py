from datetime import date
from decimal import Decimal
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.session import Base
from app.models.contractor import Contractor
from app.models.invoice import Invoice
from app.models.receivable import Receivable
from app.models.recurring_income import RecurringIncome
from app.models.shift import Shift
from app.models.tax import TaxEstimation, TaxSetting
from app.models.user import User
from app.services.tax_service import TaxService


@pytest.mark.parametrize(('value','percentage','reserve','available'),[
    ('1000','15','150.00','850.00'),('3750','12','450.00','3300.00'),('1000','0','0.00','1000.00'),('1333.33','12.75','170.00','1163.33')])
def test_authoritative_reserve_calculation(value,percentage,reserve,available):
    assert TaxService.calculate_reserve(Decimal(value),Decimal(percentage))==(Decimal(reserve),Decimal(available))


@pytest.mark.parametrize('percentage',['-1','101'])
def test_invalid_percentage_is_rejected(percentage):
    with pytest.raises(HTTPException):TaxService.calculate_reserve(Decimal('1000'),Decimal(percentage))


def tax_session():
    engine=create_engine('sqlite://')
    Base.metadata.create_all(engine,tables=[User.__table__,Contractor.__table__,Shift.__table__,RecurringIncome.__table__,Receivable.__table__,Invoice.__table__,TaxSetting.__table__,TaxEstimation.__table__])
    return Session(engine)


def test_default_is_15_and_custom_setting_is_preserved():
    db=tax_session();user_id=uuid.uuid4();service=TaxService(db)
    assert service.percentage(user_id)==Decimal('15')
    db.add(TaxSetting(user_id=user_id,default_percentage=Decimal('13'),recommended_reserve_percentage=Decimal('13')));db.commit()
    assert service.percentage(user_id)==Decimal('13')


def test_service_percentage_is_a_snapshot_when_global_setting_changes():
    db=tax_session();user_id=uuid.uuid4();shift_id=uuid.uuid4();service=TaxService(db)
    estimate=service.sync(user_id,Decimal('1000'),date(2026,1,10),shift_id=shift_id,percentage=Decimal('15'))
    db.add(TaxSetting(user_id=user_id,default_percentage=Decimal('12'),recommended_reserve_percentage=Decimal('12')));db.commit()
    estimate=service.sync(user_id,Decimal('1000'),date(2026,1,10),shift_id=shift_id,percentage=Decimal('15'))
    assert estimate.percentual==Decimal('15') and estimate.valor_estimado==Decimal('150')


def test_non_pj_service_is_excluded_from_suggested_reserve():
    db=tax_session();estimate=TaxService(db).sync(uuid.uuid4(),Decimal('1000'),date(2026,1,10),shift_id=uuid.uuid4(),percentage=Decimal('15'),tax_treatment='NON_PJ')
    assert estimate.status=='Ignorado'
