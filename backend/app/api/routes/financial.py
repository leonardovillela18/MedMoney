import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.financial import AccountInput, ManualTransactionInput, TransferInput
from app.services.financial_service import FinancialService

router = APIRouter(prefix='/financial', tags=['Financeiro'])

@router.get('/summary')
def summary(start: date|None=None, end: date|None=None, user: User=Depends(current_user), db: Session=Depends(get_db)):
    start = start or date.today().replace(day=1)
    end = end or (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return FinancialService(db).summary(user.id, start, end)

@router.get('/accounts')
def accounts(user: User=Depends(current_user), db: Session=Depends(get_db)): return FinancialService(db).accounts(user.id)

@router.post('/accounts', status_code=201)
def create_account(payload: AccountInput, user: User=Depends(current_user), db: Session=Depends(get_db)): return FinancialService(db).create_account(user.id, payload.model_dump())

@router.delete('/accounts/{account_id}', status_code=204)
def archive_account(account_id: uuid.UUID, user: User=Depends(current_user), db: Session=Depends(get_db)):
    FinancialService(db).archive_account(user.id, account_id); return Response(status_code=204)

@router.post('/transactions/manual', status_code=201)
def manual(payload: ManualTransactionInput, user: User=Depends(current_user), db: Session=Depends(get_db)): return FinancialService(db).create_manual(user.id, payload.model_dump())

@router.post('/transfers', status_code=201)
def transfer(payload: TransferInput, user: User=Depends(current_user), db: Session=Depends(get_db)): return FinancialService(db).transfer(user.id, payload.model_dump())
