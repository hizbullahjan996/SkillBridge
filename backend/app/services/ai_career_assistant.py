"""AI Career Assistant Service.

Builds context from SkillBridge student data and generates grounded responses
using a configurable LLM provider. All responses are grounded in actual data.

Hallucination controls:
- Never fabricate jobs, skills, salaries, courses, or URLs
- Clearly distinguish SkillBridge data from general advice
- Return safe fallbacks when data is missing
"""
import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill
from app.models.recommendation import CareerRecommendation
from app.models.career import Career
from app.models.skill import Skill
from app.services.skill_gap_service import get_career_skill_gap
from app.services.learning_roadmap_service import get_default_roadmap
from app.services.llm_provider import get_llm_provider

logger = logging.getLogger("skillbridge")


@dataclass
class AssistantSource:
    type: str
    reference: str


@dataclass
class AssistantContext:
    profile: dict | None = None
    skills: list[dict] = field(default_factory=list)
    career_recommendations: list[dict] = field(default_factory=list)
    skill_gap: dict | None = None
    roadmap: list[dict] = field(default_factory=list)
    jobs: list[dict] = field(default_factory=list)
    sources: list[AssistantSource] = field(default_factory=list)


@dataclass
class AssistantAnswer:
    answer: str
    sources: list[AssistantSource] = field(default_factory=list)


def build_context(db: Session, student_id: int) -> AssistantContext:
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not profile:
        return AssistantContext()

    ctx = AssistantContext()

    ctx.profile = {
        "full_name": profile.full_name,
        "major": profile.major,
        "cgpa": profile.cgpa,
        "university_year": profile.university_year,
        "interest_domain": profile.interest_domain,
        "projects_completed": profile.projects_completed,
        "certifications_count": profile.certifications_count,
        "internships": profile.internships,
    }
    ctx.sources.append(AssistantSource(type="profile", reference="Your student profile"))

    student_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id)
        .all()
    )
    for ss in student_skills:
        skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
        if skill:
            ctx.skills.append({
                "name": skill.name,
                "normalized_name": skill.normalized_name,
                "proficiency": ss.proficiency,
                "category": skill.category.value,
            })
    if ctx.skills:
        ctx.sources.append(AssistantSource(type="skills", reference=f"{len(ctx.skills)} skill(s) in your profile"))

    recs = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == student_id)
        .order_by(CareerRecommendation.rank)
        .limit(3)
        .all()
    )
    for rec in recs:
        career = db.query(Career).filter(Career.id == rec.career_id).first()
        if career:
            ctx.career_recommendations.append({
                "career_name": career.name,
                "rank": rec.rank,
                "probability": round(rec.probability * 100, 1),
            })
    if ctx.career_recommendations:
        ctx.sources.append(AssistantSource(type="career_recommendations", reference="Your top-3 career recommendations"))

    if recs:
        top_career_id = recs[0].career_id
        gap = get_career_skill_gap(db, student_id, top_career_id)
        ctx.skill_gap = {
            "matched_count": gap.matched_count,
            "missing_count": gap.missing_count,
            "match_percentage": gap.match_percentage,
            "matched_skills": [{"name": m["name"], "category": m["category"]} for m in gap.matched_skills],
            "missing_skills": [
                {
                    "name": s.skill_name,
                    "priority": s.priority,
                    "priority_score": s.priority_score,
                    "demand_count": s.demand_count,
                    "category": s.category,
                }
                for s in gap.missing_skills
            ],
        }
        ctx.sources.append(AssistantSource(type="skill_gap", reference=f"Skill gap for {ctx.career_recommendations[0]['career_name']}"))

        roadmap = get_default_roadmap(db, profile.user_id)
        if roadmap:
            ctx.roadmap = [
                {
                    "step": item.step,
                    "skill": item.skill,
                    "priority": item.priority,
                    "reason": item.reason,
                }
                for item in roadmap.roadmap
            ]
            ctx.sources.append(AssistantSource(type="roadmap", reference="Your personalized learning roadmap"))

    return ctx


