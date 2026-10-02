verdict: clean

計畫層級已處理 T4.2-01、T4.2-02，未發現新問題。

- **兩個失敗情境**：同一 identity 只保留一個未解衝突，解除後的新衝突使用當下接受的 C；歷次被否決的內容回 exit 1，避免把已解除的 cid 當成 blocker。[design.md:226](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:226)、[design.md:241](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md:241)
- **順序一致**：依 D4，先處理 duplicate、歷次否決，再套用 D6 的單一未解衝突規則；第 4 步的 Blocked／`resolves` 判定不變。
- **後續介面**：5.1、6.1 的撤銷、重新核對與效果清除契約不受影響。

| 新增測試 | Red 判定 |
| --- | --- |
| `test_one_open_conflict_per_decision_and_fresh_content_after_resolution` | 可達。現行實作會建立第二個衝突，使 `len(conflicts) == 1` 得到實際值 2 而失敗。 |
| `test_every_transition_keeps_its_committed_payload` | 已核對 attempt-2 原始證據：確實在 init payload 的比較斷言失敗，實際值為 `None`。本次是補列既存測試。 |

核對過指定 diff、design.md、tasks.md、durable-delivery/spec.md、review-1/result.json、store.py、decisions.py、test_conflicts.py，以及 payload 測試的 Red／Green 紀錄。全程唯讀，未重跑會寫檔的測試。