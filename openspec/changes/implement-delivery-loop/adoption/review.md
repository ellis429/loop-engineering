**Independent source-map review — D53 / T0.1 step 3, round 2**

**Verdict: clean.** The four composed specs faithfully preserve the reviewed semantics of formal original → D45-02 → D45-04. All 36 requirements and 88 AC scenarios were checked again. No semantic loss, unintended duplication, unsupported change, unapplied directive, or wrong-layer application was found. Both prior findings are **verified** as addressed; there are no current findings.

Reviewer: GPT-6 / Codex; exact runtime model identifier and configured reasoning effort are not exposed. Date: 2026-09-28.

**Hash verification and provenance**

All **16 of 16** SHA-256 values in `input-manifest.json` matched before the substantive review began. There were no input mismatches. This includes all originals, both deltas, D11 approval, composed files, source map, composition script/log, and both prior-review files. The manifest was checked again before delivery.

The two source pins in `d11-approval.json`, the D45-04 approved artifact hash, the compose-log source hashes, and the source-map source table agree:

| Source | Verified SHA-256 |
| --- | --- |
| D45-02 | `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565` |
| D45-04 | `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b` |

All eight original/composed hashes in the source-map table and compose-log also match the manifest. D53 choice A adopts the layered composition. Choice E approves the timeouts and limits, activating D45-04 §10's post-D11 paragraph.

**Round-1 findings**

| Prior finding | Status | Round-2 verification |
| --- | --- | --- |
| SM-01 — unsupported S2 allocation | **verified** | AC-O18/O08/O09/O14 now say `[延後] 由後續切片負責，第一片不算完成` at `inputs/composed/delivery-orchestration.md:35,76,81,118`; AC-D24 uses the same wording at `inputs/composed/durable-delivery.md:177`. None assigns S2. Their WHEN/THEN obligations remain intact. `inputs/compose.py:172` fixes the shared template; `inputs/source-map.md:27` records the ruling. |
| SM-02 — AC-D07 redundant-word contraction not recorded | **verified** | `inputs/source-map.md:26` now explicitly records removal of the duplicated `核對`. AC-D07 at `inputs/composed/durable-delivery.md:70` preserves the responsible actor, read-back/checking, assignment/versions/digests/evidence, import once, original attempt, and no redispatch. The requested documentation correction is complete; no semantic correction was necessary. |

The shared template also gives AC-D20 a generic deferral, consistent with D45-04 L142. AC-D23 still copies the explicit `[延後 S2，隨 AC-D20]` relationship from L140. The fix therefore does not erase that sourced relationship. Explicit S2 text remains in DUR-02, AC-G15, AC-O23 and AC-D23.

**Independent method and complete unit coverage**

I read both pinned deltas and the originals, inspected each original-to-composed diff, and independently reconstructed the expected requirement/scenario bodies using source line spans. The reconstruction applied D45-02 first, including its subsequently superseded text, and then D45-04. It did not use the author's script or source map as the expected-text oracle. All 124 complete units matched after the individually assessed editorial adjustments below and normalization of blank lines/line indentation. Continuation paragraphs and every nested bullet were included. The four preambles were separately reconstructed and matched exactly.

| Spec | Requirements | AC occurrences | Unique AC IDs | Names, titles and order |
| --- | ---: | ---: | ---: | --- |
| delivery-orchestration | 12 | 28 | 28 | Preserved |
| delivery-gates | 8 | 20 | 20 | Preserved |
| durable-delivery | 9 | 24 | 24 | Preserved |
| finding-resolution | 7 | 16 | 16 | Preserved |
| **Total** | **36** | **88** | **88** | No addition, deletion, rename or duplicate |

Twenty requirement bodies and 38 complete scenarios change. The remaining **16 requirement bodies and 50 scenarios** equal their formal originals exactly after trimming section-boundary whitespace:

