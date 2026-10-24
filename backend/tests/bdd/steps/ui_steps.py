import re
from urllib.parse import unquote

from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, then, when


def _sign_in(page: Page, students, name: str) -> None:
    students.me = name
    page.goto("/")
    # another student of the scenario may be signed in already
    menu = page.get_by_role("button", name="Menu")
    expect(page.get_by_label("Your name").or_(menu)).to_be_visible()
    if menu.is_visible():
        choose_from_menu(page, "Sign out")
    page.get_by_label("Your name").fill(students.id(name))
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text(f"Signed in as {students.id(name)}")).to_be_visible()


def choose_from_menu(page: Page, item: str) -> None:
    """chooses an item of the app's menu, in the bar"""
    page.get_by_role("button", name="Menu").click()
    page.get_by_role("menu", name="Menu").get_by_role("menuitem", name=item).click()


def _topic(page: Page, subject: str, topic: str):
    """a topic as its subject's page lists it"""
    open_subject_page(page, subject)
    return page.get_by_role("region", name=f"{subject} › {topic}")


def _page_title(page: Page) -> str:
    """the heading of the page shown: a course's name, "subject › topic", a material's filename, …"""
    heading = page.get_by_role("main").get_by_role("heading", level=2).first
    expect(heading).to_be_visible()
    return heading.inner_text()


def open_subject_page(page: Page, subject: str) -> None:
    """the subject's page, from the course page, a subject's page or a topic's"""
    title = _page_title(page)
    if page.locator("#subject-title").count() and title == subject:
        return
    # a topic's page goes back to its subject's, and a subject's to the course
    if page.locator("#topic-title").count():
        page.get_by_role("link", name=re.compile("^← Back to ")).click()
        expect(page.locator("#subject-title")).to_be_visible()
        if _page_title(page) == subject:
            return
    if page.locator("#subject-title").count():
        page.get_by_role("link", name=re.compile("^← Back to ")).click()
    expect(page.locator("#course-title")).to_be_visible()
    page.get_by_role("list", name="Subjects").get_by_role("link", name=subject, exact=True).click()
    expect(page.locator("#subject-title")).to_have_text(subject)


def open_topic_page(page: Page, subject: str, topic: str) -> None:
    """the topic's page, from the course page, a subject's page or another topic's"""
    if _page_title(page) == f"{subject} › {topic}":
        return
    _topic(page, subject, topic).get_by_role("link", name=topic, exact=True).click()
    expect(page.get_by_role("heading", name=f"{subject} › {topic}", level=2)).to_be_visible()


def open_topic_of(page: Page, students, filename: str) -> None:
    """the page of the topic the material is in, unless a page with the material is shown already"""
    if " › " in _page_title(page):
        return
    material = students.find_material(filename)
    open_topic_page(page, *_names(students, material["course"], material["subject"], material["topic"]))


def _names(students, course: str, subject: str, topic: str) -> tuple[str, str]:
    """what a subject and topic are called, by their ids, as the app shows them"""
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert response.status_code == 200, response.text
    named = next(t for t in response.json() if (t["subject"], t["topic"]) == (subject, topic))
    return named["subject_name"], named["name"]


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
    # shown by the title typed
    expect(page.get_by_role("heading", name=name, level=2)).to_be_visible()


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


@when("I open qubit-notes")
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
    context["course"] = course
    go_to_courses(page)
    if (
        page.get_by_role("list", name="Courses")
        .get_by_role("link", name=re.compile(f"^{re.escape(course)}\\b"))
        .count()
    ):
        open_course_page(page, course)
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
    # a topic's material is on its page
    open_topic_page(page, subject, topic)
    expect(page.get_by_role("list", name="Materials").get_by_text(filename, exact=True)).to_be_visible()


@then(parsers.parse('I see that "{filename}" is ready'))
def see_ready(page, filename):
    expect(page.get_by_role("listitem").filter(has_text=filename)).to_contain_text("ready", timeout=120_000)


@then(parsers.parse('I see the subjects "{subjects}"'))
def see_subjects(page, subjects):
    expect(page.get_by_role("main").get_by_role("heading", level=3)).to_have_text(
        [subject.strip() for subject in subjects.split(",")]
    )


@when(parsers.parse('I delete "{filename}"'))
def delete_in_browser(page, students, filename):
    open_topic_of(page, students, filename)
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
def open_to_read(page, students, filename):
    open_topic_of(page, students, filename)
    # the material in its topic's list, not a mention of another topic
    page.get_by_role("link", name=filename, exact=True).and_(page.locator("a.filename")).click()
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
    # the text being read, or the preview of the text being written
    return page.get_by_role("article", name=re.compile("^(Section text|Preview)$"))


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


@then(parsers.re(r'"(?P<tex>.+)" is typeset as mathematics, (?P<where>in the text|on a line of its own)$'))
def typeset(page, tex, where):
    # KaTeX keeps the LaTeX it typeset in the MathML it writes for screen readers
    kind = "span.math.math-display" if where == "on a line of its own" else "span.math:not(.math-display)"
    source = page.locator('annotation[encoding="application/x-tex"]', has_text=re.compile(f"^{re.escape(tex)}$"))
    expect(page.get_by_role("main").locator(kind).filter(has=source)).to_have_count(1)


