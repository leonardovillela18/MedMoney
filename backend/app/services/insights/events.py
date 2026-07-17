from sqlalchemy.orm import Session
def refresh_insights(db:Session,user_id):
 """Refreshes the cached engine after a committed domain event without affecting the source transaction."""
 try:
  from app.services.analytics_service import invalidate_analytics
  invalidate_analytics(user_id)
  from app.services.goals.engine import GoalEngine
  GoalEngine(db).update_all(user_id)
  from app.services.insights import FinancialInsightsService
  FinancialInsightsService(db).recalculate(user_id)
  from app.services.alerts import AlertEngine
  AlertEngine(db).recalculate(user_id)
 except Exception:
  db.rollback()
