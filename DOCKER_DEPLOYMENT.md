# Whatfy Docker Deployment Guide

## Overview

This guide shows how to build, deploy, and manage the Whatfy platform using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Docker Hub account (for tertwer/whatfy)

## Quick Start

### 1. Clone and Build

```bash
# Navigate to project directory
cd whatsmeow_server

# Build and push to Docker Hub
./docker-build-push.sh latest

# Or build a specific version
./docker-build-push.sh v1.0.0
```

### 2. Deploy with Docker Compose

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart
```

### 3. Access the Platform

- FastAPI: http://localhost:5000
- Documentation: http://localhost:5000/docs
- WhatsApp API: http://localhost:8080

## Docker Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Nginx (Port 80)                    │
│                    (Reverse Proxy)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌───▼──────────▼─────┐ ┌──────────────┐
│ FastAPI     │ │ Go WhatsMeow       │ │ Volume Mount │
│ (Port 5000) │ │ (Port 8080)        │ │ -            │
│ - Multi-    │ │ - Multi-Session    │ │ whatsmeow_   │
│   Tenancy   │ │ - Session Pool     │ │   data       │
│ - AI Chat   │ │ - Media Storage    │ │ - Database   │
│ - Dashboard │ │ - WhatsApp API     │ │   files      │
└─────────────┘ └────────────────────┘ └──────────────┘
```

## Services

### 1. FastAPI Service

**Purpose:** Main application with multi-tenancy, AI chat, and business tools

**Environment Variables:**
```yaml
GO_SERVER_URL=http://whatfy-gowhatsmeow:8080
SMTP_HOST=smtp.zoho.in
SMTP_PORT=465
SMTP_USER=info@opendrap.website
SMTP_PASS=h0LBrxNA4u4G
FROM_EMAIL=info@opendrap.website
APP_URL=http://localhost:5000
```

**Health Check:** `/health`

### 2. Go WhatsMeow Service

**Purpose:** Multi-session WhatsApp connection pool

**Environment Variables:**
```yaml
FASTAPI_URL=http://whatfy-fastapi:5000
```

**Ports:** 8080

### 3. Nginx Service (Optional)

**Purpose:** Reverse proxy and load balancing

**Ports:** 80, 443

## Docker Commands

### Build

```bash
# Build without pushing
docker build -t tertwer/whatfy:latest .

# Build with custom version
docker build -t tertwer/whatfy:v1.0.0 .
```

### Push

```bash
# Push to Docker Hub
docker push tertwer/whatfy:latest

# Push specific version
docker push tertwer/whatfy:v1.0.0
```

### Run

```bash
# Run container
docker run -d \
  -p 5000:5000 \
  -v whatsmeow_data:/app/whatsmeow_server \
  -e GO_SERVER_URL=http://localhost:8080 \
  tertwer/whatfy:latest

# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -p 8080:8080 \
  -v whatsmeow_data:/app/whatsmeow_server \
  -e GO_SERVER_URL=http://localhost:8080 \
  -e SMTP_HOST=smtp.zoho.in \
  -e SMTP_PASS=your_password \
  tertwer/whatfy:latest
```

### Deploy

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f fastapi

# Restart service
docker compose restart fastapi

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Maintenance

```bash
# Update image
docker compose pull
docker compose up -d

# Check disk usage
docker system df

# Clean unused images
docker image prune -a

# Clean all unused resources
docker system prune -a --volumes
```

## Docker Compose Commands

### Development

```bash
# Start in detached mode
docker compose up -d

# Start with logs
docker compose up

# Rebuild after code changes
docker compose up -d --build

# View logs of specific service
docker compose logs -f fastapi

# View logs of all services
docker compose logs -f
```

### Production

```bash
# Start in detached mode
docker compose up -d

# Check service health
docker compose ps

# View logs with tail
docker compose logs --tail=100 -f

# Restart specific service
docker compose restart fastapi

# Stop services
docker compose down

# Stop and remove volumes (data loss!)
docker compose down -v
```

## Volume Management

### What Data is Stored?

- `whatsmeow_data` volume stores:
  - WhatsApp session databases (store_*.db files)
  - Media files (media/ directory)
  - Application logs

### Backup

```bash
# Create backup
docker compose exec fastapi tar czf /tmp/backup.tar.gz /app/templates /app/whatsmeow_server
docker cp whatfy-fastapi:/tmp/backup.tar.gz ./backup.tar.gz

# Restore backup
docker cp ./backup.tar.gz whatfy-fastapi:/tmp/backup.tar.gz
docker compose exec fastapi tar xzf /tmp/backup.tar.gz -C /
```