@then(parsers.re(r'I see "(?P<tex>.+)" as written, marked as mathematics that could not be typeset$'))
def not_typeset(page, tex):
    error = page.get_by_role("main").locator("code.math-error")
    expect(error).to_have_text(tex)
    expect(error).to_have_attribute("title", re.compile("^Could not typeset this: "))


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


# courses and topics


@then("I am offered to create a new course")
def offered_to_create(page):
    expect(page.get_by_role("button", name="Create new course")).to_be_visible()


# the name in quotes only: "I am in the course "…" at the topic …" is a step of its own
@then(parsers.re(r'I am (?:back )?in the course "(?P<course>[^"]+)"$'))
def in_course(page, course):
    expect(page.get_by_role("heading", name=course, level=2)).to_be_visible()


@when(parsers.parse('I move the topic "{topic}" {direction}'))
def move_topic(page, topic, direction):
    page.get_by_role("button", name=f"Move {topic} {direction}").click()


@then(parsers.parse('the topics of "{subject}" are shown in the order "{topics}"'))
def topics_shown_in_order(page, context, subject, topics):
    open_subject_page(page, subject)
    order = [topic.strip() for topic in topics.split(",")]
    expect(page.get_by_role("region", name=subject, exact=True).get_by_role("heading", level=4)).to_have_text(order)
    context["topic order"] = (subject, order)


@then("they are still in that order when I open the subject again")
def still_in_order(page, context):
    subject, order = context["topic order"]
    page.reload()
    expect(page.get_by_role("region", name=subject, exact=True).get_by_role("heading", level=4)).to_have_text(order)


@then("I am not offered to move topics")
def not_offered_to_move(page):
    expect(page.get_by_role("main").get_by_role("heading", level=4).first).to_be_visible()
    expect(page.get_by_role("button", name=re.compile(r"^Move .* (up|down)$"))).to_have_count(0)


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


def _add_form(page: Page):
    return page.get_by_role("form", name=re.compile("^Upload to "))


@when(parsers.re(r'on the Add material page I fill in the subject "(?P<subject>[^"]+)"$'))
def fill_in_subject_on_add_page(page, subject):
    page.get_by_role("link", name="Add material", exact=True).click()
    expect(page.get_by_role("heading", name=re.compile("^Add material"), level=2)).to_be_visible()
    _add_form(page).get_by_label("Subject").fill(subject)


@when(parsers.re(r'I fill in the topic "(?P<topic>[^"]+)"$'))
def fill_in_topic_on_add_page(page, topic):
    _add_form(page).get_by_label("Topic").fill(topic)


@when(parsers.re(r'I choose the file "(?P<filename>[^"]+)"$'))
def choose_file_on_add_page(page, filename):
    _add_form(page).get_by_label("File").set_input_files(
        {"name": filename, "mimeType": "text/plain", "buffer": b"Notes."}
    )


@then(parsers.re(r'its button says "(?P<label>[^"]+)"$'))
def add_button_says(page, label):
    expect(_add_form(page).locator('button[type="submit"]')).to_have_text(label)


@when("I press it")
def press_add_button(page):
    _add_form(page).locator('button[type="submit"]').click()


@then(parsers.re(r'I am told the subject "(?P<subject>[^"]+)" is created, and can add a topic to it$'))
def told_subject_created(page, subject):
    form = _add_form(page)
    expect(form.get_by_role("status")).to_have_text(f"Created the subject {subject}. Fill in a topic to add one to it.")
    # the subject stays, for the topic
    expect(form.get_by_label("Subject")).to_have_value(subject)


@then("I am told to fill in the topic the file goes in")
def told_to_fill_in_topic(page):
    expect(_add_form(page).get_by_role("alert")).to_have_text("Fill in the topic the file goes in")


@then("I see that the topic has no material yet")
def topic_has_no_material(page):
    expect(page.get_by_role("main").get_by_text("No material yet", exact=True)).to_be_visible()


def _open_topic_named(page: Page, students, topic: str) -> None:
    """the page of the topic, from the course page or a subject's, whatever its subject"""
    if _page_title(page).endswith(f" › {topic}"):
        return
    # the course shown, by its id in the address, and the subject it has a topic of that name in
    course_id = unquote(re.search(r"#/courses/([^/?]+)", page.url).group(1))
    courses = students.client.get("/api/courses", headers=students.headers()).json()
    course = next(c["name"] for c in courses if c["id"] == course_id)
    topics = students.client.get(f"/api/courses/{course}/topics", headers=students.headers()).json()
    open_topic_page(page, next(t["subject_name"] for t in topics if t["name"] == topic), topic)


@when(parsers.parse('I add "{filename}" to this topic'))
def add_to_this_topic(page, filename):
    page.get_by_role("link", name=re.compile("^Add material to ")).click()
    # the topic is filled in already
    upload_on_add_page(page, filename, None, None)
    expect(page.get_by_role("list", name="Materials").get_by_text(filename, exact=True)).to_be_visible()


