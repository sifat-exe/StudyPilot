from config import USE_DUMMY_DATA
from data.dummy_auth_provider import DummyAuthProvider
from data.real_database_auth_provider import RealDatabaseAuthProvider


class AuthService:
    """Service layer that handles authentication logic, separating UI from Data."""

    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyAuthProvider()
        else:
            self.provider = RealDatabaseAuthProvider()

    def login(self, email_or_username, password):
        """
        Attempts to authenticate a user.
        Returns user information if successful, None if failed.
        """
        if not email_or_username or not password:
            return None

        return self.provider.authenticate(
            email_or_username,
            password
        )

    def register(self, name, email, password):
        """
        Attempts to register a new user.
        Returns a dict with 'success' (bool) and 'message' (str).
        """
        if not name or not email or not password:
            return {"success": False, "message": "All fields are required."}

        return self.provider.register(name, email, password)