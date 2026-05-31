from app.db.models.users import User
from app.db.repository import BaseRepository


class UsersRepository(BaseRepository[User]):
    """Repository for User model."""

    model = User
