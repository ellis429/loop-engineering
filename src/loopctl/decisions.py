"""register and decide: the checks and the records of native documents and
human decisions, all pure (D2, D9, D10).

The command line reads the request, the documents and the clock; these
functions see only the request, the time and the state, so the same request
always gives the same payload (D5)."""

from __future__ import annotations

import re
from typing import Any

from loopctl.next import superseded_by

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


# What a registration keeps besides the fields of every kind (D9); the
# other request fields are ignored.
OWN = {"plan": ("producer", "calibrated_from"), "binding": ("role",), "policy": ()}

# What a registration cannot do without (D2).
REGISTER_NEEDS = {"plan": ("producer",), "binding": ("role",)}

# The roles of the bindings an approval needs and pins with the plan (D10);
# never sa.
APPROVED_ROLES = ("spec", "ac", "design")


def registration(kind: str, fields: dict[str, Any]) -> dict[str, Any]:
    """The payload of `register <kind>`: the fields of its entry without the
    time (D5, D9), once its own fields are there. `path` is there only when
    the locator is a local file."""
    missing = [name for name in REGISTER_NEEDS.get(kind, ()) if not fields.get(name)]
    if missing:
        raise Rejected("missing_fields", fields=missing)
    payload = {
        "kind": kind,
        **{name: fields[name] for name in ("locator", "version", "source", "digest")},
    }
    if fields.get("path") is not None:
        payload["path"] = fields["path"]
    for name in OWN[kind]:
        payload[name] = fields.get(name)
    return payload


def registered(state: State, payload: dict[str, Any]) -> dict[str, Any] | None:
    """The entry at the place `payload` registers to: the one plan, the one
    policy, or the binding of its role and locator (D9)."""
    entry: dict[str, Any] | None
    if payload["kind"] == "plan":
        entry = state["plan"]
    elif payload["kind"] == "policy":
        entry = state["versions"]["policy"]
    else:
        role_bindings = state["versions"]["bindings"].get(payload["role"], {})
        entry = role_bindings.get(payload["locator"])
    return entry


def register(state: State, payload: dict[str, Any], at: str) -> State:
    """`state` with the registration of `payload` at `at`, in the order of
    D9: a change of what the approval covers needs scope_change first; a
    plan a scope_change superseded stays superseded; the same registration
    changes nothing; any other is written, or put in place of the one at
    the same place."""
    entry = {
        **{name: value for name, value in payload.items() if name != "kind"},
        "content": {"$object": payload["digest"]},
        "registered_at": at,
    }
    same = _comparable(registered(state, payload)) == _comparable(entry)
    covered = payload["kind"] == "plan" or payload.get("role") in APPROVED_ROLES
    if state["approval"] is not None and covered and not same:
        raise Rejected("scope_change_required")
    if payload["kind"] == "plan" and superseded_by({**state, "plan": entry}):
        raise Rejected("plan_superseded")
    if same:
        return state
    kind, versions = payload["kind"], state["versions"]
    if kind == "plan":
        return {**state, "plan": entry}
    if kind == "policy":
        return {**state, "versions": {**versions, "policy": entry}}
    bindings, role = versions["bindings"], payload["role"]
    role_bindings = {**bindings.get(role, {}), payload["locator"]: entry}
    return {
        **state,
        "versions": {**versions, "bindings": {**bindings, role: role_bindings}},
    }


def _comparable(entry: dict[str, Any] | None) -> dict[str, Any] | None:
    """An entry without what a re-registration may differ in and still be
    the same registration: its time and the derived `superseded_by` (D9)."""
    if entry is None:
        return None
    ignored = ("registered_at", "superseded_by")
    return {name: value for name, value in entry.items() if name not in ignored}


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
    effects: dict[str, Any] = {}
    if kind == "approve_plan":
        state = {**state, "approval": _approval(state, payload, at)}
    if kind == "scope_change":
        # The plan of this moment, also when a resolution takes it in (D6).
        effects["supersedes"] = _pin(_plan(state))
        state = {**state, "approval": None}
    if kind == "policy_change":
        state = {**state, "policy_approval": _policy_approval(state, payload)}
    return _record(state, payload, at, **effects)


def _policy_approval(state: State, payload: dict[str, Any]) -> State:
    """What policy_change approves (D10): the registered policy at its
    digest. An approved policy can be approved again; the latest decision
    takes the place of the earlier one."""
    policy = state["versions"]["policy"]
    if policy is None:
        raise Rejected("policy_not_registered")
    if (payload["target"], payload["version"]) != (policy["locator"], policy["digest"]):
        raise Rejected("policy_digest_mismatch")
    return {
        "decision": payload["id"],
        "locator": policy["locator"],
        "digest": policy["digest"],
    }


def _plan(state: State) -> dict[str, Any]:
    """The plan approve_plan and scope_change need (D10)."""
    plan: dict[str, Any] | None = state["plan"]
    if plan is None:
        raise Rejected("plan_not_registered")
    return plan


def _pin(plan: dict[str, Any]) -> dict[str, Any]:
    """How an approval, a scope_change and dispatch pin a plan (D9)."""
    return {name: plan[name] for name in ("locator", "version", "digest")}


def _approval(state: State, payload: dict[str, Any], at: str) -> State:
    """What approve_plan approves, once its checks pass in the order of D10:
    the plan and the digests of its bindings."""
    if state["approval"] is not None:
        raise Rejected("already_approved")
    plan = _plan(state)
    if plan["producer"] != "implementer" or not plan["calibrated_from"]:
        raise Rejected("plan_not_calibrated")
    if superseded_by(state):
        raise Rejected("plan_superseded")
    if (payload["target"], payload["version"]) != (plan["locator"], plan["version"]):
        raise Rejected("plan_version_mismatch")
    bindings = state["versions"]["bindings"]
    missing = [role for role in APPROVED_ROLES if not bindings.get(role)]
    if missing:
        raise Rejected("missing_bindings", roles=missing)
    return {
        "decision": payload["id"],
        "actor": payload["actor"],
        "at": at,
        "plan": _pin(plan),
        "bindings": {
            role: {locator: entry["digest"] for locator, entry in entries.items()}
            for role, entries in bindings.items()
            if role in APPROVED_ROLES
        },
    }


def _record(state: State, payload: dict[str, Any], at: str, **effects: Any) -> State:
    """`state` with the decision of `payload` in effect, with what its
    effects keep in its record."""
    recorded = state["decisions"]
    seq = 1 + max((record["seq"] for record in recorded.values()), default=0)
    record = {**payload, **effects, "at": at, "seq": seq, "status": "in_effect"}
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
    recorded, marked voided, and only the effects that still belong to it
    are cleared; no approval is ever restored. A voided scope_change no
    longer supersedes the plan (D7); the kinds that only record have no
    effect to clear."""
    record = {**state["decisions"][decision_id], "status": "voided", "voided_by": by}
    state = {**state, "decisions": {**state["decisions"], decision_id: record}}
    for field in ("approval", "policy_approval"):
        approved = state[field]
        if approved is not None and approved["decision"] == decision_id:
            state = {**state, field: None}
    return state
