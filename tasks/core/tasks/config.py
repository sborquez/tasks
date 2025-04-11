from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env")  # New way to load `.env`

    # Database
    FIRESTORE_PROJECT_ID: str = "demo-project"
    FIRESTORE_DATABASE: str = "(default)"

    FIRESTORE_EMULATOR_HOST: str | None = None

    # Task info
    TASK_PROJECT_ID: str | None = None
    TASK_REGION: str | None = None
    TASK_JOB_NAME: str | None = None

    # Default server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000
    SERVER_LOG_LEVEL: str = "info"
    SERVER_HEALTH_ENDPOINT: str = "/health"
    SERVER_PREDICT_ENDPOINT: str = "/predict"

settings = Settings()