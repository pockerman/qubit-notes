import json
import re
import threading
from typing import Any

from qubit_notes.platform.port import (
    Completion,
    Message,
    PlatformError,
    Researched,
    Speech,
    Transcript,
    WebSource,
    chosen_ai,
)


class FakeAI:
    """A deterministic stand-in for the AI, for scenarios that need no model provider's key: see ``complete``."""

    def __init__(self):
        # what the AI was asked, so scenarios can tell whether something new was written, and the conversation it
        # was given with each prompt
        self.completions: list[str] = []
        self.histories: list[list[Message]] = []
        # the input and output tokens each answer takes
        self.tokens = (0, 0)
        self.model = ("fake", "fake")
        # whether it can read text aloud, as if it had the app's OpenAI key, and what it read, with how it was told to
        # and by which model
        self.speaks = False
        self.spoken: list[tuple[str, str]] = []
        self.speaking_fails = False
        # set, it reads aloud only once it is let to
        self.slow_to_speak: threading.Event | None = None
        # whether it can search the web, and whether it did, for each thing it wrote searching it
        self.searches_web = True
        self.searched: list[bool] = []
        # whether it can hear what is said, as if it had the app's OpenAI key, and the model each recording was
        # heard by
        self.hears = False
        self.heard: list[str] = []

    def missing(self) -> str | None:
        return None

    def missing_key(self) -> str | None:
        return None

    def use_key(self, provider: str, key: str | None) -> None:
        pass

    def use_model(self, provider: str, model: str) -> None:
        # the model it stands in for
        self.model = (provider, model)

    def has_key(self, provider: str) -> bool:
        # it has an OpenAI key only to speak and hear with
        return provider == "openai" and (self.speaks or self.hears)

    def speak(self, text: str, instructions: str, model: str) -> Speech:
        """a stand-in MP3: an MP3 frame header, then the text"""
        if self.slow_to_speak is not None:
            self.slow_to_speak.wait(10)
        if not self.speaks:
            raise PlatformError("FAILED_PRECONDITION", "the app has no OpenAI key")
        if self.speaking_fails:
            raise PlatformError("AI_FAILED", "OpenAI refused: the voice is hoarse")
        self.spoken.append((text, instructions, model))
        return Speech(audio=b"\xff\xfb\x90\x00" + text.encode(), provider="openai", model=model)

    def transcribe(self, audio: bytes, content_type: str, model: str) -> Transcript:
        """what a stand-in recording says: the text after "said:", as the steps record it; what a browser records,
        with its fake microphone, says it was heard"""
        if not self.hears:
            raise PlatformError("FAILED_PRECONDITION", "the app has no OpenAI key")
        self.heard.append(model)
        text = audio[len(SAID) :].decode() if audio.startswith(SAID) else f"What I said, as heard by {model}"
        return Transcript(text=text, provider="openai", model=model, input_tokens=self.tokens[0])

    def research(self, system: str, prompt: str, history: list[Message] | None, search_web: bool) -> Researched:
        """a stand-in: Markdown numbered like the other answers, saying what it was asked, citing two pages of the
        web if it searched it"""
        self.completions.append(prompt)
        self.histories.append(list(history or []))
        number = len(self.completions)
        asked = re.search(r"^They ask: (.*)$", prompt, re.MULTILINE)
        about = asked.group(1) if asked else "it"
        searched = search_web and self.searches_web
        self.searched.append(searched)
        provider, model = chosen_ai.get() or self.model
        if not searched:
            text = f"## Writing {number}\n\nOn {about}, from what the AI knows."
            return Researched(text=text, provider=provider, model=model)
        text = f"## Writing {number}\n\nOn {about}, as one page says [1].\n\nAnd as another says [2]."
        sources = [
            WebSource(title=f"Page {number}.1", url=f"https://example.org/{number}/1"),
            WebSource(title=f"Page {number}.2", url=f"https://example.org/{number}/2"),
        ]
        tokens = self.tokens
        return Researched(
            text=text,
            sources=sources,
            searched=True,
            provider=provider,
            model=model,
            input_tokens=tokens[0],
            output_tokens=tokens[1],
        )

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> Completion:
        provider, model = chosen_ai.get() or self.model
        text = self._answer(prompt, json_schema, history)
        return Completion(
            text=text, provider=provider, model=model, input_tokens=self.tokens[0], output_tokens=self.tokens[1]
        )

    def _answer(self, prompt: str, json_schema: dict[str, Any] | None, history: list[Message] | None) -> str:
        """A deterministic stand-in: each answer is numbered, so no two are alike. New material has a line from each
        labelled part of the material it is written from, citing it. A quiz has the questions the
        prompt asks for, each from one of the sections the prompt gives, in turn, with the first choice correct;
        flashcards likewise, each with a front and a back. The assistant understands a request by its words (see
        ``_understand``)."""
        self.completions.append(prompt)
        self.histories.append(list(history or []))
        number = len(self.completions)
        if json_schema is None and (labelled := re.findall(r"^\[(S\d+)\] (.+)$", prompt, re.MULTILINE)):
            # new material: a line from each part of the material, citing it by its label
            lines = [f"- From {heading} [{label}]." for label, heading in labelled]
            return "\n".join([f"# Generated {number}", "", *lines])
        if json_schema is None:
            titles = re.findall(r"^## (.+)$", prompt, re.MULTILINE)
            return f"Summary {number} of {', '.join(titles) or 'the summaries'}."
        if "narration" in json_schema.get("properties", {}):
            # a narration: the material's sections, said in turn, and how to speak it as the instructions say
            told = re.search(r"^The student's instructions: (.*)$", prompt, re.MULTILINE)
            sections = re.findall(r"^## (.+)\n\n(.+)$", prompt.split("Narrate ", 1)[-1], re.MULTILINE)
            narration = "\n\n".join(f"Narration {number}. {title}. {text}" for title, text in sections)
            voice = f"Speak as told: {told.group(1)}" if told and told.group(1) != "(none)" else ""
            return json.dumps({"narration": narration, "voice": voice})
        if "request" in json_schema.get("properties", {}):
            return json.dumps(_understand(prompt, number))
        if {"question", "source"} <= json_schema.get("properties", {}).keys() or "to_study" in json_schema.get(
            "properties", {}
        ):
            return json.dumps(_check(prompt, json_schema, number))
        references = re.findall(r"^\[(S\d+)\] (.+)$", prompt, re.MULTILINE)
        if flashcards := re.search(r"Write (\d+) flashcards", prompt):
            cards = [
                {
                    "front": f"Card {i + 1} of deck {number}, on {references[i % len(references)][1]}?",
                    "back": f"The answer to card {i + 1} of deck {number}.",
                    "source": references[i % len(references)][0],
                }
                for i in range(int(flashcards.group(1)))
            ]
            return json.dumps({"cards": cards})
        count = int(re.search(r"quiz of (\d+) questions", prompt).group(1))
        questions = [
            {
                "question": f"Question {i + 1} of quiz {number}, on {references[i % len(references)][1]}?",
                "choices": ["right", "wrong", "also wrong", "still wrong"],
                "answer": 0,
                "source": references[i % len(references)][0],
            }
            for i in range(count)
        ]
        return json.dumps({"questions": questions})


