from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The study assistant's configuration, read from ``STUDY_ASSISTANT_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="STUDY_ASSISTANT_", env_file=".env", extra="ignore")

    gateway_url: str = "localhost:50051"
    # the built frontend (frontend/dist), served at /; not served if unset
    frontend_dir: str | None = None

    # the largest file a student may upload. gogi takes a file's content in one gRPC message, limited to 4 MB, and
    # passes it through its ingestion workflow, whose input a production Temporal server limits to about 2 MB
    max_upload_mb: float = 3.0

    # how material is embedded; the default runs in gogi's worker and needs no API key
    embeddings_client: str = "sentence-transformer"
    embeddings_model: str = "clip"
    chunk_strategy: str = "fixed"
