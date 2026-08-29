"""Create an admin user.

Run: python -m scripts.create_admin
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password, validate_password_strength
from app.models.base import Base
from app.models.user import User, UserRole


def create_admin():
    email = input("Admin email: ").strip()
    if not email:
        print("Email is required.")
        return

    password = getpass.getpass("Admin password: ")
    pw_error = validate_password_strength(password)
    if pw_error:
        print(f"Invalid password: {pw_error}")
        return

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return

    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin user created: {email}")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
