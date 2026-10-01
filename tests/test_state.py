"""Durable run state: init, claim, status, next and the store (D3, D4, D11)."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import Result, Runs, dig

from loopctl import store

Cli = Callable[..., Result]
StartedRun = Callable[[str, str, str], str]

REPO = "yschiang/loop-engineering"
RUN = ["--repo", REPO, "--feature", "F-1"]
GATES = ["g1", "g2", "g3"]
UNCLAIMED_NEXT = {"action": "human", "blockers": ["unclaimed"], "decision_kinds": []}


def run_dir(home: Path, repo: str = REPO, feature: str = "F-1") -> Path:
    return home / "runs" / repo / feature


def read_state(home: Path, repo: str = REPO, feature: str = "F-1") -> Any:
    """feature.json of a run, or None when it is missing or not JSON."""
    try:
        return json.loads((run_dir(home, repo, feature) / "feature.json").read_text())
    except (OSError, ValueError):
        return None


def snapshot(root: Path) -> dict[str, bytes | None]:
    """Every path under `root` with its bytes (None for a directory)."""
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(root.rglob("*"))
    }


def history(home: Path) -> list[str]:
    return sorted(path.name for path in (run_dir(home) / "history").iterdir())


def test_init_creates_a_planning_run_per_repo_and_feature(
    cli: Cli, home: Path
) -> None:
    init = cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    assert init.code == 0
    st = cli("status", *RUN)
    assert st.get("result", "phase") == "planning"
    assert init.get("revision") == 1
    state = read_state(home)
    # No handoff record exists, and none is needed to start the run.
    assert not dig(state, "decisions")
    assert "handoff" not in json.dumps(state)

    assert st.code == 0
    for name, value in {"repo": REPO, "feature": "F-1", "issue": "29"}.items():
        assert st.get("result", name) == value, name
    assert st.get("result", "coordinator", "actor") == "agent:implementer"
    assert st.get("result", "owner") is None
    for gate in GATES:
        assert st.get("result", "gates", gate, "status") == "not_evaluated", gate
        assert st.get("result", "gates", gate, "reasons"), gate
    assert st.get("result", "blockers") == ["unclaimed"]
    assert st.get("next") == UNCLAIMED_NEXT

    assert dig(state, "coordinator", "actor") == "agent:implementer"
    assert dig(state, "phase") == "planning"
    assert dig(state, "owner") is None
    assert dig(state, "gates") == st.get("result", "gates")
    assert dig(state, "blockers") == ["unclaimed"]
    assert dig(state, "next") == UNCLAIMED_NEXT
    assert (run_dir(home) / "history" / "1.json").is_file()

    other = cli(
        "init", "--repo", "other/repo", "--feature", "F-1", "--issue", "7",
        "--actor", "agent:other",
    )
    assert other.code == 0
    assert other.get("revision") == 1
    assert dig(read_state(home, "other/repo"), "issue") == "7"
    assert dig(read_state(home), "issue") == "29"


def test_status_human_renders_the_same_view(cli: Cli) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    r = cli("status", *RUN, "--human")
    result = r.get("result") or {}
    assert "human" in result
    lines = str(result["human"]).splitlines()
    expected = {
        "phase": ["planning"],
        "coordinator": ["agent:implementer"],
        "owner": ["unclaimed"],
        **{gate: ["not_evaluated", "not_started"] for gate in GATES},
        "blockers": ["unclaimed"],
        "next": ["human", "unclaimed"],
    }
    for label, words in expected.items():
        found = [line for line in lines if line.startswith(label)]
        assert found, f"no {label} line in {lines}"
        assert all(word in found[0] for word in words), (label, found[0])
    assert r.code == 0
    assert result["phase"] == "planning"


@pytest.mark.parametrize(
    ("issue", "actor"),
    [
        pytest.param("29", "agent:implementer", id="same"),
        pytest.param("30", "agent:implementer", id="other-issue"),
        pytest.param("29", "agent:other", id="other-actor"),
    ],
)
def test_init_never_overwrites_an_existing_run(
    cli: Cli, home: Path, issue: str, actor: str
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    before = snapshot(run_dir(home))
    r = cli("init", *RUN, "--issue", issue, "--actor", actor)
    assert r.code == 1
    assert r.get("result", "error") == "run_exists"
    assert snapshot(run_dir(home)) == before


def test_claim_grants_the_coordination_right_once_and_stores_only_the_token_digest(
    cli: Cli, home: Path
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    coordinator = cli("status", *RUN).get("result", "coordinator")

    claim = cli("claim", *RUN, "--actor", "agent:implementer")
    assert claim.code == 0
    token = claim.get("result", "token")
    assert isinstance(token, str) and re.fullmatch(r"[0-9a-f]{64}", token)
    assert claim.get("revision") == 2

    st = cli("status", *RUN)
    assert st.get("result", "owner", "actor") == "agent:implementer"
    assert st.get("result", "coordinator") == coordinator

    digest = "sha256:" + hashlib.sha256(token.encode()).hexdigest()
    assert dig(read_state(home), "owner", "token_digest") == digest
    holding = [
        path for path, data in snapshot(run_dir(home)).items()
        if data is not None and token.encode() in data
    ]
    assert holding == []

    again = cli("claim", *RUN, "--actor", "agent:other")
    assert again.code == 1
    assert again.get("result") == {
        "error": "already_claimed",
        "owner": "agent:implementer",
    }


def test_uninitialised_run_is_not_found_and_nothing_is_created(
    cli: Cli, home: Path, started_run: StartedRun
) -> None:
    started_run(REPO, "F-2", "agent:implementer")
    before = snapshot(home)
    missing = ["--repo", REPO, "--feature", "F-9"]
    for argv in (
        ["status", *missing],
        ["next", *missing],
        ["claim", *missing, "--actor", "agent:implementer"],
    ):
        r = cli(*argv)
        assert r.code == 1, argv[0]
        assert r.get("result") == {"error": "run_not_found"}, argv[0]
    assert snapshot(home) == before


# Prelude of each claimer: a distinct actor, and the D13 gate before os.link.
# The gate lets a process link only when all n have arrived or 3 s passed,
# and appends what it saw at release to record.jsonl.
CLAIM_GATE = """\
import json as _gj, os as _go, sys as _gs, time as _gt
_gs.argv = ["agent:claimer-%d" % _go.getpid() if _a == "ACTOR" else _a
            for _a in _gs.argv]
