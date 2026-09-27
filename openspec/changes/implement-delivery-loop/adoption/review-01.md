**Independent source-map review — D53 / T0.1 step 3**

**Verdict: changes_requested.** One blocking composition finding affects five deferral annotations (SM-01). One non-blocking editorial observation affects AC-D07 (SM-02). No missing or duplicated requirement/scenario, renamed AC, unaccounted-for baseline change, or incorrect full-text override was found. The two recorded author rulings preserve semantics.

Reviewer: GPT-6 / Codex. The exact runtime model identifier and configured reasoning effort are not exposed in this session. Date: 2026-09-28.

**Findings**

**SM-01 — Blocking: five unspecified deferrals are assigned specifically to S2.**

D45-04 L14 defines `[延後]` as a capability for later slices, not complete in the first slice. L150 marks O08, O09, O14 and O18 only `[延後]`; L141 says D24 goes to `後續切片`. The composed annotations instead say `[延後 S2]`. The shared `SLICE` template at `inputs/compose.py:172` supplies this extra allocation; it does not come from those delta entries or D53 choice A.

| Spec | Affected unit | Composed line | Governing source |
| --- | --- | --- |
| delivery-orchestration | AC-O18 | 35 | D45-04 §9 L150; definition L14 |
| delivery-orchestration | AC-O08 | 76 | D45-04 §9 L150; definition L14 |
| delivery-orchestration | AC-O09 | 81 | D45-04 §9 L150; definition L14 |
| delivery-orchestration | AC-O14 | 118 | D45-04 §9 L150; definition L14 |
| durable-delivery | AC-D24 | 177 | D45-04 §8 L141; definition L14 |

Expected: retain `[延後]` / `後續切片` and `第一片不算完成` for these five units, without selecting a specific later slice. The distinction is scope allocation, not punctuation, so it blocks this faithful-composition check. The original WHEN/THEN obligations are present and first-slice completion is correctly excluded.

This finding does not apply to explicitly sourced S2 designations: DUR-02 (L38), AC-G15 (L118), AC-O23 (L152), or AC-D23 (L140). AC-D23 explicitly says `延後 S2，隨 AC-D20`, which supports AC-D20's S2 annotation. That explicit link is absent for D24 and the four ORC scenarios.

**SM-02 — Non-blocking: AC-D07 contracts a redundant word beyond the two recorded rulings.**

D45-02 L215 replaces `resume/reconcile` with `orchestrate 經 controller 讀回核對` while preserving the rest. The original THEN (formal-original/durable-delivery.md:55) continues with `核對 assignment`. A literal substitution therefore yields `讀回核對 核對 assignment`; the composed THEN at line 70 says `讀回核對 assignment`. The author script deliberately matches the longer original fragment at line 310. This removes redundant wording without changing who checks, what is checked, import-once behavior, attempt identity, or the prohibition on redispatch. No semantic correction is needed; the contraction should be accounted for as an editorial normalization in an exact-copy audit.

**Manifest and provenance checks**

All 14 SHA-256 values in `input-manifest.json` were verified before reading the composition for review. All matched. Hashes were also cross-checked against the source-map before/after table, compose-log, and the two spec-source pins in D53. The supplied D11 approval's D45-04 artifact hash matches the same D45-04 input. Other approval-manifest artifacts are outside this snapshot.

