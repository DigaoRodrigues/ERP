# Railway Deployment Guide

This guide explains how to deploy the ERP Multi-Tenant system to Railway without Docker Desktop.

## ⚠️ CRITICAL: This is a Monorepo

This project has **backend** and **frontend** in separate directories. You **MUST** deploy them as **separate Railway services** with the **Root Directory** configured for each.

## Prerequisites

- GitHub account with repository access
- Railway account (sign up at https://railway.app)
- Railway CLI (optional, for advanced usage)

## Deployment Architecture

Railway will deploy three separate services:
1. **PostgreSQL Database** (Railway Plugin)
2. **Backend API** (FastAPI) - Root Directory: `/backend`
3. **Frontend** (Next.js) - Root Directory: `/frontend`

## Step-by-Step Deployment

### 1. Create Railway Account

1. Go to https://railway.app
2. Sign up with your GitHub account
3. Authorize Railway to access your repositories

### 2. Create New Project

1. Click "New Project" in Railway dashboard
2. Give it a name: "ERP Multi-Tenant"
3. You'll add services to this project

### 3. Add PostgreSQL Database FIRST

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Note: Database URL will be automatically available as `DATABASE_URL`
5. **Wait for PostgreSQL to be ready before proceeding**

### 4. Deploy Backend Service

#### 4.1 Create Backend Service

1. Click "New" → "GitHub Repo"
2. Select your repository: `DigaoRodrigues/ERP`
3. **CRITICAL STEP**: After service is created, go to **Settings**
4. Find **"Root Directory"** setting
5. Set it to: `backend` (without leading slash)
6. Click "Save"
7. Railway will automatically redeploy with correct directory

#### 4.2 Configure Backend Environment Variables

Go to Backend service → Variables tab → Add these:

```bash
# Database (Reference the PostgreSQL service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Configuration (IMPORTANT: Generate secure keys!)
JWT_SECRET_KEY=your-generated-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Integration
AI_PROVIDER=claude
AI_API_KEY=your-anthropic-api-key-here

# Application Settings
ENVIRONMENT=production
PROJECT_NAME=ERP Multi-Tenant API
VERSION=0.1.0

# CORS (will update after frontend is deployed)
ALLOWED_ORIGINS=http://localhost:3000
```

**Generate JWT Secret Key:**
```bash
# On your local machine (Git Bash or WSL)
openssl rand -hex 32
```

#### 4.3 Backend Service Settings

- **Root Directory**: `backend` ✅ CRITICAL
- **Watch Paths**: Leave default (watches entire repo)
- **Deploy on Push**: Enable for `main` branch
- **Health Check Path**: `/health`

### 5. Deploy Frontend Service

#### 5.1 Create Frontend Service

1. Click "New" → "GitHub Repo"
2. Select your repository: `DigaoRodrigues/ERP` (same repo, different service)
3. **CRITICAL STEP**: After service is created, go to **Settings**
4. Find **"Root Directory"** setting
5. Set it to: `frontend` (without leading slash)
6. Click "Save"
7. Railway will automatically redeploy with correct directory

#### 5.2 Configure Frontend Environment Variables

Go to Frontend service → Variables tab → Add these:

```bash
# Backend API URL (use your Railway backend URL)
NEXT_PUBLIC_API_URL=https://your-backend-service.railway.app

# Node Environment
NODE_ENV=production
```

**To get your backend URL:**
1. Go to Backend service
2. Click "Settings" → "Networking"
3. Copy the public domain (e.g., `https://erp-backend-production.up.railway.app`)
4. Paste it as `NEXT_PUBLIC_API_URL` in frontend variables

#### 5.3 Frontend Service Settings

- **Root Directory**: `frontend` ✅ CRITICAL
- **Watch Paths**: Leave default
- **Deploy on Push**: Enable for `main` branch

### 6. Update Backend CORS Settings

Now that frontend is deployed:

1. Go to Backend service → Variables
2. Update `ALLOWED_ORIGINS` to include your frontend URL:
   ```bash
   ALLOWED_ORIGINS=https://your-frontend-service.railway.app,http://localhost:3000
   ```
3. Save and redeploy backend

### 7. Run Database Migrations

Once backend is deployed successfully:

#### Option A: Using Railway Dashboard (Easiest)

1. Go to Backend service
2. Click "Deployments" tab
3. Find the latest successful deployment
4. Click the three dots (⋮) → "View Logs"
5. You'll need to run migrations manually via Railway CLI (see Option B)

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Select backend service
railway service

# Run migrations
railway run alembic upgrade head
```

### 8. Verify Deployment

#### Backend Health Check:
```bash
curl https://your-backend-service.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

#### API Documentation:
Visit: `https://your-backend-service.railway.app/docs`

#### Frontend:
Visit: `https://your-frontend-service.railway.app`

### 9. Configure Custom Domains (Optional)

1. Go to each service settings
2. Click "Settings" → "Domains"
3. Add custom domain or use Railway-provided domain
4. Update CORS settings in backend with new domains

## Troubleshooting

### Error: "Nixpacks was unable to generate a build plan"

**Solution**: You forgot to set the Root Directory!
1. Go to service Settings
2. Set Root Directory to `backend` or `frontend`
3. Save and redeploy

### Error: "Set the root directory to 'backend' or 'frontend'"

**Solution**: Same as above - configure Root Directory in service settings.

### Backend Won't Start

1. Check logs: Backend service → Deployments → View Logs
2. Verify all environment variables are set
3. Ensure DATABASE_URL is connected to PostgreSQL service
4. Check Python version compatibility (should be 3.11)

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check CORS settings in backend `ALLOWED_ORIGINS`
3. Ensure backend is deployed and healthy
4. Check browser console for errors

### Database Connection Issues

1. Verify `DATABASE_URL` format in backend variables
2. Check PostgreSQL service is running
3. Ensure database migrations ran successfully
4. Check connection pool settings

### Build Fails

1. Check build logs for specific errors
2. Verify `nixpacks.toml` exists in backend/frontend directories
3. Ensure all dependencies are listed in requirements.txt/package.json
4. Check Railway service limits

## Environment-Specific Deployments

### Staging Environment

1. Create a new Railway project for staging
2. Deploy from `staging` branch
3. Use separate database and environment variables
4. Test features before promoting to production

### Production Environment

1. Use `main` branch for production
2. Enable branch protection on GitHub
3. Require PR reviews before merging to main
4. Set up monitoring and alerts

## Monitoring and Logs

### View Logs

1. Go to service in Railway dashboard
2. Click "Deployments" tab
3. Select deployment to view logs
4. Use search and filters to debug issues

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response times

### Alerts

Set up alerts for:
- Service crashes
- High error rates
- Resource limits
- Deployment failures

## Database Backups

### Automatic Backups

Railway PostgreSQL includes automatic backups:
- Daily backups retained for 7 days
- Point-in-time recovery available

### Manual Backup

```bash
# Using Railway CLI
railway run --service postgres pg_dump > backup.sql

# Restore from backup
railway run --service postgres psql < backup.sql
```

## Cost Optimization

### Free Tier Limits

Railway free tier includes:
- $5 credit per month
- Shared resources
- Community support

### Optimize Costs

1. **Use sleep mode** for non-production environments
2. **Optimize queries** to reduce database load
3. **Enable caching** where appropriate
4. **Monitor usage** regularly
5. **Scale horizontally** only when needed

### Upgrade to Pro

When you need:
- More resources
- Custom domains
- Priority support
- Higher limits

## Security Best Practices

1. **Never commit secrets** to Git
2. **Use Railway environment variables** for all secrets
3. **Rotate JWT secrets** regularly
4. **Enable HTTPS** (automatic on Railway)
5. **Set up rate limiting** per workspace
6. **Monitor for suspicious activity**
7. **Keep dependencies updated**

## CI/CD Integration

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Rollback Strategy

### Quick Rollback

1. Go to service in Railway dashboard
2. Click "Deployments" tab
3. Find previous successful deployment
4. Click "Redeploy"

### Database Rollback

```bash
# Rollback one migration
railway run --service erp-backend alembic downgrade -1

# Rollback to specific version
railway run --service erp-backend alembic downgrade <revision>
```

## Common Railway Configuration Mistakes

### ❌ Wrong: Deploying entire repo without Root Directory
```
Root Directory: (empty)
Result: Build fails - Nixpacks can't find project files
```

### ✅ Correct: Set Root Directory for each service
```
Backend Service:
  Root Directory: backend
  
Frontend Service:
  Root Directory: frontend
```

### ❌ Wrong: Using relative paths in Root Directory
```
Root Directory: /backend  (with leading slash)
Root Directory: ./backend (with ./)
```

### ✅ Correct: Use simple directory name
```
Root Directory: backend
Root Directory: frontend
```

## Support

- **Railway Documentation**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Project Issues**: https://github.com/DigaoRodrigues/ERP/issues

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  Railway Deployment Checklist                       │
├─────────────────────────────────────────────────────┤
│  ☐ Create Railway account                           │
│  ☐ Create new project                               │
│  ☐ Add PostgreSQL database                          │
│  ☐ Deploy backend (Root Directory: backend)         │
│  ☐ Configure backend environment variables          │
│  ☐ Deploy frontend (Root Directory: frontend)       │
│  ☐ Configure frontend environment variables         │
│  ☐ Update backend CORS with frontend URL            │
│  ☐ Run database migrations                          │
│  ☐ Test backend health check                        │
│  ☐ Test frontend                                    │
│  ☐ Configure custom domains (optional)              │
└─────────────────────────────────────────────────────┘
```

## Next Steps After Deployment

1. ✅ Verify all services are running
2. ✅ Test API endpoints via Swagger docs
3. ✅ Test frontend functionality
4. ✅ Run database migrations
5. ✅ Create first workspace
6. ✅ Set up monitoring alerts
7. ✅ Configure custom domains
8. ✅ Set up staging environment

---

**Your ERP system is now deployed on Railway! 🚀**