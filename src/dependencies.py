from messenger.db import ScyllaMessageDAL, ScyllaTopicDAL
from .messenger.services import MessageService, TopicService


def get_message_service() -> MessageService:
    dal = ScyllaMessageDAL()
    return MessageService(dal=dal)


def get_topic_service() -> TopicService:
    dal = ScyllaTopicDAL()
    return TopicService(dal=dal)

