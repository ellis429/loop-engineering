# Bounded re-review — D45-04 revision-16

**Verdict: `changes_requested`.** Eight R15 findings are verified; R15-01 and R15-02 remain partial. There is one new blocking finding, R16-01, which explains the remaining task-order problem in R15-01, and one new non-blocking finding, R16-02. These represent **two unresolved blocking areas**, not three independent blockers.

Assignment: `herdr-design-plan-20260928-01 / review-r16-01`. Independent reviewer; no candidate authorship or edits. Reviewer: `gpt-6-astra`, effort `xhigh`, as reported by the current Codex run header in `stdout.log`; session `01a0e40b-8274-7bd1-bdf7-5daa15200a48`. Only header metadata was inspected for identity.

All **28/28 SHA-256 entries** in `input-manifest.json` were recomputed **before substantive review** and matched. The author's eight `before_sha256` values also match the pinned reviewed-r15 entries. The review compared every changed file against `inputs/reviewed-r15/`, checked the prior expected fixes, and traced relevant formal-spec/D45-02/D45-04 requirements, decisions, tasks, validation, coverage and D11 references. Author `fix_submitted` labels were treated as claims, not verification.

## R15 dispositions

Locations below are in `inputs/candidate/` unless another source is named. “Verified” refers to the document fix, not executed product behavior.

| Finding | Status | Evidence and remaining work |
| --- | --- | --- |
| R15-01 | **partial** | `design.md` §7, lines 220–225, adds evidence activities, `min(900 seconds, remaining active)`, process-group termination, invalid Red/non-passing G1, Blocked, no redispatch/retry, and cleanup handoff. §10 counts the intervals and unresolved periods. `validation.md` g15/b1 and D11 §3 E cover the new behavior/value. The remaining-budget and `next`/stop check is nevertheless required before its T7.1 owner exists: see R16-01. |
| R15-02 | **partial** | `design.md` §8, lines 245–252, supplies per-ID dispositions/responses, evidence, omission behavior and the common identity/version envelope. `tasks.md` T2.3/T5.1 and the `assignments.py` ownership row define the extension point. r4/r6/r8 cover partial verification, omission, stale head and disputes through public import. r10 now preserves prior review/version and fix/commit references, but only for **correction** assignments. The review-assignment definition at line 244 still lacks those explicit references; see the residual below. |
| R15-03 | **verified** | `tasks.md` lines 115 and 129–130 explicitly separate T6.1 wait-start/mergeability observation from T7.1 expiry and routing. h13 delegates timeout to b4; b4 retains G3 unknown/Blocked, no rerun and no correction round. This fixes the original split without a reverse edge. |
| R15-04 | **verified** | `validation.md` §6.1/§6.2 uses two required jobs, both running the suite and platform policy; `unit-linux` also runs ruff, mypy and dist-smoke. t7 checks the actual proposed workflow sequence and missing-test/wrong-trigger/missing-job variants; B1 supplies subsequent real execution. T1.1, design §8, coverage AC-G13 and D11 §3 D agree. R16-02 concerns only the stale rationale. |
| R15-05 | **verified** | T1.1 owned paths/card/completion (`tasks.md` lines 78, 123, 141) require a new committed `uv.lock` with `pyproject.toml` and successful fresh-clone `uv sync --frozen`. The shared-file row at line 111 assigns paired updates to later dependency-changing tasks. The legacy lockfile remains excluded from W1. |
| R15-06 | **verified** | `design.md` §6, lines 178–183, compares requested/actual repo/worktree/branch using native session placement and fails absent native evidence or input-accepted-only. f6 covers wrong worktree/branch and shell-cwd-only evidence. f5 independently varies denial and resource changes for every mandatory probe, including `gh` and `herdr`. R1 references the complete receipt; T1.1/T1.2 and AC-D18 carry the change. |
| R15-07 | **verified** | `design.md` §10 makes effects decision-ID-idempotent and target-specific, preserving other blockers/counters. b5 verifies 4h→5h once and writer/stop guards; r14 verifies one fourth round, no fifth after replay, and writer-unknown blocking. b6 covers target isolation/replay for unit/head extensions; d10 keeps authorization negatives. T7.1 owns active/attempts/CI effects, T5.1 owns rounds, and the CLI-main test convention covers time-dependent public-path cases. AC-D17/AC-F07 references agree. |
| R15-08 | **verified** | h11 now supplies H on another ref/fork while the prepared target lacks H, requiring no succeeded receipt, unknown/Blocked and zero resend. The original wrong-SHA and non-fast-forward cases remain; T6.1/coverage references retain ownership. |
| R15-09 | **verified** | `spec-delta.md` introduction/§1 explicitly restores the completed/no-later-effect permission and one human-authorized new readback. Only the local-synchronous exception is removed from the spec retry list; D11 §3 A discloses it. `design.md` §4 line 95 distinguishes temporary local Green checkouts from external-write ops. These retry conditions permit safe retries; they do not require automation of every permitted retry, so the conservative design subset is not a new spec violation. |
| R15-10 | **verified** | `spec-delta.md` §12 line 187 explicitly replaces the remaining finding-resolution Purpose phrase, handles old validation references, forbids current D40 approval claims in composed Purpose/banner text, and preserves historical `approval.json`. T0.1 retains independent source-map review after D11. |

