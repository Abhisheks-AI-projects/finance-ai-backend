from pydantic import BaseModel


class ClerkUser(BaseModel):
    clerk_user_id: str
    email: str
    username: str


class AuthUser(BaseModel):
    id: str
    email: str | None = None
    username: str | None = None


class MetaDataResponse(BaseModel):
    user_id: str
    email: str | None = None
    name: str | None = None
