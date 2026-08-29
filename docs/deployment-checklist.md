# SkillBridge — Deployment Checklist

**Date:** 2026-08-23 | **Phase:** 11

---

## Deployment Architecture

```
Internet
   |
   v
Frontend (Static Hosting: Vercel/Netlify)
   |
   v
Backend (FastAPI Hosting: Render/Railway)
   |
   +---> PostgreSQL (Neon/Supabase)
   +---> LLM API (OpenAI - optional)
```

---

## 1. Frontend Build Configuration

- **Framework:** Vite + React 18 + TypeScript
- **Build command:** `cd frontend && npm install && npm run build`
- **Output directory:** `frontend/dist`
- **Dev proxy:** `/api` -> `http://localhost:8000` (Vite dev server)
- **Production:** Nginx reverse proxy in Docker, or SPA with API base URL env var

## 2. Backend Start Command

```bash
# Development
cd backend && uvicorn app.main:app --reload --port 8000

# Production (Docker / Render)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
```

## 3. Environment Variable Checklist

| Variable | Required | Production Value |
|----------|----------|-----------------|
| `APP_ENV` | Yes | `production` |
| `SECRET_KEY` | Yes | Generate random 64+ char string |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `CORS_ORIGINS` | Yes | `["https://your-frontend.vercel.app"]` |
| `LLM_PROVIDER` | No | `openai` or omit for fallback |
| `LLM_API_KEY` | No | Your OpenAI API key |
| `LLM_MODEL` | No | `gpt-4o-mini` |

## 4. Database Migration Procedure

```bash
# 1. Set DATABASE_URL in .env
# 2. Run migrations
alembic upgrade head
# 3. Verify tables created
```

**Note:** Current Alembic migrations cover tables up to Phase 7. Tables from Phases 8-9 (learning_resources, assistant, admin_audit_logs) need manual creation or a new migration.

## 5. Dataset Import Procedure

```bash
# Skills and Careers (required for ML predictions)
python -m scripts.seed_skills
python -m scripts.seed_careers

# Jobs (Dataset 2)
python -m scripts.import_jobs

# Learning Resources
python -m scripts.import_learning_resources
```

## 6. ML Model Artifact Handling

- **Model file:** `ml/models/skillbridge_career_classifier.joblib`
- **Metadata:** `ml/models/model_metadata.json`
- **Loaded by:** `backend/app/ml/predictor.py` on first prediction request
- **Not retrained** on application startup
- Include `ml/models/` in deployment (not gitignored at artifact level)

## 7. Initial Admin Creation

```bash
cd backend
python -m scripts.create_admin
```

Prompts for email and password. Password is bcrypt-hashed.

## 8. CORS Production Configuration

```env
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

Never use `["*"]` with credentials in production.

## 9. Database Backup

```bash
# Backup
pg_dump -U postgres -d skillbridge > backup.sql

# Restore
psql -U postgres -d skillbridge < backup.sql

# Docker backup
docker compose exec db pg_dump -U postgres skillbridge > backup.sql
```

## 10. Free Tier Hosting Options

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Frontend | Vercel | Netlify, Cloudflare Pages |
| Backend | Render | Railway |
| Database | Neon | Supabase |

**Limits to be aware of:**
- Render free tier spins down after inactivity (cold start ~30s)
- Neon free tier has compute hour limits
- Vercel free tier has bandwidth limits
