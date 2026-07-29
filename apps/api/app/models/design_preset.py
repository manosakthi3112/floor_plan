import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DesignPreset(Base):
    __tablename__ = 'design_presets'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    style: Mapped[str] = mapped_column(String(50), nullable=False)
    preset_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_built_in: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
