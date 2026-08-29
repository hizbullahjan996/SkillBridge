from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    confirm_password: str
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    student_profile: "StudentProfileResponse | None" = None

    model_config = {"from_attributes": True}


class StudentProfileResponse(BaseModel):
    id: int
    full_name: str
    age: int | None = None
    gender: str | None = None
    university_year: str | None = None
    major: str | None = None
    cgpa: float | None = None

    model_config = {"from_attributes": True}
