import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class AccountInput(BaseModel):
    account_name: str = Field(min_length=2, max_length=120)
    institution_name: str|None = Field(None, max_length=120)
    account_type: str = Field(pattern='^(CHECKING|SAVINGS|PAYMENT|CASH|INVESTMENT|OTHER)$')
    last4: str|None = Field(None, pattern=r'^\d{4}$')
    opening_balance: Decimal = Decimal(0)
    opening_date: date = Field(default_factory=date.today)
    is_default: bool = False


class ManualTransactionInput(BaseModel):
    description: str = Field(min_length=2, max_length=200)
    amount: Decimal = Field(gt=0)
    transaction_date: date
    type: str = Field(pattern='^(INCOME|EXPENSE|ADJUSTMENT)$')
    status: str = Field(pattern='^(CONFIRMED|FORECAST)$')
    account_id: uuid.UUID|None = None
    category: str|None = Field(None, max_length=80)
    notes: str|None = Field(None, max_length=500)


class TransferInput(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    transaction_date: date
    description: str = Field(default='Transferência entre contas', max_length=200)

    @field_validator('to_account_id')
    @classmethod
    def valid_destination(cls, value, info):
        if value == info.data.get('from_account_id'):
            raise ValueError('As contas de origem e destino devem ser diferentes.')
        return value
