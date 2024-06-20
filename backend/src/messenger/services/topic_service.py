from uuid import uuid4

from messenger.db import AbstractTopicDAL
from messenger.schemas import CreateTopic, TopicLimit, UserID, TopicID, AddUserToTopic


class TopicService:
    def __init__(self, dal: AbstractTopicDAL):
        self.dal = dal

    def create_topic(self, body: CreateTopic):
        topic_id = uuid4()
        return self.dal.create_topic(topic_id, body.title, body.topic_type)

    def get_last_messages_of_topic(self, body: TopicLimit):
        return self.dal.get_last_messages_of_topic(body.topic_id, body.limit)

    def get_topics_by_user(self, body: UserID):
        return self.dal.get_topics_by_user(body.user_id)

    def get_users_of_topic(self, body: TopicID):
        return self.dal.get_users_of_topic(body.topic_id)

    def delete_topic(self, body: TopicID):
        return self.dal.delete_topic(body.topic_id)

    def add_user_to_topic(self, body: AddUserToTopic):
        return self.dal.add_user_to_topic(body.topic_id, body.user_id)
