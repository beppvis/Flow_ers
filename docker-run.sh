#!/bin/bash

# Run script for single Docker container

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

CONTAINER_NAME="anokha"
IMAGE_NAME="anokha:latest"

# Check if image exists
if ! docker images | grep -q "anokha"; then
    echo "📦 Image not found. Building..."
    ./docker-build.sh
fi

# Stop and remove existing container if it exists
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "🛑 Stopping existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

echo "🚀 Starting ANOKHA container..."
echo ""

# Run the container
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 80:80 \
    -p 3000:3000 \
    -p 8000:8000 \
    -p 9000:9000 \
    -e SITE_NAME="${SITE_NAME:-erpnext.localhost}" \
    -e ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}" \
    -e FRAPPE_VERSION="${FRAPPE_VERSION:-v14.0.0}" \
    -e ERPNEXT_VERSION="${ERPNEXT_VERSION:-v14.0.0}" \
    "$IMAGE_NAME"

echo ""
echo "⏳ Waiting for services to start (this may take 2-3 minutes)..."
sleep 10

echo ""
echo "✅ Container started!"
echo ""
echo "📊 Container Status:"
docker ps | grep "$CONTAINER_NAME"

echo ""
echo "🌐 Access your services:"
echo "   - ERPNext:      http://localhost:8000"
echo "   - Fleetbase API: http://localhost:3000"
echo "   - Via Nginx:    http://localhost"
echo ""
echo "📋 View logs:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "🛑 Stop container:"
echo "   docker stop $CONTAINER_NAME"
echo ""
echo "🗑️  Remove container:"
echo "   docker rm $CONTAINER_NAME"
echo ""
echo "Happy Hacking! 🎉"

