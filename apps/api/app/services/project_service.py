from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


async def create_project(
    db: AsyncSession,
    user_id: str,
    name: str | None = None,
    floor_plan_graph: dict | None = None,
    source_image_url: str | None = None,
) -> Project:
    project = Project(
        user_id=user_id,
        name=name or 'Untitled Project',
        floor_plan_graph=floor_plan_graph,
        source_image_url=source_image_url,
    )
    db.add(project)
    await db.flush()
    return project



async def get_project(db: AsyncSession, project_id: str, user_id: str) -> Project | None:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_projects(
    db: AsyncSession, user_id: str, page: int = 1, limit: int = 20
) -> tuple[list[Project], int]:
    total_result = await db.execute(
        select(func.count()).select_from(Project).where(Project.user_id == user_id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def update_project(
    db: AsyncSession, project_id: str, user_id: str, updates: dict
) -> Project | None:
    project = await get_project(db, project_id, user_id)
    if not project:
        return None
    for key, value in updates.items():
        if value is not None:
            setattr(project, key, value)
    await db.flush()
    return project


async def delete_project(db: AsyncSession, project_id: str, user_id: str) -> bool:
    project = await get_project(db, project_id, user_id)
    if not project:
        return False
    await db.delete(project)
    await db.flush()
    return True
