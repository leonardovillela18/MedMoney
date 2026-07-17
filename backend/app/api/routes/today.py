from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.services.today_service import TodayService
router=APIRouter(prefix='/today',tags=['Meu Dia'])
@router.get('')
def today(user:User=Depends(current_user),db:Session=Depends(get_db)):return TodayService(db).build(user)
