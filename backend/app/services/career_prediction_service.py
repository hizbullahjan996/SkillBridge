"""Career prediction service - orchestrates profile + skills -> ML prediction -> DB storage."""
import logging

from sqlalchemy.orm import Session

from app.ml.feature_builder import build_features
from app.ml.predictor import load_model
from app.models.career import Career
from app.models.recommendation import CareerRecommendation
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill
from app.services.student_service import check_ml_readiness

logger = logging.getLogger("skillbridge")


def get_career_recommendations(
    db: Session,
    user_id: int,
    top_k: int = 3,
) -> dict:
    """Generate career recommendations for an authenticated student.

    Returns:
        Dict with keys: ready, message, recommendations, model_version, missing_fields, missing_skills
    """
    readiness = check_ml_readiness(db, user_id)

    if not readiness["ready"]:
        return {
            "ready": False,
            "message": "Complete your profile and add at least one skill before requesting career recommendations.",
            "recommendations": [],
            "model_version": None,
            "missing_fields": readiness["missing_fields"],
            "missing_skills": readiness["missing_skills"],
        }

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return {
            "ready": False,
            "message": "Student profile not found.",
            "recommendations": [],
            "model_version": None,
            "missing_fields": [],
            "missing_skills": [],
        }

    student_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == profile.id)
        .all()
    )

    try:
        predictor = load_model()
    except FileNotFoundError:
        logger.error("ML model artifact not found")
        return {
            "ready": False,
            "message": "ML model is not available. Please contact the administrator.",
            "recommendations": [],
            "model_version": None,
            "missing_fields": [],
            "missing_skills": [],
        }
    except Exception:
        logger.exception("Failed to load ML model")
        return {
            "ready": False,
            "message": "Failed to load ML model. Please try again later.",
            "recommendations": [],
            "model_version": None,
            "missing_fields": [],
            "missing_skills": [],
        }

    try:
        feature_dict = build_features(profile, student_skills)
        predictions = predictor.predict_top_k(feature_dict, k=top_k)
    except Exception:
        logger.exception("Prediction failed for user %d", user_id)
        return {
            "ready": False,
            "message": "Career prediction failed. Please try again later.",
            "recommendations": [],
            "model_version": None,
            "missing_fields": [],
            "missing_skills": [],
        }

    # Map career names to database career records
    career_map = {}
    for pred in predictions:
        career_name = pred["career"]
        career = db.query(Career).filter(Career.name == career_name).first()
        if career:
            career_map[career_name] = career.id
        else:
            normalized = career_name.lower().replace(" ", "_").replace("-", "_")
            career = db.query(Career).filter(Career.normalized_name == normalized).first()
            if career:
                career_map[career_name] = career.id
            else:
                logger.warning("Career '%s' not found in database", career_name)

    # Save recommendations
    for pred in predictions:
        career_id = career_map.get(pred["career"])
        if career_id is None:
            continue

        rec = CareerRecommendation(
            student_id=profile.id,
            career_id=career_id,
            rank=pred["rank"],
            probability=pred["probability"],
            model_version=predictor.model_version,
        )
        db.add(rec)

    db.commit()

    return {
        "ready": True,
        "message": "Career recommendations generated successfully.",
        "recommendations": predictions,
        "model_version": predictor.model_version,
        "missing_fields": [],
        "missing_skills": [],
    }


def get_recommendation_history(db: Session, user_id: int) -> list[dict]:
    """Get the student's recommendation history grouped by model_version + timestamp."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return []

    recs = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == profile.id)
        .order_by(CareerRecommendation.created_at.desc())
        .all()
    )

    if not recs:
        return []

    # Group by timestamp (same prediction run)
    from collections import OrderedDict
    groups = OrderedDict()
    for rec in recs:
        ts = rec.created_at.isoformat() if rec.created_at else "unknown"
        key = f"{rec.model_version}_{ts}"
        if key not in groups:
            groups[key] = {
                "model_version": rec.model_version,
                "created_at": ts,
                "recommendations": [],
            }
        groups[key]["recommendations"].append({
            "rank": rec.rank,
            "career": rec.career.name if rec.career else "Unknown",
            "probability": rec.probability,
        })

    return list(groups.values())


def get_latest_recommendation(db: Session, user_id: int) -> dict | None:
    """Get the most recent recommendation for the student."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return None

    latest = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == profile.id)
        .order_by(CareerRecommendation.created_at.desc())
        .first()
    )
    if not latest:
        return None

    # Get all recommendations from the same prediction run
    recs = (
        db.query(CareerRecommendation)
        .filter(
            CareerRecommendation.student_id == profile.id,
            CareerRecommendation.model_version == latest.model_version,
        )
        .order_by(CareerRecommendation.rank)
        .all()
    )

    return {
        "model_version": latest.model_version,
        "created_at": latest.created_at.isoformat() if latest.created_at else None,
        "recommendations": [
            {
                "rank": r.rank,
                "career": r.career.name if r.career else "Unknown",
                "probability": r.probability,
            }
            for r in recs
        ],
    }
