"""A paper's details, as far as the paper itself tells them: see features/papers.feature.

- A PDF's title and authors are its own, as it keeps them, unless its title is no title (e.g. its file's name, as
  some editors write it); then its title is the text on its first page in the largest font, if any is larger than
  the rest. Its DOI is the first on its first two pages, and an arXiv identifier there, e.g. arXiv:1707.06347, makes
  its venue arXiv and its year that of the identifier.
- An EPUB's title and authors are its own.
- A Markdown paper's title is its first top-level heading.
"""

import re
from collections import Counter
from io import BytesIO

import pymupdf
from pydantic import BaseModel, Field

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)
# the year and month of an arXiv identifier, e.g. arXiv:1707.06347 is of July 2017
ARXIV = re.compile(r"\barXiv:\s*(\d{2})(\d{2})\.\d{4,5}", re.IGNORECASE)
TITLE = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)
# a PDF's title that is no title: a file's name, or what an editor writes when it has none
NO_TITLE = re.compile(r"\.(docx?|pdf|tex|dvi)$|^(microsoft word|untitled)|^\s*$", re.IGNORECASE)
# how much larger than the body's a font is to be the title's
TITLE_SIZE = 1.15


class Details(BaseModel):
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str = ""
    doi: str = ""


def details(content_type: str, content: bytes) -> Details:
    """the paper's details, those it doesn't tell left empty"""
    if content_type == "application/pdf":
        return _pdf(content)
    if content_type == "application/epub+zip":
        return _epub(content)
    if content_type == "text/markdown":
        title = TITLE.search(content.decode("utf-8", errors="replace"))
        return Details(title=_spaced(title.group(1)) if title else "")
    return Details()


def authors_of(written: str) -> list[str]:
    """the authors written in one, e.g. "Ada Lovelace; Alan Turing" or "Ada Lovelace and Alan Turing" """
    return [_spaced(author) for author in re.split(r"\s*(?:;|,|\band\b|&)\s*", written) if author.strip()]


def _spaced(text: str) -> str:
    return " ".join(text.split())


def _pdf(content: bytes) -> Details:
    try:
        document = pymupdf.open(stream=content, filetype="pdf")
    except Exception:
        return Details()
    own = document.metadata or {}
    first = "\n".join(page.get_text() for page in document.pages(0, min(2, document.page_count)))
    title = _spaced(own.get("title") or "")
    if NO_TITLE.search(title):
        title = _largest_text(document[0]) if document.page_count else ""
    doi = DOI.search(first)
    arxiv = ARXIV.search(first)
    return Details(
        title=title,
        authors=authors_of(own.get("author") or ""),
        year=2000 + int(arxiv.group(1)) if arxiv else None,
        venue="arXiv" if arxiv else "",
        doi=doi.group(1).rstrip(".,;:)]}") if doi else "",
    )


def _largest_text(page) -> str:
    """the text of the page in its largest font, if that is larger than its body's"""
    spans = [
        span
        for block in page.get_text("dict")["blocks"]
        for line in block.get("lines", [])
        for span in line["spans"]
        if span["text"].strip()
    ]
    if not spans:
        return ""
    sizes = Counter()
    for span in spans:
        sizes[round(span["size"], 1)] += len(span["text"])
    body = sizes.most_common(1)[0][0]
    largest = max(sizes)
    if largest < body * TITLE_SIZE:
        return ""
    return _spaced(" ".join(span["text"] for span in spans if round(span["size"], 1) == largest))[:300]


def _epub(content: bytes) -> Details:
    from ebooklib import epub

    try:
        book = epub.read_epub(BytesIO(content), options={"ignore_ncx": True})
    except Exception:
        return Details()
    titles = book.get_metadata("DC", "title")
    creators = book.get_metadata("DC", "creator")
    return Details(
        title=_spaced(titles[0][0]) if titles else "",
        authors=[_spaced(creator) for creator, _ in creators if creator.strip()],
    )
