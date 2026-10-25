from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# the model providers, as students know them
PROVIDER_NAMES = {"anthropic": "Anthropic", "openai": "OpenAI", "voyage": "Voyage AI"}
# the providers of the app's AI, each with the model it uses unless another is named (features/ai_model.feature)
DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "openai": "gpt-5"}
# some of each provider's models, suggested where a model is chosen; any other is taken too
SUGGESTED_MODELS = {
    "anthropic": ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"],
    "openai": ["gpt-5", "gpt-5-mini", "gpt-5-nano"],
}


def missing_key(provider: str) -> str:
    """what the app says when it hasn't the provider's key, in words students may see: no setting is named"""
    return f"the app is missing its {PROVIDER_NAMES.get(provider, provider)} key"


class Settings(BaseSettings):
    """qubit-notes' configuration, read from ``QUBIT_NOTES_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="QUBIT_NOTES_", env_file=".env", extra="ignore")

    # what keeps the material, searches it, calls the AI and keeps conversations and memories: the app itself, or
    # the gogi platform (which needs gogi-python installed beside the app: make install-gogi)
    platform: Literal["standalone", "gogi"] = "standalone"

    # gogi's gateway, where the platform is gogi
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
    # where the app changes a student's email and password with their token; https://cognito-idp.<region>.amazonaws.com/
    # if unset
    cognito_api_url: str | None = None

    # the key gogi gave the app, where gogi serves many applications; not needed where gogi runs without keys
    gogi_api_key: str | None = None
    # the certificate authority to check gogi's gateway against, e.g. where gogi has no domain; else the system's
    gogi_ca_file: str | None = None
    # the app's own data (notes, summaries, quizzes); any SQLAlchemy URL, e.g. postgresql+psycopg://...
    database_url: str = "sqlite:///qubit-notes.db"
    # the built frontend (frontend/dist), served at /; not served if unset
    frontend_dir: str | None = None

    # the largest file a student may upload; gogi refuses files larger than its own limit, 100 MB by default
    max_upload_mb: float = 100.0

    # where the app's own platform keeps the uploaded files: an S3 bucket if set (e.g. where it's deployed on AWS),
    # else a directory
    files_bucket: str | None = None
    files_dir: str = "material"
    # the model providers' keys, for the app's own platform; where the platform is gogi, they're kept in gogi
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    voyage_api_key: str | None = None
    # who may give the app the keys it is missing, from the app: students' names, separated by commas, e.g. alex,maria
    admins: str = ""
    # what the keys the admins give the app are encrypted with, in its database; they can't be given without it
    secret_key: str | None = None
    # where an embedding model that runs in the app is downloaded to; a temporary directory if unset
    embedding_cache_dir: str | None = None
    # how many documents the app's own platform processes at once
    ingestion_workers: int = 2

    # the model that writes summaries and quizzes: anthropic or openai, and its model, by default the provider's own
    # (DEFAULT_MODELS); the app's admins can choose others from the app, which are used instead
    llm_provider: str = "anthropic"
    llm_model: str | None = None
    llm_max_tokens: int = 4000
    # how much of a conversation with the assistant the model is given, in estimated tokens: its most recent messages
    conversation_tokens: int = 4000

    # the model that embeds material for search: bge-small-en-v1.5 runs in the app (or in gogi) and needs no API key;
    # voyage-* models need the Voyage AI key, text-embedding-3-* ones the OpenAI key. Material embedded with one
    # model is not found by searching with another: after changing it, run qubit-notes reembed
    embedding_model: str = "bge-small-en-v1.5"
    # gogi's chunking strategy, where the platform is gogi
    chunk_strategy: str = "fixed"

    @property
    def model(self) -> str:
        """the AI's model: the one named, or its provider's own"""
        return self.llm_model or DEFAULT_MODELS.get(self.llm_provider, "")

    @property
    def admin_names(self) -> set[str]:
        return {name.strip() for name in self.admins.split(",") if name.strip()}

    @property
    def issuer(self) -> str:
        """the issuer of the Cognito user pool's tokens"""
        if self.cognito_issuer:
            return self.cognito_issuer.rstrip("/")
        if self.cognito_region and self.cognito_user_pool_id:
            return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}"
        return ""

    @property
    def cognito_api(self) -> str:
        """Cognito's API, where a student's own account is changed with their access token"""
        if self.cognito_api_url:
            return self.cognito_api_url
        return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/" if self.cognito_region else ""
