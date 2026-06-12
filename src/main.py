import aioboto3
import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import login_router, user_router
from api.bot_router import bot_router, init_bot
from bot_engine import Dispatcher
from infra.s3_storage import S3StorageService
from survey import survey_router
import settings

app = FastAPI(title="Messenger")


@app.on_event("startup")
async def startup():
    redis_client = aioredis.from_url("redis://localhost:6379")
    s3_service = S3StorageService(session=aioboto3.Session())
    await s3_service.ensure_bucket_exists(settings.S3_BUCKET_REPORTS)

    dp = Dispatcher()
    dp.include_router(survey_router)

    init_bot(dispatcher=dp, redis_client=redis_client, s3_service=s3_service)


app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(bot_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})