from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.session import init_db

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.policies import router as policy_router
from app.api.v1.endpoints.claims import router as claim_router
from app.api.v1.endpoints.payments import router as payment_router
from app.api.v1.endpoints.documents import router as document_router
from app.api.v1.endpoints.health import router as health_router

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s [%s]", settings.APP_NAME, settings.APP_ENV)
    await init_db()
    logger.info("Database tables ready")
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Insurance Policy & Claims Management API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler — keep stack traces server-side only
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


API_PREFIX = "/api/v1"
app.include_router(health_router)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(policy_router, prefix=API_PREFIX)
app.include_router(claim_router, prefix=API_PREFIX)
app.include_router(payment_router, prefix=API_PREFIX)
app.include_router(document_router, prefix=API_PREFIX)
