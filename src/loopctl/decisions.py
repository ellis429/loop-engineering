"""decide: the checks and the record of a human decision, all pure (D2, D10).

The command line reads the request and the clock; these functions see only
the request, the time and the state, so the same request always gives the
same payload (D5)."""

from __future__ import annotations

import re
from typing import Any

State = dict[str, Any]

# The kinds of this version (D10); any other kind is unsupported.
KINDS = (
    "approve_plan",
    "scope_change",
    "policy_change",
    "budget_extension",
    "revise",
    "handoff",
    "resolve_conflict",
)

# The fields every decision records (D10).
COMMON = ("id", "actor", "target", "reason", "source", "impact")

# What a kind needs besides the common fields (D10).
NEEDS = {
    "approve_plan": ("version",),
    "policy_change": ("version",),
    "resolve_conflict": ("choice",),
}

# What resolve_conflict can choose (D6).
CHOICES = ("original", "attempted", "abandon")

# Only a person decides: `human:<name>`, the name a single segment.
HUMAN = re.compile(r"human:[A-Za-z0-9][A-Za-z0-9._-]*")

# The one target a budget_extension extends (D10): active minutes, one more
# round, one more attempt of a unit, or a new CI wait for a head SHA.
BUDGET_TARGET = re.compile(
    r"active:[1-9][0-9]*"
    r"|rounds:\+1"
    r"|attempts:[A-Za-z0-9][A-Za-z0-9._-]*:\+1"
    r"|ci_wait:[0-9a-f]{40}"
)


class Unsupported(Exception):
    """A kind this version does not have: exit 2, the state never read."""

    def __init__(self, kind: str) -> None:
        super().__init__(kind)
        self.kind = kind


class Rejected(Exception):
    """A request the checks refuse: exit 1 with `error` and its `fields`."""

    def __init__(self, error: str, **fields: Any) -> None:
        super().__init__(error)
        self.error = error
        self.fields = fields


def request(kind: str, fields: dict[str, Any]) -> dict[str, Any]:
    """The payload of a decision: the request fields it records, without the
    time or the token (D5), once the checks that need no state pass (D2).

    A field that is missing or empty is reported missing."""
    if kind not in KINDS:
        raise Unsupported(kind)
    needed = (*COMMON, *NEEDS.get(kind, ()))
    missing = [name for name in needed if not fields.get(name)]
    if missing:
        raise Rejected("missing_fields", fields=missing)
    if not HUMAN.fullmatch(fields["actor"]):
        raise Rejected("actor_not_human")
    payload = {"kind": kind, **{name: fields[name] for name in COMMON}}
    if fields.get("version"):
        payload["version"] = fields["version"]
    if kind == "resolve_conflict":
        payload["choice"] = fields["choice"]
    if kind == "scope_change":
        payload["open_questions"] = list(fields.get("open_questions") or [])
    return payload


def decide(state: State, payload: dict[str, Any], at: str) -> State:
    """`state` with the decision of `payload` recorded at `at`, once the
    kind's own checks pass (D10). The other kinds only record here."""
    kind = payload["kind"]
    if kind == "budget_extension" and not BUDGET_TARGET.fullmatch(payload["target"]):
        raise Rejected("invalid_target")
    if kind == "resolve_conflict":
        return _resolve(state, payload, at)
    return _record(state, payload, at)


def _record(state: State, payload: dict[str, Any], at: str) -> State:
    recorded = state["decisions"]
    seq = 1 + max((record["seq"] for record in recorded.values()), default=0)
    record = {**payload, "at": at, "seq": seq, "status": "in_effect"}
    return {**state, "decisions": {**recorded, payload["id"]: record}}


def _resolve(state: State, payload: dict[str, Any], at: str) -> State:
    """resolve_conflict (D6): keep the committed decision C, take the
    attempted content A in its place, or abandon C. The store checks that
    the target is unresolved and records the resolution on it."""
    choice = payload["choice"]
    if choice not in CHOICES:
        raise Rejected("invalid_choice")
    conflict = state["conflicts"][payload["target"]]
    committed, attempted = conflict["committed_payload"], conflict["attempted_payload"]
    # A resolution is never undone, nor taken in as another one's content.
    if (committed["kind"] == "resolve_conflict" and choice != "original") or (
        attempted["kind"] == "resolve_conflict" and choice == "attempted"
    ):
        raise Rejected("choice_not_allowed")
    state = _record(state, payload, at)
    if choice == "original":
        return state
    state = void(state, committed["id"], payload["id"])
    if choice == "abandon":
        return state
    # A is checked as decision C's id on the state without C; if its checks
    # fail, the whole resolution is refused.
    replaced = state["decisions"][committed["id"]]
    state = decide(state, attempted, at)
    record = {
        **state["decisions"][committed["id"]],
        "replaces": [
            {name: value for name, value in replaced.items() if name != "replaces"},
            *replaced.get("replaces", []),
        ],
    }
    return {**state, "decisions": {**state["decisions"], committed["id"]: record}}


def void(state: State, decision_id: str, by: str) -> State:
    """Undo decision `decision_id` for the decision `by` (D10): it stays
    recorded, marked voided. The kinds that only record have no effect to
    clear."""
    record = {**state["decisions"][decision_id], "status": "voided", "voided_by": by}
    return {**state, "decisions": {**state["decisions"], decision_id: record}}