@then(parsers.parse('I still see the topic "{subject}" › "{topic}", with no material'))
def topic_without_material(page, subject, topic):
    expect(_topic(page, subject, topic).get_by_label(f"Status of {topic}")).to_have_text("no material")


@when(parsers.re(r'I create the topic "(?P<topic>[^"]+)" in the subject "(?P<subject>[^"]+)"$'))
def create_topic_in_browser(page, topic, subject):
    page.get_by_role("button", name="New topic").click()
    form = page.get_by_role("form", name="New topic")
    form.get_by_label("Subject").fill(subject)
    form.get_by_label("Topic").fill(topic)
    form.get_by_role("button", name="Create topic").click()


@when(parsers.parse('I add the topic "{topic}" to the subject "{subject}"'))
def add_topic_to_subject(page, topic, subject):
    open_subject_page(page, subject)
    page.get_by_role("button", name=f"Add a topic to {subject}").click()
    form = page.get_by_role("form", name=f"New topic in {subject}")
    # the subject is the one the topic is added to, not asked again
    expect(form.get_by_label("Subject")).to_have_count(0)
    form.get_by_label("Topic").fill(topic)
    form.get_by_role("button", name="Create topic").click()


@when(parsers.re(r'I create the subject "(?P<name>[^"]+)"$'))
def create_subject_in_browser(page, name):
    page.get_by_role("button", name="New subject").click()
    form = page.get_by_role("form", name="New subject")
    form.get_by_label("Subject").fill(name)
    form.get_by_role("button", name="Create subject").click()
    expect(form).to_have_count(0)


@then(parsers.re(r'I see the subject "(?P<subject>[^"]+)" with no topics yet$'))
def see_subject_without_topics(page, subject):
    expect(page.locator("#subject-title")).to_have_text(subject)
    expect(page.get_by_role("main").get_by_text("No topics yet")).to_be_visible()
    expect(page.get_by_role("main").get_by_role("heading", level=4)).to_have_count(0)


@then(parsers.re(r'the subject offers "(?P<first>[^"]+)", "(?P<second>[^"]+)" and "(?P<third>[^"]+)"$'))
def subject_offers(page, first, second, third):
    expect(page.locator("#subject-title")).to_be_visible()
    expect(page.locator("header.page-header").get_by_role("button")).to_have_text([first, second, third])


@when(parsers.re(r'I delete the subject "(?P<subject>[^"]+)"$'))
def delete_subject_in_browser(page, subject):
    page.get_by_role("button", name=f"Delete {subject}", exact=True).click()
    # back on the course page
    expect(page.locator("#course-title")).to_be_visible()


@then(parsers.re(r'the subject "(?P<subject>[^"]+)", which has topics, does not offer "(?P<action>[^"]+)"$'))
def subject_does_not_offer(page, subject, action):
    expect(page.locator("#subject-title")).to_have_text(subject)
    expect(page.get_by_role("main").get_by_role("heading", level=4).first).to_be_visible()
    expect(page.locator("header.page-header").get_by_role("button", name=action)).to_have_count(0)


def _rename(page, name: str, new_name: str, cancel: bool = False, label: str = "Name") -> None:
    page.get_by_role("button", name=f"Rename {name}", exact=True).click()
    form = page.get_by_role("form", name=f"Rename {name}")
    form.get_by_label(label).fill(new_name)
    form.get_by_role("button", name="Cancel" if cancel else "Rename").click()
    expect(form).to_have_count(0)


@when(parsers.re(r'I rename the (?:topic|subject) "(?P<name>[^"]+)" to "(?P<new_name>[^"]+)"$'))
def rename_in_browser(page, name, new_name):
    _rename(page, name, new_name)


@when(parsers.re(r'I start renaming the topic "(?P<name>[^"]+)" to "(?P<new_name>[^"]+)", but cancel$'))
def rename_cancelled(page, name, new_name):
    _rename(page, name, new_name, cancel=True)


def change_title_in_browser(page, title: str, new_title: str) -> None:
    _rename(page, title, new_title, label="Title")


@then("I am not offered to change the course's title")
def not_offered_to_change_title(page):
    title = page.get_by_role("main").get_by_role("heading", level=2).first
    expect(title).to_be_visible()
    expect(page.get_by_role("button", name=f"Rename {title.inner_text()}", exact=True)).to_have_count(0)


@then("I am not offered to rename the topic")
def not_offered_to_rename_topic(page):
    expect(page.get_by_role("main").get_by_role("heading", level=2).first).to_be_visible()
    expect(page.get_by_role("button", name=re.compile("^Rename "))).to_have_count(0)


@then("I am not offered to rename subjects or topics")
def not_offered_to_rename(page):
    expect(page.get_by_role("main").get_by_role("heading", level=4).first).to_be_visible()
    expect(page.get_by_role("button", name=re.compile("^Rename "))).to_have_count(0)


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


# writing material


