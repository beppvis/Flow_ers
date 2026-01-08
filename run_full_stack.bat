@echo off
setlocal EnableDelayedExpansion

echo 🚀 Starting Full Stack ERPNext + MCP Agent...

REM Check if frappe_docker\.env exists
if not exist "frappe_docker\.env" (
    echo Creating frappe_docker\.env from example...
    copy "frappe_docker\example.env" "frappe_docker\.env"
)

REM Load secrets from erpnext_mcp\.env
if exist "erpnext_mcp\.env" (
    echo Loading environment variables...
    for /f "usebackq tokens=* delims=" %%A in ("erpnext_mcp\.env") do (
        REM Skip comments
        set "line=%%A"
        if "!line:~0,1!" neq "#" (
            set "%%A"
        )
    )
) else (
    echo ⚠️ Warning: erpnext_mcp\.env not found. Services might fail if keys are missing.
)

REM Navigate to frappe_docker
cd frappe_docker

REM Run compose
echo Running Docker Compose...
docker compose -f pwd.yml -f docker-compose.mcp.yml up -d --build

echo.
echo ✅ Deployment Complete!
echo ------------------------------------------------
echo ERPNext UI:     http://localhost:8080
echo MCP Agent API:  http://localhost:8001
echo React Client:   http://localhost:5173
echo ------------------------------------------------
echo Default ERPNext Creds: Administrator / admin

pause
