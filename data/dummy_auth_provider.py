class DummyAuthProvider:

    dummy_users = {
        "testuser": {
            "password": "123",
            "user_id": 1,
            "name": "Harry Potter",
            "email": "test@student.edu"
        },

        "student@university.edu": {
            "password": "123",
            "user_id": 2,
            "name": "Alice Smith",
            "email": "student@university.edu"
        }
    }

    _next_user_id = 3

    def authenticate(self, email, password):
        for user in DummyAuthProvider.dummy_users.values():
            if user["email"] == email and user["password"] == password:
                return {
                    "user_id": user["user_id"],
                    "name": user["name"],
                    "email": user["email"]
                }

        return None

    def register(self, name, email, password):
        if self.email_exists(email):
            return {
                "success": False,
                "message": "This email is already registered."
            }

        new_user_id = DummyAuthProvider._next_user_id
        DummyAuthProvider._next_user_id += 1

        DummyAuthProvider.dummy_users[email] = {
            "password": password,
            "user_id": new_user_id,
            "name": name,
            "email": email
        }

        return {
            "success": True,
            "message": "Registration successful."
        }

    def email_exists(self, email):
        for user in DummyAuthProvider.dummy_users.values():
            if user["email"] == email:
                return True

        return False