| Spec | Unchanged requirement bodies | Unchanged complete scenarios |
| --- | --- | --- |
| delivery-orchestration | ORC-02, ORC-03, ORC-04, ORC-07, ORC-09, ORC-10, ORC-11, ORC-12 | AC-O03, O04, O05, O07, O10, O11, O12, O13, O16, O17, O19, O20, O21, O22, O24, O25, O26, O27, O28 |
| delivery-gates | GAT-07 | AC-G01, G02, G03, G09, G12, G20 |
| durable-delivery | DUR-04, DUR-05, DUR-07 | AC-D01, D05, D08, D09, D11, D13, D15, D16, D18, D19 |
| finding-resolution | FIN-01, FIN-02, FIN-05, FIN-07 | AC-F01, F02, F03, F04, F06, F07, F08, F09, F10, F11, F12, F13, F14, F15, F16 |

Abbreviated scenario IDs in this table retain the `AC-` prefix. Every remaining unit is covered by the directive ledger below. An unchanged requirement body can still contain scenarios with directed changes; these were compared separately.

All seven D45-04 §12 full-text units match their specified source text: GAT-06 body, AC-G13 THEN, AC-G15, AC-D10, AC-D23, AC-O15, and AC-O23 THEN. Both THEN-only replacements preserve the original WHEN. The full replacements contain no improperly retained predecessor text.

As a separate reproducibility check, I ran `compose.py` with reads mapped to the supplied sources/originals and every write captured in memory. It reproduced all four composed files byte for byte and the complete compose-log, including **82 operations**. The source map has exactly **132 unit rows**: 124 requirements/scenarios plus four banners and four Purposes. Every row agrees with the corresponding logged operations or the unchanged-unit comparison. Reproducibility corroborates the independent comparison; it is not the sole basis for the verdict.

**Delta ledger — 86 checked directive groups**

The count comprises **53 D45-02** and **33 D45-04** rows below. A grouped directive targeting multiple units counts once; carry-forward and adoption directives count where separately listed. General precedence/marker rules and D45-02 `[不變]` declarations are checked through the complete unit inventory and final-layer comparison, rather than counted as extra mutations. This definition is independent of the author's 82 operations. Line numbers refer to the pinned delta files under `inputs/sources/`.

**D45-02 baseline**

