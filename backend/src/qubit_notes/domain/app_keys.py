"""The app's model providers' keys, given by its admins from the app (features/app_keys.feature). The app's own
platform takes its keys from its settings; a key they don't give, an admin can, and the app keeps it in its database,
encrypted with its secret, to give the platform again when it starts. A key in the settings is used rather than one
kept. gogi keeps the app's keys itself, as its credentials."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.errors import Conflict, NotAllowed, NotFound
from qubit_notes.platform.port import StudyPlatform
from qubit_notes.settings import PROVIDER_NAMES, Settings

table = storage.app_keys

# the model providers the app has keys for: its AI's and its embedding model's
PROVIDERS = ("anthropic", "openai", "voyage")


class KeyState(BaseModel):
    provider: str
    # whether the app has the provider's key, given by an admin or by its settings; the key itself is never given
    given: bool
    # whether the app's settings give it, which is used rather than one an admin gives, and isn't removed from the app
    in_settings: bool


class AppKeys:
    def __init__(self, engine: Engine, settings: Settings, platform: StudyPlatform):
        self._engine = engine
        self._settings = settings
        self._platform = platform
        self.admins = settings.admin_names

    def is_admin(self, student: str) -> bool:
        return student in self.admins

    def give(self, student: str, provider: str, key: str) -> None:
        """the app uses this key for the provider from now on, and has it again when it restarts"""
        if not self.is_admin(student):
            raise NotAllowed("only the app's admins can give it keys")
        if provider not in PROVIDERS:
            raise NotFound(f"the app has no provider {provider!r}: its providers are {', '.join(PROVIDERS)}")
        key = key.strip()
        if not self._platform.keeps_keys:
            fernet = self._fernet()
            if fernet is None:
                raise Conflict("the app can't keep keys without its secret: set QUBIT_NOTES_SECRET_KEY first")
            with self._engine.begin() as connection:
                connection.execute(delete(table).where(table.c.provider == provider))
                connection.execute(
                    insert(table).values(provider=provider, encrypted=fernet.encrypt(key.encode()).decode())
                )
        if not self._in_settings(provider):
            self._platform.use_key(provider, key)

    def states(self) -> list[KeyState]:
        """whether the app has each provider's key, and where from"""
        return [
            KeyState(provider=p, given=self._platform.has_key(p), in_settings=self._in_settings(p)) for p in PROVIDERS
        ]

    def take_back(self, student: str, provider: str) -> None:
        """the app has no key for the provider from now on, nor when it restarts; one its settings give stays"""
        if not self.is_admin(student):
            raise NotAllowed("only the app's admins can remove its keys")
        if provider not in PROVIDERS:
            raise NotFound(f"the app has no provider {provider!r}: its providers are {', '.join(PROVIDERS)}")
        name = PROVIDER_NAMES[provider]
        if self._in_settings(provider):
            raise Conflict(f"the app's settings give its {name} key, so it can't be removed here")
        if self._platform.keeps_keys:
            raise Conflict(f"gogi keeps the app's keys: its {name} key can be replaced, but not removed, here")
        with self._engine.begin() as connection:
            removed = connection.execute(delete(table).where(table.c.provider == provider)).rowcount
        if not removed:
            raise NotFound(f"the app was given no {name} key")
        self._platform.use_key(provider, None)

    def restore(self) -> None:
        """gives the platform the keys kept, but for those the settings give"""
        if self._platform.keeps_keys:
            return
        with self._engine.connect() as connection:
            kept = connection.execute(select(table.c.provider, table.c.encrypted)).all()
        if not kept:
            return
        fernet = self._fernet()
        if fernet is None:
            logger.warning("the app keeps keys, but has no secret to read them with: set QUBIT_NOTES_SECRET_KEY")
            return
        for provider, encrypted in kept:
            if self._in_settings(provider):
                continue
            try:
                self._platform.use_key(provider, fernet.decrypt(encrypted.encode()).decode())
            except InvalidToken:
                logger.warning(f"the key kept for {provider} was encrypted with another secret: give it again")

    def _in_settings(self, provider: str) -> bool:
        return bool(getattr(self._settings, f"{provider}_api_key", None))

    def _fernet(self) -> Fernet | None:
        if not self._settings.secret_key:
            return None
        # Fernet takes a key of 32 bytes; the secret is any text
        return Fernet(base64.urlsafe_b64encode(hashlib.sha256(self._settings.secret_key.encode()).digest()))
