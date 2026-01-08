FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install all system dependencies
RUN apt-get update && apt-get install -y \
    # Python and Frappe dependencies
    python3 \
    python3-pip \
    python3-dev \
    # Node.js dependencies
    curl \
    wget \
    git \
    # Database servers
    mariadb-server \
    postgresql \
    postgresql-contrib \
    # Redis server
    redis-server \
    # Web server
    nginx \
    # Process management
    supervisor \
    # Utilities
    sudo \
    cron \
    vim \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install yarn globally
RUN npm install -g yarn

# Install Frappe bench CLI
RUN pip3 install frappe-bench

# Configure MariaDB
RUN service mysql start && \
    mysql -e "CREATE DATABASE IF NOT EXISTS frappe;" && \
    mysql -e "CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'frappe';" && \
    mysql -e "GRANT ALL PRIVILEGES ON frappe.* TO 'frappe'@'localhost';" && \
    mysql -e "FLUSH PRIVILEGES;"

# Configure PostgreSQL (will be initialized in entrypoint)
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql

# Create frappe user
RUN useradd -m -s /bin/bash frappe \
    && echo "frappe ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create app directory for Fleetbase
RUN mkdir -p /app/fleetbase && \
    chown -R frappe:frappe /app

# Set working directory for Fleetbase
WORKDIR /app/fleetbase

# Copy Fleetbase files
COPY fleetbase/package*.json ./
RUN npm install --production

COPY fleetbase/ ./

# Set working directory for Frappe
WORKDIR /home/frappe

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create necessary directories
RUN mkdir -p /var/log/supervisor \
    /var/run/mysqld \
    /var/run/postgresql \
    /var/lib/redis \
    /home/frappe/frappe-bench \
    && chown -R frappe:frappe /home/frappe \
    && chown -R mysql:mysql /var/lib/mysql \
    && chown -R postgres:postgres /var/lib/postgresql

# Expose ports
EXPOSE 80 3000 8000 9000 3306 5432 6379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:3000/health && curl -f http://localhost:8000 || exit 1

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

