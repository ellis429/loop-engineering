# Review-10 — D50 first useful slice

**Verdict: changes_required.** D50's reductions are substantive: per-attempt integration and read-operation lifecycles disappear, replay becomes diagnostic, capability checks move earlier, and extraction bookkeeping shrinks. Do not restore those mechanisms. Seven bounded corrections below make the proposed slice executable without expanding platform scope.

All seven author-file hashes match the manifest. Coverage has exactly the expected 105 unique IDs (88 ACs + 17 S1 findings); ID completeness is not proof of semantic coverage. The author's `execution_status=succeeded` means candidate production succeeded, not document approval, D11, or product gates. Review-09 remains valid for its earlier frozen candidate.

## D50-R01 — Safety must precede the first real writer

**High; blocking.** `tasks.md:96–105,123–127,140–149`; `design.md:113–117`.

T4.2 depends only on preflight and G1. Worker observations arrive in T6.1 and D47 accounting/deadline-stop routing in T7.1. A real T4 worker that hangs or outlives its deadline therefore runs before the controller can fulfill its mandatory bounded-stop contract; preflight's one-time successful stop does not supply that behavior.

**Fix:** make the minimal worker-status fetch and T7.1 budget/stop behavior prerequisites of T4.2. Run their fake deadline/unknown/prepared-stop cases before real dispatch. Keep early profile preflight early; it can remain an explicitly bounded capability probe. No supervisor is needed.

## D50-R02 — Order reads before fetching; distinguish fresh facts from stale results

**High; blocking.** `design.md:69–72`; `spec-delta.md:20`; `tasks.md:123–126`; `validation.md:30`.

`seq` has no allocation point, and “old-version observations only enter history” conflicts with invalidation on newly observed versions. Counterexample: fetch A starts first at H1 and returns late; fetch B starts later, sees H2 and invalidates H1. A must not receive a larger completion-time seq and restore H1. Conversely, B must not be discarded merely because its request was prepared against H1.

**Fix:** allocate/persist an observation ordering identity before the fetch; import using that order, not completion time. Separate request context from observed head/base/binding facts. A newer applicable observation updates those facts and invalidates gates/Pass; an older superseded observation is historical only. Add both out-of-order completion and newly observed head/base change cases. A short counter update is sufficient; no read-operation lifecycle or single-execution permit.

## D50-R03 — Make G2 acceptance executable

**Medium; blocking.** `design.md:84–85,95`; `tasks.md:109–119`; `validation.md:29`.

G2 currently points to identity checks plus one blocked-verdict rule. The inherited GAT-05/AC-G11 still requires a full applicable clean review, so this is an underspecified implementation contract, not permission to weaken that AC. An independent reviewer can successfully execute yet return `changes_required`, omit a verdict, or review only part of the PR; the listed acceptance tests do not distinguish those from full clean review.

**Fix:** state the small verdict rule: passed only for valid full-scope current-version `clean`, authorized independent Reviewer, and no unresolved blocking findings; `changes_required` fails, `blocked` is unknown, malformed/missing/partial review cannot pass. Bind full PR diff, applicable contracts and prior findings to the assignment/result. Add these cases to T5.1/V6; no new review framework.

## D50-R04 — Preserve D27 at the bootstrap-to-feature boundary

**High; blocking.** `tasks.md:8–9,102–105,151–165`; `validation.md:42–43`; `coverage.md:32–33`.

T8 depends on T1.2/T4–7, not B1's human acceptance and actual merge. It can start implementing the dependent status feature from an unmerged controller branch. T4.2 also names that bounded feature before B1. D50 defers automated dependency management, not D27's accepted-and-merged prerequisite.

**Fix:** add a manual/skill check before T8 implementation: B1 accepted, actual merge confirmed, adopted baseline recorded. No automatic merge. If T4 runs before B1, define it as an isolated capability/probe exercise rather than starting the dependent delivery feature; otherwise place that feature work after the same guard. Keep this as a small explicit handoff.

## D50-R05 — A correct Blocked result is not the successful demonstration

**Medium; blocking.** `design.md:9`; `tasks.md:153–156`; `validation.md:40–44`.

R3's pass criterion is “three gates ... or evidence-backed Blocked.” A first-run infrastructure block, or stopping before fix/re-review, could therefore mark the first useful delivery complete despite D50's real review→fix→re-review objective.

**Fix:** separate safe execution outcome from demonstration completion. Evidence-backed Blocked is a valid stopped run; remaining real-loop coverage stays incomplete. Successful R3 requires the real finding/fix/re-review and current-version gates, plus the planned interruption/resume. No genuine finding means that coverage remains open; do not manufacture one.

## D50-R06 — Remove the inherited mandatory replay sentence

**Medium; blocking.** `spec-delta.md:4,32–40`; inherited `../review-09/spec-delta.md:110`.

The delta replaces GAT-03's supplemental paragraph but says AC-G06 is otherwise unchanged. The inherited AC-G06 THEN still appends “coordinator ... replays R with the same failure.” Thus an ordinary valid original Red without diagnostic replay satisfies the new design but not the composed acceptance text.

**Fix:** explicitly remove or condition that AC-G06 addition on contradiction/risk diagnostics. Preserve original Red, scope/lineage, current Green and regression. Add one normal-path case with no replay and one contradiction case; missing Red still cannot pass. The new write/read override and single-feature-worktree addition otherwise express D50 without requiring the retired machinery.

## D50-R07 — Supply the small missing execution map

**Medium; blocking.** `tasks.md:24–28,54–94,109–149`; `validation.md:18`.

Most production tasks name behavior but have no owned source/test paths or runnable verification command; `tests/<file>` is an unresolved placeholder. Dispatching T3/T5, for example, requires inventing ownership and test entry points. W1 also omits preservation of the already nonempty `loop-engineering-thin` directory (currently README.md and docs), so the stated worktree creation cannot run as written.

**Fix:** add one compact table per task group: owned paths, public command/interface, dependencies, exact verification command. Include a task owner for CI workflow creation. Complete W1 with destination/base B and a preserve-existing-directory step before worktree creation. No embedded implementation code, symbol inventory or module-count target is requested.

## Boundaries

D46–D50 remain approved directions; concrete design/spec adoption, CI set, reviewer model and technical presets still await D11. S2/S3 remain outlines, deferred rows are not delivered, and all 17 S1 findings remain open. No product code/tests or GitHub operations were run; only these review outputs were written.