@when(parsers.parse('I write material in the topic "{topic}"'))
def write_material_in_topic(page, students, topic):
    _open_topic_named(page, students, topic)
    page.get_by_role("link", name=f"Write material in {topic}").click()
    expect(page.get_by_role("form", name="Write material")).to_be_visible()


@when(parsers.parse('I name it "{name}"'))
def name_it(page, name):
    page.get_by_role("form", name="Write material").get_by_label("Name").fill(name)


@when("I type:")
def type_text(page, context, docstring):
    page.get_by_role("form", name="Write material").get_by_label("Text").fill(docstring)
    context["typed"] = docstring


@when("I save it")
def save_it(page):
    page.get_by_role("form", name="Write material").get_by_role("button", name="Save").click()


@when("I preview it")
def preview_it(page):
    page.get_by_role("tab", name="Preview").click()


@when("I go back to writing")
def back_to_writing(page):
    page.get_by_role("tab", name="Write").click()


@then("the text I typed is still there")
def typed_text_still_there(page, context):
    expect(page.get_by_role("form", name="Write material").get_by_label("Text")).to_have_value(context["typed"])


@when("I cancel, but choose to keep writing")
def cancel_but_keep_writing(page):
    form = page.get_by_role("form", name="Write material")
    form.get_by_role("button", name="Cancel").click()
    page.get_by_role("alertdialog", name="Leave without saving").get_by_role("button", name="Keep writing").click()
    expect(page.get_by_role("alertdialog")).to_have_count(0)


@then("I am not offered to write material")
def not_offered_to_write(page):
    expect(page.get_by_role("main").get_by_role("heading", name="Materials", level=3)).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("^Write material"))).to_have_count(0)


# images


def _png_file(name: str) -> dict:
    from tests.images import make_png

    return {"name": name, "mimeType": "image/png", "buffer": make_png()}


@given(parsers.parse('I have the file "{filename}" with the content:'))
def have_file(context, filename, docstring):
    context.setdefault("files", {})[filename] = docstring


@when(parsers.parse('I add "{filename}" and the image "{image}" to the topic "{topic}"'))
def add_markdown_with_image(page, students, context, filename, image, topic):
    _open_topic_named(page, students, topic)
    page.get_by_role("link", name=f"Add material to {topic}").click()
    form = page.get_by_role("form", name=re.compile("^Upload to "))
    content = context["files"][filename].encode()
    form.get_by_label("File").set_input_files({"name": filename, "mimeType": "text/markdown", "buffer": content})
    form.get_by_label("Images").set_input_files(_png_file(image))
    form.get_by_role("button", name="Upload").click()
    expect(page.get_by_role("heading", name=re.compile("^Add material"), level=2)).to_have_count(0)


@then(parsers.parse('I see the image "{alt}"'))
def see_image(page, alt):
    image = page.get_by_role("main").get_by_role("img", name=alt, exact=True)
    expect(image).to_be_visible()
    # shown, not just in the page: the browser has its pixels
    page.wait_for_function("image => image.complete && image.naturalWidth > 0", arg=image.element_handle())


@when(parsers.parse('I add the image "{name}" with the caption "{caption}"'))
def add_image_while_writing(page, name, caption):
    page.get_by_role("button", name="Add image").click()
    group = page.get_by_role("group", name="Add an image")
    group.get_by_label("Image").set_input_files(_png_file(name))
    group.get_by_label("Caption").fill(caption)
    group.get_by_role("button", name="Insert").click()


@then(parsers.parse('I see that the image "{path}" is missing'))
def see_missing_image(page, path):
    expect(page.get_by_role("group", name=f"Missing image {path}")).to_be_visible()


@when(parsers.parse('I add the missing image "{path}" from "{name}"'))
def add_missing_image(page, path, name):
    missing = page.get_by_role("group", name=f"Missing image {path}")
    expect(missing.get_by_role("button", name="Add the missing image")).to_be_visible()
    # the button opens the file picker; the file is given to its input
    missing.get_by_label(f"Image for {path}").set_input_files(_png_file(name))


@then("I am not offered to add it")
def not_offered_to_add_image(page):
    expect(page.get_by_role("button", name="Add the missing image")).to_have_count(0)


@when("I start editing it")
def start_editing(page):
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(page.get_by_role("form", name="Edit material").get_by_label("Text")).to_be_visible()


@when("I save my changes")
def save_my_changes(page):
    page.get_by_role("form", name="Edit material").get_by_role("button", name="Save").click()
    # once processed and its images added, the reader shows the material again
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible(timeout=120_000)


@then("I am not offered to add an image")
def not_offered_an_image(page):
    expect(page.get_by_role("button", name="Add image")).to_have_count(0)


# references


@when(parsers.parse('I follow the reference "{label}"'))
def follow_reference(page, label):
    page.get_by_role("article", name="Section text").get_by_role("link", name=label, exact=True).click()


