"""Quick check of job_title_clean values."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.models.job import Job

engine = create_engine(settings.database_url)
Base.metadata.create_all(engine)
db = Session(engine)

try:
    # Count jobs with empty job_title_clean
    empty_count = db.query(func.count(Job.id)).filter(
        (Job.job_title_clean == None) | (Job.job_title_clean == "")
    ).scalar()
    total = db.query(func.count(Job.id)).scalar()
    print(f"Total jobs: {total}")
    print(f"Jobs with empty job_title_clean: {empty_count}")

    # Sample some jobs
    jobs = db.query(Job).limit(5).all()
    for j in jobs:
        print(f"  ID:{j.id} Title:{j.job_title} Clean:'{j.job_title_clean}'")
finally:
    db.close()
    engine.dispose()