The remaining **R15-02** issue is the reviewer input handoff. D45-02 §4 FIN-03, line 284, requires both “派修與覆核的 assignment” to carry each finding's full content, basis, expected behavior, and previous review/fix evidence references. Revision-16 explicitly adds these to the **修正 assignment** at design line 252 and tests **派修的 assignment** in r10. The separate **Review assignment** at line 244 still enumerates finding ID/category/location/basis/expectation/status/object digest, without explicitly including the prior result/version and fix evidence. An object digest alone does not specify that its referenced object contains those missing inputs.

Extend the same immutable snapshot contract to full re-review and dispute-review assignments, and extend r10 or an existing handoff case to verify their prior review/version, fix/commit and relevant counterevidence references survive later registry changes. This is the unfinished portion of R15-02, not a new finding or a request for another result framework. The new output dispositions and importer split are otherwise adequate.

## New findings introduced by revision-16

### R16-01 — blocking, major: evidence deadline test depends on a later task

**Location:** `tasks.md` T3.1/T7.1 rows at lines 83–85, order at 94, `next.py` ownership at 105, cards at 128–130, and T3.1 completion at 146; `validation.md` g15(b), line 140; `design.md` §7 lines 222–225 and §10 lines 380–386.

The new T3.1 completion criterion requires all of g15 to pass. g15(b) must use the remaining active budget and then have public `next` prioritize the expired stop. T3.1 explicitly excludes active-union calculation. T7.1 owns that calculation and deadline routing in `next`/`safety`, and depends on T3.1 and T6.1. The prescribed sequence is therefore:

`T3.1 must pass g15(b) → needs T7.1 behavior → T7.1 cannot start until T3.1 and T6.1 finish`.

The explicit dependency column is acyclic, but its new acceptance criterion introduces a backward dependency. Neither an earlier remaining-budget/deadline interface nor a staged fixture/integration boundary is defined. A fresh T3.1 implementer must cross another task's ownership, invent a temporary interface, or leave a required completion assertion failing.

**Basis:** The handoff requires independently assignable tasks, explicit adjacent interfaces and dependency-satisfied verification. D12 makes the required-verification gap blocking; D13/D47 and retained DUR-08/AC-D17 require the actual budget and safety behavior. Unlike the former R15-03 ambiguity, these cards expressly exclude the calculation from the early task and assign routing to the later one.

**Expected fix:** Establish an earlier owned remaining-budget/deadline seam for T3.1's local runner, then place the public `next`/safety integration assertion with T7.1; alternatively split/reorder the necessary budget work. Update task cards, shared-file ownership, dependencies, test ownership, completion conditions and coverage together. Retain real verification of elapsed-time accounting, the shorter remaining-budget bound, stop priority and zero redispatch. Adding a reverse edge or stubbing the complete public-path assertion would not resolve it.

This is the remaining interaction behind R15-01's partial status; it is not counted as a third independent blocking area.

### R16-02 — non-blocking, minor: CI timeout rationale still describes three jobs

**Location:** `design.md` §10 line 395, compared with `validation.md` §6.1 lines 271–278 and D11 §3 D.

