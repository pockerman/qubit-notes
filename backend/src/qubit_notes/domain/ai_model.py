"""The AI's model (features/ai_model.feature): the provider and model the app's settings name, the provider's own
model if they name none, or those an admin chooses from the app, which the app keeps in its database and gives the
platform again when it starts."""

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.errors import InvalidRequest, NotAllowed
from qubit_notes.platform.port import StudyPlatform
from qubit_notes.settings import DEFAULT_MODELS, SUGGESTED_MODELS, Settings

table = storage.app_settings


class AIModelInUse(BaseModel):
    provider: str
    model: str
    # some of each provider's models, to choose from, and the one each uses unless another is chosen
    suggested: dict[str, list[str]]
    defaults: dict[str, str]
    # whether the app has each provider's key; the keys themselves are never given
    keys: dict[str, bool]
    # whether the app's settings give each provider's key, which is used rather than one an admin gives
    in_settings: dict[str, bool]


class AIModel:
    def __init__(self, engine: Engine, settings: Settings, platform: StudyPlatform):
        self._engine = engine
        self._settings = settings
        self._platform = platform

    def in_use(self) -> AIModelInUse:
        provider, model = self.current()
        return AIModelInUse(
            provider=provider,
            model=model,
            suggested=SUGGESTED_MODELS,
            defaults=DEFAULT_MODELS,
            keys={p: self._platform.has_key(p) for p in DEFAULT_MODELS},
            in_settings={p: bool(getattr(self._settings, f"{p}_api_key", None)) for p in DEFAULT_MODELS},
        )

    def current(self) -> tuple[str, str]:
        """the provider and model chosen, else the settings'; a provider without a model, with its own"""
        with self._engine.connect() as connection:
            chosen = dict(connection.execute(select(table.c.name, table.c.value)).all())
        if "llm_provider" in chosen:
            provider = chosen["llm_provider"]
            return provider, chosen.get("llm_model") or DEFAULT_MODELS[provider]
        return self._settings.llm_provider, self._settings.model

    def choose(self, admin: bool, provider: str, model: str | None) -> AIModelInUse:
        """the AI answers with the model from now on, and again when the app restarts; only admins choose"""
        if not admin:
            raise NotAllowed("only the app's admins can choose the AI's model")
        if provider not in DEFAULT_MODELS:
            raise InvalidRequest("the app's AI is Anthropic's or OpenAI's: choose anthropic or openai")
        model = (model or "").strip()
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.name.in_(("llm_provider", "llm_model"))))
            connection.execute(insert(table).values(name="llm_provider", value=provider))
            if model:
                connection.execute(insert(table).values(name="llm_model", value=model))
        self.restore()
        return self.in_use()

    def chosen(self, provider: str) -> tuple[str, str] | None:
        """the provider a student chose to answer them, with the app's model if it is the app's provider, else the
        provider's own; None if the app has no such provider, or not its key, so the app's answers"""
        if provider not in DEFAULT_MODELS:
            return None
        current = self.current()
        if provider == current[0]:
            return current
        if not self._platform.has_key(provider):
            return None
        return provider, DEFAULT_MODELS[provider]

    def restore(self) -> None:
        """gives the platform the model to answer with"""
        self._platform.use_model(*self.current())
