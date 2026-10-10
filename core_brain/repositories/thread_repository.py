from datetime import datetime, timezone

from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult

from app.schemas.thread import Thread, Message


class ThreadRepository:
    def __init__(self, mongo_db: Database):
        self.thread_collection = mongo_db.threads

    def create_thread(self, thread: Thread) -> InsertOneResult:
        return self.thread_collection.insert_one(thread.model_dump())

    def push_message(self, thread_id: str, user_id: str, message: Message) -> UpdateResult:
        return self.thread_collection.update_one(
            {"thread_id": thread_id, "user_id": user_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

    def get_thread(self, thread_id: str, user_id: str) -> dict | None:
        return self.thread_collection.find_one(
            {"thread_id": thread_id, "user_id": user_id, "is_deleted": False},
            {"_id": 0},
        )

    def get_thread_messages(self, thread_id: str, user_id: str) -> list[dict]:
        thread = self.thread_collection.find_one(
            {"thread_id": thread_id, "user_id": user_id, "is_deleted": False},
            {"_id": 0, "messages": 1},
        )
        if not thread:
            return []
        return thread.get("messages", [])

    def list_threads(self, user_id: str) -> list[dict]:
        cursor = self.thread_collection.find(
            {"user_id": user_id, "is_deleted": False},
            {"_id": 0, "thread_id": 1, "title": 1, "created_at": 1, "updated_at": 1},
        ).sort("updated_at", -1)
        return list(cursor)
