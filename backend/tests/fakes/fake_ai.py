import json
import re
from typing import Any

from qubit_notes.platform.port import Message


class FakeAI:
    """A deterministic stand-in for the AI, for scenarios that need no model provider's key: see ``complete``."""

    def __init__(self):
        # what the AI was asked, so scenarios can tell whether something new was written, and the conversation it
        # was given with each prompt
        self.completions: list[str] = []
        self.histories: list[list[Message]] = []

    def missing(self) -> str | None:
        return None

    def missing_key(self) -> str | None:
        return None

    def use_key(self, provider: str, key: str) -> None:
        pass

    def use_model(self, provider: str, model: str) -> None:
        # the model it stands in for
        self.model = (provider, model)

    def has_key(self, provider: str) -> bool:
        return False

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
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
        if "request" in json_schema.get("properties", {}):
            return json.dumps(_understand(prompt, number))
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
    "flashcard..." for flashcards, "summar..." for a summary, of the "topic", the "document" or else the section,
    "new" for a new one, "N questions" or "N flashcards" for its size. Anything else is a question, answered from the
    passages that share a word with it."""
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
    of = "topic" if "topic" in lowered else "document" if "document" in lowered else "section"
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
