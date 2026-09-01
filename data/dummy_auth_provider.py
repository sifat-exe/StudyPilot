# data/dummy_auth_provider.py

class DummyAuthProvider:
    """Provides hardcoded authentication data for testing the UI."""

    # Class-level dict so registered users persist across AuthService instances
    dummy_users = {
        "testuser": {"password": "123", "user_id": 1, "name": "Harry Potter", "email": "test@student.edu"},
        "student@university.edu": {"password": "123", "user_id": 2, "name": "Alice Smith", "email": "student@university.edu"}
    }
    _next_user_id = 3  # Track the next available user ID

    def authenticate(self, email_or_username, password):
        """Simulates checking credentials against a database."""
        user_record = None

        for user in DummyAuthProvider.dummy_users.values():
            if user["email"] == email_or_username or user["name"] == email_or_username:
                user_record = user
                break


        if user_record and user_record["password"] == password:
            # Return a simple user dictionary (without the password)
            return {
                "user_id": user_record["user_id"],
                "name": user_record["name"],
                "email": user_record["email"]
            }
        return None

    def register(self, name, email, password):
        """Simulates registering a new user."""
        # Check if email already exists
        if self.email_exists(email):
            return {"success": False, "message": "This email is already registered."}

        # Add the new user to the shared dummy_users dict
        new_user_id = DummyAuthProvider._next_user_id
        DummyAuthProvider._next_user_id += 1

        DummyAuthProvider.dummy_users[email] = {
            "password": password,
            "user_id": new_user_id,
            "name": name,
            "email": email
        }

        return {"success": True, "message": "Registration successful."}

    def email_exists(self, email):
        """Checks if an email is already registered in dummy data."""
        for key, user in DummyAuthProvider.dummy_users.items():
            if user["email"] == email:
                return True
        return False
