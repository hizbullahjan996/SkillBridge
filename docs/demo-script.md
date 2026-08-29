# SkillBridge — Demo Script

**Duration:** 5-7 minutes | **Audience:** KPITB x UETM evaluators

---

## 1. Problem (30 seconds)

"University students in Pakistan often don't know:
- Which career fits their skills
- Which skills they're missing for their desired career
- What they should learn next
- Which jobs match their profile

Current career guidance is generic — not personalized to each student's actual skills and academic profile."

---

## 2. Solution (30 seconds)

"SkillBridge is an AI-powered platform that solves this. It takes a student's profile and skills, uses machine learning to recommend the top 3 career fields, connects those careers to real Pakistani job market data, identifies missing skills, and provides a personalized learning roadmap."

---

## 3. Student Profile (45 seconds)

**Show:** `/profile` page

"This is a student profile. Notice the academic details — CGPA, university year, major — and the soft skills section. The profile feeds directly into our ML model."

**Show:** `/skills` page

"Here are the student's technical skills with proficiency levels. Python, JavaScript, Docker — these are used for both career prediction and skill gap analysis."

---

## 4. AI Career Recommendation (60 seconds)

**Show:** Home page after generating recommendation

"Our ML model — a RandomForest classifier trained on 6,000 student profiles — analyzes 60 features and predicts the top 3 career fields."

**Highlight:**
- "Data Scientist — 45% probability"
- "Machine Learning Engineer — 21%"
- "AI Engineer — 12%"

"Each prediction includes a confidence score. The model achieves 89% accuracy with balanced performance across all 16 career classes."

---

## 5. Job Matching (60 seconds)

**Show:** `/jobs` page

"SkillBridge connects career recommendations to real Pakistani job market data. We have 10,500 job postings from Dataset 2."

**Show:** Job filtering by city, sector, job type

"Jobs are ranked by compatibility with the student's skills and experience. Each job shows a match score based on skill overlap, education level, and experience requirements."

---

## 6. Skill Gap (60 seconds)

**Show:** Skill gap analysis page

"This is where SkillBridge gets actionable. For each recommended career, we compare the student's current skills against what's required."

**Highlight:**
- "Matched skills: Python, JavaScript — student already has these"
- "Missing skills: Machine Learning, TensorFlow, PyTorch — these are critical"
- "Priority score: 85 — high demand in the job market"

"The priority score combines job market demand, career relevance, and learning difficulty."

---

## 7. Learning Roadmap (45 seconds)

**Show:** Learning roadmap page

"Based on skill gaps, SkillBridge generates a personalized learning roadmap with curated resources."

**Highlight:**
- "Machine Learning course from Kaggle — free, beginner level"
- "TensorFlow documentation — official resource"
- Progress tracking: "2 resources completed, 3 in progress"

"Students can track their learning progress directly in the platform."

---

## 8. AI Career Assistant (45 seconds)

**Show:** `/assistant` page

"Students can ask career questions in natural language. The AI assistant uses their actual SkillBridge data — not generic advice."

**Ask:** "What skills should I learn for data science?"

"The assistant references the student's actual profile, skill gaps, and learning roadmap to provide personalized guidance."

---

## 9. Admin Dashboard (45 seconds)

**Show:** `/admin` page

"For administrators — universities, career centers — we have a full analytics dashboard."

**Show:**
- KPI cards: "120 users, 85 students, 10,500 jobs, 41 skills"
- User management with search and role filtering
- Learning analytics: "67% completion rate"
- System health: "API healthy, database connected"

"All data comes from real database records — no fake data."

---

## 10. Closing (30 seconds)

"SkillBridge connects:
- Students to careers (via ML)
- Careers to jobs (via Pakistan job market data)
- Students to skills they need (via skill gap analysis)
- Students to what they should learn (via learning roadmap)
- Students to guidance (via AI assistant)

It's built with React, FastAPI, PostgreSQL, and Scikit-learn. It has 160 tests, 76% coverage, and is Docker-ready for deployment.

SkillBridge — bridging the gap between students and their careers."

---

## Technical Notes for Demo

- **Backend:** Run `uvicorn app.main:app --reload` on port 8000
- **Frontend:** Run `npm run dev` on port 5173
- **Database:** Ensure PostgreSQL is running with seeded data
- **ML Model:** Pre-loaded from `ml/models/`
- **If LLM unavailable:** AI assistant uses fallback responses (graceful degradation)
