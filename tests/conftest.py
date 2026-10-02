"""Shared test policy and fixtures for loopctl (design D12, D13)."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest


def current_platform() -> str:
    """The only source of the platform that `only_on` is compared with."""
    return sys.platform


class PolicyPlugin:
    """Skip `only_on` cases on a foreign platform; fail the session on any
    other skip, xfail or xpass.

    A skip is allowed only when this plugin raised it; the skip reason text
    is never taken as evidence of a platform condition.
    """

    def __init__(self) -> None:
        self.platform_skips: set[str] = set()
        self.violations: list[str] = []

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item: pytest.Item) -> None:
        marker = item.get_closest_marker("only_on")
        if marker is None:
            return
        wanted, platform = marker.args[0], current_platform()
        if wanted != platform:
            self.platform_skips.add(item.nodeid)
            pytest.skip(f"only_on({wanted!r}); current platform is {platform!r}")

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.skipped:
            self.violations.append(f"{report.nodeid}: skipped at collection")

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if hasattr(report, "wasxfail"):
            outcome = "xpass" if report.passed else "xfail"
            self.violations.append(f"{report.nodeid}: {outcome}")
        elif report.skipped and not (
            report.when == "setup" and report.nodeid in self.platform_skips
        ):
            self.violations.append(f"{report.nodeid}: skip not from only_on")

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        expected = os.environ.get("LOOPCTL_EXPECT_PLATFORM")
        platform = current_platform()
        if expected and expected != platform:
            self.violations.append(
                f"platform mismatch: LOOPCTL_EXPECT_PLATFORM={expected}"
                f" but current platform is {platform}"
            )
        if self.violations and session.exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(
        self, terminalreporter: pytest.TerminalReporter
    ) -> None:
        if self.violations:
            terminalreporter.section("loopctl test policy: session failed")
            for violation in self.violations:
                terminalreporter.line(violation)


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(PolicyPlugin(), "loopctl-test-policy")


def dig(value: Any, *path: str | int) -> Any:
    """Read a nested field without raising; a missing step gives None."""
    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and isinstance(key, int):
            value = value[key] if -len(value) <= key < len(value) else None
        else:
            return None
    return value


def parse_envelope(stdout: str) -> dict[str, Any] | None:
    """The envelope when stdout is exactly one JSON object line, else None."""
    lines = stdout.splitlines()
    if len(lines) != 1:
        return None
    try:
        value = json.loads(lines[0])
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


@dataclass
class Result:
    """One loopctl invocation. An uncaught exception is kept in `exc` and
    leaves `code` as None, so a crash fails on the first assertion."""

    code: int | None
    out: dict[str, Any] | None
    stdout: str
    stderr: str
    exc: BaseException | str | None = None

    def get(self, *path: str | int) -> Any:
        return dig(self.out, *path)


def _exit_code(exc: SystemExit) -> int:
    if exc.code is None:
        return 0
    return exc.code if isinstance(exc.code, int) else 1


@pytest.fixture
def cli() -> Callable[..., Result]:
    """Run loopctl in-process through loopctl.cli.main(argv)."""

    def run(*argv: str) -> Result:
        stdout, stderr = io.StringIO(), io.StringIO()
        code: int | None = None
        exc: BaseException | None = None
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                from loopctl import cli as loopctl_cli

                code = loopctl_cli.main(list(argv))
            except SystemExit as error:
                code = _exit_code(error)
            except Exception as error:
                exc = error
        text = stdout.getvalue()
        return Result(code, parse_envelope(text), text, stderr.getvalue(), exc)

    return run


EXC_MARK = "@@loopctl-test-uncaught@@ "

# `python -m loopctl` is runpy.run_module(..., alter_sys=True); running it from
# -c lets the prelude go first and lets an uncaught exception be reported.
RUNNER = """\
import os, runpy, sys
try:
    runpy.run_module("loopctl", run_name="__main__", alter_sys=True)
except SystemExit:
    raise
except BaseException as error:
    sys.stdout.flush()
    sys.stderr.write("\\n" + MARK + repr(error) + "\\n")
    sys.stderr.flush()
    os._exit(70)
"""


def _proc_result(returncode: int, stdout: str, stderr: str) -> Result:
    code: int | None = returncode
    exc: str | None = None
    if EXC_MARK in stderr:
        code, exc = None, stderr.split(EXC_MARK, 1)[1].strip()
    return Result(code, parse_envelope(stdout), stdout, stderr, exc)


# Each process says it is ready, then waits for the `go` file of cli_proc_many.
BARRIER_WAIT = """\
import os as _os, time as _time
_open = open
_dir = {directory!r}
_open(_os.path.join(_dir, "ready-%d" % _os.getpid()), "w").close()
_deadline = _time.monotonic() + 60
while not _os.path.exists(_os.path.join(_dir, "go")):
    if _time.monotonic() > _deadline:
        _os._exit(97)
    _time.sleep(0.002)
