"""Human decisions: decide, its checks, resends and history catch-up (D2, D4, D10)."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import Result, dig

from loopctl import clock

Cli = Callable[..., Result]
StartedRun = Callable[[str, str, str], str]

REPO = "yschiang/loop-engineering"
RUN = ["--repo", REPO, "--feature", "F-1"]
AT = "2026-10-02T09:00:00+00:00"

# Every common field of a decision (D10), as given on the command line.
FIELDS = {
    "id": "d-1",
    "actor": "human:alice",
    "target": "F-1",
    "reason": "the plan needs another pass",
    "source": "#29 comment by alice",
    "impact": "the run stays in planning",
}


# The kinds of this version (D10), each with the extra field it needs.
KINDS = {
    "approve_plan": {"version": "v1"},
    "scope_change": {},
    "policy_change": {"version": "sha256:" + "0" * 64},
    "budget_extension": {"target": "rounds:+1"},
    "revise": {},
    "handoff": {},
    "resolve_conflict": {"choice": "original"},
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


def decide_args(kind: str, token: str | None, **fields: str | None) -> list[str]:
    """argv of `decide <kind>`: FIELDS, then `fields` (None leaves one out)."""
    argv = ["decide", kind, *RUN]
    if token is not None:
        argv += ["--token", token]
    for name, value in {**FIELDS, **fields}.items():
        if value is not None:
            argv += [f"--{name.replace('_', '-')}", value]
    return argv


@pytest.mark.parametrize("kind", ["revise", "handoff"])
def test_a_human_decision_is_recorded_with_its_provenance(
    cli: Cli,
    home: Path,
    started_run: StartedRun,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    monkeypatch.setattr(clock, "now", lambda: AT)
    token = started_run(REPO, "F-1", "agent:implementer")
    before = cli("status", *RUN)
    state_before = read_state(home)

    r = cli(*decide_args(kind, token))
    st = cli("status", *RUN)
    assert st.get("result", "decisions", "d-1", "source") == FIELDS["source"]
    assert r.code == 0
    assert r.get("revision") == before.get("revision") + 1

    expected = {
        "kind": kind,
        **{name: FIELDS[name] for name in ("actor", "target", "reason", "impact")},
        "source": FIELDS["source"],
        "at": AT,
        "seq": 1,
        "status": "in_effect",
    }
    # status projects decisions as they are in the state file (D11).
    for where, record in {
        "status": st.get("result", "decisions", "d-1"),
        "state file": dig(read_state(home), "decisions", "d-1"),
    }.items():
        for name, value in expected.items():
            assert dig(record, name) == value, (where, name)
    for name in ("phase", "owner", "gates"):
        assert st.get("result", name) == before.get("result", name), name
        assert dig(read_state(home), name) == dig(state_before, name), name


NOT_HUMAN = [
    "agent:implementer",
    "project_lead",
    "session:lead/child-1",
    "human:",
    "Human:alice",
]


@pytest.mark.parametrize("actor", NOT_HUMAN)
def test_only_human_actors_can_decide(
    cli: Cli, home: Path, started_run: StartedRun, actor: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    before = snapshot(run_dir(home))
    for kind, extra in KINDS.items():
        r = cli(*decide_args(kind, token, **{**extra, "actor": actor}))
        assert r.code == 1, (kind, r)
        assert r.get("result", "error") == "actor_not_human", kind
    assert cli("status", *RUN).get("revision") == 2
    assert snapshot(run_dir(home)) == before


@pytest.mark.parametrize(
    ("kind", "missing"),
    [
        *[pytest.param("revise", name, id=name) for name in FIELDS],
        pytest.param("approve_plan", "version", id="approve_plan-version"),
        pytest.param("policy_change", "version", id="policy_change-version"),
        pytest.param("resolve_conflict", "choice", id="resolve_conflict-choice"),
    ],
)
def test_missing_fields_are_rejected(
    cli: Cli, home: Path, started_run: StartedRun, kind: str, missing: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    before = snapshot(run_dir(home))
    extra = {name: value for name, value in KINDS[kind].items() if name != missing}
    r = cli(*decide_args(kind, token, **extra, **{missing: None}))
    assert r.get("result") == {"error": "missing_fields", "fields": [missing]}
    assert r.code == 1
    assert cli("status", *RUN).get("revision") == 2
    assert snapshot(run_dir(home)) == before


WRONG_TOKEN = "f" * 64


@pytest.mark.parametrize("token", [None, WRONG_TOKEN], ids=["no-token", "wrong-token"])
def test_writes_need_the_coordinator_token(
    cli: Cli, home: Path, started_run: StartedRun, token: str | None
) -> None:
    started_run(REPO, "F-1", "agent:implementer")
    before = snapshot(run_dir(home))
    r = cli(*decide_args("revise", token))
    assert r.code == 4
    assert r.get("result") == {"error": "not_owner"}
    assert snapshot(run_dir(home)) == before
    # The same caller can still read the run.
    st = cli("status", *RUN)
    assert st.code == 0
    assert st.get("revision") == 2


# The history record is linked, then the process dies before feature.json is
# replaced: the decision is committed, and feature.json lags one revision.
CRASH_ON_REPLACE = "import os; os.replace = lambda *a, **k: os._exit(9)"


@pytest.mark.parametrize("first", ["completed", "interrupted"])
def test_resending_a_decision_takes_effect_once(
    cli: Cli, cli_proc: Cli, started_run: StartedRun, first: str
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    argv = decide_args("revise", token)
    if first == "completed":
        sent = cli(*argv)
        assert (sent.code, sent.get("revision")) == (0, 3)
    else:
        sent = cli_proc(*argv, prelude=CRASH_ON_REPLACE)
        assert sent.code == 9
    committed = 3

    again = cli(*argv)
    assert again.get("revision") == committed
    assert again.code == 0
    assert again.get("result", "duplicate") is True
    st = cli("status", *RUN)
    assert st.get("revision") == committed
    assert list(st.get("result", "decisions") or {}) == ["d-1"]
    assert st.get("result", "decisions", "d-1", "seq") == 1


# D13: os.replace dies only when the state it moves into place is at the given
# revision, so catching up a lagging feature.json (D4 step 8.1) still happens.
CRASH_ON_REPLACING_REVISION = """\
import json as _cj, os as _co
_replace = _co.replace