| Entry | Source lines | Target | Verified disposition |
| --- | --- | --- | --- |
| 02-01 | §0.1 L19–28 | Four banners | Applied; adoption status/hashes subsequently updated by D45-04 §12. D40 remains historical only. |
| 02-02 | L34–36 | ORC Purpose | Replacement applied; surrounding purpose retained. |
| 02-03 | L40–42 | ORC-01 | Controller/orchestrate responsibility fragment replaced. |
| 02-04 | L44 | AC-O01 THEN | Controller identity replaced with coordinator identity; remainder retained. |
| 02-05 | L45–46 | AC-O02 THEN | Entire specified THEN applied. |
| 02-06 | L47 | AC-O18 THEN | Permission and orchestrate dispatch fragment applied. |
| 02-07 | L52–53 | AC-O06 THEN | Entire replacement, including plan/version/producer approval binding, applied. |
| 02-08 | L58–59 | AC-O09 THEN | Complete task/AC collection constraint appended. |
| 02-09 | L64–66 | ORC-08 | Responsibility/one-loop fragment replaced; punctuation joined to original semicolon. |
| 02-10 | L78–80 | GAT Purpose | D40 approval/proposal wording replaced. |
| 02-11 | L84–86 | GAT-01 | G1-before-formal-G2 permission constraint applied. |
| 02-12 | L90–97 | GAT-02 | Producer/trust-boundary paragraph and all three bullets appended. |
| 02-13 | L99–100 | AC-G04 WHEN | Full replacement applied; original THEN retained. |
| 02-14 | L104–108 | GAT-03 append | Legitimately superseded in full by D45-04 §3; original formal body retained. |
| 02-15 | L110 | AC-G06 THEN append | Legitimately superseded by D45-04 L70–71 diagnostic-only replay sentence. |
| 02-16 | L111–112 | AC-G07 THEN | Entire replacement retained, as D45-04 L72 directs. |
| 02-17 | L117–119 | GAT-04 | Eligibility permission/dispatch and independence fragment replaced; remainder retained. |
| 02-18 | L121–122 | AC-G10 WHEN | Full replacement applied; original THEN retained. |
| 02-19 | L125–133 | GAT-05 | All three replacement paragraphs applied; D45-04 supplement follows them. |
| 02-20 | L135 | AC-G11/G12 | Dispatch reading applied to G11 WHEN; G12 has no matching phrase and remains unchanged. |
| 02-21 | L137–147 | GAT-06 | Legitimately superseded by D45-04 §6 full body. |
| 02-22 | L149–150 | AC-G13 THEN | Legitimately superseded by D45-04 L114–115 full THEN. |
| 02-23 | L155–156 | AC-G16 THEN | Full replacement applied, including new observation/version invalidation rules. |
| 02-24 | L157–158 | AC-G18 THEN | Full replacement applied, including fresh observation and publication before Pass. |
| 02-25 | L161–165 | GAT-08 | Old S1 evidence exclusion appended. |
| 02-26 | L167–168 | AC-G19 WHEN | Herdr/runtime verification replacement applied; THEN retained. |
| 02-27 | L175–177 | DUR Purpose opening | Feature/local-state wording applied. |
| 02-28 | L179 | DUR Purpose D40 clause | D45–D49 wording applied. |
| 02-29 | L183–185 | DUR-01 | Single-authority/single-entry replacement applied; remainder retained. |
| 02-30 | L187–188 | AC-D02 THEN | Detection/trust-boundary sentences appended. |
| 02-31 | L191–197 | DUR-02 | First two sentences replaced; original timeout/fencing sentence retained. |
| 02-32 | L199–200 | AC-D03 THEN | Entire coordinator/permission/budget replacement applied. |
| 02-33 | L201–202 | AC-D04 THEN | Stop/read-back sentence appended after original THEN, before D45-04 supplement. |
| 02-34 | L204–208 | DUR-03 | Separate external-handle and identity obligation appended. |
| 02-35 | L210 | AC-D06 WHEN/THEN | Both adapter occurrences replaced; remainder retained. |
| 02-36 | L215 | AC-D07 THEN | Responsibility replacement applied with recorded redundant-word contraction; SM-02 verified. |
| 02-37 | L220–222 | AC-D10 | Legitimately superseded by D45-04 §7 full scenario; no history-first promise remains. |
| 02-38 | L225–237 | DUR-06 append | Legitimately superseded by all six D45-04 §1 quoted paragraphs. |
| 02-39 | L239 | AC-D12 WHEN | Interruption/resumption fragment applied; THEN retained. |
| 02-40 | L244–245 | AC-D14 THEN | Entire replacement applied, including uncertain worker/worktree/coordinator handoff. |
| 02-41 | L250–252 | DUR-08 first-paragraph addition | All online/offline, stop and bounded read-back obligations retained. |
| 02-42 | L254–256 | DUR-08 pending-timeouts paragraph | Legitimately superseded by D45-04 §10 because D53 choice E approved the condition. |
| 02-43 | L258–260 | AC-D17 | Entire replacement applied and carried forward under D45-04 §10. |
| 02-44 | L265–267 | DUR-09 | Runtime/transport/profile fragment applied; remaining original obligations retained. |
| 02-45 | L269 | AC-D20 THEN | OpenCode-only orchestration fragment applied before later deferral. |
| 02-46 | L270 | AC-D21 WHEN | Herdr handles added; remainder retained. |
| 02-47 | L271 | AC-D22 WHEN | Independent-connection verification replacement applied; THEN retained. |
| 02-48 | L278 | FIN Purpose stages | D40 S1/S2/S3 replaced by H1/H2/H3 verification stages. |
| 02-49 | L280–284 | FIN-03 | Complete eligibility, G1 correction and assignment-context paragraph appended. |
| 02-50 | L286 | AC-F05 THEN | CI-policy/documentation/validation sentence appended. |
| 02-51 | L291–293 | FIN-04 | One-time rebuttal review responsibility replaced; remaining limits retained. |
| 02-52 | L299–301 | FIN-06 fragment | Orchestrate/GitHub publication responsibility applied. |
| 02-53 | L303–305 | FIN-06 append | Required PR publication and issue-summary read-back before Pass appended. |

**D45-04 overrides, carry-forward and adoption**

