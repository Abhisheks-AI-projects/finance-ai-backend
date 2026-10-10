from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.security import get_auth_user
from app.core.events import EVENT_TYPES
from core_brain.db.mongo import get_mongo_db
from app.schemas.auth import AuthUser
from app.schemas.thread import (
    MessageRequest, MessageResponse,
    ThreadCreatedResponse,
    ThreadDataResponse,
    ThreadListResponse,
    TriggerAIRequest,
)
from core_brain.services.thread_service import ThreadService

router = APIRouter(prefix="/thread", tags=["thread"])


@router.post("/create-thread", response_model=ThreadCreatedResponse)
async def create_thread(user: AuthUser = Depends(get_auth_user), mongo_db=Depends(get_mongo_db)):
    thread_service = ThreadService(mongo_db)
    thread = thread_service.create_thread(user.id)

    return ThreadCreatedResponse(
        event_type=EVENT_TYPES.THREAD_CREATED,
        thread_id=thread.thread_id,
        timestamp=thread.created_at.isoformat(),
    )


@router.post("/send-message", response_model=MessageResponse)
async def send_message(
    message_request: MessageRequest,
    user: AuthUser = Depends(get_auth_user),
    mongo_db=Depends(get_mongo_db),
):
    thread_service = ThreadService(mongo_db)
    message = thread_service.add_message(message_request.thread_id, user.id, message_request.message, message_request.message_type)

    return MessageResponse(
        event_type=EVENT_TYPES.MESSAGE_ADDED,
        thread_id=message_request.thread_id,
        message=message,
    )


@router.get("/list-threads", response_model=ThreadListResponse)
async def list_threads(user: AuthUser = Depends(get_auth_user), mongo_db=Depends(get_mongo_db)):
    thread_service = ThreadService(mongo_db)
    threads = thread_service.list_threads(user.id)
    return ThreadListResponse(threads=threads)


@router.get("/get-thread-data/{thread_id}", response_model=ThreadDataResponse)
async def get_thread_data(
    thread_id: str,
    user: AuthUser = Depends(get_auth_user),
    mongo_db=Depends(get_mongo_db),
):
    thread_service = ThreadService(mongo_db)
    thread = thread_service.get_thread(thread_id, user.id)
    return ThreadDataResponse(**thread)


@router.post("/trigger-ai-response")
async def trigger_ai_response(
    request: TriggerAIRequest,
    auth_user: AuthUser = Depends(get_auth_user),
    mongo_db=Depends(get_mongo_db),
):
    thread_service = ThreadService(mongo_db)

    return StreamingResponse(
        thread_service.trigger_ai_response(request.thread_id, auth_user.id, request.message_id),
        media_type="text/event-stream",
    )
