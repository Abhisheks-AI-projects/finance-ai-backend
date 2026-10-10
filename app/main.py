from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.postgres import Base, engine
from core_brain.db.mongo import get_mongo_db
from app.api.routes import auth
from app.api.routes import thread

# Import all models so Base.metadata knows about them
from app.models.user import User
from app.models.transaction import Transaction
from app.models.budget import Budget

# DEV ONLY: Auto-create tables on startup. In production, use `alembic upgrade head` instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(thread.router)

@app.get("/")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        postgres_status = "connected"
    except Exception:
        postgres_status = "not connected"

    try:
        get_mongo_db().command("ping")
        mongo_status = "connected"
    except Exception:
        mongo_status = "not connected"

    return {
        "status": "ok",
        "environment": settings.environment,
        "postgres": postgres_status,
        "mongo": mongo_status,
    }