_gate_dir, _gate_n, _gate_link = {gate!r}, {n}, _go.link

def _gate_arrived():
    return sum(_f.startswith("arrived-") for _f in _go.listdir(_gate_dir))

def _gated_link(*args, **kwargs):
    open(_go.path.join(_gate_dir, "arrived-%d" % _go.getpid()), "w").close()
    _deadline, _reason = _gt.monotonic() + 3, "timeout"
    while _gt.monotonic() < _deadline:
        if _gate_arrived() >= _gate_n:
            _reason = "all_arrived"
            break
        _gt.sleep(0.002)
    with open(_go.path.join(_gate_dir, "record.jsonl"), "a") as _record:
        _record.write(_gj.dumps(
            {{"pid": _go.getpid(), "arrived": _gate_arrived(), "reason": _reason}}
        ) + "\\n")
    return _gate_link(*args, **kwargs)

_go.link = _gated_link
"""


def test_concurrent_claims_leave_one_owner_and_a_controlled_answer_for_every_loser(
    cli: Cli, home: Path, tmp_path: Path, cli_proc_many: Callable[..., Runs]
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    gate = tmp_path / "gate"
    gate.mkdir()
    runs = cli_proc_many(
        8, "claim", *RUN, "--actor", "ACTOR",
        prelude=CLAIM_GATE.format(gate=str(gate), n=8),
    )
    log = gate / "record.jsonl"
    print("gate record:", log.read_text() if log.exists() else "(no arrival)")
    print("barrier:", runs.barrier)

    winners = [r for r in runs if r.code == 0]
    assert len(winners) == 1, [(r.code, r.exc) for r in runs]
    winner = winners[0].get("result", "owner", "actor")
    losers = [r for r in runs if r is not winners[0]]
    assert len(losers) == 7
    for loser in losers:
        assert loser.get("result") == {"error": "already_claimed", "owner": winner}, (
            loser.code,
            loser.exc,
        )
        assert loser.code == 1
        assert loser.exc is None

    st = cli("status", *RUN)
    assert st.code == 0
    assert st.get("revision") == 2
    assert st.get("result", "owner", "actor") == winner
    assert history(home) == ["1.json", "2.json"]


CRASH_ON_REPLACE = "import os; os.replace = lambda *a, **k: os._exit(9)"
CRASH_ON_LINK = "import os; os.link = lambda *a, **k: os._exit(9)"


def test_interrupt_after_history_keeps_the_new_revision_once(
    cli: Cli, cli_proc: Cli, home: Path
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    crashed = cli_proc("claim", *RUN, "--actor", "agent:a", prelude=CRASH_ON_REPLACE)
    assert crashed.code == 9

    before = snapshot(run_dir(home))
    st = cli("status", *RUN)
    assert st.get("revision") == 2
    assert st.code == 0
    assert st.get("result", "owner", "actor") == "agent:a"
    again = cli("claim", *RUN, "--actor", "agent:b")
    assert again.get("result") == {"error": "already_claimed", "owner": "agent:a"}
    assert snapshot(run_dir(home)) == before
    assert history(home) == ["1.json", "2.json"]


def test_interrupt_before_history_keeps_the_old_revision(
    cli: Cli, cli_proc: Cli
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    crashed = cli_proc("claim", *RUN, "--actor", "agent:a", prelude=CRASH_ON_LINK)
    assert crashed.code == 9

    st = cli("status", *RUN)
    assert st.get("revision") == 1
    assert st.code == 0
    assert st.get("result", "owner") is None
    again = cli("claim", *RUN, "--actor", "agent:b")
    assert again.code == 0
    assert again.get("revision") == 2


# The first os.fsync of the process fails; by D4 step 8 that is the sync of
# the history temporary file, before os.link.
FAIL_FIRST_FSYNC = """\
import errno as _fe, os as _fo
_fsync, _fsync_calls = _fo.fsync, []

