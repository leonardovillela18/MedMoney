from datetime import date,timedelta
from fastapi import APIRouter,Depends
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.shift import Shift
from app.models.receivable import Receivable
from app.models.user import User
router=APIRouter(prefix='/dashboard',tags=['Dashboard'])
@router.get('')
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):
 today=date.today();month=today.replace(day=1)
 shifts=list(db.scalars(select(Shift).where(Shift.user_id==user.id,Shift.deleted_at.is_(None)).order_by(Shift.date.desc()).limit(6)))
 rec=list(db.scalars(select(Receivable).where(Receivable.user_id==user.id,Receivable.deleted_at.is_(None)).order_by(Receivable.expected_date).limit(10)))
 total=lambda col,where:float(db.scalar(select(func.coalesce(func.sum(col),0)).where(*where)) or 0)
 pending=total(Receivable.remaining_balance,[Receivable.user_id==user.id,Receivable.deleted_at.is_(None)])
 received=total(Receivable.received_value,[Receivable.user_id==user.id,Receivable.received_date>=month,Receivable.deleted_at.is_(None)])
 overdue=total(Receivable.remaining_balance,[Receivable.user_id==user.id,Receivable.expected_date<today,Receivable.status!='Recebido',Receivable.deleted_at.is_(None)])
 hours=total(Shift.duration_hours,[Shift.user_id==user.id,Shift.date>=month,Shift.deleted_at.is_(None)])
 return {'summary':{'total_expected':pending,'received_month':received,'pending':pending,'overdue':overdue,'estimated_tax':0,'estimated_profit':pending,'shifts_month':len([s for s in shifts if s.date>=month]),'hours':hours},'next_payments':[{'date':str(r.expected_date),'value':float(r.remaining_balance),'status':r.status} for r in rec if r.status!='Recebido'][:10],'recent_shifts':[{'date':str(s.date),'title':s.title or s.type,'value':float(s.gross_value),'status':s.status,'specialty':s.specialty} for s in shifts],'insights':['Seu painel será atualizado conforme você registrar novos plantões e recebimentos.']}
