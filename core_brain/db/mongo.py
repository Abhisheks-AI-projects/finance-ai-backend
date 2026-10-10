from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

client = MongoClient(settings.mongo_url)

mongo_db = client[settings.mongo_db_name]


def get_mongo_db() -> Database:
    return mongo_db
