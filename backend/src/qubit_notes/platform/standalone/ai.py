"""The AI of the app's own platform: the model provider QUBIT_NOTES_LLM_PROVIDER names, called with the app's key."""

import json
from typing import Any, Protocol

from qubit_notes.platform.port import Message, PlatformError
from qubit_notes.settings import Settings

PROVIDERS = ("anthropic", "openai")


class AI(Protocol):
    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str: ...

    def missing(self) -> str | None:
        """what the AI needs and doesn't have, e.g. its key; None if it can answer"""
        ...


class ProviderAI:
    """Anthropic's or OpenAI's models. A JSON answer is asked of Anthropic's as the input of a tool it must call,
    which follows the schema, and of OpenAI's as its response format."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._provider = settings.llm_provider
        if self._provider not in PROVIDERS:
            raise ValueError(f"unknown model provider {self._provider!r}: use one of {', '.join(PROVIDERS)}")
        self._key = settings.anthropic_api_key if self._provider == "anthropic" else settings.openai_api_key

    def missing(self) -> str | None:
        if self._key:
            return None
        return f"the app has no key for {self._provider}: set QUBIT_NOTES_{self._provider.upper()}_API_KEY"

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
        if why := self.missing():
            raise PlatformError("FAILED_PRECONDITION", why)
        messages = [{"role": m.role, "content": m.content} for m in history or []]
        messages.append({"role": "user", "content": prompt})
        if self._provider == "anthropic":
            return self._anthropic(system, messages, json_schema)
        return self._openai(system, messages, json_schema)

    def _anthropic(self, system: str, messages: list[dict], json_schema: dict | None) -> str:
        import anthropic

        arguments: dict[str, Any] = {
            "model": self._settings.llm_model,
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
            response = anthropic.Anthropic(api_key=self._key).messages.create(**arguments)
        except anthropic.APIError as e:
            raise PlatformError("AI_FAILED", f"Anthropic refused: {e}") from e
        if json_schema:
            answer = next((block.input for block in response.content if block.type == "tool_use"), None)
            if answer is None:
                raise PlatformError("AI_FAILED", "Anthropic's model gave no answer")
            return json.dumps(answer)
        return "".join(block.text for block in response.content if block.type == "text")

    def _openai(self, system: str, messages: list[dict], json_schema: dict | None) -> str:
        import openai

        arguments: dict[str, Any] = {
            "model": self._settings.llm_model,
            "max_completion_tokens": self._settings.llm_max_tokens,
            "messages": [{"role": "system", "content": system}, *messages],
        }
        if json_schema:
            arguments["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "answer", "schema": json_schema},
            }
        try:
            response = openai.OpenAI(api_key=self._key).chat.completions.create(**arguments)
        except openai.OpenAIError as e:
            raise PlatformError("AI_FAILED", f"OpenAI refused: {e}") from e
        return response.choices[0].message.content or ""
