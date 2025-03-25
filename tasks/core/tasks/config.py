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


settings = Settings()