| Manifest path (under inputs/) | Verified SHA-256 |
| --- | --- |
| `compose-log.json` | `fa0d242003ed1e7e7c82ab4b24ada2834296476d720ac8c9f84c9b6438d36d58` |
| `compose.py` | `4faff8d1f39d35e3b52934347a4aef89069cfd63850f3ddde8044e0685c4175c` |
| `composed/delivery-gates.md` | `7cdf2ee0b1bd4f0be007169d6d0599e1e9320bef2a486e4ebd9285a550907a5f` |
| `composed/delivery-orchestration.md` | `010a68306e7b5d6968c4c3538ae97814a8aa29e2c54c2d26f54474a98dc48a96` |
| `composed/durable-delivery.md` | `75561e31fdb0a0de225831f894534fd1edcd6d36ccf2b548c5023a33b51bbe64` |
| `composed/finding-resolution.md` | `e46512eb6061717adf7b54b48a6d6e2b285cc37f29167a4401594adc0f939cb2` |
| `formal-original/delivery-gates.md` | `a8d68b7c03e45a55da796f8b223d7534266010af534e8c0506f36f66b0218d91` |
| `formal-original/delivery-orchestration.md` | `a54c18f808079dfe8d2c032a574eda5411916566124909ca4149fa4a46161c25` |
| `formal-original/durable-delivery.md` | `f873aae0d549f5f8e11cfcca801cf78610aa970d071c09fcd5776f814ca5a9f6` |
| `formal-original/finding-resolution.md` | `2f37c77709d526b2259b2285c99617fe8d4a2768cb318ccf860dec8a8b6c8629` |
| `source-map.md` | `449365d91d23b0d2defb7433153408b6c08cd72a405988beeab8d91b0ad6c969` |
| `sources/d11-approval.json` | `766699a53f2402b85f6757345e7fcee4dc7fcd72f8859a0a8713364d74f4ecbd` |
| `sources/d45-02-spec-delta.md` | `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565` |
| `sources/d45-04-spec-delta.md` | `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b` |

**Independent comparison method and coverage**

I parsed the four originals and composed files into requirement bodies and complete scenario bodies, including continuation paragraphs and nested bullets. I independently selected source spans and applied the D45-02 edits before the D45-04 replacements/appends. Superseded D45-02 edits were included in this reconstruction, rather than silently skipped. Comparison covered all 124 units; whitespace/layout and the explicitly discussed punctuation/word normalization were evaluated separately. Source-map claims were not used as the expected-text oracle.

The author script was additionally executed with an in-memory file adapter: reads were restricted to the supplied sources/originals and all writes went to memory. It reproduced all four composed files byte for byte and all 82 compose-log operations. This establishes reproducibility, not correctness by itself. The source map contains every one of the 124 requirement/scenario units exactly once and its eight before/after file hashes match.

| Spec | Requirements | AC occurrences | Unique AC IDs | Header/order comparison |
| --- | ---: | ---: | ---: | --- |
| delivery-orchestration | 12 | 28 | 28 | All original names, titles and order preserved |
| delivery-gates | 8 | 20 | 20 | All original names, titles and order preserved |
| durable-delivery | 9 | 24 | 24 | All original names, titles and order preserved |
| finding-resolution | 7 | 16 | 16 | All original names, titles and order preserved |
| Total | 36 | 88 | 88 | No renamed, dropped, duplicated or added ID |

Twenty requirement bodies and 38 scenarios change through composition. The remaining 16 requirement bodies and 50 complete scenario bodies match the originals exactly after removing only their surrounding section-boundary whitespace. The inventory below identifies every unchanged unit; the delta ledger identifies every changed unit and all superseded source edits.

| Spec | Unchanged requirement bodies | Unchanged complete scenarios |
| --- | --- | --- |
| delivery-orchestration | ORC-02, ORC-03, ORC-04, ORC-07, ORC-09, ORC-10, ORC-11, ORC-12 | AC-O03, AC-O04, AC-O05, AC-O07, AC-O10, AC-O11, AC-O12, AC-O13, AC-O16, AC-O17, AC-O19, AC-O20, AC-O21, AC-O22, AC-O24, AC-O25, AC-O26, AC-O27, AC-O28 |
| delivery-gates | GAT-07 | AC-G01, AC-G02, AC-G03, AC-G09, AC-G12, AC-G20 |
| durable-delivery | DUR-04, DUR-05, DUR-07 | AC-D01, AC-D05, AC-D08, AC-D09, AC-D11, AC-D13, AC-D15, AC-D16, AC-D18, AC-D19 |
| finding-resolution | FIN-01, FIN-02, FIN-05, FIN-07 | AC-F01, AC-F02, AC-F03, AC-F04, AC-F06, AC-F07, AC-F08, AC-F09, AC-F10, AC-F11, AC-F12, AC-F13, AC-F14, AC-F15, AC-F16 |

