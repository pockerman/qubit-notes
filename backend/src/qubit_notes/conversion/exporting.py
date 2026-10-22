"""Markdown to a PDF or an EPUB, like the material's original: laid out anew, with its headings, text, lists,
tables and images. A PDF gets an outline of its headings; an EPUB is a chapter per top-level heading."""

import re
import tempfile
import uuid
from io import BytesIO
from pathlib import Path, PurePosixPath

import pymupdf
from markdown_it import MarkdownIt

from qubit_notes.conversion.importing import HEADING

CSS = """
body { font-family: sans-serif; font-size: 11pt; line-height: 1.4; }
h1 { font-size: 20pt; } h2 { font-size: 16pt; } h3 { font-size: 13pt; }
table { border-collapse: collapse; } td, th { border: 1px solid #999; padding: 2pt 4pt; }
pre, code { font-family: monospace; font-size: 9pt; }
"""
# A4, with 2 cm margins
PAGE = pymupdf.paper_rect("a4")
MARGIN = 57


def _html(markdown: str) -> str:
    return MarkdownIt("commonmark").enable("table").render(markdown)


def export(content_type: str, title: str, markdown: str, images: dict[str, bytes]) -> bytes:
    if content_type == "application/pdf":
        return _pdf(markdown, images)
    if content_type == "application/epub+zip":
        return _epub(title, markdown, images)
    raise ValueError(f"cannot export to {content_type}")


def _pdf(markdown: str, images: dict[str, bytes]) -> bytes:
    with tempfile.TemporaryDirectory() as directory:
        for path, content in images.items():
            target = Path(directory) / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        # the images no bigger than the page, as the layout can't split a picture across pages
        width, height = PAGE.width - 2 * MARGIN, PAGE.height - 2 * MARGIN
        html = _fit_images(_html(markdown), directory, width, height * 0.9)
        story = pymupdf.Story(html=html, user_css=CSS, archive=pymupdf.Archive(directory))
        written = BytesIO()
        writer = pymupdf.DocumentWriter(written)
        headings = []

        def record(position):
            if position.heading and position.open_close & 1 and position.text:
                headings.append((position.heading, position.text.strip(), position.page_num))

        where = PAGE + (MARGIN, MARGIN, -MARGIN, -MARGIN)
        more, page = 1, 0
        while more:
            page += 1
            device = writer.begin_page(PAGE)
            more, _ = story.place(where)
            story.element_positions(record, {"page_num": page})
            story.draw(device)
            writer.end_page()
        writer.close()
        output = pymupdf.open(stream=written.getvalue(), filetype="pdf")
        output.set_toc(_levels(headings))
        output.set_metadata({"producer": "qubit-notes"})
        return output.tobytes(garbage=3, deflate=True)


def _levels(headings: list[tuple[int, str, int]]) -> list[list]:
    """an outline whose levels go down by one at most, as PDFs require"""
    toc, last = [], 0
    for level, title, page in headings:
        level = min(level, last + 1)
        toc.append([level, title, page])
        last = level
    return toc


def _fit_images(html: str, directory: str, width: float, height: float) -> str:
    """gives each image a size that fits the page, keeping its proportions"""

    def sized(match: re.Match) -> str:
        tag, source = match.group(0), match.group(1)
        try:
            picture = pymupdf.Pixmap(str(Path(directory) / source))
        except Exception:
            return ""
        scale = min(1.0, width / picture.width, height / picture.height)
        size = f'width="{picture.width * scale:.0f}" height="{picture.height * scale:.0f}"'
        return tag.replace("<img ", f"<img {size} ", 1)

    return re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', sized, html)


def _epub(title: str, markdown: str, images: dict[str, bytes]) -> bytes:
    from ebooklib import epub

    book = epub.EpubBook()
    book.set_identifier(f"urn:uuid:{uuid.uuid4()}")
    book.set_title(title)
    book.set_language("en")
    style = epub.EpubItem(uid="style", file_name="style.css", media_type="text/css", content=CSS.encode())
    book.add_item(style)
    for path, content in images.items():
        suffix = PurePosixPath(path).suffix.lower().lstrip(".")
        media_type = "image/jpeg" if suffix in ("jpg", "jpeg") else f"image/{suffix}"
        book.add_item(epub.EpubItem(file_name=path, media_type=media_type, content=content))

    chapters = []
    for n, (heading, text) in enumerate(_chapters(markdown), start=1):
        chapter = epub.EpubHtml(title=heading or title, file_name=f"chapter-{n}.xhtml", lang="en")
        chapter.content = _html(text)
        chapter.add_item(style)
        book.add_item(chapter)
        chapters.append(chapter)
    book.toc = chapters
    book.spine = ["nav", *chapters]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "book.epub"
        epub.write_epub(str(path), book)
        return path.read_bytes()


def _chapters(markdown: str) -> list[tuple[str, str]]:
    """the Markdown divided at its top-level headings, each part with its heading; text before the first is a part
    of its own"""
    lines = markdown.splitlines()
    top = min((len(m.group(1)) for line in lines if (m := HEADING.match(line))), default=1)
    parts: list[tuple[str, list[str]]] = [("", [])]
    for line in lines:
        match = HEADING.match(line)
        if match and len(match.group(1)) == top:
            parts.append((match.group(2), []))
        parts[-1][1].append(line)
    return [(heading, "\n".join(text)) for heading, text in parts if "\n".join(text).strip()]
