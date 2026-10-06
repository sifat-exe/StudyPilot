from Database.database import authenticate_user


class RealDatabaseAuthProvider:

    def authenticate(self, email_or_username, password):
        return authenticate_user(email_or_username, password)

    def register(self, name, email, password):

        from Database.database import register_user

        # TODO: Sifat needs to add an email_exists() function to database.py
        # For now, we try to register and catch the unique constraint error
        try:
            register_user(name, email, password)
            return {"success": True, "message": "Registration successful."}
        except Exception as e:
            error_msg = str(e).lower()
            if "unique" in error_msg:
                return {"success": False, "message": "This email is already registered."}
            return {"success": False, "message": f"Registration failed: {str(e)}"}