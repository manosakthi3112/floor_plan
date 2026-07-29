import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, projects, parsing, presets, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title='PlanCraft3D API', version='0.1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if os.getenv('DISABLE_RATE_LIMIT') != '1':
    from app.core.rate_limit import SimpleRateLimitMiddleware
    app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=100)


@app.get('/')
async def root():
    return {'message': 'PlanCraft3D API is running', 'docs': '/docs', 'health': '/api/v1/health'}


@app.get('/api/v1/health')
async def health():
    return {'status': 'ok'}


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(parsing.router)
app.include_router(presets.router)
app.include_router(export.router)