| Entry | Source lines | Target | Verified disposition |
| --- | --- | --- | --- |
| 04-01 | §1 L18–32 | DUR-06 append | Six quoted paragraphs replace only the D45-02 append. Formal body and D12 edit retained; retry/observation boundaries correct. |
| 04-02 | §2 L36–38 | DUR-02 append | One Implementer worktree, independent Reviewer clone/session and explicit parallel-writer S2 deferral applied. |
| 04-03 | §2 L40–45 | AC-D04 supplement | Both authoritative stop/completion alternatives and idle-alone prohibition follow original THEN and D45-02 append. |
| 04-04 | §3 L49–68 | GAT-03 append | Entire D45-02 append replaced; every Red qualification and clean-head Green/regression obligation copied. |
| 04-05 | §3 L70–71 | AC-G06 supplement | Diagnostic-only replay wording applied; predecessor replay sentence absent. |
| 04-06 | §3 L72 | AC-G07 carry-forward | D45-02 THEN retained exactly. |
| 04-07 | §3 L73 | AC-G08 THEN | Attempt-commit-range/integration-head fragment replaced; remainder retained. |
| 04-08 | §3 L74 | AC-G05 supplement | New-head Green rerun and document self-SHA exclusion appended. |
| 04-09 | §3 L75–80 | AC-G17 supplement | Opening paragraph and all five bullets copied: route, shared limits, deduplication, assignment, Red/scope. |
| 04-10 | §4 L82–84 | GAT-04 clarification | Actual-behavior eligibility preserved. No file-type-wide exclusion introduced; no separate replacement was instructed. |
| 04-11 | §5 L88–94 | GAT-05 append | All three paragraphs applied: clean/no blockers, failed versus unknown/Blocked, PR identity before review. |
| 04-12 | §5 L88 | AC-G11/G12 carry-forward | D45-02 dispatch reading retained. |
| 04-13 | §6 L98–112 | GAT-06 full body | Full replacement applied, without predecessor-body remnants. |
| 04-14 | §6 L114–115 | AC-G13 full THEN | Exact source replacement; original WHEN retained. |
| 04-15 | §6 L116–118 | AC-G15 full scenario | Full replacement includes first-slice unknown/not-Pass and explicit S2 positive-mapping deferral. |
| 04-16 | §6 L119–125 | AC-G14 supplement | Opening sentence and all six bullets applied, including all runs/attempts, pagination and commit-status unknown. |
| 04-17 | §7 L129–134 | AC-D10 full scenario | Full replacement applied; DUR-05 and D09/D11 unchanged; history-first remains outside spec commitments. |
| 04-18 | §8 L138–140 | AC-D23 full scenario | Selected-profile safeguards and explicit OpenCode-only S2/D20 relationship retained exactly. |
| 04-19 | §8 L141 | AC-D24 deferral | Generic later-slice note and first-slice exclusion applied; original scenario retained; SM-01 verified. |
| 04-20 | §8 L142, L140 | AC-D20 deferral | Layer-2 scenario preserved and generically deferred; explicit S2 relationship remains in D23. |
| 04-21 | §9 L146–148 | ORC-01 append | First-slice skill/human responsibility and unsupported-entry constraints appended. |
| 04-22 | §9 L150 | AC-O08/O09/O14/O18 | All four generically deferred with first-slice exclusion and layer-2 scenario text retained; SM-01 verified. |
| 04-23 | §9 L151–152 | AC-O23 full THEN | Full-run stop and explicit partial S2 deferral copied; original WHEN retained. |
| 04-24 | §9 L153 | AC-O12/O13 responsibility | Skill/human checks and no automatic controller release recorded in ORC-06; scenario bodies retained. |
| 04-25 | §9 L154 | ORC-05 append | Entire Pass-package projection, fields and acceptance-pending text appended. |
| 04-26 | §9 L155 | ORC-06 append | Bootstrap accepted/merged/baseline conditions and no automatic merge appended. |
| 04-27 | §9 L156–158 | AC-O15 full scenario | Exact full replacement, including no historical-trial product special cases. |
| 04-28 | §10 L162 | DUR-08 boundary/carry-forward | External-write-only read-back limit applied; read-only budget correctly references DUR-06; D47/D17 retained. |
| 04-29 | §10 L164–167 | DUR-08 post-D11 paragraph | Approved paragraph copied; neither pending-approval predecessor remains. D53 E activates it. |
| 04-30 | §11 L169–175 | Unrestated baseline | Correction, trust, tested-SHA, bootstrap, budget, finding and publication obligations retained; no extra substitution instructed. |
| 04-31 | §12 L186 | Four banners | D53/date/D11 and both exact source hashes recorded; source-map reference present. |
| 04-32 | §12 L187 | FIN Purpose approval clause | Exact D45–D49 / D11 replacement applied. |
| 04-33 | §12 L187 | Four validation references | Old validation path replaced with the D53-adopted D45-04 validation reference; step-4 destination is outside this snapshot. |