def _failing_fsync(fd):
    _fsync_calls.append(fd)
    if len(_fsync_calls) == 1:
        raise OSError(_fe.EIO, "injected EIO")
    return _fsync(fd)

_fo.fsync = _failing_fsync
"""


def test_a_failed_sync_before_the_link_commits_nothing(
    cli: Cli, cli_proc: Cli, home: Path
) -> None:
    cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
    failed = cli_proc("claim", *RUN, "--actor", "agent:a", prelude=FAIL_FIRST_FSYNC)
    assert failed.code != 0
    st = cli("status", *RUN)
    assert st.get("revision") == 1
    assert st.get("result", "owner") is None
    assert history(home) == ["1.json"]


KEY = (REPO, "F-1")


def unchecked(state: dict[str, Any]) -> None:
    """An `authorize` that lets every caller through."""


def test_commit_with_a_stale_revision_writes_nothing(
    home: Path, started_run: StartedRun
) -> None:
    started_run(REPO, "F-1", "agent:implementer")
    assert store.load(KEY)[0] == 2
    before = snapshot(run_dir(home))
    with pytest.raises(store.RevisionConflict):
        store.commit(
            KEY, 1, "t-x", {"issue": "30"},
            lambda state: {**state, "issue": "30"},
            authorize=unchecked,
        )
    assert snapshot(run_dir(home)) == before


def commit_field(name: str, value: Any, transition_id: str) -> int:
    """Commit one top-level field through store.commit at the current revision."""
    revision, _ = store.load(KEY)
    return store.commit(
        KEY, revision, transition_id, {name: value},
        lambda state: {**state, name: value},
        authorize=unchecked,
    )


NEVER_STORED = "sha256:" + hashlib.sha256(b"never stored\n").hexdigest()


@pytest.mark.parametrize("case", ["missing", "deleted", "corrupt", "plain-digest"])
def test_commit_rejects_missing_or_corrupt_object_references(
    home: Path, started_run: StartedRun, case: str
) -> None:
    started_run(REPO, "F-1", "agent:implementer")
    if case == "plain-digest":
        # A sha256: string field is not a reference and commits as usual.
        assert commit_field("digest", NEVER_STORED, "t-plain") == 3
        assert dig(read_state(home), "digest") == NEVER_STORED
        return
    if case == "missing":
        ref, reason = NEVER_STORED, f"object_missing:{NEVER_STORED}"
        name, value = "probe", {"$object": NEVER_STORED}
    else:
        ref = store.put_object(b"registered content\n")
        assert commit_field("probe", {"$object": ref}, "t-ref") == 3
        stored = home / "objects" / ref.removeprefix("sha256:")
        if case == "deleted":
            stored.unlink()
            reason = f"object_missing:{ref}"
        else:
            stored.write_bytes(b"changed content\n")
            reason = f"object_corrupt:{ref}"
        name, value = "issue", "30"
    before = snapshot(run_dir(home))
    with pytest.raises(store.UntrustedState) as raised:
        commit_field(name, value, "t-check")
    assert raised.value.reason == reason
    assert snapshot(run_dir(home)) == before


# The first os.fsync after a call of os.<call> fails with EIO: in claim the
# sync of the history directory after os.link, in init the sync of the parent
# directory after os.rename (D2: both after the commit boundary).
FAIL_FSYNC_AFTER = """\
import errno as _fe, os as _fo
_fsync, _call, _armed = _fo.fsync, _fo.{call}, []

