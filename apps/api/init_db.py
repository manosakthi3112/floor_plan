import asyncio
import os
import sys

# Add apps/api to sys.path
api_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, api_dir)

from app.dependencies import engine
from app.models.base import Base
# Import all models so metadata is populated
from app.models import user, project, job, design_preset

async def main():
    print("Connecting to database and creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully!")

if __name__ == '__main__':
    asyncio.run(main())
