"""Конфигурация приложения. Секреты берутся только из переменных окружения."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # читает .env, если он есть (в Git не попадает)


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    db_name: str
    timeout_ms: int
    log_level: str


def get_settings() -> Settings:
    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        db_name=os.getenv("DB_NAME", "lab9"),
        timeout_ms=int(os.getenv("MONGO_TIMEOUT_MS", "3000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
