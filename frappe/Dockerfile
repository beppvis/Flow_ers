FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    wget \
    sudo \
    supervisor \
    cron \
    mariadb-client \
    redis-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install yarn
RUN npm install -g yarn

# Install bench CLI
RUN pip3 install frappe-bench

# Create frappe user
RUN useradd -m -s /bin/bash frappe \
    && echo "frappe ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Set working directory
WORKDIR /home/frappe

# Switch to frappe user
USER frappe

# Expose ports
EXPOSE 8000 9000

# Default command (will be overridden by docker-compose)
CMD ["bash"]

