from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.api.routes.auth import router as auth_router, limiter
from app.api.routes.contractors import router as contractors_router
from app.api.routes.shifts import router as shifts_router
from app.core.config import get_settings
app=FastAPI(title='MedMoney API',version='0.1.0')
app.state.limiter=limiter; app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware,allow_origins=get_settings().origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth_router,prefix='/api/v1')
app.include_router(contractors_router,prefix='/api/v1')
app.include_router(shifts_router,prefix='/api/v1')
@app.get('/health')
def health(): return {'status':'ok'}
