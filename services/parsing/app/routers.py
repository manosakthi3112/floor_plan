from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from .orchestrator import parse_floor_plan
from .utils import image_preprocessing as preproc


router = APIRouter(prefix='/parse', tags=['parse'])


class ParseRequest(BaseModel):
    image_url: str
    project_id: str = ''


class ParseResponse(BaseModel):
    status: str
    floor_plan_graph: dict | None = None
    error: str | None = None


@router.post('', response_model=ParseResponse)
async def parse_floor_plan_endpoint(request: ParseRequest):
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(request.image_url)
            resp.raise_for_status()
            image_bytes = resp.content

        graph = await parse_floor_plan(image_bytes, request.project_id)
        return ParseResponse(status='done', floor_plan_graph=graph.model_dump())
    except Exception as e:
        return ParseResponse(status='error', error=str(e))


@router.post('/file', response_model=ParseResponse)
async def parse_file_endpoint(file: UploadFile):
    try:
        image_bytes = await file.read()
        graph = await parse_floor_plan(image_bytes)
        return ParseResponse(status='done', floor_plan_graph=graph.model_dump())
    except Exception as e:
        return ParseResponse(status='error', error=str(e))
