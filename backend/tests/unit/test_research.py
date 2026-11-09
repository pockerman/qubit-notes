"""The AI writing, searching the web (features/writing_assistant.feature): what Anthropic's and OpenAI's models answer,
as their SDKs give it, made Markdown citing its sources by number."""

from types import SimpleNamespace as Shape

import anthropic
import openai
import pytest

from qubit_notes.platform.port import Message, PlatformError, WebSource, chosen_ai
from qubit_notes.platform.standalone.ai import ProviderAI
from qubit_notes.settings import Settings

A = WebSource(title="Finite elements, a primer", url="https://example.edu/fem")
B = WebSource(title="Shape functions", url="https://example.org/shape")


def _ai(provider: str) -> ProviderAI:
    return ProviderAI(Settings(llm_provider=provider, anthropic_api_key="a-key", openai_api_key="o-key"))


def _text(text: str, *cited: WebSource):
    citations = [Shape(type="web_search_result_location", url=s.url, title=s.title, cited_text="…") for s in cited]
    return Shape(type="text", text=text, citations=citations or None)


def _anthropic(monkeypatch, *responses) -> list[dict]:
    """Anthropic's client, answering with the responses in turn; what it was asked, each time"""
    asked: list[dict] = []
    answers = iter(responses)

    class Client:
        def __init__(self, api_key):
            assert api_key == "a-key"
            self.messages = self

        def create(self, **arguments):
            asked.append({**arguments, "messages": list(arguments["messages"])})
            return next(answers)

    monkeypatch.setattr(anthropic, "Anthropic", Client)
    return asked


def _response(content, stop_reason="end_turn", tokens=(10, 20)):
    return Shape(content=content, stop_reason=stop_reason, usage=Shape(input_tokens=tokens[0], output_tokens=tokens[1]))


def test_anthropic_cites_its_sources_by_number(monkeypatch):
    asked = _anthropic(
        monkeypatch,
        _response(
            [
                _text("I'll search for that."),
                Shape(type="server_tool_use"),
                Shape(type="web_search_tool_result"),
                _text("The method divides a domain into elements", A),
                _text(", interpolated by shape functions", B, A),
                _text("."),
            ]
        ),
    )
    history = [Message(role="user", content="Earlier"), Message(role="assistant", content="Its reply")]
    researched = _ai("anthropic").research("System", "Write it", history, search_web=True)

    # what it said before its search isn't the answer
    assert researched.text == ("The method divides a domain into elements [1], interpolated by shape functions [2][1].")
    assert researched.sources == [A, B]
    assert researched.searched is True
    assert (researched.provider, researched.input_tokens, researched.output_tokens) == ("anthropic", 10, 20)
    assert asked[0]["tools"] == [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]
    assert asked[0]["system"] == "System"
    assert [m["content"] for m in asked[0]["messages"]] == ["Earlier", "Its reply", "Write it"]


def test_anthropic_goes_on_with_a_paused_search(monkeypatch):
    paused = [Shape(type="server_tool_use")]
    asked = _anthropic(
        monkeypatch,
        _response(paused, stop_reason="pause_turn", tokens=(5, 1)),
        _response([Shape(type="web_search_tool_result"), _text("Done", A)], tokens=(7, 3)),
    )
    researched = _ai("anthropic").research("System", "Write it", [], search_web=True)

    assert researched.text == "Done [1]"
    assert (researched.input_tokens, researched.output_tokens) == (12, 4)
    # the paused turn is sent back as it is, with no new request after it
    assert asked[1]["messages"][-1] == {"role": "assistant", "content": paused}
    assert len(asked[1]["messages"]) == 2


def test_anthropic_without_searching_the_web(monkeypatch):
    asked = _anthropic(monkeypatch, _response([_text("From what it knows.")]))
    researched = _ai("anthropic").research("System", "Write it", [], search_web=False)

    assert asked[0]["tools"] == []
    assert (researched.text, researched.sources, researched.searched) == ("From what it knows.", [], False)


def test_anthropic_declining_says_so(monkeypatch):
    _anthropic(monkeypatch, _response([], stop_reason="refusal"))
    with pytest.raises(PlatformError, match="declined"):
        _ai("anthropic").research("System", "Write it", [], search_web=True)


def _openai(monkeypatch, response) -> list[dict]:
    asked: list[dict] = []

    class Client:
        def __init__(self, api_key):
            assert api_key == "o-key"
            self.responses = self

        def create(self, **arguments):
            asked.append(arguments)
            return response

    monkeypatch.setattr(openai, "OpenAI", Client)
    return asked


def _cited(text: str, inline: str, source: WebSource):
    start = text.index(inline)
    return Shape(
        type="url_citation", url=source.url, title=source.title, start_index=start, end_index=start + len(inline)
    )


def test_openai_cites_its_sources_by_number(monkeypatch):
    text = (
        "The method divides a domain ([primer](https://example.edu/fem)). "
        "Shape functions ([shape](https://example.org/shape)) interpolate it."
    )
    annotations = [
        _cited(text, " ([primer](https://example.edu/fem))", A),
        _cited(text, " ([shape](https://example.org/shape))", B),
    ]
    asked = _openai(
        monkeypatch,
        Shape(
            output=[
                Shape(type="web_search_call"),
                Shape(type="message", content=[Shape(type="output_text", text=text, annotations=annotations)]),
            ],
            usage=Shape(input_tokens=30, output_tokens=40),
        ),
    )
    token = chosen_ai.set(("openai", "gpt-5"))
    try:
        researched = _ai("anthropic").research("System", "Write it", [], search_web=True)
    finally:
        chosen_ai.reset(token)

    assert researched.text == "The method divides a domain [1]. Shape functions [2] interpolate it."
    assert researched.sources == [A, B]
    assert researched.searched is True
    assert (researched.provider, researched.model) == ("openai", "gpt-5")
    assert (researched.input_tokens, researched.output_tokens) == (30, 40)
    assert asked[0]["tools"] == [{"type": "web_search"}]
    assert asked[0]["instructions"] == "System"


def test_openai_without_searching_the_web(monkeypatch):
    asked = _openai(
        monkeypatch,
        Shape(
            output=[Shape(type="message", content=[Shape(type="output_text", text="Known.", annotations=[])])],
            usage=None,
        ),
    )
    researched = _ai("openai").research("System", "Write it", [], search_web=False)

    assert asked[0]["tools"] == []
    assert (researched.text, researched.sources, researched.searched) == ("Known.", [], False)


def test_a_provider_without_its_key_says_so():
    ai = ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key=None, openai_api_key=None))
    with pytest.raises(PlatformError, match="FAILED_PRECONDITION"):
        ai.research("System", "Write it", [], search_web=True)
