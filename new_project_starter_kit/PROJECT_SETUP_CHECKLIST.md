# Project Setup Checklist

## 🎯 Purpose

This checklist ensures you set up your new project correctly from day one, avoiding the 23+ documented errors from previous projects. Follow this step-by-step guide BEFORE writing any code.

**Estimated Time:** 1-2 hours for initial setup

---

## Phase 1: Planning & Architecture (30 minutes)

### 1.1 Define Project Scope
- [ ] Write one-sentence project description
- [ ] List 3-5 core features (MVP only)
- [ ] Identify users/stakeholders
- [ ] Set success metrics

### 1.2 Choose Technology Stack
- [ ] **Backend Framework:**
  - Python: FastAPI, Django, Flask
  - Node.js: Express, NestJS
  - Document choice and reasoning

- [ ] **Frontend Framework:**
  - React: Next.js, Create React App
  - Vue: Nuxt, Vue CLI
  - Document choice and reasoning

- [ ] **Database:**
  - Development: SQLite (local only!)
  - Production: PostgreSQL (Railway, Supabase, etc.)
  - ⚠️ NEVER use SQLite in production for web apps

- [ ] **Deployment Platforms:**
  - Backend: Railway, Heroku, Fly.io
  - Frontend: Vercel, Netlify, Cloudflare Pages
  - Database: Included with backend or separate

### 1.3 Document Architecture Decisions
- [ ] Fill out ARCHITECTURE_TEMPLATE.md
- [ ] Draw system architecture diagram (even if simple)
- [ ] Document data flow
- [ ] List external APIs you'll use

---

## Phase 2: Repository Setup (15 minutes)

### 2.1 Initialize Git Repository
```bash
# Create project directory
mkdir my-project
cd my-project

# Initialize git
git init

# Create .gitignore IMMEDIATELY
```

### 2.2 Create Essential Files

- [ ] **`.gitignore`** (critical - do this FIRST!)
  ```gitignore
  # Environment variables
  .env
  .env.local
  .env.*.local

  # Dependencies
  node_modules/
  __pycache__/
  *.pyc
  venv/
  env/

  # IDE
  .vscode/
  .idea/
  *.swp
  *.swo

  # OS
  .DS_Store
  Thumbs.db

  # Database
  *.db
  *.sqlite
  *.sqlite3

  # Build outputs
  dist/
  build/
  .next/

  # Logs
  *.log
  logs/
  ```

- [ ] **`.env.example`** (document required variables)
  ```env
  # Database
  DATABASE_URL=postgresql://user:pass@host:5432/dbname

  # APIs
  API_KEY_NAME=get_from_provider_website

  # Application
  ENVIRONMENT=development
  DEBUG=true
  LOG_LEVEL=INFO
  ```

- [ ] **`README.md`** (basic template)
  ```markdown
  # Project Name

  Brief description

  ## Setup

  1. Clone repository
  2. Copy `.env.example` to `.env`
  3. Fill in environment variables
  4. Install dependencies
  5. Run migrations
  6. Start application

  ## Tech Stack

  - Backend: [Framework]
  - Frontend: [Framework]
  - Database: PostgreSQL
  - Deployment: Railway + Vercel
  ```

### 2.3 Set Up GitHub Repository
```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/username/project.git
git branch -M main
git add .gitignore .env.example README.md
git commit -m "Initial commit: Project structure"
git push -u origin main
```

---

## Phase 3: Backend Setup (30 minutes)

### 3.1 Python/FastAPI Project
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # For PostgreSQL
pydantic==2.5.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Create Project Structure
```bash
mkdir -p backend/{api/routes,database,services,tests}
touch backend/{__init__.py,main.py}
touch backend/api/__init__.py
touch backend/api/routes/__init__.py
touch backend/database/{__init__.py,connection.py,models.py}
touch backend/services/__init__.py
```

### 3.3 Set Up Database Connection (CRITICAL!)

**backend/database/connection.py:**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ✅ CORRECT - Load .env only if DATABASE_URL not already set
if not os.getenv('DATABASE_URL'):
    load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# For SQLite (development only)
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# For PostgreSQL (production)
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3.4 Set Up Database Models

