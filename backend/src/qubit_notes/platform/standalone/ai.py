"""The AI of the app's own platform: the model provider QUBIT_NOTES_LLM_PROVIDER names, or the one the admins
choose, called with the app's key."""

import json
from typing import Any, Protocol

from qubit_notes.platform.port import Completion, Message, PlatformError, Speech, chosen_ai
from qubit_notes.settings import DEFAULT_MODELS, Settings, missing_key

PROVIDERS = tuple(DEFAULT_MODELS)


class AI(Protocol):
    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> Completion: ...

    def missing(self) -> str | None:
        """what the AI needs and doesn't have, e.g. its key; None if it can answer"""
        ...

    def missing_key(self) -> str | None:
        """the model provider whose key the AI needs and doesn't have"""
        ...

    def use_key(self, provider: str, key: str | None) -> None:
        """calls the model provider with this key from now on, if it calls that provider; None: with none"""
        ...

    def use_model(self, provider: str, model: str) -> None:
        """answers with this model of this provider from now on"""
        ...

    def has_key(self, provider: str) -> bool:
        """whether it has the provider's key"""
        ...

    def speak(self, text: str, instructions: str, model: str) -> Speech:
        """the text read aloud by one of OpenAI's speech models, as MP3; told how to speak it, if instructions say"""
        ...


class ProviderAI:
    """Anthropic's or OpenAI's models. A JSON answer is asked of Anthropic's as the input of a tool it must call,
    which follows the schema, and of OpenAI's as its response format."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._keys = {"anthropic": settings.anthropic_api_key, "openai": settings.openai_api_key}
        self.use_model(settings.llm_provider, settings.model)

    @property
    def _key(self) -> str | None:
        return self._keys.get(self._provider)

    def missing(self) -> str | None:
        return None if self._key else missing_key(self._provider)

    def missing_key(self) -> str | None:
        return None if self._key else self._provider

    def use_key(self, provider: str, key: str | None) -> None:
        if provider in self._keys:
            self._keys[provider] = key

    def use_model(self, provider: str, model: str) -> None:
        if provider not in PROVIDERS:
            raise ValueError(f"unknown model provider {provider!r}: use one of {', '.join(PROVIDERS)}")
        self._provider, self._model = provider, model

    def has_key(self, provider: str) -> bool:
        return bool(self._keys.get(provider))

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> Completion:
        # the model the student chose, else the app's
        provider, model = chosen_ai.get() or (self._provider, self._model)
        key = self._keys.get(provider)
        if not key:
            raise PlatformError("FAILED_PRECONDITION", missing_key(provider))
        messages = [{"role": m.role, "content": m.content} for m in history or []]
        messages.append({"role": "user", "content": prompt})
        if provider == "anthropic":
            return self._anthropic(model, key, system, messages, json_schema)
        return self._openai(model, key, system, messages, json_schema)

    def speak(self, text: str, instructions: str, model: str) -> Speech:
        import openai

        key = self._keys.get("openai")
        if not key:
            raise PlatformError("FAILED_PRECONDITION", missing_key("openai"))
        # tts-1 and tts-1-hd take no instructions
        told = {"instructions": instructions} if instructions else {}
        try:
            response = openai.OpenAI(api_key=key).audio.speech.create(
                model=model, voice=self._settings.speech_voice, input=text, response_format="mp3", **told
            )
        except openai.OpenAIError as e:
            raise PlatformError("AI_FAILED", f"OpenAI refused: {e}") from e
        return Speech(audio=response.content, provider="openai", model=model)

    def _anthropic(
        self, model: str, key: str, system: str, messages: list[dict], json_schema: dict | None
    ) -> Completion:
        import anthropic

        arguments: dict[str, Any] = {
            "model": model,
            "max_tokens": self._settings.llm_max_tokens,
            "system": system,
            "messages": messages,
        }
        if json_schema:
            arguments["tools"] = [
                {"name": "answer", "description": "Give the answer.", "input_schema": json_schema},
            ]
            arguments["tool_choice"] = {"type": "tool", "name": "answer"}
        try:
            response = anthropic.Anthropic(api_key=key).messages.create(**arguments)
        except anthropic.APIError as e:
            raise PlatformError("AI_FAILED", f"Anthropic refused: {e}") from e
        if json_schema:
            answer = next((block.input for block in response.content if block.type == "tool_use"), None)
            if answer is None:
                raise PlatformError("AI_FAILED", "Anthropic's model gave no answer")
            text = json.dumps(answer)
        else:
            text = "".join(block.text for block in response.content if block.type == "text")
        return Completion(
            text=text,
            provider="anthropic",
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def _openai(self, model: str, key: str, system: str, messages: list[dict], json_schema: dict | None) -> Completion:
        import openai

        arguments: dict[str, Any] = {
            "model": model,
            "max_completion_tokens": self._settings.llm_max_tokens,
            "messages": [{"role": "system", "content": system}, *messages],
        }
        if json_schema:
            arguments["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "answer", "schema": json_schema},
            }
        try:
            response = openai.OpenAI(api_key=key).chat.completions.create(**arguments)
        except openai.OpenAIError as e:
            raise PlatformError("AI_FAILED", f"OpenAI refused: {e}") from e
        return Completion(
            text=response.choices[0].message.content or "",
            provider="openai",
            model=model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        )