def format_context_for_llm(ctx: AssistantContext) -> str:
    parts = []

    if ctx.profile:
        p = ctx.profile
        parts.append("=== STUDENT PROFILE ===")
        parts.append(f"Name: {p.get('full_name', 'N/A')}")
        parts.append(f"Major: {p.get('major', 'N/A')}")
        parts.append(f"CGPA: {p.get('cgpa', 'N/A')}")
        parts.append(f"Year: {p.get('university_year', 'N/A')}")
        parts.append(f"Interest: {p.get('interest_domain', 'N/A')}")
        parts.append(f"Projects: {p.get('projects_completed', 'N/A')}")
        parts.append(f"Certifications: {p.get('certifications_count', 'N/A')}")
        parts.append(f"Internships: {p.get('internships', 'N/A')}")

    if ctx.skills:
        parts.append("\n=== CURRENT SKILLS ===")
        for s in ctx.skills:
            parts.append(f"- {s['name']} (proficiency: {s['proficiency']}/10, category: {s['category']})")

    if ctx.career_recommendations:
        parts.append("\n=== CAREER RECOMMENDATIONS ===")
        for c in ctx.career_recommendations:
            parts.append(f"- Rank {c['rank']}: {c['career_name']} ({c['probability']}% match)")

    if ctx.skill_gap:
        sg = ctx.skill_gap
        parts.append(f"\n=== SKILL GAP ({sg['match_percentage']}% match) ===")
        parts.append(f"Matched: {sg['matched_count']} skill(s)")
        for m in sg["matched_skills"]:
            parts.append(f"  - {m['name']} ({m['category']})")
        parts.append(f"Missing: {sg['missing_count']} skill(s)")
        for m in sg["missing_skills"]:
            parts.append(f"  - {m['name']} (priority: {m['priority']}, score: {m['priority_score']}, demand: {m['demand_count']})")

    if ctx.roadmap:
        parts.append("\n=== LEARNING ROADMAP ===")
        for item in ctx.roadmap:
            parts.append(f"Step {item['step']}: {item['skill']} ({item['priority']} priority) - {item['reason']}")

    return "\n".join(parts)


SYSTEM_PROMPT = """You are SkillBridge AI Career Assistant, a helpful career guidance assistant for Pakistani university students.

CORE RULES:
1. You MUST answer based ONLY on the SkillBridge student data provided in the context.
2. Never fabricate jobs, skills, salaries, courses, URLs, certifications, or career requirements.
3. Clearly distinguish between SkillBridge data and general career advice.
4. If data is missing, say "I don't have that information in the current SkillBridge data."
5. Never guarantee employment, salary, or job placement.
6. Keep responses concise: 3-6 short paragraphs or bullet points.
7. For career recommendation explanations, say "Your recommendation is based on the profile and skill features used by the trained career-classification model." Do NOT claim causal explanations.
8. Do not suggest manipulating job applications or fabricating qualifications.
9. Use the student's actual data when referencing their skills, gaps, or recommendations.
10. Be helpful and supportive while remaining honest.

RESPONSE FORMAT:
- Use the student's actual data from SkillBridge
- When citing SkillBridge data, reference it directly (e.g., "According to your profile...")
- For general advice, clearly mark it as such (e.g., "In general...")
- Use bullet points for lists
- Keep it actionable and student-friendly
"""


def build_user_message(message: str, ctx: AssistantContext) -> str:
    context_str = format_context_for_llm(ctx)
    return f"""Student Context:
{context_str}

Student Question: {message}

Answer based on the student's SkillBridge data above. If the question cannot be answered from the data, clearly state what information is missing."""


def validate_response(answer: str, ctx: AssistantContext) -> str:
    if not answer or not answer.strip():
        return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."

    if len(answer) > 3000:
        answer = answer[:3000] + "\n\n[Response truncated for brevity]"

    dangerous_patterns = [
        "api_key",
        "secret",
        "password",
        "SYSTEM_PROMPT",
        "You are SkillBridge",
    ]
    for pattern in dangerous_patterns:
        if pattern.lower() in answer.lower():
            logger.warning("Response contains potentially sensitive content, sanitizing")
            return "I apologize, but I cannot provide that information. Please ask about your career recommendations, skill gaps, or learning roadmap."

    return answer


