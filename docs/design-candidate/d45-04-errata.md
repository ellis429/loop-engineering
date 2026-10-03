# D45-04 revision-17 勘誤

D53 核准的候選檔（`docs/design-candidate/d45-04/`，publication-manifest sha256 `b408e3da…`）綁定 hash，原檔不改。本檔列出之後由 Lead 裁定的更正，效力等同改寫對應段落；實作、審查與驗收一律照「原檔＋本檔」判斷。每一項都來自 thin-controller 逐 task review 的 finding，Lead 裁定日期與追蹤 issue 見各項。

## E-1 design §4：op 新增終態 `superseded`

- 來源：T2.3-07、T2.3-08，Lead 裁定 2026-09-28；追蹤 #9。
- 原文：§4 的 op 狀態只有 `prepared → in_flight → succeeded | failed（確定未送達）| unknown`。
- 更正：加一個終態 `superseded`。
  - 條件：op 紀錄的核准與目前的核准不同，而且狀態是 `prepared`（從未送出），或是 `failed` 且確定未送達。
  - 效果：controller 把它標成 `superseded`，記下原因與新舊兩個核准；舊的 argv 永遠不再送出；routing 在目前的核准下產生新的 op ID。
  - 不適用：`in_flight` 與 `unknown` 的 op 可能已經生效，永遠不標 `superseded`，照舊走 readback 與 `resolve_operation`。
- 理由：沒有這個終態，`scope_change` 後重新核准時，沒送出的 op 佔住固定的 op ID，run 無法繼續（T2.3-07）；GitHub routing 會一直提出 `write` 拒絕的 push／`pr_ensure`（T2.3-08）。
- 驗證：validation 的 w 列（外部寫入）加上這個終態的案例：核准改變後 `prepared` 與確定未送達的 `failed` 變成 `superseded` 且不重送；`in_flight`、`unknown` 不受影響。

## E-2 tasks.md：T7.1 的擁有路徑加 `src/loopctl/cli.py`

- 來源：T7.1-05，Lead 裁定 2026-09-28（計畫漏列，比照 T2.3 延伸 `next.py` 的前例）；追蹤 #11。
- 原文：T7.1 擁有 `src/loopctl/budget.py`、`src/loopctl/next.py`、`tests/test_budget.py`；共用檔案表中 `cli.py` 只允許各 task 加自己的子指令。
- 更正：T7.1 另外擁有 `src/loopctl/cli.py` 裡的兩件事：`status` 結果的 `budget` 欄位，以及到期後 `status`／`next`／`safety`／`write` 拒絕寫入的處理。共用檔案表的 `cli.py` 列加上這個例外。
- 程式變更已接受，不需重做。

## E-3 validation h7：G2 的格子歸 T5.1

- 來源：T6.1-07，Lead 裁定 2026-09-28；追蹤 #12。
- 原文：h7 含 G2 失效與重新審查的格子，但 G2 由 T5.1 實作；T6.1 的 h7 測試只斷言 G1 與 G3。
- 更正：h7 的 G2 格子歸 T5.1。T5.1 的派工、完成條件與測試都要涵蓋這些格子；T6.1 的完成條件只含 h7 的 G1、G3 格子，不為 G2 格子負責。
- 影響：T5.1 重新派工時，派工內容要列出 h7 的 G2 格子。

## E-4 需求輸入的位置

- 來源：D75（roadmap 確認），2026-09-30。
- 原文：本目錄的 `tasks.md` 等檔案以 `openspec/changes/implement-delivery-loop/` 指稱正式 change 與其中的 specs。
- 更正：該 change 已退役並刪除。四份 capability 與 source-map 原樣搬到 `docs/requirements/delivery-controller/`（`specs/<capability>/spec.md`、`adoption/source-map.md`），sha256 不變；其餘檔案（proposal、design、tasks、approval、adoption 審查紀錄）以 commit `a1d8906` 的版本為準。
- 影響：本目錄提到舊路徑的地方，照新位置讀；切法與執行順序改依 [roadmap](../roadmap.md)，本目錄的 tasks 執行表只作參考。

## E-5 派工 runtime 改為 Orca

- 來源：D76，2026-10-02。
- 原文：design §6 與相關段落以 Herdr 0.9.1 為 transport（`herdr` 工具、D21 handle 欄位 `{herdr_session, pane, agent_name, native_session_id}`），Reviewer profile 為 Herdr＋OpenCode＋`openai/gpt-6-astra`。
- 更正：transport 改為 Orca（`orca orchestration worker-start`，工作區 `engineer`、`reviewer`）；Reviewer 改為 Orca 的 Codex agent＋`gpt-6-astra`（effort xhigh），Implementer 為 Orca 的 Claude agent＋`claude-opus-5-5`。handle 欄位改以 Orca 的 Run、Task、Dispatch ID 加 native session ID 表示，具體欄位由 Feature 2 的 design 定。協調權仍是 loopctl 的 claim token；Orca gate 不作決策紀錄。
- 影響：本目錄提到 Herdr 的地方照 Orca 讀；R1 preflight 改對 Orca 的兩個 profile 執行，Orca 版本改變時重跑。

## E-6 時間上限改為察覺卡住

- 來源：D79，2026-10-03。
- 原文：design §10 與 validation 的 b0～b7 以主動執行時間 4 小時、worker 45 分、review 30 分、CI 等待 30 分為上限，到期停止並 Blocked；需求輸入 DUR-08 的「4h 主動執行」與 AC-D17「Active budget 到限與恢復」。
- 更正：不設時間上限。改為察覺卡住：session 結束卻沒有交結果、API 或 infra 錯誤，或連續一段時間（預設 30 分鐘，寫在 `workflow.yaml`）沒有新輸出時，停止派工、保存理由與證據並交人；停止與讀回的有界規則、unknown 不視為已停止、修正 3 輪與 infra 額外重試 2 次都不變。
- 影響：AC-D17 照「察覺卡住並停下交人」讀；b 系列中以時間上限為前提的案例不再適用，Feature 2 的 spec 依此改寫。
