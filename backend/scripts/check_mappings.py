"""Check career_job_mappings table."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.models.career_job_mapping import CareerJobMapping
from app.models.career import Career
from app.models.job import Job

engine = create_engine(settings.database_url)
Base.metadata.create_all(engine)
db = Session(engine)

try:
    total_mappings = db.query(func.count(CareerJobMapping.id)).scalar()
    print(f"Total career-job mappings: {total_mappings}")

    if total_mappings == 0:
        print("NO MAPPINGS FOUND! Need to run generate_mappings.")
        # Check careers
        careers = db.query(Career).all()
        print(f"Careers in DB: {len(careers)}")
        for c in careers:
            print(f"  {c.id}: {c.name} (normalized: {c.normalized_name})")

        # Sample some job_title_clean values from jobs
        jobs = db.query(Job).limit(5).all()
        print(f"\nSample job_title_clean values:")
        for j in jobs:
            print(f"  '{j.job_title_clean}'")
    else:
        # Show some mappings
        mappings = db.query(CareerJobMapping).limit(10).all()
        for m in mappings:
            career = db.query(Career).filter(Career.id == m.career_id).first()
            print(f"  Career: {career.name if career else '?'} -> Job: '{m.job_title_clean}' (type: {m.mapping_type}, confidence: {m.confidence})")
finally:
    db.close()
    engine.dispose()
