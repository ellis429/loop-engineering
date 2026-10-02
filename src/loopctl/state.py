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


def view(revision: int, state: State, policy_digest: str | None) -> dict[str, Any]:
    """The `result` of `status`: the D11 projection of the state file, with
    `policy_digest`, the digest of the registered policy file as it is now
    (None when it cannot be read)."""
    return {
        "repo": state["repo"],
        "feature": state["feature"],
        "issue": state["issue"],
        "revision": revision,
        "phase": state["phase"],
        "coordinator": state["coordinator"],
        "owner": owner_view(state["owner"]),
        "plan": state["plan"],
        "bindings": state["versions"]["bindings"],
        "approval": approval_view(state),
        "policy": policy_view(state, policy_digest),
        "gates": state["gates"],
        "blockers": state["blockers"],
        "decisions": state["decisions"],
        "conflicts": state["conflicts"],
    }


def approval_view(state: State) -> dict[str, Any]:
    """The approval with its status; when there is none, the plan version
    that awaits it (D11)."""
    approval = state["approval"]
    if approval is None:
        plan = state["plan"]
        return {
            "status": "not_approved",
            "plan_version": None if plan is None else plan["version"],
        }
    return {"status": "approved", **approval}


def policy_view(state: State, current_digest: str | None) -> dict[str, Any]:
    """The policy, its registration, the policy_change that approved it, and
    `current_digest`, the digest of its file as it is now (D11): approved
    only while the approval, the registration and the file all have the
    same digest."""
    registration, approval = state["versions"]["policy"], state["policy_approval"]
    if registration is None:
        status = "not_registered"
    elif current_digest is None:
        status = "unreadable"
    elif approval is None or approval["digest"] != registration["digest"]:
        status = "not_approved"
    elif current_digest != approval["digest"]:
        status = "digest_mismatch"
    else:
        status = "approved"
    return {
        "status": status,
        "registration": None
        if registration is None
        else {name: value for name, value in registration.items() if name != "content"},
        "approval": approval,
        "current_digest": current_digest,
    }


# The roles of bindings, in the order `--human` shows them.
ROLES = ("spec", "ac", "design", "sa")


def _document(entry: dict[str, Any] | None) -> str:
    return "none" if entry is None else f"{entry['locator']} {entry['version']}"


def human(result: dict[str, Any], nxt: dict[str, Any]) -> str:
    """The `--human` text: the same view, one fact per line."""
    coordinator, owner = result["coordinator"], result["owner"]
    lines = [
        f"phase: {result['phase']}",
        f"coordinator: {coordinator['actor']} (since {coordinator['at']})",
        "owner: unclaimed"
        if owner is None
        else f"owner: {owner['actor']} (claimed {owner['claimed_at']})",
        f"plan: {_document(result['plan'])}",
    ]
    for role in ROLES:
        entries = result["bindings"].get(role, {}).values()
        lines.append(f"{role}: {', '.join(map(_document, entries)) or 'none'}")
    approval = dict(result["approval"])
    status = approval.pop("status")
    details = "; ".join(f"{name}: {value}" for name, value in approval.items())
    lines.append(f"approval: {status} ({details})")
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
