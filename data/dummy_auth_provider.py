# data/dummy_auth_provider.py

class DummyAuthProvider:
    """Provides hardcoded authentication data for testing the UI."""
    
    def __init__(self):
        # A simple list of valid dummy users
        self.dummy_users = {
            "testuser": {"password": "123", "user_id": 1, "name": "Harry Potter", "email": "test@student.edu"},
            "student@university.edu": {"password": "123", "user_id": 2, "name": "Alice Smith", "email": "student@university.edu"}
        }

    def authenticate(self, email_or_username, password):
        """Simulates checking credentials against a database."""
        user_record = self.dummy_users.get(email_or_username)
        if user_record and user_record["password"] == password:
            # Return a simple user dictionary (without the password)
            return {
                "user_id": user_record["user_id"],
                "name": user_record["name"],
                "email": user_record["email"]
            }
        return None

