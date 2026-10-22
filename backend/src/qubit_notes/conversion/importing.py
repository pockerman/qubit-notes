"""PDFs and EPUBs to Markdown.

A PDF's headings come from its outline if it has one, each with the text of its pages up to the next entry's (from
where its title is on its first page, if it is); else from the sizes of its fonts, as pymupdf4llm finds them; a PDF
with neither is divided into its pages. An EPUB's headings are its chapters' own; a chapter without one is given its
title in the book's table of contents. Their pictures become images the Markdown refers to.
"""

import posixpath
import re
import tempfile
from io import BytesIO
from pathlib import Path

import pymupdf
import pymupdf4llm
from bs4 import BeautifulSoup
from markdownify import markdownify
from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders

from qubit_notes.conversion.converted import IMAGES, Converted, NotConvertible

# the layout engine ignores a PDF's outline and recognises text in pictures, which the app doesn't: the classic one
# is used
pymupdf4llm.use_layout(False)

CONVERTIBLE = {"application/pdf", "application/epub+zip"}
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def to_markdown(filename: str, content_type: str, content: bytes) -> Converted:
    if content_type == "application/pdf":
        return _pdf(filename, content)
    if content_type == "application/epub+zip":
        return _epub(filename, content)
    raise NotConvertible(f"{filename!r} is not a PDF or an EPUB")


# PDFs


def _no_headers(span, page=None) -> str:
    return ""


def _pdf(filename: str, content: bytes) -> Converted:
    try:
        document = pymupdf.open(stream=content, filetype="pdf")
    except Exception as e:
        raise NotConvertible(f"{filename!r} is not a PDF that can be read: {e}") from e
    if document.needs_pass:
        raise NotConvertible(f"{filename!r} is protected by a password")
    outline = _outline(document)
    with tempfile.TemporaryDirectory() as directory:
        chunks = pymupdf4llm.to_markdown(
            document,
            # with an outline, its entries are the headings
            hdr_info=_no_headers if outline else IdentifyHeaders(document),
            page_chunks=True,
            write_images=True,
            image_path=directory,
            image_format="png",
            filename="page",
            show_progress=False,
        )
        pages = [_tidy(chunk["text"].replace(f"{directory}/", f"{IMAGES}/")) for chunk in chunks]
        images = {f"{IMAGES}/{path.name}": path.read_bytes() for path in sorted(Path(directory).iterdir())}

    if not any(_has_text(page) for page in pages):
        raise NotConvertible(f"{filename!r} has no text to convert, as it may be scanned")
    if outline:
        markdown = _by_outline(outline, pages)
    elif any(HEADING.match(line) for page in pages for line in page.splitlines()):
        markdown = "\n\n".join(page for page in pages if page)
    else:
        markdown = "\n\n".join(f"# Page {n}\n\n{page}".rstrip() for n, page in enumerate(pages, start=1))
    return Converted(markdown=markdown.strip() + "\n", images=_referred(markdown, images))


def _outline(document) -> list[tuple[int, str, int]]:
    """the outline's entries, as (level, title, 1-based page); none if they're out of page order"""
    entries = [(level, title.strip(), page) for level, title, page in document.get_toc(simple=True) if page >= 1]
    if any(entries[i][2] > entries[i + 1][2] for i in range(len(entries) - 1)):
        return []
    return entries


def _comparable(text: str) -> str:
    return re.sub(r"[\W_]+", " ", text).strip().lower()


