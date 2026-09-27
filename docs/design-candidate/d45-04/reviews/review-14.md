# Review 14 — bounded D51 residual check

**Verdict: changes_requested.** Four findings are verified; three have narrow residuals. All nine manifest hashes match and coverage retains exactly the same 105 IDs (88 ACs plus 17 historical findings).

I checked the complete revision-13→14 document diff and the immediately affected contracts. The prior full 88-note semantic assessment is carried only for unchanged mappings; changed mappings were rechecked. This is not another architecture review or a product-gate decision.

| Finding | Result | Evidence |
| --- | --- | --- |
| D51-R01 | Verified: delayed PR creation cannot trigger a second create | design:72–86; validation:h10 |
| D51-R02 | Verified: temporary-merge Green removed; actual H required | design:180; validation:h7 |
| D51-R03 | Residual: opaque run ID used as chronology | design:172; validation:h4 |
| D51-R04 | Verified: already-built T8 candidate removed; selection pending D11 | tasks:78; validation:R3; result remaining decisions |
| D51-R05 | Registry/checker deleted; residual G1/CI dependency | design:238–240; validation:16–18 |
| D51-R06 | Verified: per-sample signatures deleted | validation:152–153; tasks:46,67 |
| D51-R07 | Scope restored; residual insufficient lineage predicate | design:144; validation:g3b |

## D51-R03 — high, blocking residual

**Locations:** design.md:172, validation.md:93, coverage.md:73, spec-delta.md:79.

The contract gives run_id only identity semantics, yet numerically ranks it as chronological order. For the selected workflow, an older successful run with a numerically larger opaque ID can outrank a newer queued run; the ambiguity fallback is never reached because both IDs are sortable. No local input establishes a monotonic run_id guarantee.

**Minimal repair:** For the same bound workflow use run_number for the run sequence and run_attempt within that run; retain run_id as identity, not chronology. Missing or contradictory ordering metadata remains unknown. Add h4 inputs whose IDs do not sort in run_number order and assert the newer queued run wins; synchronize coverage/spec wording.

## D51-R05 — high, blocking residual

**Locations:** design.md:238, design.md:239, validation.md:16, validation.md:17, design.md:78.

The replacement policy rejects missing CI jobs in G1, but the established order requires G1 before push/PR and CI observation. On a new local head with passing local tests and no remote CI jobs yet, this condition blocks the push needed to obtain those jobs.

**Minimal repair:** Keep local required-suite execution, nonempty collection and applicable-skip checks in G1. Put required remote CI job presence/completion in G3. State the separation in design and validation; do not reintroduce the deleted registry/checker.

## D51-R07 — high, blocking residual

**Locations:** design.md:144, spec-delta.md:40, validation.md:78.

Let snapshot S and implementation C be sibling descendants of A, and H contain C but not S. Snapshot parent A is an ancestor of the attempt start and C is an ancestor of H, so the new concrete test passes even when S is unrelated evidence never used by that attempt. Shared-parent ancestry does not establish snapshot→attempt applicability.

**Minimal repair:** Require the Red snapshot to be the recorded pre-implementation checkpoint for this attempt, with its scope-valid changes carried into the attempt lineage (or an explicit verified existing snapshot-to-attempt mapping); common-parent ancestry alone must fail. Add this sibling/common-ancestor case to g3b. Keep replay diagnostic and avoid adding a new mapping subsystem.

The unwanted registry, custom owner marker, aggregation script and per-sample approval layer are actually removed from the live plan, not parked as future work. Temporary-merge Green and the stale T8 candidate are also removed. Historical revision records appropriately remain unchanged. No further mechanisms are requested.

All tests remain planned, all 17 old findings remain open, and D11/model/CI/preset/T8 choices remain pending. Author submission success is distinct from document readiness. Only the first slice has an executable plan; later capabilities remain outlines. No product tests, runtime, repository actions or implementation authorization occurred.
