"""The embedding models the app's own platform embeds material with, named by QUBIT_NOTES_EMBEDDING_MODEL:

- bge-small-en-v1.5 and all-minilm-l6-v2 run in the app, with fastembed; they're downloaded the first time they're
  used, and need no key
- voyage-* models, e.g. voyage-3.5-lite, run at Voyage AI, with QUBIT_NOTES_VOYAGE_API_KEY
- text-embedding-3-* models run at OpenAI, with QUBIT_NOTES_OPENAI_API_KEY
"""

import threading
from typing import Protocol

import httpx

from qubit_notes.platform.port import PlatformError
from qubit_notes.settings import Settings

# the models that run in the app, by name, as fastembed names them
IN_APP = {
    "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
    "all-minilm-l6-v2": "sentence-transformers/all-MiniLM-L6-v2",
}


class Embedder(Protocol):
    # the model's name, kept with every chunk it embeds
    model: str

    def embed(self, texts: list[str], query: bool = False) -> list[list[float]]:
        """the texts' embeddings; a query is embedded as models want what is searched for"""
        ...

    def missing(self) -> str | None:
        """what the model needs and doesn't have, e.g. its key; None if it can embed"""
        ...

    def missing_key(self) -> str | None:
        """the model provider whose key the model needs and doesn't have"""
        ...

    def use_key(self, provider: str, key: str) -> None:
        """embeds with this key from now on, if the model is that provider's"""
        ...


class InAppEmbedder:
    def __init__(self, model: str, cache_dir: str | None = None):
        self.model = model
        self._cache_dir = cache_dir
        self._embedding = None
        self._lock = threading.Lock()

    def _loaded(self):
        # loaded when first used, so the app starts at once; requests and ingestion share it
        with self._lock:
            if self._embedding is None:
                from fastembed import TextEmbedding

                self._embedding = TextEmbedding(IN_APP[self.model], cache_dir=self._cache_dir)
            return self._embedding

    def embed(self, texts: list[str], query: bool = False) -> list[list[float]]:
        embedding = self._loaded()
        vectors = embedding.query_embed(texts) if query else embedding.passage_embed(texts)
        return [vector.tolist() for vector in vectors]

    def missing(self) -> str | None:
        return None

    def missing_key(self) -> str | None:
        return None

    def use_key(self, provider: str, key: str) -> None:
        pass


class VoyageEmbedder:
    URL = "https://api.voyageai.com/v1/embeddings"
    # the most texts Voyage AI takes in one request
    BATCH = 128

    def __init__(self, model: str, api_key: str | None):
        self.model = model
        self._api_key = api_key

    def embed(self, texts: list[str], query: bool = False) -> list[list[float]]:
        _require(self)
        vectors = []
        for start in range(0, len(texts), self.BATCH):
            response = httpx.post(
                self.URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "input": texts[start : start + self.BATCH],
                    "model": self.model,
                    "input_type": "query" if query else "document",
                },
                timeout=60,
            )
            if response.status_code != 200:
                raise PlatformError("EMBEDDING_FAILED", f"Voyage AI refused: {response.status_code} {response.text}")
            data = sorted(response.json()["data"], key=lambda item: item["index"])
            vectors.extend(item["embedding"] for item in data)
        return vectors

    def missing(self) -> str | None:
        return None if self._api_key else _no_key("voyage")

    def missing_key(self) -> str | None:
        return None if self._api_key else "voyage"

    def use_key(self, provider: str, key: str) -> None:
        if provider == "voyage":
            self._api_key = key


class OpenAIEmbedder:
    BATCH = 256

    def __init__(self, model: str, api_key: str | None):
        self.model = model
        self._api_key = api_key

    def embed(self, texts: list[str], query: bool = False) -> list[list[float]]:
        _require(self)
        import openai

        client = openai.OpenAI(api_key=self._api_key)
        vectors = []
        try:
            for start in range(0, len(texts), self.BATCH):
                response = client.embeddings.create(model=self.model, input=texts[start : start + self.BATCH])
                vectors.extend(item.embedding for item in sorted(response.data, key=lambda item: item.index))
        except openai.OpenAIError as e:
            raise PlatformError("EMBEDDING_FAILED", f"OpenAI refused: {e}") from e
        return vectors

    def missing(self) -> str | None:
        return None if self._api_key else _no_key("openai")

    def missing_key(self) -> str | None:
        return None if self._api_key else "openai"

    def use_key(self, provider: str, key: str) -> None:
        if provider == "openai":
            self._api_key = key


def _no_key(provider: str) -> str:
    return f"the app has no key for {provider}: set QUBIT_NOTES_{provider.upper()}_API_KEY"


def _require(embedder: Embedder) -> None:
    if why := embedder.missing():
        raise PlatformError("FAILED_PRECONDITION", why)


def embedder_from(settings: Settings, model: str | None = None) -> Embedder:
    model = model or settings.embedding_model
    if model in IN_APP:
        return InAppEmbedder(model, settings.embedding_cache_dir)
    if model.startswith("voyage-"):
        return VoyageEmbedder(model, settings.voyage_api_key)
    if model.startswith("text-embedding-"):
        return OpenAIEmbedder(model, settings.openai_api_key)
    raise ValueError(
        f"unknown embedding model {model!r}: use {', '.join(IN_APP)}, a Voyage AI model (voyage-...) or an OpenAI "
        "one (text-embedding-...)"
    )
