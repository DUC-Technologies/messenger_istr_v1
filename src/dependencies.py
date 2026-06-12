import aioboto3
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from infra.s3_storage import S3StorageService
from messenger.db.sqlalchemy.dal import SQLAlchemyMessageDAL, SQLAlchemyTopicDAL
from messenger.services.message_service import MessageService
from messenger.services.topic_service import TopicService


def get_s3_service() -> S3StorageService:
    session = aioboto3.Session()
    return S3StorageService(session=session)


def get_message_service(
    db: AsyncSession = Depends(get_db),
    s3_service: S3StorageService = Depends(get_s3_service),
) -> MessageService:
    message_dal = SQLAlchemyMessageDAL(db_session=db)
    topic_dal = SQLAlchemyTopicDAL(db_session=db)
    return MessageService(message_dal=message_dal, topic_dal=topic_dal, s3_service=s3_service)


def get_topic_service(db: AsyncSession = Depends(get_db)) -> TopicService:
    dal = SQLAlchemyTopicDAL(db_session=db)
    return TopicService(dal=dal)