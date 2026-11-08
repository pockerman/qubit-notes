"""The real sandboxes, in Docker, with the images of `make go-runner`, python-runner, cpp-runner and sql-runner; each
language's tests
are skipped where there's no Docker or no image. These are what keep a student's program from the machine, so they try
what a hostile program would."""

import shutil
import subprocess
import time

import pytest

from qubit_notes.domain.errors import Unavailable
from qubit_notes.domain.programs import CPP, GO, MAX_OUTPUT_BYTES, PYTHON, SQL, DockerRunner, Language
from qubit_notes.settings import Settings

IMAGE = "qubit-notes-go-runner"
PYTHON_IMAGE = "qubit-notes-python-runner"
CPP_IMAGE = "qubit-notes-cpp-runner"
SQL_IMAGE = "qubit-notes-sql-runner"


def _has_image(image: str) -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "image", "inspect", image], capture_output=True, check=False).returncode == 0


go = pytest.mark.skipif(not _has_image(IMAGE), reason=f"needs Docker and the image {IMAGE}: make go-runner")
python = pytest.mark.skipif(
    not _has_image(PYTHON_IMAGE), reason=f"needs Docker and the image {PYTHON_IMAGE}: make python-runner"
)
cpp = pytest.mark.skipif(not _has_image(CPP_IMAGE), reason=f"needs Docker and the image {CPP_IMAGE}: make cpp-runner")
sql = pytest.mark.skipif(not _has_image(SQL_IMAGE), reason=f"needs Docker and the image {SQL_IMAGE}: make sql-runner")


def _runner(language: Language = GO, image: str = IMAGE, **settings) -> DockerRunner:
    return DockerRunner(Settings(**settings), language, image)


def _python(**settings) -> DockerRunner:
    return _runner(PYTHON, PYTHON_IMAGE, **settings)


def _cpp(**settings) -> DockerRunner:
    return _runner(CPP, CPP_IMAGE, **settings)


def _sql(**settings) -> DockerRunner:
    return _runner(SQL, SQL_IMAGE, **settings)


def _main(body: str, imports: str = '"fmt"') -> str:
    return f"package main\n\nimport (\n{imports}\n)\n\nfunc main() {{\n{body}\n}}\n"


