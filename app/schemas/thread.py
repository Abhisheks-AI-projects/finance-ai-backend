from datetime import datetime, timezone
from enum import Enum
from secrets import token_hex

from pydantic import BaseModel, Field


  # ============================================================================

  
class MessageType(str, Enum):
    user = "user"
    ai = "ai"


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: token_hex(6))
    message_type: MessageType
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class Thread(BaseModel):
    thread_id: str
    user_id: str
    title: str | None = None
    messages: list[Message] = []
    is_shared: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # ============================================================================


class ThreadCreatedResponse(BaseModel):
    event_type: str
    thread_id: str
    timestamp: str


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    thread_id: str
    message_type: MessageType


class MessageResponse(BaseModel):
    event_type: str
    thread_id: str
    message: Message


class ThreadTitleResponse(BaseModel):
    event_type: str
    thread_id: str
    title: str


class TriggerAIRequest(BaseModel):
    message_id: str
    thread_id: str


class TriggerAIResponse(BaseModel):
    event_type: str
    thread_id: str
    message: Message


class ThreadDataResponse(BaseModel):
    thread_id: str
    title: str | None
    messages: list[Message]
    created_at: datetime
    updated_at: datetime


class ThreadListItem(BaseModel):
    thread_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime


class ThreadListResponse(BaseModel):
    threads: list[ThreadListItem]
