# SA method

Shared by `project-lead` (project SA, A1) and `feature-to-spec` (feature SA, A4). The level decides how deep items 3-6 go; everything else is the same.

## Skeleton, then top-down

- Build a skeleton first: the seven questions below, drafted from the problem statement and research, every cell marked as an assumption. Already confirmed requirements (for example confirmed parts of an existing document) fill their cells: check applicability and ask only about differences.
- Project level: items 3-6 stay at cross-feature depth (capabilities derived from the scenarios, key rules, shared constraints, milestone acceptance direction). Feature level: this feature's actors and main flow, rules, exceptions, and acceptance criteria.
- Confirm top-down: problem and goal, scope and non-scope, actors and scenarios, behaviour and rules, exceptions and constraints, acceptance. Ask about a lower level only after the level above is agreed, and tie every question to a cell.

## Asking

- Look things up yourself when code or documents can answer them. Ask the human only for business judgement and trade-offs.
- Ask 1-3 related questions per round, ordered by impact. For each question give why it matters now, options, consequences, and your recommendation.
- Unanswerable now: record whether it can wait, what it blocks, and how to find out. Keep unaffected work moving.
- After each round, write each answer into the document that owns it (table below), then tell the human what changed and what still blocks.
- Silence is not agreement. Keep proposals, assumptions, and open items labelled as such.
- Use `grilling` or `domain-modeling` when available and appropriate; say so when they are not. `grill-with-docs` cannot be invoked by an agent; when a deeper interview would help, suggest that the human start it with `/grill-with-docs`.

## Seven questions, four slots

The seven questions are a checklist, not seven sections: 1 problem and goal; 2 scope and non-scope; 3 actors and end-to-end scenarios; 4 behaviour and business rules; 5 exceptions and required constraints; 6 acceptance conditions; 7 assumptions, dependencies, open items.

| Slot | Holds | Project level | Feature level |
| --- | --- | --- | --- |
| Why | 1 | Project intent / mission | `proposal.md` `## Why` |
| Scope | 2 | Project intent / mission | `proposal.md` `## What Changes` plus a `不做` (non-goals) list |
| Requirements | 3-6 | Project intent keeps a summary: main scenarios, the capability list, key rules, shared constraints and the milestone acceptance direction, each pointing to the requirement input, which keeps the requirement text with its source version | `changes/<id>/specs/<capability>/spec.md` delta |
| Open items | 7 | Decisions log / project intent | `proposal.md` section for open items and dependencies |

Only shared domain definitions go into `CONTEXT.md`.

## Spec rules

- One capability is a set of behaviours that change together (for example ingest, sync obligation, recovery), not a component, page, or feature. A feature may touch several capabilities. Cross-feature constraints (capacity, security, audit) form their own capability. In an existing project, keep the current capability boundaries unless they clearly mix concerns.
- `openspec/specs/` holds only implemented and accepted behaviour; only archive writes it (D58). A feature brings the requirements it delivers from the input into its change: ADDED when `openspec/specs/` does not have them yet, MODIFIED (full new text) when it does. A cross-feature constraint enters with the first feature that makes it hold; in every feature SA, check the input for constraints that touch this feature.
- Requirement IDs use one prefix per capability (`ING-01`). IDs are never reused and do not change on archive. Each `Scenario` is an acceptance condition with its own ID (`AC-I01`).
- Give each requirement its main scenario and the exception scenarios that matter (missing data, duplicates, timeouts, partial failure).
- A delta uses exactly these headings: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements` (`FROM:` / `TO:`). Other forms are not parsed.
- Do not invent quantities, choose unresolved technical options, or pad sections.

## One-page summary

Every confirmation starts from a one-page summary ordered by meaning, with links; do not ask the human to read files:

```text
Goal: ...                                   -> proposal.md#why (or project intent)
Not doing: ...
Rules: ING-01 ..., ING-02 ...               -> specs/<capability>/spec.md
Exceptions: AC-I03 duplicate, AC-I04 timeout
Open: Q1 capacity limit (blocks design, needs your decision)
Versions: <commit or file hashes>
```

Record each confirmation with who, when, their words, and the version confirmed.
