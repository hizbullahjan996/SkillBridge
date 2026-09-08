# SkillBridge

**AI-Based Career Recommendation, Job Matching & Skill Gap Analysis**

SkillBridge helps university students in Pakistan discover suitable career paths based on their academic
profile, technical skills, soft skills, projects, certifications, and internships. After recommending
careers, the system connects those careers with relevant jobs from the Pakistani job market and identifies
missing skills.

---

## Problem Statement

University students in Pakistan face a critical gap between their academic skills and career opportunities:

- Students don't know which career fits their skills
- Skills taught in universities don't always match industry demands
- Career guidance is generic, not personalized to individual profiles
- Job market data is scattered and disconnected from skill development
- Learning paths are not tailored to individual skill gaps

SkillBridge solves this by providing an end-to-end personalized career guidance pipeline powered by machine learning and AI.

---

## Key Features

- **AI/ML Career Recommendation** — RandomForest classifier trained on 6,000 student profiles (89% accuracy)
- **Top-3 Career Prediction** — Ranked career fields with confidence probabilities
- **Pakistan Job Matching** — 2,884 job postings (from 10,500 cleaned) mapped across 16 career categories
- **Skill Gap Analysis** — Identifies matched vs missing skills with priority scoring
- **Personalized Learning Roadmap** — Ordered by demand, relevance, and difficulty
- **Learning Resources** — 28 curated real resources with progress tracking
- **AI Career Assistant** — Context-aware chat using student's actual SkillBridge data
- **Admin Dashboard** — Real-time analytics, user management, system health

---

## Architecture

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

## Tech Stack

| Layer      | Technology                                                  |
| ---------- | ----------------------------------------------------------- |
| Frontend   | React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts |
| Backend    | Python, FastAPI, SQLAlchemy, Alembic, Pydantic              |
| Database   | PostgreSQL                                                  |
| ML         | Scikit-learn, Pandas, NumPy, Joblib                         |
| Auth       | JWT (PyJWT), bcrypt (passlib)                               |
| Testing    | Vitest (FE), Pytest (BE)                                    |
| DevOps     | Docker, Docker Compose                                      |

## Project Structure

```
SkillBridge/
├── frontend/                 # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page-level components
│   │   ├── layouts/          # Layout wrappers
│   │   ├── features/         # Feature modules
│   │   ├── services/         # API service layer
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript type definitions
│   │   ├── lib/              # Utilities and helpers
│   │   └── routes/           # Route configuration
│   └── public/               # Static assets
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/           # API route handlers
│   │   ├── core/             # Config, security, DB connection
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic layer
│   │   ├── ml/               # ML integration (loader, predictor, feature builder)
│   │   │   └── artifacts/    # Trained model (.joblib) + metadata
│   │   └── utils/            # Helpers
│   ├── scripts/              # Seed/import/maintenance scripts
│   ├── tests/                # Backend tests (165 passing)
│   └── alembic/              # Database migrations
├── ml/                       # Machine Learning workspace (notebooks, data)
│   ├── notebooks/            # Jupyter notebooks (EDA, preprocessing)
│   └── data/                 # ML-specific data artifacts
├── data/                     # Datasets (CSV files)
├── docs/                     # Documentation
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Datasets

| File | Description | Records |
|------|-------------|---------|
| `Dataset_1_Cleaned.csv` | Student profiles with 40+ skills and career labels | 6,000 |
| `Dataset_2_Cleaned.csv` | Pakistan job market postings (cleaned) | 10,500 |
| `career_job_mapping_candidates.csv` | Career field to job title mapping | 200 |
| `skill_mapping_review.csv` | Skill matching review between datasets | 211 |

After seeding, the live PostgreSQL database contains:

| Table | Rows |
|-------|------|
| `skills` | 212 |
| `careers` | 16 |
| `jobs` | 2,884 |
| `job_skills` | 15,849 |
| `career_job_mappings` | 45,936 (~99.6% job coverage) |
| `learning_resources` | 28 |

## Getting Started

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14
- Docker & Docker Compose (optional)

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your actual values
```

