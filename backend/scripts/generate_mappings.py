"""Generate career-to-job mappings from the imported data.

Run: python -m scripts.generate_mappings
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.services.career_job_mapping_service import generate_mappings


def main():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = Session(engine)

    try:
        count = generate_mappings(db, force=True)
        print(f"Generated {count} career-job mappings")
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
