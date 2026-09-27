# Revision-12 independent document review

**Verdict: `changes_requested`.** Of the original 16 Opus findings, 15 are verified as document fixes and M5 retains a one-line normative inconsistency. Two additional blocking-for-design interactions remain in the new base-integration route.

This verdict covers those corrections and their affected interactions. It is not D11 approval, implementation authorization, a product gate verdict, or a conclusion that all 88 AC are sufficiently tested. “Verified” below means the original concrete document defect is repaired; it does not conceal the separately identified regressions.

## Required corrections

### R12-01 — Base integration can wait for gates that it must precede

**Major; blocking for design.** Evidence: `design.md` §1 line 19, §8 lines 207 and 213–223, §9 line 253; `validation.md` g6, h13 and r12; `spec-delta.md` §3 AC-G17. The retained baseline FIN-03 exception is `inputs/baseline-spec-delta.md` line 284.

Take a valid feature head H against B0. Before the next formal review, base advances to B1 and `mergeable=false` sets `integration_required`. The G1 table routes this branch through integration and a new H; G2 is invalidated and cannot run before applicable G1. Yet the integration rule and r12 wait for same-version review/CI before opening the integration batch. No rule resolves this ordering cycle.

There is also a concrete CI version of the same dead end: if the PR opens or synchronizes while conflicting, the candidate’s only workflow trigger cannot produce the awaited run. GitHub documents that `pull_request` workflows do not run until merge conflicts are resolved. [GitHub event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)

**Smallest compatible fix:** use the existing `pre_review_g1` mechanism with an explicit `base_integration` reason for an authoritative conflict/human trigger that must be resolved before current-version checking can complete. Keep one writer, one batch and one round on dispatch; include known problems and explicitly invalidate/stop obsolete in-flight work before correction. Do not wait for an unstartable G2 or conflict-suppressed CI. Keep normal same-version collection when applicable G1 has passed and review/CI are genuinely running. After integration, obtain full new-head G1/G2/G3. Missing CI never becomes success; no extra workflow trigger or platform is needed.

Extend h13/r12 with the pre-G1/conflicted-PR/no-CI case and retain the ordinary in-flight-review case. Assert no premature G2, one correction round, no competing writer and full latest-head gates afterward.

### R12-02 — Merge scope and Red scope are not reconciled

**Major; blocking for design.** Evidence: `design.md` §7 lines 152–160 and §8 lines 221–223; `spec-delta.md` §3 lines 45–50; `validation.md` g3b(a), g13 and r12; formal DUR-02 in `inputs/durable-delivery-spec.md` line 27.

Suppose a finding owns A and its regression test, while the incoming base also changes unrelated B. The prescribed merge necessarily imports B into the worktree and merge commit. The assignment only adds a base tip; it never defines authorization for imported paths or distinguishes upstream contents from authored fixes. The unchanged Red scope rule requires the attempt’s commit scope to stay inside the batch finding scope. A faithful merge therefore either fails scope validation or relies on an undocumented broad exemption. A clean merge importing upstream behavior also lacks an explicit boundary against the blanket requirement for Red on every behavior-changing correction attempt.

**Smallest compatible fix:** bind the integration assignment to the old feature head and exact adopted base tip. Explicitly authorize importing that pinned baseline and separate unchanged incoming changes from Implementer-authored conflict/fix edits. Keep authored edits/tests in the approved batch scope; behavioral resolutions require genuine original Red tied to a stable integration finding/reason and the batch. Mechanical adoption of existing baseline behavior must not require manufacturing its Red. Any additional authored edit remains subject to scope checks; out-of-scope resolutions go through D11. Preserve both parents/lineage and new-head Green/review/CI. This needs a narrow integration contract, not a semantic-diff framework.

Extend g13/r12 with an unrelated incoming path plus a valid in-scope resolution, then with an extra out-of-scope authored edit. The first must be executable, the second rejected. Keep the missing-resolution-Red negative case and an explicit clean-baseline-merge case.

### M5 residual — Formal skip wording contradicts the allowed exception

`design.md` §11 allows skips produced by `only_on` on the non-owning platform; `validation.md` t1 requires exit 0 for a Linux-only case on macOS. But `spec-delta.md` §6 line 92 includes **“非所屬平台 marker 產生的 skip”** in the list that SHALL fail the session. This does not unambiguously preserve the sole allowed exception and reads opposite to t1.

