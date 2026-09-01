# services/auth_service.py
from config import USE_DUMMY_DATA
from data.dummy_auth_provider import DummyAuthProvider

class AuthService:
    """Service layer that handles authentication logic, separating UI from Data."""
    
    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyAuthProvider()
        else:
            # TODO (Sifat): Create a RealDatabaseAuthProvider in data/ or use your db module here
            # self.provider = RealDatabaseAuthProvider()
            
            # Temporary fallback until real database auth is implemented
            print("WARNING: Real database auth not implemented yet. Falling back to dummy data.")
            self.provider = DummyAuthProvider()

    def login(self, email_or_username, password):
        """
        Attempts to authenticate a user.
        Returns user dictionary if successful, None if failed.
        """
        if not email_or_username or not password:
            return None
            
        return self.provider.authenticate(email_or_username, password)

