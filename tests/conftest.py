"""Shared test policy and fixtures for loopctl (design D12, D13)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

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


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point LOOPCTL_HOME at a fresh directory under tmp_path."""
    path = tmp_path / "home"
    path.mkdir()
    monkeypatch.setenv("LOOPCTL_HOME", str(path))
    return path


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
