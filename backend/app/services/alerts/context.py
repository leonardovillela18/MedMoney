from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
from app.models.expense import Expense
from app.models.financial_goal import FinancialGoal
from app.models.financial_insight import FinancialInsight
from app.models.invoice import Invoice
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
from app.models.user import User
class AlertContext:
 def __init__(self,db:Session,user_id):
  self.db=db;self.user_id=user_id;self.today=date.today();self.user=db.get(User,user_id);self.contractors={x.id:x.name for x in db.scalars(select(Contractor).where(Contractor.user_id==user_id,Contractor.deleted_at.is_(None)))};self.shifts=list(db.scalars(select(Shift).where(Shift.user_id==user_id,Shift.deleted_at.is_(None))));self.receivables=list(db.scalars(select(Receivable).where(Receivable.user_id==user_id,Receivable.deleted_at.is_(None))));self.invoices=list(db.scalars(select(Invoice).where(Invoice.user_id==user_id,Invoice.deleted_at.is_(None))));self.expenses=list(db.scalars(select(Expense).where(Expense.user_id==user_id,Expense.deleted_at.is_(None),Expense.status!='Cancelado')));self.taxes=list(db.scalars(select(TaxEstimation).where(TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado')));self.goals=list(db.scalars(select(FinancialGoal).where(FinancialGoal.user_id==user_id,FinancialGoal.deleted_at.is_(None),FinancialGoal.status!='Cancelada')));self.insights=list(db.scalars(select(FinancialInsight).where(FinancialInsight.user_id==user_id,FinancialInsight.status!='Arquivado')))
