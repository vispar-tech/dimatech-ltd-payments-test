import secrets

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher


class PasswordHelper:
    """Helper class for password hashing, verification, and token generation."""

    def __init__(self) -> None:
        """Initialize password hashers."""
        self.password_hash = PasswordHash(
            (
                Argon2Hasher(),
                BcryptHasher(),
            )
        )

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, str | None]:
        """Verify password and update hash if needed."""
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        """Hash a password."""
        return self.password_hash.hash(password)

    def generate(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe()
