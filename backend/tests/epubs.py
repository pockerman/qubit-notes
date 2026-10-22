"""Builds small EPUBs, for tests."""

import tempfile
from pathlib import Path

from ebooklib import epub


def make_epub(chapters: list[tuple[str, str]], picture_in: str | None = None, picture: bytes = b"") -> bytes:
    """an EPUB of chapters (title, text), each with its title as its heading; picture_in names the chapter that shows
    the picture"""
    book = epub.EpubBook()
    book.set_identifier("test-book")
    book.set_title("A book")
    book.set_language("en")
    if picture_in:
        book.add_item(epub.EpubItem(file_name="figures/picture.png", media_type="image/png", content=picture))
    items = []
    for n, (title, text) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(title=title, file_name=f"chapter-{n}.xhtml", lang="en")
        shown = '<p><img src="figures/picture.png" alt="a picture"/></p>' if title == picture_in else ""
        chapter.content = f"<h1>{title}</h1><p>{text}</p>{shown}"
        book.add_item(chapter)
        items.append(chapter)
    book.toc = items
    book.spine = ["nav", *items]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "book.epub"
        epub.write_epub(str(path), book)
        return path.read_bytes()
