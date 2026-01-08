# Building and Publishing Docker Images

This guide shows how to build and publish your Docker images to a container registry.

## Option 1: Build Images Locally

Build the images without publishing:

```bash
# Build MCP Backend
docker build -t flowers-mcp-backend:latest ./erpnext_mcp

# Build Client
docker build -t flowers-client:latest ./client
```

## Option 2: Publish to Docker Hub

### Prerequisites
1. Create account at https://hub.docker.com
2. Login: `docker login`

### Build and Push

```bash
# Replace 'yourusername' with your Docker Hub username

# Build and tag MCP Backend
docker build -t yourusername/flowers-mcp-backend:latest ./erpnext_mcp
docker push yourusername/flowers-mcp-backend:latest

# Build and tag Client
docker build -t yourusername/flowers-client:latest ./client
docker push yourusername/flowers-client:latest
```

### Update docker-compose.yml

Replace the `build:` sections with `image:`:

```yaml
  erpnext-mcp-backend:
    image: yourusername/flowers-mcp-backend:latest
    # Remove the 'build:' section
    
  erpnext-mcp-client:
    image: yourusername/flowers-client:latest
    # Remove the 'build:' section
```

## Option 3: GitHub Container Registry (ghcr.io)

### Prerequisites
1. Create GitHub Personal Access Token with `write:packages` permission
2. Login: `echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin`

### Build and Push

```bash
# Replace 'yourusername' with your GitHub username

docker build -t ghcr.io/yourusername/flowers-mcp-backend:latest ./erpnext_mcp
docker push ghcr.io/yourusername/flowers-mcp-backend:latest

docker build -t ghcr.io/yourusername/flowers-client:latest ./client
docker push ghcr.io/yourusername/flowers-client:latest
```

## Automated Build Script

Create `build-and-push.sh`:

```bash
#!/bin/bash
REGISTRY="yourusername"  # or ghcr.io/yourusername
VERSION="latest"

# Build
docker build -t $REGISTRY/flowers-mcp-backend:$VERSION ./erpnext_mcp
docker build -t $REGISTRY/flowers-client:$VERSION ./client

# Push
docker push $REGISTRY/flowers-mcp-backend:$VERSION
docker push $REGISTRY/flowers-client:$VERSION

echo "✅ Images published!"
```

Make executable: `chmod +x build-and-push.sh`

## For End Users

Once published, users can simply:
```bash
docker compose pull  # Download pre-built images
docker compose up -d  # Start without building
```
