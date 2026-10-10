from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from pymongo.database import Database
from pymongo.errors import PyMongoError

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core_brain.prompts.finance_prompt import FINANCE_SYSTEM_PROMPT
from core_brain.repositories.thread_repository import ThreadRepository
from core_brain.finance_agent.agent import chat_with_finance_agent
from app.schemas.thread import Thread, Message, MessageType


class ThreadService:
    def __init__(self, db: Database):
        self.thread_repository = ThreadRepository(db)

    def create_thread(self, user_id: str) -> Thread:
        now = datetime.now(timezone.utc)

        thread = Thread(
            thread_id=str(uuid4()),
            user_id=user_id,
            title=None,
            messages=[],
            is_shared=False,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )

        try:
            self.thread_repository.create_thread(thread)
        except PyMongoError:
            raise HTTPException(
                status_code=503,
                detail="Unable to create thread. Please try again later.",
            )

        return thread

    def add_message(self, thread_id: str, user_id: str, content: str, message_type: MessageType) -> Message:
        now = datetime.now(timezone.utc)

        message = Message(
            message_type=message_type,
            content=content,
            timestamp=now,
        )

        result = self.thread_repository.push_message(thread_id, user_id, message)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Thread not found")

        return message

    def get_thread(self, thread_id: str, user_id: str) -> dict:
        thread = self.thread_repository.get_thread(thread_id, user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread

    def list_threads(self, user_id: str) -> list[dict]:
        return self.thread_repository.list_threads(user_id)

    def build_finance_agent_prompt(self, thread_id: str, user_id: str, message_id: str) -> list:
        raw_messages = self.thread_repository.get_thread_messages(thread_id, user_id)

        if not raw_messages:
            raise HTTPException(status_code=404, detail="Thread not found")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        prompt = [SystemMessage(content=FINANCE_SYSTEM_PROMPT + f"\n\nToday's date is: {today}")]
        user_message = None

        for raw in raw_messages:
            msg = Message(**raw)
            if msg.message_id == message_id:
                user_message = msg
            elif msg.message_type == MessageType.user:
                prompt.append(HumanMessage(content=msg.content))
            else:
                prompt.append(AIMessage(content=msg.content))

        if not user_message:
            raise HTTPException(status_code=404, detail="Message not found")

        prompt.append(HumanMessage(content=user_message.content))
        return prompt

    async def trigger_ai_response(self, thread_id: str, user_id: str, message_id: str):
        import json

        prompt = self.build_finance_agent_prompt(thread_id, user_id, message_id)

        full_response = ""
        async for chunk in chat_with_finance_agent(prompt, user_id):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        # save full AI response to thread
        message = self.add_message(thread_id, user_id, full_response, MessageType.ai)
        yield f"data: {json.dumps({'type': 'done', 'message': message.model_dump(mode='json')})}\n\n"