All seven units explicitly designated full text by D45-04 §12 match their selected D45-04 text after removing quote/layout syntax: GAT-06 body, AC-G13 THEN, AC-G15, AC-D10, AC-D23, AC-O15, and AC-O23 THEN. Original WHEN text is retained for the two THEN-only replacements. No predecessor text was improperly merged into those full replacements.

**Delta inventory: 86 checked source-directive groups**

The count is defined by the numbered rows below: 53 D45-02 edit directives and 33 D45-04 override, carry-forward and adoption directives. A source instruction targeting multiple units is one row (for example, the common banner, D06 WHEN/THEN, or four ORC deferrals). D45-02 `[不變]` declarations and general precedence/marker rules are checked through the unchanged inventory and later-layer ledger, not counted as extra edit rows. This count is independent of the author's 82 mutation operations.

**D45-02 baseline — all entries accounted for**

| Entry | Source | Target | Disposition |
| --- | --- | --- | --- |
| 02-01 | §0.1 L19–28 | All four banners | Applied, then adoption status/hashes updated by D45-04 §12; historical D40 disclaimer retained. |
| 02-02 | §1 L34–36 | ORC Purpose | Applied replacement; surrounding purpose retained. |
| 02-03 | L40–42 | ORC-01 body | Applied controller/orchestrate responsibility replacement. |
| 02-04 | L44 | AC-O01 THEN | Applied identity terminology replacement; remainder retained. |
| 02-05 | L45–46 | AC-O02 THEN | Applied full THEN replacement. |
| 02-06 | L47 | AC-O18 THEN | Applied dispatch-permission replacement; D45-04 deferral also applies (SM-01). |
| 02-07 | L52–53 | AC-O06 THEN | Applied full THEN replacement, including approval/version/provenance and first lawful permission. |
| 02-08 | L58–59 | AC-O09 THEN | Applied append; original THEN retained; later deferral has SM-01. |
| 02-09 | L64–66 | ORC-08 body | Applied fragment replacement; adjacent punctuation normalized without changing obligations. |
| 02-10 | §2 L78–80 | GAT Purpose | Applied replacement; D40 current-approval claim removed. |
| 02-11 | L84–86 | GAT-01 body | Applied permission-before-G2 replacement; remainder retained. |
| 02-12 | L90–97 | GAT-02 body | Applied producer/trust-boundary append, including all three bullets. |
| 02-13 | L99–100 | AC-G04 WHEN | Applied replacement; original THEN retained. |
| 02-14 | L104–108 | GAT-03 body append | Legitimately superseded in full by D45-04 §3 L51–68; original formal body remains. |
| 02-15 | L110 | AC-G06 THEN append | Legitimately superseded by D45-04 §3 L70–71; no mandatory normal-path replay remains. |
| 02-16 | L111–112 | AC-G07 THEN | Applied; explicitly retained by D45-04 §3. |
| 02-17 | L117–119 | GAT-04 body | Applied eligibility/independence fragment; remaining formal obligations retained. |
| 02-18 | L121–122 | AC-G10 WHEN | Applied replacement; original THEN retained. |
| 02-19 | L125–133 | GAT-05 body | Applied all three replacement paragraphs; subsequently appended D45-04 §5. |
| 02-20 | L135 | AC-G11 / AC-G12 reading | G11 dispatch wording expanded as instructed. G12 has no matching dispatch wording and remains unchanged. |
| 02-21 | L137–147 | GAT-06 body | Legitimately superseded by D45-04 §6 full body; not combined with obsolete text. |
| 02-22 | L149–150 | AC-G13 THEN | Legitimately superseded by D45-04 §6 full THEN. |
| 02-23 | L155–156 | AC-G16 THEN | Applied full replacement, including newer observations versus historical late results. |
| 02-24 | L157–158 | AC-G18 THEN | Applied full replacement, fresh observation and publication preconditions included. |
| 02-25 | L161–165 | GAT-08 body | Applied old-S1-evidence exclusion append. |
| 02-26 | L167–168 | AC-G19 WHEN | Applied replacement; original THEN retained. |
| 02-27 | §3 L175–177 | DUR Purpose opening | Applied feature/local-authority wording replacement. |
| 02-28 | L179 | DUR Purpose D40 clause | Applied D45–D49 replacement. |
| 02-29 | L183–185 | DUR-01 body | Applied single-authority/single-entry replacement; remainder retained. |
| 02-30 | L187–188 | AC-D02 THEN | Applied append; trust boundary preserved. |
| 02-31 | L191–197 | DUR-02 body | Applied first-two-sentence replacement; original timeout/fencing sentence retained. |
| 02-32 | L199–200 | AC-D03 THEN | Applied coordinator/permission/budget replacement. |
| 02-33 | L201–202 | AC-D04 THEN | Applied stop/read-back append after original THEN; retained under D45-04 §2. |
| 02-34 | L204–208 | DUR-03 body | Applied separate external-handles/identity append. |
| 02-35 | L210 | AC-D06 WHEN and THEN | Both occurrences of adapter replaced by runtime 讀回工具; other text retained. |
| 02-36 | L215 | AC-D07 THEN | Applied responsibility transfer, with redundant 核對 collapsed (non-blocking SM-02). |
| 02-37 | L220–222 | AC-D10 whole scenario | Legitimately superseded by D45-04 §7 full scenario; history-first implementation detail removed as directed. |
| 02-38 | L225–237 | DUR-06 body append | Legitimately superseded by all six D45-04 §1 quote paragraphs; original formal body retained. |
| 02-39 | L239 | AC-D12 WHEN | Applied interruption/resumption replacement; original THEN retained. |
| 02-40 | L244–245 | AC-D14 THEN | Applied full replacement, including unknown ownership/worktree/worker handoff. |
| 02-41 | L250–252 | DUR-08 first-paragraph addition | Applied complete D47 online/offline/stop/read-back constraints. |
| 02-42 | L254–256 | DUR-08 pending-timeouts paragraph | Legitimately superseded by D45-04 §10 post-D11 paragraph because D53 choice E approved it. |
| 02-43 | L258–260 | AC-D17 whole scenario | Applied full replacement; D45-04 §10 retains it. |
| 02-44 | L265–267 | DUR-09 body | Applied runtime/transport/profile fragment; other original text retained. |
| 02-45 | L269 | AC-D20 THEN | Applied OpenCode-only orchestration replacement; deferral added under D45-04 §8. |
| 02-46 | L270 | AC-D21 WHEN | Applied Herdr-handle addition; original THEN retained. |
| 02-47 | L271 | AC-D22 WHEN | Applied independent-connection-validation replacement; original THEN retained. |
| 02-48 | §4 L278 | FIN Purpose stage wording | Applied H1/H2/H3 wording in place of D40 S1/S2/S3. |
| 02-49 | L280–284 | FIN-03 body | Applied full correction-eligibility/G1-fix/assignment-context append. |
| 02-50 | L286 | AC-F05 THEN | Applied CI-policy/documentation/validation append. |
| 02-51 | L291–293 | FIN-04 body | Applied controller-permission/orchestrate dispatch replacement; one-rebuttal limit retained. |
| 02-52 | L299–301 | FIN-06 body fragment | Applied GitHub publication responsibility transfer. |
| 02-53 | L303–305 | FIN-06 body append | Applied required PR publication and issue-summary read-back before Pass. |