def _arming_call(*args, **kwargs):
    _done = _call(*args, **kwargs)
    _armed.append(True)
    return _done

def _failing_fsync(fd):
    if _armed:
        _fo.fsync = _fsync
        raise OSError(_fe.EIO, "injected EIO")
    return _fsync(fd)

_fo.{call}, _fo.fsync = _arming_call, _failing_fsync
"""


@pytest.mark.parametrize(
    ("case", "prelude", "committed"),
    [
        pytest.param("claim", FAIL_FIRST_FSYNC, False, id="a-claim-before-link"),
        pytest.param(
            "claim", FAIL_FSYNC_AFTER.format(call="link"), True,
            id="b-claim-after-link",
        ),
        pytest.param("init", FAIL_FIRST_FSYNC, False, id="c-init-before-rename"),
        pytest.param(
            "init", FAIL_FSYNC_AFTER.format(call="rename"), True,
            id="d-init-after-rename",
        ),
    ],
)
def test_io_errors_print_an_envelope_and_say_whether_the_change_committed(
    cli: Cli, cli_proc: Cli, home: Path, case: str, prelude: str, committed: bool
) -> None:
    if case == "claim":
        cli("init", *RUN, "--issue", "29", "--actor", "agent:implementer")
        failed = cli_proc("claim", *RUN, "--actor", "agent:a", prelude=prelude)
    else:
        failed = cli_proc(
            "init", *RUN, "--issue", "29", "--actor", "agent:implementer",
            prelude=prelude,
        )
    assert failed.code == 6, failed
    assert len(failed.stdout.splitlines()) == 1 and failed.out is not None
    assert failed.get("result", "error") == "io_error"
    assert {"op", "errno"} <= set(failed.get("result") or {})
    assert failed.get("result", "committed") is committed

    st = cli("status", *RUN)
    if case == "claim" and not committed:
        assert st.get("revision") == 1
        assert st.get("result", "owner") is None
    elif case == "claim":
        assert st.get("revision") == 2
        assert st.get("result", "owner", "actor") == "agent:a"
        before = snapshot(run_dir(home))
        again = cli("claim", *RUN, "--actor", "agent:b")
        assert again.code == 1
        assert again.get("result") == {"error": "already_claimed", "owner": "agent:a"}
        assert cli("status", *RUN).get("revision") == 2
        assert snapshot(run_dir(home)) == before
    elif not committed:
        assert not run_dir(home).exists()
        assert st.get("result") == {"error": "run_not_found"}
    else:
        assert st.get("revision") == 1


def write_state(home: Path, state: Any) -> None:
    """Write feature.json the way the store does, outside the store."""
    text = json.dumps(state, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    (run_dir(home) / "feature.json").write_text(text)


def break_run(home: Path, case: str) -> None:
    run = run_dir(home)
    if case == "state-missing":
        (run / "feature.json").unlink()
    elif case == "state-corrupt":
        (run / "feature.json").write_text('{"schema_version": 1, "revision": ')
    elif case == "unknown-schema":
        write_state(home, {**read_state(home), "schema_version": 9})
    elif case == "history-missing":
        (run / "history" / "2.json").unlink()
    elif case == "empty-run-dir":
        shutil.rmtree(run)
        run.mkdir()


def files_of(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    )


EVERY_COMMAND = [
    ["status", *RUN],
    ["next", *RUN],
    ["claim", *RUN, "--actor", "agent:other"],
    ["init", *RUN, "--issue", "29", "--actor", "agent:other"],
]


@pytest.mark.parametrize(
    ("case", "reason"),
    [
        ("state-missing", "state_missing"),
        ("state-corrupt", "state_corrupt"),
        ("unknown-schema", "unknown_schema:9"),
        ("history-missing", "history_missing:2"),
        ("empty-run-dir", "state_missing"),
    ],
)
def test_untrusted_state_stops_with_reason_and_files(
    cli: Cli, home: Path, started_run: StartedRun, case: str, reason: str
) -> None:
    started_run(REPO, "F-1", "agent:implementer")
    break_run(home, case)
    files = files_of(run_dir(home))
    before = snapshot(home)
    for argv in EVERY_COMMAND:
        r = cli(*argv)
        assert r.code == 5, (argv[0], r)
        assert r.get("result", "error") == "untrusted_state", argv[0]
        assert r.get("result", "reason") == reason, argv[0]
        assert r.get("result", "files") == files, argv[0]
    assert snapshot(home) == before


def edit_by_hand(state: dict[str, Any], case: str) -> None:
    if case == "gate-passed":
        state["gates"]["g1"]["status"] = "passed"
    elif case == "phase-approved":
        state["phase"] = "approved"
    elif case == "owner-changed":
        state["owner"] = {
            **state["owner"],
            "actor": "agent:intruder",
            "token_digest": "sha256:" + hashlib.sha256(b"mine").hexdigest(),
        }
    elif case == "decision-inserted":
        state["decisions"]["d-1"] = {"kind": "approve_plan", "actor": "human:x"}


@pytest.mark.parametrize(
    "case", ["gate-passed", "phase-approved", "owner-changed", "decision-inserted"]
)
def test_manual_edit_is_detected_and_never_trusted(
    cli: Cli, home: Path, started_run: StartedRun, case: str
) -> None:
    started_run(REPO, "F-1", "agent:implementer")
    state = read_state(home)
    edit_by_hand(state, case)
    write_state(home, state)
    before = snapshot(run_dir(home))
    for argv in EVERY_COMMAND[:3]:
        r = cli(*argv)
        assert r.code == 5, (argv[0], r)
        assert r.get("result", "reason") == "manual_edit", argv[0]
        assert "passed" not in r.stdout and "approved" not in r.stdout, argv[0]
    assert snapshot(run_dir(home)) == before
