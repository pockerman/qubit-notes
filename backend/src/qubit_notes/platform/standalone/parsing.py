"""Reads a document into its sections, as gogi does: a Markdown file by its headings, a PDF by its outline (or page by
page if it has none), and anything else, e.g. a plain text file, into a single section."""

import re
from io import BytesIO

from pypdf import PdfReader

from qubit_notes.platform.port import Section, SectionText

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def sections(filename: str, content: bytes) -> list[SectionText]:
    if content.startswith(b"%PDF-"):
        return _pdf(content)
    text = content.decode(errors="ignore")
    if filename.lower().endswith(".md"):
        return _markdown(text)
    return [_section(1, "", 1, text)] if text.strip() else []


def _section(position: int, title: str, level: int, text: str, start: int | None = None, end: int | None = None):
    return SectionText(
        section=Section(position=position, title=title, level=level, page_start=start, page_end=end),
        content=text.strip(),
    )


def _markdown(text: str) -> list[SectionText]:
    """a section per heading, and one for any text before the first heading"""
    found, title, level, lines = [], None, 1, []
    for line in text.splitlines() + ["# end"]:
        match = HEADING.match(line)
        if not match:
            lines.append(line)
            continue
        if title is not None or "".join(lines).strip():
            found.append(_section(len(found) + 1, title or "", level, "\n".join(lines)))
        title, level, lines = match.group(2), len(match.group(1)), []
    return found


def _pdf(content: bytes) -> list[SectionText]:
    """A section per entry of the outline, with the text of its pages up to the next entry's: pages are the finest
    unit an outline points to. A section that starts on the same page as the next has no text of its own."""
    try:
        reader = PdfReader(BytesIO(content))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception:
        return []
    entries = _outline(reader)
    if not entries:
        return [_section(n, f"Page {n}", 1, text, n, n) for n, text in enumerate(pages, start=1)]

    found = []
    for i, (title, level, start) in enumerate(entries):
        next_start = entries[i + 1][2] if i + 1 < len(entries) else len(pages) + 1
        own = range(start, next_start) if next_start > start else range(0)
        text = "\n\n".join(pages[n - 1] for n in own if pages[n - 1])
        found.append(_section(i + 1, title, level, text, start, max(start, next_start - 1)))
    return found


def _outline(reader: PdfReader) -> list[tuple[str, int, int]]:
    """the outline's entries in order, as (title, level, 1-based page); none if they're out of page order"""
    entries = []

    def walk(items, level):
        for item in items:
            if isinstance(item, list):
                walk(item, level + 1)
                continue
            try:
                entries.append((str(item.title).strip(), level, reader.get_destination_page_number(item) + 1))
            except Exception:
                continue

    try:
        walk(reader.outline, 1)
    except Exception:
        return []
    if any(entries[i][2] > entries[i + 1][2] for i in range(len(entries) - 1)):
        return []
    return entries
