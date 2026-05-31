from pydantic import EmailStr

from app.web.schemas import CamelCaseModel


class UserBase(CamelCaseModel):
    """Base fields for a user."""

    email: EmailStr
    full_name: str
    is_admin: bool = False


class UserCreate(UserBase):
    """Fields required to create a new user."""

    password: str


class UserRead(UserBase):
    """User read model."""

    id: int


class UserUpdate(CamelCaseModel):
    """Fields for updating a user; all optional."""

    full_name: str | None = None
    is_admin: bool | None = None
    password: str | None = None
    password_confirm: str | None = None