Replace that clause with the design’s exact predicate: **“任何不是由 `only_on` 在非所屬平台產生的 skip”**. Keep t1’s success and t2/t3’s failures. Because T0.1 will adopt this normative delta, agreement must be fixed in the source rather than left to an implementer’s interpretation.

## Original 16 findings

| ID | Disposition | Rationale and evidence |
| --- | --- | --- |
| M1 | `verified` | The original hidden-run failures are covered: PR-only event identity, every same-head run’s latest attempt, queued attempts and all pages; no fallback to another run’s success. Evidence: design.md §8 Run/attempt (191–202); validation.md h4, h4a–h4e; spec-delta.md §6 AC-G14. |
| M2 | `verified` | Behavior-changing correction attempts now need original Red bound to finding and batch. Abandoned-attempt Red is not transferred; missing original evidence Blocks. Integration-specific scope interaction is separately R12-02. Evidence: design.md §7 (150–163), §9 Batch; validation.md g10–g11, r11; spec-delta.md §3. |
| M3 | `verified` | The original rebase/force-push lineage defect is repaired by local merge commits, ordinary fast-forward push and explicit history_rewritten blocking. Executability of that replacement is separately R12-01/R12-02. Evidence: design.md §4 (74–77), §7 (163), §8 (219–223); validation.md g12–g13, h11; spec-delta.md §1 Branch history. |
| M4 | `verified` | T2.3 now owns generic observation and worker/native reads, so w5/w8 no longer depend on T6.1. T2.2 records recovery decisions, while T2.3 applies their effects; d9 explicitly does no fetch. Shared observe/gates ownership and the stated execution order are acyclic. Evidence: tasks.md execution table (55–68), shared files (72–81); validation.md d9, o1–o2, w5, w8, w10, h13, r12. |
| M5 | `still_open` | Design and planned tests close the Linux-skipped-everywhere hole, but spec-delta §6 line 92 names “非所屬平台 marker 產生的 skip” among mandatory session failures. That conflicts with the allowed non-owning-platform skip in design §11 and the exit-0 assertion in t1. The adoption source must carry the same unambiguous negation as the design. Evidence: design.md §11 (284–295); validation.md §0, t1–t6, h2; spec-delta.md §6 (92). |
| M6 | `verified` | PR expected repo/head/base/SHA identity and marker are persisted before creation; wrong-base or wrong-SHA existing PRs Block without creation. Unknown-create readback requires marker plus identity; explicit human binding records origin=existing. Evidence: design.md §4 (78–95); validation.md h10; spec-delta.md §1. |
| m1 | `verified` | The package is a state projection containing versions, gate reasons/evidence, findings, limitations, policy source and github_rules_verified, publication receipts and pending acceptance. p1 asserts both rules and approved-policy cases. Evidence: design.md §8 Pass package (230–239); validation.md p1; tasks.md T6.2; spec-delta.md §9 ORC-05. |
| m2 | `verified` | O23 partial continuation is explicitly proposed for S2 in all relevant lists and the delta; whole-run stopping is the first-slice behavior and is not claimed as full O23 completion. Evidence: design.md §1 (28); tasks.md deferred (115); spec-delta.md §9 (123); coverage.md AC-O23; validation.md d4, W-C. |
| m3 | `verified` | N/A follows actual behavior and independent eligibility, including comment-only config/test files. Behavioral edits remain ineligible; G2/G3 are not waived. Evidence: design.md §7 N/A (168–172); validation.md g7–g8; spec-delta.md §4. |
| m4 | `verified` | T0.1 owns full formal-spec composition from formal text plus both pinned deltas, per-requirement/all-88-AC mapping, independent document verification, replacement of competing old design/tasks/validation and commit B before assignments. Evidence: tasks.md T0.1 (27–46); README.md pending adoption; spec-delta.md header; result.json SPEC-ADOPTION. |
| m5 | `verified` | The previously absent triggers are now explicit: mergeable=false, an incompatibility finding, or human revise; null waits with a bound. The new scheduling interaction is R12-01, so verification of this definition is not approval of the integration route. Evidence: design.md §8 (213–223); validation.md h13, r12; spec-delta.md §3 AC-G17. |
| m6 | `verified` | Each job has an attempt-specific tested-SHA artifact with run, attempt, job, check and SHA equality checks; missing, stale or mismatched artifacts cannot pass. Evidence: design.md §8 (200); validation.md h12, §6 (230–233); spec-delta.md §6 (90); tasks.md T1.1, B1. |
| m7 | `verified` | Recovery records decisions and performs no external write. Bind requires a fresh identity check; not-delivered requires authoritative evidence, query absence is rejected, and any later retry retains the operation budget and PR pre-query. Evidence: design.md §4 (93–95); validation.md d9, w10, h10; spec-delta.md §1 (20); tasks.md T2.2/T2.3. |
| m8 | `verified` | Repo-root workflow.yaml is clearly distinct from the GitHub workflow, is owned by T1.1, pins that workflow’s blob digest and requires policy_change for changes; digest mismatch Blocks. Evidence: design.md §8 (185); tasks.md T1.1, shared files (79); validation.md h1, §6 (234–235); spec-delta.md §6. |
| m9 | `verified` | G2 blocked now makes the feature Blocked without opening another correction round; r1 checks the feature state and absence of dispatch. Evidence: design.md §8 (180); validation.md r1; spec-delta.md §5 (76); tasks.md T5.1. |
| m10 | `verified` | Current headers and status consistently say revision-12, fix_submitted and pending review. Historical GPT/D51 closure and the original Opus review are identified separately, and D11/product evidence remain pending. Evidence: README.md status/review table; all candidate Markdown headers; result.json; revision-12.json. |