def extract_sources_from_message(message: str, ctx: AssistantContext) -> list[AssistantSource]:
    message_lower = message.lower()
    sources = []

    skill_keywords = ["skill", "learn", "proficiency", "know", "ability"]
    career_keywords = ["career", "recommend", "suggest", "path", "job"]
    gap_keywords = ["gap", "missing", "need", "lack", "improve"]
    roadmap_keywords = ["roadmap", "plan", "sequence", "order", "step"]

    if any(kw in message_lower for kw in skill_keywords):
        sources.append(AssistantSource(type="skills", reference="Your skill profile"))
    if any(kw in message_lower for kw in career_keywords):
        sources.append(AssistantSource(type="career_recommendations", reference="Career recommendations"))
    if any(kw in message_lower for kw in gap_keywords):
        sources.append(AssistantSource(type="skill_gap", reference="Skill gap analysis"))
    if any(kw in message_lower for kw in roadmap_keywords):
        sources.append(AssistantSource(type="roadmap", reference="Learning roadmap"))

    if not sources:
        sources = ctx.sources[:3] if ctx.sources else []

    return sources


def chat(
    db: Session,
    student_id: int,
    message: str,
    conversation_id: int | None = None,
) -> dict:
    ctx = build_context(db, student_id)
    user_msg = build_user_message(message, ctx)
    sources = extract_sources_from_message(message, ctx)

    llm = get_llm_provider()
    try:
        raw_answer = llm.generate(SYSTEM_PROMPT, user_msg)
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        raw_answer = (
            "I apologize, but I'm unable to generate a response right now. "
            "The AI service is temporarily unavailable. Please try again later."
        )
        sources = []

    answer = validate_response(raw_answer, ctx)

    conv = None
    if conversation_id:
        conv = db.query(AssistantConversation).filter(
            AssistantConversation.id == conversation_id,
            AssistantConversation.student_id == student_id,
        ).first()

    if not conv:
        conv = AssistantConversation(
            student_id=student_id,
            title=message[:100] if len(message) > 100 else message,
        )
        db.add(conv)
        db.flush()

    user_db_msg = AssistantMessage(
        conversation_id=conv.id,
        role="user",
        content=message,
    )
    db.add(user_db_msg)

    assistant_db_msg = AssistantMessage(
        conversation_id=conv.id,
        role="assistant",
        content=answer,
    )
    db.add(assistant_db_msg)
    db.commit()
    db.refresh(conv)

    return {
        "answer": answer,
        "sources": [{"type": s.type, "reference": s.reference} for s in sources],
        "conversation_id": conv.id,
    }


def get_conversation_history(
    db: Session,
    student_id: int,
    conversation_id: int,
) -> dict | None:
    conv = db.query(AssistantConversation).filter(
        AssistantConversation.id == conversation_id,
        AssistantConversation.student_id == student_id,
    ).first()

    if not conv:
        return None

    messages = (
        db.query(AssistantMessage)
        .filter(AssistantMessage.conversation_id == conversation_id)
        .order_by(AssistantMessage.created_at)
        .all()
    )

    return {
        "conversation": {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
        },
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }


def get_student_conversations(
    db: Session,
    student_id: int,
) -> list[dict]:
    convs = (
        db.query(AssistantConversation)
        .filter(AssistantConversation.student_id == student_id)
        .order_by(AssistantConversation.updated_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in convs
    ]


def delete_conversation(
    db: Session,
    student_id: int,
    conversation_id: int,
) -> bool:
    conv = db.query(AssistantConversation).filter(
        AssistantConversation.id == conversation_id,
        AssistantConversation.student_id == student_id,
    ).first()

    if not conv:
        return False

    db.delete(conv)
    db.commit()
    return True
