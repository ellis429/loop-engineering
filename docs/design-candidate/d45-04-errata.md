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
