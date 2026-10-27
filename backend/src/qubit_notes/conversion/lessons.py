"""A document's Markdown divided into lessons by its headings (features/lessons.feature).

The lessons are the headings at the document's top level: the shallowest level with at least two headings, so a book
whose only top heading is its title is divided into its chapters. Each lesson's text runs to the next lesson's
heading, with its headings moved up so that its own is a top heading. Text before the first lesson is a lesson of its
own, named after the document's title if it has one; a document with fewer than two headings is a single lesson.
"""

import re
from dataclasses import dataclass

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# a code block's fence; ```code``` on a line of its own is code in the text, as a ``` fence has no ` after it
FENCE = re.compile(r"^\s*(```(?!.*`)|~~~)")
# a lesson of the text before the first, when the document has no title
INTRODUCTION = "Introduction"


@dataclass
class Lesson:
    title: str
    markdown: str


def lessons(markdown: str, untitled: str) -> list[Lesson]:
    """the document's lessons, in order; ``untitled`` names a document with neither headings nor a title"""
    lines = markdown.splitlines()
    headings = _headings(lines)
    levels = [level for _, level, _ in headings]
    level = next((n for n in sorted(set(levels)) if levels.count(n) >= 2), None)
    if level is None:
        title = headings[0][2] if headings else untitled
        return [Lesson(title, _with_heading(title, lines, headings))] if markdown.strip() else []

    starts = [(i, title) for i, n, title in headings if n == level]
    found = []
    before = lines[: starts[0][0]]
    # the document's title is a heading above the lessons' level, before them
    title = next((t for i, n, t in headings if n < level and i < starts[0][0]), None)
    text = [line for line in before if not (title and HEADING.match(line) and HEADING.match(line).group(2) == title)]
    if "".join(text).strip():
        name = title or INTRODUCTION
        found.append(Lesson(name, f"# {name}\n\n" + _moved("\n".join(text), level - 1).strip() + "\n"))
    for n, (start, title) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        found.append(Lesson(title, _moved("\n".join(lines[start:end]), level - 1).strip() + "\n"))
    return found


def _headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """each heading's line, level and title, leaving out lines of code"""
    found, in_code = [], False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and (match := HEADING.match(line)) and match.group(2):
            found.append((i, len(match.group(1)), match.group(2)))
    return found


def _moved(text: str, by: int) -> str:
    """the text with its headings ``by`` levels up, none above the top"""
    if by <= 0:
        return text
    moved, in_code = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and (match := HEADING.match(line)):
            line = "#" * max(1, len(match.group(1)) - by) + " " + match.group(2)
        moved.append(line)
    return "\n".join(moved)


def _with_heading(title: str, lines: list[str], headings: list) -> str:
    """a single lesson's text, with its title as its top heading"""
    text = "\n".join(lines).strip()
    return (text if headings else f"# {title}\n\n{text}") + "\n"
