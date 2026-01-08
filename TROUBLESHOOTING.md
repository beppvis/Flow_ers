# Troubleshooting Guide

## Docker Daemon Not Running

### Error Message
```
ERROR: Cannot connect to the Docker daemon at unix:///Users/bettim/.docker/run/docker.sock. Is the docker daemon running?
```

### Solution

**On macOS:**

1. **Start Docker Desktop:**
   ```bash
   # Option 1: Open Docker Desktop application
   open -a Docker
   
   # Option 2: Use Spotlight
   # Press Cmd+Space, type "Docker", press Enter
   ```

2. **Wait for Docker to start:**
   - Look for the Docker whale icon in your menu bar
   - Wait until it shows "Docker Desktop is running"
   - This usually takes 30-60 seconds

3. **Verify Docker is running:**
   ```bash
   docker info
   ```
   
   If this command works without errors, Docker is running.

4. **Try building again:**
   ```bash
   ./docker-build.sh
   ```

**On Linux:**

```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Verify it's running
sudo systemctl status docker
```

**On Windows:**

1. Open Docker Desktop from Start Menu
2. Wait for it to start
3. Verify with: `docker info`

## Common Issues

### Port Already in Use

**Error:** `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution:**
```bash
# Check what's using the port
lsof -i :80
lsof -i :3000
lsof -i :8000

# Stop the process or change ports in docker-run.sh
```

### Container Won't Start

**Check logs:**
```bash
docker logs anokha
```

**Check if container exists:**
```bash
docker ps -a | grep anokha
```

**Remove and recreate:**
```bash
docker rm -f anokha
./docker-run.sh
```

### Services Not Responding

**Check supervisor status:**
```bash
docker exec anokha supervisorctl status
```

**Restart specific service:**
```bash
docker exec anokha supervisorctl restart fleetbase
docker exec anokha supervisorctl restart frappe
```

**View service logs:**
```bash
docker exec anokha tail -f /var/log/supervisor/fleetbase.log
docker exec anokha tail -f /var/log/supervisor/frappe.log
```

### Database Connection Issues

**Check if databases are running:**
```bash
docker exec anokha supervisorctl status mariadb
docker exec anokha supervisorctl status postgresql
```

**Test connections:**
```bash
# MariaDB
docker exec anokha mysql -u frappe -pfrappe -e "SELECT 1"

# PostgreSQL
docker exec anokha psql -U fleetbase -d fleetbase -c "SELECT 1"
```

### Build Fails

**Clear Docker cache:**
```bash
docker system prune -a
```

**Rebuild without cache:**
```bash
docker build --no-cache -t anokha:latest .
```

### Out of Disk Space

**Check Docker disk usage:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove unused containers, networks, images
docker system prune

# Remove all unused data (including volumes)
docker system prune -a --volumes
```

### Permission Denied Errors

**On Linux, add user to docker group:**
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

**Fix script permissions:**
```bash
chmod +x docker-build.sh docker-run.sh entrypoint.sh
```

## Getting Help

1. Check container logs: `docker logs anokha`
2. Check supervisor logs: `docker exec anokha supervisorctl status`
3. Access container shell: `docker exec -it anokha bash`
4. Review the README.md for detailed documentation


