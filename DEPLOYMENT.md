# Railway Deployment Guide

This guide explains how to deploy the ERP Multi-Tenant system to Railway without Docker Desktop.

## Prerequisites

- GitHub account with repository access
- Railway account (sign up at https://railway.app)
- Railway CLI (optional, for advanced usage)

## Deployment Architecture

Railway will deploy three separate services:
1. **PostgreSQL Database** (Railway Plugin)
2. **Backend API** (FastAPI)
3. **Frontend** (Next.js)

## Step-by-Step Deployment

### 1. Create Railway Account

1. Go to https://railway.app
2. Sign up with your GitHub account
3. Authorize Railway to access your repositories

### 2. Create New Project

1. Click "New Project" in Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your repository: `DigaoRodrigues/ERP`
4. Railway will detect your project structure

### 3. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Note: Database URL will be automatically available as `DATABASE_URL`

### 4. Deploy Backend Service

#### 4.1 Create Backend Service

1. Click "New" → "GitHub Repo"
2. Select your repository
3. Configure the service:
   - **Name**: `erp-backend`
   - **Root Directory**: `/backend`
   - **Build Command**: (auto-detected from requirements.txt)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 4.2 Configure Backend Environment Variables

Add these environment variables in Railway dashboard:

```bash
# Database (auto-provided by Railway PostgreSQL plugin)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Configuration (IMPORTANT: Generate secure keys!)
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Integration
AI_PROVIDER=claude
AI_API_KEY=<your-anthropic-api-key>

# Application Settings
ENVIRONMENT=production
PROJECT_NAME=ERP Multi-Tenant API
VERSION=0.1.0

# CORS (use your Railway frontend URL)
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://erp-frontend-production.up.railway.app
```

**Generate JWT Secret Key:**
```bash
# On your local machine (Git Bash or WSL)
openssl rand -hex 32
```

#### 4.3 Backend Deployment Settings

- **Watch Paths**: `/backend/**`
- **Deploy on Push**: Enable for `main` branch
- **Health Check Path**: `/health`

### 5. Deploy Frontend Service

#### 5.1 Create Frontend Service

1. Click "New" → "GitHub Repo"
2. Select your repository
3. Configure the service:
   - **Name**: `erp-frontend`
   - **Root Directory**: `/frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

#### 5.2 Configure Frontend Environment Variables

```bash
# Backend API URL (use your Railway backend URL)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Node Environment
NODE_ENV=production
```

#### 5.3 Frontend Deployment Settings

- **Watch Paths**: `/frontend/**`
- **Deploy on Push**: Enable for `main` branch

### 6. Run Database Migrations

Once backend is deployed, run migrations:

#### Option A: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migrations
railway run --service erp-backend alembic upgrade head
```

#### Option B: Using Railway Dashboard

1. Go to backend service
2. Click "Settings" → "Deploy"
3. Add a one-time deployment command:
   ```bash
   alembic upgrade head
   ```

### 7. Configure Custom Domains (Optional)

1. Go to each service settings
2. Click "Settings" → "Domains"
3. Add custom domain or use Railway-provided domain
4. Update CORS settings in backend with new domains

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

## Troubleshooting

### Backend Won't Start

1. Check logs for errors
2. Verify all environment variables are set
3. Ensure DATABASE_URL is connected
4. Check Python version compatibility

### Frontend Can't Connect to Backend

1. Verify NEXT_PUBLIC_API_URL is correct
2. Check CORS settings in backend
3. Ensure backend is deployed and healthy
4. Check network/firewall settings

### Database Connection Issues

1. Verify DATABASE_URL format
2. Check PostgreSQL service is running
3. Ensure database migrations ran successfully
4. Check connection pool settings

### Deployment Fails

1. Check build logs for errors
2. Verify package.json/requirements.txt
3. Ensure all dependencies are listed
4. Check Railway service limits

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

## Support

- **Railway Documentation**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Project Issues**: https://github.com/DigaoRodrigues/ERP/issues

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
