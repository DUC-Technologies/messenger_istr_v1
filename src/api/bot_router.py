import datetime
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.services.auth import get_current_user_from_token
from bot_engine import Dispatcher, MessageContext, CallbackContext
from dependencies import get_message_service, get_topic_service
from messenger.services.topic_service import TopicService
from survey.presenter import ScreenPayload
from database.session import get_db
from messenger.db.sqlalchemy.models import Topic 

bot_router = APIRouter(prefix="/bot", tags=["bot"])

_redis_client: aioredis.Redis | None = None
_dispatcher: Dispatcher | None = None

BOT_AUTHOR_ID = uuid.UUID("9e31a6e6-7af8-44d5-aca2-f1224fd80061")


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
    message_id: uuid.UUID
    text: str
    buttons: list[list[ButtonSchema]] = []
    attachment_url: str | None = None


class BotResponse(BaseModel):
    messages: list[MessageSchema]
    
class BotHistoryMessageSchema(BaseModel):
    message_id: uuid.UUID
    text: str
    author_id: uuid.UUID
    created_at: datetime.datetime
    buttons: list[list[ButtonSchema]] | None = []
    attachment_url: str | None = None


async def ensure_topic_exists(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Гарантирует наличие топика (чата) в БД перед вставкой сообщений."""
    query = select(Topic).where(Topic.topic_id == user_id)
    res = await db.execute(query)
    topic = res.scalar_one_or_none()
    if not topic:
        new_topic = Topic(
            topic_id=user_id,
            title=f"Chat with User {user_id}",
            topic_type=1
        )
        db.add(new_topic)
        await db.flush()
        
        
async def save_bot_responses(
    db: AsyncSession, 
    message_service: Any, 
    user_id: uuid.UUID, 
    messages: list[MessageSchema]
) -> None:
    """Вспомогательная функция для сохранения пачки ответов бота в БД"""
    for msg in messages:
        raw_buttons = (
            [[btn.model_dump() for btn in row] for row in msg.buttons] 
            if msg.buttons else None
        )
        await message_service.message_dal.create_message(
            topic_id=user_id,
            message_id=msg.message_id,
            text=msg.text,
            author_id=BOT_AUTHOR_ID,
            buttons=raw_buttons 
        )


def _make_reply_collector() -> tuple[list[MessageSchema], Any]:
    """Накапливает схемы сообщений, автоматически генерируя им UUID."""
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
                    message_id=uuid.uuid4(),  # Генерируем уникальный ID для каждого блока
                    text=sp.text,
                    buttons=[
                        [ButtonSchema(label=b.label, payload=b.payload, selected=b.selected) for b in row]
                        for row in sp.buttons
                    ],
                ))
        else:
            messages.append(MessageSchema(
                message_id=uuid.uuid4(),  # Генерируем уникальный ID
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
    db: AsyncSession = Depends(get_db),
):
    messages, reply_fn = _make_reply_collector()
    message_service = get_message_service(db)
    
    # 1. Гарантируем существование топика чата
    await ensure_topic_exists(db, current_user.user_id)
    
    # 2. Сохраняем входящее сообщение пользователя
    user_message_id = uuid.uuid4()
    await message_service.message_dal.create_message(
        topic_id=current_user.user_id,
        message_id=user_message_id,
        text=body.text,
        author_id=current_user.user_id,
        # has_attachment=False
    )
    
    # 3. Передаем контекст в диспетчер сценариев/опросов
    ctx = MessageContext(
        user_id=current_user.user_id,
        text=body.text,
        extra={
            "redis": _redis_client,
            "reply": reply_fn,
            "message_service": message_service,
        },
    )
    await _dispatcher.dispatch(ctx)
    
    await save_bot_responses(db, message_service, current_user.user_id, messages)
    await db.commit()  # Фиксируем трансляцию в БД
    return BotResponse(messages=messages)


@bot_router.post("/callback", response_model=BotResponse)
async def handle_callback(
    body: IncomingCallback,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    messages, reply_fn = _make_reply_collector()
    message_service = get_message_service(db)
    
    await ensure_topic_exists(db, current_user.user_id)
    
    ctx = CallbackContext(
        user_id=current_user.user_id,
        payload=body.payload,
        extra={
            "redis": _redis_client,
            "reply": reply_fn,
            "message_service": message_service
        },
    )
    await _dispatcher.dispatch(ctx)
    
    await save_bot_responses(db, message_service, current_user.user_id, messages)
    await db.commit()
    return BotResponse(messages=messages)

@bot_router.get("/history", response_model=list[BotHistoryMessageSchema])
async def get_bot_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение истории сообщений текущего пользователя с ботом.
    Так как для бота topic_id равен user_id пользователя, получаем историю по его ID.
    """
    message_service = get_message_service(db)
    
    # Вызываем метод получения сообщений из вашего SQLAlchemyMessageDAL
    # (Название метода может немного отличаться, сверьтесь с вашим `message_dal`)
    messages = await message_service.topic_dal.get_last_messages_of_topic(
        topic_id=current_user.user_id,
        limit=limit
    )
    
    return messages

