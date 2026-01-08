#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")"

echo "🚀 Starting Full Stack ERPNext + MCP Agent..."

# creating .env file for frappe_docker if not exists
if [ ! -f frappe_docker/.env ]; then
    echo "Creating frappe_docker/.env from example..."
    cp frappe_docker/example.env frappe_docker/.env
fi

# Load secrets from erpnext_mcp/.env to export them for compose
if [ -f erpnext_mcp/.env ]; then
    export $(cat erpnext_mcp/.env | grep -v '^#' | xargs)
else
    echo "⚠️ Warning: erpnext_mcp/.env not found. Services might fail if keys are missing."
fi

# Navigate to frappe_docker to run compose with correct context for its relative paths
cd frappe_docker

# Run compose merging the standard pwd.yml with our custom mcp extension
docker compose -f pwd.yml -f docker-compose.mcp.yml up -d --build

echo "✅ Deployment Complete!"
echo "------------------------------------------------"
echo "ERPNext UI:     http://localhost:8080"
echo "MCP Agent API:  http://localhost:8001"
echo "React Client:   http://localhost:5173"
echo "------------------------------------------------"
echo "Default ERPNext Creds: Administrator / admin"