def _containers() -> list[str]:
    found = subprocess.run(
        # the same filter twice is either, so the database's container isn't one
        [
            "docker",
            "ps",
            "--all",
            "--quiet",
            "--filter",
            "name=qubit-notes-go-",
            "--filter",
            "name=qubit-notes-python-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return found.stdout.split()


@go
def test_a_program_runs_in_a_few_seconds_and_leaves_nothing():
    started = time.monotonic()
    run = _runner().run(_main('fmt.Println("hello")'))
    assert run.output == "hello\n"
    assert run.exit_code == 0
    assert time.monotonic() - started < 6
    assert _containers() == []


@go
def test_the_compiler_says_what_is_wrong():
    run = _runner().run("package main\n\nfunc main() {\n\tundefinedThing()\n}\n")
    assert "undefined: undefinedThing" in run.output
    assert run.exit_code == 1


@go
def test_a_program_exit_code_is_its_own():
    assert _runner().run(_main("os.Exit(3)", '"os"')).exit_code == 3


@go
def test_goroutines_work():
    body = 'c := make(chan string)\ngo func() { c <- "from a goroutine" }()\nfmt.Println(<-c)'
    assert _runner().run(_main(body)).output == "from a goroutine\n"


@go
def test_a_program_that_never_ends_is_stopped_and_removed():
    run = _runner(programs_timeout_seconds=5).run(_main("for {\n}", ""))
    assert run.timed_out
    assert run.exit_code is None
    assert _containers() == []


@go
def test_printing_forever_is_cut_off_and_stopped():
    started = time.monotonic()
    run = _runner().run(_main('for {\nfmt.Println("yes")\n}'))
    assert run.truncated
    assert len(run.output.encode()) <= MAX_OUTPUT_BYTES
    assert time.monotonic() - started < 15
    assert _containers() == []


@go
def test_there_is_no_network():
    body = """conn, err := net.DialTimeout("tcp", "1.1.1.1:53", 2*time.Second)
fmt.Println(conn != nil, err != nil)"""
    assert _runner().run(_main(body, '"fmt"\n"net"\n"time"')).output == "false true\n"


@go
def test_it_is_not_root_and_cannot_raise_itself():
    body = "fmt.Println(os.Getuid())\nfmt.Println(syscall.Setuid(0) != nil)"
    assert _runner().run(_main(body, '"fmt"\n"os"\n"syscall"')).output == "10001\ntrue\n"


@go
def test_it_cannot_see_the_machine_or_the_app():
    body = """_, app := os.Stat("/home/alex")
_, socket := os.Stat("/var/run/docker.sock")
fmt.Println(os.IsNotExist(app), os.IsNotExist(socket), len(os.Environ()) < 15)
for _, v := range os.Environ() {
	if strings.HasPrefix(v, "QUBIT_NOTES") { fmt.Println("leaked") }
}"""
    assert _runner().run(_main(body, '"fmt"\n"os"\n"strings"')).output == "true true true\n"


@go
def test_too_much_memory_kills_it():
    body = """var kept [][]byte
for {
	b := make([]byte, 64<<20)
	for i := range b { b[i] = 1 }
	kept = append(kept, b)
}"""
    run = _runner(programs_memory="256m").run(_main(body, ""))
    assert run.exit_code == 137
    assert _containers() == []


@go
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


@go
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


@go
def test_a_missing_image_says_programs_cannot_be_run():
    with pytest.raises(Unavailable):
        _runner(image="no-such-image-here").run(_main(""))


# Python


@python
def test_a_python_program_runs_and_leaves_nothing():
    started = time.monotonic()
    run = _python().run('import sys\nprint("hello")\nprint("oops", file=sys.stderr)\nsys.exit(3)\n')
    assert run.output == "hello\noops\n"
    assert run.exit_code == 3
    assert time.monotonic() - started < 6
    assert _containers() == []


@python
def test_python_says_what_is_wrong():
    run = _python().run("print(undefined_thing)\n")
    assert "NameError" in run.output
    assert run.exit_code == 1


@python
def test_a_python_program_that_never_ends_is_stopped_and_removed():
    run = _python(programs_timeout_seconds=5).run("while True:\n    pass\n")
    assert run.timed_out
    assert run.exit_code is None
    assert _containers() == []


@python
def test_python_printing_forever_is_cut_off_and_stopped():
    run = _python().run('while True:\n    print("yes")\n')
    assert run.truncated
    assert len(run.output.encode()) <= MAX_OUTPUT_BYTES
    assert _containers() == []


@python
def test_python_has_no_network_and_is_not_root():
    source = """import os, socket
try:
    socket.create_connection(("1.1.1.1", 53), timeout=2)
    print("connected")
except OSError:
    print("no network")
print(os.getuid())
try:
    os.setuid(0)
    print("root")
except PermissionError:
    print("refused")
print(os.path.exists("/home/alex"), os.path.exists("/var/run/docker.sock"))
print([k for k in os.environ if k.startswith("QUBIT_NOTES")])
"""
    assert _python().run(source).output == "no network\n10001\nrefused\nFalse False\n[]\n"


@python
def test_too_much_memory_kills_a_python_program():
    run = _python(programs_memory="256m").run("kept = []\nwhile True:\n    kept.append(bytearray(64 << 20))\n")
    # the kernel kills it, or Python runs out of memory first
    assert run.exit_code == 137 or "MemoryError" in run.output
    assert _containers() == []


@python
def test_too_many_python_processes_are_refused():
    source = """import subprocess
try:
    for _ in range(1000):
        subprocess.Popen(["sleep", "30"])
    print("all started")
except OSError:
    print("refused")
"""
    assert _python().run(source).output == "refused\n"


@python
def test_a_huge_file_from_python_is_refused():
    source = """try:
    with open("/sandbox/big", "wb") as f:
        for _ in range(200):
            f.write(bytes(1 << 20))
    print("all written")
except OSError:
    print("refused")
"""
    run = _python().run(source)
    assert "all written" not in run.output


@python
def test_a_missing_python_image_says_programs_cannot_be_run():
    with pytest.raises(Unavailable, match="Python programs can't be run here"):
        _runner(PYTHON, "no-such-image-here").run("print(1)\n")


# C++


def _cpp_main(body: str, includes: str = "#include <iostream>") -> str:
    return f"{includes}\n\nint main() {{\n{body}\n}}\n"


@cpp
def test_a_cpp_program_compiles_runs_and_leaves_nothing():
    started = time.monotonic()
    run = _cpp().run(_cpp_main('std::cout << "hello" << std::endl;\nstd::cerr << "oops" << std::endl;\nreturn 3;'))
    assert run.output == "hello\noops\n"
    assert run.exit_code == 3
    assert time.monotonic() - started < 10
    assert _containers() == []


@cpp
def test_the_cpp_compiler_says_what_is_wrong():
    run = _cpp().run(_cpp_main("undefined_thing();"))
    assert "undefined_thing" in run.output
    assert "error" in run.output
    assert run.exit_code == 1


@cpp
def test_cpp20_and_threads_work():
    body = """std::vector<int> v{3, 1, 2};
std::ranges::sort(v);
std::thread t([&] { v.push_back(4); });
t.join();
for (int x : v) std::cout << x;
std::cout << std::endl;"""
    run = _cpp().run(_cpp_main(body, "#include <algorithm>\n#include <iostream>\n#include <thread>\n#include <vector>"))
    assert run.output == "1234\n"


@cpp
def test_a_cpp_program_that_never_ends_is_stopped_and_removed():
    run = _cpp(programs_timeout_seconds=5).run(_cpp_main("volatile bool on = true;\nwhile (on) {}"))
    assert run.timed_out
    assert run.exit_code is None
    assert _containers() == []


@cpp
def test_cpp_printing_forever_is_cut_off_and_stopped():
    run = _cpp().run(_cpp_main('while (true) std::cout << "yes" << std::endl;'))
    assert run.truncated
    assert len(run.output.encode()) <= MAX_OUTPUT_BYTES
    assert _containers() == []


@cpp
def test_cpp_has_no_network_and_is_not_root():
    body = """int s = socket(AF_INET, SOCK_STREAM, 0);
sockaddr_in a{};
a.sin_family = AF_INET;
a.sin_port = htons(53);
inet_pton(AF_INET, "1.1.1.1", &a.sin_addr);
std::cout << (connect(s, (sockaddr*)&a, sizeof a) != 0) << std::endl;
std::cout << getuid() << std::endl;
std::cout << (setuid(0) != 0) << std::endl;
std::cout << (access("/var/run/docker.sock", F_OK) != 0) << std::endl;
std::cout << (getenv("QUBIT_NOTES_SECRET_KEY") == nullptr) << std::endl;"""
    includes = (
        "#include <iostream>\n#include <cstdlib>\n#include <arpa/inet.h>\n#include <sys/socket.h>\n#include <unistd.h>"
    )
    assert _cpp().run(_cpp_main(body, includes)).output == "1\n10001\n1\n1\n1\n"


@cpp
def test_too_much_memory_kills_a_cpp_program():
    body = """std::vector<std::vector<char>> kept;
while (true) kept.emplace_back(64 << 20, 1);"""
    run = _cpp(programs_memory="256m").run(_cpp_main(body, "#include <vector>"))
    # the kernel kills it, or new throws std::bad_alloc, which aborts it
    assert run.exit_code in (134, 137)
    assert _containers() == []


@cpp
def test_too_many_cpp_processes_are_refused():
    body = """for (int i = 0; i < 1000; i++) {
    pid_t p = fork();
    if (p == 0) { sleep(30); _exit(0); }
    if (p < 0) { std::cout << "refused" << std::endl; return 0; }
}
std::cout << "all started" << std::endl;"""
    assert _cpp().run(_cpp_main(body, "#include <iostream>\n#include <unistd.h>")).output == "refused\n"


# SQL


@sql
def test_sql_runs_in_a_database_of_its_own_and_leaves_nothing():
    source = """CREATE TABLE people (name TEXT, age INTEGER);
INSERT INTO people VALUES ('Ada', 36), ('Alan', 41);
SELECT name FROM people WHERE age > 40;"""
    run = _sql().run(source)
    assert "Alan" in run.output
    assert "Ada" not in run.output
    assert run.exit_code == 0
    assert _containers() == []
    # each run's database is its own
    assert "no such table: people" in _sql().run("SELECT * FROM people;").output


@sql
def test_sql_stops_at_the_first_error():
    run = _sql().run("SELECT nope;\nSELECT 'after';")
    assert "no such column: nope" in run.output
    assert "after" not in run.output
    assert run.exit_code == 1


@sql
def test_sql_cannot_reach_files_or_a_shell():
    for source in (
        ".shell id",
        ".system id",
        "SELECT readfile('/etc/passwd');",
        "ATTACH '/sandbox/x.db' AS x;",
        ".output /sandbox/x",
        ".import /etc/passwd t",
        "SELECT writefile('/sandbox/x', 'x');",
        "SELECT load_extension('/lib/x');",
    ):
        run = _sql().run(source)
        assert run.exit_code != 0, source
        assert "root:" not in run.output, source


@sql
def test_sql_that_never_ends_is_stopped_and_removed():
    run = _sql(programs_timeout_seconds=5).run(
        "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT count(*) FROM c;"
    )
    assert run.timed_out
    assert run.exit_code is None
    assert _containers() == []


@sql
def test_sql_returning_rows_forever_is_stopped():
    run = _sql().run("WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT x FROM c;")
    # a table is laid out once all its rows are in, so it is stopped by its memory, before it prints them
    assert run.truncated or run.exit_code == 137
    assert len(run.output.encode()) <= MAX_OUTPUT_BYTES
    assert _containers() == []
