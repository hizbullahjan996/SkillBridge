# SkillBridge — Final Project Audit

**Date:** 2026-08-23
**Phase:** 11 — Final QA

---

## Working Modules

| Module | Status | Notes |
|--------|--------|-------|
| Authentication (register/login/JWT) | Working | 100% test coverage on auth.py |
| Student Profile CRUD | Working | 92% coverage |
| Skills Management | Working | 94% coverage |
| ML Career Prediction | Working | 89.17% accuracy, 16 classes |
| Top-3 Career Recommendations | Working | Probabilities valid |
| Career-to-Job Mapping | Working | 200+ mappings in catalog |
| Job Listing & Search | Working | 98% coverage on jobs.py |
| Job Matching (by student skills) | Working | 46% service coverage |
| Skill Gap Analysis | Working | 99% service coverage |
| Learning Roadmap | Working | 82% service coverage |
| Learning Resources (search/recommend) | Working | 96% service coverage |
| Learning Progress Tracking | Working | Included in resource service |
| AI Career Assistant | Working | 76% service coverage, fallback LLM |
| Admin Dashboard Stats | Working | 91% admin service coverage |
| Admin User/Student Management | Working | Search, pagination, detail views |
| Admin Analytics (skills, careers, jobs) | Working | Real DB data |
| Admin Learning/AI Analytics | Working | Real DB data |
| Admin System Health | Working | API, DB, disk checks |
| Admin Audit Logging | Working | Indexed, filterable |
| Health Check Endpoints | Working | 100% coverage |
| Error Handling (global) | Working | Catches AppException, HTTP, unhandled |
| Structured Logging | Working | INFO/WARNING/ERROR levels |
| JWT (create/decode with sub fix) | Working | Fixed sub string conversion |
| Database Models (all 17) | Working | Proper constraints, indexes |
| Alembic Migrations | Partial | Only covers Phase 0-7 tables |
| Docker Compose | Configured | 3 services: db, backend, frontend |
| Backend Dockerfile | Working | Multi-stage, non-root, healthcheck |
| Frontend Dockerfile | Working | Multi-stage, nginx |

---

## Partially Working Modules

| Module | Issue |
|--------|-------|
| Alembic Migrations | Missing migrations for LearningResource, StudentLearningResource, AssistantConversation, AssistantMessage, AdminAuditLog models (6 tables) |
| ML Predictor Coverage | 27% test coverage — loads model and predicts but not well unit-tested |
| Career Prediction Service | 17% coverage — orchestrator logic not thoroughly tested |
| LLM Provider | 25% coverage — OpenAI/Ollama providers not tested (require live API) |
| Job Matching Service | 46% coverage — scoring logic partially tested |

---

## Broken Modules

| Module | Issue |
|--------|-------|
| None identified | All modules functional in test environment |

---

## Missing Configuration

| Item | Status |
|------|--------|
| `.env.example` | Present (38 lines) |
| `.env` | Not committed (correct) |
| Frontend `.env` | Not needed — uses proxy in dev, nginx in prod |
| ESLint config | Missing — `npm run lint` would fail |
| Frontend tests | Zero test files despite vitest being configured |

---

## Critical Issues

1. **Alembic migration gap**: 6 tables added in Phases 8-9 have no Alembic migration. Running `alembic upgrade head` on a fresh DB will not create: `learning_resources`, `learning_resource_skills`, `student_learning_resources`, `assistant_conversations`, `assistant_messages`, `admin_audit_logs`.

2. **ML model artifact path mismatch**: `config.py` defines `ml_model_path` pointing to `../ml/models/`, but `predictor.py` hardcodes `app/ml/artifacts/`. The model file exists at `ml/models/skillbridge_career_classifier.joblib` — the predictor path must resolve correctly at runtime.

---

## Non-Critical Issues

1. **11 unused frontend npm dependencies**: axios, Radix UI packages, lucide-react, recharts, CVA — installed but never imported.
2. **6 empty frontend scaffold directories**: components/, features/, hooks/, routes/, services/, types/.
3. **Zero frontend test files**: vitest configured but no tests exist.
4. **No ESLint configuration file**: lint script exists but config is missing.
5. **`public/` directory is empty**: favicon 404.
6. **Dead config key**: `ml_model_path` in config.py is never read by predictor.py.
7. **Minor**: `User.is_active == True` SQLAlchemy anti-pattern in admin_service.py line 96.

---

## Test Results

- **Total tests:** 160
- **Passed:** 160
- **Failed:** 0
- **Coverage:** 76%

### Coverage by Module

| Module | Coverage |
|--------|----------|
| auth.py | 100% |
| health.py | 100% |
| router.py | 100% |
| All schemas | 100% |
| skill_gap_service.py | 99% |
| learning_resource_service.py | 96% |
| admin_service.py | 91% |
| jwt.py | 90% |
| deps.py | 93% |
| config.py | 96% |
| assistant.py (API) | 65% |
| learning_resources.py (API) | 35% |
| ml/predictor.py | 27% |
| ml/feature_builder.py | 19% |
| services/llm_provider.py | 25% |
| services/career_prediction_service.py | 17% |
| services/career_job_mapping_service.py | 0% |
