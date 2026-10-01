"""loopctl command line: parse, dispatch, print one JSON envelope (D2)."""

from __future__ import annotations

import argparse
import errno
import json
import re
import secrets
import sys
from collections.abc import Callable
from typing import Any, NoReturn

from loopctl import clock, state, store

Envelope = dict[str, Any]
Handler = Callable[[argparse.Namespace], tuple[int, Envelope]]

EXIT_USAGE = 2


def envelope(
    ok: bool,
    result: dict[str, Any],
    *,
    revision: int | None = None,
    blocked: Any = None,
    next: Any = None,
) -> Envelope:
    """The one output shape of every command; `safety` is always null here."""
    return {
        "ok": ok,
        "revision": revision,
        "result": result,
        "blocked": blocked,
        "next": next,
        "safety": None,
    }


def stub(args: argparse.Namespace) -> tuple[int, Envelope]:
    """Placeholder until the command's task replaces it: right shape, no
    content, writes nothing."""
    return 0, envelope(True, {})


def _key(args: argparse.Namespace) -> store.Key:
    return args.repo, args.feature


def refusal(code: int, error: str, **fields: Any) -> tuple[int, Envelope]:
    return code, envelope(False, {"error": error, **fields})


def guarded(handler: Handler) -> Handler:
    """Turn the refusals of the store and of a state check, and the I/O
    errors of the store, into envelopes."""

    def run(args: argparse.Namespace) -> tuple[int, Envelope]:
        try:
            return handler(args)
        except store.IOFailure as error:
            return refusal(
                6,
                "io_error",
                op=error.op,
                errno=errno.errorcode.get(error.errno) if error.errno else None,
                committed=error.committed,
            )
        except store.RunNotFound:
            return refusal(1, "run_not_found")
        except store.RunExists:
            return refusal(1, "run_exists")
        except store.UntrustedState as error:
            return refusal(
                5, "untrusted_state", reason=error.reason, files=error.files
            )
        except state.AlreadyClaimed as error:
            return refusal(1, "already_claimed", owner=error.owner)

    return run


def init(args: argparse.Namespace) -> tuple[int, Envelope]:
    # An existing run, trusted or not, is never overwritten or recreated.
    try:
        store.load(_key(args))
    except store.RunNotFound:
        pass
    else:
        return refusal(1, "run_exists")
    payload = {
        "repo": args.repo,
        "feature": args.feature,
        "issue": args.issue,
        "actor": args.actor,
    }
    initial = state.initial(
        args.repo, args.feature, args.issue, args.actor, clock.now()
    )
    revision = store.create(_key(args), "init", payload, initial)
    result = {"coordinator": initial["coordinator"]}
    return 0, envelope(True, result, revision=revision)


def unchecked(st: store.State) -> None:
    """`authorize` for claim: its own check (no owner yet) is in mutate."""


def claim(args: argparse.Namespace) -> tuple[int, Envelope]:
    key = _key(args)
    token = secrets.token_hex(32)
    owner = {
        "actor": args.actor,
        "token_digest": state.token_digest(token),
        "claimed_at": clock.now(),
    }
    while True:
        expected, _ = store.load(key)
        try:
            revision = store.commit(
                key,
                expected,
                f"claim:{owner['token_digest']}",
                {"actor": args.actor},
                lambda st: state.claim(st, owner),
                authorize=unchecked,
            )
            break
        except store.RevisionConflict:
            continue  # another transition went first: re-read and redo
    result = {"token": token, "owner": state.owner_view(owner)}
    return 0, envelope(True, result, revision=revision)


def status(args: argparse.Namespace) -> tuple[int, Envelope]:
    revision, st = store.load(_key(args))
    result = state.view(revision, st)
    if args.human:
        result["human"] = state.human(result, st["next"])
    return 0, envelope(True, result, revision=revision, next=st["next"])


def next_step(args: argparse.Namespace) -> tuple[int, Envelope]:
    revision, st = store.load(_key(args))
    result = {"phase": st["phase"], "blockers": st["blockers"]}
    return 0, envelope(True, result, revision=revision, next=st["next"])


