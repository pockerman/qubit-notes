import re

from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, then, when


def _sign_in(page: Page, students, name: str) -> None:
    students.me = name
    page.goto("/")
    page.get_by_label("Your name").fill(students.id(name))
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text(f"Signed in as {students.id(name)}")).to_be_visible()


def _topic(page: Page, subject: str, topic: str):
    return page.get_by_role("region", name=f"{subject} › {topic}")


def slug(name: str) -> str:
    """a name as the app stores it, e.g. "Computer Science" as computer-science"""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def go_to_courses(page: Page) -> None:
    # reloaded, as courses may have been created since the page was loaded
    page.goto("/#/")
    page.reload()
    expect(page.get_by_role("heading", name="My courses", level=2)).to_be_visible()


def open_course_page(page: Page, course: str) -> None:
    go_to_courses(page)
    page.get_by_role("list", name="Courses").get_by_role("link", name=re.compile(f"^{course}\\b")).click()
    expect(page.get_by_role("heading", name=course, level=2)).to_be_visible()


def create_course_in_browser(page: Page, name: str) -> None:
    go_to_courses(page)
    page.get_by_role("button", name="Create new course").click()
    form = page.get_by_role("form", name="New course")
    form.get_by_label("Course name").fill(name)
    form.get_by_role("button", name="Create course").click()
    expect(page.get_by_role("heading", name=slug(name), level=2)).to_be_visible()


def upload_on_add_page(page: Page, filename: str, subject: str | None, topic: str | None) -> None:
    """on the Add material page, which may have the topic filled in already"""
    expect(page.get_by_role("heading", name=re.compile("^Add material"), level=2)).to_be_visible()
    form = page.get_by_role("form", name=re.compile("^Upload to "))
    if subject is not None:
        form.get_by_label("Subject").fill(subject)
    if topic is not None:
        form.get_by_label("Topic").fill(topic)
    form.get_by_label("File").set_input_files(
        {"name": filename, "mimeType": "text/plain", "buffer": f"Notes on {topic or 'the topic'}.".encode()}
    )
    form.get_by_role("button", name="Upload").click()


@when("I open the study assistant")
def open_app(page):
    page.goto("/")


@when(parsers.parse('I sign in as "{name}"'))
def sign_in(page, students, name):
    _sign_in(page, students, name)


@given(parsers.parse('I am signed in as "{name}"'))
def signed_in(page, students, name):
    _sign_in(page, students, name)


@then(parsers.parse('I see that I am signed in as "{name}"'))
def see_signed_in(page, students, name):
    expect(page.get_by_text(f"Signed in as {students.id(name)}")).to_be_visible()


@then("I see that the platform is connected")
def see_connected(page):
    expect(page.get_by_role("status").filter(has_text="Platform connected")).to_be_visible()


@then("I see that I have no courses yet")
def see_no_courses(page):
    expect(page.get_by_text("You have no courses yet.")).to_be_visible()


@when(parsers.parse('I upload "{filename}" to the course "{course}", subject "{subject}", topic "{topic}"'))
def upload_in_browser(page, context, filename, course, subject, topic):
    context["course"] = slug(course)
    go_to_courses(page)
    if page.get_by_role("list", name="Courses").get_by_role("link", name=re.compile(f"^{slug(course)}\\b")).count():
        open_course_page(page, slug(course))
    else:
        create_course_in_browser(page, course)
    page.get_by_role("link", name="Add material", exact=True).click()
    upload_on_add_page(page, filename, subject, topic)
    # back in the course, where the material shows as ready once processed; that takes a while on gogi
    expect(page.get_by_role("listitem").filter(has_text=filename)).to_contain_text("ready", timeout=120_000)


@then(parsers.parse('I see the course "{course}" in my courses'))
def see_course(page, course):
    go_to_courses(page)
    cards = page.get_by_role("list", name="Courses")
    expect(cards.get_by_role("link", name=re.compile(f"^{course}\\b"))).to_be_visible()


@when(parsers.parse('I open the course "{course}"'))
def open_course(page, course):
    open_course_page(page, course)


