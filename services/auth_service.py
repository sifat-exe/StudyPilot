from config import USE_DUMMY_DATA
from data.dummy_auth_provider import DummyAuthProvider
from data.real_database_auth_provider import RealDatabaseAuthProvider


class AuthService:

    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyAuthProvider()
        else:
            self.provider = RealDatabaseAuthProvider()

    def login(self, email, password):
        if not email or not password:
            return None

        return self.provider.authenticate(email, password)

    def register(self, name, email, password):
        if not name or not email or not password:
            return {
                "success": False,
                "message": "All fields are required."
            }

        return self.provider.register(name, email, password)