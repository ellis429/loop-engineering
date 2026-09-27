# Independent design+plan review — revision-15

**Verdict: changes_requested.** 7 blocking findings and 3 non-blocking findings remain. This is a review of the candidate documents, not D11 approval or a product-gate result.

Assignment: `herdr-design-plan-20260928-01 / review-r15-01`. Reviewer: `gpt-6-astra`, effort `xhigh`, as reported by this run's Codex header. The reviewer did not author or modify the candidate.

All **27/27 SHA-256 entries** in `input-manifest.json` were recomputed before substantive review and matched. No mismatch was found. The candidate/previous-r14 diff, all four formal specs, the complete D45-02 baseline, decisions, intent, handoff and both helper reports were read. Scripts also confirmed **88 unique formal AC IDs**, all present in **105 coverage rows** (88 AC + 17 legacy findings), and **103 unique product-matrix row IDs**. These are inventory checks, not evidence of adequate behavior or executed tests.

The highest-impact gaps are the unbounded/unaccounted coordinator Green command, incomplete result contracts for finding resolution, and missing preflight placement verification. The CI proposal and several assertion sets also need corrections. The explicit task dependency column is acyclic; the h13/T7.1 timeout split is an ownership ambiguity, not a demonstrated graph cycle.

## Findings

### R15-01 — blocking, major

**Location:** inputs/candidate/design.md §7 lines 215–217 and §10 lines 364–376; validation.md §6.2 evidence.commands.suite, b1–b4.

The new exhaustive active-interval definition counts worker attempts, review attempts and CI waiting, but not coordinator-run Green/regression. After the worker result/turn closes, evidence green synchronously runs the approved pytest suite in a temporary checkout; no bound for that subprocess or deadline checks during it is specified. A hanging Green can therefore consume arbitrarily long online execution while the persisted active clock does not advance and orchestrate cannot return to safety.

**Basis:** D13 bounds run active execution to 4h. D47 and baseline DUR-08 require bounded online deadline checks; stopping/readback must not be blocked by unrelated operations. The 30-second read and 60/120-second external-write limits do not define a limit for this local evidence command.

**Expected fix:** Specify the evidence-command activity interval, bounded execution/deadline handling, failure/unknown outcome and cleanup handoff, with T3.1/T7.1 ownership. Add a fake hung/over-budget Green case proving elapsed time is retained, control returns to safety/Blocked, no gate passes and no new worker is dispatched. Use the existing short-lived subprocess/tool boundary.

### R15-02 — blocking, major

**Location:** inputs/candidate/design.md §4 line 106, §8 lines 234–236, §9 lines 330–344; tasks.md T2.3/T5.1; validation.md r4/r6/r8/r10.

The newly specified review result fields contain verdict, findings, read_digests and native provenance, but no per-existing-finding verification/closure/dispute disposition or its evidence references. The assignment snapshot also does not explicitly carry the prior fix evidence required by FIN-03. T2.3 owns generic result import before T5.1, yet the shared correction-result envelope expressing fix_submitted/disputed for each batch ID is not defined. A fresh implementer must invent the core handoff that distinguishes 'F1 verified, F2 still blocking' from omission, or infer closure from a clean verdict.

**Basis:** D09/D25; FIN-02 and AC-F04 require versioned, evidenced closure of a specified finding. FIN-03 and AC-F06 require complete per-ID fix_submitted/disputed responses and previous review/fix evidence in assignments. PA-05, PA-11 and PA-24 requested this cross-task contract.

**Expected fix:** Complete the existing assignment/result contract with explicit per-ID correction responses and reviewer dispositions/evidence, their common identity/version envelope, and the T2.3-to-T5.1 validation extension point. Define omission as no closure/incomplete where applicable. Exercise partial verification, omitted prior findings, stale closure evidence and dispute responses through the public import path; include immutable prior review/fix/version references in r10.

### R15-03 — non-blocking, minor

**Location:** inputs/candidate/tasks.md execution rows T6.1/T7.1, cards lines 127–128; validation.md h13 and b4.

