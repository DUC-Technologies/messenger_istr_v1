import uuid

from messenger.db import AbstractMessageDAL, AbstractTopicDAL
from messenger.schemas import MessageID, UpdateMessage


class MessageService:
    def __init__(self, message_dal: AbstractMessageDAL, topic_dal: AbstractTopicDAL):
        self.message_dal = message_dal
        self.topic_dal = topic_dal
        
    async def send_message_to_bot(self, author_id: uuid.UUID, text: str):
        existing_topics = await self.topic_dal.get_topics_by_user(user_id=author_id)
        
        if not existing_topics:
            await self.topic_dal.create_topic(
                topic_id=author_id,
                title=f"Чат с ботом"
            )
        
        message_id = uuid.uuid4()
        new_message = await self.message_dal.create_message(
            topic_id=author_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            has_attachment=False,
        )
        
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
