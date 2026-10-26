"""Steps of flashcards.feature and reviews.feature. The reviews go by a clock the scenarios set, so they can wait days
in an instant."""

import re
from datetime import UTC, datetime, timedelta

from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from tests.bdd.steps.study_steps import _asked, _document_scope, _got, _history, _rows, _section_scope, _topic_scope


class Clock:
    """the time the reviews go by: still, unless a scenario moves it"""

    def __init__(self):
        self.at = datetime.now(UTC)

    def __call__(self) -> datetime:
        return self.at


def _clock(client) -> Clock:
    reviews = client.app.state.reviews
    if not isinstance(reviews.now, Clock):
        reviews.now = Clock()
    return reviews.now


def _duration(text: str) -> timedelta:
    amount, unit = re.fullmatch(r"(\d+) (minute|day)s?", text.strip()).groups()
    return timedelta(minutes=int(amount)) if unit == "minute" else timedelta(days=int(amount))


def _deck(client, students, context, scope: dict, count: int, *, new: bool = False, name=None):
    _clock(client)
    body = {**scope, "cards": count, "new": new}
    response = students.client.post("/api/flashcards", headers=students.headers(name), json=body)
    if name is None:
        _asked(context, "flashcards", scope, response)
        if response.status_code == 200:
            context["deck"] = response.json()
    return response


# asking for flashcards


DECK_OF_SECTION = '{count:d} flashcards of the section "{title}" of "{filename}"'
DECK_OF_DOCUMENT = '{count:d} flashcards of "{filename}"'
DECK_OF_TOPIC = '{count:d} flashcards of the topic "{location}"'


@when(parsers.parse("I ask for " + DECK_OF_SECTION))
@given(parsers.parse("I have asked for " + DECK_OF_SECTION))
def deck_of_section(client, students, context, count, title, filename):
    _deck(client, students, context, _section_scope(students, title, filename), count)


@when(parsers.parse('I ask for {count:d} new flashcards of the section "{title}" of "{filename}"'))
def new_deck_of_section(client, students, context, count, title, filename):
    _deck(client, students, context, _section_scope(students, title, filename), count, new=True)


@when(parsers.parse("I ask for " + DECK_OF_DOCUMENT))
@given(parsers.parse("I have asked for " + DECK_OF_DOCUMENT))
@given(parsers.parse('I have asked for {count:d} flashcard of "{filename}"'))
def deck_of_document(client, students, context, count, filename):
    _deck(client, students, context, _document_scope(students, filename), count)


@when(parsers.parse('I ask for {count:d} new flashcards of "{filename}"'))
def new_deck_of_document(client, students, context, count, filename):
    _deck(client, students, context, _document_scope(students, filename), count, new=True)


@when(parsers.parse("I ask for " + DECK_OF_TOPIC))
@given(parsers.parse("I have asked for " + DECK_OF_TOPIC))
def deck_of_topic(client, students, context, count, location):
    _deck(client, students, context, _topic_scope(students, location), count)


@when(parsers.parse('the student "{name}" asks for {count:d} flashcards of "{filename}"'))
@given(parsers.parse('the student "{name}" has asked for {count:d} flashcards of "{filename}"'))
def they_ask_for_a_deck(client, students, context, name, count, filename):
    context["their_response"] = _deck(client, students, context, _document_scope(students, filename), count, name=name)


# what was got


def _cited(context) -> list[dict]:
    return [card["source"] for card in _got(context)["cards"]]


@then(parsers.parse("I get a deck of {count:d} flashcards"))
def got_a_deck(context, count):
    assert len(_got(context)["cards"]) == count


@then("every card has a front and a back")
def front_and_back(context):
    assert all(card["front"].strip() and card["back"].strip() for card in _got(context)["cards"])


@then(parsers.parse('every card cites one of the sections "{first}" or "{second}" of "{filename}"'))
def every_card_cites_one_of(context, first, second, filename):
    assert all(s["filename"] == filename and s["title"] in (first, second) for s in _cited(context))


@then(parsers.parse('every card cites a section of "{filename}"'))
def every_card_cites(context, filename):
    assert all(s["filename"] == filename for s in _cited(context))


@then(parsers.parse('the cards cite "{first}" and "{second}"'))
def cards_cite_both(context, first, second):
    assert {first, second} <= {s["filename"] for s in _cited(context)}


@then(parsers.parse('no card cites "{filename}"'))
def no_card_cites(context, filename):
    assert filename not in {s["filename"] for s in _cited(context)}


@then(parsers.parse("I am told a deck has between {low:d} and {high:d} cards"))
def deck_size(context, low, high):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"between {low} and {high} cards" in response.json()["detail"]


@then("I get the deck I got before")
def same_deck(context):
    assert _got(context)["id"] == context["got"][0]["id"]


@then("I get a deck I have not seen before")
def new_deck(context):
    latest, earlier = _got(context), context["got"][0]
    assert latest["id"] != earlier["id"]
    assert [c["front"] for c in latest["cards"]] != [c["front"] for c in earlier["cards"]]


