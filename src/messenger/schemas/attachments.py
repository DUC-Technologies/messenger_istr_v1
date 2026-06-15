from typing import Any, Optional
import uuid
from pydantic import BaseModel

    
class AttachmentInput(BaseModel):
    name: str
    url: str
    metadata: Optional[Any] = None


class SendMessageRequest(BaseModel):
    chat_id: uuid.UUID
    text: str
    pics: Optional[AttachmentInput] = None
    audio: Optional[AttachmentInput] = None
    attachments: Optional[list[AttachmentInput]] = None
    reply_markup: Optional[str] = None


class AttachmentMeta(BaseModel):
    """Метаданные файла, хранимые в JSONB-колонке messages.attachments."""
    id: str
    file_name: str
    content_type: str
    object_key: str
    

class AttachmentResponse(BaseModel):
    """Метаданные файла с временной ссылкой для скачивания (для фронтенда)."""
    id: str
    file_name: str
    content_type: str
    download_url: str
