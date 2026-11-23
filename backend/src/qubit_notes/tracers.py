"""Where the AI's traces are sent (features/tracing.feature): Langfuse, where the app has its keys, or nowhere.

Langfuse's SDK sends what it is given in the background, in batches, so tracing adds no wait to a student's request,
and a Langfuse that can't be reached loses the traces, not the replies. Its scores and deletions are calls of its API,
made as they are asked for.
"""

from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from typing import Any

from loguru import logger

from qubit_notes.domain.tracing import Step, TraceInfo, Tracer
from qubit_notes.settings import Settings

# what Langfuse calls each kind of step
_OBSERVATION = {
    "generation": "generation",
    "speech": "generation",
    "transcription": "generation",
    "search": "retriever",
}
# and how it marks how it went
_LEVEL = {"ok": "DEFAULT", "unusable reply": "WARNING", "failed at the provider": "ERROR"}


class NoTracer:
    """traces nothing"""

    def trace(self, trace: TraceInfo):
        return nullcontext()

    def step(self, step: Step):
        return nullcontext()

    def score(self, trace_id: str, name: str, value: float) -> None:
        pass

    def unscore(self, trace_id: str, name: str) -> None:
        pass

    def delete(self, trace_ids: list[str]) -> None:
        pass

    def stop(self) -> None:
        pass


def _score_id(trace_id: str, name: str) -> str:
    """a trace has one score of each name"""
    return f"{trace_id}-{name}"


class LangfuseTracer:
    def __init__(self, settings: Settings):
        from langfuse import Langfuse

        self._client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            base_url=settings.langfuse_host,
            environment=settings.langfuse_environment,
        )

    @contextmanager
    def trace(self, trace: TraceInfo) -> Iterator[None]:
        from langfuse import propagate_attributes

        with self._client.start_as_current_observation(
            trace_context={"trace_id": trace.id}, name=trace.purpose, as_type="span"
        ):
            with propagate_attributes(user_id=trace.student, session_id=trace.session_id, trace_name=trace.purpose):
                yield

    @contextmanager
    def step(self, step: Step) -> Iterator[None]:
        with self._client.start_as_current_observation(
            name=step.name,
            as_type=_OBSERVATION[step.kind],
            input=step.input,
            version=step.prompt_version,
        ) as observation:
            try:
                yield
            finally:
                # filled in by now, also when what was traced failed
                observation.update(**_ended(step))

    def score(self, trace_id: str, name: str, value: float) -> None:
        self._client.create_score(
            score_id=_score_id(trace_id, name), trace_id=trace_id, name=name, value=value, data_type="BOOLEAN"
        )

    def unscore(self, trace_id: str, name: str) -> None:
        from langfuse.api.core.api_error import ApiError

        try:
            self._client.api.scores.delete(_score_id(trace_id, name))
        except ApiError as e:
            # there was no such score
            if e.status_code != 404:
                raise

    def delete(self, trace_ids: list[str]) -> None:
        self._client.api.trace.delete_multiple(trace_ids=trace_ids)

    def stop(self) -> None:
        self._client.shutdown()


def _ended(step: Step) -> dict[str, Any]:
    """what Langfuse is told of a step once it is done"""
    metadata: dict[str, Any] = {"outcome": step.outcome}
    if step.prompt:
        metadata |= {"prompt": step.prompt, "prompt_version": step.prompt_version}
    if step.passages:
        metadata["passages"] = [passage.model_dump() for passage in step.passages]
    ended: dict[str, Any] = {"output": step.output, "metadata": metadata, "level": _LEVEL[step.outcome]}
    if step.error:
        ended["status_message"] = step.error
    if step.kind != "search":
        ended |= {
            "model": step.model or None,
            "usage_details": {"input": step.input_tokens, "output": step.output_tokens},
        }
        metadata["provider"] = step.provider
    return ended


def tracer_from(settings: Settings) -> Tracer:
    """Langfuse, where the settings have its keys; else nothing"""
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return NoTracer()
    logger.info(f"the AI is traced to Langfuse at {settings.langfuse_host}")
    return LangfuseTracer(settings)
