from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.contractor import Contractor
from app.models.expense import Expense,ExpenseCategory
from app.models.receivable import Receivable
from app.models.shift import Shift
from app.models.tax import TaxEstimation
class InsightContext:
 def __init__(self,db:Session,user_id):
  self.db=db;self.user_id=user_id;self.today=date.today();self.month=self.today.replace(day=1);self.previous=(self.month-timedelta(days=1)).replace(day=1);self.year_month=self.month.replace(year=self.month.year-1);self.next_month=self.month.replace(year=self.month.year+(self.month.month==12),month=1 if self.month.month==12 else self.month.month+1)
  self.contractors={x.id:x.name for x in db.scalars(select(Contractor).where(Contractor.user_id==user_id,Contractor.deleted_at.is_(None)))};self.categories={x.id:x.nome for x in db.scalars(select(ExpenseCategory).where(ExpenseCategory.user_id==user_id,ExpenseCategory.deleted_at.is_(None)))}
  self.shifts=list(db.scalars(select(Shift).where(Shift.user_id==user_id,Shift.deleted_at.is_(None))));self.receivables=list(db.scalars(select(Receivable).where(Receivable.user_id==user_id,Receivable.deleted_at.is_(None))));self.expenses=list(db.scalars(select(Expense).where(Expense.user_id==user_id,Expense.deleted_at.is_(None),Expense.status!='Cancelado')));self.taxes=list(db.scalars(select(TaxEstimation).where(TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado')))
 def period(self,items,field,start,end):return [x for x in items if getattr(x,field) is not None and start<=getattr(x,field)<end]
 def revenue(self,start,end):return sum((x.received_value for x in self.period(self.receivables,'received_date',start,end)),Decimal(0))
 def expense(self,start,end):return sum((x.valor for x in self.period(self.expenses,'competencia',start,end)),Decimal(0))
 def tax(self,start,end):return sum((x.valor_estimado for x in self.period(self.taxes,'competencia',start,end)),Decimal(0))
 def profit(self,start,end):return self.revenue(start,end)-self.expense(start,end)-self.tax(start,end)
