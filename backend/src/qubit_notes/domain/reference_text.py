"""How a Markdown material writes a reference to another part of its course (features/references.feature):
[[subject/topic]], [[subject/topic/material]] or [[subject/topic/material#section]], with an optional label after a
"|". Text in code, fenced or inline, is never a reference."""

import re
from collections.abc import Callable
from dataclasses import dataclass

# [[path]], [[path#section]], [[path|label]] or [[path#section|label]]; in a table the "|" is escaped, "\|"
WRITTEN = re.compile(r"\[\[([^\[\]|#]*)(?:#([^\[\]|]*))?(?:\|([^\[\]]*))?\]\]")
# a code block's fence; ```code``` on a line of its own is code in the text, as a ``` fence has no ` after it
FENCE = re.compile(r"^\s*(```(?!.*`)|~~~)")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")


@dataclass(frozen=True)
class Written:
    """a reference as written: what it names, whether or not the course has it"""

    text: str
    label: str | None
    parts: tuple[str, ...]
    section: str | None

    @property
    def shown_as(self) -> str:
        """its label, else the name of what it refers to"""
        return self.label or self.section or (self.parts[-1] if self.parts else "") or self.text

    @property
    def well_formed(self) -> bool:
        """names a topic, a material, or a material's section"""
        if self.section is not None:
            return len(self.parts) == 3 and bool(self.section)
        return len(self.parts) in (2, 3)


def _written(match: re.Match) -> Written:
    path, section, label = match.groups()
    if label is not None:
        # the backslash of a "\|" in a table is not part of the name
        path, section = path.removesuffix("\\"), section.removesuffix("\\") if section is not None else None
    parts = tuple(part.strip() for part in path.split("/"))
    return Written(
        # as the reader shows it, with a table's "\|" unescaped
        text=match.group(0).replace("\\|", "|"),
        label=(label.strip() or None) if label is not None else None,
        parts=parts if all(parts) else (),
        section=section.strip() if section is not None else None,
    )


def _outside_code(text: str, change: Callable[[str], str]) -> str:
    """the text with ``change`` applied to what isn't code"""
    lines, fence = [], None
    for line in text.split("\n"):
        opened = FENCE.match(line)
        if fence is not None:
            lines.append(line)
            if opened and opened.group(1) == fence:
                fence = None
        elif opened:
            fence = opened.group(1)
            lines.append(line)
        else:
            parts, cursor = [], 0
            for span in CODE_SPAN.finditer(line):
                parts += [change(line[cursor : span.start()]), span.group(0)]
                cursor = span.end()
            lines.append("".join([*parts, change(line[cursor:])]))
    return "\n".join(lines)


def written_in(text: str) -> list[Written]:
    """the references of the Markdown, in order"""
    found: list[Written] = []

    def collect(prose: str) -> str:
        found.extend(_written(match) for match in WRITTEN.finditer(prose))
        return prose

    _outside_code(text, collect)
    return found


def as_text(text: str) -> str:
    """the Markdown with each reference as what it's shown as, e.g. for a PDF made from it"""
    return _outside_code(text, lambda prose: WRITTEN.sub(lambda match: _written(match).shown_as, prose))