@then(parsers.re(r'I am reading "(?P<filename>[^"]+)" at the section "(?P<title>[^"]+)"'))
def reading_at_section(page, filename, title):
    expect(page.get_by_role("heading", name=filename, level=2)).to_be_visible()
    section = page.get_by_role("navigation", name="Sections").get_by_role("button", name=title, exact=True)
    expect(section).to_have_attribute("aria-current", "true")


@then(parsers.re(r'I am reading "(?P<filename>[^"]+)"$'))
def reading(page, filename):
    expect(page.get_by_role("heading", name=filename, level=2)).to_be_visible()


@then(parsers.parse('I see the reference "{label}" as broken'))
def see_broken_reference(page, label):
    text = page.get_by_role("article", name="Section text")
    expect(text.locator(".reference-broken", has_text=label)).to_be_visible()
    expect(text.get_by_role("link", name=label, exact=True)).to_have_count(0)


@when(
    parsers.re(
        r'I add a reference to the section "(?P<section>[^"]+)" of "(?P<material>[^"]+)" '
        r'in "(?P<subject>[^"]+)" › "(?P<topic>[^"]+)"'
    )
)
def add_reference(page, section, material, subject, topic):
    page.get_by_role("button", name="Add reference").click()
    group = page.get_by_role("group", name="Add a reference")
    group.get_by_label("Topic").select_option(label=f"{subject} › {topic}")
    group.get_by_label("Material").select_option(label=material)
    group.get_by_label("Section").select_option(label=section)
    group.get_by_role("button", name="Insert").click()


@then(parsers.parse('the text I typed ends with "{text}"'))
def typed_text_ends_with(page, text):
    typed = page.get_by_role("form", name="Write material").get_by_label("Text")
    expect(typed).to_have_value(re.compile(f"{re.escape(text)}$"))


@then(parsers.parse('I see the reference "{label}" as a link'))
def see_reference_link(page, label):
    expect(page.get_by_role("article", name="Preview").get_by_role("link", name=label, exact=True)).to_be_visible()


@then(parsers.parse('I am told the reference "{written}" is broken'))
def told_reference_broken(page, written):
    expect(page.get_by_role("status").filter(has_text=written)).to_contain_text("broken")


@then(parsers.parse('the topic "{topic}" is mentioned in "{material}"'))
def topic_mentioned_in(page, topic, material):
    mentions = page.get_by_label(f"Mentions of {topic}")
    expect(mentions.get_by_role("link", name=material, exact=True)).to_be_visible()


@when(parsers.parse('I open the mention "{material}"'))
def open_mention(page, material):
    page.locator(".mentions").get_by_role("link", name=material, exact=True).first.click()


@when("I open the help on references")
def open_reference_help(page):
    page.get_by_role("button", name="How references work").click()


@then("I see how to refer to a topic, a material and a section")
def see_reference_help(page):
    help = page.get_by_role("region", name="How references work")
    for written in (
        "[[numerical-methods/finite-elements]]",
        "[[numerical-methods/finite-elements/fem-notes.md]]",
        "[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]",
    ):
        expect(help.get_by_text(written, exact=True)).to_be_visible()


@then(parsers.parse('I see that a label follows a "{bar}"'))
def see_label_help(page, bar):
    help = page.get_by_role("region", name="How references work")
    expect(help.get_by_text("[[numerical-methods/finite-elements|the FEM topic]]", exact=True)).to_be_visible()
    expect(help).to_contain_text(f'A label follows a "{bar}"')


# topics


@when(parsers.parse('I open the topic "{topic}"'))
def open_topic(page, students, topic):
    _open_topic_named(page, students, topic)


@then(parsers.parse('I am on the topic "{subject}" › "{topic}"'))
def on_topic(page, subject, topic):
    expect(page.get_by_role("heading", name=f"{subject} › {topic}", level=2)).to_be_visible()


@then(parsers.parse('I see its materials "{filenames}"'))
def see_its_materials(page, filenames):
    materials = page.get_by_role("list", name="Materials").locator(".filename")
    expect(materials).to_have_text([filename.strip() for filename in filenames.split(",")])


@when("I go back")
def go_back(page):
    page.get_by_role("button", name="← Back").click()


@when("I go back to the course")
def go_back_to_course(page):
    page.get_by_role("link", name=re.compile("^← Back to ")).click()
    expect(page.locator("#course-title")).to_be_visible()


@when("I go back to the subject")
def go_back_to_subject(page):
    page.get_by_role("link", name=re.compile("^← Back to ")).click()
    expect(page.locator("#subject-title")).to_be_visible()


@when(parsers.re(r'I open the subject "(?P<subject>[^"]+)"$'))
def open_subject(page, subject):
    open_subject_page(page, subject)


@then(parsers.re(r'I am on the subject "(?P<subject>[^"]+)"$'))
def on_subject(page, subject):
    expect(page.locator("#subject-title")).to_have_text(subject)


@then(parsers.re(r'I do not see "(?P<first>[^"]+)" or "(?P<second>[^"]+)" on the course page$'))
def not_on_course_page(page, first, second):
    expect(page.locator("#course-title")).to_be_visible()
    expect(page.get_by_role("list", name="Subjects")).to_be_visible()
    for name in (first, second):
        expect(page.get_by_role("main").get_by_text(name)).to_have_count(0)


