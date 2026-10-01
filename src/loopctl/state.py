"""The state of a new run, its claim, and the `status` view (D3, D11)."""

from __future__ import annotations

import hashlib
from typing import Any

State = dict[str, Any]

GATES = ("g1", "g2", "g3")


class AlreadyClaimed(Exception):
    """The run has an owner; `owner` is its actor."""

    def __init__(self, owner: str) -> None:
        super().__init__(owner)
        self.owner = owner


def token_digest(token: str) -> str:
    """What the state keeps of a claim token; the token itself is never stored."""
    return "sha256:" + hashlib.sha256(token.encode()).hexdigest()


def initial(repo: str, feature: str, issue: str, actor: str, at: str) -> State:
    """A new run: the coordinator who started it, no owner, nothing registered.

    The store adds schema_version, revision, transitions and the derived
    fields."""
    return {
        "repo": repo,
        "feature": feature,
        "issue": issue,
        "coordinator": {"actor": actor, "at": at},
        "owner": None,
        "plan": None,
        "versions": {"bindings": {}, "policy": None},
        "approval": None,
        "policy_approval": None,
        "gates": {
            gate: {"status": "not_evaluated", "reasons": ["not_started"]}
            for gate in GATES
        },
        "decisions": {},
        "conflicts": {},
    }


def claim(state: State, owner: dict[str, Any]) -> State:
    """Give the coordination right to `owner` unless the run already has one."""
    if state["owner"] is not None:
        raise AlreadyClaimed(state["owner"]["actor"])
    return {**state, "owner": owner}


def owner_view(owner: dict[str, Any] | None) -> dict[str, Any] | None:
    """The owner without its token digest."""
    if owner is None:
        return None
    return {"actor": owner["actor"], "claimed_at": owner["claimed_at"]}


def view(revision: int, state: State) -> dict[str, Any]:
    """The `result` of `status`: the D11 projection of the state file."""
    return {
        "repo": state["repo"],
        "feature": state["feature"],
        "issue": state["issue"],
        "revision": revision,
        "phase": state["phase"],
        "coordinator": state["coordinator"],
        "owner": owner_view(state["owner"]),
        "gates": state["gates"],
        "blockers": state["blockers"],
    }


def human(result: dict[str, Any], nxt: dict[str, Any]) -> str:
    """The `--human` text: the same view, one fact per line."""
    coordinator, owner = result["coordinator"], result["owner"]
    lines = [
        f"phase: {result['phase']}",
        f"coordinator: {coordinator['actor']} (since {coordinator['at']})",
        "owner: unclaimed"
        if owner is None
        else f"owner: {owner['actor']} (claimed {owner['claimed_at']})",
    ]
    for gate, value in result["gates"].items():
        lines.append(f"{gate}: {value['status']} ({', '.join(value['reasons'])})")
    lines.append(f"blockers: {_items(result['blockers'])}")
    details = "; ".join(
        f"{name}: {_items(value) if isinstance(value, list) else value}"
        for name, value in nxt.items()
        if name != "action"
    )
    lines.append(f"next: {nxt['action']} ({details})")
    return "\n".join(lines)


def _items(values: list[str]) -> str:
    return ", ".join(values) if values else "none"
