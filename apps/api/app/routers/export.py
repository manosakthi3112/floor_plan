from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.core.exceptions import NotFoundError

router = APIRouter(prefix='/api/v1/projects', tags=['export'])


@router.post('/{project_id}/export')
async def queue_export(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.project import Project
    from sqlalchemy import select

    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError('Project not found')

    return {
        'job_id': 'pending',
        'status': 'queued',
        'message': 'Export queued. Check job status for download URL.',
    }


@router.post('/{project_id}/render')
async def render_thumbnail(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {'image_url': '', 'status': 'pending'}
