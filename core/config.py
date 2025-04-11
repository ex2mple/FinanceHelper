from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_URL_ALEMBIC: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_ECHO: bool = False
    api_v1_prefix: str = "/api/v1"
    SQUARE_SIZE: int = 256


settings = Settings()