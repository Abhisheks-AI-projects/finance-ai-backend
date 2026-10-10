from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, clerk_user_id: str) -> User | None:
        return self.db.query(User).filter(User.clerk_user_id == clerk_user_id).first()

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, clerk_user_id: str, email: str, username: str) -> User:
        user = User(clerk_user_id=clerk_user_id, email=email, username=username)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user