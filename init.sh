#!/bin/bash
set -euo pipefail

SENTINEL="/home/frappe/frappe-bench/sites/.initialized"
BENCH_DIR="/home/frappe/frappe-bench"
SITE_NAME="${SITE_NAME:-erpnext.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
FRAPPE_VERSION="${FRAPPE_VERSION:-v14.0.0}"
ERPNEXT_VERSION="${ERPNEXT_VERSION:-v14.0.0}"

echo "🧩 init.sh: one-time initialization (databases + Frappe/ERPNext)"

if [ -f "$SENTINEL" ]; then
  echo "✅ init.sh: already initialized ($SENTINEL exists)"
  exit 0
fi

echo "⏳ Waiting for MariaDB..."
for i in {1..120}; do
  if mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if ! mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
  echo "❌ MariaDB did not become ready in time"
  exit 1
fi

echo "⏳ Waiting for PostgreSQL..."
for i in {1..120}; do
  if sudo -u postgres psql -c "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if ! sudo -u postgres psql -c "SELECT 1" >/dev/null 2>&1; then
  echo "❌ PostgreSQL did not become ready in time"
  exit 1
fi

echo "🗄️  Creating MariaDB database/user for Frappe..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS frappe;" 2>/dev/null || true
mysql -u root -e "CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'frappe';" 2>/dev/null || true
mysql -u root -e "GRANT ALL PRIVILEGES ON frappe.* TO 'frappe'@'localhost';" 2>/dev/null || true
mysql -u root -e "FLUSH PRIVILEGES;" 2>/dev/null || true

echo "🗄️  Creating PostgreSQL database/user for Fleetbase..."
sudo -u postgres psql -c "CREATE DATABASE fleetbase;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER fleetbase WITH PASSWORD 'fleetbase';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fleetbase TO fleetbase;" 2>/dev/null || true

is_valid_bench () {
  # Bench is "valid enough" if it has apps + sites.
  [ -d "${BENCH_DIR}/apps" ] && [ -d "${BENCH_DIR}/sites" ] && [ -f "${BENCH_DIR}/Procfile" ]
}

echo "🧱 Initializing Frappe bench (this can take several minutes on first run)..."
mkdir -p /home/frappe
chown -R frappe:frappe /home/frappe

# If a volume or prior run created the directory but it's not a bench, wipe contents so init can proceed.
if [ -d "${BENCH_DIR}" ] && ! is_valid_bench; then
  echo "⚠️  ${BENCH_DIR} exists but is not a bench. Clearing contents..."
  rm -rf "${BENCH_DIR:?}/"*
fi

if ! is_valid_bench; then
  # bench init requires the target directory to NOT exist; ensure it's removed (works even without a volume).
  if [ -d "${BENCH_DIR}" ] && [ -z "$(ls -A "${BENCH_DIR}" 2>/dev/null || true)" ]; then
    rmdir "${BENCH_DIR}" 2>/dev/null || true
  fi
  sudo -H -u frappe bash -lc "cd /home/frappe && bench init frappe-bench --frappe-branch ${FRAPPE_VERSION} --frappe-path https://github.com/frappe/frappe.git"
fi

echo "🧩 Installing ERPNext app (if missing)..."
sudo -H -u frappe bash -lc "cd ${BENCH_DIR} && if [ ! -d apps/erpnext ]; then bench get-app erpnext --branch ${ERPNEXT_VERSION}; fi"

echo "🌐 Creating site (${SITE_NAME}) if needed..."
sudo -H -u frappe bash -lc "cd ${BENCH_DIR} && if [ ! -d sites/${SITE_NAME} ]; then bench new-site ${SITE_NAME} --mariadb-root-username root --admin-password ${ADMIN_PASSWORD} --db-name frappe --db-user frappe --db-password frappe; fi"

echo "📦 Installing ERPNext on site..."
sudo -H -u frappe bash -lc "cd ${BENCH_DIR} && bench --site ${SITE_NAME} install-app erpnext"

touch "$SENTINEL"
chown frappe:frappe "$SENTINEL"

echo "✅ init.sh: initialization complete"

