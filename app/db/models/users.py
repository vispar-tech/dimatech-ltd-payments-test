from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.accounts import Account
    from app.db.models.payments import Payment


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(
        default=False, nullable=False, server_default="false"
    )

    # Связи
    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )
