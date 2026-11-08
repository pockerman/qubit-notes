"""Steps of go_programs.feature, python_programs.feature, cpp_programs.feature, sql_programs.feature and the editors in
the browser (ui_go_editor.feature, ui_python_editor.feature, ui_cpp_and_sql_editors.feature); the programs run in
stand-ins for the sandboxes."""

import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from tests.fakes.fake_programs import FakeCppRunner, FakeGoRunner, FakePythonRunner, FakeSqlRunner

FAKES = {"Go": FakeGoRunner, "Python": FakePythonRunner, "C++": FakeCppRunner, "SQL": FakeSqlRunner}
LANGUAGE = r"(?P<language>Go|Python|C\+\+|SQL)"
# each language's id, in its tool and its address
IDS = {"Go": "go", "Python": "python", "C++": "cpp", "SQL": "sql"}


def _programs(app, language: str):
    return app.state.programs[IDS[language]]


def _run(students, context, language: str, source: str, name=None) -> None:
    headers = students.headers(name) if name is not False else {}
    context["response"] = students.client.post(f"/api/{IDS[language]}/run", json={"source": source}, headers=headers)


@given(parsers.re(rf"the app can run {LANGUAGE} programs$"))
def app_runs_programs(app, language):
    _programs(app, language).runner = FAKES[language]()


@given("as many programs are running as the app allows")
def all_slots_taken(app):
    # the languages share their slots
    slots = _programs(app, "Go")._slots
    while slots.acquire(blocking=False):
        pass


@when(parsers.re(rf"I run the {LANGUAGE} program:$"))
def run_program(students, context, language, docstring):
    _run(students, context, language, docstring)


@when(parsers.re(rf"I run a {LANGUAGE} program of (?P<size>\d+) KB$"))
def run_program_of_size(students, context, language, size):
    _run(students, context, language, "x" * int(size) * 1024)


@when(parsers.re(rf"someone who isn't signed in runs a {LANGUAGE} program$"))
def run_signed_out(students, context, language):
    _run(students, context, language, "print(1)", name=False)


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


@then(parsers.re(rf"I am told to write a {LANGUAGE} program to run$"))
def told_to_write(context, language):
    _refused(context, 422, f"write a {language} program to run")


@then(parsers.re(rf"I am told a {LANGUAGE} program can be at most 64 KB$"))
def told_too_large(context, language):
    _refused(context, 413, f"a {language} program can be at most 64 KB")


@then("I am told other programs are running")
def told_busy(context):
    _refused(context, 429, "Other programs are running; try again in a moment.")


@then(parsers.re(rf"I am told {LANGUAGE} programs can't be run here$"))
def told_unavailable(context, language):
    _refused(context, 503, f"{language} programs can't be run here.")


@then("they are refused")
def refused(context):
    assert context["response"].status_code == 401, context["response"].text


@then("no program was run")
def nothing_run(app):
    for programs in app.state.programs.values():
        assert programs.runner is None or programs.runner.programs == []


# the editors

TOOLS = {"Go": "Go compiler", "Python": "Python interpreter", "C++": "C++ compiler", "SQL": "SQL interpreter"}
# what each editor starts with
STARTERS = {"Go": "package main", "Python": "print", "C++": "#include", "SQL": "SELECT"}
LANGUAGE_OF = {tool: language for language, tool in TOOLS.items()}


def _editor(page, language: str):
    return page.get_by_role("complementary", name=f"{language} editor")


def _open(context) -> str:
    """the language of the editor last opened"""
    return context.get("editor", "Go")


def _tools_menu(page):
    page.get_by_role("button", name="Tools").click()
    return page.get_by_role("menu", name="Tools")


@when(parsers.re(rf"I open the {LANGUAGE} editor$"))
def open_editor(page, context, language):
    choose_tool(page, context, TOOLS[language])


@when(parsers.parse('I choose "{tool}" from the Tools menu'))
def choose_tool(page, context, tool):
    _tools_menu(page).get_by_role("menuitemcheckbox", name=tool).click()
    context["editor"] = LANGUAGE_OF[tool]
    _editor(page, LANGUAGE_OF[tool]).wait_for()


