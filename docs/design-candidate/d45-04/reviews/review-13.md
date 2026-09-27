# Review 13 — D51 AC audit correction

**Verdict: changes_requested.** Document review completed; the author successfully produced the requested artifacts, but seven bounded corrections remain before this package is ready for human review. This is neither an implementation authorization nor a product-gate verdict.

All eight manifest hashes match. Coverage contains exactly 105 unique rows: all 88 ACs and all 17 historical findings, without omissions or duplicates. I read all 88 authoritative audit notes and compared their semantic dispositions and candidate assertions/rubrics: 58 core, 17 workflow, 6 deferred, 3 rewritten, 3 evidence, and 1 historical. Deferred automation, dual-opencode validation, positive integration-source mapping and historical P03 are not misrepresented as completed. All tests remain planned and all 17 historical findings remain open.

## Required corrections

### D51-R01 — high; blocking

**Locations:** design.md:69, design.md:71, design.md:75, validation.md:96. **Basis:** AC-A04; finite-write unknown/non-delivery contract; previously verified D45-S03.

A head-branch lookup is classified as verified native idempotence, contradicting the adjacent unknown rule. A create request may be accepted, lose its receipt, and remain absent from a subsequent lookup; treating that lookup as idempotence permits a second create.

**Smallest repair:** Remove pr_ensure lookup from the native-idempotence examples. Initial zero-match may create once; positive readback may adopt a matching PR; unknown plus zero-match remains unknown/Blocked without another create. Add this delayed-create counterexample to h10.

### D51-R02 — high; blocking

**Locations:** design.md:132, design.md:165, spec-delta.md:35, validation.md:93. **Basis:** AC-G05/G08/G17; D50 current-head Green and first-slice head-only source contract.

The base-change row replaces required head-H Green with Green on a temporary merged snapshot M while explicitly keeping H unchanged. A passing M does not establish Green at H; the new h7 test would encode this contradiction.

**Smallest repair:** Keep authoritative Green/regression at H. If a temporary base recheck is retained, label it supplemental evidence bound to H and the new base, never as Green at H. A required source change must produce a new real head and invalidate/recheck the gates. Make h7 assert the distinction; no merge-source CI support is needed.

### D51-R03 — high; blocking

**Locations:** design.md:156, design.md:158, validation.md:90. **Basis:** AC-G14: latest attempt, expected identity, pagination; pending must not inherit older success.

The universal started_at ordering is undefined for a newer queued check without a usable start time and for commit-status records (a different timestamp shape). It can retain an older success. Filtering only same name/app also leaves the advertised workflow identity unbound when another workflow emits the same check name.

**Smallest repair:** Specify a small first-slice GitHub Actions identity and attempt-order rule using available workflow/run/attempt identity; distinguish status records if supported. Unorderable or ambiguous candidates are unknown, never old-success fallback. Extend h4 with queued/no-start and same-app wrong-workflow cases; avoid a generic CI normalization platform.

### D51-R04 — medium; blocking

**Locations:** result.json:32, tasks.md:38, validation.md:39, tasks.md:77. **Basis:** AC-D01; D27/T8 requires a real downstream feature on accepted and merged B1.

The T8 feature candidate remains status --human, but T2.1 and s5 now implement and validate that behavior in B1. Approving the listed candidate can leave T8 with no new behavior and no honest implementation Red.

**Smallest repair:** Mark that T8 candidate superseded/unavailable and retain a pending D11 choice of a genuinely unimplemented bounded behavior. Keep the existing T8 handshake and success criteria; do not silently select or redesign its feature.

### D51-R05 — medium; blocking

**Locations:** design.md:220, validation.md:13, validation.md:16, tasks.md:36, tasks.md:56. **Basis:** D50 minimal first slice; D51 applicable-environment validation correction does not require a new test-accounting subsystem.

The correction mandates per-test required IDs/owner registration, a custom owner marker, cross-job JUnit aggregation and required-tests-check before the first useful slice. This adds a new maintained registry/checker contract beyond establishing that applicable required tests pass.

**Smallest repair:** Remove the bespoke registry/checker from the required architecture and T1.1. Use the small documented job/platform split and ordinary test selection/markers; required applicable suites must run and pass, with unintended skips/missing suites rejected. Keep build/install smoke and required CI jobs.

### D51-R06 — medium; blocking

**Locations:** validation.md:149, tasks.md:46, tasks.md:67. **Basis:** D50 thin scope; D51 shared workflow samples/rubrics; existing D11 and acceptance decisions.

Every W-A–W-F positive/negative sample now requires a user signature as a task completion gate, including historical and skill examples. This adds an approval layer to validation that the approved audit correction did not require.

**Smallest repair:** Have the authorized independent reviewer record rubric results in the existing validation proof. Remove mandatory per-sample user signatures; bring only unresolved policy/business choices to the existing human decision points. Preserve real plan approval and B1 acceptance/merge.

### D51-R07 — high; blocking

**Locations:** spec-delta.md:35, design.md:131, validation.md:75, validation.md:81. **Basis:** AC-G04/G06/G08, S1-R13; review-12 GAT-03 explicitly required attempt scope and scope/lineage despite optional replay.

The replacement GAT-03 drops the explicit requirement that the attempt commit range is inside approved scope. Generic snapshot/provenance corruption and arbitrary-argv cases do not test a validly produced Red on an out-of-scope snapshot or an unrelated lineage. Optional replay must not turn those records into acceptable Red.

**Smallest repair:** Restore explicit approved-scope and snapshot/attempt-to-head lineage eligibility in GAT-03 and G1. Add independent g3 cases with otherwise valid raw/provenance but out-of-scope or unrelated lineage, both rejected. Preserve original Red and diagnostic-only replay; no new execution platform.

## Boundaries and non-findings

The frozen T2.1 interface and completion condition both cover s1–s6; no missing-s6 finding is warranted. AC-A01–A05 otherwise have concrete planned policy, head-only, selected-provider, PR-path and persistent-read-budget cases. Supplementary state, evidence/N/A, findings, resume and publication cases now have explicit assertions; workflow rows have shared positive/negative rubrics. Mapping is a plan, not executed proof.

The seven findings are one correction batch, not a request for additional architecture. D11, exact reviewer/model, CI policy/presets, real T8 feature selection, spec adoption and B1 acceptance/merge remain human decisions. The first slice is the executable plan; later slices remain outlines. Prior finite-write/stop and pure-read/version-watermark fixes were not reopened; R01 above identifies an adjacent newly contradictory example. No product code, runtime, tests or repository GitHub operations were executed.
