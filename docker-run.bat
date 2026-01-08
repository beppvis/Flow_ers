@echo off
setlocal enabledelayedexpansion

:: Run script for single Docker container

:: Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker daemon is not running!
    echo.
    echo Please start Docker Desktop:
    echo   1. Open Docker Desktop application
    echo   2. Wait for it to fully start ^(whale icon in system tray^)
    echo   3. Run this script again
    echo.
    echo Or start Docker Desktop from command line.
    echo.
    exit /b 1
)

set CONTAINER_NAME=anokha
set IMAGE_NAME=anokha:latest

:: Check if image exists
docker images | findstr "anokha" >nul
if %errorlevel% neq 0 (
    echo 📦 Image not found. Building...
    call docker-build.bat
)

:: Stop and remove existing container if it exists
docker ps -a | findstr "%CONTAINER_NAME%" >nul
if %errorlevel% equ 0 (
    echo 🛑 Stopping existing container...
    docker stop "%CONTAINER_NAME%" >nul 2>&1
    docker rm "%CONTAINER_NAME%" >nul 2>&1
)

echo 🚀 Starting ANOKHA container...
echo.

:: Set default environment variables if not defined
if not defined SITE_NAME set SITE_NAME=erpnext.localhost
if not defined ADMIN_PASSWORD set ADMIN_PASSWORD=admin
if not defined FRAPPE_VERSION set FRAPPE_VERSION=v14.0.0
if not defined ERPNEXT_VERSION set ERPNEXT_VERSION=v14.0.0

:: Run the container
docker run -d ^
    --name "%CONTAINER_NAME%" ^
    -p 80:80 ^
    -p 3000:3000 ^
    -p 8000:8000 ^
    -p 9000:9000 ^
    -e SITE_NAME="%SITE_NAME%" ^
    -e ADMIN_PASSWORD="%ADMIN_PASSWORD%" ^
    -e FRAPPE_VERSION="%FRAPPE_VERSION%" ^
    -e ERPNEXT_VERSION="%ERPNEXT_VERSION%" ^
    "%IMAGE_NAME%"

echo.
echo ⏳ Waiting for services to start ^(this may take 2-3 minutes^)...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Container started!
echo.
echo 📊 Container Status:
docker ps | findstr "%CONTAINER_NAME%"

echo.
echo 🌐 Access your services:
echo    - ERPNext:      http://localhost:8000
echo    - Fleetbase API: http://localhost:3000
echo    - Via Nginx:    http://localhost
echo.
echo 📋 View logs:
echo    docker logs -f %CONTAINER_NAME%
echo.
echo 🛑 Stop container:
echo    docker stop %CONTAINER_NAME%
echo.
echo 🗑️  Remove container:
echo    docker rm %CONTAINER_NAME%
echo.
echo Happy Hacking! 🎉

endlocal
