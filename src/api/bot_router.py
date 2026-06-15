import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends
import redis.asyncio as aioredis

from auth.models import User
from auth.services.auth import get_current_user_from_token
from bot_engine import Dispatcher, MessageContext, CallbackContext
from dependencies import get_message_service
from messenger.schemas.bot import (
    UserMessageCreate,
    UserCallbackTrigger,
    BotReplyMessage,
    BotSyncResponse,
    MessageResponse,
    InlineButton,
)
from messenger.services.message_service import MessageService
from survey.presenter import ScreenPayload

bot_router = APIRouter(prefix="/bot", tags=["bot"])

_redis_client: aioredis.Redis | None = None
_dispatcher: Dispatcher | None = None
_s3_service = None  # S3StorageService — тип не импортируем здесь, чтобы избежать циклов

BOT_AUTHOR_ID = uuid.UUID("9e31a6e6-7af8-44d5-aca2-f1224fd80061")


def init_bot(dispatcher: Dispatcher, redis_client: aioredis.Redis, s3_service) -> None:
    global _dispatcher, _redis_client, _s3_service
    _dispatcher = dispatcher
    _redis_client = redis_client
    _s3_service = s3_service


def _make_reply_collector() -> tuple[list[BotReplyMessage], Any]:
    replies: list[BotReplyMessage] = []

    async def reply(
        text: str | None = None,
        buttons: list[list[dict]] | None = None,
        screen_payloads: list[ScreenPayload] | None = None,
        attachment_object_key: str | None = None,
        attachment_file_name: str | None = None,
        attachment_content_type: str | None = None,
    ) -> None:
        if screen_payloads is not None:
            for sp in screen_payloads:
                replies.append(BotReplyMessage(
                    # ИСПРАВЛЕНО: берем message_id из ScreenPayload, если он задан
                    message_id=sp.message_id if hasattr(sp, "message_id") and sp.message_id else uuid.uuid4(),
                    text=sp.text,
                    buttons=[
                        [InlineButton(label=b.label, payload=b.payload, selected=b.selected) for b in row]
                        for row in sp.buttons
                    ],
                ))
        else:
            # Для обычных текстовых сообщений оставляем генерацию нового UUID
            parsed_buttons: list[list[InlineButton]] = []
            if buttons:
                parsed_buttons = [
                    [InlineButton(**b) for b in row]
                    for row in buttons
                ]
            replies.append(BotReplyMessage(
                message_id=uuid.uuid4(),
                text=text or "",
                buttons=parsed_buttons,
                attachment_object_key=attachment_object_key,
                attachment_file_name=attachment_file_name,
                attachment_content_type=attachment_content_type,
            ))

    return replies, reply


async def _dispatch_and_save(
    ctx: MessageContext | CallbackContext,
    replies: list[BotReplyMessage],
    message_service: MessageService,
    user_id: uuid.UUID,
) -> list[MessageResponse]:
    await _dispatcher.dispatch(ctx)
    saved = await message_service.save_bot_replies(
        user_id=user_id,
        bot_author_id=BOT_AUTHOR_ID,
        replies=replies,
    )
    return [await message_service._enrich_message(msg) for msg in saved]


@bot_router.post("/message", response_model=BotSyncResponse)
async def handle_message(
    body: UserMessageCreate,
    current_user: User = Depends(get_current_user_from_token),
    message_service: MessageService = Depends(get_message_service),
):
    await message_service.ensure_topic_exists(current_user.user_id)
    await message_service.save_user_message(current_user.user_id, body.text)

    replies, reply_fn = _make_reply_collector()
    ctx = MessageContext(
        user_id=current_user.user_id,
        text=body.text,
        extra={"redis": _redis_client, "reply": reply_fn, "s3_service": _s3_service},
    )

    response_messages = await _dispatch_and_save(ctx, replies, message_service, current_user.user_id)
    await message_service.message_dal.db_session.commit()
    return BotSyncResponse(messages=response_messages)


@bot_router.post("/callback", response_model=BotSyncResponse)
async def handle_callback(
    body: UserCallbackTrigger,
    current_user: User = Depends(get_current_user_from_token),
    message_service: MessageService = Depends(get_message_service),
):
    await message_service.ensure_topic_exists(current_user.user_id)

    replies, reply_fn = _make_reply_collector()
    ctx = CallbackContext(
        user_id=current_user.user_id,
        payload=body.payload,
        extra={
            "redis": _redis_client, 
            "reply": reply_fn, 
            "s3_service": _s3_service,
            "message_id": getattr(body, "message_id", None)
        },
    )

    response_messages = await _dispatch_and_save(ctx, replies, message_service, current_user.user_id)
    await message_service.message_dal.db_session.commit()
    return BotSyncResponse(messages=response_messages)


@bot_router.get("/history", response_model=list[MessageResponse])
async def get_bot_history(
    limit: int = 50,
    before_message_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user_from_token),
    message_service: MessageService = Depends(get_message_service),
):
    return await message_service.get_bot_history(
        user_id=current_user.user_id,
        limit=limit,
        before_message_id=before_message_id,
    )


@bot_router.get("/updates", response_model=list[MessageResponse])
async def get_bot_updates(
    since_message_id: uuid.UUID,
    current_user: User = Depends(get_current_user_from_token),
    message_service: MessageService = Depends(get_message_service),
):
    """Polling-эндпоинт. Фронтенд передаёт ID последнего известного сообщения."""
    return await message_service.get_updates(
        user_id=current_user.user_id,
        since_message_id=since_message_id,
    )