T6.1 must pass h13's mergeable=null-until-timeout -> Blocked assertion before T7.1, while the new T7.1 card owns role timeouts and their next/safety effects and depends on T6.1. T6.1 also establishes the CI waiting window. The cards do not say whether T6.1 owns expiry classification and T7.1 only routes it, or whether h13 depends on T7.1's later implementation. The explicit graph is acyclic, but this shared responsibility is not specified.

**Basis:** The handoff asks for unambiguous adjacent interfaces. Design §5 line 146 uses the CI timeout clock for mergeability, and §10 gives its expiry semantics. This can be implemented without a backward edge by an explicit ownership split; the documents currently leave that split implicit.

**Expected fix:** Explicitly assign expiry detection/state effects and next/safety routing between T6.1 and T7.1. A simple option is to keep trigger classification in h13 and the elapsed-time/Blocked assertion in existing b4. Preserve the current acyclic dependency order.

### R15-04 — blocking, minor

**Location:** inputs/candidate/validation.md §6.1 static job (line 270), §0 lines 14–20; design.md §11; spec-delta.md §6 line 110.

The proposed complete static job runs ruff, mypy and dist-smoke only. It does not run pytest or the test-only collection/skip/xfail policy, while the composed requirement and design require the same test command/policy in every necessary CI job. That job can report success without applying the required collection and skip checks.

**Basis:** GAT-06 as replaced by spec-delta §6: '本機 G1 與每個必要 CI job SHALL 套用同一套收集／skip／失敗政策'. Design §11 and validation §0 also say every required job uses the same command. D12 makes a spec/verification mismatch blocking.

**Expected fix:** Make the static job apply the promised suite and platform policy, or explicitly propose and consistently scope a policy change to test-running jobs through the spec/design/D11 package. Validate the actual job command sequence rather than relying only on the pytest policy unit cases.

### R15-05 — blocking, minor

**Location:** inputs/candidate/tasks.md T0.1 step 2 and T1.1 owned paths/completion; validation.md §6.1 common prerequisite 4.

All proposed CI jobs begin with uv sync --frozen. W1 explicitly excludes the old uv.lock, the selected main baseline has no lockfile, and no task owns generating and committing the new uv.lock. Local uv run can generate an untracked lockfile and pass the stated T1.1 checks, while a clean CI checkout still fails before the required commands. The dispatch plan leaves an indispensable tracked artifact unowned.

