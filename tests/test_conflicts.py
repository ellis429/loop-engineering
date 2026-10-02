"""Transition conflicts: Blocked, owners only, and resolve_conflict (D4, D6, D10)."""

from __future__ import annotations

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

# Every common field of decision X (D10), as given on the command line.
FIELDS = {
    "id": "d-x",
    "actor": "human:alice",
    "target": "F-1",
    "reason": "a",
    "source": "#29 comment by alice",
    "impact": "the run stays in planning",
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


def history_files(home: Path) -> list[str]:
    records = (run_dir(home) / "history").iterdir()
    return sorted(f"history/{record.name}" for record in records)


def decide_args(kind: str, token: str | None, **fields: str | None) -> list[str]:
    """argv of `decide <kind>`: FIELDS, then `fields` (None leaves one out)."""
    argv = ["decide", kind, *RUN]
    if token is not None:
        argv += ["--token", token]
    for name, value in {**FIELDS, **fields}.items():
        if value is not None:
            argv += [f"--{name.replace('_', '-')}", value]
    return argv


def payload(kind: str, **fields: str) -> dict[str, str]:
    """The full payload of a decision sent with decide_args(kind, ..., **fields)."""
    return {"kind": kind, **FIELDS, **fields}


def blocked_next(*cids: str) -> dict[str, Any]:
    return {
        "action": "human",
        "blockers": [f"transition_conflict:{cid}" for cid in cids],
        "decision_kinds": ["resolve_conflict"],
    }


def test_same_decision_id_with_other_content_blocks_the_run(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    first = cli(*decide_args("revise", token, reason="a"))
    assert (first.code, first.get("revision")) == (0, 3)

    r = cli(*decide_args("revise", token, reason="b"))
    assert r.code == 3
    assert r.get("result", "error") == "transition_conflict"

    st = cli("status", *RUN)
    conflicts = st.get("result", "conflicts") or {}
    assert len(conflicts) == 1, conflicts
    [cid] = conflicts
    a, b = payload("revise", reason="a"), payload("revise", reason="b")
    for where, conflict in {
        "status": conflicts[cid],
        "state file": dig(read_state(home), "conflicts", cid),
    }.items():
        assert dig(conflict, "transition_id") == "decide:d-x", where
        assert dig(conflict, "committed_revision") == 3, where
        assert dig(conflict, "committed_payload") == a, where
        assert dig(conflict, "attempted_payload") == b, where
    assert st.get("result", "decisions", "d-x", "reason") == "a"
    assert dig(read_state(home), "decisions", "d-x", "reason") == "a"

    nx = cli("next", *RUN)
    for name, out in {"status": st, "next": nx}.items():
        assert out.code == 3, name
        assert out.get("result", "blockers") == [f"transition_conflict:{cid}"], name
        assert out.get("next") == blocked_next(cid), name
        files = out.get("result", "files") or []
        assert "feature.json" in files, name
        assert set(history_files(home)) <= set(files), name

    before = snapshot(run_dir(home))
    other = cli(*decide_args("revise", token, id="d-y"))
    assert other.code == 3
    assert other.get("result", "error") == "transition_conflict"
    assert snapshot(run_dir(home)) == before

    again = cli(*decide_args("revise", token, reason="a"))
    assert again.code == 0
    assert again.get("result", "duplicate") is True


WRONG_TOKEN = "f" * 64

# The history record is linked, then the process dies before feature.json is
# replaced: the decision is committed, and feature.json lags one revision.
CRASH_ON_REPLACE = "import os; os.replace = lambda *a, **k: os._exit(9)"


@pytest.mark.parametrize("case", ["a-wrong-token", "b-no-token", "c-after-interrupt"])
def test_non_owners_cannot_create_conflicts(
    cli: Cli, cli_proc: Cli, home: Path, started_run: StartedRun, case: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    if case == "c-after-interrupt":
        crashed = cli_proc(*decide_args("revise", token), prelude=CRASH_ON_REPLACE)
        assert crashed.code == 9
        # Committed in history; feature.json still lags at revision 2.
        assert dig(read_state(home), "revision") == 2
    else:
        assert cli(*decide_args("revise", token)).code == 0
    status_before = cli("status", *RUN)
    assert status_before.get("revision") == 3
    before = snapshot(run_dir(home))

    given = None if case == "b-no-token" else WRONG_TOKEN
    r = cli(*decide_args("revise", given, reason="b"))
    assert r.code == 4
    assert r.get("result") == {"error": "not_owner"}
    assert snapshot(run_dir(home)) == before
    st = cli("status", *RUN)
    assert st.get("revision") == 3
    assert st.get("result", "conflicts") == status_before.get("result", "conflicts")
    assert st.get("result", "conflicts") == {}


def conflict_ids(cli: Cli) -> set[str]:
    return set(cli("status", *RUN).get("result", "conflicts") or {})


def resolve_args(token: str, cid: str, **fields: str) -> list[str]:
    """argv of a human resolve_conflict on `cid`; `fields` override."""
    given = {"id": "r-1", "target": cid, "choice": "original", "reason": "keep a"}
    return decide_args("resolve_conflict", token, **{**given, **fields})


def test_a_human_resolve_conflict_can_keep_the_original(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token, reason="a")).code == 0
    next_before = cli("status", *RUN).get("next")
    assert cli(*decide_args("revise", token, reason="b")).code == 3
    [k] = conflict_ids(cli)

    # Refused while K is unresolved; what each did is checked after K is resolved.
    refused = {}
    for name, argv in {
        "actor_not_human": resolve_args(token, k, actor="agent:implementer"),
        "unknown_target": resolve_args(token, "0" * 16),
        "invalid_choice": resolve_args(token, k, choice="maybe"),
    }.items():
        before = snapshot(run_dir(home))
        r = cli(*argv)
        after = cli("status", *RUN)
        refused[name] = (r, snapshot(run_dir(home)) == before, after)

    resolved = cli(*resolve_args(token, k))
    assert resolved.code == 0
    st = cli("status", *RUN)
    conflict = st.get("result", "conflicts", k)
    assert dig(conflict, "resolved_by") == "r-1"
    assert dig(conflict, "choice") == "original"
    assert dig(conflict, "committed_payload") == payload("revise", reason="a")
    assert dig(conflict, "attempted_payload") == payload("revise", reason="b")
    assert st.get("result", "decisions", "d-x", "reason") == "a"
    assert st.get("result", "decisions", "d-x", "status") == "in_effect"
    assert st.code == 0
    assert st.get("next") == next_before

    for error, (r, wrote_nothing, after) in refused.items():
        assert r.get("result", "error") == error
        assert r.code == 1, error
        assert wrote_nothing, error
        # Still Blocked: K is unresolved after each refusal.
        assert after.code == 3, error
        assert after.get("result", "conflicts", k, "resolved_by") is None, error

    again = cli(*decide_args("revise", token, reason="a"))
    assert again.code == 0
    assert again.get("result", "duplicate") is True
    before = snapshot(run_dir(home))
    ruled_out = cli(*decide_args("revise", token, reason="b"))
    assert ruled_out.code == 1
    assert ruled_out.get("result", "error") == f"transition_rejected:{k}"
    assert snapshot(run_dir(home)) == before
    assert cli("status", *RUN).code == 0

    third = cli(*decide_args("revise", token, reason="c"))
    assert third.code == 3
    [k2] = conflict_ids(cli) - {k}
    before = snapshot(run_dir(home))
    r = cli(*resolve_args(token, k, id="r-2"))
    assert r.code == 1
    assert r.get("result", "error") == "unknown_target"
    assert snapshot(run_dir(home)) == before
    st = cli("status", *RUN)
    assert st.get("result", "conflicts", k2, "resolved_by") is None
    assert st.code == 3


@pytest.mark.parametrize(
    "case", ["attempted", "abandon", "conflicted-resolve_conflict"]
)
def test_resolve_conflict_can_take_the_attempted_content_or_abandon_it(
    cli: Cli, started_run: StartedRun, case: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token, reason="a")).code == 0
    assert cli(*decide_args("revise", token, reason="b")).code == 3
    [k] = conflict_ids(cli)

    if case == "attempted":
        resolved = cli(*resolve_args(token, k, choice="attempted"))
        assert resolved.code == 0
        x = cli("status", *RUN).get("result", "decisions", "d-x")
        assert dig(x, "reason") == "b"
        assert dig(x, "replaces", 0, "reason") == "a"
        assert dig(x, "replaces", 0, "voided_by") == "r-1"
        accepted, ruled_out = "b", "a"
    elif case == "abandon":
        resolved = cli(*resolve_args(token, k, choice="abandon"))
        assert resolved.code == 0
        x = cli("status", *RUN).get("result", "decisions", "d-x")
        assert dig(x, "reason") == "a"
        assert dig(x, "status") == "voided"
        assert dig(x, "voided_by") == "r-1"
        accepted, ruled_out = "a", "b"
    else:
        # The conflicted decision is itself the resolve_conflict R.
        assert cli(*resolve_args(token, k)).code == 0
        assert cli(*resolve_args(token, k, reason="keep a after all")).code == 3
        [k_r] = conflict_ids(cli) - {k}
        for n, choice in enumerate(["attempted", "abandon"], 2):
            r = cli(*resolve_args(token, k_r, id=f"r-{n}", choice=choice))
            assert r.code == 1, choice
            assert r.get("result", "error") == "choice_not_allowed", choice
        assert cli(*resolve_args(token, k_r, id="r-4")).code == 0
        return

    again = cli(*decide_args("revise", token, reason=accepted))
    assert again.code == 0
    assert again.get("result", "duplicate") is True
    if case == "abandon":
        assert again.get("result", "decision", "status") == "voided"
    r = cli(*decide_args("revise", token, reason=ruled_out))
    assert r.code == 1
    assert r.get("result", "error") == f"transition_rejected:{k}"


@pytest.mark.parametrize("other", ["original", "abandon"])
def test_attempted_cannot_apply_another_resolve_conflict(
    cli: Cli, home: Path, started_run: StartedRun, other: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token, reason="a")).code == 0
    # K2: a conflict on another decision Y.
    assert cli(*decide_args("revise", token, id="d-y")).code == 0
    assert cli(*decide_args("revise", token, id="d-y", reason="b")).code == 3
    [k2] = conflict_ids(cli)
    # K1: X's id resent as a resolve_conflict of K2, so K1's A resolves K2.
    assert cli(*resolve_args(token, k2, id="d-x")).code == 3
    [k1] = conflict_ids(cli) - {k2}
    k1_state = dig(read_state(home), "conflicts", k1)
    assert dig(k1_state, "committed_payload", "kind") == "revise"
    assert dig(k1_state, "attempted_payload", "kind") == "resolve_conflict"
    status_before = cli("status", *RUN)
    before = snapshot(run_dir(home))

    r = cli(*resolve_args(token, k1, choice="attempted"))
    assert r.code == 1
    assert r.get("result", "error") == "choice_not_allowed"
    assert snapshot(run_dir(home)) == before
    st = cli("status", *RUN)
    assert st.get("revision") == status_before.get("revision")
    for field in ("decisions", "conflicts"):
        assert st.get("result", field) == status_before.get("result", field), field

    r = cli(*resolve_args(token, k1, choice=other))
    assert r.code == 0


