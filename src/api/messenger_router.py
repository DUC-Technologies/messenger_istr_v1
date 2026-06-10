from uuid import UUID

from fastapi import APIRouter, Body, Depends

from auth.models import User
from auth.services.auth import get_current_user_from_token
from messenger import MessageService
from messenger import TopicService
from dependencies import get_message_service, get_topic_service
from messenger.schemas import (
    CreateMessage, ShowMessage, MessageID, UpdateMessage,
    CreateTopic, TopicID, TopicLimit, ShowTopic, ShowTopicWithLastMessage, ShowUserOfTopic, UserID, AddUserToTopic
)

messenger_router = APIRouter()


@messenger_router.post("/messages/", response_model=ShowMessage, tags=["Мessages"])
async def send_message_to_bot(
    text: str, 
    service: MessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_user_from_token)):
    return await service.send_message_to_bot(author_id=current_user, text=text)


@messenger_router.get("/messages/{topic_id}/{message_id}", response_model=ShowMessage, tags=["Мessages"])
async def get_message(
    topic_id: UUID, message_id: UUID, 
    service: MessageService = Depends(get_message_service)
    ):
    return await service.get_message_by_id(body=MessageID(topic_id=topic_id, message_id=message_id))


@messenger_router.get("/topics/{topic_id}/messages", response_model=list[ShowMessage], tags=["Мessages"])
async def get_last_user_messages_with_bot(
    limit: int = 30, 
    current_user: User = Depends(get_current_user_from_token),
    service: TopicService = Depends(get_topic_service)
    ):
    return await service.get_last_messages_of_topic(topic_id=current_user.user_id, limit=limit)


# @messenger_router.put("/messages/", response_model=ShowMessage, tags=["Мessages"])
# async def update_message(update_data: UpdateMessage = Body(...), service: MessageService = Depends(get_message_service)):
#     return await service.update_message(body=update_data)


# @messenger_router.delete("/messages/{topic_id}/{message_id}", tags=["Мessages"])
# async def delete_message(topic_id: UUID, message_id: UUID, service: MessageService = Depends(get_message_service)):
#     return await service.delete_message(body=MessageID(topic_id=topic_id, message_id=message_id))


# @messenger_router.post("/topics/", response_model=ShowTopic, tags=["Topic"])
# async def create_topic(topic_data: CreateTopic = Body(...), service: TopicService = Depends(get_topic_service)):
#     return await service.delete_topic(body=topic_data)


# @messenger_router.delete("/topics/", tags=["Topic"])
# async def delete_topic(topic_data: TopicID = Body(...), service: TopicService = Depends(get_topic_service)):
#     return await service.create_topic(body=topic_data)


# @messenger_router.post("/topics/add_user", tags=["Topic"])
# async def add_user_to_topic(body: AddUserToTopic = Body(...), service: TopicService = Depends(get_topic_service)):
#     return await service.add_user_to_topic(body=body)


# @messenger_router.get("/topics/{topic_id}/messages", response_model=list[ShowMessage], tags=["Мessages"])
# async def get_last_messages_of_topic(topic_id: UUID, limit: int = 30, service: TopicService = Depends(get_topic_service)):
#     return await service.get_last_messages_of_topic(topic_id=topic_id, limit=limit)


# @messenger_router.get("/users/{user_id}/topics", response_model=list[ShowTopicWithLastMessage], tags=["Topic"])
# async def get_topics_by_user(user_id: UUID, service: TopicService = Depends(get_topic_service)):
#     return await service.get_topics_by_user(body=UserID(user_id=user_id))


# @messenger_router.get("/topics/{topic_id}/users", response_model=list[ShowUserOfTopic], tags=["Topic"])
# async def get_users_of_topic(topic_id: UUID, service: TopicService = Depends(get_topic_service)):
#     return await service.get_users_of_topic(body=TopicID(topic_id=topic_id))
