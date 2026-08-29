"""Import curated learning resources into the database.

Usage:
    cd backend
    python scripts/import_learning_resources.py

This script:
1. Reads the curated resource catalog
2. Matches skills to the centralized skills table
3. Creates LearningResource and LearningResourceSkill records
4. Avoids duplicates (safe to run multiple times)
5. Reports unmatched skills
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base
from app.models.skill import Skill
from app.models.learning_resource import LearningResource, LearningResourceSkill
from data.learning_resources_catalog import get_resources


def import_resources():
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        existing_skills = {
            s.normalized_name: s
            for s in db.query(Skill).all()
        }

        existing_resources = {
            r.title: r
            for r in db.query(LearningResource).all()
        }

        resources = get_resources()
        created_count = 0
        skipped_count = 0
        unmatched_skills = set()

        for res_data in resources:
            title = res_data["title"]

            if title in existing_resources:
                skipped_count += 1
                continue

            resource = LearningResource(
                title=title,
                provider=res_data["provider"],
                description=res_data.get("description", ""),
                url=res_data.get("url", ""),
                resource_type=res_data["resource_type"],
                difficulty=res_data.get("difficulty"),
                is_free=res_data.get("is_free", True),
            )
            db.add(resource)
            db.flush()

            for skill_name in res_data.get("skills", []):
                normalized = skill_name.lower().strip()
                if normalized in existing_skills:
                    skill = existing_skills.get(normalized)
                    if skill:
                        link = LearningResourceSkill(
                            resource_id=resource.id,
                            skill_id=skill.id,
                        )
                        db.add(link)
                    else:
                        unmatched_skills.add(skill_name)

            created_count += 1

        db.commit()

        print(f"\n=== Import Summary ===")
        print(f"Created: {created_count} resources")
        print(f"Skipped: {skipped_count} (already exist)")

        if unmatched_skills:
            print(f"\nUnmatched skills ({len(unmatched_skills)}):")
            for skill in sorted(unmatched_skills):
                print(f"  - {skill}")
        else:
            print("\nAll skills matched successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_resources()
