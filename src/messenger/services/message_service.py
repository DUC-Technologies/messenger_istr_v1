from uuid import uuid4

from messenger.db import AbstractMessageDAL
from messenger.schemas import CreateMessage, MessageID, UpdateMessage


class MessageService:
    def __init__(self, dal: AbstractMessageDAL):
        self.dal = dal

    async def send_message_to_bot(self, author_id, text):
        message_id = uuid4()
        return await self.dal.create_message(
            topic_id=author_id,
            message_id=message_id,
            text=text,
            author_id=author_id,
            has_attachment=False,
        )

    async def get_message_by_id(self, body: MessageID):
        return await self.dal.get_message_by_id(body.topic_id, body.message_id)

    async def update_message(self, body: UpdateMessage):
        return await self.dal.update_message(body.topic_id, body.message_id, body.text)

    async def delete_message(self, body: MessageID):
        return await self.dal.delete_message(body.topic_id, body.message_id)
