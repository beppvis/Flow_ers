#!/bin/bash
set -e

echo "🚀 Starting ANOKHA Logistics Tech Stack..."

# Start database services first
echo "📦 Starting database services..."

# Start MariaDB
if [ ! -d /var/lib/mysql/mysql ]; then
    echo "Initializing MariaDB..."
    mysql_install_db --user=mysql --datadir=/var/lib/mysql
fi

# Start PostgreSQL
if [ ! -d /var/lib/postgresql/data ]; then
    echo "Initializing PostgreSQL..."
    mkdir -p /var/lib/postgresql/data
    chown -R postgres:postgres /var/lib/postgresql/data
    # Find PostgreSQL version
    PG_VERSION=$(ls /usr/lib/postgresql/ | head -n1)
    sudo -u postgres /usr/lib/postgresql/$PG_VERSION/bin/initdb -D /var/lib/postgresql/data
fi

# Wait for databases to be ready
echo "⏳ Waiting for databases to initialize..."
sleep 5

# Ensure databases exist
service mysql start || true
service postgresql start || true

sleep 3

# Setup MariaDB
mysql -e "CREATE DATABASE IF NOT EXISTS frappe;" 2>/dev/null || true
mysql -e "CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'frappe';" 2>/dev/null || true
mysql -e "GRANT ALL PRIVILEGES ON frappe.* TO 'frappe'@'localhost';" 2>/dev/null || true
mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true

# Setup PostgreSQL (wait for it to be ready)
for i in {1..30}; do
    if sudo -u postgres psql -c "SELECT 1" &>/dev/null; then
        break
    fi
    echo "Waiting for PostgreSQL... ($i/30)"
    sleep 2
done

sudo -u postgres psql -c "CREATE DATABASE fleetbase;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER fleetbase WITH PASSWORD 'fleetbase';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fleetbase TO fleetbase;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER fleetbase CREATEDB;" 2>/dev/null || true

# Initialize Frappe/ERPNext if not already done
if [ ! -f /home/frappe/frappe-bench/sites/.initialized ]; then
    echo "🔧 Initializing Frappe/ERPNext..."
    
    # Wait for MySQL to be fully ready
    for i in {1..30}; do
        if mysql -u frappe -pfrappe -e "SELECT 1" frappe &>/dev/null; then
            break
        fi
        echo "Waiting for MySQL... ($i/30)"
        sleep 2
    done
    
    cd /home/frappe
    
    # Initialize bench
    if [ ! -d frappe-bench ]; then
        bench init frappe-bench --frappe-branch ${FRAPPE_VERSION:-v14.0.0} --frappe-path https://github.com/frappe/frappe.git || true
    fi
    
    cd frappe-bench
    
    # Create site if it doesn't exist
    if [ ! -d sites/${SITE_NAME:-erpnext.localhost} ]; then
        bench new-site ${SITE_NAME:-erpnext.localhost} \
            --db-host localhost \
            --db-port 3306 \
            --db-name frappe \
            --db-user frappe \
            --db-password frappe \
            --admin-password ${ADMIN_PASSWORD:-admin} || true
        
        # Get and install ERPNext
        bench get-app erpnext --branch ${ERPNEXT_VERSION:-v14.0.0} || true
        bench --site ${SITE_NAME:-erpnext.localhost} install-app erpnext || true
    fi
    
    touch sites/.initialized
    echo "✅ Frappe/ERPNext initialized"
fi

# Start Redis
echo "🔴 Starting Redis..."
redis-server --daemonize yes || true

# Update Nginx configuration for localhost
sed -i 's/fleetbase:3000/localhost:3000/g' /etc/nginx/conf.d/default.conf
sed -i 's/frappe:8000/localhost:8000/g' /etc/nginx/conf.d/default.conf
sed -i 's/frappe_socketio:9000/localhost:9000/g' /etc/nginx/conf.d/default.conf

echo "✅ All services initialized"
echo "🌐 Services will be available at:"
echo "   - ERPNext: http://localhost:8000"
echo "   - Fleetbase: http://localhost:3000"
echo "   - Nginx: http://localhost"

# Execute the main command (supervisord)
exec "$@"

