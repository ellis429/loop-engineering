---
name: to-pr
description: Use when every task of a feature has passed its per-task review and the feature needs its pull requests, an independent whole-change review and CI before the acceptor sees it, or when open pull requests must be verified again after new commits. Not for implementing tasks (plan-to-code) or for recording acceptance (project-lead).
---

# To PR

Take a feature whose tasks are done and reviewed to PR Pass: gate G1 (tests on the integrated head), one pull request per affected repo, G2 (independent review of the whole set) and G3 (required CI), a bounded fix loop, and the PR Pass package on the ticket. Stop at 待驗收 (D69).

Read repository instructions first; they override this skill. Superpowers skills are named here without a prefix; installed as the Superpowers plugin they appear as `superpowers:<name>`.

## 0. Check the entry

- Every task in `tasks.md` is done and its per-task review is clean; findings marked for before the PR are resolved.
- The worktree is clean and each affected repo is on `feature/<id>`; the ticket state is `開發中`, or `待驗收` when the recorded version set went stale before acceptance (below).
- Get authorisation to push, open pull requests and write to the ticket; without it, hand over the commands and text.

## 1. G1: tests on the integrated head

In a fresh clone of each affected repo at the head to be proposed, run the full test suite and every check the repository requires (lint, types, build). Use `verification-before-completion`: no "passes" without the command and its output at that commit. A failure goes to `plan-to-code` as a fix and counts as a round (step 4).

## 2. Open the pull requests

One pull request per affected repo from `feature/<id>` (D61); the root repo's is the change itself. Each body: a short summary, a link to the change, the acceptance IDs, `Refs #<ticket>`, and links to the other pull requests of the feature. No `Closes`, no AI attribution, no auto-merge. In the ticket body, point the Spec line to the root pull request (D67). Use `finishing-a-development-branch` only for push and pull-request mechanics, never its merge options.

## 3. G2 and G3 on the same version set

Record the version set: every pull request with its base and head commit. Then, in parallel:

- **G2:** a reviewer that is a different model from every implementer of this feature (D52; a new session or another effort of the same model does not count), read-only, in a fresh session, reviews the whole set against the spec, `design.md` and `tasks.md`. Findings carry IDs and are blocking or not.
- **G3:** the required CI checks at each pull request's head. Pending, cancelled, skipped or unknown is not success.

Both verdicts must be for the recorded version set. They go stale when a head changes, a base moves (the default branch advanced), or the spec or `design.md` they were judged against changes.

- A changed head or base: run the gates again. If this happens after PR Pass but before acceptance, set the ticket back to `開發中` with the reason in 下一步, mark the old PR Pass comment superseded, and run steps 1–5 again.
- A changed spec or design: first mark any PR Pass comment superseded and set the ticket to `開發中` with 下一步 naming the re-approval needed; then stop. The spec change goes through `feature-to-spec` and its confirmation, a design or plan change through `spec-to-plan` and a new start approval; only then are the gates run again.

## 4. Fix loop, at most three rounds

Collect every G2 blocking finding and G3 code failure of one version set into one batch. `plan-to-code` fixes the batch, each fix with a Red tied to its finding; push; record the new version set; run G1, G2 (resume the same reviewer session) and G3 again. A round is one batch, which `plan-to-code` records on the ticket with a batch ID and counts once it is dispatched (G1 failures in step 1 included); the fix batch for an acceptor's rejection of existing acceptance IDs counts the same way. The limit is three rounds plus any rounds the human's recorded decisions added.

- **Beyond the plan:** a fix that needs a new task, paths no task owns, or a change to what a task promises (behaviour, acceptance mapping, design, or rewriting or dropping a planned test) goes back to `spec-to-plan`: post a ticket comment that the start approval no longer covers the plan (name the finding) and set 下一步 to the Engineer revising it; amend the plan, get a clean plan review and a new start approval, then `plan-to-code`. A regression test for a finding inside the approved scope is part of the fix, not a plan change.
- **Infrastructure failures** (runner lost, network, quota) are not code rounds: retry each at most twice, recorded separately; an unknown outcome or retries used up is saved and handed back as Blocked (`Blocked：infrastructure`), as in the last item.
- **Disputed finding:** send the rebuttal and its evidence to the independent reviewer once; a blocking finding still disputed after that goes to the human as Blocked (`Blocked：disputed finding`), as in the last item.
- **Limit:** when the limit is used without passing, stop: set the ticket to `Blocked：correction limit`. Every Blocked hand-back here sets 下一步 to the human who decides, posts one Blocked comment: the run id (or who ran it by hand), the change id and the commits it applies to, the problem, what was tried with its evidence, the options, and who decides, and hands over.

## 5. PR Pass package

When G1, G2 and G3 pass for the current version set, post one ticket comment, the PR Pass package, with:

- who posted it and when, and the run id, or "run by hand by <person>" before the controller exists;
- correction rounds used so far, and the limit, from the batch comments on the ticket;
- change id and the spec commit it implements;
- for each affected repo: the pull request, its base and head commit, CI run and review links;
- each acceptance ID with its result and the evidence, all for the current heads;
- review outcome: findings, how each was resolved, anything accepted as is;
- risks, known limits and anything not covered;
- the worktree and branch the work lives on. Link it from the ticket's 驗收 section; set the state to `待驗收` and 下一步 to the acceptor (D67). Leave every acceptance box unticked.

## 6. Stop

Hand over to the acceptor. Do not merge, tick acceptance boxes, set 已接受, archive, delete branches or close the ticket; that belongs to the acceptor and `project-lead`.

## Red flags

| Thought | Reality |
| --- | --- |
| "Two fresh subagents reviewed it" | Same model as the implementer: not an independent G2 |
| "Tests passed in my worktree" | G1 runs in a fresh clone at the proposed head |
| "One more fix round will do it" | Three rounds, then Blocked for the human |
| "CI is still running but review is clean" | G3 pending is not a pass |
