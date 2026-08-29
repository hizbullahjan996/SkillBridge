# SkillBridge Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or use Docker)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -e ".[dev]"

# Create .env from template
cp ..\\.env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Run migrations
alembic upgrade head

# Seed data (optional)
python -m scripts.seed_skills
python -m scripts.seed_careers
python -m scripts.import_jobs
python -m scripts.import_learning_resources

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173 and proxies /api to localhost:8000.

### Create Admin User

```bash
cd backend
python -m scripts.create_admin
```

---

## Docker (Recommended)

### Quick Start

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env (set SECRET_KEY, DATABASE_URL, etc.)

# Build and start all services
docker compose up --build -d

# Run migrations
docker compose exec backend alembic upgrade head

# Seed data
docker compose exec backend python -m scripts.seed_skills
docker compose exec backend python -m scripts.seed_careers
docker compose exec backend python -m scripts.import_jobs
docker compose exec backend python -m scripts.import_learning_resources

# Create admin
docker compose exec backend python -m scripts.create_admin
```

### Services

| Service    | Port  | Description         |
|------------|-------|---------------------|
| frontend   | 80    | React SPA (nginx)   |
| backend    | 8000  | FastAPI (gunicorn)  |
| db         | 5432  | PostgreSQL 16       |

### Useful Commands

```bash
docker compose logs backend          # View backend logs
docker compose logs -f               # Follow all logs
docker compose down                  # Stop services
docker compose down -v               # Stop and remove volumes
docker compose exec backend pytest   # Run tests
```

---

## Production Deployment

### Recommended Architecture

```
Internet
   |
   v
Frontend (Vercel/Netlify/Cloudflare Pages)
   |
   v
Backend (Render/Railway)
   |
   +---> PostgreSQL (Neon/Supabase)
   +---> LLM API (OpenAI)
```

### Backend (Render/Railway)

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `cd backend && pip install -e .`
4. Set start command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. Set environment variables:
   - `APP_ENV=production`
   - `SECRET_KEY=<generate a random key>`
   - `DATABASE_URL=<your PostgreSQL URL>`
   - `CORS_ORIGINS=["https://your-frontend.vercel.app"]`
   - `LLM_PROVIDER=openai`
   - `LLM_API_KEY=<your API key>`

### Frontend (Vercel)

1. Import your GitHub repository
2. Framework: Vite
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variable: `VITE_API_BASE_URL=https://your-backend.onrender.com/api`

### Database (Neon/Supabase)

1. Create a free PostgreSQL database
2. Copy the connection string to `DATABASE_URL`
3. Run migrations: `alembic upgrade head`
4. Import data using the seed scripts

---

## Environment Variables

| Variable                  | Required | Default         | Description                    |
|---------------------------|----------|-----------------|--------------------------------|
| `APP_ENV`                 | No       | `development`   | `development` or `production`  |
| `SECRET_KEY`              | Yes*     | (insecure default) | JWT signing key             |
| `DATABASE_URL`            | Yes      | (local pg)      | PostgreSQL connection string   |
| `CORS_ORIGINS`            | No       | localhost:5173  | JSON array of allowed origins  |
| `LLM_PROVIDER`            | No       | `openai`        | `openai`, `ollama`, or omit    |
| `LLM_MODEL`               | No       | `gpt-4o-mini`   | LLM model name                |
| `LLM_API_KEY`             | No       | (empty)         | LLM API key                   |

*Required in production. Default value is rejected when `APP_ENV=production`.

---

## Database Backup

### PostgreSQL Backup

```bash
pg_dump -U postgres -d skillbridge > backup.sql
```

### PostgreSQL Restore

```bash
psql -U postgres -d skillbridge < backup.sql
```

### Docker Backup

```bash
docker compose exec db pg_dump -U postgres skillbridge > backup.sql
```

---

## Data Import Process

```
Dataset_1_Cleaned.csv
   |
   +--> python -m scripts.seed_skills      (41 skills)
   +--> python -m scripts.seed_careers     (16 careers)
   +--> [Train ML model offline]           (save to ml/models/)

Dataset_2_Cleaned.csv
   |
   +--> python -m scripts.import_jobs      (~10,500 jobs)

learning_resources_catalog.py
   |
   +--> python -m scripts.import_learning_resources  (30+ resources)
```

The ML model is pre-trained and shipped as a `.joblib` artifact. It is NOT retrained on application startup.
