from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from pydantic import BaseModel, Field

from qubit_notes.domain.tracing import Step, TraceInfo


class Traced(BaseModel):
    """a trace as the stand-in for Langfuse keeps it: what it is of, and its steps, in turn"""

    info: TraceInfo
    steps: list[Step] = Field(default_factory=list)


class FakeTracer:
    """A stand-in for Langfuse, which keeps the traces it is sent, and their scores; one that can't be reached
    fails whatever it is asked to do."""

    def __init__(self):
        self.traces: list[Traced] = []
        self.scores: dict[tuple[str, str], float] = {}
        self.reachable = True
        self._current: ContextVar[Traced | None] = ContextVar("fake_trace", default=None)

    def _reach(self) -> None:
        if not self.reachable:
            raise ConnectionError("Langfuse can't be reached")

    @contextmanager
    def trace(self, trace: TraceInfo) -> Iterator[None]:
        self._reach()
        traced = Traced(info=trace)
        self.traces.append(traced)
        token = self._current.set(traced)
        try:
            yield
        finally:
            self._current.reset(token)

    @contextmanager
    def step(self, step: Step) -> Iterator[None]:
        self._reach()
        try:
            yield
        finally:
            # as it is once done
            traced = self._current.get()
            if traced is not None:
                traced.steps.append(step.model_copy(deep=True))

    def score(self, trace_id: str, name: str, value: float) -> None:
        self._reach()
        self.scores[(trace_id, name)] = value

    def unscore(self, trace_id: str, name: str) -> None:
        self._reach()
        self.scores.pop((trace_id, name), None)

    def delete(self, trace_ids: list[str]) -> None:
        self._reach()
        deleted = set(trace_ids)
        self.traces = [t for t in self.traces if t.info.id not in deleted]
        self.scores = {key: value for key, value in self.scores.items() if key[0] not in deleted}

    def stop(self) -> None:
        pass
