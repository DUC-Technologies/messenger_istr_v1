from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from messenger.db import SQLAlchemyMessageDAL, SQLAlchemyTopicDAL
from messenger.services import MessageService, TopicService


def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    message_dal = SQLAlchemyMessageDAL(db_session=db)
    topic_dal = SQLAlchemyTopicDAL(db_session=db)
    return MessageService(message_dal=message_dal, topic_dal=topic_dal)


def get_topic_service(db: AsyncSession = Depends(get_db)) -> TopicService:
    dal = SQLAlchemyTopicDAL(db_session=db)
    return TopicService(dal=dal)

