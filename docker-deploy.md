# SafeGuardLLM Docker Deployment Guide

This guide explains how to deploy the SafeGuardLLM application locally using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 4GB RAM available for containers
- LLM Provider API Keys (OpenAI, Anthropic, Google)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd safeguard-llm

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual API keys and configuration:

```bash
# Required: Add your LLM API keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here  
GOOGLE_API_KEY=your-google-gemini-key-here

# Optional: Customize other settings
JWT_SECRET=your-secure-jwt-secret
SESSION_SECRET=your-session-secret
```

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Web Interface**: http://localhost:80 (or http://localhost:5000 if not using nginx)
- **Database**: localhost:5432 (for external tools)
- **Redis Cache**: localhost:6379

## Architecture

The Docker deployment includes:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │  SafeGuardLLM   │    │   PostgreSQL    │
│  Reverse Proxy  │───▶│   Application   │───▶│    Database     │
│   Port: 80      │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │      Redis      │
                       │   Cache Store   │
                       │   Port: 6379    │
                       └─────────────────┘
```

## Service Details

### Application Container
- **Image**: Built from local Dockerfile
- **Port**: 5000 (internal), exposed via nginx
- **Health Check**: `/api/stats` endpoint
- **Volumes**: Application logs mounted to host

### PostgreSQL Database
- **Image**: postgres:15-alpine
- **Port**: 5432 (exposed to host)
- **Volume**: Persistent data storage
- **Health Check**: pg_isready command
- **Initial Setup**: Runs init-db.sql on first start

### Redis Cache (Optional)
- **Image**: redis:7-alpine  
- **Port**: 6379 (exposed to host)
- **Volume**: Persistent cache data
- **Health Check**: redis-cli ping

### Nginx Reverse Proxy (Optional)
- **Image**: nginx:alpine
- **Port**: 80 (main entry point)
- **Features**: Rate limiting, gzip compression, security headers
- **Config**: Custom nginx.conf with WebSocket support

## Management Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services  
docker-compose down

# Restart specific service
docker-compose restart app

# View service logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec app bash
docker-compose exec postgres psql -U safeguard_user -d safeguard_llm
```

### Database Management
```bash
# Run database migrations
docker-compose exec app npm run db:push

# Backup database
docker-compose exec postgres pg_dump -U safeguard_user safeguard_llm > backup.sql

# Restore database
docker-compose exec -T postgres psql -U safeguard_user safeguard_llm < backup.sql

# Access database shell
docker-compose exec postgres psql -U safeguard_user -d safeguard_llm
```

### Application Management
```bash
# View application logs
docker-compose logs -f app

# Restart application only
docker-compose restart app

# Update application (rebuild)
docker-compose build app
docker-compose up -d app

# Check application health
curl http://localhost:5000/api/stats
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Application environment | production | No |
| `PORT` | Application port | 5000 | No |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://... | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | - | Yes |
| `REDIS_URL` | Redis connection string | redis://redis:6379 | No |
| `JWT_SECRET` | JWT signing secret | - | Yes |
| `SESSION_SECRET` | Session secret | - | Yes |

### Docker Compose Overrides

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  app:
    environment:
      - DEBUG=safeguard:*
    volumes:
      - ./custom-config:/app/config
      
  postgres:
    ports:
      - "5433:5432"  # Use different port
```

## Development Mode

For development with hot reloading:

```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or set environment
export NODE_ENV=development
docker-compose up -d
```

## Production Considerations

### Security
- Change default passwords in production
- Use Docker secrets for sensitive data
- Enable SSL/TLS with real certificates
- Configure firewall rules
- Regular security updates

### Performance
- Allocate sufficient memory (4GB+ recommended)
- Configure PostgreSQL for your workload
- Monitor resource usage
- Set up log rotation

### Monitoring
- Add health check endpoints
- Configure log aggregation
- Set up alerting for service failures
- Monitor database performance

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U safeguard_user safeguard_llm | gzip > "backup_${DATE}.sql.gz"
```

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check logs for errors
docker-compose logs app

# Verify environment variables
docker-compose exec app env | grep -E "(DATABASE_URL|API_KEY)"

# Test database connection
docker-compose exec app npm run db:push
```

**Database connection failed:**
```bash
# Check database status
docker-compose ps postgres

# Test connection manually
docker-compose exec postgres pg_isready -U safeguard_user

# Check database logs
docker-compose logs postgres
```

**API keys not working:**
```bash
# Verify API keys are set
docker-compose exec app printenv | grep API_KEY

# Test API connectivity
docker-compose exec app curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Performance Issues

**High memory usage:**
```bash
# Check container resource usage
docker stats

# Optimize PostgreSQL settings
# Edit postgresql.conf in container or via environment variables
```

**Slow responses:**
```bash
# Check database query performance
docker-compose exec postgres psql -U safeguard_user -d safeguard_llm -c "SELECT * FROM pg_stat_activity;"

# Monitor application metrics
docker-compose logs app | grep -E "(slow|timeout|error)"
```

### Network Issues

**Services can't communicate:**
```bash
# Check network connectivity
docker-compose exec app ping postgres
docker-compose exec app ping redis

# Verify network configuration
docker network ls
docker network inspect safeguard-llm_safeguard-network
```

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run any database migrations
docker-compose exec app npm run db:push
```

## Uninstalling

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```

## Support

For issues with the Docker deployment:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs [service]`
3. Verify environment configuration
4. Check service health: `docker-compose ps`

---

This Docker deployment provides a complete, production-ready SafeGuardLLM environment that can be easily deployed and managed on any Docker-compatible system.