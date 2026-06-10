import uuid
from typing import List

from sqlalchemy import String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.session import Base
from .schemas import PortalRole


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    name: Mapped[str | None] = mapped_column(String)
    surname: Mapped[str | None] = mapped_column(String)
    
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    roles: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    @property
    def is_superadmin(self) -> bool:
        return PortalRole.ROLE_SUPERADMIN in self.roles

    @property
    def is_admin(self) -> bool:
        return PortalRole.ROLE_ADMIN in self.roles

    def enrich_admin_roles_by_admin_role(self):
        if not self.is_admin:
            return {*self.roles, PortalRole.ROLE_ADMIN}

    def remove_admin_privileges_from_model(self):
        if self.is_admin:
            return {role for role in self.roles if role != PortalRole.ROLE_ADMIN}
        