The rationale says CI has three jobs, each expected to finish within five minutes. Revision-16 removes `static` and moves its commands into `unit-linux`, leaving two jobs. The operative workflow/policy/D11 definitions agree, but the explanatory estimate refers to the previous topology.

**Expected fix:** Describe the two proposed jobs and the additional Linux commands; keep durations explicitly estimated until real execution. This does not weaken a gate or require changing the timeout, and is not blocking.

## The 11 previously partial helper items

**9 verified; 2 partial; 0 not_addressed.** The helper reports themselves were not included in this input set, so these judgments use the pinned prior review's helper dispositions and stated gaps.

| ID | Status | Evidence |
| --- | --- | --- |
| SS-02 | verified | `spec-delta.md` §1 restores the missing retry/readback wording and explains temporary checkouts; R15-09. |
| SS-09 | verified | Two test-running jobs, t7, committed new lockfile ownership and fresh-clone completion; R15-04/05. R16-02 is a separate explanatory inconsistency. |
| SS-10 | **partial** | Evidence execution is now bounded/counted and extension effects have tests, but the deadline verification has the unresolved T3.1/T7.1 dependency; R15-01/R16-01. |
| PA-05 | verified | Common envelope, correction responses and the T2.3→T5.1 body-validation extension are explicit. |
| PA-07 | verified | h13 tests observation/trigger classification; b4/T7.1 tests expiry/routing; R15-03. |
| PA-08 | verified | b5/r14 verify active/round extension effects and replay/guard behavior with explicit owners; R15-07. |
| PA-11 | verified | Per-finding reviewer dispositions, closure evidence, omission rules and importer handoff are defined and exercised by r4/r8. The remaining assignment-input gap is under PA-24/R15-02. |
| PA-22 | verified | h11 includes the desired SHA on the wrong ref/fork; h10's G1-before-push negative remains. |
| PA-24 | **partial** | r10 preserves prior review/version and fix references for correction assignments, but the same requirement is not explicit/tested for re-review assignments; R15-02. |
| PA-25 | verified | f5 independently tests every permission probe; f6 tests native placement; R1 remains the real capability proof and R2 still requires G1 passed. |
| PA-27 | verified | `validation.md` §4 line 250 adds a `proof.md` rubric negative for falsely claiming completion after no finding or Blocked, assigned to T4.3. r1/R3 retain no fabricated blocker and incomplete-demo rules. |

## Interaction checks and preserved scope

- Inventory checks found **88 unique formal ACs**, all present in **105 unique coverage rows** (88 ACs plus 17 legacy findings), and **109 unique product-matrix rows**. The added rows are t7, g15, r14, b5, b6 and f6. These counts do not establish verification sufficiency.
- Changed coverage and cleanup references point to the new rows. The explicit dependency graph remains acyclic; R16-01 is the semantic prerequisite that the graph omits. The repaired T6.1/T7.1 CI split and the new T2.3/T5.1 result-validation split otherwise preserve their order.
- The revised CI proposal preserves per-job tested-SHA identity, platform/skip policy and real B1 execution. D11 D/E disclose the two-job set and evidence-command bound. The alternative without macOS consistently retains only `unit-linux`.
- Changed review/closure text preserves independent, versioned, evidenced closure; `clean` alone closes nothing. Unchanged lineage, integration-routing and original worker/native split fixes were not reopened. The changed h12 job-count wording preserves the earlier per-job identity requirement.
- README, D11 and `revision-16.json` continue to say pending approval/no product execution. Historical review status is not carried forward as revision-16 clean. The Purpose composition fix applies only after D11. No new resident service, general scheduler, test registry or sandbox platform is introduced beyond D50.

## Limits

This is a bounded review of the supplied documents and complete revision-15→16 diff, not a fresh all-AC audit or D11 approval. Previously verified items were inspected only where changed supporting text could affect them. No product code or tests, Herdr/Claude/OpenCode inference, permission/placement probes, R1–R3, Actions runs, GitHub writes, W1/adoption, merge or example launch were performed. No runtime availability, current remote policy or historical native-model claim is certified. External references and publication-manifest contents absent from the supplied snapshot were not independently authenticated.

Only `review.md` and `review-result.json` were authored. Inputs were not modified. All ACs remain planned and all 17 legacy S1 findings remain open. The current reviewer identity comes from this run's header, not the candidate's requested profile or the prior reviewer's metadata.
