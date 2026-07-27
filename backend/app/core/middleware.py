import json,logging,time,uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.database.session import SessionLocal
from app.services.audit_service import AuditService
logger=logging.getLogger('crmoney.http')
class RequestContextMiddleware(BaseHTTPMiddleware):
 async def dispatch(self,request:Request,call_next):
  request_id=request.headers.get('x-request-id') or str(uuid.uuid4());request.state.request_id=request_id;started=time.perf_counter()
  try:response=await call_next(request)
  except Exception:
   logger.exception(json.dumps({'event':'request_error','request_id':request_id,'method':request.method,'path':request.url.path}));raise
  duration=round((time.perf_counter()-started)*1000,2);response.headers['X-Request-ID']=request_id;response.headers['X-Content-Type-Options']='nosniff';response.headers['X-Frame-Options']='DENY';response.headers['Referrer-Policy']='strict-origin-when-cross-origin';response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()';response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self' http://localhost:8000 ws://localhost:*";
  if request.url.scheme=='https':response.headers['Strict-Transport-Security']='max-age=31536000; includeSubDomains'
  logger.info(json.dumps({'event':'request','request_id':request_id,'method':request.method,'path':request.url.path,'status':response.status_code,'duration_ms':duration}));return response
class AuditMiddleware(BaseHTTPMiddleware):
 async def dispatch(self,request:Request,call_next):
  response=await call_next(request)
  if request.method in ('POST','PUT','PATCH','DELETE') and request.url.path.startswith('/api/v1/') and response.status_code<400 and getattr(request.state,'user_id',None):
   parts=[x for x in request.url.path.split('/') if x];entity=parts[2] if len(parts)>2 else 'api';entity_id=parts[3] if len(parts)>3 else None;db=SessionLocal()
   try:AuditService.record(db,request.method,entity,getattr(request.state,'user_id'),entity_id,request)
   except Exception:db.rollback();logger.exception(json.dumps({'event':'audit_error','request_id':getattr(request.state,'request_id',None)}))
   finally:db.close()
  return response