# what a stand-in recording starts with: what it says comes after it
SAID = b"said:"


def _check(prompt: str, json_schema: dict, number: int) -> dict:
    """The fake comprehension assistant: its questions are on the labelled sections in turn; an answer that says
    "don't know" or "not sure" was not understood, one that shares two words with the question's section was, and
    any other was partly; its verdict says the sections understood and those to study again."""
    sections = dict(re.findall(r"^\[(S\d+)\] [^\n]+\n(.*?)(?=^\[S\d+\] |\Z|^The check so far)", prompt, re.M | re.S))
    references = list(sections) or ["S1"]
    asked = len(re.findall(r"^Question \d+ \(from S\d+\):", prompt, re.MULTILINE))
    following = references[asked % len(references)]
    question = {"question": f"Question {number}: what does {following} say?", "source": following}
    properties = json_schema.get("properties", {})
    if "to_study" in properties:
        assessed = re.findall(r"^Question \d+ \(from (S\d+)\):.*?^Understood: (yes|partly|no)", prompt, re.M | re.S)
        return {
            "summary": f"Verdict {number}: you understood {sum(u == 'yes' for _, u in assessed)} of {len(assessed)}.",
            "understood": [f"What {reference} says" for reference, understood in assessed if understood == "yes"],
            "to_study": [reference for reference, understood in assessed if understood != "yes"],
        }
    if "feedback" not in properties:
        return question
    on = re.search(r"^The last question is from (S\d+)\.$", prompt, re.MULTILINE).group(1)
    answer = re.search(r"^The student's answer[^:]*: (.*)$", prompt, re.MULTILINE).group(1)
    if re.search(r"don't know|not sure", answer, re.IGNORECASE):
        understood = "no"
    elif len(_content_words(answer) & _content_words(sections.get(on, ""))) >= 2:
        understood = "yes"
    else:
        understood = "partly"
    no_more = "Ask no further question" in prompt
    return {
        "understood": understood,
        "feedback": f"Feedback {number}: {understood}, as {on} says.",
        "cited": [on],
        "question": "" if no_more else question["question"],
        "source": "" if no_more else question["source"],
    }


# words too common to tell whether a passage answers a question
COMMON = {
    "what",
    "which",
    "does",
    "that",
    "this",
    "with",
    "from",
    "into",
    "about",
    "have",
    "there",
    "their",
    "when",
    "where",
    "whom",
    "whose",
    "they",
    "them",
    "then",
    "than",
    "your",
    "mine",
}


def _content_words(text: str) -> set[str]:
    return {word for word in re.findall(r"\w+", text.lower()) if len(word) > 3 and word not in COMMON}


def _understand(prompt: str, number: int) -> dict:
    """The fake assistant's reading of the student's words, the last part of the prompt: "quiz" asks for a quiz,
    "flashcard..." for flashcards, "summar..." for a summary, of the "topic" (or "collection"), the "document" (or
    "paper") or else the section, "new" for a new one, "N questions" or "N flashcards" for its size. Anything else is
    a question, answered from the passages that share a word with it."""
    words = prompt.rsplit("The student says:", 1)[-1].strip()
    lowered = words.lower()
    request = (
        "quiz"
        if "quiz" in lowered
        else "flashcards"
        if "flashcard" in lowered
        else "summary"
        if "summar" in lowered
        else "question"
    )
    of = (
        "topic"
        if re.search(r"\b(topic|collection)\b", lowered)
        else "document"
        if re.search(r"\b(document|paper)\b", lowered)
        else "section"
    )
    count = re.search(r"(\d+) (?:questions|flashcards)", lowered)
    cited = []
    if request == "question":
        passages = re.findall(
            r"^\[(P\d+)\] [^\n]+\n(.*?)(?=^\[P\d+\] |^The student says:)", prompt, re.MULTILINE | re.DOTALL
        )
        cited = [reference for reference, text in passages if _content_words(words) & _content_words(text)]
    return {
        "request": request,
        "of": of,
        "new": bool(re.search(r"\bnew\b", lowered)),
        "questions": int(count.group(1)) if count else 0,
        "answer": f"Answer {number}, from {', '.join(cited)}." if cited else "Your material does not cover this.",
        "covered": bool(cited) or request != "question",
        "cited": cited,
    }
