from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "InsuranceAPI"
    APP_ENV: str = "development"
    DEBUG: bool = False

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/insurance_db"

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
