"""Career-to-job mapping service."""
import logging
from collections import defaultdict
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.career import Career
from app.models.career_job_mapping import CareerJobMapping, MappingType
from app.models.job import Job
from app.models.job_skill import JobSkill

logger = logging.getLogger("skillbridge")

CAREER_KEYWORDS = {
    "ai_engineer": ["ai engineer", "artificial intelligence", "machine learning engineer", "ml engineer"],
    "automation_engineer": ["automation engineer", "test automation", "qa automation"],
    "backend_developer": ["backend developer", "back-end developer", "server side", "api developer"],
    "business_analyst": ["business analyst", "data analyst", "bi analyst"],
    "cloud_engineer": ["cloud engineer", "devops engineer", "infrastructure engineer"],
    "cybersecurity_analyst": ["cybersecurity", "security analyst", "soc analyst", "penetration tester"],
    "data_analyst": ["data analyst", "reporting analyst", "bi developer", "analytics"],
    "data_scientist": ["data scientist", "machine learning", "nlp engineer"],
    "devops_engineer": ["devops", "sre", "site reliability", "platform engineer"],
    "embedded_systems_engineer": ["embedded", "firmware engineer", "iot engineer"],
    "full_stack_developer": ["full stack", "fullstack", "full-stack", "web developer"],
    "it_support_engineer": ["it support", "help desk", "technical support", "it specialist"],
    "machine_learning_engineer": ["machine learning engineer", "ml engineer"],
    "penetration_tester": ["penetration tester", "pentester", "ethical hacker"],
    "soc_analyst": ["soc analyst", "security operations", "threat analyst"],
    "software_engineer": ["software engineer", "software developer", "programmer"],
}


def normalize_title(title):
    return title.lower().strip()


def title_similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def get_job_skill_names(db, job_id):
    from app.models.skill import Skill
    skill_ids = [js.skill_id for js in db.query(JobSkill).filter(JobSkill.job_id == job_id).all()]
    if not skill_ids:
        return set()
    skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
    return {s.normalized_name for s in skills}


def compute_skill_overlap(career_skills, job_skills):
    if not career_skills or not job_skills:
        return 0.0
    return len(career_skills & job_skills) / len(career_skills)


def classify_mapping(title_sim, skill_overlap):
    if title_sim >= 0.5 or skill_overlap >= 0.4:
        return MappingType.strong, round(max(title_sim, skill_overlap), 2)
    elif title_sim >= 0.3 or skill_overlap >= 0.2:
        return MappingType.moderate, round((title_sim + skill_overlap) / 2, 2)
    elif title_sim >= 0.15 or skill_overlap >= 0.1:
        return MappingType.weak, round((title_sim + skill_overlap) / 2, 2)
    return None, 0.0


def generate_mappings(db, force=False):
    from app.models.career_skill import CareerSkill
    from app.models.skill import Skill

    careers = db.query(Career).all()
    jobs = db.query(Job).all()

    if not careers or not jobs:
        logger.warning("No careers or jobs found.")
        return 0

    existing = set()
    if not force:
        for m in db.query(CareerJobMapping).all():
            existing.add((m.career_id, m.job_title_clean))

    career_skill_cache = {}
    for career in careers:
        cs_rows = db.query(CareerSkill).filter(CareerSkill.career_id == career.id).all()
        skill_ids = [cs.skill_id for cs in cs_rows]
        if skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            career_skill_cache[career.id] = {s.normalized_name for s in skills}
        else:
            career_skill_cache[career.id] = set()

    # Precompute skill names per job once to avoid per-pair DB queries.
    job_skill_map = defaultdict(set)
    for js in db.query(JobSkill).all():
        job_skill_map[js.job_id].add(js.skill_id)
    all_skill_ids = {sid for sids in job_skill_map.values() for sid in sids}
    skill_name_by_id = {}
    if all_skill_ids:
        for s in db.query(Skill).filter(Skill.id.in_(all_skill_ids)).all():
            skill_name_by_id[s.id] = s.normalized_name
    job_skills_cache = {
        job_id: {skill_name_by_id[sid] for sid in sids if sid in skill_name_by_id}
        for job_id, sids in job_skill_map.items()
    }

    count = 0
    for career in careers:
        norm = career.normalized_name
        keywords = CAREER_KEYWORDS.get(norm, [career.name.lower()])
        career_skills = career_skill_cache.get(career.id, set())

        for job in jobs:
            if (career.id, job.job_title_clean) in existing:
                continue

            job_title_lower = normalize_title(job.job_title_clean)
            max_title_sim = max((title_similarity(kw, job_title_lower) for kw in keywords), default=0.0)

            job_skills = job_skills_cache.get(job.id, set())
            skill_overlap = compute_skill_overlap(career_skills, job_skills)

            mapping_type, confidence = classify_mapping(max_title_sim, skill_overlap)
            if mapping_type is None:
                continue

            mapping = CareerJobMapping(
                career_id=career.id,
                job_title_clean=job.job_title_clean,
                mapping_type=mapping_type,
                confidence=str(confidence),
                is_verified=False,
                notes=f"title_sim={max_title_sim:.2f}, skill_overlap={skill_overlap:.2f}",
            )
            db.add(mapping)
            count += 1

    db.commit()
    logger.info("Generated %d career-job mappings", count)
    return count
