from abc import ABCMeta, abstractmethod
from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import PortalRole
from .models import User


class AbstractUserDAL(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, db_session):
        pass

    @abstractmethod
    async def create_user(self, email, hashed_password, roles):
        pass

    @abstractmethod
    async def delete_user(self, user_id):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id):
        pass

    @abstractmethod
    async def get_user_by_email(self, email):
        pass

    @abstractmethod
    async def update_user(self, user_id, kwargs):
        pass


class SQLAlchemyUserDAL(AbstractUserDAL):
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self,
            email: str,
            hashed_password: str,
            roles: list[PortalRole],
    ) -> User:
        new_user = User(
            username=email,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        return res.scalars().first()

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        return res.scalars().first()

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        if "email" in kwargs:
            kwargs["username"] = kwargs["email"]

        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()
    