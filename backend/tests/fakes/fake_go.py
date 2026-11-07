import re

from qubit_notes.domain.go_programs import GoRun


class FakeGoRunner:
    """A stand-in for the sandbox: a program prints what its fmt.Println calls are given; `undefined` doesn't compile;
    `for {` never ends. The real sandbox is tested in tests/unit/test_go_sandbox.py."""

    def __init__(self):
        self.programs: list[str] = []

    def run(self, source: str) -> GoRun:
        self.programs.append(source)
        if "undefined" in source:
            return GoRun(output="./main.go:4:2: undefined: undefined\n", exit_code=1)
        if "for {" in source:
            return GoRun(output="", exit_code=None, timed_out=True)
        printed = re.findall(r'fmt\.Println\("([^"]*)"\)', source)
        return GoRun(output="".join(f"{line}\n" for line in printed), exit_code=0)
