"""Running a student's Go or Python program, in a sandbox of its own (domain/programs.py)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, programs
from qubit_notes.domain.programs import ProgramRun, Programs

router = APIRouter(tags=["programs"])
ProgramsDep = Annotated[dict[str, Programs], Depends(programs)]


class Program(BaseModel):
    source: str


@router.post("/go/run", response_model=ProgramRun)
async def run_go(program: Program, student: Student, languages: ProgramsDep) -> ProgramRun:
    return await run_in_threadpool(languages["go"].run, program.source)


@router.post("/python/run", response_model=ProgramRun)
async def run_python(program: Program, student: Student, languages: ProgramsDep) -> ProgramRun:
    return await run_in_threadpool(languages["python"].run, program.source)
