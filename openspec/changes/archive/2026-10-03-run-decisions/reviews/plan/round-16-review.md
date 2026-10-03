verdict: changes_requested

有兩項需要修正；`history_ahead` 的方向合理，但測試 (b) 還原錯版本，且讀取規則尚未處理並行提交造成的誤判。

**P10-01｜major**

- **位置**：[tasks.md:214](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md:214)
- **問題**：(b) 要求還原到「核准那一版」，隨後期待 `history_ahead`，與新規則矛盾。若核准為 revision 7、撤銷為 8，還原 7 只讓 history 領先一版；正確行為是讀回 revision 8，不會回 exit 5。
- **依據（事實）**：[G2 原文:13](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/g2-1/result.json:13) 還原的是**核准前的 revision 6**，因此舊 reader 誤讀核准版 7、漏掉撤銷版 8。[design.md:156](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:156) 允許領先一版；:158 只拒絕超過一版。以現有 reader／next 配合純記憶體檔案重現：還原 6 得到 `dispatch`；還原 7 得到 revision 8、`human`、`plan_superseded:s-1`。
- **建議**：(b) 改為保存並還原「文件登記完成、尚未核准」的版本。另將還原核准版的情況保留為正向案例，期待讀回撤銷版且不寫檔。不要擴大 `history_ahead` 條件來滿足目前的錯誤期待，否則會破壞正常中斷恢復。

**P10-02｜major**

- **位置**：[design.md:158](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:158)
- **問題**：新增判斷未要求從一致的讀取結果比較 revision。讀者先取得舊 `feature.json`，再看到合法提交產生的新 history，就可能誤報 `history_ahead`。
- **依據（事實）**：[store.py:155](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/src/loopctl/store.py:155) 的 `load` 直接讀取，沒有持鎖；:177 先讀 feature bytes。[design.md:173](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:173) 僅明定提交持鎖，:192 要求寫入前先前移。[G2 原文:15](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/g2-1/result.json:15) 也明確要求並行讀寫的驗證。
- **依據（推論）**：合法交錯可以是：讀者取得 F2／H3 的 F2 bytes → writer 前移為 F3 → writer 建立 H4 → 讀者掃到 H4。磁碟上的差距始終不超過一版，但讀者用舊 F2 比較會得到 `4 > 2 + 1`，誤報 exit 5。
- **建議**：明定確認 `history_ahead` 時的一致性策略，例如在既有 lock 下重新讀取確認，並區分 commit 已持鎖的路徑，避免重複取鎖。補一個可控制上述交錯的測試；保持不建立 lock、不修復 feature 的唯讀契約。

Red 核對：

| 新測試參數 | 判斷 |
|---|---|
| (a) F2、history 到 4 | 可在 `code == 5` 失敗：舊 reader 回 0／revision 3；新規則可使其 Green。 |
| (b) 目前寫法：F7、history 到 8 | 能在 `code == 5` 失敗，但實際已回撤銷版、不是 `dispatch`；依正確 D4 實作仍無法 Green。 |
| (b) 改為 G2 原情境：F6、history 到 8 | 可在指定斷言失敗，且能由新規則修正。 |

其他一致性：在一致的讀取結果下，正常 F1／H2，以及連續兩次中斷後的 F3／H4，都不符合 `history_ahead`，既有預期可保留。新規則本身只拒絕、不寫檔，也與 [人工處理段落:162](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:162)「只往最新完整 history 修復」一致。

實際核對：指定 diff、`design.md`、`tasks.md`、`specs/durable-delivery/spec.md`、G2 `result.json`、`src/loopctl/{store,cli,state,next,decisions}.py`、`tests/{test_state,test_decisions}.py`、spec-to-plan 相關規則。未執行會寫檔的測試套件。