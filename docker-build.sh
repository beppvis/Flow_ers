#!/bin/bash

# Build script for single Docker container

set -e

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running!"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  1. Open Docker Desktop application"
    echo "  2. Wait for it to fully start (whale icon in menu bar)"
    echo "  3. Run this script again"
    echo ""
    echo "Or start Docker Desktop from command line:"
    echo "  open -a Docker"
    echo ""
    exit 1
fi

echo "🐳 Building ANOKHA single container image..."
echo ""

# Build the Docker image
docker build -t anokha:latest .

echo ""
echo "✅ Build complete!"
echo ""
echo "To run the container:"
echo "  ./docker-run.sh"
echo ""
echo "Or manually:"
echo "  docker run -d -p 80:80 -p 3000:3000 -p 8000:8000 --name anokha anokha:latest"

