import logging
from typing import Annotated

import jwt
from clerk_backend_api import (
    AuthenticateRequestOptions,
    authenticate_request,
)
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.postgres import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthUser, ClerkUser

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)


# This function verifies the Clerk token and returns the ClerkUser object if the token is valid.
#  It raises an HTTPException if the token is invalid or missing.
async def verify_clerk_token(
    request: Request,
    _credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ] = None,
) -> ClerkUser:
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.clerk_secret_key,
            jwt_key=settings.clerk_jwt_key,
            accepts_token=["session_token"],
        ),
    )

    if not state.is_signed_in:
        logger.error(
            "Clerk auth failed: reason=%s, message=%s",
            state.reason,
            state.message,
        )
        raise HTTPException(
            status_code=401,
            detail=state.message or "Unauthorized",
        )

    payload = state.payload
    return ClerkUser(
        clerk_user_id=payload["sub"],
        email=payload.get("email", ""),
        username=payload.get("username", ""),
    )


# This function is a simplified version of the above function that decodes the JWT token without verifying the signature.
#  It is useful for development and testing purposes, but should not be used in production.
async def verify_clerk_token_v2(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> ClerkUser:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization token required")
    try:
        payload = jwt.decode(
            credentials.credentials,
            options={"verify_signature": False},
            algorithms=["RS256"],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user_id found")
        return ClerkUser(
            clerk_user_id=user_id,
            email=payload.get("email", ""),
            username=payload.get("username", ""),
        )
    except jwt.exceptions.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token format: {e}")


# This function retrieves the authenticated user from the database based on the ClerkUser object obtained from the token verification.
#  It raises an HTTPException if the user is not found in the database.
async def get_auth_user(
    clerk_user: ClerkUser = Depends(verify_clerk_token_v2),
    db: Session = Depends(get_db),
) -> AuthUser:
    user = UserRepository(db).get_user(clerk_user.clerk_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return AuthUser(
        id=str(user.id),
        email=user.email,
        username=user.username,
    )