from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.design_preset import DesignPreset


async def list_presets(
    db: AsyncSession,
    user_id: str | None = None,
    room_type: str | None = None,
    style: str | None = None,
    is_built_in: bool | None = None,
) -> list[DesignPreset]:
    query = select(DesignPreset)

    conditions = []
    if is_built_in is True:
        conditions.append(DesignPreset.is_built_in == True)
    elif is_built_in is False and user_id:
        conditions.append(DesignPreset.user_id == user_id)
    else:
        if user_id:
            conditions.append(or_(DesignPreset.is_built_in == True, DesignPreset.user_id == user_id))
        else:
            conditions.append(DesignPreset.is_built_in == True)

    if room_type:
        conditions.append(DesignPreset.room_type == room_type)
    if style:
        conditions.append(DesignPreset.style == style)

    if conditions:
        query = query.where(*conditions)

    query = query.order_by(DesignPreset.is_built_in.desc(), DesignPreset.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_preset(db: AsyncSession, user_id: str, name: str, room_type: str, style: str, preset_data: dict) -> DesignPreset:
    preset = DesignPreset(
        name=name,
        room_type=room_type,
        style=style,
        preset_data=preset_data,
        user_id=user_id,
        is_built_in=False,
    )
    db.add(preset)
    await db.flush()
    return preset


async def delete_preset(db: AsyncSession, preset_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(DesignPreset).where(DesignPreset.id == preset_id, DesignPreset.user_id == user_id)
    )
    preset = result.scalar_one_or_none()
    if not preset:
        return False
    await db.delete(preset)
    await db.flush()
    return True
