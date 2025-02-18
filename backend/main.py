from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db, engine
import models, schemas
from auth import auth_router, create_access_token, pwd_context
from orders import orders_router
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from models import User

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders API",
    description="API для управления заказами",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Только фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(orders_router, prefix="/api", tags=["orders"])

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    end_time = datetime.utcnow()
    
    logger.info(
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Status: {response.status_code} "
        f"Duration: {(end_time - start_time).total_seconds():.3f}s"
    )
    return response

@app.get("/")
def read_root():
    return {"message": "Orders API"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "path": request.url.path
        }
    ) 