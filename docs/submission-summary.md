# SkillBridge — Submission Summary

**KPITB x UETM Project Submission**

---

## 1. Project Title

**SkillBridge — AI-Powered Career Recommendation and Skill Gap Analysis Platform**

---

## 2. Problem

University students in Pakistan face a critical gap between their academic skills and career opportunities:

- **Students** don't know which career fits their skills
- **Skills** taught in universities don't always match industry demands
- **Career guidance** is generic, not personalized
- **Job market data** is scattered and not connected to skill development
- **Learning paths** are not tailored to individual skill gaps

---

## 3. Solution

SkillBridge provides an end-to-end personalized career guidance pipeline:

```
Student Profile + Skills
        |
        v
ML Career Recommendation (Top-3 Career Fields)
        |
        v
Career-to-Job Mapping (Pakistan Job Market)
        |
        v
Job Recommendations (Matched to Student Profile)
        |
        v
Skill Gap Analysis (Matched vs Required Skills)
        |
        v
Priority-Based Learning Roadmap
        |
        v
Learning Resources (Curated, Real URLs)
        |
        v
AI Career Assistant (Personalized Guidance)
```

---

## 4. Innovation

**What differentiates SkillBridge:**

1. **ML-powered predictions** — Not rule-based, but trained on 6,000 student profiles with 60 features across 16 career fields
2. **Pakistan-specific** — Job market data from Pakistani job portals, mapped to Pakistani career categories
3. **End-to-end pipeline** — From profile to career to jobs to skills to learning — all connected
4. **Skill gap with priority scoring** — Considers demand (job frequency), relevance (career importance), and learning difficulty
5. **AI Career Assistant** — Answers questions using the student's actual SkillBridge data, not generic advice
6. **Learning progress tracking** — Students can track their progress through recommended resources
7. **Admin analytics** — Real-time platform usage analytics for administrators

---

## 5. Technology

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| ML | Scikit-learn (RandomForestClassifier), Pandas, NumPy |
| AI Assistant | OpenAI / Ollama (configurable) |
| Auth | JWT (PyJWT), bcrypt (passlib) |
| Testing | Pytest (160 tests, 76% coverage) |
| DevOps | Docker, Docker Compose, Nginx |

---

## 6. Machine Learning

- **Algorithm:** RandomForestClassifier
- **Training data:** 6,000 synthetic student profiles
- **Features:** 60 (demographics, academic, skills, experience, soft skills)
- **Target:** Career_Field (16 classes)
- **Accuracy:** 89.17%
- **F1 (macro):** 89.26%
- **Top-3 predictions** with probability scores

---

## 7. Datasets

**Dataset 1:** Student Profile Dataset
- 6,000 student profiles
- 60 features (demographics, skills, academic, experience)
- 16 career field labels
- Used for ML model training

**Dataset 2:** Pakistan Job Market Dataset
- 10,500 job postings
- Fields: title, company, city, sector, salary, skills, experience
- Mapped to career categories via 200+ career-job mappings

**Learning Resources:** 30+ curated real resources
- Python.org, MDN, freeCodeCamp, Docker, AWS, Kaggle, etc.
- All URLs verified and functional

---

## 8. System Architecture

```
React SPA (Vite)
    |
    v
FastAPI Backend (Python)
    |
    +---> PostgreSQL Database
    +---> ML Model (Scikit-learn)
    +---> LLM API (OpenAI/Ollama)
```

- **Frontend:** Single-page application with 17 routes (6 student, 11 admin)
- **Backend:** 35+ REST API endpoints across 10 modules
- **ML:** Pre-trained model loaded on-demand, no retraining at startup
- **AI Assistant:** Context-aware, uses student's actual data for grounded responses

---

## 9. Target Users

- **University students** (undergraduate/graduate)
- **Fresh graduates** seeking career direction
- **Career changers** exploring new fields
- **Universities** wanting to track student career readiness

---

## 10. Impact

- Students receive **personalized** career recommendations based on their actual skills
- **Skill gaps** are identified with specific priority scores
- **Learning roadmaps** provide actionable next steps
- **Job matching** connects students to relevant Pakistani job opportunities
- **Admin analytics** help institutions understand student career patterns

---

## 11. Limitations

1. **Synthetic training data** — ML model trained on generated student profiles, not real university data
2. **Static job market** — Job data is imported from CSV, not live API feeds
3. **16 career fields** — Limited to predefined categories
4. **No real-time LLM** — AI assistant uses fallback responses if no LLM API key configured
5. **No user authentication persistence** — JWT tokens expire (configurable, default 60 min)
6. **No resume analysis** — Profile is manually entered
7. **No employer dashboard** — Students cannot connect directly with employers

---

## 12. Future Work

- Live job API integrations (LinkedIn, Indeed, Rozee.pk)
- Larger, real student dataset from Pakistani universities
- Resume upload and skill extraction
- Employer dashboard for posting and reviewing candidates
- More localized career categories for Pakistani market
- Mobile application (React Native)
- Peer comparison and benchmarking
- Skill assessment quizzes
- Internship recommendation engine