D45-02's unchanged declarations were checked at the correct layer. Later D45-04 edits to ORC-05/06, O08/O14/O15/O23, G05/G08/G14/G15/G17 and D23/D24 correctly take precedence. D45-02 §5 is a topic-to-location index; its listed obligations are accounted for above. D45-04 §11 carries existing obligations forward rather than requiring duplicate copies. No unlisted unit was changed.

**Banners, Purpose and D53**

All four banners record D53 adoption through D11 on 2026-09-28 with the two verified source hashes above. No banner or Purpose claims current D40 approval or `scope revision pending`. D40 references in the banners expressly describe historical evidence. All four Purposes retain their statements that document/spec existence does not establish product acceptance, and their old validation pointers are replaced.

DUR-08 at `inputs/composed/durable-delivery.md:134` contains the D45-04 L165 approved paragraph, including activity-interval union, approved design/`workflow.yaml` timeouts and human `policy_change`. It correctly preserves D47's online/offline stopping and bounded recovery obligations and AC-D17. This verifies adoption wording, not actual runtime timeout behavior.

**Author rulings and editorial differences**

The six-paragraph ruling at `inputs/source-map.md:24` is faithful. D45-04 L18 says “five,” but its contiguous quote at L20–30 has six named paragraphs: external writes, PR identity, human unknown handling, branch history, read-only observation, and read-failure budget. The section title and L162 explicitly require the last budget. All six are copied once, replacing only the D45-02 append. Both retained retry grounds and the bounded human recheck remain; the removed local-synchronous retry exception and read-only execution permit do not survive.

The sentence-final `。` ruling at `inputs/source-map.md:25` is faithful. AC-O09, AC-G05, AC-G06, AC-D02, AC-D04 and AC-F05 gain only a sentence separator before their appended source text. The multiline D04/G14/G17 supplements preserve their full paragraphs and bullets.

Other inspected editorial adaptations also preserve semantics: ORC-08 and GAT-04 avoid a doubled full stop before an existing semicolon; the AC-D07 redundant `核對` contraction is now explicitly recorded; the D45-04 §10 reference to `§1` becomes `DUR-06`, its destination in the composed specs; ORC-06 expresses L153's first-slice responsibility with full AC prefixes. Blank lines, quote removal, indentation, and the missing final newline in durable-delivery do not change obligations. These are not new findings.

**Deferred items**

All deferred capabilities are marked and excluded from first-slice completion: DUR-02 parallel writers; AC-G15 positive integration mapping; AC-D20 and AC-D24; the OpenCode-only portion of AC-D23; AC-O08/O09/O14/O18; and the unaffected-work continuation portion of AC-O23. AC-D24's first-slice exclusion also prevents the first-slice profile combination from serving as completion evidence. AC-O12/O13 remain skill/human checks with no automatic controller release. No unsupported S2 allocation or first-slice completion claim remains.

**Limits**

This is a snapshot-only composition review of the 16 manifest inputs, including a full rerun across every current unit. The prior review supplies the two findings to verify, not evidence that other units remain correct. No product implementation, runtime isolation, actual timeout values, product acceptance, or T0.1 step-4 validation destination/content was verified. Other artifacts whose hashes occur inside D11 approval were not supplied and were not independently validated. The exact runtime model identifier and configured reasoning effort are not exposed.

Only `review.md` and `review-result.json` were written in this workspace. Inputs were not modified.
