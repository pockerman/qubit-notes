"""Steps of tracing.feature: every call to the AI traced, to a stand-in for Langfuse."""

from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import prompts, storage
from qubit_notes.domain.tracing import Step
from qubit_notes.tracers import NoTracer, tracer_from
from tests.bdd.steps.assistant_steps import _conversation
from tests.bdd.steps.study_steps import _document_scope
from tests.fakes.fake_tracer import FakeTracer, Traced


def _tracer(context) -> FakeTracer:
    return context["tracer"]


def _mine(context, students, purpose: str | None = None) -> list[Traced]:
    me = students.id(students.me)
    return [
        t for t in _tracer(context).traces if t.info.student == me and (purpose is None or t.info.purpose == purpose)
    ]


def _last(context, students, purpose: str) -> Traced:
    traces = _mine(context, students, purpose)
    assert traces, f"nothing traced as {purpose!r}: {_tracer(context).traces}"
    return traces[-1]


def _calls(trace: Traced) -> list[Step]:
    """the trace's calls to the AI, without its searches"""
    return [step for step in trace.steps if step.kind != "search"]


def _the_call(context) -> Step:
    calls = _calls(context["trace"])
    assert len(calls) == 1, calls
    return calls[0]


@given("qubit-notes traces the AI")
def traces_the_ai(app, context):
    context["tracer"] = FakeTracer()
    app.state.traces.tracer = context["tracer"]


@given("qubit-notes does not trace the AI")
def does_not_trace(app):
    # the app's own settings, without Langfuse's keys
    settings = app.state.settings.model_copy(update={"langfuse_public_key": None, "langfuse_secret_key": None})
    app.state.traces.tracer = tracer_from(settings)
    assert isinstance(app.state.traces.tracer, NoTracer)


@given("the AI first replies with something that is not valid")
def first_reply_invalid(app):
    app.state.platform.ai.invalid_replies = 1


@given("the AI's provider fails")
def provider_fails(app):
    app.state.platform.ai.fails = True


@given("Langfuse can't be reached")
def unreachable(context):
    _tracer(context).reachable = False


@when("Langfuse can be reached again")
def reachable_again(app, context):
    _tracer(context).reachable = True
    # what the app does when it starts, and with the next deletion
    app.state.traces.retry_deletions()


@when("I try to ask the AI for a summary")
def try_summary(students, context):
    scope = _document_scope(students, "fem-notes.md")
    context["response"] = students.client.post("/api/summaries", headers=students.headers(), json=scope)
    assert context["response"].status_code != 200, context["response"].text


@then("nothing has been traced")
def nothing_traced(context):
    assert _tracer(context).traces == []


@then(parsers.parse('{count:d} trace "{purpose}" has been traced for me'))
def traced_for_me(students, context, count, purpose):
    traces = _mine(context, students, purpose)
    assert len(traces) == count, traces
    assert len(_mine(context, students)) == count, _mine(context, students)
    context["trace"] = traces[-1]


@then(parsers.parse('its step used the prompt "{prompt}" at its version'))
def used_prompt(context, prompt):
    call = _the_call(context)
    assert (call.prompt, call.prompt_version) == (prompt, prompts.version(prompt))


@then(
    parsers.parse(
        'its step records the provider, the model, the input, the output, the latency and the outcome "{outcome}"'
    )
)
def step_records(context, outcome):
    call = _the_call(context)
    assert call.provider and call.model, call
    assert call.input["prompt"] and call.output, call
    assert call.ended_at is not None and call.ended_at >= call.started_at
    assert call.outcome == outcome and call.error is None


@then(parsers.parse("its step used {tokens_in:d} input tokens and {tokens_out:d} output tokens"))
def step_tokens(context, tokens_in, tokens_out):
    call = _the_call(context)
    assert (call.input_tokens, call.output_tokens) == (tokens_in, tokens_out)


@then(parsers.parse('its step records the outcome "{outcome}", with the provider\'s error'))
def step_failed(context, outcome):
    call = _the_call(context)
    assert call.outcome == outcome
    assert "overloaded" in call.error


@then(parsers.parse('the trace of the reply records the search for "{question}"'))
def records_search(students, context, question):
    searches = [step for step in _last(context, students, "assistant").steps if step.kind == "search"]
    assert [search.input for search in searches] == [question]
    context["search"] = searches[0]


@then(parsers.parse('the search found the passage "{reference}" of "{filename}", in the section "{title}"'))
def search_found(context, reference, filename, title):
    found = {(p.reference, p.filename, p.title) for p in context["search"].passages}
    assert (reference, filename, title) in found, context["search"].passages


@then(parsers.parse('both traces are of my conversation on "{filename}"'))
def of_conversation(students, context, filename):
    conversation = _conversation(students, filename)["id"]
    traces = _mine(context, students, "assistant")
    assert len(traces) == 2
    assert {t.info.session_id for t in traces} == {conversation}


@then(parsers.parse('it has {count:d} calls to the AI, the first with the outcome "{first}", the second "{second}"'))
def calls_with_outcomes(context, count, first, second):
    calls = _calls(context["trace"])
    assert [call.outcome for call in calls] == [first, second]
    assert calls[0].error


@then('the trace "audio" records the text read aloud, and no audio')
def audio_traced(students, context):
    speeches = [step for step in _last(context, students, "audio").steps if step.kind == "speech"]
    assert speeches
    for speech in speeches:
        assert speech.input["text"].strip()
        assert speech.output.endswith("bytes of audio")
        assert not any(isinstance(value, bytes) for value in (*speech.input.values(), speech.output))


@then(parsers.parse('the trace of the reply has the score "{name}" of {score:d}'))
def reply_scored(students, context, name, score):
    trace = _last(context, students, "assistant")
    assert _tracer(context).scores.get((trace.info.id, name)) == score


@then(parsers.parse('the trace of the reply has no score "{name}"'))
def reply_not_scored(students, context, name):
    trace = _last(context, students, "assistant")
    assert (trace.info.id, name) not in _tracer(context).scores


@then(parsers.parse('the trace of the writing assistant\'s reply has the score "{name}" of {score:d}'))
def writing_reply_scored(students, context, name, score):
    trace = _last(context, students, "writing")
    assert _tracer(context).scores.get((trace.info.id, name)) == score


@then("nothing traced for me is kept")
def nothing_kept(app, students, context):
    assert _mine(context, students) == []
    with app.state.database.connect() as connection:
        kept = connection.execute(
            select(storage.ai_traces).where(storage.ai_traces.c.student == students.id(students.me))
        ).all()
        pending = connection.execute(select(storage.ai_trace_deletions)).all()
    assert kept == [] and pending == []
