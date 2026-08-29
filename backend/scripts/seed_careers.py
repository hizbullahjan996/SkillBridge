"""Seed the careers table from Dataset 1 Career_Field values.

Run: python -m scripts.seed_careers
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.career import Career
from app.models.base import Base
from app.core.config import settings
from sqlalchemy import create_engine

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "Dataset_1_Cleaned.csv"

# Career field descriptions (basic, can be enriched later)
CAREER_DESCRIPTIONS = {
    "AI Engineer": "Designs and implements artificial intelligence and machine learning systems",
    "Automation Engineer": "Builds automated testing and deployment pipelines",
    "Backend Developer": "Develops server-side logic, APIs, and database interactions",
    "Business Analyst": "Analyzes business processes and translates requirements into technical solutions",
    "Cloud Engineer": "Designs, deploys, and manages cloud infrastructure and services",
    "Cybersecurity Analyst": "Protects systems and networks from security threats and vulnerabilities",
    "Data Analyst": "Collects, processes, and performs statistical analysis on datasets",
    "Data Scientist": "Builds predictive models and extracts insights from complex data",
    "DevOps Engineer": "Manages CI/CD pipelines and bridges development and operations",
    "Embedded Systems Engineer": "Develops software for embedded devices and IoT systems",
    "Full Stack Developer": "Builds both frontend and backend components of web applications",
    "IT Support Engineer": "Provides technical support and maintains IT infrastructure",
    "Machine Learning Engineer": "Designs and deploys machine learning models at scale",
    "Penetration Tester": "Conducts authorized security testing to identify vulnerabilities",
    "SOC Analyst": "Monitors and responds to security incidents in security operations centers",
    "Software Engineer": "Designs, develops, and maintains software applications",
}


def seed_careers():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        # Collect unique career fields from the dataset
        career_fields = set()
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                career_fields.add(row["Career_Field"].strip())

        count = 0
        for field in sorted(career_fields):
            normalized = field.lower().replace(" ", "_").replace("&", "and").replace("/", "_")
            existing = db.query(Career).filter(Career.normalized_name == normalized).first()
            if not existing:
                career = Career(
                    name=field,
                    normalized_name=normalized,
                    description=CAREER_DESCRIPTIONS.get(field),
                )
                db.add(career)
                count += 1

        db.commit()
        print(f"Seeded {count} new careers from {len(career_fields)} unique fields in Dataset 1.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding careers: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_careers()
