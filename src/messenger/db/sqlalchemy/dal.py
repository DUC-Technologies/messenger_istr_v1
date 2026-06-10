import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc

from messenger.db.base_dal import AbstractMessageDAL, AbstractTopicDAL
from messenger.db.sqlalchemy.models import Message, Topic


class SQLAlchemyMessageDAL(AbstractMessageDAL):
    """Асинхронный DAL для работы с сообщениями в PostgreSQL"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_message(
        self,
        topic_id: uuid.UUID,
        message_id: uuid.UUID,
        text: str,
        author_id: uuid.UUID,
        has_attachment: bool,
    ) -> Message:
        new_message = Message(
            topic_id=topic_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            has_attachment=has_attachment
        )
        self.db_session.add(new_message)
        await self.db_session.flush() 
        return new_message

    async def get_message_by_id(self, topic_id: uuid.UUID, message_id: uuid.UUID) -> Optional[Message]:
        query = select(Message).where(
            Message.topic_id == topic_id,
            Message.message_id == message_id
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


class SQLAlchemyTopicDAL(AbstractTopicDAL):
    """Асинхронный DAL для работы с топиками (сессиями чатов) в PostgreSQL"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_topic(self, topic_id: uuid.UUID, title: str, topic_type: str = None) -> Topic:
        new_topic = Topic(
            topic_id=topic_id,
            title=title,
            topic_type=topic_type
        )
        self.db_session.add(new_topic)
        await self.db_session.flush()
        return new_topic

    async def get_last_messages_of_topic(self, topic_id: uuid.UUID, limit: int = 30) -> List[Message]:
        """Получение истории сообщений чата (от старых к новым)"""
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
        # ВАРИАНТ А: один юзер = один топик, где topic_id == user_id
        query = select(Topic).where(Topic.topic_id == user_id)
        
        # ВАРИАНТ Б: полноценные групповые чаты через таблицу связи TopicMember
        # query = select(Topic).join(TopicMember).where(TopicMember.user_id == user_id)
        
        result = await self.db_session.execute(query)
        return list(result.scalars().all())