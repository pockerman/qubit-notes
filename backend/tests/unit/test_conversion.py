"""Converting PDFs and EPUBs to Markdown and back, in the cases the scenarios don't reach."""

import pymupdf
import pytest
from ebooklib import epub

from qubit_notes.conversion import NotConvertible, export, to_markdown
from qubit_notes.platform.standalone import parsing
from tests.epubs import make_epub

PDF = "application/pdf"
EPUB = "application/epub+zip"


def _pdf(lines_by_page: list[list[str]], toc: list[list]) -> bytes:
    document = pymupdf.open()
    for lines in lines_by_page:
        page = document.new_page()
        for n, line in enumerate(lines):
            page.insert_text((72, 72 + 20 * n), line, fontsize=11)
    document.set_toc(toc)
    return document.tobytes()


def _titles(markdown: str) -> list[str]:
    return [part.section.title for part in parsing.sections("x.md", markdown.encode())]


def test_an_outline_title_on_its_page_is_not_repeated_and_splits_the_page():
    pdf = _pdf(
        [["1 Introduction", "Elements divide the domain.", "2 Assembly", "Matrices are assembled."]],
        [[1, "1 Introduction", 1], [1, "2 Assembly", 1]],
    )

    markdown = to_markdown("a.pdf", PDF, pdf).markdown

    assert _titles(markdown) == ["1 Introduction", "2 Assembly"]
    sections = parsing.sections("x.md", markdown.encode())
    assert sections[0].content == "Elements divide the domain."
    assert sections[1].content == "Matrices are assembled."


def test_an_outline_out_of_page_order_is_not_used():
    pdf = _pdf([["First page text."], ["Second page text."]], [[1, "Late", 2], [1, "Early", 1]])

    assert _titles(to_markdown("a.pdf", PDF, pdf).markdown) == ["Page 1", "Page 2"]


def test_a_file_that_is_not_a_pdf_is_not_converted():
    with pytest.raises(NotConvertible, match="not a PDF that can be read"):
        to_markdown("a.pdf", PDF, b"%PDF-1.4 but not really")


def test_an_epub_chapter_without_a_heading_is_given_its_title(tmp_path):
    book = epub.EpubBook()
    book.set_identifier("b")
    book.set_title("B")
    chapter = epub.EpubHtml(title="Preface", file_name="preface.xhtml")
    chapter.content = "<p>Why this book.</p>"
    book.add_item(chapter)
    book.toc = [chapter]
    book.spine = [chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    path = tmp_path / "b.epub"
    epub.write_epub(str(path), book)

    assert _titles(to_markdown("b.epub", EPUB, path.read_bytes()).markdown) == ["Preface"]


def test_an_exported_epub_is_a_chapter_per_top_heading_and_converts_back():
    markdown = "# One\n\nFirst.\n\n## One and a half\n\nMiddle.\n\n# Two\n\nSecond.\n"

    exported = export(EPUB, "book", markdown, {})

    assert _titles(to_markdown("book.epub", EPUB, exported).markdown) == ["One", "One and a half", "Two"]


def test_a_comment_in_code_is_not_an_exported_epub_chapter():
    markdown = "# One\n\n```bash\n# a comment\nls\n```\n\n# Two\n\nSecond.\n"

    exported = export(EPUB, "book", markdown, {})

    assert _titles(to_markdown("book.epub", EPUB, exported).markdown) == ["One", "Two"]


def test_an_exported_pdf_has_an_outline_of_its_headings():
    markdown = "# One\n\nFirst.\n\n### Deep\n\nDeeper.\n\n# Two\n\nSecond.\n"

    document = pymupdf.open(stream=export(PDF, "notes", markdown, {}), filetype="pdf")

    # a heading two levels down is put one level down, as an outline must be
    assert document.get_toc() == [[1, "One", 1], [2, "Deep", 1], [1, "Two", 1]]


def test_a_converted_epub_keeps_its_pictures():
    from tests.pdfs import picture

    converted = to_markdown("b.epub", EPUB, make_epub([("Meshing", "Triangles.")], "Meshing", picture()))

    assert list(converted.images) == ["images/picture.png"]
    assert "](images/picture.png)" in converted.markdown
