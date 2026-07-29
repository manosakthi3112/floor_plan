from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.design_preset import (
    DesignPresetCreate,
    DesignPresetListResponse,
    DesignPresetResponse,
)
from app.services import preset_library
from app.core.exceptions import NotFoundError

router = APIRouter(prefix='/api/v1/presets', tags=['presets'])


@router.get('', response_model=DesignPresetListResponse)
async def list_presets(
    room_type: str | None = Query(None),
    style: str | None = Query(None),
    is_built_in: bool | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    presets = await preset_library.list_presets(
        db, user_id=user.id, room_type=room_type, style=style, is_built_in=is_built_in
    )
    return DesignPresetListResponse(
        presets=[DesignPresetResponse.model_validate(p) for p in presets]
    )


@router.post('', response_model=DesignPresetResponse, status_code=201)
async def create_preset(
    body: DesignPresetCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    preset = await preset_library.create_preset(
        db, user.id, body.name, body.room_type, body.style, body.preset_data
    )
    return DesignPresetResponse.model_validate(preset)


@router.delete('/{preset_id}', status_code=204)
async def delete_preset(
    preset_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await preset_library.delete_preset(db, preset_id, user.id)
    if not deleted:
        raise NotFoundError('Preset not found')