### Database Setup

1. Install PostgreSQL and create a database:

```sql
CREATE DATABASE skillbridge;
```

2. Configure `.env` with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/skillbridge
```

3. Install backend dependencies:

```bash
cd backend
pip install -e .
```

4. Run database migrations:

```bash
alembic upgrade head
```

5. (Optional) Seed initial data from datasets:

```bash
python -m scripts.seed_skills
python -m scripts.seed_careers
python -m scripts.import_jobs
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload
```

The API will be available at:

```
http://localhost:8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
OpenAPI:     http://localhost:8000/openapi.json
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build -d
```

The full stack is then available at `http://localhost` (frontend via Nginx on port 80, which proxies `/api` to the FastAPI backend). The backend API is also directly reachable at `http://localhost:8000`.

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Conventions

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

**Base URL:** `/api`

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Application health check |
| `/api/health/db` | GET | Database connectivity check |
| `/api/auth/register` | POST | Register a new student account |
| `/api/auth/login` | POST | Login and receive JWT token |
| `/api/auth/me` | GET | Get current authenticated user |
| `/api/students/me` | GET | Get current student profile |
| `/api/students/me` | PUT | Update current student profile |
| `/api/students/me/profile-completion` | GET | Get profile completion percentage |
| `/api/students/me/ml-readiness` | GET | Check if profile is ready for ML prediction |
| `/api/students/me/skills` | GET | Get current student's skills |
| `/api/skills` | GET | Get all available skills (filter by category/search) |
| `/api/skills/me` | POST | Add a skill to current student |
| `/api/skills/me/{skill_id}` | DELETE | Remove a skill from current student |
| `/api/recommendations/careers` | POST | Get career recommendations |
| `/api/recommendations/careers/history` | GET | Get recommendation history |
| `/api/recommendations/careers/latest` | GET | Get latest recommendations |
| `/api/jobs` | GET | List available jobs |
| `/api/jobs/{job_id}` | GET | Get job details |
| `/api/recommendations/jobs` | GET | Get job recommendations |
| `/api/skill-gaps/career/{career_id}` | GET | Get skill gap for career |
| `/api/skill-gaps/job/{job_id}` | GET | Get skill gap for job |
| `/api/learning-roadmap` | GET | Get personalized learning roadmap |
| `/api/learning-resources` | GET | Search learning resources |
| `/api/learning-resources/{id}` | GET | Get resource details |
| `/api/learning-resources/recommended` | GET | Get recommended resources |
| `/api/learning-progress` | GET/POST | Track learning progress |
| `/api/learning-progress/{resource_id}` | PUT | Update progress |
| `/api/learning-roadmap/with-resources` | GET | Roadmap with resources |
| `/api/assistant/chat` | POST | Chat with AI assistant |
| `/api/assistant/conversations` | GET | List conversations |
| `/api/assistant/conversations/{id}` | GET/DELETE | Manage conversation |

### Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Get a token by registering or logging in via `/api/auth/register` or `/api/auth/login`.

### Profile Endpoints

**Get Profile:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/students/me
```

**Update Profile:**
```bash
curl -X PUT http://localhost:8000/api/students/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"age": 22, "cgpa": 3.8, "interest_domain": "Software Development"}'
```

**Get Profile Completion:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/students/me/profile-completion
```

**Check ML Readiness:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/students/me/ml-readiness
```

### Skills Endpoints

**List All Skills:**
```bash
curl http://localhost:8000/api/skills
curl http://localhost:8000/api/skills?category=technical
curl http://localhost:8000/api/skills?search=python
```

**Add Skill:**
```bash
curl -X POST http://localhost:8000/api/skills/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_id": 1, "proficiency": 8}'
```

**Remove Skill:**
```bash
curl -X DELETE http://localhost:8000/api/skills/me/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Development Phases

