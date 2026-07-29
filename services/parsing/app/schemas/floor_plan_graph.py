from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class CamelModel(BaseModel):
    """Base model that serialises to camelCase for the TypeScript frontend."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Point(BaseModel):
    x: float
    y: float


class WallSegment(CamelModel):
    id: str
    start: dict  # {x, y}
    end: dict    # {x, y}
    thickness: float = 10.0
    height: float = 270.0
    type: str = 'interior'


class RoomOutput(CamelModel):
    id: str
    label: str = ''
    polygon: list[dict]  # [{x, y}, ...]
    level: int = 0
    area: float = 0.0


class OpeningOutput(CamelModel):
    id: str
    type: str  # 'door' | 'window'
    wall_id: str
    position: float
    width: float
    height: float = 210.0
    sill_height: float = 0.0


class FloorPlanGraph(BaseModel):
    version: int = 1
    unit: str = 'mm'
    walls: list[dict]
    rooms: list[dict]
    openings: list[dict]
    confidence: float = 1.0
    metadata: dict = {}
