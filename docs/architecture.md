# SkillBridge Architecture

## System Overview

```
                     SkillBridge
                         |
               +---------+---------+
               |                   |
           Frontend             Backend
           React (Vite)         FastAPI
               |                   |
               |             +-----+------+
               |             |            |
               |         PostgreSQL      ML
               |             |          Engine
               |             |            |
               +--------- REST API -------+
```

## Technology Stack

| Layer      | Technology                                                  |
| ---------- | ----------------------------------------------------------- |
| Frontend   | React 18, TypeScript, Vite, Tailwind CSS, Recharts         |
| Backend    | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2          |
| Database   | PostgreSQL 16 (SQLite for tests)                            |
| ML         | Scikit-learn (RandomForestClassifier), Pandas, NumPy        |
| Auth       | JWT (python-jose), bcrypt                                   |
| AI         | OpenAI API (configurable provider)                          |
| Testing    | Vitest (FE), Pytest + coverage (BE)                         |
| Deployment | Docker, Docker Compose, Gunicorn                            |

## Backend Structure

```
backend/
  app/
    api/
      deps.py              # Auth dependencies
      router.py            # Central API router
      v1/
        auth.py            # Register, login, current user
        students.py        # Student profile CRUD
        skills.py          # Skill catalog + management
        recommendations.py # Career predictions
        jobs.py            # Job listing + matching
        skill_gaps.py      # Gap analysis + learning roadmap
        learning_resources.py  # Resource search + progress
        assistant.py       # AI career assistant
        admin.py           # Admin dashboard + analytics
    models/                # SQLAlchemy models (17 tables)
    schemas/               # Pydantic request/response schemas
    services/              # Business logic
    core/                  # Config, security, JWT, DB, logging
    ml/                    # ML predictor + feature builder
    main.py                # FastAPI app factory
  scripts/                 # Data import + admin creation
  tests/                   # Pytest test suite
  alembic/                 # Database migrations
```

## Frontend Structure

```
frontend/
  src/
    App.tsx                # Route definitions
    main.tsx               # Entry point
    layouts/
      AdminLayout.tsx      # Admin sidebar layout
    lib/
      api.ts               # Typed API client
      client.ts            # HTTP client (fetch wrapper)
    pages/
      ProfilePage.tsx      # Student profile
      EditProfilePage.tsx  # Profile editor
      SkillsPage.tsx       # Skill management
      LearningResourcesPage.tsx  # Resource browser
      AssistantPage.tsx    # AI chat interface
      admin/               # 11 admin pages
```

## Data Flow

### Student Journey

```
Register/Login
      |
Complete Profile (14 fields)
      |
Add Skills (proficiency 0-10)
      |
POST /api/recommendations/careers
      |
      +--> ML Model (RandomForest)
      |      |
      |      +--> Top-3 Career Predictions
      |
GET /api/recommendations/jobs
      |
      +--> Job Matching Service
             |
             +--> Career compatibility (0.35)
             +--> Skill match (0.30)
             +--> Education match (0.20)
             +--> Experience match (0.15)
             |
             +--> Ranked job list with scores

GET /api/skill-gaps/career/{id}
      |
      +--> Gap Analysis
             |
             +--> Matched skills
             +--> Missing skills (with priority)
             +--> Match percentage

GET /api/learning-roadmap/career/{id}
      |
      +--> Learning Roadmap
             |
             +--> Prioritized skills to learn
             +--> Recommended resources per skill
```

### Admin Journey

```
Admin Login (role=admin)
      |
GET /api/admin/dashboard
      |
      +--> Platform stats (users, students, jobs, skills, resources)

Various analytics endpoints:
  /api/admin/users       -- User management
  /api/admin/students    -- Student management
  /api/admin/skills      -- Skill analytics
  /api/admin/careers     -- Career analytics
  /api/admin/jobs        -- Job market analytics
  /api/admin/learning    -- Learning progress analytics
  /api/admin/ai          -- AI assistant analytics
  /api/admin/system/health  -- System health checks
  /api/admin/audit       -- Audit logs
```

## ML Pipeline

### Model

- **Algorithm:** RandomForestClassifier (scikit-learn)
- **Features:** 60 (14 profile + 5 engineered + 41 skill columns)
- **Target:** Career_Field (16 classes)
- **Accuracy:** 89.2% | **Macro F1:** 89.3%

### Inference Pipeline

```
Student Profile + Skills
         |
Feature Builder (60 features)
         |
Label Encoder (categorical features)
         |
RandomForest.predict_proba()
         |
Top-3 Career Predictions + Probabilities
```

### Key Design Decisions

1. **Pre-trained model shipped as artifact** - No retraining on startup
2. **Singleton model loader** - Model loaded once, reused across requests
3. **Unknown categories handled** - Assigned -1 encoding (logged)
4. **No data leakage** - Features use only student-provided information

## Security Architecture

### Authentication

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 30-minute expiration
- `sub` claim contains user ID (integer)
- No refresh tokens (re-login required)

### Authorization

- Two roles: `student`, `admin`
- Backend enforces role checks via `require_role()` dependency
- Admin endpoints require `role=admin`
- Student endpoints require authentication
- Public endpoints: `/api/health`, `/api/jobs`, `/api/skills`

### Input Validation

- Pydantic schemas validate all request bodies
- Password: minimum 8 chars, uppercase, lowercase, digit
- Email: validated via Pydantic EmailStr
- IDs: validated as integers
- Pagination: bounded page/page_size

### SQL Safety

- All queries use SQLAlchemy ORM (parameterized)
- No raw SQL string concatenation
- Search uses `ilike` with parameterized patterns

### XSS Protection

- React escapes all rendered content by default
- No `dangerouslySetInnerHTML` usage
- AI assistant responses rendered as plain text

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

### Docker Stack

```
docker-compose.yml
   |
   +---> db (PostgreSQL 16 Alpine)
   +---> backend (Python 3.12 + Gunicorn)
   +---> frontend (Node 20 build + Nginx)
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `CORS_ORIGINS` | JSON array of allowed origins |
| `LLM_PROVIDER` | `openai`, `ollama`, or omit for fallback |
| `LLM_API_KEY` | OpenAI API key |
| `APP_ENV` | `development` or `production` |
