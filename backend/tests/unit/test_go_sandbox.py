"""The real sandbox, in Docker, with the image of `make go-runner`; skipped where there's neither. These are what keep
a student's program from the machine, so they try what a hostile program would."""

import shutil
import subprocess
import time

import pytest

from qubit_notes.domain.errors import Unavailable
from qubit_notes.domain.go_programs import MAX_OUTPUT_BYTES, DockerGoRunner
from qubit_notes.settings import Settings

IMAGE = "qubit-notes-go-runner"


def _has_image() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True, check=False).returncode == 0


pytestmark = pytest.mark.skipif(not _has_image(), reason=f"needs Docker and the image {IMAGE}: make go-runner")


def _runner(**settings) -> DockerGoRunner:
    return DockerGoRunner(Settings(go_image=IMAGE, **settings))


def _main(body: str, imports: str = '"fmt"') -> str:
    return f"package main\n\nimport (\n{imports}\n)\n\nfunc main() {{\n{body}\n}}\n"


def _containers() -> list[str]:
    found = subprocess.run(
        ["docker", "ps", "--all", "--quiet", "--filter", "name=qubit-notes-go-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return found.stdout.split()


def test_a_program_runs_in_a_few_seconds_and_leaves_nothing():
    started = time.monotonic()
    run = _runner().run(_main('fmt.Println("hello")'))
    assert run.output == "hello\n"
    assert run.exit_code == 0
    assert time.monotonic() - started < 6
    assert _containers() == []


def test_the_compiler_says_what_is_wrong():
    run = _runner().run("package main\n\nfunc main() {\n\tundefinedThing()\n}\n")
    assert "undefined: undefinedThing" in run.output
    assert run.exit_code == 1


def test_a_program_exit_code_is_its_own():
    assert _runner().run(_main("os.Exit(3)", '"os"')).exit_code == 3


def test_goroutines_work():
    body = 'c := make(chan string)\ngo func() { c <- "from a goroutine" }()\nfmt.Println(<-c)'
    assert _runner().run(_main(body)).output == "from a goroutine\n"


def test_a_program_that_never_ends_is_stopped_and_removed():
    run = _runner(go_timeout_seconds=5).run(_main("for {\n}", ""))
    assert run.timed_out
    assert run.exit_code is None
    assert _containers() == []


def test_printing_forever_is_cut_off_and_stopped():
    started = time.monotonic()
    run = _runner().run(_main('for {\nfmt.Println("yes")\n}'))
    assert run.truncated
    assert len(run.output.encode()) <= MAX_OUTPUT_BYTES
    assert time.monotonic() - started < 15
    assert _containers() == []


def test_there_is_no_network():
    body = """conn, err := net.DialTimeout("tcp", "1.1.1.1:53", 2*time.Second)
fmt.Println(conn != nil, err != nil)"""
    assert _runner().run(_main(body, '"fmt"\n"net"\n"time"')).output == "false true\n"


def test_it_is_not_root_and_cannot_raise_itself():
    body = "fmt.Println(os.Getuid())\nfmt.Println(syscall.Setuid(0) != nil)"
    assert _runner().run(_main(body, '"fmt"\n"os"\n"syscall"')).output == "10001\ntrue\n"


def test_it_cannot_see_the_machine_or_the_app():
    body = """_, app := os.Stat("/home/alex")
_, socket := os.Stat("/var/run/docker.sock")
fmt.Println(os.IsNotExist(app), os.IsNotExist(socket), len(os.Environ()) < 15)
for _, v := range os.Environ() {
	if strings.HasPrefix(v, "QUBIT_NOTES") { fmt.Println("leaked") }
}"""
    assert _runner().run(_main(body, '"fmt"\n"os"\n"strings"')).output == "true true true\n"


def test_too_much_memory_kills_it():
    body = """var kept [][]byte
for {
	b := make([]byte, 64<<20)
	for i := range b { b[i] = 1 }
	kept = append(kept, b)
}"""
    run = _runner(go_memory="256m").run(_main(body, ""))
    assert run.exit_code == 137
    assert _containers() == []


def test_too_many_processes_are_refused():
    body = """for i := 0; i < 1000; i++ {
	cmd := exec.Command("sleep", "30")
	if err := cmd.Start(); err != nil {
		fmt.Println("refused")
		return
	}
}
fmt.Println("all started")"""
    assert _runner().run(_main(body, '"fmt"\n"os/exec"')).output == "refused\n"


def test_a_huge_file_is_refused():
    body = """f, _ := os.Create("/sandbox/big")
b := make([]byte, 1<<20)
for i := 0; i < 200; i++ {
	if _, err := f.Write(b); err != nil {
		fmt.Println("refused")
		return
	}
}
fmt.Println("all written")"""
    run = _runner().run(_main(body, '"fmt"\n"os"'))
    # the limit on file sizes ends it, as a signal, or an error if the signal is ignored
    assert "all written" not in run.output
    assert run.exit_code != 0 or "refused" in run.output


def test_a_missing_image_says_programs_cannot_be_run():
    with pytest.raises(Unavailable):
        DockerGoRunner(Settings(go_image="no-such-image-here")).run(_main(""))
