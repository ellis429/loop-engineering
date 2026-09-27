# Bounded recheck of revision-03

**Verdict: verified within the requested scope; no residual D45-R01–R06 findings.** This is not a full-design clean verdict, product G2 or implementation approval. All fixed artifact hashes match `manifest.json`.

| ID | Status | Evidence |
| --- | --- | --- |
| D45-R01 | verified | `design.md:84–85,148,179,184–188,361–363` consistently puts initial registered operations, including read-only observations, through a single begin. Existing in-flight/unknown readback bypasses begin, records through the API and never reissues the original operation. The double-consumption, lost-receipt and initial-observation counterexamples are addressed. |
| D45-R02 | verified | `design.md:160,238,242–266,322` prioritizes due stopping independently of blockers/unrelated in-flight work. No stop op creates one; prepared executes that same ID; in-flight/unknown reads it back without resending; failed requires proven-safe retry and remaining allowance; succeeded requires stop evidence. The prepare/crash/resume case explicitly executes the persisted stop first, once. Unconfirmed stopping retains active/Blocked status. |
| D45-R03 | verified, carried | Version/observation and Pass sections are unchanged from review-03. |
| D45-R04 | verified, carried | Checking publication sequence and GitHub publication section are unchanged from review-03. |
| D45-R05 | verified, carried | Cleanup document is byte-identical to review-03; selective test extraction remains permitted. |
| D45-R06 | verified, carried | Cleanup document is byte-identical to review-03; corrected CLI mutation facts and behavioral verification remain. |

DN-2/DN-3 clarifications and DN-1's no-implicit-fallback wording are carried verified: `decisions-needed.md` is unchanged. Original historical Red remains mandatory; replay is supplemental. GitHub 403 and the example check name do not authorize fallback. **DN-1–3 remain unapproved human decisions.**

Only the two residuals and immediate adjacent contracts were rechecked; R03–R06 were carried using unchanged-source comparisons. The described CLI/concurrency/crash cases are planned verification, not executed evidence. No product code, tests or GitHub operations were run, and no S1 finding was closed. Full design synchronization, spec-delta, tasks, coverage, validation and D11 remain pending. Hash binding and comparison results are in `review-result.json`.
