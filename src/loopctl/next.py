"""derive(state): the derived fields phase, blockers and next (D7)."""

from __future__ import annotations

from typing import Any

State = dict[str, Any]


def derive(state: State) -> State:
    """`state` with phase, blockers and next recomputed from its other fields."""
    nxt = _next(state)
    return {**state, "phase": _phase(state), "blockers": nxt["blockers"], "next": nxt}


def unresolved(state: State) -> list[str]:
    """The conflicts no human has resolved yet, by cid (D6)."""
    return sorted(
        cid
        for cid, conflict in (state.get("conflicts") or {}).items()
        if conflict.get("resolved_by") is None
    )


def _phase(state: State) -> str:
    if state.get("approval"):
        return "approved"
    if state.get("plan"):
        return "awaiting_approval"
    return "planning"


def _human(blockers: list[str], kinds: list[str] | None = None) -> dict[str, Any]:
    return {"action": "human", "blockers": blockers, "decision_kinds": kinds or []}


def _next(state: State) -> dict[str, Any]:
    """The first D7 row that holds; this version has the rows up to a plan."""
    blocking = unresolved(state)
    if blocking:
        return _human(
            [f"transition_conflict:{cid}" for cid in blocking], ["resolve_conflict"]
        )
    if state.get("owner") is None:
        return _human(["unclaimed"])
    return _human(["plan_not_registered"])
