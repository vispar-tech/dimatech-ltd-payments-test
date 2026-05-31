from app.db.models.payments import Payment
from app.db.repository import BaseRepository


class PaymentsRepository(BaseRepository[Payment]):
    """Repository for Payment model."""

    model = Payment
