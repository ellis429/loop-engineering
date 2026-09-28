---
name: plan-to-code
description: Use when a feature's plan (design.md and tasks.md) has its start-of-work approval and its tasks must be implemented, or when review findings, a failed gate or an acceptor's rejection send fixes back to a feature's tasks. Used by the Engineer or the coordinator of the feature loop. Not for writing the plan (spec-to-plan) or opening pull requests (to-pr).
---

# Plan to code

Implement an approved plan task by task: dispatch an Implementer at the planned effort, check the attempt yourself, have a different model review it, and fix within limits. Stop when every task is accepted and its review is clean (D69).

Read repository instructions first; they override this skill. Commit and test conventions come from them. Superpowers skills are named here without a prefix; installed as the Superpowers plugin they appear as `superpowers:<name>`.

## 0. Check the entry

- The start-of-work approval is recorded (ticket comment with the plan's commit) and the ticket state is `開發中`, or `Blocked：correction limit` with a later recorded human decision adding rounds (then set the state back to `開發中` with 下一步 naming the batch, and continue). It must be the latest approval: no later comment supersedes it, `design.md` and every task plan linked from `tasks.md` are unchanged since the approved commit, and `tasks.md` differs from it only in ticked boxes and regression tests added for findings. Without it, stop.
- Fixes sent back by `to-pr` (G1 or G3 failures, G2 findings) or by an acceptor's rejection (defects against acceptance IDs) are fixes to the task that owns the affected paths, handled as in step 3. They come as one batch, handled in this order:
  1. A batch on the ticket without a result comment is unfinished: continue it under its ID. If it is marked dispatched it already counts; if it is still pending, dispatch it as in step 3.
  2. Otherwise count the dispatched batches on the ticket. If they have reached the limit (three plus any rounds the human's recorded decisions added, D70), set `Blocked：correction limit` with 下一步 the human who decides, post one Blocked comment: the run id (or who ran it by hand), the change id and the commits it applies to, the problem, what was tried with its evidence, the options, and who decides, and stop.
  3. Otherwise post one ticket comment for the new batch, marked pending (a batch ID, its source, the findings or defects, its round number). When its first Implementer session starts, edit the comment to mark it dispatched with the time; from then on it counts.
  4. When the batch is done, post its result comment (commits and evidence per finding).
- Every upstream feature this one depends on is accepted and merged, at the version the handoff package names (D27); otherwise stop, because only preparation may run ahead of it.
- If the approval depends on a spec change (a decision that alters a requirement or scenario), that change is already committed through `feature-to-spec`; otherwise stop and send it there. Do not implement against a spec that says something else.
- Work on `feature/<id>` in the feature's worktree, and on the branch of the same name in each affected service repo (D67). Do not commit to the default branch.
- `tasks.md` is the only plan. Take each task's owned paths, tests, expected Reds and effort from it; do not re-plan. A plan that cannot be followed goes back to `spec-to-plan`.

## 1. Dispatch one task

Follow `subagent-driven-development` for the rhythm (one fresh Implementer per task, you as coordinator), with these rules:

- Implementer: a fresh session at the task's planned model and effort; when the task links a code-level plan (`task-plans/<task-id>.md`), the Implementer follows it with TDD. Its prompt holds the task's row and card from `tasks.md`, the relevant `design.md` sections, the acceptance rows, the owned paths, what is out of scope, and the repository's commit rules.
- Method: `test-driven-development`. Write the tests the plan lists, run each, and save the raw Red (command, output, exit code, commit) before implementing, then the Green. A task that only changes documentation or comments has no Red: the plan states the reason, and the reviewer confirms it. Save evidence outside the tracked tree, for example `.delivery/<id>/<task>/attempt-<n>/`.
- A test that passes on its first run is not a Red: record it, and show it can fail (break the guarded line, see it fail, restore) or ask why the behaviour already exists.
- Commits: one logical change per commit, each green, in the repository's format; no AI attribution. A task may have several commits. Tick the task's box in `tasks.md` in the task's last commit, not a separate one.
- A requirement that looks wrong or missing is not implemented: the Implementer reports it, and you stop that task and send it to the Project Lead (`feature-to-spec` revises the feature).
- A fix that would change what the task promises (its behaviour, acceptance mapping or design, or rewriting or dropping a test the plan lists) is not a fix: post a ticket comment that the start approval no longer covers the plan (name the finding), set 下一步 to the Engineer revising the plan, and send it to `spec-to-plan`, even when the paths are the same. Adding a regression test for a finding inside the approved scope is part of the fix.

## 2. Accept the attempt yourself

Before any review:

- `git diff --name-only <task base>..HEAD` stays inside the task's owned paths.
- In a fresh clone at the attempt's head: the full test suite and every repository check pass.
- Every listed test exists, and every Red fails on its planned assertion. A Red that stops in setup, import, a missing command or a stub does not count, in the harness task too (D68).
- Evidence files exist for every Red and Green.

Any miss sends the task to a new attempt with the concrete reasons. At most three attempts per task. When they are used up, set the ticket to `Blocked：<task and reason>`, set 下一步 to the human who decides, post one Blocked comment: the run id (or who ran it by hand), the change id and the commits it applies to, the problem, what was tried with its evidence, the options, and who decides (the attempts with their evidence), and stop.

## 3. Per-task review

A reviewer that is a different model from the Implementer (D52), preferably from another vendor (for example `codex exec -m gpt-6-sol -s read-only`), in a fresh session on a fresh clone, reviews the task's range (task base to accepted head) against `tasks.md`, `design.md` and the spec, at the task's planned Reviewer effort. Another effort, alias or session of the same model does not count.

Sort each finding:

- **now:** blocking; fix before the next dependent task.
- **before PR:** fix before `to-pr`.
- **ticket:** out of this feature's scope; open a ticket with the evidence (authorised) and link it.

A fix is a new attempt with a Red tied to the finding, made as new commits on top: never amend, squash or rebase a commit that was reviewed or accepted, so the reviewed version and its evidence stay reachable. Add each fix's tests to the task's test list in `tasks.md` in the same commit. Then re-review in the same reviewer session; the three-attempt limit counts fixes too. Post the review outcome as one ticket comment per task (D60): who posts it, the reviewer model and effort, when, the reviewed range (base and head commits), each finding with its sorting and resolution, and the evidence others can open: the failing and passing lines inline, and the raw Red and Green records (command, full output, exit code, commit) in a collapsed `<details>` block, since local evidence paths are not reachable.

## 4. Stop

When every task is accepted and its review has no open `now` or `before PR` finding, report: tasks with their commits, evidence locations, review outcomes, tickets opened, and anything parked. Continue with `to-pr`. Do not open pull requests or run the whole-change review here.

## Red flags

| Thought | Reality |
| --- | --- |
| "The first failure was `invalid choice`, close enough" | Not a Red; the test must reach its assertion |
| "A Sonnet agent reviewed the Opus work" | Allowed only as a different model; prefer another vendor, and never the same model at another effort |
| "Tests pass in my worktree" | Acceptance runs in a fresh clone |
| "I'll tick the box in its own commit" | The box goes in the task's last commit |
| "It's a small spec gap, I'll just handle it" | Report it; the spec changes only through the Project Lead |
| "The plan says one commit per task, so I'll amend the fix in" | Fixes are new commits; a reviewed commit is never rewritten |
