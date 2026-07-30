import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cashflow import CashflowProjection
from app.models.expense import Expense
from app.models.financial import FinancialAccount
from app.models.receivable import Receivable
from app.models.tax import TaxEstimation
from app.services.cashflow_service import CashflowService


class FinancialService:
    def __init__(self, db: Session): self.db = db

    @staticmethod
    def calculate_balances(items):
        operational = [x for x in items if x.transaction_type not in ('TRANSFER', 'RESERVE') and x.status != 'Cancelado']
        current = sum((x.valor for x in operational if x.status == 'Confirmado'), Decimal(0))
        forecast = current + sum((x.valor for x in operational if x.status == 'Previsto'), Decimal(0))
        return current, forecast

    def account(self, user, account_id):
        item = self.db.scalar(select(FinancialAccount).where(FinancialAccount.id == account_id, FinancialAccount.user_id == user, FinancialAccount.deleted_at.is_(None)))
        if not item: raise HTTPException(404, 'Conta financeira não encontrada.')
        return item

    def accounts(self, user):
        items = list(self.db.scalars(select(FinancialAccount).where(FinancialAccount.user_id == user, FinancialAccount.deleted_at.is_(None)).order_by(FinancialAccount.account_name)))
        balances = dict(self.db.execute(select(CashflowProjection.account_id, func.coalesce(func.sum(CashflowProjection.valor), 0)).where(CashflowProjection.user_id == user, CashflowProjection.status == 'Confirmado', CashflowProjection.deleted_at.is_(None)).group_by(CashflowProjection.account_id)).all())
        return [{'id': x.id, 'account_name': x.account_name, 'institution_name': x.institution_name, 'account_type': x.account_type, 'last4': x.last4, 'status': x.status, 'is_default': x.is_default, 'balance': balances.get(x.id, Decimal(0))} for x in items]

    def create_account(self, user, data):
        opening = Decimal(data.pop('opening_balance')); opening_date = data.pop('opening_date')
        if data.get('is_default'):
            for old in self.db.scalars(select(FinancialAccount).where(FinancialAccount.user_id == user)): old.is_default = False
        item = FinancialAccount(user_id=user, **data); self.db.add(item); self.db.flush()
        if opening:
            self._entry(user, 'Saldo inicial', abs(opening), opening_date, 'ADJUSTMENT', 'Confirmado', item.id, 'Saldo inicial', direction='INFLOW' if opening > 0 else 'OUTFLOW')
        self.db.commit(); return next(x for x in self.accounts(user) if x['id'] == item.id)

    def archive_account(self, user, account_id):
        item = self.account(user, account_id); item.status = 'ARCHIVED'; item.deleted_at = datetime.now(timezone.utc); self.db.commit()

    def _entry(self, user, description, amount, when, kind, status, account_id, category, notes=None, direction=None, group=None):
        direction = direction or ('OUTFLOW' if kind == 'EXPENSE' else 'INFLOW')
        signed = -abs(Decimal(amount)) if direction == 'OUTFLOW' else abs(Decimal(amount))
        item = CashflowProjection(user_id=user, data=when, tipo={'INCOME':'Entrada Manual','EXPENSE':'Saída Manual','ADJUSTMENT':'Ajuste','TRANSFER':'Transferência'}[kind], origem='Manual' if kind != 'TRANSFER' else 'Transferência', origem_id=uuid.uuid4(), descricao=description, categoria=category or 'Sem categoria', valor=signed, saldo_projetado=0, status=status, account_id=account_id, transaction_type=kind, direction=direction, notes=notes, transfer_group_id=group)
        self.db.add(item); self.db.flush(); return item

    def create_manual(self, user, data):
        account_id = data.get('account_id')
        if account_id: self.account(user, account_id)
        status = 'Confirmado' if data.pop('status') == 'CONFIRMED' else 'Previsto'
        kind = data.pop('type'); amount = data.pop('amount'); when = data.pop('transaction_date'); description = data.pop('description'); category = data.pop('category', None); notes = data.pop('notes', None)
        item = self._entry(user, description, amount, when, kind, status, account_id, category, notes)
        self.db.commit(); CashflowService(self.db).recalculate(user); return item

    def transfer(self, user, data):
        source = self.account(user, data['from_account_id']); destination = self.account(user, data['to_account_id']); group = uuid.uuid4()
        self._entry(user, data['description'], data['amount'], data['transaction_date'], 'TRANSFER', 'Confirmado', source.id, 'Transferência', direction='OUTFLOW', group=group)
        self._entry(user, data['description'], data['amount'], data['transaction_date'], 'TRANSFER', 'Confirmado', destination.id, 'Transferência', direction='INFLOW', group=group)
        self.db.commit(); CashflowService(self.db).recalculate(user); return {'transfer_id': group}

    def summary(self, user, start, end):
        CashflowService(self.db).reconcile(user)
        items = list(self.db.scalars(select(CashflowProjection).where(CashflowProjection.user_id == user, CashflowProjection.deleted_at.is_(None), CashflowProjection.status != 'Cancelado')))
        operational = [x for x in items if x.transaction_type not in ('TRANSFER', 'RESERVE')]
        confirmed = [x for x in operational if x.status == 'Confirmado']
        current, forecast = self.calculate_balances(items)
        period = [x for x in confirmed if start <= x.data < end]
        inflows = sum((x.valor for x in period if x.valor > 0), Decimal(0)); outflows = -sum((x.valor for x in period if x.valor < 0), Decimal(0))
        receivable = Decimal(self.db.scalar(select(func.coalesce(func.sum(Receivable.remaining_balance), 0)).where(Receivable.user_id == user, Receivable.remaining_balance > 0, Receivable.status != 'Cancelado', Receivable.deleted_at.is_(None))) or 0)
        payable = Decimal(self.db.scalar(select(func.coalesce(func.sum(Expense.valor), 0)).where(Expense.user_id == user, Expense.status.in_(['Pendente','Atrasado']), Expense.competencia >= start, Expense.competencia < end, Expense.deleted_at.is_(None))) or 0)
        suggested = Decimal(self.db.scalar(select(func.coalesce(func.sum(TaxEstimation.valor_estimado), 0)).where(TaxEstimation.user_id == user, TaxEstimation.status == 'Estimado', TaxEstimation.deleted_at.is_(None))) or 0)
        reserved = Decimal(self.db.scalar(select(func.coalesce(func.sum(TaxEstimation.valor_estimado), 0)).where(TaxEstimation.user_id == user, TaxEstimation.status == 'Reservado', TaxEstimation.deleted_at.is_(None))) or 0)
        return {'current_balance': current, 'forecast_balance': forecast, 'receivable': receivable, 'payable': payable, 'tax_reserve_suggested': suggested, 'tax_reserve_effective': reserved, 'available': current - reserved, 'month_inflows': inflows, 'month_outflows': outflows, 'month_result': inflows - outflows}
