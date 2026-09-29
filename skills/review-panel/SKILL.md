---
name: review-panel
description: Use when a change needs an independent review that should not rest on one reviewer's blind spots, such as the whole-change review (G2) of a feature's pull requests or the per-task review of a high-risk task. Recommended, not required; the Engineer may choose a single reviewer. Not for fixing findings (plan-to-code) or running the gates (to-pr).
---

# Review panel

Review a change with two or more independent reviewers from different vendors, each looking from a different angle, then merge their findings, have each finding checked by a reviewer that did not raise it, and re-review the whole merged list after fixes (D73).

Why: in the blind cross-checks of the A/B/C rerun (tasks T2.2 and T2.3), 21 of 25 defects were raised by only one arm's reviewers, and every arm's own final state still held two to five major defects. In a trial of this skill, the second reviewer raised seven reproduced findings the first missed, but the panel did not find more of the known residual defects than a single reviewer did. Reviewers differ a lot from run to run; a second vendor adds coverage, not certainty. That is why this is recommended, not required.

Read repository instructions first; they override this skill.

## 1. Set up the panel

- **Scope:** the version set (each pull request's base and head) or the task's range; the spec, `design.md`, `tasks.md` and the acceptance IDs it must meet.
- **Reviewers:** at least two, from different vendors (for example GPT-6 Sol through `codex exec`, Claude Opus through `claude -p`). Each is a different model from every implementer of the change (D52) and a strong model, at the planned Reviewer effort (the task's for a per-task review; the highest of the feature's tasks for G2), in a fresh session on its own fresh clone of the reviewed version. The review is read-only: it changes nothing in the repository and pushes nothing. It may run the tests, and writes any reproduction scripts and their output to a scratch folder outside the clone that the coordinator gives it; that folder is the only place it writes.
- **Angles:** every reviewer gets the same inputs and reports anything it finds, but leads with one angle:
  1. **Spec and acceptance:** for each scenario, try to build an input or sequence that violates it.
  2. **State and failure paths:** repeated, resent, concurrent, interrupted and out-of-order operations, and what they leave in the state for later steps.
  3. **Tests and evidence:** does each Red reach the behaviour, and which rows have no test that would fail if the behaviour broke.
  With two reviewers, give angle 1 to one and angle 2 to the other; both also cover angle 3. Run them in parallel.
- Tell every reviewer not to use commit messages, history or earlier review notes as evidence.

## 2. Merge and cross-verify

- Merge the findings into one list with stable IDs; findings about the same wrong behaviour are one entry. Note who raised each. A finding raised by two reviewers independently stands without further checking.
- Send each other finding to a reviewer that did not raise it, resuming that reviewer's session, to confirm it with a reproduction or refute it with evidence. A new finding that appears during this step joins the list and is checked the same way by the other reviewer.
  - Confirmed, or not refuted: it stands.
  - Refuted: show the refutation to the reviewer that raised it, once, in its session. If it withdraws, the finding is dropped and both sides are kept in the record. If it holds, the finding stands and the dispute goes to the human, with both sides.
  - Never drop a finding on the other reviewer's word alone, and never settle between reviewers what the spec requires: a dispute over the spec's meaning or scope goes to the human.
- Severity: when the reviewers rate a standing finding differently, it takes the higher rating; a disagreement over whether it blocks goes to the human.

## 3. Re-review after fixes

Every reviewer re-checks the whole merged list at the new head, not only its own findings, and reports anything the fixes broke. Resume each reviewer's session. A new finding from the re-review joins the merged list and goes through step 2 like any other.

## 4. Record

One ticket comment: the reviewers (model, vendor, effort, angle), the version set or range, each merged finding with who raised it and who verified it, and a coverage line: how many of the standing findings each reviewer raised alone and how many both raised. This comment is the G2 record for `to-pr`, or the per-task review record for `plan-to-code`.

## One reviewer instead

The Engineer may choose a single reviewer, for example for documentation or configuration only. The record says so. Everything else in `to-pr` and `plan-to-code` still applies.

## Red flags

| Thought | Reality |
| --- | --- |
| "The reviewer said clean, so it is clean" | In the rerun, one reviewer's clean still held two to five major defects |
| "Run the same model twice at a higher effort" | Same model, same blind spots; add a reviewer from another vendor |
| "Each reviewer re-checks only its own findings" | Fixes for one finding can break another; re-check the merged list |
| "The other reviewer refuted it, drop it" | In the trial, a refutation dropped a defect that blind judges later confirmed; the raiser answers once, then the human decides |
