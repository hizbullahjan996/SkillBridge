# SkillBridge — ML Model Validation Report

**Date:** 2026-08-23
**Phase:** 11 — Final QA

---

## Model Overview

| Property | Value |
|----------|-------|
| Model Name | SkillBridge Career Classifier |
| Version | 1.0.0 |
| Algorithm | RandomForestClassifier |
| Training Dataset | Dataset_1_Cleaned.csv |
| Training Samples | 6,000 |
| Features | 60 |
| Target | Career_Field |
| Classes | 16 |

---

## 16 Career Classes

1. AI Engineer
2. Automation Engineer
3. Backend Developer
4. Business Analyst
5. Cloud Engineer
6. Cybersecurity Analyst
7. Data Analyst
8. Data Scientist
9. DevOps Engineer
10. Embedded Systems Engineer
11. Full Stack Developer
12. IT Support Engineer
13. Machine Learning Engineer
14. Penetration Tester
15. SOC Analyst
16. Software Engineer

---

## Model Metrics (from model_metadata.json)

| Metric | Value |
|--------|-------|
| Accuracy | 89.17% |
| F1 (macro) | 89.26% |
| F1 (weighted) | 89.00% |
| CV Accuracy (mean) | 88.94% |
| CV Accuracy (std) | 0.91% |

---

## Feature Pipeline

### Feature Columns (60 total)

**Demographics (4):** Age, Gender, University_Year, Major

**Academic (4):** CGPA, Attendance_Percentage, Study_Hours_Per_Week, Projects_Completed

**Experience (3):** Certifications_Count, Internships, total experience score

**Soft Skills (3):** Communication_Skills, Teamwork, Problem_Solving

**Interest (1):** Interest_Domain

**Derived (4):** Total_Skills, Average_Skill_Level, Experience_Score, Soft_Skill_Score, Academic_Strength

**Skill Binary Features (41):** Skill_AWS, Skill_Python, Skill_JavaScript, Skill_Docker, etc.

### Categorical Encoding

4 categorical columns: Gender, University_Year, Major, Interest_Domain — LabelEncoded during training, with unseen values mapped to -1.

---

## Preprocessing Consistency

| Step | Training | Inference | Match |
|------|----------|-----------|-------|
| Feature columns | 60 columns | Same 60 columns from model artifact | Yes |
| Feature ordering | Stored in `feature_columns` | Iterates `self.feature_columns` | Yes |
| Categorical encoding | LabelEncoder fitted on train | Same encoders from artifact | Yes |
| Skill features | Binary 0/1 | Binary 0/1 | Yes |
| Missing features | N/A | Defaults to 0 | Safe fallback |

---

## Top-3 Prediction Behavior

The model returns `predict_proba()` for all 16 classes, sorts by probability descending, and returns the top 3.

**Example output:**
```json
[
  {"rank": 1, "career": "Data Scientist", "probability": 0.4521},
  {"rank": 2, "career": "Machine Learning Engineer", "probability": 0.2103},
  {"rank": 3, "career": "AI Engineer", "probability": 0.1247}
]
```

Probabilities sum to 1.0 across all 16 classes. Top-3 are always valid class names from the encoder.

---

## Known Limitations

1. **Dataset size**: 6,000 samples for 16 classes (~375 per class) — moderate class balance
2. **Synthetic data**: Dataset_1_Cleaned.csv is synthetic student data, not real Pakistani university records
3. **Feature coverage**: 41 skill binary features do not cover all possible technical skills
4. **No confidence threshold**: Model always returns predictions even for very low-confidence cases
5. **No temporal features**: Does not account for changing job market trends
6. **Static model**: Not retrained automatically — requires manual retraining with new data