@then(parsers.re(r'I do not see "(?P<first>[^"]+)" or "(?P<second>[^"]+)" on the subject\'s page$'))
def not_on_subject_page(page, first, second):
    expect(page.get_by_role("main").get_by_role("heading", level=4).first).to_be_visible()
    for filename in (first, second):
        expect(page.get_by_role("main").get_by_text(filename)).to_have_count(0)


def _subject_actions(page) -> list[list[str]]:
    """the buttons each subject on the course page offers"""
    subjects = page.get_by_role("list", name="Subjects").locator("section.subject")
    expect(subjects.first).to_be_visible()
    return [[b.inner_text() for b in subjects.nth(i).get_by_role("button").all()] for i in range(subjects.count())]


@then(parsers.re(r'each subject offers only "(?P<action>[^"]+)"$'))
def each_subject_offers_only(page, action):
    assert all(actions == [action] for actions in _subject_actions(page)), _subject_actions(page)


@then("each subject offers nothing")
def each_subject_offers_nothing(page):
    assert all(actions == [] for actions in _subject_actions(page)), _subject_actions(page)


@when(parsers.re(r'I rename the subject "(?P<name>[^"]+)" to "(?P<new_name>[^"]+)" on the course page$'))
def rename_subject_on_course_page(page, name, new_name):
    expect(page.locator("#course-title")).to_be_visible()
    _rename(page, name, new_name)


@then("I am not offered to rename the subject, or add topics to it")
def not_offered_to_change_subject(page):
    header = page.locator("header.page-header")
    expect(page.locator("#subject-title")).to_be_visible()
    expect(header.get_by_role("button")).to_have_count(0)


@then(parsers.parse('I see the topics "{topics}" under "{subject}"'))
def see_topics(page, topics, subject):
    open_subject_page(page, subject)
    listed = page.get_by_role("list", name=f"Topics of {subject}").get_by_role("heading", level=4)
    expect(listed).to_have_text([topic.strip() for topic in topics.split(",")])


@then(parsers.parse('each topic offers only "{up}", "{down}", "{rename}" and "{remove}"'))
def topic_actions(page, up, down, rename, remove):
    topics = page.get_by_role("main").locator("section.topic")
    expect(topics.first).to_be_visible()
    for i in range(topics.count()):
        topic = topics.nth(i)
        name = topic.get_by_role("heading", level=4).inner_text()
        # the topic's name is its one link, which opens its page
        expect(topic.get_by_role("link")).to_have_text([name])
        # each button is labelled with what it does to the topic, e.g. "Move Finite elements up"
        labels = [button.get_attribute("aria-label") or "" for button in topic.get_by_role("button").all()]
        assert [label.replace(f" {name}", "") for label in labels] == [up, down, rename, remove], labels


@then("the topics show the statuses:")
def topic_statuses(page, datatable):
    header, *rows = datatable
    assert header == ["topic", "status"]
    for topic, status in rows:
        expect(page.get_by_label(f"Status of {topic}", exact=True)).to_have_text(status)


def _delete_topic(page, context, topic: str):
    page.get_by_role("button", name=f"Delete {topic}", exact=True).click()
    dialog = page.get_by_role("alertdialog", name=f"Delete the topic {topic}")
    expect(dialog).to_be_visible()
    context["asked"] = dialog.inner_text()
    return dialog


@when(parsers.parse('I delete the topic "{topic}", and confirm it'))
def delete_topic_confirmed(page, context, topic):
    _delete_topic(page, context, topic).get_by_role("button", name=f"Yes, delete {topic}").click()
    expect(page.get_by_role("main").get_by_role("heading", name=topic, level=4)).to_have_count(0)


@when(parsers.parse('I delete the topic "{topic}", but cancel'))
def delete_topic_cancelled(page, context, topic):
    _delete_topic(page, context, topic).get_by_role("button", name="Cancel").click()


@then(parsers.parse("I am told before that its {count:d} materials are deleted with it"))
def told_materials_deleted(context, count):
    assert f"its {count} materials" in context["asked"], context["asked"]


@then("I am not offered to move or delete topics")
def not_offered_to_move_or_delete(page):
    expect(page.get_by_role("main").get_by_role("heading", level=4).first).to_be_visible()
    expect(page.get_by_role("main").get_by_role("button", name=re.compile(r"^(Move|Delete) "))).to_have_count(0)


@then("I am not offered to add, write, move or delete material")
def not_offered_to_change_topic(page):
    expect(page.get_by_role("list", name="Materials")).to_be_visible()
    main = page.get_by_role("main")
    expect(main.get_by_role("link", name=re.compile("^(Add|Write) material"))).to_have_count(0)
    expect(main.get_by_role("button", name=re.compile("^(Delete|Move) "))).to_have_count(0)


# the order of a topic's material, and reading on


@when(parsers.parse('I move the material "{filename}" {direction}'))
def move_material(page, context, filename, direction):
    page.get_by_role("button", name=f"Move {filename} {direction}").click()