## Other checked interactions

The changed T2.3/T6.1 dependency is repaired. Worker/native observation belongs to T2.3; PR/CI extends it later. `decisions.py` records recovery decisions while `writes.py`/`observe.py` apply effects, and d9 tests that separation. The explicit task order and sequential shared-file order contain no backward dependency introduced by these fixes. The unexecutable owned-scope seam found is R12-02.

CI cannot pass on a newer run while hiding the latest failed/pending attempt of another same-head run. Event/PR mismatches, unsupported sources and unmatched per-job tested-SHA artifacts are rejected. GitHub supports rerunning only failed or selected jobs; the proposed full latest-attempt artifact requirement can therefore reject an otherwise green partial rerun. I treat this as conservative evidence rejection, not a false-pass defect or a requirement to build rerun orchestration. [GitHub rerun documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs) The artifact API supports listing and downloading artifacts, so the proposed content check requires inspecting the artifact, not inferring all job fields from its name alone. [GitHub artifact API](https://docs.github.com/en/rest/actions/artifacts)

The new unknown-write resolution has no automatic write side effect: `--bind` requires a fresh identity match, and `--not-delivered` requires authoritative non-delivery evidence, not query absence. Later retries retain their budget and PR pre-query. No unsafe replay authorization was found in these corrected rules.

N/A follows actual behavior. T0.1 owns adoption of the complete formal text plus both pinned deltas and replacement of competing old design/tasks/validation. O23/G15/runtime deferrals remain declared proposals for D11; this review does not adopt them.

## Inputs, checks and limits

- Read all 17 manifest-pinned inputs in full: seven candidate Markdown documents, candidate `result.json` and `revision-12.json`, original review, decisions, project intent, four formal specs and the baseline delta.
- Independently recomputed SHA-256 for all 17: every byte hash matches `input-manifest.json`; the JSON result records each expected/actual pair. The coordinator reports comparing the five supplied spec/baseline copies with originals; I did not repeat that outside-snapshot comparison.
- Checked exactly the 16 original response IDs, and counted 105 unique coverage rows: 88 AC plus 17 historical S1 findings. This was a correction/interactions review, not a fresh proof of adequacy for every AC row.
- No product code, tests, runtime probes, GitHub repository operations or formal adoption were performed. Public official GitHub documentation was read only for the stated platform facts. Only this report and `review-result.json` were written.
- All 88 AC remain planned, all 17 old S1 findings remain open, and D11 remains pending. Historical D51-R01–R07 closure is distinct from the 16 Opus findings and supplies no current product evidence.
