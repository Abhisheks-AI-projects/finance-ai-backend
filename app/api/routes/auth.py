from clerk_backend_api import Session
from fastapi import APIRouter, Depends

from app.core.security import get_auth_user, verify_clerk_token, verify_clerk_token_v2
from app.db.postgres import get_db
from app.models.user import User
from app.schemas.auth import ClerkUser, MetaDataResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MetaDataResponse)
async def get_me(clerk_user: ClerkUser = Depends(verify_clerk_token_v2), db: Session = Depends(get_db)):
    user = AuthService(db).get_or_create_user(clerk_user_id=clerk_user.clerk_user_id, email=clerk_user.email, username=clerk_user.username)
    return MetaDataResponse(user_id=str(user.id), email=user.email, name=user.username)

@router.get("/all-users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users} 