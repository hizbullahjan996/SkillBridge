"""Fix job_title_clean for all jobs and regenerate career-job mappings.

Run: python -m scripts.fix_job_title_clean
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.models.job import Job
from app.models.career_job_mapping import CareerJobMapping
from app.models.skill import Skill
from app.models.job_skill import JobSkill


def clean_job_title(title: str) -> str:
    """Normalize job title the same way the dataset's Job_Title_Clean was done."""
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9\s/]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = Session(engine)

    try:
        # Step 1: Fix job_title_clean for all jobs
        jobs = db.query(Job).all()
        fixed = 0
        for job in jobs:
            if not job.job_title_clean or job.job_title_clean.strip() == "":
                job.job_title_clean = clean_job_title(job.job_title)
                fixed += 1
        db.commit()
        print(f"Fixed job_title_clean for {fixed} jobs (out of {len(jobs)} total)")

        # Step 2: Delete old career-job mappings (they used empty job_title_clean)
        deleted = db.query(CareerJobMapping).delete()
        db.commit()
        print(f"Deleted {deleted} old career-job mappings")

        # Step 3: Regenerate mappings using the career_job_mapping_service
        from app.services.career_job_mapping_service import generate_mappings
        count = generate_mappings(db, force=True)
        print(f"Generated {count} new career-job mappings")

        # Verify
        total_mappings = db.query(func.count(CareerJobMapping.id)).scalar()
        print(f"Total career-job mappings in DB: {total_mappings}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
