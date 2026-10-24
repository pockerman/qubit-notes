"""The parts of the app's own platform the scenarios don't reach: PDFs with an outline, chunking, the files in S3, and
the model providers it calls, which are stood in for here."""

import json
from types import SimpleNamespace

import pytest

from qubit_notes.platform.port import Message, PlatformError, Section, SectionText
from qubit_notes.platform.standalone import chunking, parsing
from qubit_notes.platform.standalone.ai import ProviderAI
from qubit_notes.platform.standalone.embeddings import (
    InAppEmbedder,
    OpenAIEmbedder,
    VoyageEmbedder,
    embedder_from,
)
from qubit_notes.platform.standalone.files import S3Files
from qubit_notes.settings import Settings
from tests.pdfs import make_pdf


def test_a_pdf_is_read_by_its_outline():
    pdf = make_pdf(
        ["Intro text.", "Methods text.", "More methods.", "Results text."],
        outline=[("Introduction", 1, 1), ("Methods", 1, 2), ("Meshes", 2, 3), ("Results", 1, 4)],
    )

    found = parsing.sections("paper.pdf", pdf)

    assert [(s.section.title, s.section.level, s.section.page_start, s.section.page_end) for s in found] == [
        ("Introduction", 1, 1, 1),
        ("Methods", 1, 2, 2),
        ("Meshes", 2, 3, 3),
        ("Results", 1, 4, 4),
    ]
    assert found[1].content == "Methods text."


def test_chunks_overlap_and_never_span_sections():
    def section(position: int, words: int) -> SectionText:
        return SectionText(
            section=Section(position=position), content=" ".join(f"w{position}-{i}" for i in range(words))
        )

    found = chunking.chunks([section(1, 25), section(2, 5)], size=10, overlap=2)

    assert [position for position, _ in found] == [1, 1, 1, 2]
    assert found[0][1].split()[-2:] == found[1][1].split()[:2]
    assert found[2][1].split()[-1] == "w1-24"
    assert found[3][1] == "w2-0 w2-1 w2-2 w2-3 w2-4"


@pytest.mark.parametrize(
    ("model", "kind"),
    [
        ("bge-small-en-v1.5", InAppEmbedder),
        ("all-minilm-l6-v2", InAppEmbedder),
        ("voyage-3.5-lite", VoyageEmbedder),
        ("text-embedding-3-small", OpenAIEmbedder),
    ],
)
def test_the_embedding_model_is_the_settings(model, kind):
    assert isinstance(embedder_from(Settings(embedding_model=model)), kind)


def test_an_unknown_embedding_model_is_refused():
    with pytest.raises(ValueError, match="unknown embedding model"):
        embedder_from(Settings(embedding_model="clip"))


def test_a_model_without_its_key_says_so():
    embedder = VoyageEmbedder("voyage-3.5-lite", api_key=None)

    assert embedder.missing() == "the app is missing its Voyage AI key"
    with pytest.raises(PlatformError, match="missing its Voyage AI key"):
        embedder.embed(["text"])


def test_a_key_given_later_is_used():
    embedder = VoyageEmbedder("voyage-3.5-lite", api_key=None)
    ai = ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key=None))
    assert (embedder.missing_key(), ai.missing_key()) == ("voyage", "anthropic")

    # each takes only its own provider's key
    embedder.use_key("anthropic", "sk-ant")
    ai.use_key("anthropic", "sk-ant")
    embedder.use_key("voyage", "pa-voyage")

    assert (embedder.missing_key(), ai.missing_key()) == (None, None)
    assert embedder.missing() is None and ai.missing() is None


def test_voyage_embeds_documents_and_queries_in_batches(monkeypatch):
    requests = []

    def post(url, headers, json, timeout):
        requests.append(json)
        data = [{"index": i, "embedding": [float(i)]} for i in reversed(range(len(json["input"])))]
        return SimpleNamespace(status_code=200, json=lambda: {"data": data})

    monkeypatch.setattr("qubit_notes.platform.standalone.embeddings.httpx.post", post)
    embedder = VoyageEmbedder("voyage-3.5-lite", api_key="key")

    vectors = embedder.embed([f"text {i}" for i in range(130)])
    embedder.embed(["what"], query=True)

    assert [len(r["input"]) for r in requests] == [128, 2, 1]
    assert [r["input_type"] for r in requests] == ["document", "document", "query"]
    assert vectors[:3] == [[0.0], [1.0], [2.0]]