@then(parsers.parse('the Tools menu has "{tools}"'))
def tools_menu_has(page, tools):
    menu = _tools_menu(page)
    expect(menu.get_by_role("menuitemcheckbox")).to_have_text(tools.split(","))
    page.keyboard.press("Escape")
    expect(menu).to_have_count(0)


@when(parsers.re(rf"I close the {LANGUAGE} editor$"))
def close_editor(page, language):
    _editor(page, language).get_by_role("button", name=f"Close the {language} editor").click()


@when(parsers.re(rf"I write the {LANGUAGE} program:$"))
def write_program(page, language, docstring):
    _editor(page, language).get_by_role("textbox", name=f"{language} program").fill(docstring)


@when("I run it")
def run_it(page, context):
    _editor(page, _open(context)).get_by_role("button", name="Run", exact=True).click()


@when(parsers.re(rf"I press Ctrl\+Enter in the {LANGUAGE} editor$"))
def run_by_keyboard(page, language):
    _editor(page, language).get_by_role("textbox", name=f"{language} program").press("Control+Enter")


@when(parsers.re(rf"I open the code block in the {LANGUAGE} editor$"))
def open_block(page, context, language):
    page.get_by_role("button", name=f"Open in the {language} editor").click()
    context["editor"] = language


@then(parsers.re(rf"the {LANGUAGE} editor has a program to start from$"))
def has_starter(page, language):
    textbox = _editor(page, language).get_by_role("textbox", name=f"{language} program")
    expect(textbox).to_have_value(re.compile(STARTERS[language]))


@then(parsers.re(rf'the {LANGUAGE} editor has "(?P<text>.*)"$'))
def has_text(page, language, text):
    # \n in the text is a new line
    expected = text.replace("\\n", "\n")
    expect(_editor(page, language).get_by_role("textbox", name=f"{language} program")).to_have_value(expected)


@when(parsers.re(rf"I press Tab at the end of the {LANGUAGE} program$"))
def press_tab(page, language):
    textbox = _editor(page, language).get_by_role("textbox", name=f"{language} program")
    textbox.press("End")
    textbox.press("Control+End")
    textbox.press("Tab")


@then(parsers.parse('I see the program printed "{text}"'))
def see_printed(page, context, text):
    expect(_editor(page, _open(context)).get_by_label("Output")).to_contain_text(text)


@then(parsers.parse("I am told it ended with exit code {code:d}"))
def see_exit_code(page, context, code):
    expect(_editor(page, _open(context)).get_by_role("status")).to_contain_text(f"exit code {code}")


@then(parsers.re(rf"only the {LANGUAGE} code block can be opened in the (?P=language) editor$"))
def only_block(page, language):
    expect(page.get_by_role("button", name=re.compile(r"^Open in the .+ editor$"))).to_have_count(1)
    expect(page.get_by_role("button", name=f"Open in the {language} editor")).to_have_count(1)


@then(parsers.re(rf"I see the {LANGUAGE} editor but not the assistant$"))
def editor_not_assistant(page, language):
    expect(_editor(page, language)).to_be_visible()
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


@then(parsers.re(rf"I am offered the {LANGUAGE} editor$"))
def offered(page, language):
    expect(page.get_by_role("button", name=f"Open in the {language} editor")).to_be_visible()
    menu = _tools_menu(page)
    expect(menu.get_by_role("menuitemcheckbox", name=TOOLS[language])).to_be_visible()
    page.keyboard.press("Escape")


@then(parsers.re(rf"I am not offered the {LANGUAGE} editor$"))
def not_offered(page, language):
    actions = page.get_by_role("group", name="Material actions")
    expect(actions.get_by_role("button", name="AI", exact=True)).to_be_visible()
    expect(page.locator(".section-text pre, pre").first).to_be_visible()
    expect(page.get_by_role("button", name=f"Open in the {language} editor")).to_have_count(0)
    tools = page.get_by_role("button", name="Tools")
    if tools.count():
        menu = _tools_menu(page)
        expect(menu.get_by_role("menuitemcheckbox", name=TOOLS[language])).to_have_count(0)
        page.keyboard.press("Escape")