### Migration

```bash
# Stop services
docker compose down

# Backup current volume
docker run --rm -v whatsmeow_data:/data -v $(pwd):/backup alpine tar czf /backup/whatsmeow_data.tar.gz /data

# Start new version
docker compose pull
docker compose up -d

# Restore volume
docker run --rm -v whatsmeow_data:/data -v $(pwd):/backup alpine tar xzf /backup/whatsmeow_data.tar.gz -C /data
```

## Health Checks

### Check Service Status

```bash
# Check FastAPI health
curl http://localhost:5000/health

# Check Nginx status
curl http://localhost/

# Check Go service
curl http://localhost:8080/check
```

### Monitor Resources

```bash
# Check container stats
docker stats

# Check memory usage
docker stats whatfy-fastapi --no-stream

# Check CPU usage
docker stats whatfy-gowhatsmeow --no-stream
```

## Network Troubleshooting

### Connection Issues

```bash
# Check network
docker network ls
docker network inspect whatfy-whatfy-network

# Check service connectivity
docker compose exec fastapi ping whatfy-gowhatsmeow
docker compose exec whatfy-gowhatsmeow ping whatfy-fastapi
```

### Port Conflicts

```bash
# Find process using port
netstat -tulpn | grep 5000
lsof -i :5000

# Stop conflicting service
docker compose down

# Start with different port
docker run -p 5010:5000 -v whatsmeow_data:/app/whatsmeow_server tertwer/whatfy:latest
```

## Security

### Environment Variables

- Always use environment variables for sensitive data
- Never hardcode passwords in Dockerfiles
- Use Docker secrets for production

### Best Practices

1. **Secret Management:**
   ```bash
   docker run -d \
     -e SMTP_PASS_FILE=/run/secrets/smtp_pass \
     --secret smtp_pass \
     tertwer/whatfy:latest
   ```

2. **Network Security:**
   - Use internal Docker networks only
   - Expose only necessary ports
   - Use Nginx with SSL/TLS

3. **Image Updates:**
   - Always pull latest image before starting
   - Test updates in staging first
   - Monitor logs after update

## Deployment Checklist

### Before Production Deployment

- [ ] Update environment variables
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Test health checks
- [ ] Review resource limits
- [ ] Update firewall rules
- [ ] Test rollback procedure

## Monitoring

### Logs

```bash
# Real-time logs
docker compose logs -f

# Logs with timestamps
docker compose logs -f --timestamps

# Last 100 lines
docker compose logs --tail=100

# Logs of specific service
docker compose logs -f fastapi
docker compose logs -f whatfy-gowhatsmeow
```

### Metrics

```bash
# Container stats
docker stats

# CPU and memory usage
docker stats --no-stream
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs fastapi

# Check exit code
docker inspect whatfy-fastapi | grep -A 5 State

# Remove and recreate
docker compose down
docker compose up -d
```

### Database Issues

```bash
# Check database size
docker exec whatfy-gowhatsmeow ls -lh whatsmeow_server/*.db

# Backup database
docker exec whatfy-gowhatsmeow cp whatsmeow_server/store_*.db whatsmeow_server/backup.db

# Restart Go service
docker compose restart whatfy-gowhatsmeow
```

### Volume Issues

```bash
# Check volume
docker volume ls | grep whatsmeow
docker volume inspect whatsmeow_data

# Remove volume (data loss!)
docker volume rm whatsmeow_data
```

## Performance Tuning

### Resource Limits

Update `docker-compose.yml`:

```yaml
services:
  whatfy-fastapi:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  whatfy-gowhatsmeow:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Database Optimization

```bash
# Backup before optimization
docker exec whatfy-gowhatsmeow tar czf /tmp/backup.tar.gz whatsmeow_server/

# Optimize database
docker exec whatfy-gowhatsmeow sqlite3 whatsmeow_server/store_*.db "VACUUM;"

# Check database size
docker exec whatfy-gowhatsmeow ls -lh whatsmeow_server/*.db
```

## Support

For issues and questions:
- Check logs: `docker compose logs -f`
- Review documentation in this repo
- Check Docker Hub: https://hub.docker.com/r/tertwer/whatfy

## License

MIT License - See LICENSE file for details.