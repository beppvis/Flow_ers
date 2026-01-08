#!/bin/bash
set -euo pipefail

echo "🚀 Starting ANOKHA Logistics Tech Stack..."

cd /

# For judge reliability: Supervisor should own all daemons.
# This entrypoint ONLY initializes database data dirs if needed.
echo "📦 Preparing database data directories..."

mkdir -p /var/lib/mysql /var/run/mysqld
chown -R mysql:mysql /var/lib/mysql /var/run/mysqld
chmod 755 /var/run/mysqld

if [ ! -d /var/lib/mysql/mysql ]; then
  echo "Initializing MariaDB data directory..."
  mysql_install_db --user=mysql --datadir=/var/lib/mysql --auth-root-authentication-method=normal
fi

mkdir -p /var/lib/postgresql/data
chown -R postgres:postgres /var/lib/postgresql/data

if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
  echo "Initializing PostgreSQL data directory..."
  PG_VERSION="$(ls /usr/lib/postgresql/ 2>/dev/null | head -n1 || true)"
  if [ -z "$PG_VERSION" ]; then
    echo "❌ Could not detect PostgreSQL version in /usr/lib/postgresql/"
    exit 1
  fi
  sudo -u postgres "/usr/lib/postgresql/${PG_VERSION}/bin/initdb" -D /var/lib/postgresql/data
fi

# Execute the main command (supervisord)
exec "$@"