@then("they are still in that order when I open the topic again")
def materials_still_in_order(page):
    materials = page.get_by_role("list", name="Materials").locator(".filename")
    expect(materials.first).to_be_visible()
    order = materials.all_inner_texts()
    page.reload()
    expect(page.get_by_role("list", name="Materials").locator(".filename")).to_have_text(order)


def _reading_order(page):
    return page.get_by_role("navigation", name="Reading order")


def _neighbour(page, which: str):
    # "← Previous: …" or "Next: … →"
    return _reading_order(page).get_by_role("link", name=re.compile(f"^(← )?{which.capitalize()}:"))


@when(parsers.re(r"I go to the (?P<which>next|previous) topic$"))
def go_to_neighbour(page, which):
    _neighbour(page, which).click()


@then(parsers.re(r'the (?P<which>next|previous) topic is shown as "(?P<name>[^"]+)"$'))
def neighbour_shown_as(page, which, name):
    expect(_neighbour(page, which)).to_have_text(f"Next: {name} →" if which == "next" else f"← Previous: {name}")


@then(parsers.re(r"I am not offered a (?P<which>next|previous) topic$"))
def no_neighbour_offered(page, which):
    expect(_reading_order(page)).to_be_visible()
    expect(_neighbour(page, which)).to_have_count(0)


# generating


@when("I choose to generate material")
def choose_to_generate(page):
    page.get_by_role("link", name=re.compile("^Generate material")).click()
    expect(page.get_by_role("form", name="Generate material")).to_be_visible()


def _materials_menu(page):
    """the menu of materials to generate from, opened"""
    button = page.get_by_role("button", name=re.compile("^Materials"))
    if button.get_attribute("aria-expanded") != "true":
        button.click()
    return page.get_by_role("list", name="Materials to generate from")


@then(parsers.parse('the materials menu offers "{filenames}"'))
def materials_menu_offers(page, filenames):
    expect(_materials_menu(page).locator(".filename")).to_have_text([f.strip() for f in filenames.split(",")])


@then(parsers.parse('the materials menu says "{summary}"'))
def materials_menu_says(page, summary):
    expect(page.get_by_role("button", name=re.compile("^Materials"))).to_have_text(f"{summary} ▾")


@when(parsers.re(r'I tick "(?P<first>[^"]+)"(?: and "(?P<second>[^"]+)")?$'))
def tick(page, first, second):
    for filename in (first, second):
        if filename:
            _materials_menu(page).get_by_role("checkbox", name=f"Tick {filename}").check()


@when(parsers.parse('I untick "{filename}"'))
def untick(page, filename):
    _materials_menu(page).get_by_role("checkbox", name=f"Tick {filename}").uncheck()


@then(parsers.parse('"{first}" and "{second}" are ticked'))
def ticked(page, first, second):
    for filename in (first, second):
        expect(_materials_menu(page).get_by_role("checkbox", name=f"Tick {filename}")).to_be_checked()


@when(parsers.re(r'I generate "(?P<kind>[^"]+)" from them(?:, with the instructions "(?P<instructions>[^"]*)")?$'))
def generate_in_browser(page, kind, instructions):
    page.keyboard.press("Escape")
    form = page.get_by_role("form", name="Generate material")
    form.get_by_label("Kind").select_option(label=kind)
    if instructions:
        form.get_by_role("textbox", name="Instructions").fill(instructions)
    form.get_by_role("button", name="Generate", exact=True).click()
    expect(page.get_by_role("form", name="Write material")).to_be_visible(timeout=120_000)


@then(parsers.parse('the editor has the name "{name}"'))
def editor_named(page, name):
    expect(page.get_by_role("form", name="Write material").get_by_label("Name")).to_have_value(name)


@when(parsers.parse('I choose to save it in "{subject}" › "{topic}"'))
def choose_topic_to_save_in(page, subject, topic):
    page.get_by_role("form", name="Write material").get_by_label("Save in").select_option(label=f"{subject} › {topic}")


@when("I cancel, and choose to discard it")
def cancel_and_discard(page):
    page.get_by_role("form", name="Write material").get_by_role("button", name="Cancel").click()
    page.get_by_role("alertdialog", name="Leave without saving").get_by_role("button", name="Discard").click()


@when("I cancel generating")
def cancel_generating(page):
    page.get_by_role("form", name="Generate material").get_by_role("button", name="Cancel").click()


@then("I cannot generate until I tick a material")
def generate_needs_a_tick(page):
    generate = page.get_by_role("form", name="Generate material").get_by_role("button", name="Generate", exact=True)
    expect(generate).to_be_disabled()
    _materials_menu(page).get_by_role("checkbox", name="Tick fem-notes.md").check()
    expect(generate).to_be_enabled()


@then(parsers.parse('I cannot tick "{filename}"'))
def cannot_tick(page, filename):
    expect(_materials_menu(page).get_by_role("checkbox", name=f"Tick {filename}")).to_be_disabled()


