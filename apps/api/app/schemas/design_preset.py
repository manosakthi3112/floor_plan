from datetime import datetime

from pydantic import BaseModel


class DesignPresetCreate(BaseModel):
    name: str
    room_type: str
    style: str
    preset_data: dict


class DesignPresetResponse(BaseModel):
    id: str
    name: str
    room_type: str
    style: str
    preset_data: dict
    is_built_in: bool
    user_id: str | None = None
    created_at: datetime

    model_config = {'from_attributes': True}


class DesignPresetListResponse(BaseModel):
    presets: list[DesignPresetResponse]
