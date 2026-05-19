# Docker & Containerization Agent

## Domain Overview

This agent provides expertise in Docker containerization, multi-stage builds, optimization strategies, and container orchestration for the ERP Multi-Tenant System.

## Core Responsibilities

- Container configuration and optimization
- Multi-stage build strategies
- Docker Compose orchestration
- Production deployment best practices
- Security hardening

---

## Project Docker Architecture

### Current Structure

```
/docker
├── docker-compose.yml          # Local development orchestration
├── Dockerfile.backend          # Backend Python/FastAPI container
├── Dockerfile.frontend         # Frontend Next.js container
└── init-db.sql                 # PostgreSQL initialization
```

### Container Strategy

**Development**: Docker Compose with hot-reload
**Production**: Individual containers on Railway with nixpacks

---

## Backend Dockerfile Best Practices

### Multi-Stage Build Pattern

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts are executable
ENV PATH=/root/.local/bin:$PATH

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Optimizations

1. **Layer Caching**: Copy requirements.txt before source code
2. **Multi-stage**: Separate build and runtime environments
3. **Minimal Base**: Use slim images to reduce size
4. **Security**: Run as non-root user
5. **Health Checks**: Enable container health monitoring

---

## Frontend Dockerfile Best Practices

### Next.js Production Build

```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:18-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Stage 3: Runner
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Next.js Configuration for Standalone

```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  // Other configurations...
}
```

---

## Docker Compose for Development

### Complete Development Setup

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: erp_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-erp_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-erp_password}
      POSTGRES_DB: ${POSTGRES_DB:-erp_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-erp_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: erp_backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-erp_user}:${POSTGRES_PASSWORD:-erp_password}@postgres:5432/${POSTGRES_DB:-erp_db}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-dev-secret-key}
      ALLOWED_ORIGINS: http://localhost:3000
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_cache:/root/.cache
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
      target: deps  # Use deps stage for development
    container_name: erp_frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:
  backend_cache:
```

---

## Security Best Practices

### 1. Non-Root User

```dockerfile
# Create and use non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### 2. Minimal Base Images

```dockerfile
# Use Alpine or slim variants
FROM python:3.11-slim
FROM node:18-alpine
```

### 3. No Secrets in Images

```dockerfile
# ❌ BAD: Hardcoded secrets
ENV JWT_SECRET_KEY=my-secret-key

# ✅ GOOD: Use environment variables at runtime
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

### 4. Scan for Vulnerabilities

```bash
# Use Docker Scout or Trivy
docker scout cves local://myimage:latest
trivy image myimage:latest
```

---

## Performance Optimization

### 1. Layer Caching Strategy

```dockerfile
# Copy dependency files first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code last (changes frequently)
COPY . .
```

### 2. .dockerignore File

```
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.env
.venv
venv/
.git/
.gitignore
*.md
node_modules/
.next/
.cache/
coverage/
*.log
```

### 3. Multi-Stage Builds

Reduce final image size by 50-70% using multi-stage builds.

### 4. Build Cache Mounts

```dockerfile
# Use BuildKit cache mounts
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

---

## Health Checks

### Backend Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Frontend Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1
```

### Health Endpoint Implementation

```python
# backend/app/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

---

## Environment Variables Management

### Development (.env)

```bash
# Database
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=erp_password
POSTGRES_DB=erp_db

# Backend
DATABASE_URL=postgresql://erp_user:erp_password@postgres:5432/erp_db
JWT_SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Railway)

Use Railway's environment variable management:
- Never commit production secrets
- Use Railway's secret management
- Rotate secrets regularly

---

## Common Issues and Solutions

### Issue 1: Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

### Issue 2: Database Connection Refused

```yaml
# Ensure depends_on with health check
depends_on:
  postgres:
    condition: service_healthy
```

### Issue 3: Hot Reload Not Working

```yaml
# Ensure volumes are mounted correctly
volumes:
  - ./backend:/app
  - backend_cache:/root/.cache  # Prevent cache conflicts
```

### Issue 4: Build Cache Not Working

```bash
# Clear build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

---

## Railway Deployment Considerations

### Nixpacks Configuration

Railway uses Nixpacks for automatic builds. Configure via `nixpacks.toml`:

```toml
# backend/nixpacks.toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### Port Binding

Railway assigns `$PORT` dynamically:

```python
# Use environment variable for port
import os
port = int(os.getenv("PORT", 8000))
```

---

## Monitoring and Logging

### Container Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View specific service
docker logs erp_backend --tail 100 -f
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats

# Inspect container
docker inspect erp_backend
```

---

## Best Practices Checklist

- [ ] Use multi-stage builds
- [ ] Run as non-root user
- [ ] Implement health checks
- [ ] Use .dockerignore
- [ ] Optimize layer caching
- [ ] Scan for vulnerabilities
- [ ] Use minimal base images
- [ ] Never commit secrets
- [ ] Document environment variables
- [ ] Test locally before deploying

---

## Related Agents

- **Database Agent**: PostgreSQL container configuration
- **CI/CD Agent**: Container build and deployment pipelines
- **Performance Agent**: Container resource optimization

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
