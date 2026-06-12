import datetime
import uuid
from typing import Any

from pydantic import BaseModel

from messenger.schemas.attachments import AttachmentResponse


# --- Входящие запросы ---

class UserMessageCreate(BaseModel):
    text: str


class UserCallbackTrigger(BaseModel):
    payload: dict[str, Any]


# --- Компоненты UI ---

class InlineButton(BaseModel):
    label: str
    payload: dict[str, Any]
    selected: bool = False


# --- Исходящие ответы ---

class MessageResponse(BaseModel):
    """Универсальный объект сообщения для фронтенда."""
    message_id: uuid.UUID
    topic_id: uuid.UUID
    author_id: uuid.UUID
    text: str
    created_at: datetime.datetime
    buttons: list[list[InlineButton]] = []
    attachments: list[AttachmentResponse] = []

    class Config:
        from_attributes = True


class BotReplyMessage(BaseModel):
    """Накопитель ответов бота внутри одного запроса (до сохранения в БД)."""
    message_id: uuid.UUID
    text: str
    buttons: list[list[InlineButton]] = []
    # object_key вложения, если бот прикрепил файл из S3
    attachment_object_key: str | None = None
    attachment_file_name: str | None = None
    attachment_content_type: str | None = None


class BotSyncResponse(BaseModel):
    """Ответ на POST /bot/message и POST /bot/callback."""
    messages: list[MessageResponse]
