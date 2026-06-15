import uuid
from typing import Any, Optional

from messenger.db import AbstractMessageDAL, AbstractTopicDAL
from messenger.db.sqlalchemy.dal import SQLAlchemyMessageDAL
from messenger.db.sqlalchemy.models import Message
from messenger.schemas.attachments import AttachmentMeta, AttachmentResponse
from messenger.schemas.bot import BotReplyMessage, MessageResponse, InlineButton
from infra.s3_storage import S3StorageService
import settings


class MessageService:
    def __init__(
        self,
        message_dal: AbstractMessageDAL,
        topic_dal: AbstractTopicDAL,
        s3_service: S3StorageService,
    ):
        self.message_dal = message_dal
        self.topic_dal = topic_dal
        self.s3_service = s3_service

    async def ensure_topic_exists(self, user_id: uuid.UUID) -> None:
        if not await self.topic_dal.topic_exists(user_id):
            await self.topic_dal.create_topic(
                topic_id=user_id,
                title=f"Chat with User {user_id}",
                topic_type=1,
            )

    async def save_user_message(self, user_id: uuid.UUID, text: str) -> Message:
        message_id = uuid.uuid4()
        return await self.message_dal.create_message(
            topic_id=user_id,
            message_id=message_id,
            text=text,
            author_id=user_id,
        )

    async def save_bot_replies(
        self,
        user_id: uuid.UUID,
        bot_author_id: uuid.UUID,
        replies: list[BotReplyMessage],
    ) -> list[Message]:
        saved = []
        for reply in replies:
            raw_buttons = (
                [[btn.model_dump() for btn in row] for row in reply.buttons]
                if reply.buttons else None
            )
            raw_attachments = None
            if reply.attachment_object_key:
                raw_attachments = [
                    AttachmentMeta(
                        id=str(uuid.uuid4()),
                        file_name=reply.attachment_file_name or "attachment",
                        content_type=reply.attachment_content_type or "application/octet-stream",
                        object_key=reply.attachment_object_key,
                    ).model_dump()
                ]

            msg = await self.message_dal.create_message(
                topic_id=user_id,
                message_id=reply.message_id,
                text=reply.text,
                author_id=bot_author_id,
                buttons=raw_buttons,
                attachments=raw_attachments,
            )
            saved.append(msg)
        return saved

    async def get_bot_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        before_message_id: Optional[uuid.UUID] = None,
    ) -> list[MessageResponse]:
        if before_message_id:
            # Пагинация: сообщения до указанного ID реализуется через timestamp.
            # Используем базовый метод; курсорная пагинация — расширение при необходимости.
            messages = await self.topic_dal.get_last_messages_of_topic(user_id, limit)
        else:
            messages = await self.topic_dal.get_last_messages_of_topic(user_id, limit)

        return [await self._enrich_message(msg) for msg in messages]

    async def get_updates(
        self,
        user_id: uuid.UUID,
        since_message_id: uuid.UUID,
    ) -> list[MessageResponse]:
        assert isinstance(self.message_dal, SQLAlchemyMessageDAL)
        messages = await self.message_dal.get_messages_after(user_id, since_message_id)
        return [await self._enrich_message(msg) for msg in messages]

    async def _enrich_message(self, msg: Message) -> MessageResponse:
        """Конвертирует ORM-объект в MessageResponse, учитывая внешние ссылки."""
        attachment_responses: list[AttachmentResponse] = []
        if msg.attachments:
            for raw in msg.attachments:
                meta = AttachmentMeta(**raw)
                
                if meta.object_key.startswith(("http://", "https://")):
                    url = meta.object_key
                else:
                    url = await self.s3_service.generate_presigned_url(
                        bucket=settings.S3_BUCKET_REPORTS,
                        object_key=meta.object_key,
                        expires_in=settings.S3_PRESIGNED_URL_EXPIRES,
                    )
                
                attachment_responses.append(
                    AttachmentResponse(
                        id=meta.id,
                        file_name=meta.file_name,
                        content_type=meta.content_type,
                        download_url=url,
                    )
                )

        buttons: list[list[InlineButton]] = []
        if msg.buttons:
            buttons = [[InlineButton(**btn) for btn in row] for row in msg.buttons]

        return MessageResponse(
            message_id=msg.message_id,
            topic_id=msg.topic_id,
            author_id=msg.author_id,
            text=msg.text,
            created_at=msg.created_at,
            buttons=buttons,
            attachments=attachment_responses,
        )
        
    async def save_bot_message(
        self,
        user_id: uuid.UUID,
        message_id: uuid.UUID,
        bot_author_id: uuid.UUID,
        text: str,
        buttons: list[list[dict]] | None,
        attachments: list[dict] | None = None,
    ) -> bool:
        """
        Сохраняет сообщение от бота, переданное через API-эндпоинт.
        """
        await self.ensure_topic_exists(user_id)
        await self.message_dal.create_message(
            topic_id=user_id,
            message_id=message_id,
            text=text,
            author_id=bot_author_id,
            buttons=buttons,
            attachments=attachments,
        )
        return True
    