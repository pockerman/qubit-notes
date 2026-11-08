"""Steps of go_programs.feature and of ui_go_editor.feature; the programs run in a stand-in for the sandbox."""

import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from tests.fakes.fake_go import FakeGoRunner


def _run(students, context, source: str, name=None) -> None:
    headers = students.headers(name) if name is not False else {}
    context["response"] = students.client.post("/api/go/run", json={"source": source}, headers=headers)


@given("the app can run Go programs")
def app_runs_programs(app):
    app.state.go_programs.runner = FakeGoRunner()


@given("as many programs are running as the app allows")
def all_slots_taken(app):
    while app.state.go_programs._slots.acquire(blocking=False):
        pass


@when("I run the Go program:")
def run_program(students, context, docstring):
    _run(students, context, docstring)


@when(parsers.parse("I run a Go program of {size:d} KB"))
def run_program_of_size(students, context, size):
    _run(students, context, "x" * size * 1024)


@when("someone who isn't signed in runs a Go program")
def run_signed_out(students, context):
    _run(students, context, "package main", name=False)


def _ran(context) -> dict:
    assert context["response"].status_code == 200, context["response"].text
    return context["response"].json()


def _refused(context, status: int, detail: str) -> None:
    assert context["response"].status_code == status, context["response"].text
    assert context["response"].json()["detail"] == detail


@then(parsers.parse('the program printed "{text}"'))
def program_printed(context, text):
    assert text in _ran(context)["output"]


@then(parsers.parse("it ended with the exit code {code:d}"))
def ended_with(context, code):
    assert _ran(context)["exit_code"] == code


@then("I am told the program ran out of time")
def out_of_time(context):
    assert _ran(context)["timed_out"]


@then("I am told to write a Go program to run")
def told_to_write(context):
    _refused(context, 422, "write a Go program to run")


@then("I am told a Go program can be at most 64 KB")
def told_too_large(context):
    _refused(context, 413, "a Go program can be at most 64 KB")


@then("I am told other Go programs are running")
def told_busy(context):
    _refused(context, 429, "Other Go programs are running; try again in a moment.")


@then("I am told Go programs can't be run here")
def told_unavailable(context):
    _refused(context, 503, "Go programs can't be run here.")


@then("they are refused")
def refused(context):
    assert context["response"].status_code == 401, context["response"].text


@then("no program was run")
def nothing_run(app):
    assert app.state.go_programs.runner.programs == []


# the editor


def _editor(page):
    return page.get_by_role("complementary", name="Go editor")


def _tools_menu(page):
    page.get_by_role("button", name="Tools").click()
    return page.get_by_role("menu", name="Tools")


@when("I open the Go editor")
def open_editor(page):
    choose_tool(page, "Go compiler")


@when(parsers.parse('I choose "{tool}" from the Tools menu'))
def choose_tool(page, tool):
    _tools_menu(page).get_by_role("menuitemcheckbox", name=tool).click()
    _editor(page).wait_for()


@then(parsers.parse('the Tools menu has "{tools}"'))
def tools_menu_has(page, tools):
    menu = _tools_menu(page)
    expect(menu.get_by_role("menuitemcheckbox")).to_have_text(tools.split(","))
    page.keyboard.press("Escape")
    expect(menu).to_have_count(0)


@when("I close the Go editor")
def close_editor(page):
    _editor(page).get_by_role("button", name="Close the Go editor").click()


@when("I write the Go program:")
def write_program(page, docstring):
    _editor(page).get_by_role("textbox", name="Go program").fill(docstring)


@when("I run it")
def run_it(page):
    _editor(page).get_by_role("button", name="Run", exact=True).click()


@when("I press Ctrl+Enter in the Go editor")
def run_by_keyboard(page):
    _editor(page).get_by_role("textbox", name="Go program").press("Control+Enter")


@when("I open the code block in the Go editor")
def open_block(page):
    page.get_by_role("button", name="Open in the Go editor").click()


@then("the Go editor has a program to start from")
def has_starter(page):
    expect(_editor(page).get_by_role("textbox", name="Go program")).to_have_value(re.compile("package main"))