def _crashing_replace(src, dst, *args, **kwargs):
    with open(src, "rb") as _file:
        _revision = _cj.load(_file).get("revision")
    if _revision == {revision}:
        _co._exit(9)
    return _replace(src, dst, *args, **kwargs)

_co.replace = _crashing_replace
"""


def history(home: Path) -> list[str]:
    return sorted(path.name for path in (run_dir(home) / "history").iterdir())


def test_consecutive_interruptions_keep_every_committed_revision(
    cli: Cli, cli_proc: Cli, home: Path, started_run: StartedRun
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    x = decide_args("revise", token, id="d-x")
    y = decide_args("handoff", token, id="d-y")
    crash_x = cli_proc(*x, prelude=CRASH_ON_REPLACING_REVISION.format(revision=3))
    assert crash_x.code == 9
    crash_y = cli_proc(*y, prelude=CRASH_ON_REPLACING_REVISION.format(revision=4))
    assert crash_y.code == 9

    st = cli("status", *RUN)
    assert st.get("result", "revision") == 4
    assert st.code == 0
    assert sorted(st.get("result", "decisions") or {}) == ["d-x", "d-y"]

    for argv in (x, y):
        again = cli(*argv)
        assert again.code == 0, argv
        assert again.get("result", "duplicate") is True, argv
        assert again.get("revision") == 4, argv
    st = cli("status", *RUN)
    assert st.get("revision") == 4
    decided = st.get("result", "decisions") or {}
    assert {name: dig(record, "seq") for name, record in decided.items()} == {
        "d-x": 1,
        "d-y": 2,
    }

    z = cli(*decide_args("revise", token, id="d-z"))
    assert z.code == 0
    assert z.get("revision") == 5
    assert history(home) == [f"{revision}.json" for revision in range(1, 6)]
    assert dig(read_state(home), "revision") == 5


@pytest.mark.parametrize("case", ["a-wrong-token", "b-no-token", "c-after-interrupt"])
def test_non_owners_cannot_resend(
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
    assert cli("status", *RUN).get("revision") == 3
    before = snapshot(run_dir(home))

    r = cli(*decide_args("revise", None if case == "b-no-token" else WRONG_TOKEN))
    assert r.code == 4
    assert r.get("result") == {"error": "not_owner"}
    assert snapshot(run_dir(home)) == before
    assert cli("status", *RUN).get("revision") == 3


BUDGET_TARGETS = [
    "active:60",
    "rounds:+1",
    "attempts:1.1:+1",
    "ci_wait:0123456789abcdef0123456789abcdef01234567",
]
# Requests that are refused: what differs from a valid one, and the error.
BUDGET_REFUSED: list[tuple[dict[str, str | None], str]] = [
    ({"actor": "agent:implementer"}, "actor_not_human"),
    ({"reason": None}, "missing_fields"),
    ({"target": "rounds:+2"}, "invalid_target"),
    ({"target": "active:0"}, "invalid_target"),
    ({"target": "wallclock:30"}, "invalid_target"),
    ({"target": "ci_wait:abc"}, "invalid_target"),
]
# The fields a recorded decision may change in the state file.
DECISION_FIELDS = {"decisions", "transitions", "revision"}


def test_budget_extension_only_records_a_human_ruling(
    cli: Cli, home: Path, repo: Path, started_run: StartedRun
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    policy = (repo / "workflow.yaml").read_bytes()
    state_before = read_state(home)

    for n, target in enumerate(BUDGET_TARGETS, 1):
        r = cli(*decide_args("budget_extension", token, id=f"b-{n}", target=target))
        assert r.code == 0, (target, r)
    recorded = dig(read_state(home), "decisions") or {}
    assert sorted(recorded) == ["b-1", "b-2", "b-3", "b-4"]
    for n, target in enumerate(BUDGET_TARGETS, 1):
        record = recorded[f"b-{n}"]
        assert record["kind"] == "budget_extension", target
        assert record["target"] == target
        assert record["actor"] == FIELDS["actor"], target
        assert record["reason"] == FIELDS["reason"], target
    assert (repo / "workflow.yaml").read_bytes() == policy
    state = read_state(home)
    assert {name: state[name] for name in state if name not in DECISION_FIELDS} == {
        name: state_before[name] for name in state_before if name not in DECISION_FIELDS
    }

    revision = cli("status", *RUN).get("revision")
    assert revision == 6
    for change, error in BUDGET_REFUSED:
        r = cli(*decide_args("budget_extension", token, id="b-9", **change))
        assert r.get("result", "error") == error, change
        assert r.code == 1, change
        assert cli("status", *RUN).get("revision") == revision, change


LATER_KINDS = [
    "adopt",
    "delegate",
    "accept",
    "return",
    "resolve_read",
    "resolve_operation",
    "resolve_finding",
    "nonsense",
]


def test_adopt_delegate_and_later_kinds_are_unsupported(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    token = started_run(REPO, "F-1", "agent:implementer")
    before = snapshot(home)
    status_before = cli("status", *RUN)

    for command, argv in (("adopt", RUN), ("delegate", ["--to", "x"])):
        r = cli(command, *argv)
        assert r.get("result") == {"error": "unsupported", "command": command}
        assert r.code == 2, command
    for kind in LATER_KINDS:
        for given in (token, None):
            r = cli(*decide_args(kind, given))
            assert r.get("result") == {"error": "unsupported", "kind": kind}, (
                kind,
                given,
            )
            assert r.code == 2, (kind, given)

    assert snapshot(home) == before
    # Owner, approval and revision are all as they were.
    assert cli("status", *RUN).out == status_before.out
