You are the independent G2 reviewer (GPT-6 Astra) for the whole pull request of Feature 1, change `run-decisions`, in a fresh session. Read-only: do not modify files, no git commands that write, no GitHub writes. The Implementer of every task was Claude Opus 5.5; per-task reviews were done by GPT-6 Astra in other sessions — do not rely on them; judge the whole set yourself.

Version set: PR #37, base main `2ab642d`, head `3e98902`. The working directory is a fresh clone detached at the head. Review the whole diff `2ab642d...3e98902` (merge base `c91b774`).

## Judge against
- The fixed spec: `openspec/changes/run-decisions/specs/*/spec.md` and `proposal.md` (20 acceptance IDs: AC-O01 O03 O05 O07 O15 O19 O22 O23 O26 O29 O30, G21 G22, D01 D02 D03 D09 D10 D11 D25).
- The approved design and plan: `openspec/changes/run-decisions/design.md` and `tasks.md` (plan commit `5a0a92f`; the 驗收驗證 section maps each AC to tests).
- `docs/decisions.md` (D52, D53, D57, D58, D68, D75) and the high-level design `docs/design-candidate/d45-04/` with its errata.

## Check
1. **Acceptance**: for each of the 20 AC IDs, does the implementation make the scenario's THEN true, and is there a test that would fail if it were not? List each AC with verdict and evidence.
2. **Whole-change correctness**: interactions across tasks (store ↔ decisions ↔ next ↔ cli), state persistence and crash recovery, locking and concurrency, authorization before any write, idempotency and conflicts, io_error commit boundaries, reads never writing, untrusted state never overwritten. Demonstrate defects with concrete inputs/state → wrong result.
3. **Scope**: nothing outside the spec's scope (no dispatch, no GitHub reads, no G1/G3 evaluation); no test-only hooks in production code; no TODO/temporary code.
4. **CI and packaging**: `.github/workflows/loopctl-ci.yml`, `workflow.yaml`, `pyproject.toml`, `scripts/dist-smoke.sh` match design D12 and validation §6.1 (actions pinned to SHAs, PR head checked out and verified).
5. **Commits**: format per tasks.md 共同規則; no AI attribution trailers.

You may run read-only commands. The coordinator's G1 (fresh clone, head and head merged with main): uv sync --frozen, pytest 167 passed, ruff, mypy, dist-smoke all exit 0.

Blocking: violates spec/design/plan, a provable correctness or security defect, or a missing required verification. Style preferences are non-blocking. Set `requires_spec_change` when a finding cannot be fixed without changing spec, design or plan. Set `still_at_current_head` "yes". Do not report speculative issues.

## Output
JSON per the schema. `task` = "G2 run-decisions"; `reviewed_ranges` ["2ab642d...3e98902"]; finding IDs G2-01, G2-02…; `ac_rows` one entry per acceptance ID (row = AC id, tests = the proving tests, asserts_row, red_valid "not_applicable" unless you checked a Red, note = your verdict); `verdict` clean only if no blocking finding; `limits` = what you could not verify.