@then(parsers.parse('the Go editor has "{text}"'))
def has_text(page, text):
    expect(_editor(page).get_by_role("textbox", name="Go program")).to_have_value(text)


@then(parsers.parse('I see the program printed "{text}"'))
def see_printed(page, text):
    expect(_editor(page).get_by_label("Output")).to_contain_text(text)


@then(parsers.parse("I am told it ended with exit code {code:d}"))
def see_exit_code(page, code):
    expect(_editor(page).get_by_role("status")).to_contain_text(f"exit code {code}")


@then("only the Go code block can be opened in the Go editor")
def only_go_block(page):
    expect(page.get_by_role("button", name="Open in the Go editor")).to_have_count(1)
    expect(page.locator("pre")).to_have_count(2)


@then("I see the Go editor but not the assistant")
def editor_not_assistant(page):
    expect(_editor(page)).to_be_visible()
    expect(page.get_by_role("complementary", name="Assistant")).to_have_count(0)


@when(parsers.parse('I edit the material, typing "{text}"'))
def edit_typing(page, text):
    page.get_by_role("button", name="Edit", exact=True).click()
    box = page.get_by_role("form", name="Edit material").get_by_label("Text")
    expect(box).not_to_have_value("")
    box.press("Control+Home")
    box.press_sequentially(text)


@then(parsers.parse('the text being edited still has "{text}"'))
def still_editing(page, text):
    expect(page.get_by_role("form", name="Edit material").get_by_label("Text")).to_have_value(re.compile(text))


def _subject_tools(page):
    return page.get_by_role("button", name=re.compile("^The tools of "))


def _tool(page, tool: str):
    # a subject's page shows its tools only when asked for
    shown = _subject_tools(page)
    shown.wait_for()
    if shown.get_attribute("aria-expanded") != "true":
        shown.click()
    return page.get_by_role("group", name="Tools").get_by_role("checkbox", name=tool)


@then("I don't see the subject's tools")
def subject_tools_hidden(page):
    expect(page.get_by_role("button", name=re.compile("^Add a topic to "))).to_be_visible()
    expect(page.get_by_role("group", name="Tools")).to_have_count(0)


@when("I choose to see the subject's tools")
def show_subject_tools(page):
    _subject_tools(page).click()


@then(parsers.parse('I can attach the tool "{tool}"'))
def can_attach_tool(page, tool):
    expect(page.get_by_role("group", name="Tools").get_by_role("checkbox", name=tool)).to_be_visible()


@then(parsers.parse('the tool "{tool}" is attached'))
def tool_attached(page, tool):
    expect(_tool(page, tool)).to_be_checked()


@when("I start a new subject")
def start_new_subject(page):
    page.get_by_role("button", name="New subject").click()


@then(parsers.parse('I can attach the tools "{tools}"'))
def can_attach(page, tools):
    group = page.get_by_role("form", name="New subject").get_by_role("group", name="Tools")
    expect(group.get_by_role("checkbox")).to_have_count(len(tools.split(",")))
    for tool in tools.split(","):
        expect(group.get_by_role("checkbox", name=tool)).not_to_be_checked()


@when(parsers.parse('I attach the tool "{tool}"'))
def attach_tool(page, tool):
    _tool(page, tool).check()


@when(parsers.parse('I detach the tool "{tool}"'))
def detach_tool(page, tool):
    _tool(page, tool).uncheck()


@then("I am offered the Go editor")
def offered(page):
    expect(page.get_by_role("button", name="Open in the Go editor")).to_be_visible()
    tools_menu_has(page, "Go compiler")


@then("I am not offered the Go editor")
def not_offered(page):
    actions = page.get_by_role("group", name="Material actions")
    expect(actions.get_by_role("button", name="AI", exact=True)).to_be_visible()
    expect(page.locator(".section-text pre, pre").first).to_be_visible()
    expect(page.get_by_role("button", name="Tools")).to_have_count(0)
    expect(page.get_by_role("button", name="Open in the Go editor")).to_have_count(0)
