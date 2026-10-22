from dataclasses import dataclass, field

# where a converted material's images are, as its Markdown refers to them
IMAGES = "images"


class NotConvertible(ValueError):
    """the file can't be converted, e.g. a PDF without text; the message says why, for the student"""


@dataclass
class Converted:
    markdown: str
    # the images the Markdown refers to, by the path it refers to them by, e.g. images/page-1-0.png
    images: dict[str, bytes] = field(default_factory=dict)
