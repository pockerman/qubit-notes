import re

from qubit_notes.domain.programs import ProgramRun


class FakeGoRunner:
    """A stand-in for the sandbox: a program prints what its fmt.Println calls are given; `undefined` doesn't compile;
    `for {` never ends. The real sandbox is tested in tests/unit/test_sandboxes.py."""

    def __init__(self):
        self.programs: list[str] = []

    def run(self, source: str) -> ProgramRun:
        self.programs.append(source)
        if "undefined" in source:
            return ProgramRun(output="./main.go:4:2: undefined: undefined\n", exit_code=1)
        if "for {" in source:
            return ProgramRun(output="", exit_code=None, timed_out=True)
        printed = re.findall(r'fmt\.Println\("([^"]*)"\)', source)
        return ProgramRun(output="".join(f"{line}\n" for line in printed), exit_code=0)


class FakePythonRunner:
    """A stand-in for the Python sandbox: a program prints what its print calls are given; `undefined` is a NameError;
    `while True` never ends. The real sandbox is tested in tests/unit/test_sandboxes.py."""

    def __init__(self):
        self.programs: list[str] = []

    def run(self, source: str) -> ProgramRun:
        self.programs.append(source)
        if "undefined" in source:
            return ProgramRun(output="NameError: name 'undefined' is not defined\n", exit_code=1)
        if "while True" in source:
            return ProgramRun(output="", exit_code=None, timed_out=True)
        printed = re.findall(r'print\("([^"]*)"\)', source)
        return ProgramRun(output="".join(f"{line}\n" for line in printed), exit_code=0)


class FakeCppRunner:
    """A stand-in for the C++ sandbox: a program prints what it gives std::cout as "..."; `undefined` doesn't compile;
    `while (true)` never ends. The real sandbox is tested in tests/unit/test_sandboxes.py."""

    def __init__(self):
        self.programs: list[str] = []

    def run(self, source: str) -> ProgramRun:
        self.programs.append(source)
        if "undefined" in source:
            return ProgramRun(output="main.cpp:4:5: error: 'undefined' was not declared in this scope\n", exit_code=1)
        if "while (true)" in source:
            return ProgramRun(output="", exit_code=None, timed_out=True)
        printed = re.findall(r'std::cout << "([^"]*)"', source)
        return ProgramRun(output="".join(f"{line}\n" for line in printed), exit_code=0)


class FakeSqlRunner:
    """A stand-in for the SQL sandbox: SELECT 'text' prints the text; `nope` is a column there isn't; WITH RECURSIVE
    never ends. The real sandbox is tested in tests/unit/test_sandboxes.py."""

    def __init__(self):
        self.programs: list[str] = []

    def run(self, source: str) -> ProgramRun:
        self.programs.append(source)
        if "nope" in source:
            return ProgramRun(output="Parse error near line 1: no such column: nope\n", exit_code=1)
        if "WITH RECURSIVE" in source:
            return ProgramRun(output="", exit_code=None, timed_out=True)
        printed = re.findall(r"SELECT '([^']*)'", source)
        return ProgramRun(output="".join(f"{line}\n" for line in printed), exit_code=0)
