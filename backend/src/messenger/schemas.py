from datetime import datetime

from pydantic import BaseModel, UUID4


class MessageID(BaseModel):
    topic_id: UUID4
    message_id: UUID4


class CreateMessage(BaseModel):
    topic_id: UUID4
    text: str
    author_id: UUID4
    has_attachment: bool = False


class UpdateMessage(MessageID):
    text: str


class ShowMessage(BaseModel):
    topic_id: UUID4
    message_id: UUID4
    text: str
    created_at: datetime
    author_id: UUID4
    has_attachment: bool

    class Config:
        from_attributes = True


class CreateTopic(BaseModel):
    title: str
    topic_type: int


class TopicID(BaseModel):
    topic_id: UUID4


class TopicLimit(BaseModel):
    topic_id: UUID4
    limit: int = 30


class UserID(BaseModel):
    user_id: UUID4


class ShowTopic(BaseModel):
    topic_id: UUID4
    title: str
    topic_type: int

    class Config:
        from_attributes = True


class ShowTopicWithLastMessage(BaseModel):
    topic: ShowTopic
    last_message: ShowMessage


class ShowUserOfTopic(BaseModel):
    user_id: UUID4
    role: int

    class Config:
        from_attributes = True


class AddUserToTopic(BaseModel):
    user_id: UUID4
    topic_id: UUID4


class ContactBase(BaseModel):
    contact_id: UUID4
    nickname: str


class ContactCreate(ContactBase):
    user_id: UUID4


class ContactUpdate(BaseModel):
    contact_id: UUID4
    nickname: str


class ContactDelete(BaseModel):
    user_id: UUID4
    contact_id: UUID4


class ShowContact(ContactBase):
    user_id: UUID4

    class Config:
        orm_mode = True
