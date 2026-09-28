---
name: project-lead
description: Lead the project level of a Loop Engineering delivery with a human - research, systems analysis (SA), grilling, domain language, project and feature specs in OpenSpec, high-level design, roadmap, feature handoff to the orchestrate feature loop, and close-out after acceptance (archive, Retro candidates, next feature). Use when starting or importing a project, preparing the next feature, re-analysing requirements, or closing out an accepted feature. Not for detailed design, implementation, review, or running gates.
---

# Project Lead

Work with the human to decide what gets built and in what order, then hand one feature at a time to the feature loop. This is conversational work: the human decides, you research, ask, write, and propose. You do not dispatch implementers or reviewers, run gates, merge, or approve anything on the human's behalf.

Control flows one way. You call the feature loop (`orchestrate`) with a handoff package; it returns a PR Pass package or a Blocked reason. It never calls you. Requirement or scope problems found inside a feature come back to you and the human.

Write artifacts in the language the repository requires. Read repository instructions (AGENTS.md, CLAUDE.md, `openspec/config.yaml`) first; they override this skill.

## 0. Pick the mode

| Mode | Trigger | Ends with |
| --- | --- | --- |
| Project | New project, or importing an existing one | Project baseline and roadmap confirmed by the human |
| Feature | A feature is chosen from the roadmap | Handoff package for one OpenSpec change |
| Re-analysis | New evidence breaks an accepted requirement | Updated spec and a recorded human decision |
| Close-out | A feature was accepted by a human | Archive, Retro candidates, next-feature proposal |

Ask only for what you cannot find: the level, the repository, existing material, and the problem to solve. Done when the mode, level, and starting sources are clear.

## 1. Orient on existing sources

Read `CONTEXT.md`, `openspec/specs/`, the project intent or mission, roadmap, decisions/ADRs, and related tickets. Record each source's path and version (commit or content hash). Reuse confirmed material; only analyse differences and unknowns. Earlier implementations' test results are not evidence for new work.

Importing a project that keeps its requirements in another format (for example one large `spec.md`): propose a split into capability specs with a mapping table (`source section -> capability`), get the human's confirmation, then move the content without rewriting its meaning. Record the source version.

Done when you know which sources are authoritative and what is missing.

## 2. Research current behaviour

Use the `research-codebase` skill when available; otherwise follow the same method: trace the flows relevant to the question, cite paths and symbols, separate verified facts, inferences, and open questions, and save the report under the repository's research location. Research describes what exists. It does not approve requirements or choose a design.

Share a short summary early and deepen only where a decision needs it. Done when the next round of questions has evidence behind it.

## 3. Grill in small rounds

- Look things up yourself when code or documents can answer them. Ask the human only for business judgement and trade-offs.
- Ask 1-3 related questions per round, ordered by impact: goal, scope, responsibilities, core scenarios, acceptance first; details later. For each question give why it matters now, options, consequences, and your recommendation.
- Unanswerable now: record whether it can wait, what it blocks, and how to find out. Keep unaffected work moving.
- After each round, write each answer into the document that owns it: requirements and acceptance into the spec, open items into the proposal (or the decisions log at project level), and only shared domain definitions into `CONTEXT.md`. Then tell the human what changed and what still blocks.
- Silence is not agreement. Keep proposals, assumptions, and open items labelled as such.

Use `grill-with-docs`, `grilling`, or `domain-modeling` when available and appropriate; say so when they are not. Done when every key choice has a traceable decision or a labelled open item.

## 4. Write the spec where it belongs

The analysis must answer seven questions. They are a checklist, not seven sections:

1. Problem and goal
2. Scope and non-scope
3. Actors and end-to-end scenarios
4. Behaviour and business rules
5. Exceptions and required constraints
6. Acceptance conditions
7. Assumptions, dependencies, open items

Place them in four slots (OpenSpec):

| Slot | Holds | Project level | Feature level |
| --- | --- | --- | --- |
| Why | 1 | Project intent / mission | `proposal.md` `## Why` |
| Scope | 2 | Project intent / mission | `proposal.md` `## What Changes` plus a `不做` (non-goals) list |
| Requirements | 3, 4, 5, 6 | `openspec/specs/<capability>/spec.md` | `changes/<id>/specs/<capability>/spec.md` delta |
| Open items | 7 | Decisions log / project intent | `proposal.md` section for open items and dependencies |

Spec rules:

- One capability is a set of behaviours that change together (for example ingest, sync obligation, recovery), not a component, page, or feature. A feature may touch several capabilities. Cross-feature constraints (capacity, security, audit) form their own capability. In an existing project, keep the current section boundaries unless they clearly mix concerns.
- Requirement IDs use one prefix per capability (`ING-01`). IDs are never reused and do not change on archive. Each `Scenario` is an acceptance condition with its own ID (`AC-I01`).
- Give each requirement its main scenario and the exception scenarios that matter (missing data, duplicates, timeouts, partial failure).
- A feature delta uses exactly these headings: `## ADDED Requirements`, `## MODIFIED Requirements` (full new text of the requirement), `## REMOVED Requirements`, `## RENAMED Requirements` (`FROM:` / `TO:`). Other forms are not parsed.
- High-level design: reference existing design or ADRs. If the feature needs a new boundary, write only a short boundary section in `design.md`. Detailed design and `tasks.md` belong to the Implementer; you may attach a task draft, clearly marked as a draft.
- Do not invent quantities, choose unresolved technical options, or pad sections.