**backend/database/models.py:**
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .connection import Base

class ExampleModel(Base):
    """
    Example model with best practices.
    """
    __tablename__ = "examples"

    # ✅ CORRECT - Works for both SQLite and PostgreSQL
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Data columns
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Always include timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### 3.5 Initialize Alembic (Database Migrations)
```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini - set sqlalchemy.url to use env var
# Edit alembic/env.py - import Base and configure
```

**alembic/env.py (important lines):**
```python
from backend.database.connection import Base
from backend.database import models  # Import all models

target_metadata = Base.metadata

# In run_migrations_online():
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
```

### 3.6 Create Main Application

**backend/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
if not os.getenv('DATABASE_URL'):
    load_dotenv()

app = FastAPI(
    title="Project API",
    description="API description",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend
        # Add production origins after deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### 3.7 Backend Checklist
- [ ] Virtual environment created and activated
- [ ] `requirements.txt` with pinned versions
- [ ] Database connection configured correctly
- [ ] Environment variables loaded conditionally
- [ ] Alembic initialized for migrations
- [ ] Health check endpoint exists
- [ ] CORS configured (localhost only for now)
- [ ] `.env` file created with DATABASE_URL
- [ ] Test: `python backend/main.py` runs without errors

---

## Phase 4: Frontend Setup (30 minutes)

### 4.1 Next.js Project
```bash
# Create Next.js app in frontend directory
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

cd frontend
```

### 4.2 Configure Environment Variables

**frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**frontend/.env.example:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4.3 Configure API Base URL

**frontend/lib/api.ts:**
```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API fetch error:', error);
    throw error;
  }
}
```

### 4.4 Test API Connection

**frontend/app/page.tsx:**
```typescript
'use client';

import { useEffect, useState } from 'react';
import { fetchAPI } from '@/lib/api';

export default function Home() {
  const [status, setStatus] = useState<string>('Loading...');

  useEffect(() => {
    fetchAPI('/health')
      .then((data) => setStatus(data.status))
      .catch(() => setStatus('Error connecting to API'));
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold">Project Name</h1>
      <p>API Status: {status}</p>
    </main>
  );
}
```

### 4.5 Frontend Checklist
- [ ] Next.js app created
- [ ] `.env.local` with API_URL
- [ ] `.env.example` documented
- [ ] API utility function created
- [ ] Test page connects to backend health endpoint
- [ ] Test: `npm run dev` works
- [ ] Test: Frontend shows "healthy" from backend

---

## Phase 5: Development Environment Verification (15 minutes)

### 5.1 Test Local Development
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
# Should show "API Status: healthy"
```

### 5.2 Create Test Endpoints

**backend/api/routes/test.py:**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.get("/config-check")
async def config_check():
    import os
    return {
        "database_url_set": bool(os.getenv('DATABASE_URL')),
        "environment": os.getenv('ENVIRONMENT', 'development'),
    }
```

**Add to main.py:**
```python
from api.routes import test
app.include_router(test.router, prefix="/api/test", tags=["test"])
```

### 5.3 Verification Checklist
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Frontend can call backend `/health`
- [ ] `/api/test/ping` returns "pong"
- [ ] `/api/test/config-check` shows correct environment
- [ ] No CORS errors in browser console
- [ ] Git status shows only tracked files (no .env, no venv)

---

## Phase 6: Database Setup (15 minutes)

### 6.1 Create First Migration
```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Review the generated migration file
# Make sure it looks correct

# Apply migration
alembic upgrade head
```

### 6.2 Verify Database
```bash
# For SQLite (local)
sqlite3 database.db ".tables"

# For PostgreSQL (will set up in deployment)
# Will verify after Railway setup
```

### 6.3 Database Checklist
- [ ] Alembic migration created
- [ ] Migration applied successfully
- [ ] Tables exist in database
- [ ] No errors in migration
- [ ] `.alembic/` directory in .gitignore

---

## Phase 7: Deployment Preparation (30 minutes)

### 7.1 Create Dockerfile for Backend

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start app
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 7.2 Configure Vercel for Frontend

**vercel.json (optional - prefer dashboard config):**
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

### 7.3 Document Deployment Settings

**DEPLOYMENT.md:**
```markdown
# Deployment Configuration

## Railway (Backend)

### Environment Variables:
- DATABASE_URL: (provided by Railway PostgreSQL)
- ENVIRONMENT: production
- LOG_LEVEL: INFO
- [Add your API keys here]

### Build:
- Dockerfile: Yes
- Auto-deploy: main branch

## Vercel (Frontend)

### Environment Variables:
- NEXT_PUBLIC_API_URL: https://your-backend.railway.app

### Build Settings:
- Framework: Next.js
- Root Directory: frontend/
- Build Command: npm run build
- Install Command: npm install
```

### 7.4 Deployment Prep Checklist
- [ ] Dockerfile created and tested locally
- [ ] All environment variables documented
- [ ] DEPLOYMENT.md created
- [ ] Railway account ready
- [ ] Vercel account ready
- [ ] GitHub repository pushed and up to date

---

## Phase 8: First Deployment (45 minutes)

### 8.1 Deploy Backend to Railway

1. [ ] Go to railway.app
2. [ ] Create new project
3. [ ] Connect GitHub repository
4. [ ] Add PostgreSQL database (Railway provides)
5. [ ] Set environment variables:
   - ENVIRONMENT=production
   - LOG_LEVEL=INFO
   - (DATABASE_URL auto-set by Railway)
6. [ ] Deploy and wait for build
7. [ ] Check logs for errors
8. [ ] Test: `curl https://your-app.railway.app/health`

### 8.2 Fix PostgreSQL Sequences (IMPORTANT!)

After first deployment with database:
```python
# Create diagnostic endpoint first
@router.post("/admin/fix-sequences")
async def fix_sequences(db: Session = Depends(get_db)):
    """Fix PostgreSQL sequences after data import"""
    from sqlalchemy import text

    tables = ['your_table_names']
    results = {}

    for table in tables:
        max_id = db.execute(text(f"SELECT MAX(id) FROM {table}")).scalar() or 0
        next_id = max_id + 1
        db.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH {next_id}"))
        results[table] = {"max_id": max_id, "next_id": next_id}

    db.commit()
    return results
```

### 8.3 Deploy Frontend to Vercel

1. [ ] Go to vercel.com
2. [ ] Import GitHub repository
3. [ ] Set Root Directory: `frontend/`
4. [ ] Set environment variables:
   - NEXT_PUBLIC_API_URL=https://your-app.railway.app
5. [ ] Deploy and wait for build
6. [ ] Test: Visit your-app.vercel.app

### 8.4 Update CORS for Production

**backend/main.py:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
        "https://*.vercel.app",  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.5 First Deployment Checklist
- [ ] Backend deployed to Railway
- [ ] Database created and migrations run
- [ ] PostgreSQL sequences fixed
- [ ] Frontend deployed to Vercel
- [ ] CORS updated for production domain
- [ ] Both deployments working
- [ ] Frontend can call backend API
- [ ] No console errors in browser

---

## Phase 9: Post-Deployment Verification (15 minutes)

### 9.1 Test Production Endpoints
```bash
# Backend health check
curl https://your-app.railway.app/health

# Frontend loads
curl -I https://your-app.vercel.app

# API connection works (check browser console)
# Visit https://your-app.vercel.app and verify API status
```

### 9.2 Set Up Monitoring

**Add to backend:**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log important events
logger = logging.getLogger(__name__)
logger.info("Application started")
```

### 9.3 Create Diagnostic Endpoints (CRITICAL!)

**backend/api/routes/diagnostics.py:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from sqlalchemy import text, inspect

router = APIRouter()

@router.get("/db-check")
async def check_database(db: Session = Depends(get_db)):
    """Check database connection and table status"""
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()

        return {
            "connected": True,
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.get("/env-check")
async def check_environment():
    """Check environment variables (sanitized)"""
    import os
    return {
        "environment": os.getenv('ENVIRONMENT'),
        "database_url_set": bool(os.getenv('DATABASE_URL')),
        "database_type": "postgresql" if os.getenv('DATABASE_URL', '').startswith('postgresql') else "sqlite"
    }
```

### 9.4 Post-Deployment Checklist
- [ ] All production URLs documented
- [ ] Logging configured
- [ ] Diagnostic endpoints created
- [ ] Health checks passing
- [ ] Database accessible
- [ ] Environment variables correct
- [ ] No errors in Railway logs
- [ ] No errors in Vercel logs
- [ ] Frontend loads correctly
- [ ] API calls working

---

## Phase 10: Documentation & Cleanup (15 minutes)

### 10.1 Update README.md

**README.md (complete version):**
```markdown
# Project Name

Description of project

## Tech Stack

- **Backend:** FastAPI + Python 3.9
- **Frontend:** Next.js 14 + TypeScript
- **Database:** PostgreSQL
- **Deployment:** Railway (backend) + Vercel (frontend)

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (or use SQLite for local dev)

### Setup

1. Clone repository:
   \`\`\`bash
   git clone https://github.com/username/project.git
   cd project
   \`\`\`

2. Backend setup:
   \`\`\`bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env
   # Edit .env and add your values

   # Run migrations
   alembic upgrade head

   # Start server
   python main.py
   \`\`\`

3. Frontend setup:
   \`\`\`bash
   cd frontend
   npm install

   # Copy environment file
   cp .env.example .env.local
   # Edit .env.local

   # Start dev server
   npm run dev
   \`\`\`

4. Visit http://localhost:3000

## Deployment

See DEPLOYMENT.md for full deployment instructions.

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

\`\`\`
project/
├── backend/
│   ├── api/routes/       # API endpoints
│   ├── database/         # Models and connection
│   ├── services/         # Business logic
│   └── main.py          # Application entry point
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   └── lib/             # Utilities
└── README.md
\`\`\`
```

### 10.2 Create Contributing Guide

**CONTRIBUTING.md:**
```markdown
# Contributing Guide

## Before Making Changes

1. Read BEST_PRACTICES_PRD.md
2. Check ERRORS_ENCOUNTERED.md for known issues
3. Create feature branch from main

## Development Workflow

1. Create branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test locally
4. Commit with descriptive message
5. Push and create PR
6. Wait for CI/CD checks

## Code Review Checklist

Reference BEST_PRACTICES_PRD.md during review.
```

### 10.3 Final Cleanup
- [ ] All secrets removed from code
- [ ] All TODO comments addressed
- [ ] All console.log / print statements removed (or appropriate)
- [ ] All test endpoints documented
- [ ] README.md complete
- [ ] CONTRIBUTING.md created
- [ ] All files committed to git
- [ ] .gitignore comprehensive

---

## ✅ Project Setup Complete!

If you've completed all phases:

✅ Local development environment works
✅ Git repository configured correctly
✅ Backend deployed to Railway
✅ Frontend deployed to Vercel
✅ Database migrations working
✅ Environment variables configured correctly
✅ CORS configured properly
✅ Diagnostic endpoints exist
✅ Documentation complete

**Next Steps:**
1. Start building features!
2. Reference BEST_PRACTICES_PRD.md during development
3. Add to ERRORS_ENCOUNTERED.md when you find issues
4. Keep documentation updated

**Estimated Prevention:**
Following this checklist prevents ~15 of the 23 documented errors (65% reduction in issues!)

---

## 🆘 Troubleshooting

**If something doesn't work:**

1. Check ERRORS_ENCOUNTERED.md for similar issues
2. Verify environment variables: `/api/test/config-check`
3. Check database connection: `/api/diagnostics/db-check`
4. Review Railway/Vercel logs
5. Ensure CORS is configured correctly
6. Verify PostgreSQL sequences after data import

---

**Document Version:** 1.0
**Last Updated:** 2025-10-31
**Based On:** 23 documented errors and 10+ hours of debugging
