import logging
from fastapi import FastAPI,HTTPException,Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse,PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from app.api.routes.auth import limiter,router as auth_router
from app.api.routes.contractors import router as contractors_router
from app.api.routes.shifts import router as shifts_router
from app.api.routes.receivables import router as receivables_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.taxes import router as taxes_router
from app.api.routes.cashflow import router as cashflow_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.today import router as today_router
from app.api.routes.insights import router as insights_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.goals import router as goals_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.admin_users import router as admin_users_router
from app.api.routes.assistants import router as assistants_router
from app.api.routes.assistant_dashboard import router as assistant_dashboard_router
from app.api.routes.recurring_incomes import router as recurring_incomes_router
from app.api.routes.locations import router as locations_router
from app.api.routes.medical_specialties import router as medical_specialties_router
from app.api.routes.financial import router as financial_router
from app.core.config import get_settings
from app.core.middleware import AuditMiddleware,RequestContextMiddleware
from app.database.session import SessionLocal
from app.infrastructure.cache import get_cache
from app.infrastructure.jobs import get_job_queue
from app.infrastructure.storage import get_storage
settings=get_settings();logging.basicConfig(level=getattr(logging,settings.log_level.upper(),'INFO'),format='%(asctime)s %(levelname)s %(name)s %(message)s')
app=FastAPI(title='CRMoney API',version=settings.app_version,docs_url='/docs' if settings.enable_docs else None,redoc_url='/redoc' if settings.enable_docs else None,openapi_url='/openapi.json' if settings.enable_docs else None)
app.state.limiter=limiter;app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(AuditMiddleware);app.add_middleware(RequestContextMiddleware);app.add_middleware(GZipMiddleware,minimum_size=700);app.add_middleware(TrustedHostMiddleware,allowed_hosts=settings.hosts);app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'],allow_headers=['Authorization','Content-Type','X-Request-ID','X-Device-Name'])
for router in (auth_router,contractors_router,shifts_router,receivables_router,recurring_incomes_router,locations_router,medical_specialties_router,financial_router,dashboard_router,invoices_router,taxes_router,cashflow_router,expenses_router,today_router,insights_router,analytics_router,goals_router,alerts_router,admin_users_router,assistants_router,assistant_dashboard_router):app.include_router(router,prefix='/api/v1')
@app.exception_handler(HTTPException)
async def http_error(request:Request,error:HTTPException):return JSONResponse(status_code=error.status_code,content={'success':False,'error':{'code':f'HTTP_{error.status_code}','message':str(error.detail),'request_id':getattr(request.state,'request_id',None)},'detail':error.detail},headers=error.headers)
@app.exception_handler(RequestValidationError)
async def validation_error(request:Request,error:RequestValidationError):return JSONResponse(status_code=422,content={'success':False,'error':{'code':'VALIDATION_ERROR','message':'Dados inválidos.','request_id':getattr(request.state,'request_id',None),'fields':error.errors()},'detail':error.errors()})
@app.exception_handler(Exception)
async def internal_error(request:Request,error:Exception):logging.getLogger('crmoney').exception('Unhandled error',extra={'request_id':getattr(request.state,'request_id',None)});return JSONResponse(status_code=500,content={'success':False,'error':{'code':'INTERNAL_ERROR','message':'Erro interno. Tente novamente.','request_id':getattr(request.state,'request_id',None)},'detail':'Erro interno. Tente novamente.'})
def dependencies_health():
 result={'api':'ok'};db=SessionLocal()
 try:db.execute(text('SELECT 1'));result['database']='ok'
 except Exception:result['database']='error'
 finally:db.close()
 for name,check in [('cache',lambda:get_cache().health()),('queue',lambda:get_job_queue().health()),('storage',lambda:get_storage().health())]:
  try:result[name]='ok' if check() else 'error'
  except Exception:result[name]='error'
 return result
@app.get('/health',tags=['Monitoring'])
def health():
 checks=dependencies_health();return {'status':'ok' if all(x=='ok' for x in checks.values()) else 'degraded','version':settings.app_version,'environment':settings.environment,'checks':checks}
@app.get('/live',tags=['Monitoring'])
def live():return {'status':'ok','api':'ok'}
@app.get('/ready',tags=['Monitoring'])
def ready():
 checks=dependencies_health()
 if any(x!='ok' for x in checks.values()):raise HTTPException(503,'Uma ou mais dependências não estão prontas.')
 return {'status':'ok','checks':checks}
@app.get('/metrics',include_in_schema=False)
def metrics():return PlainTextResponse('crmoney_api_up 1\n',media_type='text/plain; version=0.0.4')
