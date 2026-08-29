"""Seed the skills table from Dataset 1 skill columns.

Run: python -m scripts.seed_skills
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.skill import Skill, SkillCategory
from app.models.base import Base
from app.core.config import settings
from sqlalchemy import create_engine

# Soft skills from Dataset 1
SOFT_SKILLS = {
    "communication_skills": "Communication",
    "teamwork": "Teamwork",
    "problem_solving": "Problem Solving",
}

# Technical skill column name -> display name
TECHNICAL_SKILLS = {
    "Skill_AWS": "AWS",
    "Skill_Adobe_XD": "Adobe XD",
    "Skill_Agile": "Agile",
    "Skill_Ansible": "Ansible",
    "Skill_Azure": "Azure",
    "Skill_CI_CD": "CI/CD",
    "Skill_Cybersecurity": "Cybersecurity",
    "Skill_Data_Analysis": "Data Analysis",
    "Skill_Django": "Django",
    "Skill_Docker": "Docker",
    "Skill_Elasticsearch": "Elasticsearch",
    "Skill_FastAPI": "FastAPI",
    "Skill_Figma": "Figma",
    "Skill_Flutter": "Flutter",
    "Skill_GCP": "GCP",
    "Skill_Git": "Git",
    "Skill_GraphQL": "GraphQL",
    "Skill_JavaScript": "JavaScript",
    "Skill_Kubernetes": "Kubernetes",
    "Skill_Laravel": "Laravel",
    "Skill_Linux": "Linux",
    "Skill_Machine_Learning": "Machine Learning",
    "Skill_MongoDB": "MongoDB",
    "Skill_MySQL": "MySQL",
    "Skill_Networking": "Networking",
    "Skill_Node.js": "Node.js",
    "Skill_NumPy": "NumPy",
    "Skill_PHP": "PHP",
    "Skill_Pandas": "Pandas",
    "Skill_PostgreSQL": "PostgreSQL",
    "Skill_PyTorch": "PyTorch",
    "Skill_Python": "Python",
    "Skill_REST_APIs": "REST APIs",
    "Skill_React": "React",
    "Skill_React_Native": "React Native",
    "Skill_Redis": "Redis",
    "Skill_SQL": "SQL",
    "Skill_Scrum": "Scrum",
    "Skill_TensorFlow": "TensorFlow",
    "Skill_Terraform": "Terraform",
    "Skill_TypeScript": "TypeScript",
}


def seed_skills():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        count = 0

        # Seed technical skills
        for col_name, display_name in TECHNICAL_SKILLS.items():
            normalized = display_name.lower().replace(" ", "_").replace(".", "_").replace("/", "_")
            existing = db.query(Skill).filter(Skill.normalized_name == normalized).first()
            if not existing:
                skill = Skill(
                    name=display_name,
                    normalized_name=normalized,
                    category=SkillCategory.technical,
                )
                db.add(skill)
                count += 1

        # Seed soft skills
        for col_name, display_name in SOFT_SKILLS.items():
            normalized = display_name.lower().replace(" ", "_")
            existing = db.query(Skill).filter(Skill.normalized_name == normalized).first()
            if not existing:
                skill = Skill(
                    name=display_name,
                    normalized_name=normalized,
                    category=SkillCategory.soft,
                )
                db.add(skill)
                count += 1

        db.commit()
        print(f"Seeded {count} new skills. Total technical: {len(TECHNICAL_SKILLS)}, soft: {len(SOFT_SKILLS)}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding skills: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_skills()
