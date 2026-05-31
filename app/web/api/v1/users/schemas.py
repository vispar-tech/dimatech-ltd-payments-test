import re

from pydantic import EmailStr, field_validator

from app.web.schemas import CamelCaseModel


class UserBase(CamelCaseModel):
    """Base fields for a user."""

    email: EmailStr
    full_name: str
    is_admin: bool = False


class UserCreate(UserBase):
    """Fields required to create a new user."""

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, pwd: str) -> str:
        """Validate password strength according to policy."""
        if len(pwd) < 6:
            raise ValueError("Пароль должен быть не короче 6 символов")
        checks = [
            (
                any(c.isdigit() for c in pwd),
                "Пароль должен содержать хотя бы одну цифру",
            ),
            (
                any(c.islower() for c in pwd),
                "Пароль должен содержать хотя бы одну строчную букву",
            ),
            (
                any(c.isupper() for c in pwd),
                "Пароль должен содержать хотя бы одну заглавную букву",
            ),
            (
                re.search(r"[\$&\+,:;=\?@#\|'<>\.\^\*\(\)%!-]", pwd),
                "Пароль должен содержать хотя бы один специальный символ",
            ),
        ]
        for condition, reason in checks:
            if not condition:
                raise ValueError(reason)
        return pwd


class UserRead(UserBase):
    """User read model."""

    id: int


class UserUpdate(CamelCaseModel):
    """Fields for updating a user; all optional."""

    full_name: str | None = None
    is_admin: bool | None = None
    password: str | None = None
    password_confirm: str | None = None
