"""How references are written in Markdown, beyond the scenarios: labels, sections, malformed ones, tables and code."""

import pytest

from qubit_notes.domain.reference_text import as_text, written_in


@pytest.mark.parametrize(
    ("written", "parts", "section", "shown_as", "well_formed"),
    [
        ("[[a/b]]", ("a", "b"), None, "b", True),
        ("[[a/b/notes.md]]", ("a", "b", "notes.md"), None, "notes.md", True),
        ("[[a/b/notes.md#2 Assembly]]", ("a", "b", "notes.md"), "2 Assembly", "2 Assembly", True),
        ("[[a/b/notes.md#2 Assembly|the assembly]]", ("a", "b", "notes.md"), "2 Assembly", "the assembly", True),
        ("[[ a / b |  the topic ]]", ("a", "b"), None, "the topic", True),
        ("[[b]]", ("b",), None, "b", False),
        ("[[a/b#Intro]]", ("a", "b"), "Intro", "Intro", False),
        ("[[a//c]]", (), None, "[[a//c]]", False),
        ("[[a/b/c/d]]", ("a", "b", "c", "d"), None, "d", False),
    ],
)
def test_a_reference_names_a_topic_a_material_or_a_section(written, parts, section, shown_as, well_formed):
    [found] = written_in(f"See {written}.")

    assert (found.text, found.parts, found.section, found.shown_as, found.well_formed) == (
        written,
        parts,
        section,
        shown_as,
        well_formed,
    )


def test_a_label_in_a_table_is_after_an_escaped_bar():
    [topic, section] = written_in("| [[a/b\\|the topic]] | [[a/b/notes.md#Intro\\|the intro]] |")

    assert (topic.text, topic.parts, topic.shown_as) == ("[[a/b|the topic]]", ("a", "b"), "the topic")
    assert (section.parts, section.section, section.shown_as) == (("a", "b", "notes.md"), "Intro", "the intro")


def test_text_in_code_has_no_references():
    text = "\n".join(
        [
            "Before [[a/b]] and `[[c/d]]`, and ``[[e/f]] `x` ``.",
            "~~~",
            "[[g/h]]",
            "```",
            "[[i/j]]",
            "~~~",
            "After [[k/l]].",
        ]
    )

    assert [r.text for r in written_in(text)] == ["[[a/b]]", "[[k/l]]"]


def test_as_text_shows_each_reference_as_its_label_but_leaves_code_alone():
    text = "See [[a/b|the topic]] and [[a/b/notes.md#Intro]], written `[[a/b]]`."

    assert as_text(text) == "See the topic and Intro, written `[[a/b]]`."
