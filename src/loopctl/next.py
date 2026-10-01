"""derive(state): the derived fields phase, blockers and next (D7)."""

from __future__ import annotations

from typing import Any

State = dict[str, Any]


def derive(state: State) -> State:
    """`state` with phase, blockers and next recomputed from its other fields."""
    nxt = _next(state)
    return {**state, "phase": _phase(state), "blockers": nxt["blockers"], "next": nxt}


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
    if state.get("owner") is None:
        return _human(["unclaimed"])
    return _human(["plan_not_registered"])
