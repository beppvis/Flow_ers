# 🚀 Quick Start Guide - Single Container

## One-Command Setup

```bash
# Build and run
./docker-build.sh && ./docker-run.sh

# Or using Docker Compose
docker-compose up -d
```

## Access Your Services

After starting, wait 2-3 minutes for initialization:

- **ERPNext**: http://localhost:8000
  - Username: `Administrator`
  - Password: `admin`

- **Fleetbase API**: http://localhost:3000
  - Health: http://localhost:3000/health

- **Via Nginx**: http://localhost

## Common Commands

```bash
# View all logs
docker logs -f anokha

# Check service status
docker exec anokha supervisorctl status

# Restart a service
docker exec anokha supervisorctl restart fleetbase

# Access container shell
docker exec -it anokha bash

# Stop container
docker stop anokha

# Start container
docker start anokha
```

## Troubleshooting

### Services not starting?
```bash
# Check logs
docker logs anokha

# Check supervisor status
docker exec anokha supervisorctl status
```

### Port conflicts?
```bash
# Check what's using ports
lsof -i :80
lsof -i :3000
lsof -i :8000
```

### Need to reset?
```bash
# Remove container and start fresh
docker rm -f anokha
./docker-run.sh
```

---

**Happy Coding! 🎉**
