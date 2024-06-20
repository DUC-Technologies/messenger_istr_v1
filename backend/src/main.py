import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import settings
from api import login_router
from api import messenger_router
from api import user_router
from api.chat_ws_router import chat_ws_router

app = FastAPI(
    title='Messenger'
)

app.include_router(messenger_router, prefix="/messenger")
app.include_router(chat_ws_router, prefix="/messenger", tags=["chat"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(login_router, prefix="/login", tags=["login"])

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )


@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.MESSENGER_APP_PORT)