1. **Phase 0** — Architecture *(completed)*
2. **Phase 1** — Database (SQLAlchemy + Alembic) *(completed)*
3. **Phase 2** — Backend Foundation (FastAPI + config) *(completed)*
4. **Phase 3** — Authentication (JWT + roles) *(completed)*
5. **Phase 4** — Student Profile & Skills Management *(completed)*
6. **Phase 5** — ML Integration *(completed)*
7. **Phase 6** — Career Recommendation *(completed)*
8. **Phase 7** — Skill Gap Analysis & Learning Roadmap *(completed)*
9. **Phase 8** — Learning Resources & AI Career Assistant *(completed)*
10. **Phase 9** — Admin Dashboard, Analytics & System Management *(completed)*
11. **Phase 10** — Production Readiness, Testing, Docker & Deployment *(completed)*

## Phase 8 — Learning Resources & AI Career Assistant

### Learning Resources

The system provides real, curated learning resources for missing skills:

```
Missing Skill → Relevant Resources → Learning Progress
```

**Curated Catalog:**
- 28 real, verified learning resources
- Providers: Python.org, MDN, freeCodeCamp, Docker, AWS, Kaggle, Scikit-learn, etc.
- All URLs are real and verified
- Resource types: course, documentation, tutorial, book

**Resource Ranking Formula:**
```
Resource Score = Skill Priority × 60
              + Free Bonus (20 if free)
              + Difficulty Bonus (10 beginner, 5 intermediate)
```

### AI Career Assistant

The AI assistant answers questions about career recommendations, skill gaps, and learning roadmaps using the student's actual SkillBridge data.

```
Student Question
       ↓
SkillBridge Context (profile, skills, careers, gaps, roadmap)
       ↓
LLM Provider (OpenAI / Ollama / Fallback)
       ↓
Grounded Response
```

**Hallucination Controls:**
- Never fabricates jobs, skills, salaries, courses, or URLs
- Clearly distinguishes SkillBridge data from general advice
- Returns safe fallbacks when data is missing
- Validates responses for length and sensitive content

**Environment Variables:**
```env
LLM_PROVIDER=openai       # or "ollama"
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your-api-key  # do not commit real keys
LLM_BASE_URL=             # optional custom URL
```

### New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/learning-resources` | GET | Search and filter learning resources |
| `/api/learning-resources/{id}` | GET | Get resource details |
| `/api/learning-resources/recommended` | GET | Personalized resource recommendations |
| `/api/learning-progress` | GET | Get student learning progress |
| `/api/learning-progress` | POST | Start tracking a resource |
| `/api/learning-progress/{resource_id}` | PUT | Update resource progress |
| `/api/learning-roadmap/with-resources` | GET | Roadmap with integrated resources |
| `/api/assistant/chat` | POST | Chat with AI career assistant |
| `/api/assistant/conversations` | GET | List conversation history |
| `/api/assistant/conversations/{id}` | GET | Get conversation messages |
| `/api/assistant/conversations/{id}` | DELETE | Delete a conversation |

### Import Learning Resources

```bash
cd backend
python scripts/import_learning_resources.py
```

## Phase 9 — Admin Dashboard, Analytics & System Management

Full admin panel for monitoring platform usage, managing users/content, and system health checks.

### Admin Features

```
Admin Dashboard → User/Student Management → Analytics → System Health → Audit Logs
```

**Dashboard Stats:**
- Total users, students, jobs, skills, resources (all from live DB)
- Users by role breakdown

**User & Student Management:**
- Paginated user/student lists with search and filters
- User detail view (profile, skills, recent activity)
- Admin audit logging for all management actions

**Analytics:**
- Skill analytics (student counts, demand mapping)
- Career analytics (student counts, job mapping)
- Job analytics (city distribution, sector breakdown, top skills)
- Learning analytics (resource usage, completion rates, popular resources)
- AI assistant analytics (conversation/message counts, active users)

