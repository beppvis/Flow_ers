@echo off
setlocal EnableDelayedExpansion

echo 🚀 Starting Full Stack ERPNext + MCP Agent...

REM Check if frappe_docker exists, if not clone it
if not exist "frappe_docker" (
    echo 📦 Cloning frappe_docker repository...
    git clone https://github.com/frappe/frappe_docker.git
)

REM Navigate to frappe_docker
cd frappe_docker

REM Run compose
echo 🐳 Running Docker Compose...
docker compose -f pwd.yml -f ..\docker-compose.yml up -d --build

echo.
echo ✅ Deployment Complete!
echo ------------------------------------------------
echo ERPNext UI:     http://localhost:8080
echo MCP Agent API:  http://localhost:8001
echo React Client:   http://localhost:5173
echo ------------------------------------------------
echo Default ERPNext Creds: Administrator / admin

pause