HANDLERS: dict[str, Handler] = {
    "init": guarded(init),
    "claim": guarded(claim),
    "status": guarded(status),
    "next": guarded(next_step),
    "register": stub,
    "decide": stub,
    "adopt": stub,
    "delegate": stub,
}


class UsageError(Exception):
    """A command line the parser rejects; reported as exit 2 `usage`."""


class HelpExit(Exception):
    """`--help` was printed; main returns `status`."""

    def __init__(self, status: int) -> None:
        super().__init__(status)
        self.status = status


class Parser(argparse.ArgumentParser):
    """argparse that raises instead of writing to stderr and exiting."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> NoReturn:
        raise UsageError(message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        raise HelpExit(status)


SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def repo_name(value: str) -> str:
    parts = value.split("/")
    if len(parts) != 2 or not all(SEGMENT.fullmatch(part) for part in parts):
        raise argparse.ArgumentTypeError(f"expected owner/name, got {value!r}")
    return value


def feature_id(value: str) -> str:
    if not SEGMENT.fullmatch(value):
        raise argparse.ArgumentTypeError(
            f"expected a single path segment, got {value!r}"
        )
    return value


def _run_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", required=True, type=repo_name, help="owner/name")
    parser.add_argument("--feature", required=True, type=feature_id)


def build_parser() -> Parser:
    parser = Parser(
        prog="loopctl",
        description="Durable run state and human decisions for one repo and feature.",
    )
    commands = parser.add_subparsers(dest="command", metavar="command", required=True)

    init = commands.add_parser("init", help="start a run for a repo and feature")
    _run_options(init)
    init.add_argument("--issue", required=True)
    init.add_argument("--actor", required=True)

    claim = commands.add_parser("claim", help="take the coordination right")
    _run_options(claim)
    claim.add_argument("--actor", required=True)

    status = commands.add_parser("status", help="show the run state")
    _run_options(status)
    status.add_argument("--human", action="store_true")

    nxt = commands.add_parser("next", help="show the one allowed next step")
    _run_options(nxt)

    register = commands.add_parser("register", help="register a native document")
    register.add_argument("kind", choices=["plan", "binding", "policy"])
    _run_options(register)
    register.add_argument("--token")
    register.add_argument("--locator", required=True)
    register.add_argument("--version", required=True)
    register.add_argument("--source", required=True)
    register.add_argument("--content-from")
    register.add_argument("--role", choices=["spec", "ac", "design", "sa"])
    register.add_argument("--producer", choices=["implementer", "project_lead"])
    register.add_argument("--calibrated-from")

    decide = commands.add_parser("decide", help="record a human decision")
    decide.add_argument("kind")
    _run_options(decide)
    decide.add_argument("--token")
    decide.add_argument("--id")
    decide.add_argument("--actor")
    decide.add_argument("--target")
    decide.add_argument("--reason")
    decide.add_argument("--source")
    decide.add_argument("--impact")
    decide.add_argument("--version")
    decide.add_argument("--choice")
    decide.add_argument("--open-question", action="append")

    commands.add_parser("adopt", help="unsupported in this version")
    commands.add_parser("delegate", help="unsupported in this version")
    return parser


PASSTHROUGH = ("adopt", "delegate")
HELP = {"-h", "--help"}


def parse(argv: list[str]) -> argparse.Namespace:
    """Parse argv; `adopt` and `delegate` keep every other argument in `rest`.

    Their tail never reaches argparse, which would read `-host` as `-h` and
    reject `--help=foo`; only an exact `-h` or `--help` prints their usage.
    """
    parser = build_parser()
    if argv and argv[0] in PASSTHROUGH:
        command, rest = argv[0], argv[1:]
        if HELP.intersection(rest):
            parser.parse_args([command, "--help"])  # raises HelpExit
        return argparse.Namespace(command=command, rest=rest)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse(sys.argv[1:] if argv is None else argv)
    except HelpExit as done:
        return done.status
    except UsageError as error:
        code = EXIT_USAGE
        out = envelope(False, {"error": "usage", "message": str(error)})
    else:
        code, out = HANDLERS[args.command](args)
    print(json.dumps(out, ensure_ascii=False))
    return code
