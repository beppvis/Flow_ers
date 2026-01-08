# ANOKHA - Logistics Tech Hackathon Project

A single Docker container setup integrating Fleetbase, Frappe, and ERPNext for logistics management solutions.

## 🏗️ Architecture

This project runs all services in a **single Docker container**:

- **Fleetbase**: Logistics platform API (Node.js) - Port 3000
- **Frappe/ERPNext**: ERP system for business management (Python) - Port 8000
- **MariaDB**: Database for Frappe/ERPNext
- **PostgreSQL**: Database for Fleetbase
- **Redis**: Caching and session management
- **Nginx**: Reverse proxy - Port 80

All services are managed by **Supervisor** within the container.

## 📋 Prerequisites

- Docker Engine 20.10+
- At least 4GB RAM available
- 10GB free disk space

## 🚀 Quick Start (Remote Judge / One Command)

From a fresh clone, a judge can run **one command**:

```bash
docker compose up --build
```

Then open:
- **ERPNext (official)**: `http://localhost:8080` (override with `ERPNEXT_HOST_PORT=8081`)
  - Username: `Administrator`
  - Password: `admin`
- **Fleetbase API**: `http://localhost:3001/health` (override with `FLEETBASE_HOST_PORT=3000`)

## Judge checklist

- Run: `docker compose up --build`
- Wait for ERPNext site creation to finish:

```bash
docker compose logs -f create-site
```

- While `create-site` is running, the ERPNext page may show `500`/`404` temporarily—**refresh after it finishes**.
- If ERPNext is up, `http://localhost:8080` loads and you can login as `Administrator/admin`.

### If you get “port is already allocated”

If `8080` or `3001` is already in use on your laptop, you can override ports in a single command:

```bash
ERPNEXT_HOST_PORT=8081 FLEETBASE_HOST_PORT=3002 docker compose up --build
```

If you previously ran the older single-container template, remove it:

```bash
docker rm -f anokha 2>/dev/null || true
```

### Option 2: Manual Docker commands (2-step)

```bash
# Build the image
docker build -t anokha:latest .

# Run the container
docker run -d \
  --name anokha \
  -p 8080:80 \
  -p 3000:3000 \
  -p 8000:8000 \
  -p 9000:9000 \
  anokha:latest
```

### Option 3: Using Docker Compose (simplified)

```bash
docker compose up -d
```

## 🌐 Access Services

After starting (wait 2-3 minutes for initialization):

- **ERPNext**: http://localhost:8000
  - Username: `Administrator`
  - Password: `admin` (default)

- **Fleetbase API**: http://localhost:3000
  - Health check: http://localhost:3000/health

- **Via Nginx**: http://localhost
  - Routes to both services

## 🔧 Configuration

### Environment Variables

You can customize the container using environment variables:

```bash
docker run -d \
  --name anokha \
  -p 80:80 -p 3000:3000 -p 8000:8000 \
  -e SITE_NAME=erpnext.localhost \
  -e ADMIN_PASSWORD=yourpassword \
  -e FRAPPE_VERSION=v14.0.0 \
  -e ERPNEXT_VERSION=v14.0.0 \
  anokha:latest
```

Available environment variables:
- `SITE_NAME`: ERPNext site name (default: `erpnext.localhost`)
- `ADMIN_PASSWORD`: ERPNext admin password (default: `admin`)
- `FRAPPE_VERSION`: Frappe version (default: `v14.0.0`)
- `ERPNEXT_VERSION`: ERPNext version (default: `v14.0.0`)

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker logs -f anokha

# Follow specific service logs
docker exec anokha tail -f /var/log/supervisor/fleetbase.log
docker exec anokha tail -f /var/log/supervisor/frappe.log
```

### Access Container Shell

```bash
docker exec -it anokha bash
```

### Check Service Status

```bash
# View supervisor status
docker exec anokha supervisorctl status

# Check individual services
docker exec anokha supervisorctl status mariadb
docker exec anokba supervisorctl status fleetbase
docker exec anokha supervisorctl status frappe
```

### Restart Services

```bash
# Restart specific service
docker exec anokha supervisorctl restart fleetbase
docker exec anokha supervisorctl restart frappe

# Restart all services
docker restart anokha
```

### Stop and Remove

```bash
# Stop container
docker stop anokha

# Remove container
docker rm anokha

# Stop and remove in one command
docker rm -f anokha
```

## 🗄️ Database Access

### MariaDB (Frappe/ERPNext)

```bash
docker exec -it anokha mysql -u frappe -pfrappe frappe
```

### PostgreSQL (Fleetbase)

```bash
docker exec -it anokha psql -U fleetbase -d fleetbase
```

### Redis

```bash
docker exec -it anokha redis-cli
```

## 📁 Project Structure

```
ANOKHA/
├── Dockerfile              # Single container Dockerfile
├── supervisord.conf        # Supervisor configuration
├── entrypoint.sh           # Container initialization script
├── docker-build.sh         # Build script
├── docker-run.sh           # Run script
├── docker-compose.yml      # Simplified compose file (optional)
├── env.template           # Environment variables template
│
├── fleetbase/             # Fleetbase application
│   ├── package.json
│   ├── server.js
│   └── healthcheck.js
│
└── nginx/                 # Nginx configuration
    ├── nginx.conf
    └── conf.d/
        └── default.conf
```

## 🔄 Updates and Maintenance

### Rebuild Container

```bash
# Stop and remove existing container
docker rm -f anokha

# Rebuild image
./docker-build.sh

# Run again
./docker-run.sh
```

### Backup Data

```bash
# Backup MariaDB
docker exec anokha mysqldump -u frappe -pfrappe frappe > backup_frappe.sql

# Backup PostgreSQL
docker exec anokha pg_dump -U fleetbase fleetbase > backup_fleetbase.sql

# Backup entire container data
docker cp anokha:/home/frappe/frappe-bench ./backup_frappe_bench
docker cp anokha:/app/fleetbase ./backup_fleetbase
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs anokha

# Check if ports are in use
lsof -i :80
lsof -i :3000
lsof -i :8000
```

### Services not responding

```bash
# Check supervisor status
docker exec anokha supervisorctl status

# Restart specific service
docker exec anokha supervisorctl restart <service-name>

# View service logs
docker exec anokha cat /var/log/supervisor/<service-name>.log
```

### Database connection issues

```bash
# Check if databases are running
docker exec anokha supervisorctl status mariadb
docker exec anokha supervisorctl status postgresql

# Test database connections
docker exec anokha mysql -u frappe -pfrappe -e "SELECT 1"
docker exec anokha psql -U fleetbase -d fleetbase -c "SELECT 1"
```

### ERPNext not initializing

The first startup can take 5-10 minutes. Check logs:

```bash
docker logs -f anokha
```

If initialization fails, you can manually initialize:

```bash
docker exec -it anokha bash
cd /home/frappe/frappe-bench
bench new-site erpnext.localhost --db-host localhost --db-port 3306
```

## 🔐 Security Notes

⚠️ **Important for Production:**

1. Change all default passwords
2. Use Docker secrets for sensitive data
3. Don't expose database ports externally
4. Enable SSL/TLS in Nginx
5. Regularly update base images
6. Use environment variables for secrets

## 📚 Additional Resources

- [Fleetbase Documentation](https://fleetbase.io/docs)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## 🆘 Support

For hackathon support, please contact your team or check the project documentation.

---

**Happy Hacking! 🚀**
