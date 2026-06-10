import uuid

from messenger.db import AbstractTopicDAL
from messenger.schemas import UserID


class TopicService:
    def __init__(self, dal: AbstractTopicDAL):
        self.dal = dal

    def create_topic(self, title: str, topic_type: str):
        topic_id = uuid.uuid4()
        return self.dal.create_topic(topic_id, title, topic_type)

    def get_last_messages_of_topic(self, topic_id: uuid.UUID, limit: int = 30):
        return self.dal.get_last_messages_of_topic(topic_id, limit)

    def get_topics_by_user(self, body: UserID):
        return self.dal.get_topics_by_user(body.user_id)

    # def get_users_of_topic(self, body: TopicID):
    #     return self.dal.get_users_of_topic(body.topic_id)

    # def delete_topic(self, body: TopicID):
    #     return self.dal.delete_topic(body.topic_id)

    # def add_user_to_topic(self, body: AddUserToTopic):
    #     return self.dal.add_user_to_topic(body.topic_id, body.user_id)
