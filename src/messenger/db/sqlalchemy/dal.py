import uuid
from typing import Any, List, Optional

from sqlalchemy import select, update, delete, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from messenger.db.base_dal import AbstractMessageDAL, AbstractTopicDAL
from messenger.db.sqlalchemy.models import Message, Topic


class SQLAlchemyMessageDAL(AbstractMessageDAL):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_message(
        self,
        topic_id: uuid.UUID,
        message_id: uuid.UUID,
        text: str,
        author_id: uuid.UUID,
        buttons: list[list[dict]] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> Message:


        existing_msg = await self.db_session.get(Message, message_id)
        
        if existing_msg:
            existing_msg.text = text
            existing_msg.buttons = buttons
            existing_msg.attachments = attachments
            if hasattr(existing_msg, "is_edited"):
                existing_msg.is_edited = True
                
            await self.db_session.flush()
            return existing_msg
        
        new_message = Message(
            topic_id=topic_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            buttons=buttons,
            attachments=attachments,
        )
        self.db_session.add(new_message)
        await self.db_session.flush()
        return new_message

    async def get_message_by_id(self, topic_id: uuid.UUID, message_id: uuid.UUID) -> Optional[Message]:
        query = select(Message).where(
            Message.topic_id == topic_id,
            Message.message_id == message_id,
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_message(self, topic_id: uuid.UUID, message_id: uuid.UUID, text: str) -> Optional[uuid.UUID]:
        query = (
            update(Message)
            .where(Message.topic_id == topic_id, Message.message_id == message_id)
            .values(text=text, is_edited=True)
            .returning(Message.message_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def delete_message(self, topic_id: uuid.UUID, message_id: uuid.UUID) -> Optional[uuid.UUID]:
        query = (
            delete(Message)
            .where(Message.topic_id == topic_id, Message.message_id == message_id)
            .returning(Message.message_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_messages_after(
        self,
        topic_id: uuid.UUID,
        since_message_id: uuid.UUID,
    ) -> List[Message]:
        """Возвращает сообщения новее указанного (для polling-эндпоинта /updates)."""
        since_msg = await self.get_message_by_id(topic_id, since_message_id)
        if since_msg is None:
            return []
        query = (
            select(Message)
            .where(
                Message.topic_id == topic_id,
                Message.created_at > since_msg.created_at,
            )
            .order_by(asc(Message.created_at))
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())


class SQLAlchemyTopicDAL(AbstractTopicDAL):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_topic(self, topic_id: uuid.UUID, title: str, topic_type: str = None) -> Topic:
        new_topic = Topic(topic_id=topic_id, title=title, topic_type=topic_type)
        self.db_session.add(new_topic)
        await self.db_session.flush()
        return new_topic

    async def get_last_messages_of_topic(self, topic_id: uuid.UUID, limit: int = 30) -> List[Message]:
        query = (
            select(Message)
            .where(Message.topic_id == topic_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        messages = result.scalars().all()
        return list(reversed(messages))

    async def get_topics_by_user(self, user_id: uuid.UUID) -> List[Topic]:
        query = select(Topic).where(Topic.topic_id == user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def topic_exists(self, topic_id: uuid.UUID) -> bool:
        query = select(Topic.topic_id).where(Topic.topic_id == topic_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none() is not None
    