**D45-04 overrides and carry-forward — all entries accounted for**

| Entry | Source | Target | Disposition |
| --- | --- | --- | --- |
| 04-01 | §1 L18–32 | DUR-06 body append | Applied all six quoted paragraphs, replacing only D45-02 append. Both retained retry grounds and bounded human recheck remain; local synchronous retry exception and read-only permits removed. |
| 04-02 | §2 L36–38 | DUR-02 body append | Applied one Implementer worktree, independent Reviewer clone/session, and explicit parallel-writer [延後 S2]. |
| 04-03 | §2 L40–45 | AC-D04 THEN supplement | Applied both authoritative stop/completion alternatives and idle-alone exclusion, after formal THEN and D45-02 append. |
| 04-04 | §3 L49–68 | GAT-03 body append | Applied complete replacement append, all Red eligibility/lineage/scope rules and clean-head Green/regression requirements included. |
| 04-05 | §3 L70–71 | AC-G06 THEN supplement | Applied diagnostic-only replay wording after formal THEN; D45-02 replay sentence absent. |
| 04-06 | §3 L72 | AC-G07 THEN carry-forward | Confirmed D45-02 full replacement remains. |
| 04-07 | §3 L73 | AC-G08 THEN | Applied attempt-commit-range/integration-head replacement; remainder retained. |
| 04-08 | §3 L74 | AC-G05 THEN supplement | Applied new-head Green rerun and document self-SHA exclusion. |
| 04-09 | §3 L75–80 | AC-G17 THEN supplement | Applied opening paragraph and all five bullets: route, shared limits, deduplication, assignment, Red/scope. |
| 04-10 | §4 L82–84 | GAT-04 / N/A clarification | Inherited actual-behavior test remains; no file-type-wide exclusion added. No separate replacement instructed. |
| 04-11 | §5 L88–94 | GAT-05 body append | Applied all three paragraphs: clean/no blockers, failed versus unknown/Blocked, and PR identity before dispatch. |
| 04-12 | §5 L88 | AC-G11 / AC-G12 carry-forward | Confirmed D45-02 reading retained. |
| 04-13 | §6 L98–112 | GAT-06 full body | Exact full replacement after dequoting; no obsolete predecessor body retained. |
| 04-14 | §6 L114–115 | AC-G13 full THEN | Exact replacement; WHEN retained. |
| 04-15 | §6 L116–118 | AC-G15 whole scenario | Exact replacement, including explicit [延後 S2] positive mapping and first-slice unknown/not-Pass. |
| 04-16 | §6 L119–125 | AC-G14 THEN supplement | Applied opening sentence and all six bullets, including run/attempt/PR matching, pagination and commit-status unknown. |
| 04-17 | §7 L129–134 | AC-D10 whole scenario | Exact full replacement; DUR-05 body and D09/D11 retained; no history-first spec promise added. |
| 04-18 | §8 L138–140 | AC-D23 whole scenario | Exact full replacement; selected-profile limits and OpenCode-only [延後 S2，隨 AC-D20] retained. |
| 04-19 | §8 L141 | AC-D24 deferral | Original scenario retained and first-slice exclusion marked, but generic later-slice deferral narrowed to S2: SM-01. |
| 04-20 | §8 L142, read with L140 | AC-D20 deferral | D45-02 scenario retained and marked deferred; S2 connection is expressly supplied by AC-D23 at L140. |
| 04-21 | §9 L146–148 | ORC-01 body append | Applied first-slice workflow/skill/human boundaries and unsupported-entry checks. |
| 04-22 | §9 L150 | AC-O08 / O09 / O14 / O18 deferrals | All four marked and original/layer-2 scenarios retained, but unspecified later slice narrowed to S2: SM-01. |
| 04-23 | §9 L151–152 | AC-O23 full THEN | Exact replacement; original WHEN retained; full-run stop and explicit partial S2 deferral present. |
| 04-24 | §9 L153 | AC-O12 / AC-O13 execution responsibility | Applied to ORC-06 supplemental paragraph; both scenario texts retained; no automatic controller release. |
| 04-25 | §9 L154 | ORC-05 body supplement | Applied complete Pass-package projection/fields/pending-acceptance text. |
| 04-26 | §9 L155 | ORC-06 body supplement | Applied bootstrap accepted/merged/baseline preconditions and no automatic merge. |
| 04-27 | §9 L156–158 | AC-O15 whole scenario | Exact replacement; no product special case for P03/Q-TARGET. |
| 04-28 | §10 L162 | DUR-08 read-back boundary / carry-forward | Applied external-write-only limit and DUR-06 read-failure-budget reference; D47 and AC-D17 preserved. |
| 04-29 | §10 L164–167 | DUR-08 post-D11 paragraph | Applied approved paragraph exactly, followed by L162 boundary; D53 E satisfies the stated condition. |
| 04-30 | §11 L169–175 | Unrestated baseline obligations | Checked carry-forward of corrections, trust boundaries, per-job SHA/bootstrap distinctions, findings and publication; no new text substitution instructed. |
| 04-31 | §12 L186 | All four adoption banners | D53/date/D11 and both exact pinned source hashes recorded; D40 historical-only wording retained. |
| 04-32 | §12 L187 | FIN Purpose D40 clause | Applied exact D45–D49 / D11 replacement. |
| 04-33 | §12 L187 | All four validation references | Old validation pointer removed; D53-adopted D45-04 validation source named. T0.1 step-4 destination is outside supplied inputs. |

