import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv(verbose=True)


class CommonSettings(BaseSettings):
    APP_NAME: str = "Arbocensus JOBS API"
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE')


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000


class Settings(CommonSettings, ServerSettings):
    pass


settings = Settings()
