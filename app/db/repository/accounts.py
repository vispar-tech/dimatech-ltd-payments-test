from app.db.models.accounts import Account
from app.db.repository import BaseRepository


class AccountsRepository(BaseRepository[Account]):
    """Repository for Account model."""

    model = Account
