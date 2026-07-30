from datetime import datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.models.recurring_income import RecurringIncome
from app.models.receivable import Receivable
from app.schemas.recurring_income import NON_PJ_TYPES
from app.services.recurrence import first_occurrence,next_occurrence

class RecurringIncomeService:
    def __init__(self,db:Session):self.db=db
    def get(self,user,item_id):
        item=self.db.scalar(select(RecurringIncome).where(RecurringIncome.id==item_id,RecurringIncome.user_id==user,RecurringIncome.deleted_at.is_(None)))
        if not item:raise HTTPException(404,'Recebimento recorrente não encontrado.')
        return item
    def list(self,user,page,size,active=None):
        q=select(RecurringIncome).where(RecurringIncome.user_id==user,RecurringIncome.deleted_at.is_(None))
        if active is not None:q=q.where(RecurringIncome.active==active)
        q=q.order_by(RecurringIncome.active.desc(),RecurringIncome.next_occurrence_date)
        return list(self.db.scalars(q.offset((page-1)*size).limit(size))),self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
    def normalize(self,user,data,current=None):
        if data['income_type'] in NON_PJ_TYPES:data['tax_treatment']='NON_PJ';data['tax_reserve_percentage']=None
        elif data['tax_treatment']=='PJ_TAXABLE' and data.get('tax_reserve_percentage') is None:
            data['tax_reserve_percentage']=current.tax_reserve_percentage if current else __import__('app.services.tax_service',fromlist=['TaxService']).TaxService(self.db).percentage(user)
        if data['tax_treatment']=='NON_PJ':data['tax_reserve_percentage']=None
        return data
    def create(self,user,data):
        data=self.normalize(user,data);first=first_occurrence(data['start_date'],data['frequency'],data.get('day_of_month'));item=RecurringIncome(user_id=user,next_occurrence_date=first,**data);self.db.add(item);self.db.commit();self.db.refresh(item);self.materialize_next(user,item.id);return item
    def update(self,user,item_id,data):
        item=self.get(user,item_id);data=self.normalize(user,data,item)
        for key,value in data.items():setattr(item,key,value)
        open_item=self.db.scalar(select(Receivable).where(Receivable.recurring_income_id==item.id,Receivable.deleted_at.is_(None),Receivable.received_value==0).order_by(Receivable.expected_date))
        if open_item:
            open_item.expected_value=item.amount;open_item.remaining_balance=item.amount;open_item.tax_treatment=item.tax_treatment;open_item.tax_reserve_percentage=item.tax_reserve_percentage
            item.next_occurrence_date=next_occurrence(open_item.expected_date,item.frequency,item.day_of_month or item.start_date.day)
            from app.services.cashflow_service import CashflowService
            CashflowService(self.db).sync_source(user,'Recebimento Recorrente',open_item.id,open_item.expected_date,'Receita Prevista',item.description,'Recebimentos',item.amount,'Previsto')
        self.db.commit();self.db.refresh(item);return item
    def deactivate(self,user,item_id):
        item=self.get(user,item_id);item.active=False;self.db.commit();return item
    def delete(self,user,item_id):
        item=self.get(user,item_id);item.active=False;item.deleted_at=datetime.now(timezone.utc);self.db.commit()
    def materialize_next(self,user,item_id):
        item=self.get(user,item_id)
        if not item.active or item.end_date and item.next_occurrence_date>item.end_date:return None
        open_item=self.db.scalar(select(Receivable).where(Receivable.user_id==user,Receivable.recurring_income_id==item.id,Receivable.deleted_at.is_(None),Receivable.status.in_(['A Receber','Atrasado','Recebido Parcialmente'])))
        if open_item:return open_item
        due=item.next_occurrence_date
        existing=self.db.scalar(select(Receivable).where(Receivable.user_id==user,Receivable.recurring_income_id==item.id,Receivable.expected_date==due,Receivable.deleted_at.is_(None)))
        if existing:return existing
        occurrence=Receivable(user_id=user,recurring_income_id=item.id,expected_value=item.amount,received_value=Decimal(0),remaining_balance=item.amount,expected_date=due,competence=due.replace(day=1),tax_treatment=item.tax_treatment,tax_reserve_percentage=item.tax_reserve_percentage,status='A Receber',notes=item.notes);self.db.add(occurrence);self.db.flush()
        from app.services.cashflow_service import CashflowService
        CashflowService(self.db).sync_source(user,'Recebimento Recorrente',occurrence.id,due,'Receita Prevista',item.description,'Recebimentos',item.amount,'Previsto')
        if item.tax_treatment!='NON_PJ':
            from app.services.tax_service import TaxService
            TaxService(self.db).sync(user,item.amount,due,receivable_id=occurrence.id,percentage=item.tax_reserve_percentage,tax_treatment=item.tax_treatment)
        item.next_occurrence_date=next_occurrence(due,item.frequency,item.day_of_month or item.start_date.day);self.db.commit();return occurrence
