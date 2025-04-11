from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_URL_ALEMBIC: str = "postgresql+asyncpg://root:hackpassword@db/hack"
    DB_ECHO: bool = False
    api_v1_prefix: str = "/api/v1"
    SQUARE_SIZE: int = 256
    mistral_api_key: str = "20vEo5bCNAvcJznBwpJ7Py0i53ngdy3X"
    mistral_default_agent_id: str = "ag:5fe02e86:20250411:untitled-agent:6d9da368"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()