import re
from typing import Optional
import uuid
from enum import Enum
from pydantic import BaseModel
from pydantic import EmailStr

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    
class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID

class Token(BaseModel):
    access_token: str
    token_type: str


class PortalRole(str, Enum):
    ROLE_USER = "ROLE_USER"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_SUPERADMIN = "ROLE_SUPERADMIN"
