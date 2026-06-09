from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Attachment(BaseModel):
    type: str
    url: HttpUrl
    thumbnail: Optional[HttpUrl] = None


class SendMessage(BaseModel):
    chat_id: str
    content: str
    reply_to: Optional[str] = None
    attachments: Optional[list[Attachment]] = None


class ReceivedMessage(SendMessage):
    id: str
    sender_id: str
    timestamp: datetime
