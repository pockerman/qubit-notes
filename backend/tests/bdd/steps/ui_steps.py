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
    expect(page.get_by_role("navigation", name="Courses").get_by_text("No courses yet")).to_be_visible()


@when(parsers.parse('I upload "{filename}" to the course "{course}", subject "{subject}", topic "{topic}"'))
def upload_in_browser(page, filename, course, subject, topic):
    form = page.get_by_role("form", name="Add material")
    form.get_by_label("Course").fill(course)
    form.get_by_label("Subject").fill(subject)
    form.get_by_label("Topic").fill(topic)
    form.get_by_label("File").set_input_files(
        {"name": filename, "mimeType": "text/plain", "buffer": f"Notes on {topic}.".encode()}
    )
    form.get_by_role("button", name="Upload").click()
    # processing takes a while on a real platform
    expect(form.get_by_role("status")).to_have_text(f"{filename} is ready", timeout=120_000)


@then(parsers.parse('I see the course "{course}" in my courses'))
def see_course(page, course):
    expect(page.get_by_role("navigation", name="Courses").get_by_role("button", name=course)).to_be_visible()


@when(parsers.parse('I open the course "{course}"'))
def open_course(page, course):
    # the course may have been created after the page was loaded
    page.reload()
    page.get_by_role("navigation", name="Courses").get_by_role("button", name=re.compile(f"^{course}")).click()
    expect(page.get_by_role("heading", name=course, level=2)).to_be_visible()


@then(parsers.parse('I see "{filename}" under "{subject}" › "{topic}"'))
def see_under(page, filename, subject, topic):
    expect(_topic(page, subject, topic).get_by_text(filename)).to_be_visible()


@then(parsers.parse('I see that "{filename}" is ready'))
def see_ready(page, filename):
    expect(page.get_by_role("listitem").filter(has_text=filename)).to_contain_text("ready")


@then(parsers.parse('I see the subjects "{subjects}"'))
def see_subjects(page, subjects):
    expect(page.get_by_role("main").get_by_role("heading", level=3).filter(has_not_text="Members")).to_have_text(
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


@then(parsers.parse('I see that the course is shared with me by "{owner}" as {role}'))
def see_shared(page, students, owner, role):
    expect(page.get_by_text(f"Shared with you by {students.id(owner)} as {role}")).to_be_visible()


@then("I cannot upload, delete or share in this course")
def cannot_change(page):
    course = page.get_by_role("main")
    expect(course.get_by_role("button", name=re.compile("^Delete "))).to_have_count(0)
    expect(course.get_by_text(re.compile("^Upload to "))).to_have_count(0)
    expect(course.get_by_role("form", name="Share this course")).to_have_count(0)


# reading


@when(parsers.parse('I open "{filename}" to read it'))
def open_to_read(page, filename):
    page.get_by_role("button", name=filename, exact=True).click()
    expect(page.get_by_role("heading", name=filename, level=2)).to_be_visible()


@then(parsers.parse('I see its sections "{titles}"'))
def see_its_sections(page, titles):
    outline = page.get_by_role("navigation", name="Sections")
    expect(outline.get_by_role("button")).to_have_text([title.strip() for title in titles.split(",")])


@when(parsers.parse('I choose the section "{title}"'))
def choose_section(page, title):
    page.get_by_role("navigation", name="Sections").get_by_role("button", name=title, exact=True).click()


@then(parsers.parse('I see the text "{text}"'))
def see_text(page, text):
    expect(page.get_by_role("article", name="Section text")).to_contain_text(text)
