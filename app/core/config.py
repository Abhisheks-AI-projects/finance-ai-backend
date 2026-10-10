from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Finance AI Backend"
    environment: str = "dev"

    # Database URLs
    postgres_url: str
    mongo_url: str
    mongo_db_name: str
    clerk_secret_key: str
    clerk_jwt_key: str

    # LLM key
    groq_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()