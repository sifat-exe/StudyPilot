from database.database import authenticate_user


class RealDatabaseAuthProvider:

    def authenticate(self, email_or_username, password):
        return authenticate_user(email_or_username, password)