import uuid

from messenger.db import AbstractMessageDAL, AbstractTopicDAL
from messenger.schemas import CreateMessage, MessageID, UpdateMessage


class MessageService:
    def __init__(self, message_dal: AbstractMessageDAL, topic_dal: AbstractTopicDAL):
        self.message_dal = message_dal
        self.topic_dal = topic_dal
        
    async def send_message_to_bot(self, author_id: uuid.UUID, text: str):
        # 1. Автоматическая проверка: ищем топик пользователя (где topic_id == user_id)
        existing_topics = await self.topic_dal.get_topics_by_user(user_id=author_id)
        
        # 2. Если топика нет — прозрачно создаем его
        if not existing_topics:
            await self.topic_dal.create_topic(
                topic_id=author_id,
                title=f"Чат с ботом"
            )
        
        # 3. Создаем и сохраняем само сообщение
        message_id = uuid4()
        new_message = await self.message_dal.create_message(
            topic_id=author_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            has_attachment=False,
        )
        
        # 4. Важно: фиксируем изменения в БД (так как в DAL вызывается только flush)
        await self.message_dal.db_session.commit()
        
        return new_message

    async def send_message(self, author_id, text):
        message_id = uuid.uuid4()
        return await self.message_dal.create_message(
            topic_id=author_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            has_attachment=False,
        )

    async def get_message_by_id(self, body: MessageID):
        return await self.message_dal.get_message_by_id(body.topic_id, body.message_id)

    async def update_message(self, body: UpdateMessage):
        return await self.message_dal.update_message(body.topic_id, body.message_id, body.text)

    async def delete_message(self, body: MessageID):
        return await self.message_dal.delete_message(body.topic_id, body.message_id)