**System Health:**
- API, Database, ML model, and disk space status checks

### Admin API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/dashboard` | GET | Dashboard statistics |
| `/api/admin/users` | GET | List users (search, filter by role, pagination) |
| `/api/admin/users/{id}` | GET | User detail with profile |
| `/api/admin/students` | GET | List students with search/pagination |
| `/api/admin/students/{id}` | GET | Student detail with skills |
| `/api/admin/skills` | GET | Skill analytics |
| `/api/admin/careers` | GET | Career analytics |
| `/api/admin/jobs` | GET | Job analytics (cities, sectors, skills) |
| `/api/admin/resources` | GET | Learning resource management |
| `/api/admin/learning` | GET | Learning progress analytics |
| `/api/admin/ai` | GET | AI assistant analytics |
| `/api/admin/system/health` | GET | System health checks |
| `/api/admin/audit` | GET | Audit log history |

**Access Control:** All admin endpoints require `role=admin`. Students receive 403; unauthenticated requests receive 401.

### Frontend Pages

| Route | Component |
|-------|-----------|
| `/student/login` | LoginPage |
| `/student/register` | RegisterPage |
| `/admin/login` | LoginPage (admin mode) |
| `/profile` | ProfilePage |
| `/profile/edit` | EditProfilePage |
| `/skills` | SkillsPage |
| `/careers` | CareersPage |
| `/jobs` | JobsPage |
| `/skill-gap` | SkillGapPage (falls back to top recommended career) |
| `/skill-gap/:careerName` | SkillGapPage (career-specific) |
| `/learning-resources` | LearningResourcesPage |
| `/assistant` | AssistantPage |
| `/admin` | AdminDashboardPage (8 KPI cards) |
| `/admin/users` | AdminUsersPage (search, filter, pagination) |
| `/admin/students` | AdminStudentsPage (student table) |
| `/admin/skills` | AdminSkillsPage (skill analytics) |
| `/admin/careers` | AdminCareersPage (career analytics) |
| `/admin/jobs` | AdminJobsPage (city/sector/skill analytics) |
| `/admin/resources` | AdminResourcesPage (resource management) |
| `/admin/learning` | AdminLearningPage (progress KPIs + popular resources) |
| `/admin/ai` | AdminAIPage (AI assistant metrics) |
| `/admin/system` | AdminSystemPage (health status) |
| `/admin/audit` | AdminAuditPage (audit log table) |

## Phase 10 — Production Readiness, Testing, Docker & Deployment

Stabilization phase: security hardening, testing, Docker, and deployment preparation.

### Test Results

| Metric | Value |
|--------|-------|
| Total tests | 165 |
| Passed | 165 |
| Coverage | 76% |

### End-to-End Regression Tests

`backend/tests/test_career_recommendation_flow.py` exercises the full pipeline against the **real trained model**
(no fixtures/mocks) and validates the persisted end-to-end flow:

1. Predicting careers persists 3 ranked `CareerRecommendation` rows with `ready=true` and `model_version=1.0.0`
2. Retrieving the latest recommendations returns the freshly predicted careers in order
3. Job recommendations return ranked jobs with `match_score`, `career_score`, and `in_top_career`
4. Skill gap analysis returns both matched and missing skills for the recommended career
5. Learning recommendations return relevant resources ordered by skill priority

Verified by walking through the flow for a real student profile: predict → latest → jobs → skill-gap → learning.

### Security & Bug Fixes

- Password strength validation (8+ chars, uppercase, lowercase, digit)
- Default SECRET_KEY rejected in production
- Swagger/ReDoc disabled in production
- Unused passlib dependency removed
- Dead code in admin analytics removed
- Bug in learning resource import fixed
- **ML model path fixed** — now resolves to `app/ml/artifacts/skillbridge_career_classifier.joblib` (the stale
  `../ml/models/...` default broke model loading and the admin health check)
