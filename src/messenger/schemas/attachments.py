import uuid
from pydantic import BaseModel


class AttachmentMeta(BaseModel):
    """Метаданные файла, хранимые в JSONB-колонке messages.attachments."""
    id: str
    file_name: str
    content_type: str
    object_key: str  # путь внутри S3-бакета


class AttachmentResponse(BaseModel):
    """Метаданные файла с временной ссылкой для скачивания (для фронтенда)."""
    id: str
    file_name: str
    content_type: str
    download_url: str  # presigned URL, генерируется динамически
