from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractMessageDAL(ABC):
    """Data Access Layer for operating message info"""
    
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @abstractmethod
    async def create_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str,
            author_id: UUID,
            buttons: list[list[dict[str, Any]]] | None = None,
            # has_attachment: bool,
    ):
        pass

    @abstractmethod
    async def get_message_by_id(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        pass

    @abstractmethod
    async def update_message(
            self,
            topic_id: UUID,
            message_id: UUID,
            text: str,
    ):
        pass

    @abstractmethod
    async def delete_message(
            self,
            topic_id: UUID,
            message_id: UUID,
    ):
        pass


class AbstractTopicDAL(ABC):
    """Data Access Layer for operating topic info"""

    @abstractmethod
    async def create_topic(
            self,
            topic_id: UUID,
            title: str,
            topic_type: str|None = None,
    ):
        pass

    @abstractmethod
    async def get_last_messages_of_topic(
            self,
            topic_id: UUID,
            limit: int = 30,
    ):
        pass

    @abstractmethod
    async def get_topics_by_user(
            self,
            user_id: UUID,
    ):
        pass

    # @abstractmethod
    # async def get_users_of_topic(
    #         self,
    #         topic_id: UUID,
    # ):
    #     pass

    # @abstractmethod
    # async def get_topic_by_id(
    #         self,
    #         topic_id: UUID,
    # ):
    #     pass

    # @abstractmethod
    # async def delete_topic(
    #         self,
    #         topic_id: UUID,
    # ):
    #     pass

    # @abstractmethod
    # async def add_user_to_topic(
    #         self,
    #         topic_id: UUID,
    #         user_id: UUID,
    # ): pass
