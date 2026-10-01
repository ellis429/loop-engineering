"""The unit-linux CI workflow and the workflow.yaml policy file (D12)."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CI_FILE = ".github/workflows/loopctl-ci.yml"
HEAD_SHA = "${{ github.event.pull_request.head.sha }}"
TESTED_SHA_ARTIFACT = "tested-sha-${{ github.job }}-${{ github.run_attempt }}"
PINNED = re.compile(r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$")

# The D12 step order of every required-check job.
STEP_ORDER = [
    "checkout",
    "verify-head",
    "write-tested-sha",
    "upload-tested-sha",
    "setup-uv",
    "sync",
    "pytest",
    "ruff",
    "mypy",
    "dist-smoke",
]


def load(relative: str) -> dict[Any, Any]:
    """Parse a YAML file of the repository; {} when it does not exist."""
    path = ROOT / relative
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def test_workflow_yaml_declares_unit_linux_as_the_required_check() -> None:
    policy = load("workflow.yaml")
    g3 = policy.get("g3") or {}
    assert g3.get("required_checks") == [
        {"name": "unit-linux", "app": "github-actions", "workflow": CI_FILE}
    ]
    assert policy == {
        "schema_version": 1,
        "repo": "yschiang/loop-engineering",
        "g3": {"required_checks": g3.get("required_checks")},
    }


def kind(step: dict[str, Any]) -> str:
    """Name what a workflow step does, so the order can be compared."""
    uses = str(step.get("uses", ""))
    run = str(step.get("run", "")).strip()
    with_ = step.get("with") or {}
    if uses.startswith("actions/checkout@") and with_.get("ref") == HEAD_SHA:
        return "checkout"
    if uses.startswith("actions/upload-artifact@"):
        if with_.get("name") == TESTED_SHA_ARTIFACT:
            return "upload-tested-sha"
    if uses.startswith("astral-sh/setup-uv@"):
        if with_.get("python-version") == "3.12" and with_.get("version"):
            return "setup-uv"
    if "git rev-parse HEAD" in run:
        return "verify-head"
    if "tested-sha.json" in run:
        return "write-tested-sha"
    commands = {
        "uv sync --frozen": "sync",
        "uv run pytest": "pytest",
        "uv run ruff check .": "ruff",
        "uv run mypy src": "mypy",
        "scripts/dist-smoke.sh": "dist-smoke",
    }
    return commands.get(run, f"other: {step.get('name') or uses or run}")


def test_required_check_is_a_pull_request_job_running_the_policy_command() -> None:
    workflow = load(CI_FILE)
    jobs = workflow.get("jobs") or {}
    checks = (load("workflow.yaml").get("g3") or {}).get("required_checks") or []
    names = [check.get("name") for check in checks]
    assert names == ["unit-linux"]
    for name in names:
        assert name in jobs, f"no job for required check {name}"
        assert jobs[name].get("name", name) == name

    # PyYAML reads the bare key `on` as the boolean True.
    trigger = workflow.get("on", workflow.get(True))
    assert trigger == {
        "pull_request": {
            "types": ["opened", "synchronize", "reopened"],
            "branches": ["main"],
        }
    }
    assert workflow.get("permissions") == {"contents": "read"}

    for name in names:
        job = jobs[name]
        assert job.get("runs-on") == "ubuntu-24.04"
        assert job.get("timeout-minutes") == 15
        steps = job.get("steps") or []
        assert [kind(step) for step in steps] == STEP_ORDER
        pytest_step = steps[STEP_ORDER.index("pytest")]
        assert pytest_step.get("run") == "uv run pytest"
        assert (pytest_step.get("env") or {}).get("LOOPCTL_EXPECT_PLATFORM") == (
            "linux"
        )
        unpinned = [
            step["uses"]
            for step in steps
            if "uses" in step and not PINNED.match(step["uses"])
        ]
        assert unpinned == []
        commit_msg = [step for step in steps if "commit-msg" in str(step)]
        assert commit_msg == []


def repository_files() -> list[str]:
    """Tracked and untracked files, without what .gitignore excludes."""
    listing = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return listing.stdout.splitlines()


def test_pytest_policy_has_one_source() -> None:
    files = repository_files()
    other_config = [
        path
        for path in files
        if PurePosixPath(path).name in ("pytest.ini", "tox.ini")
        or (
            PurePosixPath(path).name == "setup.cfg"
            and re.search(r"^\[(tool:)?pytest\]", (ROOT / path).read_text(), re.M)
        )
    ]
    assert other_config == [], "no other pytest configuration file"
    conftests = [
        path for path in files if PurePosixPath(path).name == "conftest.py"
    ]
    assert conftests == ["tests/conftest.py"]

    with (ROOT / "pyproject.toml").open("rb") as f:
        options = tomllib.load(f)["tool"]["pytest"]["ini_options"]
    assert "--strict-markers" in options.get("addopts", [])
    assert options.get("xfail_strict") is True
    markers = [marker.split("(")[0] for marker in options.get("markers", [])]
    assert "only_on" in markers
