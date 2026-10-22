"""Divides sections into the chunks search finds: runs of words that overlap a little, never spanning two sections,
small enough for every embedding model (bge-small-en-v1.5 reads at most 512 tokens)."""

from qubit_notes.platform.port import SectionText

WORDS = 200
OVERLAP = 30


def chunks(sections: list[SectionText], size: int = WORDS, overlap: int = OVERLAP) -> list[tuple[int, str]]:
    """the chunks of the sections, each as (its section's position, its text)"""
    found = []
    step = max(1, size - overlap)
    for part in sections:
        words = part.content.split()
        for start in range(0, len(words), step):
            found.append((part.section.position, " ".join(words[start : start + size])))
            if start + size >= len(words):
                break
    return found
