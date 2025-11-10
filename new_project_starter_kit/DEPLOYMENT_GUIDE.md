# Deployment Guide - Railway & Vercel

## 🎯 Purpose
Complete step-by-step guide for deploying your application to production using Railway (backend) and Vercel (frontend).

---

## Overview

### Deployment Architecture

```
GitHub Repository
    ├── Backend Code (Python/FastAPI)
    │   └── Deploys to → Railway
    │       └── PostgreSQL Database on Railway
    │
    └── Frontend Code (Next.js)
        └── Deploys to → Vercel
            └── Edge Network (CDN)
```

### Deployment Flow

```
1. Push to GitHub (main branch)
   ↓
2. Railway auto-deploys backend (2-3 minutes)
   ↓
3. Vercel auto-deploys frontend (2-3 minutes)
   ↓
4. Verify deployments
   ↓
5. Test production environment
```

---

## Prerequisites

### Required Accounts

- [ ] GitHub account (free)
- [ ] Railway account (free tier available) - [railway.app](https://railway.app)
- [ ] Vercel account (free tier available) - [vercel.com](https://vercel.com)

### Required Tools

- [ ] Git installed
- [ ] GitHub CLI (`gh`) installed (optional but recommended)
- [ ] Railway CLI installed (optional but recommended)
- [ ] Vercel CLI installed (optional but recommended)

```bash
# Install CLIs (macOS)
brew install gh
npm install -g railway
npm install -g vercel
```

### Repository Structure

Your repository should have this structure:
```
your-project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile (optional)
│   └── alembic/
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   └── src/
├── .gitignore
└── README.md
```

---

## Part 1: Railway Backend Deployment

### Step 1: Create Railway Project

#### Option A: Using Railway Dashboard (Recommended for First Time)

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select your repository
6. Railway will auto-detect your backend

#### Option B: Using Railway CLI

```bash
# Login to Railway
railway login

# Initialize project
cd your-project/backend
railway init

# Link to existing project (if already created)
railway link [project-id]
```

### Step 2: Add PostgreSQL Database

1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable
4. Wait 1-2 minutes for database to provision

**Verify Database:**
```bash
# Using Railway CLI
railway run echo $DATABASE_URL

# Should output: postgresql://postgres:[password]@[host]:[port]/railway
```

### Step 3: Configure Environment Variables

#### Set Variables in Railway Dashboard:

1. Click on your backend service
2. Go to "Variables" tab
3. Add each variable:

```bash
# Required Variables
DATABASE_URL=postgresql://...  # Auto-set by Railway
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Keys (replace with your actual keys)
FINNHUB_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# CORS Settings
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

**Important:** Do NOT set these in `.env` file in production!

#### Using Railway CLI:

```bash
# Set individual variable
railway variables set FINNHUB_API_KEY=your_key_here

# Set multiple variables from file
railway variables set -f .env.production
```

### Step 4: Configure Build Settings

#### Option A: Let Railway Auto-Detect (Nixpacks)

If you have `requirements.txt`, Railway will auto-detect Python and:
- Install dependencies
- Start your app with gunicorn/uvicorn
- No configuration needed!

#### Option B: Use Custom Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run database migrations (if using Alembic)
RUN if [ -d "alembic" ]; then alembic upgrade head; fi

# Expose port (Railway uses PORT environment variable)
EXPOSE 8000

# Start application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**When to use Dockerfile:**
- Need specific system packages
- Complex build process
- Custom startup commands
- Need to run migrations before starting

**When to use Nixpacks (auto-detect):**
- Simple Python app
- Standard dependencies
- No custom build steps

### Step 5: Configure Root Directory

If your backend is in a subdirectory:

1. Go to Railway dashboard → Settings
2. Set "Root Directory" to `backend`
3. Or use `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 6: Deploy Backend

#### Automatic Deployment (Recommended):

```bash
# Push to GitHub main branch
git push origin main

# Railway auto-deploys in 2-3 minutes
```

#### Manual Deployment:

```bash
# Using Railway CLI
railway up

# Force redeploy from dashboard
# Click "Deploy" → "Redeploy"
```

### Step 7: Get Backend URL

```bash
# Using Railway CLI
railway domain

# Or get from dashboard
# Settings → Generate Domain
```

**Example URL:** `https://your-app.railway.app`

### Step 8: Verify Backend Deployment

```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Expected response:
# {"status":"healthy"}

# Test database connection
curl https://your-app.railway.app/db-check

# Expected response:
# {"connected":true,"tables":["your_tables"]}
```

### Step 9: Check Railway Logs

```bash
# Using Railway CLI
railway logs

# Or view in dashboard
# Click on service → Logs tab
```

**Look for:**
- ✅ "Application startup complete"
- ✅ "Uvicorn running on 0.0.0.0:8000"
- ❌ Any error messages

---

## Part 2: Vercel Frontend Deployment

### Step 1: Create Vercel Project

#### Option A: Using Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel auto-detects Next.js

#### Option B: Using Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy from frontend directory
cd your-project/frontend
vercel

# Follow prompts to link project
```

### Step 2: Configure Build Settings

In Vercel dashboard:

1. **Framework Preset:** Next.js (auto-detected)
2. **Root Directory:** `frontend` (if applicable)
3. **Build Command:** `npm run build` (default)
4. **Output Directory:** `.next` (default)
5. **Install Command:** `npm install` (default)

### Step 3: Configure Environment Variables

#### Add Variables in Vercel Dashboard:

1. Go to Project Settings → Environment Variables
2. Add each variable:

```bash
# Backend API URL (from Railway)
NEXT_PUBLIC_API_URL=https://your-app.railway.app

# Environment
NEXT_PUBLIC_ENVIRONMENT=production

# Any server-side secrets (NOT exposed to browser)
ANALYTICS_SECRET=your_secret_here
```

**Important:** Only `NEXT_PUBLIC_*` variables are exposed to the browser!

#### Using Vercel CLI:

```bash
# Set production variable
vercel env add NEXT_PUBLIC_API_URL production

# Pull variables to local
vercel env pull .env.local
```

### Step 4: Configure next.config.js

Ensure CORS and API proxy are configured:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Configure API rewrites (optional, for same-origin requests)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },

  // Configure headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },

  // Image optimization domains (if using next/image)
  images: {
    domains: ['your-cdn.com'],
  },
};

module.exports = nextConfig;
```

### Step 5: Deploy Frontend

#### Automatic Deployment (Recommended):

```bash
# Push to GitHub main branch
git push origin main

# Vercel auto-deploys in 2-3 minutes
```

#### Manual Deployment:

```bash
# Using Vercel CLI
vercel --prod

# Or redeploy from dashboard
# Deployments → Click "..." → Redeploy
```

### Step 6: Get Frontend URL

Your app will be available at:
- **Production:** `https://your-app.vercel.app`
- **Preview:** `https://your-app-[hash].vercel.app` (for branches)

### Step 7: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as shown
4. Vercel automatically provisions SSL certificate

### Step 8: Verify Frontend Deployment

```bash
# Test frontend
curl https://your-app.vercel.app

# Check in browser
open https://your-app.vercel.app
```

**Verify:**
- [ ] Page loads without errors
- [ ] Can fetch data from backend
- [ ] No CORS errors in browser console

### Step 9: Check Vercel Logs

1. Go to Vercel Dashboard → Project → Deployments
2. Click on latest deployment
3. View "Build Logs" and "Function Logs"

**Look for:**
- ✅ "Build completed"
- ✅ "Deployment ready"
- ❌ Any error messages

---

## Part 3: Connect Frontend to Backend

### Step 1: Update CORS in Backend

Ensure backend allows frontend domain:

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://your-app.vercel.app",  # Production
        "https://*.vercel.app",  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Update API URL in Frontend

Verify `NEXT_PUBLIC_API_URL` is set correctly:

```typescript
// frontend/src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchData() {
  const response = await fetch(`${API_URL}/api/data`);
  return response.json();
}
```

### Step 3: Test Frontend → Backend Connection

Open browser console and check:

```javascript
// In browser console
fetch('https://your-app.railway.app/health')
  .then(r => r.json())
  .then(console.log)

// Should see: {status: "healthy"}
```

**If CORS error:**
1. Check Railway `CORS_ORIGINS` includes Vercel domain
2. Redeploy backend after changing CORS
3. Wait 2-3 minutes for deployment

---

## Part 4: Database Migrations

### Step 1: Set Up Alembic (First Time)

```bash
# In backend directory
pip install alembic

# Initialize Alembic
alembic init alembic

# Configure alembic.ini
# Set sqlalchemy.url to use environment variable
```

Edit `alembic/env.py`:

```python
import os
from dotenv import load_dotenv

# Load environment variables conditionally
if not os.getenv('DATABASE_URL'):
    load_dotenv()

# Get database URL
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
```

### Step 2: Create Migration

```bash
# Auto-generate migration from models
alembic revision --autogenerate -m "Initial migration"

# Review generated migration file
# Edit if necessary
```

### Step 3: Apply Migration Locally

```bash
# Test migration locally first
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### Step 4: Apply Migration to Production

#### Option A: Run Migration in Dockerfile

```dockerfile
# In Dockerfile, before starting app
RUN alembic upgrade head
```

#### Option B: Run Migration via Railway CLI

```bash
# Connect to Railway environment
railway run bash

# Inside Railway shell
alembic upgrade head
exit
```

#### Option C: Run Migration Manually

```bash
# Get Railway database URL
railway variables get DATABASE_URL

# Run migration locally pointing to production DB
DATABASE_URL=postgresql://... alembic upgrade head
```

**⚠️ Warning:** Be very careful with production database operations!

### Step 5: Verify Migration

```bash
# Check database tables
railway run psql $DATABASE_URL -c "\dt"

# Or use diagnostic endpoint
curl https://your-app.railway.app/db-check
```

---

## Part 5: Post-Deployment Checklist

### Immediate Checks (Within 5 Minutes)

- [ ] Backend health check returns 200
  ```bash
  curl https://your-app.railway.app/health
  ```

- [ ] Database connection works
  ```bash
  curl https://your-app.railway.app/db-check
  ```

- [ ] Frontend loads without errors
  ```bash
  open https://your-app.vercel.app
  ```

- [ ] Frontend can fetch from backend
  - Open browser console
  - Check for CORS errors
  - Verify API calls complete

- [ ] Railway logs show no errors
  ```bash
  railway logs --tail
  ```

- [ ] Vercel deployment succeeded
  - Check Vercel dashboard
  - View deployment logs

### Environment Variable Checks

- [ ] All required variables set in Railway
  ```bash
  railway variables
  ```

- [ ] All required variables set in Vercel
  ```bash
  vercel env ls
  ```

- [ ] No `.env` file committed to git
  ```bash
  git ls-files | grep .env
  # Should return nothing
  ```

- [ ] `.env.example` exists with placeholder values

### Database Checks

- [ ] Migrations applied successfully
- [ ] Tables exist in database
- [ ] Sequences are correct (if data was imported)
  ```sql
  SELECT MAX(id) FROM your_table;
  -- Then fix sequence if needed
  ALTER SEQUENCE your_table_id_seq RESTART WITH [max_id + 1];
  ```

### Security Checks

- [ ] No API keys in code
  ```bash
  grep -r "sk_live\|api_key" . --exclude-dir={venv,node_modules,.git}
  ```

- [ ] CORS configured with explicit origins (not "*")
- [ ] Database not publicly accessible
- [ ] HTTPS enabled (automatic with Railway/Vercel)

### Performance Checks

- [ ] API response time < 1 second
  ```bash
  time curl https://your-app.railway.app/api/endpoint
  ```

- [ ] Frontend loads < 3 seconds
  - Check Vercel Analytics
  - Use Lighthouse in Chrome DevTools

- [ ] No N+1 queries in logs

---

## Part 6: Monitoring & Debugging

### Railway Monitoring

#### View Logs
```bash
# Tail logs in real-time
railway logs --tail

# View last 100 lines
railway logs

# Filter logs
railway logs | grep ERROR
```

#### Check Metrics
1. Go to Railway Dashboard → Project → Metrics
2. View:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

#### Common Railway Issues

**Issue: Application Won't Start**
```bash
# Check logs
railway logs

# Common causes:
# 1. Import error (missing dependency)
# 2. DATABASE_URL not set
# 3. Port binding issue (use $PORT)
# 4. Dockerfile CMD incorrect
```

**Issue: Database Connection Failed**
```bash
# Verify DATABASE_URL is set
railway variables get DATABASE_URL

# Check if load_dotenv() is overriding it
# Should be conditional:
if not os.getenv('DATABASE_URL'):
    load_dotenv()
```

**Issue: Environment Variables Not Loading**
```bash
# Verify variables are set
railway variables

# Redeploy to pick up new variables
railway up --detach
```

### Vercel Monitoring

#### View Logs
1. Go to Vercel Dashboard → Project → Deployments
2. Click on deployment → "View Function Logs"
3. Filter by:
   - Errors only
   - Specific paths
   - Time range

#### Check Analytics
1. Go to Project → Analytics
2. View:
   - Page views
   - Top pages
   - Response times
   - Error rates

#### Common Vercel Issues

**Issue: Build Failed**
```bash
# Check build logs in Vercel dashboard

# Common causes:
# 1. TypeScript errors
# 2. Missing environment variables
# 3. Incorrect build command
# 4. Node version mismatch
```

**Issue: API Calls Failing (CORS)**
```javascript
// Check browser console for CORS errors
// Solution: Update backend CORS_ORIGINS
```

**Issue: Environment Variables Not Available**
```bash
# Verify variables are set in Vercel
vercel env ls

# Check if using correct prefix
# NEXT_PUBLIC_* for client-side
# NO PREFIX for server-side only
```

### Testing Production Issues Locally

```bash
# Use production database locally
export DATABASE_URL="postgresql://..."  # From Railway
python backend/main.py

# Use production API locally
export NEXT_PUBLIC_API_URL="https://your-app.railway.app"
npm run dev
```

**⚠️ Warning:** Be careful when connecting locally to production database!

---

## Part 7: Continuous Deployment Setup

### Enable Auto-Deploy

**Railway:**
1. Auto-deploys on push to `main` branch (default)
2. To change:
   - Settings → Deployments
   - Configure branch and PR settings

**Vercel:**
1. Auto-deploys on push to `main` branch (default)
2. Preview deploys on all branches/PRs (default)
3. To change:
   - Settings → Git
   - Configure deployment branches

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push to GitHub
git push origin feature/new-feature

# 4. Vercel creates preview deployment automatically
# Railway does NOT deploy feature branches (unless configured)

# 5. Merge to main via pull request
gh pr create --title "Add new feature"

# 6. After merge, both Railway and Vercel deploy automatically
```

### Preview Deployments

**Vercel Preview Deployments:**
- Created automatically for every branch/PR
- Unique URL: `https://your-app-[hash].vercel.app`
- Test before merging to production

**Railway Preview Environments (Optional):**
1. Settings → Environments → Create PR Environment
2. Railway creates isolated environment for each PR
3. Separate database and resources

---

## Part 8: Rollback Strategy

### Vercel Rollback

```bash
# List recent deployments
vercel ls

# Rollback to previous deployment (via dashboard)
# 1. Go to Deployments
# 2. Find working deployment
# 3. Click "..." → "Promote to Production"

# Or use CLI
vercel rollback [deployment-url]
```

### Railway Rollback

```bash
# Via dashboard:
# 1. Go to Deployments
# 2. Find working deployment
# 3. Click "Redeploy"

# Via git:
git revert HEAD
git push origin main
# Railway auto-deploys reverted code
```

### Database Rollback

```bash
# Rollback migration
alembic downgrade -1

# Or to specific revision
alembic downgrade [revision]
```

**⚠️ Warning:** Database rollbacks can cause data loss!

---

## Part 9: Cost Optimization

### Railway Free Tier

- **$5 free credit per month**
- Usage-based pricing after free credit
- Typical costs: $5-20/month for small app

**Optimization Tips:**
- [ ] Use sleep mode for non-production services
- [ ] Set resource limits
- [ ] Monitor usage in dashboard

### Vercel Free Tier

- **Unlimited deployments**
- **100 GB bandwidth/month**
- **6000 build minutes/month**

**Optimization Tips:**
- [ ] Use Next.js Image Optimization
- [ ] Enable ISR (Incremental Static Regeneration)
- [ ] Configure proper caching headers

---

## Part 10: Troubleshooting Guide

### Common Error Patterns

#### Error: `ModuleNotFoundError: No module named 'X'`
**Cause:** Dependency missing from requirements.txt
**Solution:**
```bash
pip freeze | grep package-name >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

#### Error: `duplicate key value violates unique constraint`
**Cause:** PostgreSQL sequence out of sync
**Solution:**
```sql
SELECT MAX(id) FROM your_table;
ALTER SEQUENCE your_table_id_seq RESTART WITH [max_id + 1];
```

#### Error: `Access blocked by CORS policy`
**Cause:** Frontend domain not in backend CORS settings
**Solution:**
```python
# Update backend/main.py
allow_origins=[
    "https://your-app.vercel.app",  # Add this
]
```

#### Error: `Expecting value: line 1 column 1`
**Cause:** API returned HTML error page instead of JSON
**Solution:**
```bash
# Check what backend is actually returning
curl https://your-app.railway.app/api/endpoint

# Fix backend error first, then redeploy
```

### Diagnostic Commands

```bash
# Check if Railway service is running
railway status

# Check environment variables
railway variables

# Connect to Railway database
railway run psql $DATABASE_URL

# View Railway logs with filter
railway logs | grep -i error

# Test API endpoint
curl -v https://your-app.railway.app/health

# Check Vercel deployment status
vercel inspect [deployment-url]

# Pull Vercel environment variables
vercel env pull
```

---

## Appendix A: Complete Deployment Timeline

```
Time   | Action                          | Status
-------|--------------------------------|--------
00:00  | Push to GitHub main branch     | ✓
00:01  | Railway detects changes        | Building...
00:03  | Railway build complete         | ✓
00:04  | Railway deployment live        | ✓
00:05  | Vercel detects changes         | Building...
00:07  | Vercel build complete          | ✓
00:08  | Vercel deployment live         | ✓
00:09  | Test health endpoints          | ✓
00:10  | Test frontend → backend        | ✓
00:15  | Monitor logs for errors        | ✓
```

**Total time: 10-15 minutes for complete deployment**

---

## Appendix B: Environment Variable Reference

### Backend (Railway)

```bash
# Required
DATABASE_URL=postgresql://...  # Auto-set by Railway
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app

# API Keys (if needed)
FINNHUB_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}

# Optional
REDIS_URL=redis://...
SENTRY_DSN=https://...
```

### Frontend (Vercel)

```bash
# Required (exposed to browser)
NEXT_PUBLIC_API_URL=https://your-app.railway.app
NEXT_PUBLIC_ENVIRONMENT=production

# Server-side only (not exposed)
ANALYTICS_SECRET=your_secret
DATABASE_URL=postgresql://...  # If doing SSR with direct DB access
```

---

## Appendix C: Quick Reference Commands

```bash
# Railway
railway login
railway link
railway up
railway logs --tail
railway run bash
railway variables
railway status

# Vercel
vercel login
vercel link
vercel
vercel --prod
vercel logs
vercel env ls
vercel inspect

# Database
alembic upgrade head
alembic downgrade -1
railway run psql $DATABASE_URL

# Testing
curl https://your-app.railway.app/health
curl https://your-app.vercel.app
```

---

**Last Updated:** 2025-10-31
**Version:** 1.0
**Tested With:** Railway v3, Vercel v28, Next.js 14, FastAPI 0.104
