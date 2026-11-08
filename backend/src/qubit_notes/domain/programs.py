"""Running a student's program, in Go or Python (features/go_programs.feature, features/python_programs.feature).

A program is anything anyone typed, so it never runs in the app. Each run is a container of its own, thrown away
afterwards, of its language's image (backend/go-runner, backend/python-runner): no network, an unprivileged user with
no capabilities, and limits on its memory, CPU, processes, file sizes and time. The program reaches ``docker run`` on
its standard input, never in its command line. Where the app has no Docker for a language
(QUBIT_NOTES_GO_RUNNER=off, QUBIT_NOTES_PYTHON_RUNNER=off, the defaults), its programs aren't run at all: the app must
never be given the Docker socket of a machine it shares with anything else.
"""

import subprocess
import threading
import uuid
from dataclasses import dataclass
from typing import Protocol

from loguru import logger
from pydantic import BaseModel

from qubit_notes.domain.errors import Busy, InvalidRequest, TooLarge, Unavailable
from qubit_notes.settings import Settings

MAX_SOURCE_BYTES = 64 * 1024
# what a program prints beyond this is dropped, and the program stopped
MAX_OUTPUT_BYTES = 64 * 1024
MAX_FILE_BYTES = 64 * 1024 * 1024
PROCESSES = 256
# docker's own exit code when it couldn't start the container, e.g. the image is missing or its daemon isn't running
DOCKER_FAILED = 125
# how long docker is given to stop a container
STOPPING_SECONDS = 10


@dataclass(frozen=True)
class Language:
    id: str
    name: str
    # what the container does with the program it's given on its standard input
    command: str


GO = Language("go", "Go", "cat > main.go && go build -o program main.go 2>&1 && exec ./program 2>&1")
PYTHON = Language("python", "Python", "cat > main.py && exec python3 main.py 2>&1")


def _not_here(language: Language) -> str:
    return f"{language.name} programs can't be run here."


class ProgramRun(BaseModel):
    # what the compiler, the interpreter or the program printed, as it printed it
    output: str
    # None if it was stopped before it ended
    exit_code: int | None
    timed_out: bool = False
    truncated: bool = False


class Runner(Protocol):
    def run(self, source: str) -> ProgramRun: ...


class DockerRunner:
    """Each program in a container of its own, of its language's image (see the top of this file)."""

    def __init__(self, settings: Settings, language: Language, image: str):
        self._language = language
        self._image = image
        self._timeout = settings.programs_timeout_seconds
        self._memory = settings.programs_memory
        self._cpus = settings.programs_cpus

    def _command(self, name: str) -> list[str]:
        return [
            "docker",
            "run",
            "--rm",
            "--interactive",
            "--name",
            name,
            "--pull",
            "never",
            "--network",
            "none",
            "--memory",
            self._memory,
            "--memory-swap",
            self._memory,
            "--cpus",
            str(self._cpus),
            "--pids-limit",
            str(PROCESSES),
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--ulimit",
            f"fsize={MAX_FILE_BYTES}",
            "--ulimit",
            "nofile=256",
            self._image,
            "sh",
            "-c",
            self._language.command,
        ]

    def run(self, source: str) -> ProgramRun:
        name = f"qubit-notes-{self._language.id}-{uuid.uuid4().hex}"
        try:
            process = subprocess.Popen(
                self._command(name), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        except OSError as e:
            logger.error(f"docker could not be run: {e}")
            raise Unavailable(_not_here(self._language)) from e

        output = bytearray()
        truncated = threading.Event()

        def read() -> None:
            # read to the end, even what is dropped: docker can't exit while its output isn't read
            while chunk := process.stdout.read1(8192):
                if truncated.is_set():
                    continue
                output.extend(chunk)
                if len(output) > MAX_OUTPUT_BYTES:
                    truncated.set()
                    threading.Thread(target=_remove, args=(name,), daemon=True).start()

        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        try:
            process.stdin.write(source.encode())
            process.stdin.close()
        except OSError:
            # the container is gone already; its output says why
            pass

        timed_out = False
        try:
            exit_code = process.wait(self._timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _remove(name)
            exit_code = _end(process)
        reader.join(STOPPING_SECONDS)

        if exit_code == DOCKER_FAILED:
            printed = bytes(output).decode(errors="replace")
            logger.error(f"docker could not run a {self._language.name} program: {printed}")
            raise Unavailable(_not_here(self._language))
        stopped = timed_out or truncated.is_set()
        return ProgramRun(
            output=bytes(output[:MAX_OUTPUT_BYTES]).decode(errors="replace"),
            exit_code=None if stopped else exit_code,
            timed_out=timed_out,
            truncated=truncated.is_set(),
        )


def _remove(name: str) -> None:
    """stops the container: stopping `docker run` itself would leave it running"""
    try:
        subprocess.run(["docker", "rm", "--force", name], capture_output=True, check=False, timeout=STOPPING_SECONDS)
    except subprocess.TimeoutExpired:
        logger.error(f"docker could not remove the container {name}")


def _end(process: subprocess.Popen) -> int:
    """`docker run` once its container is gone, which is stopped if it doesn't end: the request can't wait for ever"""
    try:
        return process.wait(STOPPING_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait()


class Programs:
    """Runs students' programs in one language. The languages share their slots, a few runs at a time, so that they
    can't take the machine's memory between them."""

    def __init__(self, language: Language, runner: Runner | None, slots: threading.BoundedSemaphore):
        self.language = language
        self.runner = runner
        self._slots = slots

    def run(self, source: str) -> ProgramRun:
        name = self.language.name
        if not source.strip():
            raise InvalidRequest(f"write a {name} program to run")
        if len(source.encode()) > MAX_SOURCE_BYTES:
            raise TooLarge(f"a {name} program can be at most {MAX_SOURCE_BYTES // 1024} KB")
        if self.runner is None:
            raise Unavailable(_not_here(self.language))
        if not self._slots.acquire(blocking=False):
            raise Busy("Other programs are running; try again in a moment.")
        try:
            return self.runner.run(source)
        finally:
            self._slots.release()


def programs(settings: Settings) -> dict[str, Programs]:
    """each language's programs, by its id"""
    slots = threading.BoundedSemaphore(settings.programs_concurrent_runs)
    images = {GO: (settings.go_runner, settings.go_image), PYTHON: (settings.python_runner, settings.python_image)}
    return {
        language.id: Programs(language, DockerRunner(settings, language, image) if runner == "docker" else None, slots)
        for language, (runner, image) in images.items()
    }