@then("no new deck was written")
def no_new_deck(students, context):
    assert len(_history(students, "flashcards", context["scope"])) == 1


@then(parsers.parse('I have {count:d} decks of the section "{title}" of "{filename}", newest first'))
def decks_newest_first(students, context, count, title, filename):
    history = _history(students, "flashcards", _section_scope(students, title, filename))
    assert [d["id"] for d in history] == [d["id"] for d in reversed(context["got"])][:count]
    assert len(history) == count


@then(parsers.parse('I am told the deck is out of date, as "{filename}" was {change} since'))
def deck_out_of_date(context, filename, change):
    assert filename in (_got(context)["out_of_date"] or {}).get(change, [])


@then(parsers.parse('the student "{name}" gets a deck written for them'))
def their_own_deck(students, context, name):
    response = context["their_response"]
    assert response.status_code == 200, response.text
    assert response.json()["id"] != context["got"][0]["id"]
    assert len(_history(students, "flashcards", context["scope"], name=name)) == 1


@then(parsers.parse('I have no flashcards of "{filename}"'))
def no_flashcards(client, context, filename):
    decks, cards = storage.flashcard_decks, storage.flashcards
    deck_id = context["got"][0]["id"]
    with client.app.state.database.connect() as connection:
        assert connection.execute(select(decks).where(decks.c.document_id == context["document_id"])).all() == []
        assert connection.execute(select(cards).where(cards.c.deck_id == deck_id)).all() == []


# reviews


def _due(students, name=None, course_id=None) -> dict:
    params = {"course_id": course_id} if course_id else {}
    response = students.client.get("/api/reviews", headers=students.headers(name), params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _review(students, card_id: str, answer: str, name=None):
    return students.client.post(f"/api/reviews/{card_id}", headers=students.headers(name), json={"answer": answer})


def _card(context) -> dict:
    """the first card of the deck asked for last"""
    return context["deck"]["cards"][0]


@then(parsers.parse("I have {count:d} cards due for review"))
@then(parsers.parse("I have {count:d} card due for review"))
def cards_due(students, count):
    assert len(_due(students)["cards"]) == count


@then("I have no cards due for review")
def nothing_due(students):
    assert _due(students)["cards"] == []


@then(parsers.parse('I have {count:d} cards due for review in the course "{course}"'))
def cards_due_in(students, count, course):
    course_id = next(c["id"] for c in students.courses() if c["name"] == course)
    due = _due(students, course_id=course_id)["cards"]
    assert len(due) == count
    assert {card["course_id"] for card in due} == {course_id}


@then("they are the cards of the new deck")
def cards_of_new_deck(students, context):
    assert {card["deck_id"] for card in _due(students)["cards"]} == {context["deck"]["id"]}


@then(parsers.parse('the student "{name}" has no cards due for review'))
def they_have_nothing_due(students, name):
    assert _due(students, name=name)["cards"] == []


@then(parsers.parse('the student "{name}" has {count:d} cards due for review'))
def they_have_cards_due(students, name, count):
    assert len(_due(students, name=name)["cards"]) == count


@then(parsers.parse('the student "{name}" can\'t review their cards'))
def they_cannot_review(students, context, name):
    for card in context["their_response"].json()["cards"]:
        assert _review(students, card["id"], "good", name=name).status_code == 404


@when(parsers.parse('I review the card and remembered it "{answer}"'))
def review_the_card(students, context, answer):
    context["review"] = _review(students, _card(context)["id"], answer)


@then(parsers.parse("the card is due again in {due}"))
def due_again_in(client, context, due):
    response = context["review"]
    assert response.status_code == 200, response.text
    due_at = datetime.fromisoformat(response.json()["due_at"])
    assert due_at - _clock(client)() == _duration(due)


@then(parsers.parse("I have {count:d} card due for review after {due}"))
@then(parsers.parse("I have {count:d} cards due for review after {due}"))
def due_after(client, students, count, due):
    _clock(client).at += _duration(due)
    assert len(_due(students)["cards"]) == count


@when("I review the card each time it is due, and remember it:")
def review_each_time(client, students, context, datatable):
    clock, card_id = _clock(client), _card(context)["id"]
    for row in _rows(datatable):
        due = _due(students)
        if not due["cards"]:
            clock.at = datetime.fromisoformat(due["next_due_at"])
            due = _due(students)
        assert [card["id"] for card in due["cards"]] == [card_id]
        response = _review(students, card_id, row["answer"])
        assert response.status_code == 200, response.text
        due_at = datetime.fromisoformat(response.json()["due_at"])
        assert due_at - clock() == _duration(row["due again in"]), row


@then("I am told to answer Again, Hard, Good or Easy")
def told_to_answer(context):
    response = context["review"]
    assert response.status_code == 422, response.text
    assert "again, hard, good or easy" in response.json()["detail"]


@when(parsers.parse('the student "{name}" reviews my card'))
def they_review_my_card(students, context, name):
    context["review"] = _review(students, _card(context)["id"], "good", name=name)


@then("they are told there is no such card")
def no_such_card(context):
    assert context["review"].status_code == 404, context["review"].text