"""


def _spawn(
    argv: tuple[str, ...], prelude: str, barrier: Path | None = None
) -> subprocess.Popen[str]:
    source = prelude + "\n"
    if barrier is not None:
        source += BARRIER_WAIT.format(directory=str(barrier))
    source += f"MARK = {EXC_MARK!r}\n" + RUNNER
    return subprocess.Popen(
        [sys.executable, "-c", source, *argv],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd(),
    )


@pytest.fixture
def cli_proc() -> Callable[..., Result]:
    """Run `python -m loopctl` in a subprocess after `prelude`."""

    def run(*argv: str, prelude: str = "") -> Result:
        proc = _spawn(argv, prelude)
        stdout, stderr = proc.communicate(timeout=60)
        return _proc_result(proc.returncode, stdout, stderr)

    return run


class Runs(list[Result]):
    """Results of cli_proc_many, with what the barrier saw at release."""

    barrier: dict[str, Any]


@pytest.fixture
def cli_proc_many(tmp_path: Path) -> Callable[..., Runs]:
    """Run n `python -m loopctl` subprocesses that start together: each runs
    its prelude, reports ready, and waits; the `go` file is created only once
    all n are ready (or one has already exited, or 60 s passed)."""
    counter = iter(range(1_000_000))

    def run(n: int, *argv: str, prelude: str = "") -> Runs:
        barrier = tmp_path / f"barrier-{next(counter)}"
        barrier.mkdir()
        procs = [_spawn(argv, prelude, barrier) for _ in range(n)]
        deadline = time.monotonic() + 60
        reason = "all_ready"
        while len(ready := list(barrier.glob("ready-*"))) < n:
            if any(proc.poll() is not None for proc in procs):
                reason = "process_exited"
                break
            if time.monotonic() > deadline:
                reason = "timeout"
                break
            time.sleep(0.002)
        go = barrier / "go"
        go.write_text(json.dumps({"ready": len(ready), "reason": reason}))
        runs = Runs()
        runs.barrier = {
            "ready_at_release": len(ready),
            "reason": reason,
            "ready_ns": [path.stat().st_mtime_ns for path in ready],
            "released_ns": go.stat().st_mtime_ns,
        }
        for proc in procs:
            stdout, stderr = proc.communicate(timeout=60)
            runs.append(_proc_result(proc.returncode, stdout, stderr))
        return runs

    return run


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point LOOPCTL_HOME at a fresh directory under tmp_path."""
    path = tmp_path / "home"
    path.mkdir()
    monkeypatch.setenv("LOOPCTL_HOME", str(path))
    return path


@pytest.fixture
def started_run(cli: Callable[..., Result]) -> Callable[[str, str, str], str]:
    """`init` and `claim` a run in-process as `actor`; returns the claim token."""

    def start(repo: str, feature: str, actor: str) -> str:
        run = ["--repo", repo, "--feature", feature]
        init = cli("init", *run, "--issue", "29", "--actor", actor)
        assert init.code == 0, init
        claim = cli("claim", *run, "--actor", actor)
        token = claim.get("result", "token")
        assert claim.code == 0 and isinstance(token, str), claim
        return token

    return start


REPO_FILES = {
    "tasks.md": "# Tasks\n\n- [ ] 1.1 calibrated plan for F-1\n",
    "tasks-draft.md": "# Tasks (draft)\n\n- [ ] 1.1 Project Lead draft for F-1\n",
    "specs/orchestration/spec.md": "## ADDED Requirements\n\n### ORC-01\n",
    "specs/durable/spec.md": "## ADDED Requirements\n\n### DUR-01\n",
    "ac.md": "# Acceptance criteria\n\n- AC-O01\n",
    "design.md": "# Design\n\n## D1\n",
    "sa.md": "# Solution architecture\n",
    "issue-29.md": "Feature 1: run-decisions\n\nExported issue body.\n",
    "workflow.yaml": (
        "schema_version: 1\n"
        "repo: yschiang/loop-engineering\n"
        "g3:\n"
        "  required_checks:\n"
        "    - {name: unit-linux, app: github-actions,"
        " workflow: .github/workflows/loopctl-ci.yml}\n"
    ),
}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A sample repo with the native documents a run registers (D13)."""
    root = tmp_path / "repo"
    for name, text in REPO_FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root
