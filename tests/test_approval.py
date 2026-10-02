"""Native documents and the start-of-work approval: register, approve_plan,
the status of versions and approval, and dispatch (D7, D8, D9, D10, D11)."""

from __future__ import annotations

import datetime
import hashlib
import json
from collections.abc import Callable
from itertools import combinations
from pathlib import Path
from typing import Any

import pytest
from conftest import Result, dig

from loopctl import clock

Cli = Callable[..., Result]
StartedRun = Callable[[str, str, str], str]

REPO = "yschiang/loop-engineering"
RUN = ["--repo", REPO, "--feature", "F-1"]
ISSUE = "https://github.com/yschiang/loop-engineering/issues/29"
SOURCE = "#29 plan review"

# The version each document of the `repo` fixture is registered at.
VERSIONS = {
    "tasks.md": "plan-3",
    "tasks-draft.md": "draft-1",
    "specs/orchestration/spec.md": "spec-o-1",
    "specs/durable/spec.md": "spec-d-1",
    "ac.md": "ac-1",
    "design.md": "design-2",
    "sa.md": "2026-09-30",
    ISSUE: "issue-29@2026-09-30",
    "workflow.yaml": "policy-1",
}


def run_dir(home: Path) -> Path:
    return home / "runs" / REPO / "F-1"


def snapshot(root: Path) -> dict[str, bytes | None]:
    """Every path under `root` with its bytes (None for a directory)."""
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(root.rglob("*"))
    }


def read_state(home: Path) -> Any:
    """feature.json of the run, or None when it is missing or not JSON."""
    try:
        return json.loads((run_dir(home) / "feature.json").read_text())
    except (OSError, ValueError):
        return None


def files(root: Path) -> list[str]:
    """The paths under `root`, sorted."""
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def register_args(
    kind: str, token: str | None, locator: str, **options: str | None
) -> list[str]:
    """argv of `register <kind>` for `locator` at its VERSIONS entry;
    `options` add or override (None leaves one out)."""
    argv = ["register", kind, *RUN, "--locator", locator]
    if token is not None:
        argv += ["--token", token]
    given = {"version": VERSIONS.get(locator, "v1"), "source": SOURCE, **options}
    for name, value in given.items():
        if value is not None:
            argv += [f"--{name.replace('_', '-')}", value]
    return argv


def entry_in(state: Any, kind: str, locator: str, role: str | None = None) -> Any:
    """The registration of `locator` in a state file."""
    if kind == "plan":
        return dig(state, "plan")
    if kind == "policy":
        return dig(state, "versions", "policy")
    return dig(state, "versions", "bindings", role, locator)


AT = "2026-10-02T09:00:00+00:00"

# What test 1 registers: kind, locator, options, and the file the content is.
DOCUMENTS = [
    # A plan ignores --role: it is not a binding.
    (
        "plan",
        "tasks.md",
        {
            "producer": "implementer",
            "calibrated_from": "tasks-draft.md",
            "role": "spec",
        },
        "tasks.md",
    ),
    ("binding", "specs/orchestration/spec.md", {"role": "spec"}, None),
    ("binding", "specs/durable/spec.md", {"role": "spec"}, None),
    ("binding", "ac.md", {"role": "ac"}, None),
    ("binding", "design.md", {"role": "design"}, None),
    ("binding", ISSUE, {"role": "spec", "content_from": "issue-29.md"}, "issue-29.md"),
]


