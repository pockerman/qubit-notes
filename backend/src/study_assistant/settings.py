from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The study assistant's configuration, read from ``STUDY_ASSISTANT_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="STUDY_ASSISTANT_", env_file=".env", extra="ignore")

    gateway_url: str = "localhost:50051"
    # the app's own data (notes, summaries, quizzes); any SQLAlchemy URL, e.g. postgresql+psycopg://...
    database_url: str = "sqlite:///study-assistant.db"
    # the built frontend (frontend/dist), served at /; not served if unset
    frontend_dir: str | None = None

    # the largest file a student may upload; gogi refuses files larger than its own limit, 100 MB by default
    max_upload_mb: float = 100.0

    # how material is embedded; the default runs in gogi's worker and needs no API key
    embeddings_client: str = "sentence-transformer"
    embeddings_model: str = "clip"
    chunk_strategy: str = "fixed"