@then(parsers.parse('I see "{filename}" under "{subject}" › "{topic}"'))
def see_under(page, context, filename, subject, topic):
    # the scenario may have looked at its courses since, which are on a page of their own
    if context.get("course") and page.get_by_role("heading", name="My courses", level=2).count():
        open_course_page(page, context["course"])
    expect(_topic(page, subject, topic).get_by_text(filename)).to_be_visible()


@then(parsers.parse('I see that "{filename}" is ready'))
def see_ready(page, filename):
    expect(page.get_by_role("listitem").filter(has_text=filename)).to_contain_text("ready", timeout=120_000)


@then(parsers.parse('I see the subjects "{subjects}"'))
def see_subjects(page, subjects):
    expect(page.get_by_role("main").get_by_role("heading", level=3)).to_have_text(
        [subject.strip() for subject in subjects.split(",")]
    )


@when(parsers.parse('I delete "{filename}"'))
def delete_in_browser(page, filename):
    page.get_by_role("button", name=f"Delete {filename}").click()


@then(parsers.parse('I no longer see "{filename}"'))
def no_longer_see(page, filename):
    expect(page.get_by_role("main").get_by_text(filename)).to_have_count(0)


@when(parsers.parse('I share it with "{name}" as {role}'))
def share_in_browser(page, students, name, role):
    form = page.get_by_role("form", name="Share this course")
    form.get_by_label("Classmate").fill(students.id(name))
    form.get_by_label("Role").select_option({"a reader": "reader", "an owner": "owner"}[role])
    form.get_by_role("button", name="Share").click()


@then(parsers.parse('I see "{name}" as {role} of the course'))
def see_member(page, students, name, role):
    member = page.get_by_role("list", name="Members").get_by_role("listitem").filter(has_text=students.id(name))
    expect(member).to_contain_text({"a reader": "reader", "an owner": "owner"}[role])


@when("I open its members")
def open_members(page):
    page.get_by_role("link", name="Members", exact=True).click()
    expect(page.get_by_role("heading", name=re.compile("^Members of "), level=2)).to_be_visible()


@then("I do not see the members on the course page")
def no_members_on_course_page(page):
    expect(page.get_by_role("list", name="Members")).to_have_count(0)
    expect(page.get_by_role("form", name="Share this course")).to_have_count(0)


@then(parsers.parse('I can go back to the course "{course}"'))
def back_to_course(page, course):
    page.get_by_role("link", name=f"← {course}").click()
    expect(page.get_by_role("heading", name=course, level=2)).to_be_visible()


@then("I am not offered to share the course")
def not_offered_to_share(page):
    expect(page.get_by_role("list", name="Members")).to_be_visible()
    expect(page.get_by_role("form", name="Share this course")).to_have_count(0)


@then(parsers.parse('I see that the course is shared with me by "{owner}" as {role}'))
def see_shared(page, students, owner, role):
    expect(page.get_by_text(f"Shared with you by {students.id(owner)} as {role}")).to_be_visible()


@then("I cannot upload, delete or share in this course")
def cannot_change(page):
    course = page.get_by_role("main")
    expect(course.get_by_role("button", name=re.compile("^Delete "))).to_have_count(0)
    expect(course.get_by_role("link", name=re.compile("^Add material"))).to_have_count(0)
    expect(course.get_by_role("form", name="Share this course")).to_have_count(0)


# reading


@when(parsers.parse('I open "{filename}" to read it'))
def open_to_read(page, filename):
    page.get_by_role("link", name=filename, exact=True).click()
    expect(page.get_by_role("heading", name=filename, level=2)).to_be_visible()


@then(parsers.parse('I see its sections "{titles}"'))
def see_its_sections(page, titles):
    outline = page.get_by_role("navigation", name="Sections")
    expect(outline.get_by_role("button")).to_have_text([title.strip() for title in titles.split(",")])


@when(parsers.parse('I choose the section "{title}"'))
def choose_section(page, title):
    page.get_by_role("navigation", name="Sections").get_by_role("button", name=title, exact=True).click()


