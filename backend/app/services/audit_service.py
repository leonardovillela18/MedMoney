import json
from sqlalchemy.orm import Session
from app.models.enterprise import AuditLog
class AuditService:
 @staticmethod
 def record(db:Session,action:str,entity:str,user_id=None,entity_id=None,request=None,metadata=None):
  log=AuditLog(user_id=user_id,action=action,entity=entity,entity_id=str(entity_id) if entity_id else None,ip_address=request.client.host if request and request.client else None,user_agent=(request.headers.get('user-agent','')[:500] if request else None),request_id=getattr(request.state,'request_id',None) if request else None,metadata_json=json.dumps(metadata,ensure_ascii=False) if metadata else None);db.add(log);db.commit();return log