D45-02 provisions marked unchanged but later modified by D45-04 were checked at the final layer: ORC-05/06, O08/O14/O15/O23, G05/G08/G14/G15/G17, D23/D24 and the affected runtime deferrals. The baseline unchanged marker does not override the later delta. The §4 N/A explanation is already represented by the original actual-behavior requirement plus D45-02's independent eligibility check; no extra file-type exception or restriction was introduced.

**Banners, Purpose, and D53**

All four banners identify D53 adoption on 2026-09-28 through D11 and record both hashes:

- D45-02: `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565`.
- D45-04: `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b`.

None retains `scope revision pending` as current status. All D40 references in the banners are explicitly historical; no Purpose claims D40 approval for the current version. All four old validation references were replaced by the D53-adopted D45-04 validation source. The actual step-4 adopted destination/content is not supplied, so this review confirms the pointer/status update rather than completion of step 4.

D53 choice E expressly approves timeouts and limits. DUR-08 therefore correctly contains the D45-04 §10 post-D11 paragraph, including activity-interval union, approved design/workflow timeouts and human `policy_change`, rather than either earlier pending-approval paragraph. D47 online/offline stopping, bounded read-back and AC-D17 are preserved.

**Author rulings and formatting**

The six-paragraph §1 ruling is faithful. Although L18 says five paragraphs, the contiguous quote at L20–30 has six named paragraphs: external writes, PR identity, human handling of unknown, branch history, read-only observation, and read-failure budget. All six are copied once, replacing only the D45-02 append. Omitting the sixth would lose the persistent failure budget explicitly named by the section. Both retained retry grounds, human bounded recheck, and the distinction between write read-back and read-only observation remain intact.

