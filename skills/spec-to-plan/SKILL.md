---
name: spec-to-plan
description: Use when a feature's handoff package is ready and its design and implementation plan must be written before work starts, or when a plan was sent back at the start-of-work approval. Used by the Engineer or the coordinator of the feature loop. Not for writing the spec (feature-to-spec) or for implementing tasks (plan-to-code).
---

# Spec to plan

Turn a confirmed spec into `design.md` and `tasks.md` in the feature's OpenSpec change, have a different model review the plan, and stop at the start-of-work approval (◆確認開工). `tasks.md` holds no implementation code, but it states every test and where its Red must fail (D68, D69); only a task plan the Engineer asked for goes down to code (D72).

Read repository instructions (AGENTS.md, CLAUDE.md, `openspec/config.yaml`) first; they override this skill. Superpowers skills are named here without a prefix; installed as the Superpowers plugin they appear as `superpowers:<name>`.

## 0. Check the entry

- Work in the feature's worktree on `feature/<id>` in the root repo (D67); in a multi-repo product, run the sync command and use a branch of the same name in each affected service repo.
- The ticket state is `就緒（可設計）`; `開發中` when `plan-to-code`, `to-pr` or a rejection sent a fix beyond the approved plan back here; or `Blocked：…` (an unclean plan review, or a limit reached in `plan-to-code` or `to-pr`) once the human's decision to revise the plan is recorded on the ticket; after a correction limit, that decision also states how many more correction rounds it adds to the limit, and `plan-to-code` and `to-pr` count against the new total. Otherwise stop and report the state.
- Read the handoff package (ticket comment): spec commit, spec confirmation or fold note, acceptance IDs, affected repos with base commits, start approver, acceptor. Anything missing or contradictory goes back to `feature-to-spec` as specific questions.
- The spec is fixed here. A requirement that looks wrong is a question for the Project Lead, not an edit.

## 1. Research the code

Use `research-codebase` on the flows this feature touches: entry points, existing fixtures and test helpers, test seams, and the files each change will own. On legacy code, also which of the paths it changes have no tests protecting them: they get characterization tests first (D72). Save the report on the branch and commit it.

## 2. Write design.md

Run `openspec instructions design --change <id>` and write within the high-level design's boundaries: modules, interfaces, data flow, failure handling, and the seams tests will use. When two approaches need comparing, use the option comparison from `brainstorming`, but write the outcome into `design.md`, never into `docs/superpowers/specs/`. A new high-level boundary goes back to the Project Lead.

## 3. Write tasks.md, the only plan

Run `openspec instructions tasks --change <id>`. Cut the work into tasks as vertical slices, the tracer-bullet rules of Matt Pocock's `to-tickets` (D71):

- **Vertical:** each task cuts a narrow but complete path through every layer it needs and is verifiable on its own through a public entry point. No task is one layer only.
- **One session:** each task fits one fresh session. Split a larger one; merge a task too small to review on its own. `writing-plans`' 2–5 minute steps belong inside a task, never as tasks.
- **Prefactor first:** changes that make later tasks easy come first, the shared test harness below among them.
- **Blocking edges:** each task names only the tasks that must finish before it, and the interface it takes from each: the signature, and also the invariants, ordering constraints and error cases a caller must respect (the vocabulary of `codebase-design`).
- **Wide refactors** (one mechanical change that breaks every caller at once, such as a rename) are the exception: sequence them expand, migrate in batches, contract.

Then write each task, with these rules:


- **No implementation code in `tasks.md`.** How to implement stays with the Implementer, unless the Engineer asked for that task's code-level plan (below).
- **Shared test harness first.** If tests need shared fixtures, setup helpers, a CLI entry point or parser, or stubs that return plausible values, make that the first task, with its own tests. Every later Red must be able to reach its assertion. The harness task's own tests assert the entry point's contract (arguments passed through, output format), and their Reds fail on those assertions too; a test helper that catches the usage error lets them get there. When no harness is needed, say why in `tasks.md`.
- **Every task lists:** ID; what it delivers; mode and Implementer model (D72); owned paths per repo, shared files included; blocking edges with the interface taken from each; acceptance IDs covered; commit subject; Implementer and Reviewer effort; and its tests. For each test: name, the observable behaviour asserted, **the assertion its Red must fail on**, the expected Green, and the command. Tests are listed as behaviour at the entry point, not as test code: the Implementer writes them one at a time and may organise them differently, but not change what they assert.
- **Acceptance verification:** for each acceptance ID, how and where it is verified, what passing means, and where the evidence goes.
- **Scope, environment, risks and execution limits** are written down.

