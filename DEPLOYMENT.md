# Deployment Guide

This guide covers deployment options for the Data Quality Validation Framework backend.

## Table of Contents

- [Development Deployment](#development-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)

## Development Deployment

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with local settings

# Start PostgreSQL and Redis
# (Ensure they are running on your system)

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Quick Start

```bash
cd backend

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

The API will be available at: http://localhost:8000

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Remove all data (volumes)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# View logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api bash

# Run database migrations
docker-compose exec api alembic upgrade head
```

### Custom Configuration

Edit `docker-compose.yml` to customize:
- Port numbers
- Database credentials
- Environment variables
- Volume mounts

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose
- Domain name (optional but recommended)
- SSL/TLS certificate

### Recommended Architecture

```
                  ┌─────────────────┐
                  │  Reverse Proxy  │
                  │   (Nginx/HAProxy)│
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
        ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
        │  API   │    │  API   │    │  API   │
        │Instance│    │Instance│    │Instance│
        └───┬────┘    └───┬────┘    └───┬────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
        ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
        │PostgreSQL    │ Redis   │    │ Storage│
        │Cluster │    │Cluster  │    │        │
        └────────┘    └─────────┘    └────────┘
```

### Production Setup

1. **Create directory structure:**
```bash
mkdir -p /opt/data-quality-api
cd /opt/data-quality-api
```

2. **Clone repository:**
```bash
git clone <repository-url> .
cd backend
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env
# Update with production settings
```

4. **Secure configuration:**
```bash
chmod 600 .env
# Generate strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. **Update docker-compose.yml:**
```yaml
services:
  api:
    # ... other config ...
    environment:
      DEBUG: "False"  # Disable debug mode
      LOG_LEVEL: WARNING
      WORKERS: 4
    deploy:
      replicas: 3  # Multiple instances
      restart_policy:
        condition: on-failure
        delay: 5s
```

6. **Start services:**
```bash
docker-compose -f docker-compose.yml up -d
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/api`:

```nginx
upstream api {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # GZIP compression
    gzip on;
    gzip_types text/plain text/css application/json;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Cache static responses
    location /docs {
        proxy_pass http://api;
        proxy_cache_valid 200 1d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check API health
curl https://api.yourdomain.com/health

# Check with authentication
curl -H "Authorization: Bearer <token>" \
     https://api.yourdomain.com/api/auth/me
```

### Logs

```bash
# View logs
docker-compose logs -f api

# Save logs to file
docker-compose logs api > api_logs.txt

# Clear old logs
docker exec data_quality_api bash -c "rm /app/logs/*.log"
```

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U data_quality_user data_quality_db \
    > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T postgres psql -U data_quality_user data_quality_db \
    < backup_20240101_120000.sql
```

### Database Maintenance

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Check database status
docker-compose exec postgres psql -U data_quality_user -d data_quality_db -c "\dt"
```

### Redis Management

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check memory usage
redis-cli INFO memory

# Clear cache
redis-cli FLUSHDB

# Monitor real-time commands
redis-cli MONITOR
```

### Performance Monitoring

```bash
# Check container stats
docker stats

# Monitor API response times
docker-compose logs api | grep "Process-Time"

# Database query performance
docker-compose exec postgres psql -U data_quality_user -d data_quality_db \
    -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10"
```

### Update & Upgrade

```bash
# Update dependencies
docker-compose build --no-cache

# Pull latest changes
git pull origin main

# Restart services
docker-compose restart api
```

## Troubleshooting

### Connection Refused

```bash
# Check if services are running
docker-compose ps

# Check port availability
netstat -tlnp | grep 8000
netstat -tlnp | grep 5432
netstat -tlnp | grep 6379

# Restart services
docker-compose restart
```

### Database Connection Error

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U data_quality_user -h postgres -c "SELECT 1"

# Check connection string in .env
cat .env | grep DATABASE_URL
```

### High Memory Usage

```bash
# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHDB

# Check application logs
docker-compose logs api | grep -i error
```

### API Slow Response

```bash
# Check database query performance
docker-compose logs api | tail -100

# Check Redis cache status
docker-compose exec redis redis-cli DBSIZE

# Monitor system resources
docker stats data_quality_api
```

## Security Checklist

- [ ] Change default database credentials
- [ ] Change SECRET_KEY to a strong random value
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable database encryption
- [ ] Use strong passwords for all accounts
- [ ] Restrict CORS origins
- [ ] Enable API rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Audit logs review

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 5  # Scale to 5 instances
```

### Performance Optimization

1. **Connection Pooling**
   - DATABASE_POOL_SIZE=30
   - DATABASE_MAX_OVERFLOW=20

2. **Caching**
   - ENABLE_CACHING=True
   - Adjust TTL values

3. **Database Indexing**
   - Ensure indexes on frequently queried fields
   - Run ANALYZE periodically

4. **Load Balancing**
   - Use Nginx or HAProxy
   - Configure health checks

## Support & Documentation

- API Documentation: /docs
- GitHub Issues: [Project Repository]
- Contact: [Support Email]

---

**Last Updated:** 2024  
**Version:** 1.0.0
