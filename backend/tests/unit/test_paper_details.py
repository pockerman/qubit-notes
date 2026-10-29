"""A paper's details, as far as the paper tells them (conversion/details.py)."""

import pymupdf

from qubit_notes.conversion.details import authors_of, details
from tests.epubs import make_epub
from tests.pdfs import make_pdf, make_pdf_of_lines

PDF = "application/pdf"


def _pdf(text: str, **metadata: str) -> bytes:
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), text, fontsize=11)
    document.set_metadata(metadata)
    return document.tobytes()


def test_a_pdf_without_a_title_of_its_own_is_titled_by_its_largest_text():
    pdf = make_pdf_of_lines([("Attention Is All You Need", 20), ("Abstract", 11), ("The dominant models are", 11)])

    assert details(PDF, pdf).title == "Attention Is All You Need"


def test_a_pdf_whose_text_is_all_alike_has_no_title():
    assert details(PDF, make_pdf(["We propose proximal policy optimization"])).title == ""


def test_a_file_name_is_no_title():
    pdf = _pdf("Some text", title="Microsoft Word - draft3.docx")

    assert details(PDF, pdf).title == ""


def test_a_doi_ends_before_the_punctuation_after_it():
    pdf = _pdf("Published as doi:10.1038/nature14236.")

    assert details(PDF, pdf).doi == "10.1038/nature14236"


def test_a_pdf_without_an_arxiv_identifier_has_no_year_or_venue():
    found = details(PDF, _pdf("Proceedings of something, 2019"))

    assert (found.year, found.venue) == (None, "")


def test_an_epub_has_its_own_title():
    assert details("application/epub+zip", make_epub([("One", "Text.")])).title == "A book"


def test_a_markdown_paper_is_titled_by_its_first_top_heading():
    markdown = b"Preamble\n\n## Not this\n\n# Deep Q-Networks #\n\nText.\n"

    assert details("text/markdown", markdown).title == "Deep Q-Networks"


def test_authors_are_separated_by_semicolons_commas_or_and():
    assert authors_of("Ada Lovelace;  Alan Turing, Grace Hopper and Edsger Dijkstra") == [
        "Ada Lovelace",
        "Alan Turing",
        "Grace Hopper",
        "Edsger Dijkstra",
    ]


def test_what_is_not_a_paper_tells_nothing():
    assert details(PDF, b"not a pdf").title == ""
