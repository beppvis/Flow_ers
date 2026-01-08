@echo off
setlocal enabledelayedexpansion

:: Build script for single Docker container

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

echo 🐳 Building ANOKHA single container image...
echo.

:: Build the Docker image
docker build -t anokha:latest .
if %errorlevel% neq 0 (
    echo.
    echo ❌ Build failed!
    exit /b 1
)

echo.
echo ✅ Build complete!
echo.
echo To run the container:
echo   .\docker-run.bat
echo.
echo Or manually:
echo   docker run -d -p 80:80 -p 3000:3000 -p 8000:8000 --name anokha anokha:latest
echo.

endlocal