def _by_outline(outline: list[tuple[int, str, int]], pages: list[str]) -> str:
    """A heading per entry, followed by the text from where the entry starts to where the next does. An entry starts
    at its title, if its first page has it on a line of its own after where the previous entry starts, and else at
    its page's top: an entry on the same page as the previous whose title isn't found has no text of its own."""
    lines = [(n, line) for n, page in enumerate(pages, start=1) for line in page.splitlines()]
    starts, previous = [], 0
    for _, title, page in outline:
        first = next((i for i, (n, _) in enumerate(lines) if n >= page), len(lines))
        start = max(first, previous)
        wanted = _comparable(title)
        found = next(
            (i for i in range(start, len(lines)) if lines[i][0] == page and _comparable(lines[i][1]) == wanted), None
        )
        # the title's own line isn't text of the section
        starts.append((found + 1, found) if found is not None else (start, start))
        previous = starts[-1][1]

    parts = []
    for i, (level, title, _) in enumerate(outline):
        begin = starts[i][0]
        end = starts[i + 1][1] if i + 1 < len(outline) else len(lines)
        text = "\n".join(line for _, line in lines[begin:end]).strip()
        parts.append(f"{'#' * min(level, 6)} {title}\n\n{text}".rstrip())
    return "\n\n".join(parts)


def _tidy(markdown: str) -> str:
    """headings with blank lines around them and without emphasis, and no runs of blank lines"""
    out = []
    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match:
            title = re.sub(r"(\*\*|__|\*|_)(.+?)\1", r"\2", match.group(2)).strip()
            out.extend(["", f"{match.group(1)} {title}", ""])
        else:
            out.append(line.rstrip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def _has_text(markdown: str) -> bool:
    return bool(re.sub(r"!\[[^\]]*\]\([^)]*\)", "", markdown).strip())


def _referred(markdown: str, images: dict[str, bytes]) -> dict[str, bytes]:
    return {path: content for path, content in images.items() if f"]({path})" in markdown}


# EPUBs


def _epub(filename: str, content: bytes) -> Converted:
    from ebooklib import ITEM_DOCUMENT, epub

    try:
        book = epub.read_epub(BytesIO(content), options={"ignore_ncx": True})
    except Exception as e:
        raise NotConvertible(f"{filename!r} is not an EPUB that can be read: {e}") from e

    titles = {href.split("#")[0]: title for href, title in _toc(book.toc)}
    chapters, images = [], {}
    for idref, _ in book.spine:
        item = book.get_item_with_id(idref)
        if item is None or item.get_type() != ITEM_DOCUMENT or isinstance(item, epub.EpubNav):
            continue
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for picture in soup.find_all(["img", "image"]):
            attribute = "src" if picture.name == "img" else "xlink:href"
            source = picture.get(attribute) or picture.get("href")
            kept = _epub_image(book, item.file_name, source, images)
            if kept:
                picture.name, picture.attrs = "img", {"src": kept, "alt": picture.get("alt", "")}
            else:
                picture.decompose()
        body = soup.body or soup
        markdown = _tidy(markdownify(str(body), heading_style="ATX", strip=["script", "style"]))
        if not markdown:
            continue
        if not any(HEADING.match(line) for line in markdown.splitlines()) and item.file_name in titles:
            markdown = f"# {titles[item.file_name]}\n\n{markdown}"
        chapters.append(markdown)

    markdown = "\n\n".join(chapters)
    if not _has_text(markdown):
        raise NotConvertible(f"{filename!r} has no text to convert")
    return Converted(markdown=markdown.strip() + "\n", images=_referred(markdown, images))


def _toc(entries) -> list[tuple[str, str]]:
    """the table of contents' (href, title) pairs, in order"""
    found = []
    for entry in entries:
        if isinstance(entry, tuple):
            section, children = entry
            if getattr(section, "href", None):
                found.append((section.href, section.title))
            found.extend(_toc(children))
        elif getattr(entry, "href", None):
            found.append((entry.href, entry.title))
    return found


def _epub_image(book, chapter: str, source: str | None, images: dict[str, bytes]) -> str | None:
    """keeps the picture the chapter refers to among the images, returning the path the Markdown refers to it by"""
    if not source or re.match(r"^[a-z][a-z0-9+.-]*:", source, re.IGNORECASE):
        return None
    href = posixpath.normpath(posixpath.join(posixpath.dirname(chapter), source.split("#")[0]))
    # the kinds of image a material may have
    if posixpath.splitext(href)[1].lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        return None
    item = book.get_item_with_href(href)
    if item is None:
        return None
    path = f"{IMAGES}/{posixpath.basename(href)}"
    images[path] = item.get_content()
    return path
