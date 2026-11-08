"""Running a student's Go program, in a sandbox of its own (domain/go_programs.py)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, go_programs
from qubit_notes.domain.go_programs import GoPrograms, GoRun

router = APIRouter(tags=["go programs"])
GoProgramsDep = Annotated[GoPrograms, Depends(go_programs)]


class Program(BaseModel):
    source: str


@router.post("/go/run", response_model=GoRun)
async def run(program: Program, student: Student, service: GoProgramsDep) -> GoRun:
    return await run_in_threadpool(service.run, program.source)
