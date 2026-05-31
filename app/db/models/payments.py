from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.accounts import Account
    from app.db.models.users import User


class Payment(Base):
    """Payment model."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    transaction_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="payments")
    account: Mapped["Account"] = relationship("Account", back_populates="payments")
