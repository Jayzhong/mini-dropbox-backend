import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.infrastructure.database.models.base import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    folders: Mapped[List["FolderModel"]] = relationship("FolderModel", back_populates="user")
    files: Mapped[List["FileModel"]] = relationship("FileModel", back_populates="user")
    share_links: Mapped[List["ShareLinkModel"]] = relationship("ShareLinkModel", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
