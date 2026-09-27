# Revision-13 bounded independent re-review

**Verdict: `changes_requested`.** M5 and R12-02 are verified. R12-01 has one remaining route-predicate overlap. No new finding or scope expansion is requested.

The original 16 Opus findings are now all verified as document corrections; the separate R12-01 regression still prevents a clean candidate verdict. This is not D11 approval, product validation, or an assessment that all 88 AC have sufficient tests.

## R12-01 — Still open: the mixed state selects both routes

**Major; blocking for design.** Evidence: `design.md` §8 “路徑選擇”, `spec-delta.md` §3 AC-G17 “路徑”, `validation.md` r12(a)–(b), and `tasks.md` T5.1 completion condition.

Use this exact state: H has applicable passed G1, its G2 review is active, and the PR is conflicted with no candidate CI run. Route 1 matches because the review is in flight and directs collection of review/CI. Route 2 also explicitly includes the conflicted/no-CI state. There is no stated precedence, so the implementation can still choose to wait for CI that cannot start. The new tests cover both-in-flight and pre-G1/no-CI, but not this mixed state.

**Smallest fix:** give unavailable, obsolete or unstartable required evidence priority. Normal collection requires applicable G1 **and each of G2/G3** to be either terminal or genuinely in flight. Otherwise an established integration trigger uses the existing `pre_review_g1` / `base_integration` path. Preserve writer termination, correction-round and active-budget guards; the routing exception must not grant a new budget or treat missing CI as success. Add the mixed state above to r12 and assert one batch/round, no new premature G2, and full new-head gates after integration.

The existing single-writer and new-head G1/G2/G3 requirements are retained. This asks only for a deterministic boundary between the two already proposed routes.

## Verified bounded corrections

- **M5:** the formal delta now uses the exact design predicate, “任何不是由 `only_on` 在非所屬平台產生的 skip”. It agrees with t1 exit 0 and t2/t3 failure. The prior normative wording residual is closed.
- **R12-02:** the integration assignment pins prior H and incoming B and distinguishes inherited baseline input from authored conflict/fix edits. Exact parents and reproducible `merge-tree` comparison support that distinction. Pure import neither fabricates upstream Red nor claims behavior N/A; authored behavioral changes still need original Red, and extra out-of-scope changes are rejected. g13(a)–(f), T3.1 ownership and T5.1 assignment ownership cover the defined cases. Prior feature Red lineage and complete latest-head gates remain required.
- The partial-job-rerun note explicitly describes conservative rejection and reads artifact contents, without adding rerun capability. Status headers point to README. Planned coordinator status/link edits are publication bookkeeping, not author self-approval.

## Original 16 dispositions

| ID | Disposition | Evidence / retained result |
| --- | --- | --- |
| M1 | `verified` | Design §8 run/attempt rules and h4/h4a–h4e remain intact; artifact content inspection is clarified. |
| M2 | `verified` | Design §7, g10/g11/r11 retain original correction Red and abandoned-attempt rules; R12-02 now separates inherited baseline input. |
| M3 | `verified` | Fast-forward push, local merge and history-rewrite rejection remain; exact [H,B] parents reinforce lineage. R12-01 is separately open. |
| M4 | `verified` | T2.3 worker/native observation and T6.1 extension order remain intact. T3.1 now expressly owns the merge-evidence tool/checks. |
| M5 | `verified` | Spec delta §6 now matches design §11 and t1/t2/t3; the residual is closed. |
| M6 | `verified` | Design §4/h10 expected PR identity, marker and mismatched-existing-PR rejection are unchanged. |
| m1 | `verified` | Pass package projection/content and p1 assertions are unchanged. |
| m2 | `verified` | O23 partial S2 deferral remains explicit in design/tasks/spec delta/coverage. |
| m3 | `verified` | Behavior-based independent N/A eligibility and g7/g8 remain unchanged; pure base import is explicitly not behavior N/A. |
| m4 | `verified` | T0.1 complete formal adoption, both pinned deltas, independent mapping check and old-plan supersession remain unchanged. |
| m5 | `verified` | Explicit mergeability/finding/human triggers remain; their scheduling overlap is tracked under R12-01. |
| m6 | `verified` | Per-job/run/attempt/check/SHA identity remains mandatory; contents are explicitly read, partial-rerun limitation documented. |
| m7 | `verified` | Record-only unknown-write recovery, authoritative non-delivery evidence and retry bounds remain unchanged. |
| m8 | `verified` | T1.1 workflow.yaml ownership and workflow-digest/policy_change checks remain unchanged. |
| m9 | `verified` | G2 blocked still Blocks the feature without dispatching a correction; the integration route does not grant G2 success. |
| m10 | `verified` | Headers consistently identify revision-13 and defer current review status to README; historical verdicts are distinguished. |

## Checks and limits

- Reviewed `revision-13.json` and the complete candidate diffs against review-01; retained the previously read authorities after verifying byte identity. All 19 manifest hashes match. The JSON result records every expected/actual hash.
- Confirmed all seven authority inputs and historical `revision-12.json` are unchanged; the supplied review-01 is an exact copy. All 105 coverage IDs/order remain unchanged: 88 AC and 17 old S1 findings.
- The coordinator reports local Git 2.54.0 supports `merge-tree --write-tree`; I did not perform a capability probe or product test. No implementation, runtime or GitHub repository actions were taken. Only these two review files were written.
- All 88 AC remain planned, all 17 historical S1 findings remain open, D11 is pending, and the historical D51 review is distinct. No product gate is passed; no formal deferral/narrowing is adopted by this document review.
