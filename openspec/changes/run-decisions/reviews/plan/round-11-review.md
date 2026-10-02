verdict: changes_requested

**P7-01**

- **嚴重度**：major
- **位置**：[tasks.md:303](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md:303)
- **問題**：新增的拒絕條件沒有獨立測試，不能確認「4.2 的測試不需改動」。
- **依據**：**事實**：[design.md:242](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:242) 新增「A 是 `resolve_conflict` 時拒絕 attempted」。但計畫與 [wip-test_conflicts.py:263](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/tasks/4.2/attempt-1/wip-test_conflicts.py:263) 只測 C 本身是 `resolve_conflict`；該情況已被原有條件擋下。**推論**：移除 patch 中新增的 A 條件，既有案例仍無法偵測缺陷。
- **建議**：新增具名案例：C 為 `revise`、A 為 `resolve_conflict`，A 指向另一個有效未解衝突。選 attempted 應 exit 1 `choice_not_allowed`，revision、decisions、conflicts 與檔案不變；original／abandon 仍可選。Red 可暫時移除「A 是 resolve_conflict」的拒絕條件，失敗在 `code == 1`；保留原有 C 條件。

**P7-02**

- **嚴重度**：minor，**不阻擋**
- **位置**：[design.md:119](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:119)
- **問題**：新版 D3 將所有 transitions entry 描述為含 `payload`，但本次交付說明仍明定 `create` 不變，兩者尚未一致。
- **依據**：**事實**：[result.json:47](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/tasks/4.2/attempt-1/result.json:47) 說明只有 `commit` 新增 payload；patch 沒有修改 `create`，而 [store.py:221](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/src/loopctl/store.py:221) 的 init entry 仍只有 revision、payload_digest。
- **建議**：保留目前 D3 時，明列 4.2 同步補上 `create` 的 payload；若刻意保留 init 舊形狀，則在 D3 明列例外。不能直接把現有 patch 視為完全符合新版 D3。

其餘確認：

- CLI 擁有範圍與共用順序一致：4.2 處理衝突映射及 `resolves`，5.1 實作 register，6.1 加 policy 視圖，沒有範圍衝突（tasks.md:36、281、316、364）。
- 保存正規化 payload 本身不洩漏 token，也不改變 3.1／4.1 的授權、冪等與提交順序。D5 明定 payload 不含 token、時間；目前 claim 與 decision 的組裝也符合此規則（design.md:215；cli.py:167；decisions.py:65）。
- D6 新限制合理：避免在一次解除中再套用另一筆解除；仍保留 original／abandon。問題在新增行為尚未被測試獨立驗證。

實際核對：指定 diff、design.md、tasks.md、durable-delivery/spec.md、4.2 的 result.json、working-tree.patch、wip-test_conflicts.py、目前 cli.py／store.py／decisions.py、test_state.py／test_decisions.py，以及 D68、D71 與指定 spec-to-plan 規則。全程唯讀，未執行會寫檔的測試。