- **Skill Gap page blank-screen fix** — `/skill-gap` now matches its own route (sidebar link hid behind the
  `/skill-gap/:careerName` pattern); `SkillGapPage` falls back to the student's top recommended career when no
  career name is supplied
- **Readable API errors** — FastAPI 422 validation messages are extracted from the `detail[]` array instead of
  rendering as `[object Object]`
- **N+1 query optimization** — precomputed caches in `career_job_mapping_service` and `job_matching_service`
  eliminate repeated per-row DB queries during job matching / mapping generation
- **Feature normalization fix** — `feature_builder` now emits the same column names the trained model expects
  (e.g. `Skill_Node.js`, `Skill_REST_APIs`)

### Docker

```bash
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

The stack consists of three services:

| Service | Container | Port | Notes |
|---------|-----------|------|-------|
| PostgreSQL | `skillbridge-db` | 5432 | Postgres 16, healthchecked |
| Backend API | `skillbridge-backend` | 8000 | FastAPI + Gunicorn (4 workers), healthchecked |
| Frontend | `skillbridge-frontend` | 80 | Nginx serving the React SPA; proxies `/api` to the backend |

The **frontend container** does triple duty — it serves the compiled SPA, acts as a reverse proxy for API
requests (`location /api → backend:8000`), and provides deep-link support via SPA fallback
(`try_files $uri $uri/ /index.html`), so routes like `/careers` and `/skill-gap` work on refresh.

> **Note:** `.dockerignore` files are required in both `backend/` and `frontend/` build contexts — without them,
> locked/sensitive files (e.g. `.pytest_cache`) break the image build on Windows.

### Creating an Admin User

```bash
docker compose exec backend python -m scripts.create_admin
```

The default admin used in testing and the E2E walkthrough is `admin@skillbridge.com` (login at `/admin/login`).

### Quick Start

```bash
# Backend
cd backend && python -m venv .venv && pip install -e ".[dev]"
cp ..\\.env.example .env && alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

### Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) — Full deployment guide
- [docs/architecture.md](docs/architecture.md) — System architecture
- [docs/production-readiness.md](docs/production-readiness.md) — Quality report
- [docs/final-audit.md](docs/final-audit.md) — Complete project audit
- [docs/api-test-results.md](docs/api-test-results.md) — API test matrix
- [docs/ml-validation.md](docs/ml-validation.md) — ML model validation
- [docs/deployment-checklist.md](docs/deployment-checklist.md) — Deployment steps
- [docs/submission-summary.md](docs/submission-summary.md) — KPITB x UETM submission
- [docs/demo-script.md](docs/demo-script.md) — Demo script
- [docs/final-checklist.md](docs/final-checklist.md) — Final checklist

## Limitations

1. **Synthetic training data** — ML model trained on generated student profiles, not real university records
2. **Static job market** — Job data imported from CSV, not live API feeds (Rozee.pk, LinkedIn)
3. **16 career fields** — Limited to predefined categories from the training dataset
4. **No resume analysis** — Student profiles are manually entered
5. **No employer dashboard** — Students cannot connect directly with employers
6. **LLM dependency** — AI assistant requires external API key; uses fallback responses otherwise
7. **Free-tier hosting constraints** — Cold starts on Render, compute limits on Neon

## Future Improvements

- Live job API integrations (LinkedIn, Indeed, Rozee.pk)
- Larger, real student dataset from Pakistani universities
- Resume upload and automatic skill extraction
- Employer dashboard for posting jobs and reviewing candidates
- More localized career categories for the Pakistani market
- Mobile application (React Native)
- Peer comparison and benchmarking
- Skill assessment quizzes
- Internship recommendation engine
- Real-time job market trend analysis

## License

This project is for educational purposes (KPITB x UETM). 
