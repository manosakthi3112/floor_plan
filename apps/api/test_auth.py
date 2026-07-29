import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.dependencies import async_session_factory
from app.services.auth_service import register_user, login_user

async def main():
    async with async_session_factory() as db:
        print("Testing registration...")
        reg = await register_user(db, "demo@example.com", "Password123!", "Demo User")
        print("Registration Successful! Token:", reg.access_token[:25])
        
        print("Testing login...")
        log = await login_user(db, "demo@example.com", "Password123!")
        print("Login Successful! Token:", log.access_token[:25])

if __name__ == "__main__":
    asyncio.run(main())
