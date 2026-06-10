from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

import redis.asyncio as aioredis

from auth.models import User
from auth.services.auth import get_current_user_from_token
from bot_engine import Dispatcher, MessageContext, CallbackContext
from survey.presenter import ScreenPayload

bot_router = APIRouter(prefix="/bot", tags=["bot"])

_redis_client: aioredis.Redis | None = None
_dispatcher: Dispatcher | None = None


def init_bot(dispatcher: Dispatcher, redis_client: aioredis.Redis) -> None:
    """Called once at application startup."""
    global _dispatcher, _redis_client
    _dispatcher = dispatcher
    _redis_client = redis_client


class IncomingMessage(BaseModel):
    text: str


class IncomingCallback(BaseModel):
    payload: dict[str, Any]


class ButtonSchema(BaseModel):
    label: str
    payload: dict[str, Any]
    selected: bool = False


class MessageSchema(BaseModel):
    text: str
    buttons: list[list[ButtonSchema]] = []
    attachment_url: str | None = None


class BotResponse(BaseModel):
    messages: list[MessageSchema]


def _make_reply_collector() -> tuple[list[MessageSchema], Any]:
    """
    Returns (messages, reply_fn).

    Handlers call reply_fn to emit responses. The collector accumulates
    MessageSchema objects that are returned to the HTTP client as one response.

    reply_fn accepts either:
      - screen_payloads: list[ScreenPayload]  — bulk from survey blocks
      - text + buttons + attachment_url       — single arbitrary message
    """
    messages: list[MessageSchema] = []

    async def reply(
        text: str | None = None,
        buttons: list[list[dict]] | None = None,
        screen_payloads: list[ScreenPayload] | None = None,
        attachment_url: str | None = None,
    ) -> None:
        if screen_payloads is not None:
            for sp in screen_payloads:
                messages.append(MessageSchema(
                    text=sp.text,
                    buttons=[
                        [ButtonSchema(label=b.label, payload=b.payload, selected=b.selected) for b in row]
                        for row in sp.buttons
                    ],
                ))
        else:
            messages.append(MessageSchema(
                text=text or "",
                buttons=[
                    [ButtonSchema(**b) for b in row]
                    for row in (buttons or [])
                ],
                attachment_url=attachment_url,
            ))

    return messages, reply


@bot_router.post("/message", response_model=BotResponse)
async def handle_message(
    body: IncomingMessage,
    current_user: User = Depends(get_current_user_from_token),
):
    messages, reply_fn = _make_reply_collector()
    ctx = MessageContext(
        user_id=current_user.user_id,
        text=body.text,
        extra={
            "redis": _redis_client,
            "reply": reply_fn,
            "message_service": get_message_service(db),
        },
    )
    await _dispatcher.dispatch(ctx)
    return BotResponse(messages=messages)


@bot_router.post("/callback", response_model=BotResponse)
async def handle_callback(
    body: IncomingCallback,
    current_user: User = Depends(get_current_user_from_token),
):
    messages, reply_fn = _make_reply_collector()
    ctx = CallbackContext(
        user_id=current_user.user_id,
        payload=body.payload,
        extra={"redis": _redis_client, "reply": reply_fn},
    )
    await _dispatcher.dispatch(ctx)
    return BotResponse(messages=messages)