@then("I am not offered to generate material")
def not_offered_to_generate(page):
    expect(page.get_by_role("list", name="Materials")).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("^Generate material"))).to_have_count(0)


# the navigation bar


def _platform_status(page):
    return page.get_by_role("banner").locator(".brand").get_by_role("status")


@then("I see the platform's status next to the app's name")
def see_status_by_name(page):
    brand = page.get_by_role("banner").locator(".brand")
    expect(brand.get_by_role("heading", name="Qubit Notes")).to_be_visible()
    expect(brand.get_by_role("status")).to_be_visible()


@then(parsers.parse('I see "Signed in as {name}" beside the menu'))
def see_signed_in_beside_menu(page, students, name):
    session = page.get_by_role("navigation", name="Session")
    expect(session.get_by_text(f"Signed in as {students.id(name)}")).to_be_visible()
    expect(session.get_by_role("button", name="Menu")).to_be_visible()


@when("I open the menu")
def open_menu(page):
    page.get_by_role("button", name="Menu").click()


@then(parsers.parse('it offers "{items}"'))
def menu_offers(page, items):
    expect(page.get_by_role("menu", name="Menu").get_by_role("menuitem")).to_have_text(
        [item.strip() for item in items.split(",")]
    )


@when(parsers.parse('I choose "{item}" from the menu'))
def choose_menu_item(page, item):
    choose_from_menu(page, item)


@then("I see my courses")
def see_my_courses(page):
    expect(page.get_by_role("heading", name="My courses", level=2)).to_be_visible()


@then("I am asked who I am")
def asked_who_i_am(page):
    expect(page.get_by_label("Your name")).to_be_visible()


@then(parsers.parse('the platform\'s status says "{text}"'))
def platform_status_says(page, text):
    expect(_platform_status(page)).to_have_text(text)


@when("I open the platform's status")
def open_platform_status(page):
    page.get_by_role("banner").locator(".brand").get_by_role("button").click()


def _where_keys_are(page: Page):
    """where the app says what keys it is missing: the settings, if they are shown, else the platform's status"""
    if page.locator("#settings-title").count():
        return page.get_by_role("region", name="AI model")
    return page.get_by_role("dialog", name="The platform")


@then(parsers.parse('I am told the app is missing its "{provider}" key'))
def told_missing_key(page, provider):
    expect(_where_keys_are(page)).to_contain_text(f"The app is missing its {provider} key.")


@then(parsers.parse('I am not shown the setting "{setting}"'))
def not_shown_setting(page, setting):
    expect(_where_keys_are(page)).to_be_visible()
    expect(_where_keys_are(page)).not_to_contain_text(setting)


@when(parsers.parse('I give it the key "{key}"'))
def give_it_the_key(page, key):
    where = _where_keys_are(page)
    where.get_by_role("textbox", name=re.compile(" key$")).fill(key)
    where.get_by_role("form", name=re.compile(" key$")).get_by_role("button", name="Save").click()
    expect(where.get_by_role("form", name=re.compile(" key$"))).to_have_count(0)


@then("I am told to ask an admin to give it")
def told_to_ask_admin(page):
    expect(page.get_by_role("dialog", name="The platform")).to_contain_text("Ask an admin")


@then("I am not offered to give it a key")
def not_offered_key(page):
    dialog = page.get_by_role("dialog", name="The platform")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("button", name="Save")).to_have_count(0)


# settings


def _ai_model_section(page: Page):
    expect(page.locator("#settings-title")).to_be_visible()
    return page.get_by_role("region", name="AI model")


@then(parsers.re(r'I see the AI uses "(?P<model>[^"]+)" of "(?P<provider>[^"]+)"$'))
def see_ai_model(page, model, provider):
    expect(_ai_model_section(page)).to_contain_text(f"The AI uses {model} of {provider}.")


@when(parsers.re(r'I choose the provider "(?P<provider>[^"]+)" in the settings$'))
def choose_provider_in_settings(page, provider):
    _ai_model_section(page).get_by_label("Provider").select_option(label=provider)


@then(parsers.re(r'the model is filled in as "(?P<model>[^"]+)"$'))
def model_filled_in(page, model):
    expect(_ai_model_section(page).get_by_label("Model", exact=True)).to_have_value(model)


@when(parsers.re(r'I choose the model "(?P<model>[^"]+)" in the settings, and save it$'))
def choose_model_in_settings(page, model):
    form = _ai_model_section(page).get_by_role("form", name="Choose the AI model")
    form.get_by_label("Model", exact=True).fill(model)
    form.get_by_role("button", name="Save").click()


@then(parsers.re(r'I am told the AI uses "(?P<model>[^"]+)" of "(?P<provider>[^"]+)" from now on$'))
def told_ai_model_chosen(page, model, provider):
    expect(_ai_model_section(page).get_by_role("status")).to_have_text(
        f"The AI uses {model} of {provider} from now on."
    )


@then("I am not offered to change it")
def not_offered_to_change_model(page):
    section = _ai_model_section(page)
    expect(section).to_contain_text("Only the app's admins can change it.")
    expect(section.get_by_role("form")).to_have_count(0)
