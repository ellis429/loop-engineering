"""The loopctl entry point, its dispatch and its JSON envelope (D2, D13)."""

from __future__ import annotations

import argparse
import re
from collections.abc import Callable

import pytest
from conftest import Result, Runs

from loopctl import cli as loopctl_cli

Cli = Callable[..., Result]

COMMANDS = [
    "init",
    "claim",
    "status",
    "next",
    "register",
    "decide",
    "adopt",
    "delegate",
]


def test_help_lists_every_command(cli: Cli) -> None:
    r = cli("--help")
    assert r.code == 0
    assert r.stdout.startswith("usage: loopctl")
    words = set(re.findall(r"[a-z]+", r.stdout))
    assert [c for c in COMMANDS if c not in words] == []


RUN = ["--repo", "a/b", "--feature", "F-1"]
RUN_FIELDS = {"repo": "a/b", "feature": "F-1"}
FAKE_ENVELOPE = {
    "ok": False,
    "revision": 3,
    "result": {"fake": True},
    "blocked": None,
    "next": None,
    "safety": None,
}


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        pytest.param(
            ["init", *RUN, "--issue", "X", "--actor", "agent:impl"],
            {**RUN_FIELDS, "command": "init", "issue": "X", "actor": "agent:impl"},
            id="init",
        ),
        pytest.param(
            ["claim", *RUN, "--actor", "agent:impl"],
            {**RUN_FIELDS, "command": "claim", "actor": "agent:impl"},
            id="claim",
        ),
        pytest.param(
            ["status", *RUN, "--human"],
            {**RUN_FIELDS, "command": "status", "human": True},
            id="status",
        ),
        pytest.param(
            ["next", *RUN],
            {**RUN_FIELDS, "command": "next"},
            id="next",
        ),
        pytest.param(
            ["register", "binding", *RUN, "--token", "T", "--locator", "L"]
            + ["--version", "V", "--source", "S", "--content-from", "P"]
            + ["--role", "spec", "--producer", "implementer"]
            + ["--calibrated-from", "C"],
            {
                **RUN_FIELDS,
                "command": "register",
                "kind": "binding",
                "token": "T",
                "locator": "L",
                "version": "V",
                "source": "S",
                "content_from": "P",
                "role": "spec",
                "producer": "implementer",
                "calibrated_from": "C",
            },
            id="register",
        ),
        pytest.param(
            ["decide", "revise", *RUN, "--token", "T", "--id", "d-1"]
            + ["--actor", "human:alice", "--target", "t", "--reason", "r"]
            + ["--source", "s", "--impact", "i", "--version", "v"]
            + ["--choice", "original"]
            + ["--open-question", "q1", "--open-question", "q2"],
            {
                **RUN_FIELDS,
                "command": "decide",
                "kind": "revise",
                "token": "T",
                "id": "d-1",
                "actor": "human:alice",
                "target": "t",
                "reason": "r",
                "source": "s",
                "impact": "i",
                "version": "v",
                "choice": "original",
                "open_question": ["q1", "q2"],
            },
            id="decide",
        ),
        pytest.param(
            ["adopt", "--anything", "x"],
            {"rest": ["--anything", "x"], "command": "adopt"},
            id="adopt",
        ),
        pytest.param(
            ["delegate", "--to", "x"],
            {"rest": ["--to", "x"], "command": "delegate"},
            id="delegate",
        ),
    ],
)
def test_parsed_arguments_reach_the_handler_and_its_envelope_is_printed(
    cli: Cli,
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    expected: dict[str, object],
) -> None:
    calls: list[argparse.Namespace] = []

    def fake(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
        calls.append(args)
        return 7, FAKE_ENVELOPE

    monkeypatch.setitem(loopctl_cli.HANDLERS, argv[0], fake)
    r = cli(*argv)
    received = calls[0] if calls else None
    for name, value in expected.items():
        assert getattr(received, name, None) == value, f"received.{name}"
    assert len(calls) == 1
    assert r.code == 7
    assert r.stdout.endswith("\n") and r.stdout.count("\n") == 1
    assert r.out == FAKE_ENVELOPE


@pytest.mark.parametrize("command", ["adopt", "delegate"])
@pytest.mark.parametrize(
    "rest",
    [
        pytest.param(["-host", "example.com"], id="short-h-prefix"),
        pytest.param(["--help=foo"], id="help-with-value"),
        pytest.param(["--to", "x", "-hx"], id="h-cluster-after-option"),
    ],
)
def test_adopt_and_delegate_keep_arguments_that_start_with_h(
    cli: Cli,
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    rest: list[str],
) -> None:
    calls: list[argparse.Namespace] = []

    def fake(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
        calls.append(args)
        return 7, FAKE_ENVELOPE

    monkeypatch.setitem(loopctl_cli.HANDLERS, command, fake)
    r = cli(command, *rest)
    assert len(calls) == 1, "handler called once"
    assert calls[0].command == command
    assert calls[0].rest == rest
    assert r.code == 7
    assert r.stdout.endswith("\n") and r.stdout.count("\n") == 1
    assert r.out == FAKE_ENVELOPE


@pytest.mark.parametrize("command", ["adopt", "delegate"])
@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_adopt_and_delegate_explicit_help_prints_usage(
    cli: Cli, monkeypatch: pytest.MonkeyPatch, command: str, flag: str
) -> None:
    calls: list[argparse.Namespace] = []

    def fake(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
        calls.append(args)
        return 7, FAKE_ENVELOPE

    monkeypatch.setitem(loopctl_cli.HANDLERS, command, fake)
    r = cli(command, flag)
    assert r.code == 0
    assert r.stdout.startswith(f"usage: loopctl {command}")
    assert calls == []


ENVELOPE_KEYS = ["ok", "revision", "result", "blocked", "next", "safety"]


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(
            ["init", *RUN, "--issue", "29", "--actor", "agent:impl"], id="init"
        ),
        pytest.param(["claim", *RUN, "--actor", "agent:impl"], id="claim"),
        pytest.param(["status", *RUN], id="status"),
        pytest.param(["next", *RUN], id="next"),
        pytest.param(
            ["register", "plan", *RUN, "--locator", "tasks.md"]
            + ["--version", "v1", "--source", "s"],
            id="register",
        ),
        pytest.param(["decide", "revise", *RUN], id="decide"),
        pytest.param(["adopt"], id="adopt"),
        pytest.param(["delegate"], id="delegate"),
    ],
)
def test_each_command_prints_one_json_envelope(cli: Cli, argv: list[str]) -> None:
    r = cli(*argv)
    assert r.stdout.endswith("\n") and r.stdout.count("\n") == 1, r
    assert sorted(r.out or {}) == sorted(ENVELOPE_KEYS)
    assert r.stderr == ""


@pytest.mark.parametrize(
    ("argv", "names"),
    [
        pytest.param([], "command", id="no-command"),
        pytest.param(["merge"], "merge", id="unknown-command"),
        pytest.param(["init", *RUN, "--issue", "29"], "--actor", id="init-no-actor"),
        pytest.param(
            ["register", "other", *RUN, "--locator", "L", "--version", "V"]
            + ["--source", "S"],
            "other",
            id="register-other",
        ),
        pytest.param(
            ["status", "--repo", "noslash", "--feature", "F-1"],
            "--repo",
            id="repo-noslash",
        ),
        pytest.param(
            ["status", "--repo", "../x", "--feature", "F-1"],
            "--repo",
            id="repo-dotdot",
        ),
        pytest.param(
            ["status", "--repo", "a/b", "--feature", "a/b"],
            "--feature",
            id="feature-with-slash",
        ),
    ],
)
def test_usage_errors_are_json_envelopes_with_exit_2(
    cli: Cli, argv: list[str], names: str
) -> None:
    r = cli(*argv)
    assert r.get("result", "error") == "usage"
    assert r.code == 2
    assert r.get("ok") is False
    assert names in (r.get("result", "message") or "")
    assert "usage:" not in r.stderr


def test_python_m_loopctl_matches_the_in_process_entry(
    cli: Cli, cli_proc: Cli, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Same help width in both, whatever the terminal is.
    monkeypatch.setenv("COLUMNS", "100")
    for argv in (
        ["--help"],
        ["merge"],
        ["status", "--repo", "a/b", "--feature", "F-1"],
    ):
        inproc, proc = cli(*argv), cli_proc(*argv)
        assert proc.code == inproc.code, argv
        assert proc.stdout == inproc.stdout, argv


def test_cli_proc_runs_the_prelude_first_and_starts_processes_together(
    cli_proc: Cli, cli_proc_many: Callable[..., Runs]
) -> None:
    # (a) The prelude runs before loopctl: exiting there leaves no output.
    early = cli_proc("--help", prelude="import os; os._exit(9)")
    assert early.code == 9
    assert early.stdout == ""

    # (b) The barrier file is created only after all 4 processes are ready.
    runs = cli_proc_many(4, "--help")
    assert [r.code for r in runs] == [0, 0, 0, 0]
    assert all("usage: loopctl" in r.stdout for r in runs)
    assert runs.barrier.get("ready_at_release") == 4
    assert runs.barrier.get("released_ns", -1) >= max(
        runs.barrier.get("ready_ns") or [float("inf")]
    )
