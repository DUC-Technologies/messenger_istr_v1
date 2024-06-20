from uuid import UUID

from fastapi import APIRouter, Body, Depends

from messenger import ContactService
from messenger import MessageService
from messenger import TopicService
from messenger.dependencies import get_message_service, get_topic_service, get_contact_service
from messenger.schemas import (
    CreateMessage, ShowMessage, MessageID, UpdateMessage,
    CreateTopic, TopicID, TopicLimit, ShowTopic, ShowTopicWithLastMessage, ShowUserOfTopic, UserID, AddUserToTopic,
    ShowContact, ContactCreate, ContactUpdate, ContactDelete
)

messenger_router = APIRouter()


@messenger_router.post("/messages/", response_model=ShowMessage, tags=["Мessages"])
def create_message(message: CreateMessage = Body(...), service: MessageService = Depends(get_message_service)):
    return service.create_message(body=message)


@messenger_router.get("/messages/{topic_id}/{message_id}", response_model=ShowMessage, tags=["Мessages"])
def get_message(topic_id: UUID, message_id: UUID, service: MessageService = Depends(get_message_service)):
    return service.get_message_by_id(body=MessageID(topic_id=topic_id, message_id=message_id))


@messenger_router.put("/messages/", response_model=ShowMessage, tags=["Мessages"])
def update_message(update_data: UpdateMessage = Body(...), service: MessageService = Depends(get_message_service)):
    return service.update_message(body=update_data)


@messenger_router.delete("/messages/{topic_id}/{message_id}", tags=["Мessages"])
def delete_message(topic_id: UUID, message_id: UUID, service: MessageService = Depends(get_message_service)):
    return service.delete_message(body=MessageID(topic_id=topic_id, message_id=message_id))


@messenger_router.post("/topics/", response_model=ShowTopic, tags=["Topic"])
def create_topic(topic_data: CreateTopic = Body(...), service: TopicService = Depends(get_topic_service)):
    return service.create_topic(body=topic_data)


@messenger_router.delete("/topics/", tags=["Topic"])
def delete_topic(topic_data: TopicID = Body(...), service: TopicService = Depends(get_topic_service)):
    return service.create_topic(body=topic_data)


@messenger_router.post("/topics/add_user", tags=["Topic"])
def add_user_to_topic(body: AddUserToTopic = Body(...), service: TopicService = Depends(get_topic_service)):
    return service.add_user_to_topic(body=body)


@messenger_router.get("/topics/{topic_id}/messages", response_model=list[ShowMessage], tags=["Мessages"])
def get_last_messages_of_topic(topic_id: UUID, limit: int = 30, service: TopicService = Depends(get_topic_service)):
    return service.get_last_messages_of_topic(body=TopicLimit(topic_id=topic_id, limit=limit))


@messenger_router.get("/users/{user_id}/topics", response_model=list[ShowTopicWithLastMessage], tags=["Topic"])
def get_topics_by_user(user_id: UUID, service: TopicService = Depends(get_topic_service)):
    return service.get_topics_by_user(body=UserID(user_id=user_id))


@messenger_router.get("/topics/{topic_id}/users", response_model=list[ShowUserOfTopic], tags=["Topic"])
def get_users_of_topic(topic_id: UUID, service: TopicService = Depends(get_topic_service)):
    return service.get_users_of_topic(body=TopicID(topic_id=topic_id))


@messenger_router.post("/contacts/", response_model=ShowContact, tags=["Contact"])
def create_contact(contact: ContactCreate, service: ContactService = Depends(get_contact_service)):
    return service.create_contact(contact)


@messenger_router.get("/contacts/{user_id}", response_model=ShowContact, tags=["Contact"])
def get_contact(user: UserID, service: ContactService = Depends(get_contact_service)):
    contact = service.get_contacts(user)
    if contact is None:
        # TODO: make a fastapi exceptions
        raise Exception
    return contact


@messenger_router.put("/contacts/{user_id}", response_model=ShowContact, tags=["Contact"])
def update_contact(contact: ContactUpdate, service: ContactService = Depends(get_contact_service)):
    updated_contact = service.update_contact(contact)
    if updated_contact is None:
        # TODO: make a fastapi exceptions
        raise Exception
    return updated_contact


@messenger_router.put("/contacts/{user_id}", tags=["Contact"])
def delete_contact(contact: ContactDelete, service: ContactService = Depends(get_contact_service)):
    service.delete_contact(contact)