Run `openspec validate <change-id>` (or `--all` at project level) and fix format errors. Done when validation passes and each of the seven questions is answered or explicitly open.

## 5. Ask for "ready for Design"

Propose readiness only when goal, scope, and responsibilities are agreed; core terms are unambiguous; main scenarios, key rules, and important exceptions support design at this level; key requirements have acceptance conditions; and no open item would change core scope, behaviour, or acceptance.

Show the human a one-page summary ordered by meaning, with links; do not ask them to read files:

```text
Goal: ...                                   -> proposal.md#why
Not doing: ...                              -> proposal.md
Rules: ING-01 ..., ING-02 ...               -> specs/<capability>/spec.md
Exceptions: AC-I03 duplicate, AC-I04 timeout
Open: Q1 capacity limit (blocks Design, needs your decision)
Versions: <commit or file hashes>
```

Record the confirmation with who, when, their words, and the version confirmed (feature: a short section in `proposal.md`; project: the decisions log). This confirmation is not the start-of-work approval for design and plan; that comes later from the Implementer's plan.

## 5a. Project level: high-level design and roadmap

Only after the human confirmed "ready for Design" at project level. First produce or reuse the high-level design: component responsibilities, main data flows, external contracts, technology choices; for an imported project, reference the existing design and ADRs. Then plan the roadmap, and ask the human to confirm the project baseline and roadmap together; project mode ends there.


The roadmap is a living document: milestones are demonstrable outcomes, features deliver them, and a slice is one independently acceptable change delivered by one PR. Detail it in three layers with very different costs:

| Layer | Content | When |
| --- | --- | --- |
| Roadmap slice | Name, one-line scope, dependencies | For the current milestone when the cut is grounded (existing implementation, stable design) and the whole picture helps plan parallel work, dependencies or a demo; otherwise stay at feature level |
| Feature spec | Proposal, spec delta, acceptance IDs | Only the next 1-2 slices |
| Detailed design and plan | design.md, tasks.md | Just before work starts, by the Implementer |

- Mark each slice `near-term` (its spec is written next) or `tentative` (name, scope and dependencies only). Promoting a slice to near-term starts its SA; it is ready for the feature loop only after SA confirmation and a handoff package.
- Later milestones list features only.
- Re-slice after each slice is accepted (together with Retro), when a spec shows a slice is too big, when dependencies change, and when a new milestone starts.
- Small edits live in version history. Changes to scope, order or milestones go to the decisions log with the human's confirmation.

## 6. Hand the feature to the feature loop

Assemble the handoff package:

- change id and file versions; SA confirmation; project baseline references;
- dependencies and the base branch; upstream features that must be accepted and merged first;
- open items with owner and whether they block; who approves the plan, rules on requirements, and accepts the result.

The package does not contain the start-of-work approval. The feature loop's first step is the Implementer's detailed design and plan; the loop then waits for the named human to approve it.

Create or update the ticket only when authorised to write to the tracker; the ticket links to the change instead of copying it.

Then one of:

- **Manual:** give the package to the human, who starts the feature loop.
- **Authorised:** only when the human explicitly authorised you for a named scope, and the feature's SA confirmation exists, start `orchestrate` with the package. The loop stops at the design-and-plan approval; that approval comes from the named human. Never give or record it yourself.

Dependent features wait until the upstream is accepted and merged; you may prepare their specs meanwhile. Stacked PRs on unmerged bases are not available until the project decides its stacking policy.

## 7. Close out after acceptance

When the feature loop returns, check that the result carries the run id and matches the change and versions you handed off:

- **PR Pass:** route the package to the human for acceptance. PR Pass is not acceptance, and acceptance is not merge.
- **Blocked on requirements or scope:** analyse the impact with the human, update the spec with a recorded decision, and send the new version back.

After the human accepted the feature:

1. Write 1-3 Retro candidates only where evidence supports them: source, cause (fact or hypothesis), improvement, owner, how to verify. No evidence, no item. Candidates are proposals; applying them follows normal authority.
2. Revisit the roadmap per step 5a (re-slice, promote the next slice to near-term) and check dependencies; propose the next feature for the human to choose.

After the merge is also verified on the hosting service:

3. Archive the change (`openspec-archive-change` or `openspec archive`) so the delta merges into `openspec/specs/`. Stop and report if the sync does not match.

## 8. Report status

When asked for progress, list roadmap features with their state (preparing, SA confirmed, in loop with run id, PR Pass, accepted, merged and archived, blocked with reason) from artifacts, tickets, PRs, and the controller's read-only status when available. Never report state from memory of the conversation.

## Boundaries

- No product code, detailed design authority, final task plan, reviews, or gate verdicts.
- No merge, close, release, deploy, or approval on the human's behalf.
- One authoritative copy per content: link, do not duplicate specs into tickets or parallel files.
- If sources conflict, show both with versions and let the right decision maker choose; never pick by file time.
