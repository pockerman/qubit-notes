"""Running a student's Go program (features/go_programs.feature).

A program is anything anyone typed, so it never runs in the app. Each run is a container of its own, thrown away
afterwards, of the image in backend/go-runner: no network, an unprivileged user with no capabilities, and limits on its
memory, CPU, processes, file sizes and time. The program reaches ``docker run`` on its standard input, never in its
command line. Where the app has no Docker (QUBIT_NOTES_GO_RUNNER=off, the default), programs aren't run at all: the app
must never be given the Docker socket of a machine it shares with anything else.
"""

import subprocess
import threading
import uuid
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

BUILD_AND_RUN = "cat > main.go && go build -o program main.go && exec ./program"
NOT_HERE = "Go programs can't be run here."


class GoRun(BaseModel):
    # what the compiler or the program printed, as it printed it
    output: str
    # None if it was stopped before it ended
    exit_code: int | None
    timed_out: bool = False
    truncated: bool = False


class GoRunner(Protocol):
    def run(self, source: str) -> GoRun: ...


class DockerGoRunner:
    """Each program in a container of its own (see the top of this file)."""

    def __init__(self, settings: Settings):
        self._image = settings.go_image
        self._timeout = settings.go_timeout_seconds
        self._memory = settings.go_memory
        self._cpus = settings.go_cpus

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
            BUILD_AND_RUN,
        ]

    def run(self, source: str) -> GoRun:
        name = f"qubit-notes-go-{uuid.uuid4().hex}"
        try:
            process = subprocess.Popen(
                self._command(name), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        except OSError as e:
            logger.error(f"docker could not be run: {e}")
            raise Unavailable(NOT_HERE) from e

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
            logger.error(f"docker could not run a Go program: {bytes(output).decode(errors='replace')}")
            raise Unavailable(NOT_HERE)
        stopped = timed_out or truncated.is_set()
        return GoRun(
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


class GoPrograms:
    """Runs students' programs, a few at a time, so that they can't take the machine's memory between them."""

    def __init__(self, runner: GoRunner | None, concurrent_runs: int):
        self.runner = runner
        self._slots = threading.BoundedSemaphore(concurrent_runs)

    def run(self, source: str) -> GoRun:
        if not source.strip():
            raise InvalidRequest("write a Go program to run")
        if len(source.encode()) > MAX_SOURCE_BYTES:
            raise TooLarge(f"a Go program can be at most {MAX_SOURCE_BYTES // 1024} KB")
        if self.runner is None:
            raise Unavailable(NOT_HERE)
        if not self._slots.acquire(blocking=False):
            raise Busy("Other Go programs are running; try again in a moment.")
        try:
            return self.runner.run(source)
        finally:
            self._slots.release()


def go_programs(settings: Settings) -> GoPrograms:
    runner = DockerGoRunner(settings) if settings.go_runner == "docker" else None
    return GoPrograms(runner, settings.go_concurrent_runs)