Effort per task (D69):

| The task | Implementer | Reviewer |
| --- | --- | --- |
| Docs or configuration only | medium | high |
| Ordinary behaviour, even when it touches several files | high | high |
| A mistake could lose or corrupt data, break a concurrency or failure-recovery guarantee, or weaken security; or the task covers six or more acceptance rows | xhigh | xhigh |

Mode per task (D72), written on the task with its effort:

| The task | Plan goes down to | Implementer model |
| --- | --- | --- |
| Default | Design, the interfaces with their invariants, and the tests | Strong |
| All five hold: deciding is harder than writing, the task is separable, tests and checks catch mistakes, much more writing than deciding, common code | Also the change points: files, functions, signatures, edge cases, tests to run; never line-by-line code | May be cheaper |
| Legacy code, or domain rules hidden in the code | Design; research reads the code first | Strong; without tests over the paths it changes, the first task adds characterization tests (current behaviour recorded by running the code, not inferred) |
| Mechanical work under tests: rename, boilerplate, migrate batches | The required task fields only, no extra detail | Cheaper |

The Reviewer is always a strong model and a different model from the Implementer, preferably from another vendor (D52).

**Code-level plan, on request.** When the Engineer asks for one on a task (typically a PBI-sized task on legacy code), write that task's plan down to code with `writing-plans` into `openspec/changes/<id>/task-plans/<task-id>.md` and link it from the task: its steps, code and commands, starting with characterization tests when the paths have none. `tasks.md` stays the plan of record; the plan review covers the task plan too. Nothing else changes for that task: the cut, its tests and expected Reds, the per-task review, `to-pr`.

Red flags, each a sign the plan is not ready:

| In the plan | Why it fails | Fix |
| --- | --- | --- |
| "Red: argparse rejects `cas`" or "fails with unknown command" | The Red proves the command is missing, not that the behaviour is | Add the parser and a stub in the harness task; the Red must fail on the behaviour's assertion |
| "Red: ImportError" or "module not found" | Same | Create the module interface in the harness task |
| Tests described only as "tests for AC-X pass" | The Implementer invents the tests | List each test with its assertion and expected Red |
| No effort per task | Effort gets chosen ad hoc | Apply the table |

Run `openspec validate <id>` and commit.

## 4. Independent plan review

A model different from the plan's author reviews the plan in a fresh session, read-only (D52), for example `codex exec -m gpt-6-sol -s read-only`. Ask it to check: the cut (vertical, one session each, prefactoring first, blocking edges with their interfaces and invariants), the D68 rules above, every acceptance ID covered, owned paths, effort, risks, and whether each listed Red can actually fail on its assertion. Fix and re-review in the same reviewer session until clean, at most three rounds. The start-of-work approval needs a clean review. Not clean after three rounds: set the ticket to `Blocked：plan review not clean`, set 下一步 to the human who decides, post one Blocked comment: the run id (or who ran it by hand), the change id and the commits it applies to, the problem, what was tried with its evidence, the options, and who decides (the open findings and the plan commit among them), and stop. The human decides how the plan (or, through `feature-to-spec`, the spec) changes; then review again. Keep the review result on the branch.

## 5. Stop at the start-of-work approval

Show the start approver a one-page summary: tasks in order with what each delivers, its blocking edges and its effort, and whether the granularity looks right (too coarse or too fine); what each Red proves, risks and limits, the plan review result, and any decision they must make. When the Project Lead is also the Engineer, this approval also covers the spec (D59).

If the approver changes only a task's effort, update `tasks.md` and commit before recording. Any other change (tests, acceptance mapping, owned paths, tasks, design) goes back through step 4 until the review is clean, and the approval is asked again. When approved, record it as one ticket comment: who, when, their words, and the plan's commit, naming any approval it supersedes (D60); set the ticket state to `開發中` and 下一步 to implementation (D67). Every tracker write needs authorisation. Implementation continues with `plan-to-code`.

## Boundaries

- No implementation code outside a requested task plan; no commits outside the design, plan, task plan, research and review records.
- No approval on the human's behalf; no spec edits.
- One plan: `tasks.md`. No `docs/superpowers/plans/` file.
