---
name: feature-to-spec
description: Use when a feature chosen on the roadmap needs its OpenSpec change, spec and ticket before engineering starts, or when the spec of a feature still in preparation must change. Used by the Project Lead or the Engineer. Not for project-level planning or close-out (project-lead), and not for design, tasks, implementation or review (orchestrate).
---

# Feature to spec

Turn one roadmap feature into an OpenSpec change (proposal and spec delta) and a ticket, get the spec confirmed, and hand the feature to the feature loop. The person you work with may be the Project Lead or the Engineer (D64); the spec confirmation always comes from the Project Lead, folded into the start-of-work approval when one person holds both roles (D59).

Read repository instructions (AGENTS.md, CLAUDE.md, `openspec/config.yaml`) first; they override this skill. Asking, writing and spec rules follow [the SA method](../project-lead/sa-method.md) at feature depth. `design.md` and `tasks.md` belong to the Implementer (D54); you may attach a task draft clearly marked as a draft.

## 0. Check the entry

- Multi-repo product: work from the root repo and run its sync command first (D61).
- Small work does not open a change: a fix that restores behaviour the spec already states, a dependency update, or missing tests. Write a self-contained ticket (goal, acceptance criteria, narrow scope) and stop. A bug the spec never covered is a feature.
- The feature must be on the roadmap and chosen when the Project Lead confirmed it (D63). If not, stop and send the human to `project-lead`.

## 1. Open the change and the ticket

- `openspec new change <id>` in the root repo, with a short English id (`finalize-protocol`). First use in the repository: `openspec init --tools claude,codex`.
- Ticket: create one, or bring an existing one up to this shape. Title: the feature name, no prefix. Body: goal in one or two lines, milestone, link to `openspec/changes/<id>/`, blocked-by, state `準備中`. It links to the change and never copies it.
- Every tracker write needs authorisation; without it, hand the text to the human to post.

Done when the change folder exists and the ticket links to it.

## 2. Research

Read the feature's roadmap row, the requirement input it points to, the cross-feature constraints in the project intent, `openspec/specs/`, design documents and ADRs, and related tickets; record each source's path and version. Then research the code this feature touches with `research-codebase` (query `graphify-out/` first when it exists). Save the report under the repository's research location; separate facts, assumptions, and unknowns.

Done when the next questions have evidence behind them.

## 3. Proposal and scope

Draft `proposal.md` first: Why, What Changes, a `不做` list, and a 「待決與依賴」 section (each item: whether it blocks design, owner). Ask about goal and scope before anything else; do not write requirements until the human agrees the scope. A new high-level boundary goes into the project's design documents or an ADR, referenced from the proposal.

Done when the human agreed goal, scope and non-scope.

## 4. Spec delta

Bring the requirements this feature delivers from the input into `specs/<capability>/spec.md` (ADDED or MODIFIED). Ask down the skeleton: flow, rules, exceptions, acceptance; write each answer in place as a requirement with ID-bearing scenarios. Check the cross-feature constraints this feature touches. Run `openspec validate <id>` and fix format errors.

Done when validation passes, every requirement has an ID and at least one scenario, the main flow and each exception have a scenario, and no open item would change scope, behaviour, or acceptance.

## 5. Confirm the spec

Show the one-page summary. The Project Lead confirms; record it in a short section of `proposal.md`: who, when, their words, the version. When one person holds both roles, record instead that the confirmation is folded into the start-of-work approval. This is not the start-of-work approval.

## 6. Hand off

1. Ask the Project Lead who approves the start of work (usually the Engineer) and who accepts the result: the Project Lead unless the requirement came from someone else, who then accepts (D62).
2. Assemble the handoff package: change id and file versions; the spec confirmation or the fold note; versions of the project intent, high-level design and roadmap it relies on; spec, acceptance IDs and design boundaries; for each affected repo its base branch, commit, and the PR to be opened (D61); dependencies with their version and state; open items with decision maker and next owner; the start approver and the acceptor.
3. Post the package as one ticket comment (D60); add the acceptance IDs to the ticket; set the state to `就緒`.
4. The Engineer checks the package and either starts or returns specific questions; answer them by going back to step 3 or 4.

Then one of:

- **Manual:** the Engineer starts `orchestrate` with the package.
- **Authorised:** only when the human explicitly authorised you for a named scope and the spec confirmation exists (or is folded), start `orchestrate` yourself. The loop stops at the design-and-plan approval, which only the named human gives.

A feature that depends on another may be prepared now; its implementation starts only after the upstream is accepted and merged (D27).

## Boundaries

- No design, final task plan, product code, reviews, or gate verdicts.
- No approval, merge, or close on the human's behalf.
- One authoritative copy: the spec lives in the change; the ticket links to it.