def test_native_documents_are_registered_in_place_and_read_back(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.setattr(clock, "now", lambda: AT)
    token = started_run(REPO, "F-1", "agent:implementer")
    listing = files(repo)

    registered = {}
    for kind, locator, options, content_file in DOCUMENTS:
        content = (repo / (content_file or locator)).read_bytes()
        r = cli(*register_args(kind, token, locator, **options))
        assert r.code == 0, locator
        if kind == "plan":
            assert dig(read_state(home), "plan", "locator") == "tasks.md"
        entry = entry_in(read_state(home), kind, locator, options.get("role"))
        digest = sha256(content)
        expected = {
            "locator": locator,
            "version": VERSIONS[locator],
            "source": SOURCE,
            "digest": digest,
            "content": {"$object": digest},
            "registered_at": AT,
            "path": None if locator == ISSUE else str((repo / locator).resolve()),
        }
        if kind == "binding":
            expected["role"] = options["role"]
        else:
            expected["producer"] = "implementer"
            expected["calibrated_from"] = "tasks-draft.md"
        for name, value in expected.items():
            assert dig(entry, name) == value, (locator, name)
        if kind == "plan":
            assert "role" not in entry
        object_file = home / "objects" / digest.removeprefix("sha256:")
        assert object_file.read_bytes() == content, locator
        shown = {name: value for name, value in entry.items() if name != "content"}
        assert r.get("result") == {**shown, "unchanged": False}, locator
        registered[digest] = content

    # The originals change in place; what was registered reads back unchanged.
    for name in ("tasks.md", "specs/durable/spec.md", "issue-29.md"):
        (repo / name).write_text("changed after registration\n")
    for digest, content in registered.items():
        object_file = home / "objects" / digest.removeprefix("sha256:")
        assert object_file.read_bytes() == content
    # Registered in place: nothing renamed, moved or added in the repo.
    assert files(repo) == listing


# Locators with no content to adopt (D9): kind, locator, options.
UNREADABLE = {
    "missing-locator": ("binding", "nope.md", {"role": "spec"}),
    "directory-locator": ("binding", "specs", {"role": "spec"}),
    "url-without-content-from": ("binding", ISSUE, {"role": "spec"}),
    "missing-content-from": (
        "binding", ISSUE, {"role": "spec", "content_from": "nope.md"}
    ),
    # A policy is re-read from its own file (D11), so never from elsewhere.
    "policy-with-content-from": (
        "policy", "workflow.yaml", {"content_from": "issue-29.md"}
    ),
}

FIELDS = {
    "id": "d-x",
    "actor": "human:alice",
    "target": "tasks.md",
    "reason": "a",
    "source": "#29 comment by alice",
    "impact": "work on the plan may start",
}


def decide_args(kind: str, token: str | None, **fields: str | None) -> list[str]:
    """argv of `decide <kind>`: FIELDS, then `fields` (None leaves one out)."""
    argv = ["decide", kind, *RUN]
    if token is not None:
        argv += ["--token", token]
    for name, value in {**FIELDS, **fields}.items():
        if value is not None:
            argv += [f"--{name.replace('_', '-')}", value]
    return argv


@pytest.mark.parametrize(
    "case",
    [*UNREADABLE, "no-token", "wrong-token", "run-not-found", "blocked"],
)
def test_unreadable_documents_are_not_registered(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    monkeypatch.chdir(repo)
    token = started_run(REPO, "F-1", "agent:implementer")
    readable = register_args("binding", token, "ac.md", role="ac")

    if case in UNREADABLE:
        kind, locator, options = UNREADABLE[case]
        before = snapshot(run_dir(home))
        r = cli(*register_args(kind, token, locator, **options))
        assert r.code == 1
        assert r.get("result") == {"error": "locator_unreadable"}
        assert snapshot(run_dir(home)) == before
    elif case in ("no-token", "wrong-token"):
        given = None if case == "no-token" else "f" * 64
        before, objects = snapshot(home), sorted((home / "objects").glob("*"))
        r = cli(*register_args("binding", given, "ac.md", role="ac"))
        assert r.code == 4
        assert r.get("result") == {"error": "not_owner"}
        assert snapshot(home) == before
        assert sorted((home / "objects").glob("*")) == objects
    elif case == "run-not-found":
        before = snapshot(home)
        r = cli(*[("F-9" if arg == "F-1" else arg) for arg in readable])
        assert r.code == 1
        assert r.get("result") == {"error": "run_not_found"}
        assert snapshot(home) == before
    else:
        assert cli(*decide_args("revise", token, reason="a")).code == 0
        assert cli(*decide_args("revise", token, reason="b")).code == 3
        before = snapshot(run_dir(home))
        r = cli(*readable)
        assert r.code == 3
        assert r.get("result", "error") == "transition_conflict"
        assert snapshot(run_dir(home)) == before


@pytest.mark.parametrize(
    ("kind", "locator", "options", "missing"),
    [
        pytest.param("binding", "ac.md", {}, ["role"], id="binding-without-role"),
        pytest.param(
            "plan", "tasks.md", {"calibrated_from": "tasks-draft.md"}, ["producer"],
            id="plan-without-producer",
        ),
    ],
)
def test_a_binding_needs_its_role_and_a_plan_its_producer(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    locator: str,
    options: dict[str, str],
    missing: list[str],
) -> None:
    """D2, D9: the missing fields of a registration are refused before the
    state is read."""
    monkeypatch.chdir(repo)
    token = started_run(REPO, "F-1", "agent:implementer")
    before = snapshot(home)
    r = cli(*register_args(kind, token, locator, **options))
    assert r.get("result") == {"error": "missing_fields", "fields": missing}
    assert r.code == 1
    assert snapshot(home) == before


# The plan an Implementer calibrated, and the bindings approve_plan needs.
CALIBRATED = {"producer": "implementer", "calibrated_from": "tasks-draft.md"}
BINDINGS = {
    "spec": ["specs/orchestration/spec.md", "specs/durable/spec.md"],
    "ac": ["ac.md"],
    "design": ["design.md"],
}
ROLES = tuple(BINDINGS)


def registered(cli: Cli, token: str, kind: str, locator: str, **options: str) -> Result:
    """A registration that must succeed."""
    r = cli(*register_args(kind, token, locator, **options))
    assert r.code == 0, r
    return r


def ready_run(
    cli: Cli, started_run: StartedRun, roles: tuple[str, ...] = ROLES
) -> str:
    """A run claimed by agent:implementer, with the calibrated plan tasks.md
    and the bindings of `roles` registered; returns the token. The cwd must
    be the `repo` fixture."""
    token = started_run(REPO, "F-1", "agent:implementer")
    registered(cli, token, "plan", "tasks.md", **CALIBRATED)
    for role in roles:
        for locator in BINDINGS[role]:
            registered(cli, token, "binding", locator, role=role)
    return token


AWAITING_NEXT = {
    "action": "human",
    "blockers": ["plan_not_approved"],
    "decision_kinds": ["approve_plan"],
}


def test_status_shows_versions_and_awaiting_approval(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    ready_run(cli, started_run)
    plan_version = VERSIONS["tasks.md"]

    st = cli("status", *RUN)
    assert st.get("result", "phase") == "awaiting_approval"
    assert st.get("result", "approval") == {
        "status": "not_approved",
        "plan_version": plan_version,
    }
    plan = {
        "locator": "tasks.md",
        "version": plan_version,
        "digest": sha256((repo / "tasks.md").read_bytes()),
        "producer": "implementer",
        "calibrated_from": "tasks-draft.md",
    }
    for name, value in plan.items():
        assert st.get("result", "plan", name) == value, name
    for role, locators in BINDINGS.items():
        for locator in locators:
            version = st.get("result", "bindings", role, locator, "version")
            assert version == VERSIONS[locator], locator
    assert st.get("next") == AWAITING_NEXT
    assert st.code == 0

    lines = str(cli("status", *RUN, "--human").get("result", "human")).splitlines()
    expected = {
        "plan:": ["tasks.md", plan_version],
        "spec:": [
            "specs/orchestration/spec.md",
            VERSIONS["specs/orchestration/spec.md"],
            "specs/durable/spec.md",
            VERSIONS["specs/durable/spec.md"],
        ],
        "design:": ["design.md", VERSIONS["design.md"]],
        "approval:": ["not_approved", plan_version],
    }
    for label, words in expected.items():
        found = [line for line in lines if line.startswith(label)]
        assert found, f"no {label} line in {lines}"
        assert all(word in found[0] for word in words), (label, found[0])

    state = read_state(home)
    assert dig(state, "approval") is None
    assert dig(state, "phase") == "awaiting_approval"
    assert dig(state, "plan", "version") == plan_version
    assert dig(state, "next") == st.get("next")


class Clock:
    """A clock the test moves (D13)."""

    def __init__(self) -> None:
        self.at = datetime.datetime(2026, 10, 2, 9, tzinfo=datetime.UTC)

    def __call__(self) -> str:
        return self.at.isoformat(timespec="seconds")

    def advance(self, **delta: float) -> None:
        self.at += datetime.timedelta(**delta)


@pytest.fixture
def moving_clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    now = Clock()
    monkeypatch.setattr(clock, "now", now)
    return now


def approve_args(token: str, **fields: str) -> list[str]:
    """argv of a human approve_plan of tasks.md at its version; `fields`
    override."""
    given = {
        "id": "ap-1",
        "target": "tasks.md",
        "version": VERSIONS["tasks.md"],
        "reason": "the plan is ready",
    }
    return decide_args("approve_plan", token, **{**given, **fields})


def test_only_a_human_approve_plan_on_a_calibrated_plan_approves(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    moving_clock: Clock,
) -> None:
    monkeypatch.chdir(repo)
    # A direct init by the Implementer: no handoff record is needed.
    token = started_run(REPO, "F-1", "agent:implementer")
    assert not dig(read_state(home), "decisions")

    # (a') Before any plan is registered; its answer is checked below, with
    # the first refusal of approve_plan's own checks.
    no_plan = cli(*approve_args(token, id="ap-0"))

    for role, locators in BINDINGS.items():
        for locator in locators:
            registered(cli, token, "binding", locator, role=role)
    draft = {"target": "tasks-draft.md", "version": VERSIONS["tasks-draft.md"]}
    registered(
        cli, token, "plan", "tasks-draft.md",
        producer="project_lead", calibrated_from="tasks-draft.md",
    )

    # (a) No decision: thirty days pass and nothing is approved.
    moving_clock.advance(days=30)
    st = cli("status", *RUN)
    assert st.get("result", "approval") == {
        "status": "not_approved",
        "plan_version": VERSIONS["tasks-draft.md"],
    }
    assert st.get("result", "phase") == "awaiting_approval"

    # (b) O26: an SA confirmation is a binding with its version and source.
    sa_source = "Project Lead 確認，#29"
    registered(cli, token, "binding", "sa.md", role="sa", source=sa_source)
    st = cli("status", *RUN)
    for where, entry in {
        "status": st.get("result", "bindings", "sa", "sa.md"),
        "state file": dig(read_state(home), "versions", "bindings", "sa", "sa.md"),
    }.items():
        assert dig(entry, "version") == "2026-09-30", where
        assert dig(entry, "source") == sa_source, where
    assert st.get("result", "approval", "status") == "not_approved"
    assert st.get("result", "phase") == "awaiting_approval"

    # (c) An agent's approval is no approval.
    r = cli(*approve_args(token, id="ap-c", actor="agent:implementer", **draft))
    assert r.code == 1
    assert r.get("result", "error") == "actor_not_human"

    # (d) The Project Lead's plan cannot be approved.
    r = cli(*approve_args(token, id="ap-d", **draft))
    assert r.get("result", "error") == "plan_not_calibrated"
    assert r.code == 1
    # (a')
    assert no_plan.get("result", "error") == "plan_not_registered"
    assert no_plan.code == 1

    # (e) The Implementer's plan without its calibration source.
    registered(cli, token, "plan", "tasks.md", producer="implementer")
    r = cli(*approve_args(token, id="ap-e"))
    assert r.get("result", "error") == "plan_not_calibrated"
    assert r.code == 1

    # (g) The same file and version with --calibrated-from replaces it.
    r = registered(cli, token, "plan", "tasks.md", **CALIBRATED)
    assert r.get("result", "unchanged") is False
    assert dig(read_state(home), "plan", "calibrated_from") == "tasks-draft.md"

    # (f) Only the registered plan's locator and version.
    for name, fields in {
        "target": {"target": "tasks-draft.md"},
        "version": {"version": "plan-2"},
    }.items():
        r = cli(*approve_args(token, id=f"ap-f-{name}", **fields))
        assert r.get("result", "error") == "plan_version_mismatch", name
        assert r.code == 1, name

    # (g) A human approve_plan of the calibrated plan approves it.
    r = cli(*approve_args(token))
    assert r.code == 0
    state = read_state(home)
    assert dig(state, "phase") == "approved"
    assert dig(state, "approval") == {
        "decision": "ap-1",
        "actor": "human:alice",
        "at": moving_clock(),
        "plan": {
            "locator": "tasks.md",
            "version": VERSIONS["tasks.md"],
            "digest": sha256((repo / "tasks.md").read_bytes()),
        },
        # spec, ac and design; never sa.
        "bindings": {
            role: {
                locator: sha256((repo / locator).read_bytes()) for locator in locators
            }
            for role, locators in BINDINGS.items()
        },
    }
    # One current plan: the Project Lead's draft was replaced, not kept.
    assert dig(state, "plan", "locator") == "tasks.md"
    assert "tasks-draft.md" not in json.dumps(dig(state, "versions"))

    r = cli(*approve_args(token, id="ap-2"))
    assert r.code == 1
    assert r.get("result", "error") == "already_approved"


# Every incomplete subset of the roles approve_plan needs.
INCOMPLETE = [roles for n in range(len(ROLES)) for roles in combinations(ROLES, n)]


@pytest.mark.parametrize(
    "roles", INCOMPLETE, ids=lambda roles: "+".join(roles) or "none"
)
def test_approve_plan_needs_spec_ac_and_design_bindings(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    roles: tuple[str, ...],
) -> None:
    monkeypatch.chdir(repo)
    token = ready_run(cli, started_run, roles)
    missing = [role for role in ROLES if role not in roles]
    revision = cli("status", *RUN).get("revision")

    r = cli(*approve_args(token))
    assert r.code == 1
    assert r.get("result") == {"error": "missing_bindings", "roles": missing}
    st = cli("status", *RUN)
    assert st.get("revision") == revision
    assert st.get("next", "blockers") == [f"missing_binding:{role}" for role in missing]

    for role in missing:
        for locator in BINDINGS[role]:
            registered(cli, token, "binding", locator, role=role)
    # The same plan version is approved once all three are registered.
    r = cli(*approve_args(token))
    assert r.code == 0
    assert dig(read_state(home), "phase") == "approved"


@pytest.mark.parametrize(
    ("locator", "options", "roles", "blockers"),
    [
        pytest.param(
            "tasks-draft.md",
            {"producer": "project_lead", "calibrated_from": "tasks-draft.md"},
            ROLES,
            ["plan_not_calibrated"],
            id="project-lead-plan",
        ),
        pytest.param(
            "tasks.md",
            {"producer": "implementer"},
            ("spec", "design"),
            ["plan_not_calibrated", "missing_binding:ac"],
            id="no-calibration-and-no-ac",
        ),
    ],
)
def test_next_names_every_blocker_of_the_plan(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    locator: str,
    options: dict[str, str],
    roles: tuple[str, ...],
    blockers: list[str],
) -> None:
    """D7: a plan that is not calibrated is a blocker too, listed with the
    others and with no decision kind."""
    monkeypatch.chdir(repo)
    token = started_run(REPO, "F-1", "agent:implementer")
    for role in roles:
        for binding in BINDINGS[role]:
            registered(cli, token, "binding", binding, role=role)
    registered(cli, token, "plan", locator, **options)

    expected = {"action": "human", "blockers": blockers, "decision_kinds": []}
    for name in ("status", "next"):
        assert cli(name, *RUN).get("next") == expected, name
    assert dig(read_state(home), "next") == expected


def test_next_after_approval_reports_dispatch(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    token = ready_run(cli, started_run)
    assert cli(*approve_args(token)).code == 0

    nx = cli("next", *RUN)
    assert nx.get("next", "action") == "dispatch"
    dispatch = {
        "action": "dispatch",
        "plan": {
            "locator": "tasks.md",
            "version": VERSIONS["tasks.md"],
            "digest": sha256((repo / "tasks.md").read_bytes()),
        },
        "approval": "ap-1",
    }
    for name, out in {"next": nx, "status": cli("status", *RUN)}.items():
        assert out.get("next") == dispatch, name
        assert out.get("result", "blockers") == [], name
        assert out.code == 0, name
    state = read_state(home)
    assert dig(state, "next") == dispatch
    assert dig(state, "blockers") == []


SPEC = BINDINGS["spec"][0]
NEW_SPEC = "specs/scope/spec.md"

# What an approval covers, changed: kind, locator, options, and the file whose
# bytes change in place for the attempt.
APPROVED_CHANGES = {
    "new-plan-version": ("plan", "tasks.md", {**CALIBRATED, "version": "plan-4"}, None),
    "plan-bytes": ("plan", "tasks.md", CALIBRATED, "tasks.md"),
    "spec-bytes": ("binding", SPEC, {"role": "spec"}, SPEC),
    "ac-bytes": ("binding", "ac.md", {"role": "ac"}, "ac.md"),
    "design-bytes": ("binding", "design.md", {"role": "design"}, "design.md"),
    "new-spec": ("binding", NEW_SPEC, {"role": "spec"}, None),
    "same-digest-other-version": (
        "binding", SPEC, {"role": "spec", "version": "spec-o-2"}, None
    ),
    "same-digest-other-source": (
        "binding", SPEC, {"role": "spec", "source": "a later review"}, None
    ),
}


def test_changing_an_approved_document_needs_scope_change(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    moving_clock: Clock,
) -> None:
    monkeypatch.chdir(repo)
    token = ready_run(cli, started_run)
    assert cli(*approve_args(token)).code == 0
    approval = dig(read_state(home), "approval")
    revision = cli("status", *RUN).get("revision")
    (repo / NEW_SPEC).parent.mkdir(parents=True)
    (repo / NEW_SPEC).write_text("## ADDED Requirements\n\n### ORC-99\n")

    for name, (kind, locator, options, edited) in APPROVED_CHANGES.items():
        original = (repo / edited).read_bytes() if edited else b""
        if edited:
            (repo / edited).write_text("changed after approval\n")
        before = snapshot(run_dir(home))
        r = cli(*register_args(kind, token, locator, **options))
        if edited:
            (repo / edited).write_bytes(original)
        assert r.code == 1, name
        assert r.get("result") == {"error": "scope_change_required"}, name
        assert snapshot(run_dir(home)) == before, name
        assert dig(read_state(home), "approval") == approval, name
        assert cli("status", *RUN).get("revision") == revision, name

    # The same registration (D9), a second later: nothing to commit.
    where = ("versions", "bindings", "spec", SPEC, "registered_at")
    registered_at = dig(read_state(home), *where)
    moving_clock.advance(seconds=1)
    r = cli(*register_args("binding", token, SPEC, role="spec"))
    assert r.code == 0
    assert r.get("result", "unchanged") is True
    assert r.get("revision") == revision
    assert cli("status", *RUN).get("revision") == revision
    assert dig(read_state(home), *where) == registered_at != moving_clock()

    # The approval covers neither an SA confirmation nor the policy.
    for kind, locator, options in [
        ("binding", "sa.md", {"role": "sa"}),
        ("policy", "workflow.yaml", {}),
    ]:
        r = cli(*register_args(kind, token, locator, **options))
        assert r.code == 0, locator
        assert r.get("result", "unchanged") is False, locator
        assert dig(read_state(home), "approval") == approval, locator
        assert dig(read_state(home), "phase") == "approved", locator


def resolve_args(token: str, cid: str, **fields: str) -> list[str]:
    """argv of a human resolve_conflict on `cid`; `fields` override."""
    given = {"id": "r-1", "target": cid, "choice": "original", "reason": "settle d-x"}
    return decide_args("resolve_conflict", token, **{**given, **fields})


@pytest.mark.parametrize(
    "case", ["original", "attempted", "abandon", "attempted-other-version"]
)
def test_a_conflict_on_an_applied_approve_plan_follows_the_chosen_content(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    monkeypatch.chdir(repo)
    token = ready_run(cli, started_run)
    assert cli(*approve_args(token, id="d-x", reason="a")).code == 0
    # DG-03: the attempted content names a version that is not the plan's.
    other = {"version": "plan-9"} if case == "attempted-other-version" else {}
    assert cli(*approve_args(token, id="d-x", reason="b", **other)).code == 3
    [k] = dig(read_state(home), "conflicts") or {}

    if case == "attempted-other-version":
        status_before = cli("status", *RUN)
        before = snapshot(run_dir(home))
        r = cli(*resolve_args(token, k, choice="attempted"))
        assert r.code == 1
        assert r.get("result") == {"error": "plan_version_mismatch"}
        assert snapshot(run_dir(home)) == before
        st = cli("status", *RUN)
        assert st.get("revision") == status_before.get("revision")
        for field in ("approval", "decisions", "conflicts"):
            assert st.get("result", field) == status_before.get("result", field), field
        assert st.get("result", "conflicts", k, "resolved_by") is None
        assert st.code == 3
        return

    resolved = cli(*resolve_args(token, k, choice=case))
    assert resolved.code == 0
    state = read_state(home)
    x = dig(state, "decisions", "d-x")
    if case == "abandon":
        assert dig(state, "approval") is None
        assert dig(state, "phase") == "awaiting_approval"
        assert dig(state, "next") == AWAITING_NEXT
        assert dig(x, "status") == "voided"
        # Undoing never restores an approval; a new one is a new decision.
        assert cli(*approve_args(token, id="d-y")).code == 0
        assert dig(read_state(home), "phase") == "approved"
        assert dig(read_state(home), "approval", "decision") == "d-y"
    else:
        assert dig(state, "phase") == "approved"
        assert dig(state, "approval", "decision") == "d-x"
        assert dig(x, "reason") == ("a" if case == "original" else "b")
        if case == "attempted":
            assert dig(x, "replaces", 0, "reason") == "a"
            assert dig(x, "replaces", 0, "voided_by") == "r-1"


# Once `register` has read the revision it commits at, and before it takes the
# run's lock (D4), each command line of `first` runs to its end in a process
# of its own; their exit codes and stdout go to `record`. The clock first
# moves to the next second, so what they register is registered later than
# the delayed registration's own time.
REGISTER_FIRST = """\
import fcntl as _rf, json as _rj, subprocess as _rs, sys as _rsys, time as _rt
_flock, _first = _rf.flock, {first!r}

def _flock_after_first(*args, **kwargs):
    if _first:
        _second = int(_rt.time())
        while int(_rt.time()) == _second:
            _rt.sleep(0.01)
    while _first:
        _run = _rs.run(
            [_rsys.executable, "-m", "loopctl", *_first.pop(0)],
            capture_output=True, text=True,
        )
        with open({record!r}, "a") as _out:
            _out.write(_rj.dumps({{"code": _run.returncode, "stdout": _run.stdout}}))
            _out.write("\\n")
    return _flock(*args, **kwargs)

_rf.flock = _flock_after_first
"""


@pytest.mark.parametrize("case", ["identical", "replaced"])
def test_a_registration_that_lost_a_commit_race_is_checked_again(
    cli: Cli,
    cli_proc: Cli,
    home: Path,
    repo: Path,
    tmp_path: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    """D4, D5, D9: plan A is registered at revision 2 while, before its
    commit, the same registration of A (and then B) commits first; A is
    checked again on the latest state, not answered as their duplicate."""
    monkeypatch.chdir(repo)
    token = started_run(REPO, "F-1", "agent:implementer")
    plan_a = register_args("plan", token, "tasks.md", **CALIBRATED)
    plan_b = register_args("plan", token, "tasks.md", **CALIBRATED, version="plan-4")
    first = [plan_a] if case == "identical" else [plan_a, plan_b]
    record = tmp_path / "first.jsonl"
    delayed = cli_proc(
        *plan_a, prelude=REGISTER_FIRST.format(first=first, record=str(record))
    )
    runs = [json.loads(line) for line in record.read_text().splitlines()]
    outs = [json.loads(run["stdout"]) for run in runs]
    assert [run["code"] for run in runs] == [0] * len(first)
    assert [out["revision"] for out in outs] == [3, 4][: len(first)]
    assert delayed.code == 0, delayed

    state = read_state(home)
    if case == "identical":
        # The same registration (D9): nothing to commit; the entry is the one
        # the first registration wrote.
        assert delayed.get("result", "unchanged") is True
        assert delayed.get("result") == {**outs[0]["result"], "unchanged": True}
        assert delayed.get("revision") == 3
        assert dig(state, "plan", "registered_at") == outs[0]["result"]["registered_at"]
    else:
        # B is the plan now, so A replaces it again (D5: A → B → A).
        assert delayed.get("result", "version") == VERSIONS["tasks.md"]
        assert delayed.get("result", "unchanged") is False
        assert delayed.get("revision") == 5
        assert dig(state, "plan", "version") == VERSIONS["tasks.md"]
        plan = dig(state, "plan") or {}
        shown = {name: value for name, value in plan.items() if name != "content"}
        assert delayed.get("result") == {**shown, "unchanged": False}
    assert dig(state, "revision") == delayed.get("revision")
    history = sorted(path.name for path in (run_dir(home) / "history").iterdir())
    assert len(history) == delayed.get("revision")
