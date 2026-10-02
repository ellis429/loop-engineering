"""derive(state): the derived fields phase, blockers and next (D7)."""

from __future__ import annotations

from typing import Any

State = dict[str, Any]


def derive(state: State) -> State:
    """`state` with phase, blockers, next and plan.superseded_by recomputed
    from its other fields."""
    plan = state.get("plan")
    if plan:
        state = {**state, "plan": {**plan, "superseded_by": superseded_by(state)}}
    nxt = _next(state)
    blockers = nxt["blockers"] if nxt["action"] == "human" else []
    return {**state, "phase": _phase(state), "blockers": blockers, "next": nxt}


def unresolved(state: State) -> list[str]:
    """The conflicts no human has resolved yet, by cid (D6)."""
    return sorted(
        cid
        for cid, conflict in (state.get("conflicts") or {}).items()
        if conflict.get("resolved_by") is None
    )


def superseded_by(state: State) -> list[str]:
    """The scope_change decisions in effect that supersede the current plan,
    by seq (D7). The plan is superseded while this is not empty; register,
    approve_plan and next all tell it by this one list."""
    plan = state.get("plan")
    if not plan:
        return []
    current = (plan["version"], plan["digest"])
    found = [
        record
        for record in (state.get("decisions") or {}).values()
        if record["kind"] == "scope_change"
        and record["status"] == "in_effect"
        and (record["supersedes"]["version"], record["supersedes"]["digest"]) == current
    ]
    return [record["id"] for record in sorted(found, key=lambda record: record["seq"])]


def _phase(state: State) -> str:
    if state.get("approval"):
        return "approved"
    if state.get("plan"):
        return "awaiting_approval"
    return "planning"


def _human(blockers: list[str], kinds: list[str] | None = None) -> dict[str, Any]:
    return {"action": "human", "blockers": blockers, "decision_kinds": kinds or []}


def _next(state: State) -> dict[str, Any]:
    """The first D7 row that holds."""
    blocking = unresolved(state)
    if blocking:
        return _human(
            [f"transition_conflict:{cid}" for cid in blocking], ["resolve_conflict"]
        )
    if state.get("owner") is None:
        return _human(["unclaimed"])
    approval = state.get("approval")
    if approval:
        # The approved plan goes out as the first task (D8).
        plan = approval["plan"]
        return {"action": "dispatch", "plan": plan, "approval": approval["decision"]}
    if not state.get("plan"):
        return _human(["plan_not_registered"])
    blockers = _plan_blockers(state)
    if blockers:
        return _human(blockers)
    return _human(["plan_not_approved"], ["approve_plan"])


# The roles a plan needs bindings of before it can be approved (D7, D10).
NEEDED_ROLES = ("spec", "ac", "design")


def _plan_blockers(state: State) -> list[str]:
    """What keeps the plan from approval (D7)."""
    plan, bindings = state["plan"], state["versions"]["bindings"]
    blockers = [f"plan_superseded:{id_}" for id_ in superseded_by(state)]
    # Only a plan an Implementer calibrated can be approved (ORC-11).
    if plan["producer"] != "implementer" or not plan["calibrated_from"]:
        blockers.append("plan_not_calibrated")
    blockers += [
        f"missing_binding:{role}" for role in NEEDED_ROLES if not bindings.get(role)
    ]
    return blockers
