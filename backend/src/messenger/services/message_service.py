from uuid import uuid4

from messenger.db import AbstractMessageDAL
from messenger.schemas import CreateMessage, MessageID, UpdateMessage


class MessageService:
    def __init__(self, dal: AbstractMessageDAL):
        self.dal = dal

    def create_message(self, body: CreateMessage):
        message_id = uuid4()
        return self.dal.create_message(
            topic_id=body.topic_id,
            message_id=message_id,
            text=body.text,
            author_id=body.author_id,
            has_attachment=body.has_attachment,
        )

    def get_message_by_id(self, body: MessageID):
        return self.dal.get_message_by_id(body.topic_id, body.message_id)

    def update_message(self, body: UpdateMessage):
        return self.dal.update_message(body.topic_id, body.message_id, body.text)

    def delete_message(self, body: MessageID):
        return self.dal.delete_message(body.topic_id, body.message_id)
