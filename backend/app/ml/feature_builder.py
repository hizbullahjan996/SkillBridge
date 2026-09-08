"""Builds ML feature vectors from student profile and skills."""
import logging

from sqlalchemy.orm import Session

from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill

logger = logging.getLogger("skillbridge.ml")


def build_features(profile: StudentProfile, skills: list[StudentSkill]) -> dict:
    """Convert a student profile and skills into the model's feature dictionary.

    This must produce exactly the same feature representation used during training:
    - 14 demographic/academic features
    - 5 engineered features
    - 41 skill features (Skill_*)
    - 4 categorical features (encoded by the predictor)

    Args:
        profile: The student's profile from the database.
        skills: The student's skill relationships.

    Returns:
        Dictionary mapping feature names to values.
    """
    skill_values = {}
    for ss in skills:
        if ss.skill:
            # Use the skill's display name to build the model column name,
            # preserving case and dots (e.g. "Node.js" → "Skill_Node.js").
            skill_col = f"Skill_{ss.skill.name.replace(' ', '_').replace('/', '_')}"
            skill_values[skill_col] = ss.proficiency

    skill_level_sum = sum(s.proficiency for s in skills)
    skill_count = len([s for s in skills if s.proficiency > 0])
    avg_skill = skill_level_sum / skill_count if skill_count > 0 else 0

    comm = profile.communication_skills or 0
    team = profile.teamwork or 0
    problem = profile.problem_solving or 0
    soft_skill_avg = (comm + team + problem) / 3

    projects = profile.projects_completed or 0
    certs = profile.certifications_count or 0
    internships = profile.internships or 0
    experience_score = projects + certs * 2 + internships * 3

    cgpa = profile.cgpa or 0
    attendance = profile.attendance_percentage or 0
    academic_strength = (cgpa / 4.0 * 0.6 + attendance / 100.0 * 0.4)

    features = {
        "Age": profile.age or 21,
        "Gender": profile.gender or "Male",
        "University_Year": profile.university_year or "Junior",
        "Major": profile.major or "Computer Science",
        "CGPA": cgpa,
        "Attendance_Percentage": attendance,
        "Study_Hours_Per_Week": profile.study_hours_per_week or 15,
        "Projects_Completed": projects,
        "Certifications_Count": certs,
        "Internships": internships,
        "Communication_Skills": comm,
        "Teamwork": team,
        "Problem_Solving": problem,
        "Interest_Domain": profile.interest_domain or "Software Development",
        "Total_Skills": skill_count,
        "Average_Skill_Level": round(avg_skill, 2),
        "Experience_Score": experience_score,
        "Soft_Skill_Score": round(soft_skill_avg, 2),
        "Academic_Strength": round(academic_strength, 4),
    }

    # Add all 41 skill columns with 0 as default
    ALL_SKILL_COLUMNS = [
        "Skill_AWS", "Skill_Adobe_XD", "Skill_Agile", "Skill_Ansible", "Skill_Azure",
        "Skill_CI_CD", "Skill_Cybersecurity", "Skill_Data_Analysis", "Skill_Django",
        "Skill_Docker", "Skill_Elasticsearch", "Skill_FastAPI", "Skill_Figma",
        "Skill_Flutter", "Skill_GCP", "Skill_Git", "Skill_GraphQL", "Skill_JavaScript",
        "Skill_Kubernetes", "Skill_Laravel", "Skill_Linux", "Skill_Machine_Learning",
        "Skill_MongoDB", "Skill_MySQL", "Skill_Networking", "Skill_Node.js",
        "Skill_NumPy", "Skill_PHP", "Skill_Pandas", "Skill_PostgreSQL", "Skill_PyTorch",
        "Skill_Python", "Skill_REST_APIs", "Skill_React", "Skill_React_Native",
        "Skill_Redis", "Skill_SQL", "Skill_Scrum", "Skill_TensorFlow", "Skill_Terraform",
        "Skill_TypeScript",
    ]

    for col in ALL_SKILL_COLUMNS:
        if col not in features:
            features[col] = skill_values.get(col, 0)

    return features
