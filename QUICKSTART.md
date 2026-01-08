# 🚀 Quick Start Guide (Remote Judge)

## One-Command Setup

```bash
docker compose up --build
```

## Access Your Services

After starting, wait for the `create-site` container to finish (this can take a few minutes):

- **ERPNext**: http://localhost:8080 (or set `ERPNEXT_HOST_PORT=8081`)
  - Username: `Administrator`
  - Password: `admin`

- **Fleetbase API**: http://localhost:3001 (or set `FLEETBASE_HOST_PORT=3000`)
  - Health: http://localhost:3001/health

## Common Commands

```bash
# Follow ERPNext site creation logs
docker compose logs -f create-site

# View everything
docker compose logs -f

# Stop
docker compose down
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