@given(parsers.parse("my screen is {width:d} pixels wide"))
def screen_width(page, width):
    page.set_viewport_size({"width": width, "height": 900})


@then(parsers.parse("the text is at least {percent:d}% of the page wide"))
def text_width(page, percent):
    text = page.get_by_role("article", name="Section text")
    expect(text).to_be_visible()
    assert text.bounding_box()["width"] >= page.viewport_size["width"] * percent / 100, text.bounding_box()


def _section_text(page: Page):
    return page.get_by_role("article", name="Section text")


@then(parsers.parse('I see a table with the columns "{columns}"'))
def see_table(page, columns):
    table = _section_text(page).get_by_role("table")
    expect(table.get_by_role("columnheader")).to_have_text([column.strip() for column in columns.split(",")])


@then("the table has the rows:")
def table_rows(page, datatable):
    rows = _section_text(page).get_by_role("table").get_by_role("row")
    expect(rows).to_have_count(len(datatable))
    for row, cells in zip(rows.all(), datatable):
        expect(row.get_by_role("columnheader").or_(row.get_by_role("cell"))).to_have_text(cells)


@then(parsers.parse('"{label}" links to "{href}"'))
def links_to(page, label, href):
    expect(_section_text(page).get_by_role("link", name=label)).to_have_attribute("href", href)


@then(parsers.parse('"{text}" is in bold'))
def in_bold(page, text):
    expect(_section_text(page).locator("strong", has_text=text)).to_be_visible()


@then(parsers.parse('"{text}" is shown as code'))
def as_code(page, text):
    expect(_section_text(page).locator("pre code", has_text=text)).to_be_visible()


@then(parsers.parse('I see the text "{text}"'))
def see_text(page, text):
    expect(page.get_by_role("article", name="Section text")).to_contain_text(text)


# notes

SELECT_PASSAGE = """(passage) => {
    const article = document.querySelector('article[aria-label="Section text"]')
    const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT)
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const at = node.textContent.indexOf(passage)
        if (at < 0) continue
        const range = document.createRange()
        range.setStart(node, at)
        range.setEnd(node, at + passage.length)
        const selection = window.getSelection()
        selection.removeAllRanges()
        selection.addRange(range)
        article.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
        return true
    }
    return false
}"""


def _save_note(page: Page, text: str) -> None:
    form = page.get_by_role("form", name="New note")
    form.get_by_label("Note").fill(text)
    form.get_by_role("button", name="Save note").click()


@when(parsers.parse('I select "{passage}" and note "{text}"'))
def select_and_note(page, passage, text):
    expect(page.get_by_role("article", name="Section text")).to_contain_text(passage)
    assert page.evaluate(SELECT_PASSAGE, passage), f"{passage!r} is not in the text"
    _save_note(page, text)


@when(parsers.parse('I select the passage "{passage}"'))
def select_passage(page, passage):
    expect(page.get_by_role("article", name="Section text")).to_contain_text(passage)
    assert page.evaluate(SELECT_PASSAGE, passage), f"{passage!r} is not in the text"


PASSAGE_BOX = """(passage) => {
    const article = document.querySelector('article[aria-label="Section text"]')
    const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT)
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const at = node.textContent.indexOf(passage)
        if (at < 0) continue
        const range = document.createRange()
        range.setStart(node, at)
        range.setEnd(node, at + passage.length)
        const box = range.getBoundingClientRect()
        return { top: box.top, bottom: box.bottom }
    }
    return null
}"""


@then(parsers.parse('the new note opens to the left of the text, level with "{passage}"'))
def note_opens_beside(page, passage):
    form = page.get_by_role("form", name="New note")
    expect(form).to_be_visible()
    note = form.bounding_box()
    text = page.get_by_role("article", name="Section text").bounding_box()
    words = page.evaluate(PASSAGE_BOX, passage)
    assert note["x"] + note["width"] <= text["x"], (note, text)
    # the note starts on the passage's line
    assert words["top"] - 4 <= note["y"] <= words["bottom"] + 4, (note, words)


