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
            message = await websocket.receive_text()
            message = f'<b>{cookie_or_token}<b>' + message
            await manager.push_to_chat(chat_id, message)
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)


@chat_ws_router.get("/")
async def get():
    return HTMLResponse(get_html_stub_chat_dev())
