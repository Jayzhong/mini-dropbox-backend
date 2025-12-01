from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base
# We will import UserModel inside the relationship or use string forward reference to avoid circular imports.

class FolderModel(Base):
    __tablename__ = "folders"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("folders.id"), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="folders")
    parent: Mapped[Optional["FolderModel"]] = relationship(
        "FolderModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["FolderModel"]] = relationship(
        "FolderModel", back_populates="parent", cascade="all, delete-orphan"
    )
    files: Mapped[List["FileModel"]] = relationship("FileModel", back_populates="folder", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "parent_id", "name", name="uq_folder_user_parent_name"),
    )


class FileModel(Base):
    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    folder_id: Mapped[UUID] = mapped_column(ForeignKey("folders.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="files")
    folder: Mapped["FolderModel"] = relationship("FolderModel", back_populates="files")
    share_links: Mapped[List["ShareLinkModel"]] = relationship("ShareLinkModel", back_populates="file", cascade="all, delete-orphan")
