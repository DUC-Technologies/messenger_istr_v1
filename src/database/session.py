from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.AUTH_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()