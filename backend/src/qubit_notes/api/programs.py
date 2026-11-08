"""Running a student's program, in Go, Python, C++ or SQL, in a sandbox of its own (domain/programs.py)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, programs
from qubit_notes.domain.programs import LANGUAGES, Language, ProgramRun, Programs

router = APIRouter(tags=["programs"])
ProgramsDep = Annotated[dict[str, Programs], Depends(programs)]


class Program(BaseModel):
    source: str


def _route(language: Language) -> None:
    async def run(program: Program, student: Student, languages: ProgramsDep) -> ProgramRun:
        return await run_in_threadpool(languages[language.id].run, program.source)

    router.add_api_route(
        f"/{language.id}/run",
        run,
        methods=["POST"],
        response_model=ProgramRun,
        name=f"run_{language.id}",
        summary=f"Run a {language.name} program",
    )


# POST /go/run, /python/run, /cpp/run and /sql/run
for _language in LANGUAGES:
    _route(_language)
