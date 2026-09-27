# Independent candidate document review

Verdict: **changes_required**. This is formative feedback on `design.md` (`draft_pending_sync`) and review of the delivered cleanup/policy documents, **not rejection of a claimed-ready design, product G2, or implementation approval**. Pending spec-delta/tasks/validation/coverage are intentionally excluded.

The direction fits D41/D46: one feature authority, short controller calls, native runtime execution, isolated rebuilding and selective extraction. Module count alone does not establish overengineering. The issues below concern actual call contracts, retained behavior, and unnecessary mandatory work.

## Findings

**D45-R01 — High; blocks eventual design readiness. Consume execution permission in one place.**
`design.md:78`, `design.md:137`, `design.md:319` assign `begin` both to the tool and to orchestrate before calling that tool. Counterexample: orchestrate receives `execute:true`, then the tool calls `api.begin` and receives `execute:false` because the operation is already in flight. Alternatively, bypassing the second check leaves tool execution authority unspecified. Basis: AC-D12/D13 and reconciliation gap 1. Smaller fix: orchestrate prepares and invokes one tool command; that command alone calls begin, executes once, and records. Verify through the public CLI, including two concurrent callers; an AST import test cannot establish this behavior.

**D45-R02 — High; blocks eventual design readiness. Allow bounded stopping despite unrelated blockers.**
`design.md:232–235` puts blockers and in-flight reconciliation before budget stopping; `design.md:280` instead promises only stop at deadline. Counterexample: a reviewer is still active when CI policy becomes unknown; once a blocker exists, every next-action request returns blocked, including after 4h. `prepare` accepts only next_action (`design.md:228`), so the known worker cannot receive the promised stop permit. Basis: DUR-08/AC-D17 and D41 bounded execution, independent of DN-1's offline choice. Fix: distinguish blocked normal work from permitted stop/readback actions; prioritize handling known active workers at deadline without creating a supervisor or treating unknown workers as stopped.

**D45-R03 — High; blocks eventual design readiness. Separate stale results from fresh external observations.**
`design.md:253` discards observations whose version differs from the current key, conflicting with `design.md:265` and the version matrix. Counterexample: saved Pass is H1, a fresh GitHub observation sees H2, and the mismatch rule archives it without invalidating H1. Basis: AC-G16/G17/G18 and AC-D15. Fix: stale assignment results cannot authorize current gates; fresh observations update observed facts and trigger invalidation. Only an observation proven superseded by a later observation should be ignored. Specify ordering without adding another authority.

**D45-R04 — High; blocks eventual design readiness. Add publication to the normal next-action path.**
`design.md:241` moves clean gates directly to Pass observation; `design.md:306` merely registers publication, while `design.md:264` requires both publications to succeed. Counterexample: review and CI are clean, PR publication remains prepared, but the engine keeps requesting Pass observations; the skill only follows next_action (`design.md:319`). Basis: AC-G01 and AC-F13/F14. Fix: explicitly drain the pending PR publication, then its dependent issue summary, before the final Pass observation. Retry/readback must target those original operations. No additional queue/service is needed.

**D45-R05 — Medium; nonblocking simplification. Permit reviewed behavioral tests to be selectively extracted.**
`cleanup-map.md:71–73`, `cleanup-map.md:79–86` mandate rewriting every old test, beyond D46's prohibition on bulk copying. Concrete counterexample: `inputs/tests/test_budget.py::test_overlapping_worker_and_ci_count_once` exercises the same union algorithm that `design.md:277` explicitly retains; changing its import and recording provenance need not recreate it from scratch. Basis: D41 reduced scope and steering-02 selective reuse of necessary behavioral tests. Fix: evaluate individual tests by retained contract, source defects and production coupling; selectively adapt sound cases, retire platform-specific cases, and add new CLI regressions. Do not carry old pass counts forward as new evidence.

**D45-R06 — Medium; nonblocking factual correction. Correct the CLI migration premise.**
`cleanup-map.md:48` says only start/adopt write state. In the supplied baseline, `cli.py:141–160` (`cmd_decide`), `cli.py:165–181` (`_abandon`), and `cli.py:223–239` (`_reconcile_local`) also commit state. The latter is reached by resume/reconcile before external work is refused. Basis: source-backed extraction decisions required by D46. Fix: distinguish “does not drive the delivery loop” (supported) from “does not mutate state” (false), and retain or explicitly replace these decision/budget/history behaviors. Static production references in `cleanup-map.md:92–95` do not prove those paths actually execute.

## Human decisions and limits

DN-1, DN-2 and DN-3 remain **unapproved alternatives**, not design defects merely because they require a choice. DN-1 B/C and DN-2 B add platform responsibilities; they must not enter the default implementation through an assumed fallback. No option is selected here.

Before presenting DN-2 A (`decisions-needed.md:42–46`), explicitly preserve the original historical Red capture: raw output, exit, task/attempt, snapshot and provenance remain mandatory; coordinator replay and transcript review supplement them. Accepting a same-UID threat boundary must not silently authorize reconstructed Red. DN-3 B must remain a repo-scoped, versioned human policy exception, visibly distinct from verified GitHub rules. Neither a 403 response nor the example name `test` constitutes approval. The coordinator-supplied `../ci-policy-recheck.json` confirms a plan-restriction 403; old CI success is execution evidence only, and the old macOS sandbox-only job cannot establish the new runtime profile.

Read-only review of fixed files and selected baseline source/tests. No product code or tests executed, no GitHub operations, no runtime capability claims verified. No conclusions about missing future artifacts or closure of S1 findings. Hashes are recorded in `result.json`.
