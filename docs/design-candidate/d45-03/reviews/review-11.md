# Review-11 — bounded D50 correction recheck

**Verdict: changes_required; one residual, D50-R02.** The other six fixes verify within this recheck. All eight author-file hashes match the manifest; the expected 105 unique coverage IDs remain (88 ACs + 17 S1 findings). No new broad review or platform requirement is introduced.

## D50-R02 — Shared version facts need ordering across purposes

**High; residual blocking.** `design.md:72–80` (especially 77); `spec-delta.md:22–24`; `tasks.md:78–84`; `validation.md:29` (V7).

Persisting seq before fetch fixes completion-order races within a purpose. However, the update guard explicitly compares only the **same purpose**, while head/base/bindings and gate invalidation are shared feature facts.

**Counterexample:** `purpose=pass, seq=10` reads H1 but returns late. `purpose=pr, seq=11` imports H2 first, invalidating H1. The late Pass response is newer than the previous *Pass-purpose* response, so the stated rule lets it restore H1. The same-purpose tests do not reject this case.

**Minimal replacement:** “Updates to shared head/base/merge-base/binding facts compare against a persisted feature-level version-observation watermark across all version-bearing purposes. An older observation is historical only for those facts and cannot authorize Pass, even when it is the newest result of its own purpose. A newer applicable version observation advances the watermark and performs normal invalidation. Per-purpose result/check caches remain separate and may support gates only when applicable to the current version.” Observations that carry no shared version facts need not advance that watermark.

Add the exact delayed `pass` versus newer `pr` case to T6.1/V7: retain H2, never restore H1 or pass with seq=10, and require a fresh applicable Pass observation. This is one state comparison using the existing seq, **not** a read-operation lifecycle, scheduler or additional authority service.

## Verified fixes

| ID | Status / evidence |
| --- | --- |
| D50-R01 | Verified: worker observations and budget/stop fake checks precede the real writer probe in the execution table, run order and R2 prerequisites. |
| D50-R03 | Verified: design §7, spec §3a, T5.1/V6 explicitly require authorized independent full-scope current-version clean review; other verdicts cannot pass. |
| D50-R04 | Verified: T8.0 and spec §3b require B1 human acceptance, actual merge and adopted baseline. Earlier T4.2 is an isolated unmerged probe. |
| D50-R05 | Verified: Blocked is a valid safe stop, not R3 completion. Genuine fix/re-review, current gates and resume are required; missing coverage stays open. |
| D50-R06 | Verified: inherited AC-G06 mandatory replay sentence is expressly removed; normal no-replay and diagnostic cases are specified. |
| D50-R07 | Verified: task ownership/interfaces/dependencies/commands and CI owner are supplied; W1 preserves the existing destination before attachment. |

D50 simplifications remain intact. Review-09 retains its meaning for its frozen earlier candidate. Author execution success is distinct from document readiness. D11, check set, reviewer model and presets remain pending; no implementation or product-gate approval is given. All validations remain planned, all 17 old S1 findings remain open, and S2/S3 remain deferred outlines. No product code/tests, GitHub operations or candidate edits were performed.
