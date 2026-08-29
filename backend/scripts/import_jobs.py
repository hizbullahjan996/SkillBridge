"""Import jobs from Dataset 2 into the jobs and job_skills tables.

Idempotent - safe to run multiple times without creating duplicates.

Run: python -m scripts.import_jobs
"""
import ast
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill, SkillCategory

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "Dataset_2_Cleaned.csv"


def parse_date(date_str: str):
    if not date_str or date_str.strip() == "":
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_skills_list(skills_str: str) -> list[str]:
    try:
        parsed = ast.literal_eval(skills_str)
        if isinstance(parsed, list):
            return [s.strip() for s in parsed if s.strip()]
    except (ValueError, SyntaxError):
        pass
    return []


def normalize_skill_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace(".", "_").replace("/", "_").replace("-", "_")


def get_or_create_skill(db: Session, skill_name: str) -> Skill:
    normalized = normalize_skill_name(skill_name)
    existing = db.query(Skill).filter(Skill.normalized_name == normalized).first()
    if existing:
        return existing
    skill = Skill(
        name=skill_name,
        normalized_name=normalized,
        category=SkillCategory.technical,
    )
    db.add(skill)
    db.flush()
    return skill


def job_exists(db: Session, job_title: str, company: str) -> bool:
    return db.query(Job).filter(
        Job.job_title == job_title,
        Job.company == company,
    ).first() is not None


def import_jobs():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = Session(engine)

    try:
        imported = 0
        skipped = 0
        duplicates = 0
        skills_created = 0

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                job_title = row.get("Job_Title", "").strip()
                company = row.get("Company", "").strip()

                if not job_title or not company:
                    skipped += 1
                    continue

                if job_exists(db, job_title, company):
                    duplicates += 1
                    continue

                job = Job(
                    job_title=job_title,
                    job_title_clean=row.get("Job_Title_Clean", "").strip() or job_title,
                    company=company,
                    city=row.get("City", "").strip(),
                    sector=row.get("Sector", "").strip(),
                    salary_min=float(row["Salary_Min"]) if row.get("Salary_Min") else None,
                    salary_max=float(row["Salary_Max"]) if row.get("Salary_Max") else None,
                    salary_average=float(row["Salary_Average"]) if row.get("Salary_Average") else None,
                    experience_min_years=float(row["Experience_Min_Years"]) if row.get("Experience_Min_Years") else None,
                    experience_max_years=float(row["Experience_Max_Years"]) if row.get("Experience_Max_Years") else None,
                    experience_required_raw=row.get("Experience_Required", "").strip() or None,
                    education_level=row.get("Education_Level", "").strip() or None,
                    job_type=row.get("Job_Type", "").strip() or None,
                    gender_preference=row.get("Gender_Preference", "").strip() or None,
                    number_of_vacancies=int(row["Number_of_Vacancies"]) if row.get("Number_of_Vacancies") else None,
                    posted_date=parse_date(row.get("Posted_Date", "")),
                    application_deadline=parse_date(row.get("Application_Deadline", "")),
                )
                db.add(job)
                db.flush()

                skills_str = row.get("Required_Skills_Clean", "")
                skill_names = parse_skills_list(skills_str)
                for skill_name in skill_names:
                    skill = get_or_create_skill(db, skill_name)
                    existing_js = db.query(JobSkill).filter(
                        JobSkill.job_id == job.id,
                        JobSkill.skill_id == skill.id,
                    ).first()
                    if not existing_js:
                        js = JobSkill(job_id=job.id, skill_id=skill.id)
                        db.add(js)

                imported += 1

        db.commit()

        total_jobs = db.query(func.count(Job.id)).scalar()
        total_skills = db.query(func.count(Skill.id)).scalar()
        total_job_skills = db.query(func.count(JobSkill.id)).scalar()

        print(f"Import complete:")
        print(f"  New jobs imported: {imported}")
        print(f"  Duplicates skipped: {duplicates}")
        print(f"  Rows skipped (empty): {skipped}")
        print(f"  Total jobs in DB: {total_jobs}")
        print(f"  Total skills in DB: {total_skills}")
        print(f"  Total job-skill links: {total_job_skills}")

    except Exception as e:
        db.rollback()
        print(f"Error importing jobs: {e}")
        raise
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    import_jobs()
