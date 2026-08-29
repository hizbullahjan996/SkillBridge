"""Tests for authentication and authorization."""
from app.core.jwt import create_access_token
from app.models.user import User, UserRole
from app.core.security import hash_password


def _create_user(db_session, email="test@example.com", role=UserRole.student, active=True):
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=role,
        is_active=active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# === Registration Tests ===


def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "email": "new@student.com",
        "password": "Secure123!",
        "confirm_password": "Secure123!",
        "full_name": "New Student",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new@student.com"
    assert data["user"]["role"] == "student"
    assert data["user"]["is_active"] is True


def test_register_duplicate_email(client, db_session):
    _create_user(db_session, email="dup@test.com")
    response = client.post("/api/auth/register", json={
        "email": "dup@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "Dup User",
    })
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_password_mismatch(client):
    response = client.post("/api/auth/register", json={
        "email": "mismatch@test.com",
        "password": "Password123!",
        "confirm_password": "Different123!",
        "full_name": "Mismatch User",
    })
    assert response.status_code == 400
    assert "do not match" in response.json()["detail"]


def test_register_weak_password(client):
    response = client.post("/api/auth/register", json={
        "email": "weak@test.com",
        "password": "short",
        "confirm_password": "short",
        "full_name": "Weak User",
    })
    assert response.status_code == 422


def test_register_no_uppercase_password(client):
    response = client.post("/api/auth/register", json={
        "email": "noupper@test.com",
        "password": "alllowercase1",
        "confirm_password": "alllowercase1",
        "full_name": "No Upper",
    })
    assert response.status_code == 400


def test_register_invalid_email(client):
    response = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "Bad Email",
    })
    assert response.status_code == 422


def test_register_empty_name(client):
    response = client.post("/api/auth/register", json={
        "email": "noname@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "",
    })
    assert response.status_code == 422


def test_register_creates_student_profile(client, db_session):
    response = client.post("/api/auth/register", json={
        "email": "profile@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "Profile User",
    })
    assert response.status_code == 201

    user = db_session.query(User).filter(User.email == "profile@test.com").first()
    assert user is not None
    assert user.student_profile is not None
    assert user.student_profile.full_name == "Profile User"


# === Login Tests ===


def test_login_success(client, db_session):
    _create_user(db_session, email="login@test.com")
    response = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "Password123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"


def test_login_wrong_password(client, db_session):
    _create_user(db_session, email="wrong@test.com")
    response = client.post("/api/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_unknown_email(client):
    response = client.post("/api/auth/login", json={
        "email": "unknown@test.com",
        "password": "password123",
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user(client, db_session):
    _create_user(db_session, email="inactive@test.com", active=False)
    response = client.post("/api/auth/login", json={
        "email": "inactive@test.com",
        "password": "Password123!",
    })
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"]


# === Current User Tests ===


def test_get_me_success(client, db_session):
    from app.models.student import StudentProfile
    user = _create_user(db_session, email="me@test.com")
    profile = StudentProfile(user_id=user.id, full_name="Me Student")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@test.com"
    assert data["role"] == "student"
    assert data["student_profile"] is not None


def test_get_me_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_get_me_inactive_user(client, db_session):
    user = _create_user(db_session, email="inactive-me@test.com", active=False)
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# === Role Authorization Tests ===


def test_admin_route_with_admin(client, db_session):
    user = _create_user(db_session, email="admin@test.com", role=UserRole.admin)
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    response = client.get("/api/auth/admin-test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "admin" in response.json()["message"]


def test_admin_route_with_student(client, db_session):
    user = _create_user(db_session, email="student@test.com", role=UserRole.student)
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    response = client.get("/api/auth/admin-test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_admin_route_no_token(client):
    response = client.get("/api/auth/admin-test")
    assert response.status_code == 401


# === Health Endpoint Preservation ===


def test_health_still_works(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db_still_works(client):
    response = client.get("/api/health/db")
    assert response.status_code == 200
