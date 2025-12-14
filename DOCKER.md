# Docker Deployment Guide

This guide provides detailed information about running the Home Network Monitor in Docker containers.

## Overview

The application consists of two Docker containers:
- **Backend**: Python FastAPI application that pings hosts and stores data
- **Frontend**: React application served by nginx

Both containers are orchestrated using Docker Compose.

## Architecture

```
┌─────────────────────────────────────────┐
│           Host Machine                   │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Docker Network (bridge)        │ │
│  │                                    │ │
│  │  ┌──────────────┐  ┌────────────┐ │ │
│  │  │   Frontend   │  │   Backend  │ │ │
│  │  │   (nginx)    │─▶│  (FastAPI) │ │ │
│  │  │   Port 80    │  │  Port 8000 │ │ │
│  │  └──────────────┘  └────────────┘ │ │
│  │         │                 │        │ │
│  └─────────┼─────────────────┼────────┘ │
│            │                 │          │
│            │                 ▼          │
│            │          ┌────────────┐    │
│            │          │  SQLite DB │    │
│            │          │ ./data/    │    │
│            │          └────────────┘    │
│            ▼                            │
│     User's Browser                      │
└─────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd home-network-monitor

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Configuration

### Environment Variables

Configure the application by editing `docker-compose.yml` or creating a `.env` file:

```yaml
environment:
  # Ping Configuration
  - PING_INTERVAL=60         # Seconds between pings
  - PING_TIMEOUT=5           # Ping timeout in seconds
  - PING_RETRIES=2           # Number of retry attempts

  # Data Retention
  - RETENTION_DAYS=120       # Days to keep data
  - CLEANUP_HOUR=2           # Hour to run cleanup (0-23)

  # Monitored Hosts
  - MONITORED_HOSTS=router.local,8.8.8.8,1.1.1.1,192.168.1.1

  # CORS (if accessing from different domain)
  - CORS_ORIGINS=http://localhost,http://localhost:80
```

### Volume Mounts

The database is persisted using a Docker volume:

```yaml
volumes:
  - ./data:/app/data  # Database stored on host machine
```

This ensures data persists across container restarts and rebuilds.

## Docker Commands

### Starting and Stopping

```bash
# Start all services in detached mode
docker-compose up -d

# Start with specific compose file
docker-compose -f docker-compose.yml up -d

# Stop all services
docker-compose down

# Stop and remove volumes (deletes database!)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# View last 100 lines
docker-compose logs --tail=100

# Logs with timestamps
docker-compose logs -f -t
```

### Managing Services

```bash
# Restart services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop services without removing containers
docker-compose stop

# Start stopped services
docker-compose start

# View service status
docker-compose ps

# View resource usage
docker stats
```

### Rebuilding

```bash
# Rebuild and restart (after code changes)
docker-compose up -d --build

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Rebuild without cache
docker-compose build --no-cache

# Pull latest base images and rebuild
docker-compose pull
docker-compose up -d --build
```

### Inspecting Containers

```bash
# Execute command in running container
docker-compose exec backend bash
docker-compose exec backend python -c "print('Hello')"

# View container details
docker inspect network-monitor-backend

# View container logs directly
docker logs network-monitor-backend

# View processes in container
docker-compose top backend
```

## Data Management

### Backup Database

```bash
# Stop backend to ensure clean backup
docker-compose stop backend

# Backup database
cp ./data/pings.db ./data/pings.db.backup-$(date +%Y%m%d)

# Or create tar archive
tar -czf network-monitor-backup-$(date +%Y%m%d).tar.gz ./data/

# Restart backend
docker-compose start backend
```

### Restore Database

```bash
# Stop backend
docker-compose stop backend

# Restore database
cp ./data/pings.db.backup ./data/pings.db

# Or extract from tar
tar -xzf network-monitor-backup-20240101.tar.gz

# Restart backend
docker-compose start backend
```

### Clear All Data

```bash
# Stop and remove containers and volumes
docker-compose down -v

# Remove data directory
rm -rf ./data

# Start fresh
docker-compose up -d
```

## Network Configuration

### Accessing Local Network Hosts

If you need to ping devices on your local network:

**Option 1: Bridge Network (Default)**
Works for most cases. The container can reach hosts on your LAN.

**Option 2: Host Network**
If bridge network doesn't work, use host networking:

```yaml
# In docker-compose.yml, add under backend service:
network_mode: "host"
```

Note: With host networking, you can't use container port mapping.

### Custom Network

Create a custom network for better isolation:

```yaml
networks:
  monitor-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

## Production Deployment

### Docker Compose Production

```yaml
version: '3.8'

services:
  backend:
    image: your-registry/network-monitor-backend:latest
    restart: always
    environment:
      - MONITORED_HOSTS=${MONITORED_HOSTS}
    volumes:
      - /var/lib/network-monitor/data:/app/data
    networks:
      - monitor-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: your-registry/network-monitor-frontend:latest
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - monitor-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  monitor-net:
    driver: bridge
```

### Security Hardening

```bash
# Run as non-root user
# Add to Dockerfile:
USER nobody

# Limit resources
# Add to docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M

# Read-only root filesystem (where possible)
read_only: true
tmpfs:
  - /tmp

# Drop unnecessary capabilities
cap_drop:
  - ALL
cap_add:
  - NET_RAW  # Only needed for ICMP ping
```

### Reverse Proxy with HTTPS

Using Traefik:

```yaml
services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/traefik.yml
      - ./acme.json:/acme.json

  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.monitor.rule=Host(`monitor.example.com`)"
      - "traefik.http.routers.monitor.tls=true"
      - "traefik.http.routers.monitor.tls.certresolver=letsencrypt"
```

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Backend health
curl http://localhost:8000/health

# Check from within container
docker-compose exec backend curl http://localhost:8000/health
```

### Docker Health Status

```bash
# View health status
docker-compose ps

# Inspect health check logs
docker inspect network-monitor-backend | jq '.[0].State.Health'
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Container-specific stats
docker stats network-monitor-backend network-monitor-frontend

# Export metrics (for Prometheus, etc.)
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Troubleshooting

### Container Won't Start

```bash
# View detailed error
docker-compose logs backend

# Check if port is in use
sudo netstat -tulpn | grep :8000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
chmod 755 ./data

# Run container as specific user
# Add to docker-compose.yml:
user: "${UID}:${GID}"
```

### Network Issues

```bash
# Test connectivity between containers
docker-compose exec frontend ping backend
docker-compose exec backend ping frontend

# Test external connectivity
docker-compose exec backend ping 8.8.8.8

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

### Debug Mode

```bash
# Run container in foreground with full logs
docker-compose up backend

# Override entrypoint for debugging
docker-compose run --entrypoint /bin/bash backend

# View all environment variables
docker-compose exec backend env
```

## Advanced Usage

### Multi-Stage Builds

The Dockerfiles use multi-stage builds for smaller images:

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### Docker BuildKit

Enable BuildKit for faster builds:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with BuildKit
docker-compose build

# Use BuildKit cache
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '1.0'
          memory: 512M
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: docker-compose build

      - name: Push to registry
        run: |
          docker tag backend your-registry/backend:latest
          docker push your-registry/backend:latest
```

## Support

For issues specific to Docker deployment, check:
1. Container logs: `docker-compose logs`
2. Health status: `docker-compose ps`
3. Resource usage: `docker stats`
4. Network connectivity: `docker network inspect home-network-monitor_network-monitor`
