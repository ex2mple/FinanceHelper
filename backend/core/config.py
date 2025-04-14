from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_URL_ALEMBIC: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_ECHO: bool = False
    api_v1_prefix: str = "/api/v1"
    SQUARE_SIZE: int = 256
    mistral_api_key: str
    mistral_large_agent_id: str
    mistral_small_agent_id: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()