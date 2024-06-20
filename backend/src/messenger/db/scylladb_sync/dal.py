from datetime import datetime
from typing import Optional
from uuid import UUID

from messenger.db.base_dal import AbstractMessageDAL, AbstractTopicDAL, AbstractContactDAL
from .connection import setup_database_connection
from .models import Message, TopicsMember, UsersTopic, Topic, Contact

setup_database_connection()


class ScyllaMessageDAL(AbstractMessageDAL):

    def create_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str,
            author_id: UUID,
            has_attachment: bool,
    ):
        created_at = datetime.now()
        message = Message.create(
            topic_id=topic_id,
            message_id=message_id,
            text=text,
            created_at=created_at,
            author_id=author_id,
            has_attachment=has_attachment,
        )
        return message

    def get_message_by_id(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        return Message.objects(
            topic_id=topic_id,
            message_id=message_id
        ).first()

    def update_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str
    ):
        message = Message.objects(
            topic_id=topic_id,
            message_id=message_id,
        ).if_exists().first()

        # Обновляем сообщение, если оно найдено
        if message:
            message.update(
                text=text,
                is_edited=True,
            )
            return message
        else:
            # Сообщение не найдено, можно выбросить исключение или вернуть None
            return None

    def delete_message(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        message = self.get_message_by_id(topic_id, message_id)
        message.delete()


class ScyllaTopicDAL(AbstractTopicDAL):

    def create_topic(
            self,
            topic_id: UUID,
            title: str,
            topic_type: str,
    ):
        topic = Topic.create(
            topic_id=topic_id,
            title=title,
            topic_type=topic_type
        )
        return topic

    def get_last_messages_of_topic(
            self,
            topic_id: UUID,
            limit: int = 30,
    ):
        return Message.objects(topic_id=topic_id).limit(limit)

    def get_topics_by_user(
            self,
            user_id: UUID,
    ):
        # This will return the last 10 topics a user has messages in, based on the last message timestamp.
        user_topics = UsersTopic.objects(user_id=user_id).limit(10)
        topics_with_last_message = []
        for user_topic in user_topics:
            last_message = Message.objects(topic_id=user_topic.topic_id).limit(1).first()
            topics_with_last_message.append((user_topic, last_message))
        return topics_with_last_message

    def get_users_of_topic(
            self,
            topic_id: UUID,
    ):
        return TopicsMember.objects(topic_id=topic_id)

    def get_topic_by_id(
            self,
            topic_id: UUID,
    ):
        return Topic.objects(
            topic_id=topic_id,
        ).first()

    def delete_topic(
            self,
            topic_id: UUID,
    ):
        topic = self.get_topic_by_id(topic_id)
        topic.delete()

    def add_user_to_topic(
            self,
            topic_id: UUID,
            user_id: UUID,
    ):
        return TopicsMember.create(
            topic_id=topic_id,
            user_id=user_id,
        )


class ScyllaContactDAL(AbstractContactDAL):
    def create_contact(self, user_id: UUID, contact_id: UUID, nickname: str):
        contact = Contact.create(
            user_id=user_id,
            contact_id=contact_id,
            nickname=nickname
        )
        return contact

    def get_contacts_by_user_id(self, user_id: UUID) -> Optional[Contact]:
        return Contact.objects(user_id=user_id).all()

    @staticmethod
    def _get_contact(user_id: UUID, contact_id: UUID):
        return Contact.objects(
            user_id=user_id,
            contact_id=contact_id
        ).first()

    def update_contact(self, user_id: UUID, contact_id: UUID, new_nickname: str):
        contact = self._get_contact(user_id, contact_id)
        if contact:
            contact.update(nickname=new_nickname)
            return contact
        return None

    def delete_contact(self, user_id: UUID, contact_id: UUID):
        contact = self._get_contact(user_id, contact_id)
        if contact:
            contact.delete()