def test_one_open_conflict_per_decision_and_fresh_content_after_resolution(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    """Regression (review T4.2-01): while X has an open conflict, other content
    for X records nothing, so a later conflict never keeps a stale payload."""
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token, reason="a")).code == 0
    blockers_before = cli("status", *RUN).get("result", "blockers")
    assert cli(*decide_args("revise", token, reason="b")).code == 3
    [kb] = conflict_ids(cli)
    revision_before = cli("status", *RUN).get("revision")
    before = snapshot(run_dir(home))

    r = cli(*decide_args("revise", token, reason="c"))
    assert r.code == 3
    conflicts = cli("status", *RUN).get("result", "conflicts") or {}
    assert len(conflicts) == 1, conflicts
    assert set(conflicts) == {kb}
    assert r.get("result", "error") == "transition_conflict"
    assert r.get("result", "blockers") == [f"transition_conflict:{kb}"]
    assert cli("status", *RUN).get("revision") == revision_before
    assert snapshot(run_dir(home)) == before

    assert cli(*resolve_args(token, kb, choice="attempted")).code == 0
    assert cli("status", *RUN).get("result", "decisions", "d-x", "reason") == "b"

    r = cli(*decide_args("revise", token, reason="c"))
    assert r.code == 3
    [kc] = conflict_ids(cli) - {kb}
    assert r.get("result", "blockers") == [f"transition_conflict:{kc}"]
    b, c = payload("revise", reason="b"), payload("revise", reason="c")
    for where, conflict in {
        "status": cli("status", *RUN).get("result", "conflicts", kc),
        "state file": dig(read_state(home), "conflicts", kc),
    }.items():
        assert dig(conflict, "committed_payload") == b, where
        assert dig(conflict, "attempted_payload") == c, where

    assert cli(*resolve_args(token, kc, id="r-2")).code == 0
    assert cli("status", *RUN).get("result", "decisions", "d-x", "reason") == "b"

    for reason, cid in {"a": kb, "c": kc}.items():
        before = snapshot(run_dir(home))
        r = cli(*decide_args("revise", token, reason=reason))
        assert r.code == 1, reason
        assert r.get("result", "error") == f"transition_rejected:{cid}", reason
        assert snapshot(run_dir(home)) == before, reason
    st = cli("status", *RUN)
    assert st.code == 0
    assert st.get("result", "blockers") == blockers_before


