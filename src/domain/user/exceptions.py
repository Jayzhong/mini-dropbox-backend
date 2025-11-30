class UserAlreadyExistsError(Exception):
    """Raised when attempting to register a user with an email that already exists."""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists.")

class InvalidCredentialsError(Exception):
    """Raised when authentication credentials (e.g., email/password) are invalid."""
    def __init__(self):
        super().__init__("Invalid authentication credentials.")