**Basis:** The requested plan must be runnable from a fresh checkout with explicit file ownership. The [uv command reference](https://docs.astral.sh/uv/reference/cli/#uv-sync--frozen) documents that --frozen errors when the lockfile is missing. This is a prerequisite for the proposed G3 verification, not a request to copy the legacy environment.

**Expected fix:** Give T1.1 ownership of a newly generated uv.lock, require it to be committed with pyproject.toml, and include a fresh-checkout uv sync --frozen check in the handoff/completion conditions. Define the normal ownership for later dependency changes.

### R15-06 — blocking, major

**Location:** inputs/candidate/design.md §6 preflight/receipt lines 173–179; validation.md f3/f5/R1; coverage.md AC-D18/AC-G19.

The proposed R1 success criterion and receipt verify model/marker, permission probes and stop, but do not record or compare requested versus actual repo/worktree/branch placement. f3 tests only model mismatch; w6 tests a later imported result, not a wrongly placed preflight session. R1 can be marked verified without proving the workspace capability required for dispatch. In addition, f5 has no individually failing gh/herdr permission-probe variants, so a preflight reducer that ignores those mandatory probe failures still passes the listed fake cases.

**Basis:** DUR-09 requires actual repo/workspace/branch checks before dispatch. AC-D18 forbids inferring actual placement from shell cwd/current/role; GAT-08/AC-G19 preserve a placement capability gap. Design §6 itself requires each listed permission negative, and PA-25 asked for each denied-operation fake case.

**Expected fix:** Add native, session-bound requested/actual placement checks to the preflight contract and receipt, with wrong-workspace/branch and input-accepted-only failures. Parameterize each mandatory permission probe, including gh and herdr, so denial missing or resources changed independently makes the receipt unverified. Keep R1 as the real capability proof.

### R15-07 — blocking, minor

**Location:** inputs/candidate/validation.md d10, b1–b4, r7; design.md §10 line 379; tasks.md T7.1.

d10 says the four budget_extension effects are verified by b2–b4 and r7. Those rows test extra attempts and a new CI window, but r7 only rejects an unapproved fourth correction and b1 contains no active-budget extension. An implementation that records active/rounds decisions but never applies either, or applies a rounds extension repeatedly after restart, can pass every referenced row.

**Basis:** AC-D17 and AC-F07 require an explicit recorded human decision for changed budgets; revision-15 adds supported active:<minutes> and rounds:+1 operations. D12 requires verification of the promised behavior, including preserving other counters and avoiding reset/replay.

**Expected fix:** Add positive and negative effect cases for active and rounds extensions through the public decision/next path: correct target only, one-time application across replay/restart, other counters preserved, and no bypass of writer/stop/unknown blockers. Assign each case to the task that owns the effect.

### R15-08 — blocking, minor

**Location:** inputs/candidate/validation.md h11 [r15]; inputs/helpers/sol-plan-ac.md PA-22.

The added h11 negative is 'the remote ref is another SHA'. PA-22 required the different failure mode 'the desired SHA exists on another ref'. A readback implementation that searches for the desired SHA on any branch can pass the current positive and negative while falsely declaring the requested target-ref push successful.

**Basis:** DUR-06 persists and reconciles an operation's target identity; design §4 requires readback of the original operation. PA-22 specifically requested the wrong-remote-ref counterexample. This is a required identity check, not a style preference.

**Expected fix:** Add a fake readback where the prepared target repo/ref does not contain H but another repo/ref does. Assert no succeeded receipt for the prepared operation, Blocked/unknown as specified, and zero resend. Preserve the existing wrong-SHA case.

### R15-09 — non-blocking, minor

**Location:** inputs/candidate/spec-delta.md introduction and §1 lines 18–20; inputs/baseline-spec-delta-d45-02.md DUR-06 lines 229–237.

The 'only narrowing' explanation names removal of the local-synchronous exception, but replacing the whole baseline paragraph also drops the separate alternative '已完成且排除之後才生效' from the authoritative-evidence retry bullet, and the explicit 'until human approval to check again' readback wording. The new text permits only proven non-delivery or native idempotence. The conservative stopping behavior is acceptable, but the claimed exact scope of the change is incomplete. The blanket rationale that all writes use Herdr/GitHub also needs to distinguish the new direct-git temporary Green checkout.

**Basis:** SS-02 asked for the complete retry list's fate to be explicit. D11/D19 require disclosed semantic changes; the retry maximum does not force automatic retries in every safely retryable case. This does not create an unsafe retry or remove a mandatory successful outcome.

**Expected fix:** Document the fate of the completed/no-later-effect alternative and bounded human-authorized re-observation explicitly; either retain them or disclose their intentional removal in the D11 package. Clarify that feature external-write operations and temporary evidence-checkout operations are distinct if that is intended.

### R15-10 — non-blocking, minor

**Location:** inputs/candidate/spec-delta.md §12; inputs/baseline-spec-delta-d45-02.md §4 Purpose line 278; inputs/formal-specs/finding-resolution.md Purpose.

Literal composition still leaves finding-resolution's Purpose saying '本文是本 change 的D40 已核准的規格'. The baseline only replaces the later S1/S2/S3 phrase, and revision-15's explicit composition rules replace the banner, not this Purpose sentence. This disagrees with the adopted-source banner and the clear intent to keep D40 approval historical.

**Basis:** T0.1 and D11 require one current adopted authority and historical treatment of D40 approval. The overall candidate clearly remains unapproved, so this is a localized adoption-text defect rather than evidence of unauthorized implementation.

**Expected fix:** Add an explicit replacement for this remaining Purpose sentence to the composition instructions/source map. Keep the original approval.json historical and do not apply its approval to revision-15.

## Review across the requested dimensions

| Dimension | Result |
| --- | --- |
| Requirement consistency | D41/D46/D48–D52 remain recognizable: one outer orchestrate loop, a thin deterministic controller, isolated rebuilding, original Red/current Green, separate gates, human decisions and no automatic merge. D47's online bound is incomplete for coordinator Green (R15-01). Result handoffs do not yet express all retained finding obligations (R15-02). |
| Only declared narrowing | Removing the local-synchronous retry exception is an acceptable conservative proposal: it authorizes no unsafe retry and need not promise a successful automatic retry. It remains subject to D11. The claim that this is the only affected retry wording is incomplete; see R15-09. D51's head-only CI, runtime and automation deferrals remain explicit, rather than being counted as completed. |
| Mechanical spec composition | The seven full replacements named in §12 eliminate the helper's AC-D10/D23/G13/G15/O15/O23 and GAT-06 splice ambiguities. §1 names the complete DUR-06 paragraph replacement; §3 preserves the original GAT-03 and restores independent Green checkout. All 88 IDs survive. The finding-resolution Purpose retains a stale D40 approval sentence (R15-10); the retry replacement needs accurate disclosure (R15-09). T0.1's independent source map and stop-on-conflict guard remain necessary. No adopted formal specs were created in this review. |
| Dispatchability | Task cards, file owners, handoff paths, CLI registration and the next/safety vocabulary are substantial improvements. Explicit dependencies run forward in the stated order. Remaining concerns are the result/import contract, timeout ownership split and unowned lockfile (R15-02/03/05). The store contract is sufficient at plan level; it need not grow into a generalized event or schema platform. |
| Verification sufficiency | New g5/g14, w2/w8/w11, h8/h10, p4/p6/p7 and r13 have useful failure-sensitive assertions. d7a/d7b correctly separate decision recording from later effects. Rows/AC IDs alone are insufficient: R15-06/07/08 identify cases where a defective implementation can satisfy the listed assertions. PA-27 is only partially addressed; a small reporting/rubric negative can close it without a new product service. |
| Concrete D11 defaults | The proposed product models, runtimes, effort, three CI jobs, timeouts, read/write limits and W1-A/W1-B are concrete and explicitly pending. Model unavailability and unverified profiles stop rather than silently substitute. The default bootstrap Astra reviewer is different from every proposed Opus/Sol implementer, not merely a different session/effort. CI and timeout defects are listed above; the exact model IDs are proposals, not proof of OpenCode inference capability. |
| W1 and source preservation | Starting from main rather than the old PR head is a justified way to preserve separation. A0 carries current document contents/deletions, B carries adoption plus independent review, and W1-A binds later assignments to B′ while W1-B binds them to B. The main-baseline objects inspected contain no src/tests tree. W1 is still only a proposal; no workspace, branch, PR or adoption was created. |
| D50 / over-design | No new resident service, platform, scheduler, test registry or general sandbox is proposed. The existing finding registry is required by D24. The needed corrections can use current CLI, subprocess, result and test boundaries; they do not justify expanding the product architecture. |
| Human–machine boundary | The D11 package asks exactly three questions. README, d11-confirmation and revision-15.json keep approval, implementation and test results pending. Historical revision-14 clean is scoped correctly. B1 and T8 remain separate, and T8 requires its own approved packet plus B1 acceptance, actual merge and adopted baseline. |

The W1 rationale should be read precisely: GitHub can mark an old PR merged when its head commits become reachable from its base through another merge. It is not unconditional for every squash/rebase strategy. The selected ancestry exclusion addresses the risk. [GitHub's indirect-merge documentation](https://docs.github.com/en/pull-requests/reference/pull-request-merges).

The new frozen CI prerequisite does require a tracked lockfile; `--frozen` does not generate a missing one. [uv's command reference](https://docs.astral.sh/uv/reference/cli/#uv-sync--frozen). The read-only local object check established `359ffcf6b439c054e6d5e61e2e80fc2e37944e6b` and `4ce111011fde83c3a2784402cea111e52a954b3c`; it did not refresh origin/main or query current PR #2 status.

## Revision-14 finding impact

Each status below refers to the **original bounded finding**, not a blanket endorsement of revision-15. Newly exposed issues in the same area are cross-referenced. No original fix is shown to have been reverted; several wider claims require the corrections above.

| ID | Status | Evidence and impact |
| --- | --- | --- |
| M1 | `still_verified` | design §8 lines 247–256 and validation h4/h4a–h4e retain event/PR identity, latest attempt per run, all same-head runs and no fallback to stale success; R15 adds the readable URL field. |
| M2 | `still_verified` | design §7 lines 201–214, spec-delta §3 and g10/g11/r11 retain original correction Red bound to finding/batch, no transfer from abandoned attempts and no fabricated Red; g14 additionally restores independent Green checkout. |
| M3 | `still_verified` | design §4 line 107 and §8 lines 289–306 retain fast-forward pushes, exact [H,B] merge parents and reproducible imported/authored classification; g12/g13/h11 retain the lineage checks. R15-08 concerns an additional readback negative. |
| M4 | `still_verified` | The original T2.3 worker/native ownership is retained, and batch/finding effects move to T5.1 with documented G1 fixtures. The explicit graph remains acyclic. R15-03 identifies a timeout ownership ambiguity; it is not proof of a cycle or regression of the original worker/native split. |
| M5 | `still_verified` | spec-delta §6 line 110, design §11 and t1–t6 preserve the exact only_on/non-owning-platform predicate. R15-04 separately identifies the static-job command-list inconsistency, which was also implicit in r14 §6 and is not a newly changed skip predicate. |
| M6 | `still_verified` | design §4 lines 108–125 and h10 retain expected repo/head/base/SHA plus marker before PR creation, mismatch rejection and origin=existing; R15 adds failed/pending G1 -> zero push/PR calls. |
| m1 | `still_verified` | design §8 lines 308–322 and p1 retain the state-derived human-readable Pass package and policy/rules/publication details; p7 names both fresh pass-purpose observations. |
| m2 | `still_verified` | spec-delta §9 gives AC-O23 an explicit phase-specific full THEN; design §1, tasks deferred list and coverage AC-O23 still defer unaffected-work continuation to S2. |
| m3 | `unaffected` | design §7 N/A and §8 integration Red, g7/g8/g13 retain behavior-based eligibility and no fabricated N/A for pure base import. |
| m4 | `still_verified` | T0.1 still pins both deltas, composes all four formal specs, requires an independent source-map review and retires competing plans before B/dispatch. R15 adds A0/B/B′ and concrete adoption paths. R15-10 is a residual Purpose wording issue, not removal of those guards. |
| m5 | `still_verified` | design §8 trigger/routing text, spec-delta AC-G17 and r12/r12b retain authoritative conflict/finding/human triggers and unavailable-result priority; h13's timeout ownership issue is separately R15-03. |
| m6 | `still_verified` | design §8 line 256 and validation h12/§6.1 retain per-job run/attempt/job/check/tested-SHA artifact contents and the conservative partial-rerun limitation. |
| m7 | `still_verified` | design §4 resolve_operation, d9/w10/h10 retain record-only decisions, fresh identity checks, rejection of not-found as non-delivery proof and bounded retry; w11 correctly makes write timeout unknown. |
| m8 | `still_verified` | T1.1 still owns workflow.yaml; design §8 and validation h1/§6.2 retain workflow blob and policy digest binding plus policy_change. The newly required uv.lock ownership is separately missing (R15-05). |
| m9 | `unaffected` | design §8 G2 and r1/r12b(f) retain blocked verdict -> G2 unknown plus feature Blocked, no correction round and no clearing independent blockers. |
| m10 | `still_verified` | README's review table limits historical clean to revision-14 and labels revision-15 pending; d11-confirmation and revision-15.json state pending approval and no product tests/implementation. |
| R12-01 | `unaffected` | design §8 lines 278–288, spec-delta AC-G17 [R14] and r12b(a–f) preserve unavailable/obsolete/unstartable-result priority, valid in-flight collection, safety/budget precedence and independent blockers. The §9 'path 2' cross-reference is stale in both r14 and r15; use §8's numbered rules. |
| R12-02 | `unaffected` | design §8 lines 289–306 and g13 retain pinned H/B, exact parents, merge-tree comparison, pure import versus authored scope, original Red for authored behavior and full gates on the new head. |

## Helper dispositions

**27 verified; 11 partial; 0 not_addressed.** “Verified” means the requested document fix is present and adequate for that bounded item; it does not mean product tests passed. Fix-submitted labels in the author's disposition file were not treated as verification.

| ID | Status | Independent check |
| --- | --- | --- |
| SS-01 | `verified` | spec-delta §1 names the entire baseline DUR-06 appended paragraph as replaced; read-only observation no longer consumes write permission. |
| SS-02 | `partial` | The local-synchronous exception is explicitly removed and stopping conservatively is acceptable; the complete replacement also drops other baseline wording without disclosing its fate (R15-09). |
| SS-03 | `verified` | spec-delta §7 supplies the full AC-D10 WHEN/THEN; history-first remains a design choice, with s1/s2/s3 retaining recovery and conflict behavior. |
| SS-04 | `verified` | spec-delta §6 supplies full GAT-06 text including readable URL, run/attempt identity and all retained checks; design §8 requires a URL. The concrete static job has the separate R15-04 mismatch. |
| SS-05 | `verified` | spec-delta §9 fully replaces AC-O23 THEN with whole-run stop in S1 and explicit later partial continuation. |
| SS-06 | `verified` | spec-delta §9 fully replaces AC-O15 with a generic unauthorized-start scenario; s7 and W-F cover the intended behavior and absence of a historical-product special case. |
| SS-07 | `verified` | spec-delta §8 fully replaces AC-D23 for the selected Claude Code/OpenCode pair and explicitly defers its OpenCode-only variant. |
| SS-08 | `verified` | spec-delta §6 fully replaces AC-G15 with S1 unknown for non-head CI and deferred S2 verified mapping. |
| SS-09 | `partial` | Exact model, jobs, runners and policy source are proposed and remain unapproved; the CI commands contradict the per-job policy and lack lockfile ownership (R15-04/R15-05). |
| SS-10 | `partial` | Read/write limits, polling and worker/review/CI timeouts are concrete; coordinator Green execution is neither bounded nor counted, and active/round extension effects lack tests (R15-01/R15-07). |
| SS-11 | `verified` | spec-delta §2 marks parallel writers explicitly deferred S2, consistent with design and tasks. |
| PA-01 | `verified` | T0.1 names adoption/source-map.md and review.json/review.md, records source and before/after hashes, and commits the comparison and review in B. |
| PA-02 | `verified` | T1.1 owns both permission/profile files, workflow profile definitions and preflight; design §6 defines their loading intent and receipt. Capability verification gaps are separately R15-06. |
| PA-03 | `verified` | design §3 specifies store load/commit/object operations, revision conflict/idempotency behavior and token handoff; T2.1 owns the common API. |
| PA-04 | `verified` | d7a is record-layer rejection in T2.2; d7b's finding, Pass and version effects are explicitly owned and tested in T6.2. |
| PA-05 | `partial` | Op records and adapter outcomes are defined in design §4, but the shared result envelope and correction responses needed by later imports remain incomplete (R15-02). |
| PA-06 | `verified` | G1 now only consumes assignment finding/batch fields and emits gate reasons; g6/r13 split batch creation into T5.1. g13 uses the documented pinned H/B assignment fixture. |
| PA-07 | `partial` | T6.1 owns push/pr_ensure extensions and finding-ID deduplication moved to r12. The h13 timeout responsibility still needs an explicit split with T7.1 (R15-03); there is no explicit dependency cycle. |
| PA-08 | `partial` | T7.1 owns next/safety timeout priority and design §2 defines the action shape; active/rounds budget_extension effects are not verified by the cited cases (R15-07). |
| PA-09 | `verified` | T4.1 depends on T7.1, owns its DOC checklist and consumes the complete next/safety vocabulary in design §2. |
| PA-10 | `verified` | T4.2 owns probe/fixture and expected trace; R2 now requires an actual positive G1 outcome and leaves an evidenced Blocked probe open. |
| PA-11 | `partial` | Review diff/PR/digests and native provenance fields are specified, but per-finding review dispositions/closure evidence and the generic importer handoff are still missing (R15-02). |
| PA-12 | `verified` | design §2/§8 and T6.2 specify observe pr and observe ci with --purpose pass; p7 tests changed checks preventing Pass. |
| PA-13 | `verified` | T8's separately approved D11 packet explicitly supplies issue/spec/AC/plan version and digest; B1 accepted/merged/baseline remains a prerequisite. |
| PA-14 | `verified` | The shared-file table explicitly allocates sequential cli.py registration to the task introducing each public interface. |
| PA-15 | `verified` | The shared-file table gives tools/herdr.py and its fake a T1.1 -> T2.3 order and preserves prior preflight behavior. |
| PA-16 | `verified` | T1.1 owns the versioned profiles and permission files; T1.2 owns the real receipts. This closes the artifact-ownership finding, not the separate R1 sufficiency gap. |
| PA-17 | `verified` | T1.1 defines the scenario JSON directory/schema and FAKE_LOG contract; T2.3/T6.1 own their tool-specific extensions. |
| PA-18 | `verified` | B1 owns index.md and T4.1 owns docs/validation/s1/doc/orchestrate.md. |
| PA-19 | `verified` | tasks general/shared-file rules and cleanup-map §1 assign append-only extraction-log sections to each extracting task with source/path/reason/new row IDs. |
| PA-20 | `verified` | g5 checks actual Green SHA D and a failing-Green-on-D variant, so recording a documents-only reason alone cannot satisfy it. |
| PA-21 | `verified` | w2 rejects wrong marker/target identity; w8 rejects another attempt's marker and an unfinished native turn without import or resend. |
| PA-22 | `partial` | h10 now rejects failed/pending G1 with zero push/PR calls. h11 adds wrong SHA but not desired SHA on the wrong ref (R15-08). |
| PA-23 | `verified` | p4 rejects altered publication digest/marker; p6 invokes all four forbidden verbs and requires zero external calls. |
| PA-24 | `partial` | r10 now mutates registry category/basis and checks immutable snapshot/digest, but the snapshot/result contract does not explicitly preserve prior fix evidence and version references or assert their immutability (R15-02). |
| PA-25 | `partial` | R1 requires denial plus unchanged resources, R2 requires G1 passed and f5 adds false-success/stop cases; individually failing gh/herdr probes and actual placement proof remain missing (R15-06). |
| PA-26 | `verified` | W-F adds product-source inspection and reviewer rejection of an injected P03 branch; s7 separately tests generic no-init behavior, so string inspection is not the sole behavior test. |
| PA-27 | `partial` | r1 now asserts clean creates no fabricated finding, but it does not assert demonstration coverage remains open on no-finding/Blocked. §4/R3 retain that human/skill reporting rule. Add a proof/report fixture or rubric negative; no new product demonstration-status service is needed. |

## Limits and preserved status

Document/design-plan review of the 27 pinned inputs, full r14-to-r15 textual diffs and requirement/AC/task/matrix cross-checks. No product code was implemented or executed; no Herdr/Claude/OpenCode inference, permission probe, real R1–R3, Actions run, GitHub write, W1 worktree/adoption, merge or example launch was performed. Read-only local git object inspection checked the named 359ffcf/4ce1110 baseline facts; it did not establish current remote PR/rules/model availability. Official GitHub and uv documentation was consulted only for indirect-merge and frozen-lockfile facts. The inherited run header reports gpt-6-astra/xhigh; no hidden reasoning was inspected. Exactly review.md and review-result.json were authored. All AC remain planned and all 17 legacy S1 findings remain open; this review is not D11 approval.

No runtime/model availability, CLI permission enforcement, runner availability, private-repo billing amount or live GitHub policy was certified by this document review. The candidate itself acknowledges that OpenCode/Astra inference and both product profiles need R1. R2 must actually reach G1 passed; R3 must supply a real finding/fix/re-review and successful resume. Neither an evidenced Blocked result nor clean-with-no-finding completes the demonstration.