def test_every_transition_keeps_its_committed_payload(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    """Regression (review of 4.2 attempt 1): D3 keeps the committed payload in
    every transitions entry, the first one written by init included."""
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token)).code == 0
    transitions = dig(read_state(home), "transitions") or {}
    assert dig(transitions, "init", "payload") == {
        "repo": REPO,
        "feature": "F-1",
        "issue": "29",
        "actor": "agent:implementer",
    }
    assert dig(transitions, "decide:d-x", "payload") == payload("revise")
    [claim] = [entry for tid, entry in transitions.items() if tid.startswith("claim:")]
    assert dig(claim, "payload") == {"actor": "agent:implementer"}


@pytest.mark.parametrize(
    ("choice", "ruled_out"), [("attempted", "a"), ("original", "b")], ids=["a", "b"]
)
def test_a_rejected_content_stays_rejected_while_a_later_conflict_is_open(
    cli: Cli, home: Path, started_run: StartedRun, choice: str, ruled_out: str
) -> None:
    """Regression (review T4.2-03): D4 step 3 refuses content an earlier
    resolution ruled out before it looks for the open conflict on the id."""
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("revise", token, reason="a")).code == 0
    assert cli(*decide_args("revise", token, reason="b")).code == 3
    [kb] = conflict_ids(cli)
    assert cli(*resolve_args(token, kb, choice=choice)).code == 0
    assert cli(*decide_args("revise", token, reason="c")).code == 3
    [kc] = conflict_ids(cli) - {kb}
    status_before = cli("status", *RUN)
    before = snapshot(run_dir(home))

    r = cli(*decide_args("revise", token, reason=ruled_out))
    assert r.code == 1
    assert r.get("result") == {"error": f"transition_rejected:{kb}"}
    assert snapshot(run_dir(home)) == before
    st = cli("status", *RUN)
    assert st.get("revision") == status_before.get("revision")
    assert st.get("result", "conflicts") == status_before.get("result", "conflicts")
    assert st.get("result", "conflicts", kc, "resolved_by") is None
    assert st.code == 3


def test_attempted_is_refused_when_the_attempted_content_fails_its_checks(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    """DG-03: the target check is the kind's own, after the conflict (D2), so
    an invalid A is recorded as a conflict, and only `attempted` is refused."""
    token = started_run(REPO, "F-1", "agent:implementer")
    assert cli(*decide_args("budget_extension", token, target="active:60")).code == 0
    assert cli(*decide_args("budget_extension", token, target="rounds:+2")).code == 3
    [k] = conflict_ids(cli)
    status_before = cli("status", *RUN)
    before = snapshot(run_dir(home))

    r = cli(*resolve_args(token, k, choice="attempted"))
    assert r.code == 1
    assert r.get("result") == {"error": "invalid_target"}
    assert snapshot(run_dir(home)) == before
    st = cli("status", *RUN)
    assert st.get("revision") == status_before.get("revision")
    for field in ("decisions", "conflicts"):
        assert st.get("result", field) == status_before.get("result", field), field
    assert st.get("result", "conflicts", k, "resolved_by") is None
    assert st.code == 3

    r = cli(*resolve_args(token, k, choice="original"))
    assert r.code == 0
