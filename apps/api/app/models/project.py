from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


class Project(Base, TimestampMixin):
    __tablename__ = 'projects'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default='Untitled Project')
    floor_plan_graph: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    room_styles: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    width_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
