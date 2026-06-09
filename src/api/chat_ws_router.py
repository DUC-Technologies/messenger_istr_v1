import uuid
from datetime import datetime

from fastapi import (
    Cookie,
    Depends,
    Query,
    WebSocket,
    WebSocketException,
    status, APIRouter,
)
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect

from messenger.chat.connection_manager import ConnectionManager
from messenger.chat.html_stub_dev import get_html_stub_chat_dev
from messenger.chat.shemas import ReceivedMessage

chat_ws_router = APIRouter()
manager = ConnectionManager()


async def _get_cookie_or_token(
        websocket: WebSocket,
        session: str | None = Cookie(default=None),
        token: str | None = Query(default=None),
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


async def get_user_from_token(token):
    return token


@chat_ws_router.websocket("/chats/{chat_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: str,
    q: int | None = None,
    cookie_or_token: str = Depends(_get_cookie_or_token),
):
    await manager.connect(chat_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            user = await get_user_from_token(cookie_or_token)  # Получение user_id из токена

            received_message = ReceivedMessage(
                id=str(uuid.uuid4()),  # Генерация уникального ID
                chat_id=chat_id,
                sender_id=user,
                timestamp=datetime.utcnow(),
                content=data['content'],
                reply_to=data.get('reply_to'),
                attachments=data.get('attachments')
            )
            ic(received_message)

            await manager.push_to_chat(chat_id, received_message.dict())
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)


@chat_ws_router.get("/")
async def get():
    return HTMLResponse(get_html_stub_chat_dev())
