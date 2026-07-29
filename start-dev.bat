@echo off
echo Ensuring PostgreSQL and Redis are running in Docker...
docker compose start postgres redis >nul 2>&1
if %errorlevel% neq 0 (
    docker compose up -d postgres redis
)

echo.
echo Starting Web Frontend...
start "PlanCraft3D Web (Port 3000)" cmd /k "pnpm --filter @plancraft3d/web dev"

echo Starting API Backend...
start "PlanCraft3D API (Port 8001)" cmd /k "cd apps\api && python -m uvicorn app.main:app --reload --port 8001"

echo Starting Parsing Service...
start "PlanCraft3D Parsing (Port 8002)" cmd /k "cd services\parsing && python -m uvicorn app.main:app --reload --port 8002"

echo.
echo All services launched!
echo Web: http://localhost:3000
echo API: http://localhost:8001
echo Parsing: http://localhost:8002