@when(parsers.parse('I note "{text}" at the current moment of the video'))
def note_at_current_moment(page, text):
    page.get_by_role("button", name=re.compile(r"^Add note at")).click()
    _save_note(page, text)


@then(parsers.parse('I see my note "{text}" at {moment}'))
def see_my_note_at(page, text, moment):
    note = page.get_by_role("complementary", name="My notes").get_by_role("listitem", name=f"Note: {text}")
    expect(note.get_by_role("button", name=moment)).to_be_visible()


@then(parsers.parse('I see my note "{text}"'))
def see_my_note(page, text):
    expect(
        page.get_by_role("complementary", name="My notes").get_by_role("listitem", name=f"Note: {text}")
    ).to_be_visible()


@then(parsers.parse('the passage "{passage}" is highlighted'))
def passage_highlighted(page, passage):
    expect(page.get_by_role("article", name="Section text").locator("mark", has_text=passage)).to_be_visible()


# the assistant


def _assistant(page: Page):
    return page.get_by_role("complementary", name="Assistant")


@when("I open the assistant")
def open_assistant(page):
    page.get_by_role("button", name="AI", exact=True).click()
    expect(_assistant(page)).to_be_visible()


@when(parsers.parse('I ask "{question}"'))
def ask(page, question):
    assistant = _assistant(page)
    turns = assistant.get_by_role("list", name="Conversation").locator("li.turn")
    before = turns.count()
    assistant.get_by_role("textbox", name="Ask the assistant").fill(question)
    assistant.get_by_role("button", name="Ask", exact=True).click()
    # the AI may take minutes on a local model
    expect(assistant.get_by_text("Thinking…")).to_have_count(0, timeout=600_000)
    expect(turns).to_have_count(before + 1)


def _cites(reply, title: str) -> None:
    reply.get_by_text(re.compile(r"^From \d+ sections?$")).click()
    expect(reply.get_by_role("listitem").filter(has_text=title)).to_be_visible()


@then(parsers.parse('I see an answer that cites "{title}"'))
def see_answer(page, title):
    answer = _assistant(page).get_by_role("region", name="Answer").last
    expect(answer.locator(".markdown")).not_to_be_empty()
    _cites(answer, title)


@then(parsers.parse('I see a summary drawn from "{title}"'))
def see_summary(page, title):
    summary = _assistant(page).get_by_role("region", name="Summary").last
    expect(summary.locator(".markdown")).not_to_be_empty()
    _cites(summary, title)


@when("I answer every question with its first choice")
def answer_first_choices(page):
    quiz = _assistant(page).get_by_role("region", name="Quiz").last
    for question in quiz.get_by_role("group").all():
        question.get_by_role("radio").first.check()
    quiz.get_by_role("button", name="Check my answers").click()


@then(parsers.parse("I see that I scored {score:d} out of {total:d}"))
def see_score(page, score, total):
    expect(page.get_by_role("status").filter(has_text="You scored")).to_have_text(f"You scored {score} out of {total}")


@then(parsers.parse('I see the buttons "{first}", "{second}" and "{third}" together'))
def see_buttons_together(page, first, second, third):
    actions = page.get_by_role("group", name="Material actions")
    expect(actions.get_by_role("button")).to_have_text([first, second, third])


@then(parsers.parse('I see no "{first}" or "{second}" button'))
def see_no_buttons(page, first, second):
    for name in (first, second):
        expect(page.get_by_role("button", name=name)).to_have_count(0)


@when(parsers.parse('I study the topic "{topic}"'))
def study_topic(page, topic):
    page.get_by_role("region", name=re.compile(f"› {topic}$")).get_by_role("link", name="Study this topic").click()
    expect(page.get_by_role("heading", name=re.compile(f"› {topic}$"), level=2)).to_be_visible()


# courses and topics


@then("I am offered to create a new course")
def offered_to_create(page):
    expect(page.get_by_role("button", name="Create new course")).to_be_visible()


