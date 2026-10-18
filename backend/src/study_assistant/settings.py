from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The study assistant's configuration, read from ``STUDY_ASSISTANT_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="STUDY_ASSISTANT_", env_file=".env", extra="ignore")

    gateway_url: str = "localhost:50051"

    # how students sign in: by name, as in development, or with Amazon Cognito where the app is deployed
    auth: Literal["name", "cognito"] = "name"
    # the user pool and its app client, e.g. eu-west-2, eu-west-2_AbC123, and its sign-in pages' domain, e.g.
    # https://qubit-notes.auth.eu-west-2.amazoncognito.com
    cognito_region: str = ""
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_domain: str = ""
    # the issuer of the user pool's tokens; https://cognito-idp.<region>.amazonaws.com/<user pool> if unset
    cognito_issuer: str | None = None

    # the key gogi gave the app, where gogi serves many applications; not needed where gogi runs without keys
    gogi_api_key: str | None = None
    # the certificate authority to check gogi's gateway against, e.g. where gogi has no domain; else the system's
    gogi_ca_file: str | None = None
    # the app's own data (notes, summaries, quizzes); any SQLAlchemy URL, e.g. postgresql+psycopg://...
    database_url: str = "sqlite:///study-assistant.db"
    # the built frontend (frontend/dist), served at /; not served if unset
    frontend_dir: str | None = None

    # the largest file a student may upload; gogi refuses files larger than its own limit, 100 MB by default
    max_upload_mb: float = 100.0

    # the model that writes summaries and quizzes, through gogi's model service
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-5-5"
    llm_max_tokens: int = 4000
    # how much of a conversation with the assistant the model is given, in estimated tokens: its most recent messages
    conversation_tokens: int = 4000

    # how material is embedded; the default runs in gogi's worker and needs no API key
    embeddings_client: str = "sentence-transformer"
    embeddings_model: str = "clip"
    chunk_strategy: str = "fixed"

    @property
    def issuer(self) -> str:
        """the issuer of the Cognito user pool's tokens"""
        if self.cognito_issuer:
            return self.cognito_issuer.rstrip("/")
        if self.cognito_region and self.cognito_user_pool_id:
            return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}"
        return ""
