# Bounded re-review: revision-01

**Verdict: changes_required within this recheck.** D45-R03–R06 are verified as document fixes. D45-R01/R02 each retain one adjacent protocol contradiction. This is formative review of a `draft_pending_sync` design, not full-design rejection, product G2, implementation validation, or D11 approval. All five fixed artifact hashes match `manifest.json`.

| ID | Status | Evidence and conclusion |
| --- | --- | --- |
| D45-R01 | residual | `design.md:82,139,141,175–179,329`: normal execution now has one begin owner, fixing the original double-consumption path. But the universal tool protocol still conflicts with readback; see below. |
| D45-R02 | residual | `design.md:229,233–236,290,329`: unrelated blockers no longer prohibit deadline stops. In-flight reconciliation still precedes stop, and the alternate-action list is specified only while Blocked; see below. |
| D45-R03 | verified | `design.md:259–263,275`: fresh observations are separated from stale assignment results. The original H1 Pass → new H2 observation counterexample now updates observed facts and invalidates affected gates/Pass; old assignment results remain unable to authorize current gates. |
| D45-R04 | verified | `design.md:242–247,274,316`: clean gates now lead through original PR publication, dependent issue publication, then final Pass observation. Publication failure preserves the review and targets its original operation. |
| D45-R05 | verified | `cleanup-map.md:74,80–91,103`: case-level behavioral reuse is permitted with provenance and new-tree execution; blanket test rewriting is removed. Old test counts are not reused as evidence. |
| D45-R06 | verified | `cleanup-map.md:9,49,102`: decision, abandon and local-reconcile commits are acknowledged and explicitly replaced; static reachability is distinguished from actual CLI execution. |

## Residuals under existing IDs

**D45-R01 — High; remains blocking for eventual design readiness.** `design.md:82` says every `tool … --op` must receive `execute:true` from begin before its external call; `design.md:139` rejects begin on in-flight/unknown operations. Yet `design.md:141` and the CLI table require `tool … reconcile --op` precisely for those states. Counterexample: an external effect finishes, its receipt is lost, and reconcile cannot make its readback because begin returns false. The double-begin bug is fixed, but the revised universal rule still makes recovery ambiguous. Basis remains AC-D12/D13. **Small fix:** explicitly limit begin to execution/retry; reconcile reads the existing operation without consuming/replaying its execution permit and records readback through the API. Update §2 and §17 consistently; no extra recovery platform is needed.

**D45-R02 — High; remains blocking for eventual design readiness.** `design.md:234` still selects an unrelated in-flight reconciliation before the due stop at line 235. With a known worker past its role deadline, an unrelated operation in flight, and no pre-existing blocker, the only permitted primary action is reconcile; `permitted_while_blocked` is not specified for this state. This contradicts line 290's unconditional deadline-stop rule and preserves the in-flight-priority portion of the original finding. Basis remains DUR-08/AC-D17. **Small fix:** make due stops for known active attempts the first selection, or always expose their permitted action independently of blocker status. Reconcile an already-issued stop instead of issuing it twice; keep unknown worker state unknown. No supervisor is requested.

## Policy clarification recheck

DN-2 clarification is verified at `decisions-needed.md:52–57`: original pre-implementation Red, raw output, exit, task/attempt, snapshot and provenance remain necessary; replay/transcript review only supplement them. The same-UID boundary does not permit reconstructed Red. DN-2 B is not an implicit fallback.

DN-3 clarification is verified at `decisions-needed.md:84–87`: a repo-scoped, versioned human policy is distinct from verified GitHub rules; 403 and the example name `test` do not authorize fallback. Old CI/sandbox success is explicitly insufficient evidence for the new profile. DN-1 B/C also remain opt-in (`decisions-needed.md:23`). **DN-1–3 are still unapproved.**

Only the six prior findings and these clarifications were rechecked against review-01. No new full-design review, product execution, tests, GitHub calls, source edits or S1 closure. “Verified” means the specified document counterexample was addressed, not implemented or tested. Pending future artifacts remain excluded.
