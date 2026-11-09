"""The AI of the app's own platform: the model provider QUBIT_NOTES_LLM_PROVIDER names, or the one the admins
choose, called with the app's key."""

import json
from typing import Any, Protocol

from qubit_notes.platform.port import Completion, Message, PlatformError, Researched, Speech, WebSource, chosen_ai
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

    def research(self, system: str, prompt: str, history: list[Message] | None, search_web: bool) -> Researched:
        """what the AI writes, searching the web, unless told not to, its text citing its sources by number"""
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

    # writing, searching the web (features/writing_assistant.feature)

    def research(self, system: str, prompt: str, history: list[Message] | None, search_web: bool) -> Researched:
        provider, model = chosen_ai.get() or (self._provider, self._model)
        key = self._keys.get(provider)
        if not key:
            raise PlatformError("FAILED_PRECONDITION", missing_key(provider))
        messages = [{"role": m.role, "content": m.content} for m in history or []]
        messages.append({"role": "user", "content": prompt})
        if provider == "anthropic":
            return self._anthropic_research(model, key, system, messages, search_web)
        return self._openai_research(model, key, system, messages, search_web)

    def _anthropic_research(
        self, model: str, key: str, system: str, messages: list[dict], search_web: bool
    ) -> Researched:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": WEB_SEARCHES}] if search_web else []
        conversation = list(messages)
        input_tokens = output_tokens = 0
        content: list = []
        try:
            # a long search pauses the turn; it is sent back as it is for the server to go on with it
            for _ in range(MAX_CONTINUATIONS):
                response = client.messages.create(
                    model=model,
                    max_tokens=max(self._settings.llm_max_tokens, RESEARCH_MAX_TOKENS),
                    system=system,
                    messages=conversation,
                    tools=tools,
                )
                input_tokens += response.usage.input_tokens
                output_tokens += response.usage.output_tokens
                content += list(response.content)
                if response.stop_reason != "pause_turn":
                    break
                conversation.append({"role": "assistant", "content": response.content})
        except anthropic.APIError as e:
            raise PlatformError("AI_FAILED", f"Anthropic refused: {e}") from e
        if response.stop_reason == "refusal":
            raise PlatformError("AI_FAILED", "Anthropic's model declined to write that")
        searched = any(block.type == "web_search_tool_result" for block in content)
        # what it wrote after its last search is the answer; before, it says what it is about to search
        last = max((i for i, block in enumerate(content) if block.type == "web_search_tool_result"), default=-1)
        numbered = _Numbered()
        parts = []
        for block in content[last + 1 :]:
            if block.type != "text":
                continue
            cited = [c for c in block.citations or [] if c.type == "web_search_result_location"]
            markers = "".join(dict.fromkeys(f"[{numbered.of(c.url, c.title)}]" for c in cited))
            parts.append(block.text + (f" {markers}" if markers else ""))
        return Researched(
            text="".join(parts).strip(),
            sources=numbered.sources,
            searched=searched,
            provider="anthropic",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def _openai_research(self, model: str, key: str, system: str, messages: list[dict], search_web: bool) -> Researched:
        import openai

        try:
            response = openai.OpenAI(api_key=key).responses.create(
                model=model,
                instructions=system,
                input=messages,
                tools=[{"type": "web_search"}] if search_web else [],
                max_output_tokens=max(self._settings.llm_max_tokens, RESEARCH_MAX_TOKENS),
            )
        except openai.OpenAIError as e:
            raise PlatformError("AI_FAILED", f"OpenAI refused: {e}") from e
        numbered = _Numbered()
        parts = []
        for item in response.output:
            if item.type != "message":
                continue
            for part in item.content:
                if part.type != "output_text":
                    continue
                text = part.text
                # each citation, from the last, made a numbered marker in the place of what cites it
                cited = [a for a in part.annotations if a.type == "url_citation"]
                numbers = {id(a): numbered.of(a.url, a.title) for a in sorted(cited, key=lambda a: a.start_index)}
                for annotation in sorted(cited, key=lambda a: a.start_index, reverse=True):
                    marker = f"[{numbers[id(annotation)]}]"
                    text = f"{text[: annotation.start_index].rstrip()} {marker}{text[annotation.end_index :]}"
                parts.append(text)
        usage = response.usage
        return Researched(
            text="".join(parts).strip(),
            sources=numbered.sources,
            searched=any(item.type == "web_search_call" for item in response.output),
            provider="openai",
            model=model,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
        )


# how many times the AI may search the web for one request, and how many times a paused search is gone on with
WEB_SEARCHES = 5
MAX_CONTINUATIONS = 5
# what writing takes, at least: material is longer than an answer
RESEARCH_MAX_TOKENS = 16_000


class _Numbered:
    """the sources cited, numbered in the order they are first cited"""

    def __init__(self):
        self.sources: list[WebSource] = []
        self._numbers: dict[str, int] = {}

    def of(self, url: str, title: str | None) -> int:
        if url not in self._numbers:
            self.sources.append(WebSource(title=title or url, url=url))
            self._numbers[url] = len(self.sources)
        return self._numbers[url]
