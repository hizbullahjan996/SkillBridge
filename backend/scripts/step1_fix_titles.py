"""Step 1: Fix job_title_clean for all jobs."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.models.job import Job


def clean_job_title(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9\s/]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


engine = create_engine(settings.database_url)
Base.metadata.create_all(engine)
db = Session(engine)

try:
    jobs = db.query(Job).all()
    fixed = 0
    for job in jobs:
        if not job.job_title_clean or job.job_title_clean.strip() == "":
            job.job_title_clean = clean_job_title(job.job_title)
            fixed += 1
    db.commit()
    print(f"Fixed job_title_clean for {fixed}/{len(jobs)} jobs")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
    engine.dispose()
