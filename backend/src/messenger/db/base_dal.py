from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from messenger.db.scylladb_sync.models import Contact


class AbstractMessageDAL(ABC):
    """Data Access Layer for operating message info"""

    @abstractmethod
    def create_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str,
            author_id: UUID,
            has_attachment: bool,
    ):
        pass

    @abstractmethod
    def get_message_by_id(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        pass

    @abstractmethod
    def update_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str,
    ):
        pass

    @abstractmethod
    def delete_message(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        pass


class AbstractTopicDAL(ABC):
    """Data Access Layer for operating topic info"""

    @abstractmethod
    def create_topic(
            self,
            topic_id: UUID,
            title: str,
            topic_type: str,
    ):
        pass

    @abstractmethod
    def get_last_messages_of_topic(
            self,
            topic_id: UUID,
            limit: int = 30,
    ):
        pass

    @abstractmethod
    def get_topics_by_user(
            self,
            user_id: UUID,
    ):
        pass

    @abstractmethod
    def get_users_of_topic(
            self,
            topic_id: UUID,
    ):
        pass

    @abstractmethod
    def get_topic_by_id(
            self,
            topic_id: UUID,
    ):
        pass

    @abstractmethod
    def delete_topic(
            self,
            topic_id: UUID,
    ):
        pass

    @abstractmethod
    def add_user_to_topic(
            self,
            topic_id: UUID,
            user_id: UUID,
    ): pass


class AbstractContactDAL:

    @abstractmethod
    def create_contact(self, user_id: UUID, contact_id: UUID, nickname: str):
        pass

    @abstractmethod
    def get_contacts_by_user_id(self, user_id: UUID) -> Optional[Contact]:
        pass

    @abstractmethod
    def update_contact(self, user_id: UUID, contact_id: UUID, new_nickname: str):
        pass

    @abstractmethod
    def delete_contact(self, user_id: UUID, contact_id: UUID):
        pass
