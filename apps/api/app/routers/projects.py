from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import project_service
from app.core.exceptions import NotFoundError

router = APIRouter(prefix='/api/v1/projects', tags=['projects'])


@router.get('', response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    projects, total = await project_service.list_projects(db, user.id, page, limit)
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
    )


@router.post('', response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.create_project(
        db,
        user.id,
        body.name,
        floor_plan_graph=body.floor_plan_graph,
        source_image_url=body.source_image_url,
    )
    return ProjectResponse.model_validate(project)



@router.get('/{project_id}', response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, user.id)
    if not project:
        raise NotFoundError('Project not found')
    return ProjectResponse.model_validate(project)


@router.put('/{project_id}', response_model=ProjectResponse)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updates = body.model_dump(exclude_none=True)
    project = await project_service.update_project(db, project_id, user.id, updates)
    if not project:
        raise NotFoundError('Project not found')
    return ProjectResponse.model_validate(project)


@router.delete('/{project_id}', status_code=204)
async def delete_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await project_service.delete_project(db, project_id, user.id)
    if not deleted:
        raise NotFoundError('Project not found')
