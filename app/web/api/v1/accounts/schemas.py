from decimal import Decimal

from app.web.schemas import CamelCaseModel


class AccountRead(CamelCaseModel):
    """Account model for response schema."""

    id: int
    balance: Decimal
