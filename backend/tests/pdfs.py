"""Builds small PDFs with text and an outline, for tests."""

from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def make_pdf(pages: list[str], outline: list[tuple[str, int, int]] = ()) -> bytes:
    """a PDF of the pages' texts, with outline entries (title, level, 1-based page) in order"""
    writer = PdfWriter()
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
    )
    for text in pages:
        page = writer.add_blank_page(width=612, height=792)
        stream = DecodedStreamObject()
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
            }
        )

    parents = {}
    for title, level, page in outline:
        parents[level] = writer.add_outline_item(title, page - 1, parent=parents.get(level - 1))

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def make_pdf_of_lines(lines: list[tuple[str, float]]) -> bytes:
    """a one-page PDF of the lines, each in its own size of font, with no outline"""
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    y = 72
    for text, size in lines:
        page.insert_text((72, y), text, fontsize=size)
        y += size * 2
    return document.tobytes()


def picture(width: int = 200, height: int = 150) -> bytes:
    """a PNG of one colour"""
    import pymupdf

    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, width, height), False)
    pixmap.set_rect(pixmap.irect, (200, 30, 30))
    return pixmap.tobytes("png")


def make_pdf_with_picture(title: str, text: str) -> bytes:
    """a one-page PDF with an outline entry, a line of text and a picture"""
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text, fontsize=11)
    page.insert_image(pymupdf.Rect(72, 100, 372, 325), stream=picture())
    document.set_toc([[1, title, 1]])
    return document.tobytes()


def make_scanned_pdf() -> bytes:
    """a PDF of a picture of a page, without text"""
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    page.insert_image(page.rect, stream=picture(600, 800))
    return document.tobytes()
