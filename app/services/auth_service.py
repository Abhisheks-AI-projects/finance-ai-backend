from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, db: Session): 
       self.user_repository = UserRepository(db)

    def get_or_create_user(self, clerk_user_id: str, email: str = "", username: str = "") -> User:
        user = self.user_repository.get_user(clerk_user_id)
        if not user:
            user = self.user_repository.create_user(clerk_user_id, email, username)
        return user