def test_openai_embeds_with_the_apps_key(monkeypatch):
    import openai

    calls = []

    class Client:
        def __init__(self, api_key):
            self.embeddings = SimpleNamespace(create=self.create)
            calls.append(api_key)

        def create(self, model, input):
            data = [SimpleNamespace(index=i, embedding=[float(len(text))]) for i, text in enumerate(input)]
            return SimpleNamespace(data=data)

    monkeypatch.setattr(openai, "OpenAI", Client)

    assert OpenAIEmbedder("text-embedding-3-small", api_key="key").embed(["a", "bbb"]) == [[1.0], [3.0]]
    assert calls == ["key"]


class FakeAnthropic:
    """records what the app asks of Anthropic's API, and answers with the given content blocks"""

    def __init__(self, content):
        self.asked = {}
        self._content = content

    def __call__(self, api_key):
        self.asked["api_key"] = api_key
        return SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **arguments):
        self.asked.update(arguments)
        return SimpleNamespace(content=self._content)


def test_anthropic_answers_in_json_through_a_tool(monkeypatch):
    import anthropic

    answer = {"request": "question", "answer": "It is assembled."}
    fake = FakeAnthropic([SimpleNamespace(type="tool_use", input=answer)])
    monkeypatch.setattr(anthropic, "Anthropic", fake)
    ai = ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key="key", llm_model="claude-sonnet-5-5"))
    schema = {"type": "object", "properties": {"request": {"type": "string"}}}

    reply = ai.complete(
        "be brief", "what is assembled?", json_schema=schema, history=[Message(role="user", content="hi")]
    )

    assert json.loads(reply) == answer
    assert fake.asked["api_key"] == "key"
    assert fake.asked["model"] == "claude-sonnet-5-5"
    assert fake.asked["system"] == "be brief"
    assert fake.asked["messages"] == [
        {"role": "user", "content": "hi"},
        {"role": "user", "content": "what is assembled?"},
    ]
    assert fake.asked["tools"][0]["input_schema"] == schema
    assert fake.asked["tool_choice"] == {"type": "tool", "name": "answer"}


def test_anthropic_answers_in_text(monkeypatch):
    import anthropic

    fake = FakeAnthropic([SimpleNamespace(type="text", text="A summary.")])
    monkeypatch.setattr(anthropic, "Anthropic", fake)
    ai = ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key="key"))

    assert ai.complete("summarise", "the text") == "A summary."
    assert "tools" not in fake.asked


def test_openai_answers_in_json_by_its_response_format(monkeypatch):
    import openai

    asked = {}

    class Client:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        def create(self, **arguments):
            asked.update(arguments)
            message = SimpleNamespace(content='{"answer": "yes"}')
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setattr(openai, "OpenAI", Client)
    ai = ProviderAI(Settings(llm_provider="openai", openai_api_key="key", llm_model="gpt-5"))
    schema = {"type": "object"}

    assert ai.complete("be brief", "yes?", json_schema=schema) == '{"answer": "yes"}'
    assert asked["messages"][0] == {"role": "system", "content": "be brief"}
    assert asked["response_format"]["json_schema"]["schema"] == schema


def test_the_ai_without_its_key_says_so():
    ai = ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key=None))

    # in words students may see: no setting is named
    assert ai.missing() == "the app is missing its Anthropic key"
    with pytest.raises(PlatformError, match="missing its Anthropic key"):
        ai.complete("system", "prompt")


def test_s3_reads_part_of_a_file(monkeypatch):
    asked = []

    class Client:
        exceptions = SimpleNamespace(NoSuchKey=KeyError, ClientError=RuntimeError)

        def get_object(self, **arguments):
            asked.append(arguments)
            return {"Body": SimpleNamespace(read=lambda: b"part")}

    import boto3

    monkeypatch.setattr(boto3, "client", lambda service: Client())
    files = S3Files("bucket")

    assert files.get("documents/d1", 10, 5) == b"part"
    files.get("documents/d1", 10)
    files.get("documents/d1")

    assert [a.get("Range") for a in asked] == ["bytes=10-14", "bytes=10-", None]
