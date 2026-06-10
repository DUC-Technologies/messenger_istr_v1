import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import login_router, messenger_router, user_router
from api.bot_router import bot_router, init_bot
from bot_engine import Dispatcher
from survey import survey_router

app = FastAPI(title="Messenger")


@app.on_event("startup")
async def startup():
    redis_client = aioredis.from_url("redis://localhost:6379")

    dp = Dispatcher()
    dp.include_router(survey_router)

    init_bot(dispatcher=dp, redis_client=redis_client)


app.include_router(messenger_router, prefix="/messenger")
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
