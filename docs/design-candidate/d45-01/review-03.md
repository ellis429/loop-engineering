# Final bounded recheck of revision-02

**Verdict: changes_required, limited to two adjacent residuals.** Both preceding counterexamples are fixed: reconcile no longer consumes begin, and due stops precede unrelated reconciliation. Two narrow contradictions introduced in those edits prevent marking R01/R02 fully verified. No other design scope was reviewed. Manifest hashes match.

| ID | Status | Result |
| --- | --- | --- |
| D45-R01 | residual | Readback exemption verified (`design.md:84–85,148,150,179,342–344`); initial read-only operations remain inconsistently classified below. |
| D45-R02 | residual | Deadline-stop priority and no resend after issued stop verified (`design.md:160,238,242–249,303`); prepared-but-unsent stop is omitted below. |
| D45-R03 | verified, carried | Version/observation and Pass sections are unchanged from review-02. |
| D45-R04 | verified, carried | Checking publication sequence and GitHub publication section are unchanged from review-02. |
| D45-R05 | verified, carried | Cleanup document is byte-identical to review-02. |
| D45-R06 | verified, carried | Cleanup document is byte-identical to review-02. |

**D45-R01 — Medium; residual before design readiness.** At `design.md:84`, execution mode is restricted to operations with external side effects. But `design.md:184,188` explicitly puts initial `herdr observe`/`gh observe` in execution mode, and line 163 defines gh_observe as a read without side effects. Reconcile mode at line 85 only accepts existing in-flight/unknown operations, so a new prepared gh_observe has no consistently defined mode. The prior lost-receipt counterexample is fixed. **Minimal correction:** define execution mode as initial execution or permitted retry of a registered operation, including read-only observation; define reconcile as readback of an existing attempt without reissuing its original action. Keep begin single-owner and retain retry accounting. No third mode or new platform is needed. Basis: the original R01 protocol consistency and AC-D12/D13/D16.

Exact replacement for line 84’s opening: 「**執行／重試模式**（`tool … --op OP`）：用於已登記 operation 的首次執行（包含唯讀 observation）或明確失敗後允許的重試。由該 tool 在同一程序內呼叫 `api.begin`，拿到 `execute:true` 才做一次原操作，最後 `api.record`。」Keep line 85’s reconcile exemption.

**D45-R02 — High; residual before design readiness.** `design.md:243–245` only covers an attempt with no stop op, or an existing stop in-flight/unknown. Counterexample: deadline creates a stop via prepare, then the coordinator exits before calling the tool. On restart the worker is still active and its stop is `prepared`: it is neither absent nor already issued, so the priority branch has no defined next action. Treating every existing stop as readback would query for an action never sent. **Minimal correction:** explicitly select execution of the same prepared stop op; use readback only after that op's begin/possible issuance. Keep the original ID and never create or resend an issued stop. This preserves the fixed deadline priority and the issued-stop readback rule. Basis: original R02, DUR-08/AC-D17 and operation persistence. No supervisor is needed.

Replace lines 243–245’s state branches with: 「若沒有 stop op → prepare 同一 attempt 的 stop；若 stop op 為 `prepared` → 執行該既有 stop op（經 begin，只送一次）；若為 `in_flight`／`outcome_unknown` → 只讀回該既有 stop op，不重送。僅有 stop op 存在不代表已送出；是否可能已送出依 begin 後的狀態判定。」

DN-2/DN-3 clarifications and the DN-1 no-fallback note are carried verified: `decisions-needed.md` is byte-identical to review-02. **All policy choices remain unapproved.** Original historical Red remains mandatory; 403/`test` never constitute policy approval.

Hashes and unchanged-section checks are recorded in `review-result.json`. This is document verification only, not full-design clean, product G2, executed tests, S1 closure or D11 authorization. No product code/tests or GitHub operations were run. Tasks, coverage, spec-delta and validation remain outside this bounded check.