The sentence-final `。` ruling is faithful. At AC-O09, AC-G05, AC-G06, AC-D02, AC-D04 and AC-F05 it separates an existing unterminated THEN sentence from the appended source sentence without changing either obligation. The multiline additions to D04/G14/G17 retain their complete source paragraphs and bullets.

Two replacement fragments also avoid doubled punctuation by omitting the source quote's terminal `。` before an existing `；`: ORC-08 and GAT-04. These are non-semantic punctuation joins. AC-D07's redundant-word contraction is separately recorded as SM-02. Moving §10's `§1` reference to `DUR-06` correctly preserves the reference after composition.

**Deferred capability check**

All deferred items are visibly marked and none is claimed complete in the first slice: parallel writers in DUR-02; AC-G15's positive integration mapping; AC-D20, AC-D24 and the OpenCode-only part of AC-D23; AC-O08/O09/O14/O18; and the unaffected-work continuation part of AC-O23. AC-O12/O13 remain skill/human checks with no automatic controller release. The first-slice exclusion passes; the extra S2 allocation on five notes is the blocking issue in SM-01.

**Limits**

Snapshot-only composition review of the 14 input-manifest entries. 86 enumerated source-directive groups checked (53 D45-02 and 33 D45-04; grouped multi-target/carry-forward entries are defined in review.md), independently of the author's 82 operations. No product implementation, runtime isolation, actual timeout values, or T0.1 step-4 validation destination was verified. Other artifacts whose hashes appear inside d11-approval.json were not supplied and were not independently validated. Exact runtime model identifier and configured reasoning effort were not exposed.

Only `review.md` and `review-result.json` were written in this review workspace. No input was modified.