@then(parsers.parse('I am in the course "{course}"'))
@then(parsers.parse('I am back in the course "{course}"'))
def in_course(page, course):
    expect(page.get_by_role("heading", name=course, level=2)).to_be_visible()


@when("I delete the course, and confirm it")
def delete_course_confirmed(page):
    page.get_by_role("button", name="Delete course").click()
    page.get_by_role("alertdialog", name="Delete this course").get_by_role(
        "button", name=re.compile("^Yes, delete ")
    ).click()


@when("I delete the course, but cancel")
def delete_course_cancelled(page):
    page.get_by_role("button", name="Delete course").click()
    page.get_by_role("alertdialog", name="Delete this course").get_by_role("button", name="Cancel").click()
    expect(page.get_by_role("alertdialog")).to_have_count(0)


@then("I am in my courses")
def in_my_courses(page):
    expect(page.get_by_role("heading", name="My courses", level=2)).to_be_visible()


@then("I am not offered to delete the course")
def not_offered_to_delete(page):
    # an owner who didn't create the course still manages its material
    expect(page.get_by_role("link", name="Add material", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Delete course")).to_have_count(0)


@then("I see that it has no material yet")
def no_material_yet(page):
    expect(page.get_by_text("This course has no material yet.")).to_be_visible()


@when("I go to my courses")
def go_to_my_courses(page):
    go_to_courses(page)


@then(parsers.parse('I see the courses "{courses}"'))
def see_courses_listed(page, courses):
    cards = page.get_by_role("list", name="Courses").get_by_role("link")
    expect(cards.locator("strong")).to_have_text([course.strip() for course in courses.split(",")])


@when(parsers.parse('I add "{filename}" to the subject "{subject}", topic "{topic}"'))
def add_to_subject_topic(page, filename, subject, topic):
    page.get_by_role("link", name="Add material", exact=True).click()
    upload_on_add_page(page, filename, subject, topic)


@when(parsers.parse('I add "{filename}" to the topic "{topic}"'))
def add_to_topic(page, filename, topic):
    page.get_by_role("link", name=f"Add material to {topic}").click()
    # the topic is filled in already
    upload_on_add_page(page, filename, None, None)


@then(parsers.parse('I still see the topic "{subject}" › "{topic}", with no material'))
def topic_without_material(page, subject, topic):
    expect(_topic(page, subject, topic).get_by_text("No material yet")).to_be_visible()


@when(parsers.parse('I create the topic "{topic}" in the subject "{subject}"'))
def create_topic_in_browser(page, topic, subject):
    page.get_by_role("button", name="New topic").click()
    form = page.get_by_role("form", name="New topic")
    form.get_by_label("Subject").fill(subject)
    form.get_by_label("Topic").fill(topic)
    form.get_by_role("button", name="Create topic").click()


@when(parsers.parse('I add the topic "{topic}" to the subject "{subject}"'))
def add_topic_to_subject(page, topic, subject):
    page.get_by_role("button", name=f"Add a topic to {subject}").click()
    form = page.get_by_role("form", name=f"New topic in {subject}")
    # the subject is the one the topic is added to, not asked again
    expect(form.get_by_label("Subject")).to_have_count(0)
    form.get_by_label("Topic").fill(topic)
    form.get_by_role("button", name="Create topic").click()


@then("I am not offered to create a topic")
def not_offered_to_create_topic(page):
    course = page.get_by_role("main")
    expect(course.get_by_role("heading", level=3).first).to_be_visible()
    expect(course.get_by_role("button", name="New topic")).to_have_count(0)
    expect(course.get_by_role("button", name=re.compile("^Add a topic to "))).to_have_count(0)


@when("I edit its text to:")
def edit_text_in_browser(page, docstring):
    page.get_by_role("button", name="Edit", exact=True).click()
    form = page.get_by_role("form", name="Edit material")
    form.get_by_label("Text").fill(docstring)
    form.get_by_role("button", name="Save").click()
    # once processed, the reader shows the material again
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible(timeout=120_000)
