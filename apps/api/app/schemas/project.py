from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str | None = None
    floor_plan_graph: dict | None = None
    source_image_url: str | None = None



class ProjectUpdate(BaseModel):
    name: str | None = None
    floor_plan_graph: dict | None = None
    room_styles: dict | None = None
    thumbnail_url: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    floor_plan_graph: dict | None = None
    room_styles: dict | None = None
    thumbnail_url: str | None = None
    source_image_url: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
