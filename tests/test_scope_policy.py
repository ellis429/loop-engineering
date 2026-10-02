"""scope_change and policy_change: a scope change revokes the approval and
supersedes the plan, a policy is approved on its digest, and undoing either
clears only its own effect, never restoring an approval (D7, D9, D10, D11)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import Result, dig

Cli = Callable[..., Result]
StartedRun = Callable[[str, str, str], str]

REPO = "yschiang/loop-engineering"
RUN = ["--repo", REPO, "--feature", "F-1"]
SOURCE = "#29 plan review"

# The version each document of the `repo` fixture is registered at.
VERSIONS = {
    "tasks.md": "plan-3",
    "specs/orchestration/spec.md": "spec-o-1",
    "specs/durable/spec.md": "spec-d-1",
    "ac.md": "ac-1",
    "design.md": "design-2",
    "workflow.yaml": "policy-1",
}

# The plan an Implementer calibrated, and the bindings approve_plan needs.
CALIBRATED = {"producer": "implementer", "calibrated_from": "tasks-draft.md"}
BINDINGS = {
    "spec": ["specs/orchestration/spec.md", "specs/durable/spec.md"],
    "ac": ["ac.md"],
    "design": ["design.md"],
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


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def register_args(
    kind: str, token: str, locator: str, **options: str
) -> list[str]:
    """argv of `register <kind>` for `locator` at its VERSIONS entry;
    `options` add or override."""
    argv = ["register", kind, *RUN, "--locator", locator, "--token", token]
    given = {"version": VERSIONS.get(locator, "v1"), "source": SOURCE, **options}
    for name, value in given.items():
        argv += [f"--{name.replace('_', '-')}", value]
    return argv


def registered(cli: Cli, token: str, kind: str, locator: str, **options: str) -> Result:
    """A registration that must succeed."""
    r = cli(*register_args(kind, token, locator, **options))
    assert r.code == 0, r
    return r


FIELDS = {
    "actor": "human:alice",
    "reason": "a",
    "source": "#29 comment by alice",
    "impact": "work on the plan may start",
}


def decide_args(kind: str, token: str, *extra: str, **fields: str) -> list[str]:
    """argv of `decide <kind>`: FIELDS, then `fields`, then `extra`."""
    argv = ["decide", kind, *RUN, "--token", token]
    for name, value in {**FIELDS, **fields}.items():
        argv += [f"--{name.replace('_', '-')}", value]
    return [*argv, *extra]


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


QUESTIONS = ["does F-2 keep its contract?", "is AC-O07 still testable?"]


def scope_args(token: str, **fields: str) -> list[str]:
    """argv of a human scope_change S with two open questions; `fields`
    override."""
    given = {
        "id": "s-1",
        "target": "tasks.md",
        "reason": "the AC must change",
        "impact": "the run stops until a new plan is approved",
    }
    extra = [arg for question in QUESTIONS for arg in ("--open-question", question)]
    return decide_args("scope_change", token, *extra, **{**given, **fields})


def ready_run(cli: Cli, started_run: StartedRun) -> str:
    """A run claimed by agent:implementer, with the calibrated plan tasks.md
    and its spec, ac and design bindings registered; returns the token. The
    cwd must be the `repo` fixture."""
    token = started_run(REPO, "F-1", "agent:implementer")
    registered(cli, token, "plan", "tasks.md", **CALIBRATED)
    for role, locators in BINDINGS.items():
        for locator in locators:
            registered(cli, token, "binding", locator, role=role)
    return token


def plan_pin(repo: Path, version: str = VERSIONS["tasks.md"]) -> dict[str, str]:
    """How an approval or a scope_change pins tasks.md as it is now (D9)."""
    return {
        "locator": "tasks.md",
        "version": version,
        "digest": sha256((repo / "tasks.md").read_bytes()),
    }


def superseded_next(*ids: str) -> dict[str, Any]:
    return {
        "action": "human",
        "blockers": [f"plan_superseded:{i}" for i in ids],
        "decision_kinds": [],
    }


@pytest.mark.parametrize("start", ["no-plan", "approved", "awaiting"])
def test_scope_change_stops_the_run_and_supersedes_the_plan(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    start: str,
) -> None:
    monkeypatch.chdir(repo)
    if start == "no-plan":
        # Just claimed: there is no plan a scope change could supersede.
        token = started_run(REPO, "F-1", "agent:implementer")
        revision = cli("status", *RUN).get("revision")
        r = cli(*scope_args(token))
        assert r.code == 1
        assert r.get("result") == {"error": "plan_not_registered"}
        assert cli("status", *RUN).get("revision") == revision
        return

    token = ready_run(cli, started_run)
    if start == "approved":
        assert cli(*approve_args(token)).code == 0
    approval = dig(read_state(home), "approval")
    pin = plan_pin(repo)

    # The coordinator cannot change the scope: the approval stays.
    r = cli(*scope_args(token, actor="agent:implementer"))
    assert r.code == 1
    assert r.get("result") == {"error": "actor_not_human"}
    assert dig(read_state(home), "approval") == approval

    r = cli(*scope_args(token))
    assert r.code == 0
    state = read_state(home)
    assert dig(state, "approval") is None
    record = dig(state, "decisions", "s-1")
    assert dig(record, "impact") == "the run stops until a new plan is approved"
    assert dig(record, "reason") == "the AC must change"
    assert dig(record, "open_questions") == QUESTIONS
    assert dig(record, "supersedes") == pin
    assert dig(state, "phase") == "awaiting_approval"
    assert dig(state, "plan", "superseded_by") == ["s-1"]
    assert dig(state, "next") == superseded_next("s-1")
    for name in ("status", "next"):
        assert cli(name, *RUN).get("next") == superseded_next("s-1"), name


def scoped_run(cli: Cli, started_run: StartedRun, *, approved: bool) -> str:
    """A ready run, approved by ap-1 when `approved`, whose plan tasks.md
    (P1) the human scope_change s-1 then superseded; returns the token."""
    token = ready_run(cli, started_run)
    if approved:
        assert cli(*approve_args(token)).code == 0
    assert cli(*scope_args(token)).code == 0
    return token


NEW_PLAN = "# Tasks\n\n- [ ] 1.1 calibrated plan for F-1, rescoped\n"

AWAITING_NEXT = {
    "action": "human",
    "blockers": ["plan_not_approved"],
    "decision_kinds": ["approve_plan"],
}


@pytest.mark.parametrize("start", ["approved", "awaiting"])
def test_only_a_new_plan_version_is_approvable_after_scope_change(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    start: str,
) -> None:
    monkeypatch.chdir(repo)
    token = scoped_run(cli, started_run, approved=start == "approved")
    p1 = (repo / "tasks.md").read_bytes()

    # The superseded plan cannot be approved ...
    r = cli(*approve_args(token, id="ap-old"))
    assert r.code == 1
    assert r.get("result") == {"error": "plan_superseded"}
    # ... nor registered again at the same version and digest.
    before = snapshot(run_dir(home))
    r = cli(*register_args("plan", token, "tasks.md", **CALIBRATED))
    assert r.code == 1
    assert r.get("result") == {"error": "plan_superseded"}
    assert snapshot(run_dir(home)) == before

    # A new plan version is approvable, and then the run goes on.
    (repo / "tasks.md").write_text(NEW_PLAN)
    registered(cli, token, "plan", "tasks.md", **CALIBRATED, version="plan-4")
    assert cli("next", *RUN).get("next") == AWAITING_NEXT
    r = cli(*approve_args(token, id="ap-2", version="plan-4"))
    assert r.code == 0
    assert dig(read_state(home), "phase") == "approved"
    nx = cli("next", *RUN)
    assert nx.get("next", "action") == "dispatch"
    assert nx.get("next", "plan") == plan_pin(repo, "plan-4")

    # Once approved, the approval guard comes before plan_superseded (D9).
    (repo / "tasks.md").write_bytes(p1)
    r = cli(*register_args("plan", token, "tasks.md", **CALIBRATED))
    assert r.code == 1
    assert r.get("result") == {"error": "scope_change_required"}


def conflict_on(cli: Cli, resend: list[str]) -> str:
    """Resend a committed decision with other content; the cid of the
    conflict it records (D6)."""
    r = cli(*resend)
    assert r.code == 3, r
    blockers = r.get("result", "blockers") or []
    assert len(blockers) == 1, r
    return str(blockers[0]).removeprefix("transition_conflict:")


def resolve_args(token: str, cid: str, choice: str, **fields: str) -> list[str]:
    """argv of a human resolve_conflict r-1 on `cid`; `fields` override."""
    given = {"id": "r-1", "target": cid, "choice": choice, "reason": "settle it"}
    return decide_args("resolve_conflict", token, **{**given, **fields})


SPEC = BINDINGS["spec"][0]
IMPACT = "the run stops until a new plan is approved"
OTHER_IMPACT = "the run stops for the F-2 contract too"


@pytest.mark.parametrize("case", ["i", "ii", "iii", "iv", "v"])
def test_undoing_a_scope_change_never_restores_the_approval(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    monkeypatch.chdir(repo)
    # ap-1 approves P1 with B1, then s-1 supersedes P1.
    token = scoped_run(cli, started_run, approved=True)
    if case in ("i", "ii"):
        # Only the spec changes (B2); the plan stays P1.
        (repo / SPEC).write_text("## ADDED Requirements\n\n### ORC-01 revised\n")
        registered(cli, token, "binding", SPEC, role="spec", version="spec-o-2")
    if case in ("iii", "v"):
        # A new plan P2 is registered.
        (repo / "tasks.md").write_text(NEW_PLAN)
        registered(cli, token, "plan", "tasks.md", **CALIBRATED, version="plan-4")
    p2 = dig(read_state(home), "plan")
    undone = "s-1"
    if case == "iv":
        # Another scope_change s-2 on the same P1, then s-2 is undone.
        assert cli(*scope_args(token, id="s-2")).code == 0
        undone = "s-2"
    choice = "attempted" if case in ("ii", "v") else "abandon"
    cid = conflict_on(cli, scope_args(token, id=undone, impact=OTHER_IMPACT))
    assert cli(*resolve_args(token, cid, choice)).code == 0
    state = read_state(home)
    assert dig(state, "approval") is None

    if case == "i":
        assert dig(state, "next", "blockers") == ["plan_not_approved"]
        assert dig(state, "next") == AWAITING_NEXT
        assert dig(state, "plan", "superseded_by") == []
        assert dig(state, "decisions", "s-1", "status") == "voided"
        # A new approval is a new decision, on the bindings of now.
        assert cli(*approve_args(token, id="ap-y")).code == 0
        state = read_state(home)
        assert dig(state, "phase") == "approved"
        assert dig(state, "approval", "decision") == "ap-y"
        b2 = sha256((repo / SPEC).read_bytes())
        assert dig(state, "approval", "bindings", "spec", SPEC) == b2
    elif case == "ii":
        s = dig(state, "decisions", "s-1")
        assert dig(s, "kind") == "scope_change"
        assert dig(s, "impact") == OTHER_IMPACT
        assert dig(s, "replaces", 0, "impact") == IMPACT
        assert dig(s, "replaces", 0, "voided_by") == "r-1"
        assert dig(state, "plan", "superseded_by") == ["s-1"]
        assert dig(state, "next") == superseded_next("s-1")
    elif case == "iii":
        assert dig(state, "plan") == p2
        assert dig(state, "plan", "version") == "plan-4"
        assert dig(state, "next") == AWAITING_NEXT
    elif case == "iv":
        assert dig(state, "plan", "superseded_by") == ["s-1"]
        assert dig(state, "next") == superseded_next("s-1")
        r = cli(*approve_args(token, id="ap-y"))
        assert r.code == 1
        assert r.get("result") == {"error": "plan_superseded"}
        r = cli(*register_args("plan", token, "tasks.md", **CALIBRATED))
        assert r.code == 1
        assert r.get("result") == {"error": "plan_superseded"}
    else:
        # The attempted scope_change supersedes the plan of the resolution,
        # P2, not P1 (G-12).
        assert dig(state, "decisions", "s-1", "supersedes") == plan_pin(repo, "plan-4")
        assert dig(state, "plan", "superseded_by") == ["s-1"]
        assert dig(state, "next") == superseded_next("s-1")


POLICY_REASON = "accept unit-linux as the required check"


def policy_args(token: str, digest: str, **fields: str) -> list[str]:
    """argv of a human policy_change p-1 of workflow.yaml at `digest`;
    `fields` override."""
    given = {
        "id": "p-1",
        "target": "workflow.yaml",
        "version": digest,
        "reason": POLICY_REASON,
        "impact": "G3 may use this policy",
    }
    return decide_args("policy_change", token, **{**given, **fields})


def policy_of(cli: Cli) -> Any:
    return cli("status", *RUN).get("result", "policy")


def approved_policy(cli: Cli, started_run: StartedRun, repo: Path) -> tuple[str, str]:
    """A run whose workflow.yaml the human policy_change p-1 approved;
    returns the token and the approved digest."""
    token = started_run(REPO, "F-1", "agent:implementer")
    registered(cli, token, "policy", "workflow.yaml")
    digest = sha256((repo / "workflow.yaml").read_bytes())
    assert cli(*policy_args(token, digest)).code == 0
    return token, digest


def test_policy_is_approved_only_by_policy_change_on_its_digest(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    token = started_run(REPO, "F-1", "agent:implementer")
    nxt = cli("next", *RUN).get("next")
    digest = sha256((repo / "workflow.yaml").read_bytes())

    policy = policy_of(cli)
    assert dig(policy, "status") == "not_registered"
    assert policy == {
        "status": "not_registered",
        "registration": None,
        "approval": None,
        "current_digest": None,
    }
    revision = cli("status", *RUN).get("revision")
    r = cli(*policy_args(token, digest))
    assert r.code == 1
    assert r.get("result") == {"error": "policy_not_registered"}
    assert cli("status", *RUN).get("revision") == revision

    registered(cli, token, "policy", "workflow.yaml")
    policy = policy_of(cli)
    assert dig(policy, "status") == "not_approved"
    assert dig(policy, "registration", "digest") == digest
    assert dig(policy, "registration", "locator") == "workflow.yaml"
    assert dig(policy, "approval") is None
    assert cli("next", *RUN).get("next") == nxt

    for name, fields, error in [
        ("agent", {"actor": "agent:implementer"}, "actor_not_human"),
        ("digest", {"version": "sha256:" + "0" * 64}, "policy_digest_mismatch"),
        ("locator", {"target": "workflow.yml"}, "policy_digest_mismatch"),
    ]:
        before = snapshot(run_dir(home))
        r = cli(*policy_args(token, digest, id=f"p-{name}", **fields))
        assert r.code == 1, name
        assert r.get("result") == {"error": error}, name
        assert snapshot(run_dir(home)) == before, name
        assert dig(policy_of(cli), "status") == "not_approved", name

    r = cli(*policy_args(token, digest))
    assert r.code == 0
    policy = policy_of(cli)
    assert dig(policy, "status") == "approved"
    assert dig(policy, "approval", "decision") == "p-1"
    assert dig(policy, "approval", "digest") == digest
    assert dig(read_state(home), "policy_approval") == {
        "decision": "p-1",
        "locator": "workflow.yaml",
        "digest": digest,
    }

    # Approved already: another policy_change on the same digest takes its
    # place (G-11).
    r = cli(*policy_args(token, digest, id="p-2"))
    assert r.code == 0
    assert dig(read_state(home), "policy_approval", "decision") == "p-2"
    assert dig(policy_of(cli), "status") == "approved"

    # The policy never changes next (D7).
    for name in ("status", "next"):
        assert cli(name, *RUN).get("next") == nxt, name
    assert dig(read_state(home), "next") == nxt


CHANGED_POLICY = "schema_version: 1\nrepo: yschiang/loop-engineering\ng3: {}\n"


def test_policy_changed_after_approval_is_not_approved(
    cli: Cli,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    token, approved = approved_policy(cli, started_run, repo)
    path = repo / "workflow.yaml"

    # Changed in place after the approval.
    path.write_text(CHANGED_POLICY)
    changed = sha256(path.read_bytes())
    policy = policy_of(cli)
    assert dig(policy, "status") == "digest_mismatch"
    assert dig(policy, "approval", "digest") == approved
    assert dig(policy, "current_digest") == changed

    # Gone.
    path.unlink()
    policy = policy_of(cli)
    assert dig(policy, "status") == "unreadable"
    assert dig(policy, "current_digest") is None

    # Back with the changed content and registered again: not approved.
    path.write_text(CHANGED_POLICY)
    registered(cli, token, "policy", "workflow.yaml", version="policy-2")
    policy = policy_of(cli)
    assert dig(policy, "status") == "not_approved"
    assert dig(policy, "registration", "digest") == changed
    assert dig(policy, "approval", "digest") == approved

    # A policy_change on the new digest approves it.
    assert cli(*policy_args(token, changed, id="p-2")).code == 0
    policy = policy_of(cli)
    assert dig(policy, "status") == "approved"
    assert dig(policy, "approval", "digest") == changed
    assert dig(policy, "current_digest") == changed


@pytest.mark.parametrize(
    "case", ["original", "attempted", "abandon", "abandon-replaced"]
)
def test_undoing_a_policy_change_removes_its_policy_approval(
    cli: Cli,
    home: Path,
    repo: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    monkeypatch.chdir(repo)
    # p-1 approves the policy with POLICY_REASON.
    token, digest = approved_policy(cli, started_run, repo)
    if case == "abandon-replaced":
        # A later p-2 takes p-1's place as the approval (G-11).
        assert cli(*policy_args(token, digest, id="p-2")).code == 0
    cid = conflict_on(cli, policy_args(token, digest, reason="b"))
    choice = case.removesuffix("-replaced")
    assert cli(*resolve_args(token, cid, choice)).code == 0
    state, policy = read_state(home), policy_of(cli)

    if case == "original":
        assert dig(policy, "status") == "approved"
        assert dig(policy, "approval", "decision") == "p-1"
        assert dig(state, "decisions", "p-1", "reason") == POLICY_REASON
        assert dig(state, "decisions", "p-1", "status") == "in_effect"
    elif case == "attempted":
        assert dig(policy, "status") == "approved"
        assert dig(state, "decisions", "p-1", "reason") == "b"
        assert dig(state, "policy_approval", "decision") == "p-1"
    elif case == "abandon":
        assert dig(policy, "status") == "not_approved"
        assert dig(state, "policy_approval") is None
        assert dig(state, "decisions", "p-1", "status") == "voided"
        # Undoing never restores an approval; a new one is a new decision.
        assert cli(*policy_args(token, digest, id="p-3")).code == 0
        assert dig(policy_of(cli), "status") == "approved"
        assert dig(read_state(home), "policy_approval", "decision") == "p-3"
    else:
        # Only what still belongs to p-1 is cleared: p-2's approval stays.
        assert dig(state, "decisions", "p-1", "status") == "voided"
        assert dig(state, "policy_approval", "decision") == "p-2"
        assert dig(policy, "status") == "approved"
