from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The study assistant's configuration, read from ``STUDY_ASSISTANT_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="STUDY_ASSISTANT_", env_file=".env", extra="ignore")

    gateway_url: str = "localhost:50051"
