from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import router



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title='PlanCraft3D Parsing Service', version='0.1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root():
    return {'message': 'PlanCraft3D Parsing Service is running', 'health': '/health'}


@app.get('/health')
async def health():
    return {'status': 'ok'}

app.include_router(router)
