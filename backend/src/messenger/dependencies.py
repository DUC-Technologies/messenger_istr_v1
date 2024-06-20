from messenger.db import ScyllaMessageDAL, ScyllaTopicDAL
from messenger.db.scylladb_sync.dal import ScyllaContactDAL
from .services import MessageService, TopicService
from .services.contact_service import ContactService


def get_message_service() -> MessageService:
    dal = ScyllaMessageDAL()
    return MessageService(dal=dal)


def get_topic_service() -> TopicService:
    dal = ScyllaTopicDAL()
    return TopicService(dal=dal)


def get_contact_service() -> ContactService:
    dal = ScyllaContactDAL()
    return ContactService(dal=dal)
