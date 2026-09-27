# 人可讀的檔案狀態

> 文件定位（2026-09-27）：早期設計推導，保留供查閱。閱讀入口及現行文件狀態見 [文件導覽](../../README.md)；搬移不撤銷已確認決策，也不構成開工授權。

> **2026-09-27 範圍更新（D41／D42）**：已確認改為 orchestrate 呼叫薄 controller，完整成品包含多人 Project／Feature 流程及 cross-node-file-transfer 多 feature 示範。見 [Project intent](../../project-intent.md)。本文涉及 controller 自動派工、全面恢復及平台責任的舊設計待逐項對照，不能直接據此續派；三 gates、證據／版本及 finding 覆核仍保留。

日期：2026-09-26。已確認 D14：使用 JSON／YAML 檔案作 MVP 持久化，讓人能直接讀取。以下為格式分工與恢復機制的設計提案，尚未實作。

## 格式與布局

```text
workflow.yaml                    # 人維護的流程、gate 與限制設定
.delivery/project.json           # Project binding、roadmap refs、feature run 指標、人工接受紀錄
.delivery/runs/<run-id>/
  run.json                       # 目前進度、tasks、gates、findings、待執行操作
  events.jsonl                   # 每行一個事件，包含時間、原因與版本
  assignments/<attempt-id>.json   # 固定版本的派工輸入
  results/<attempt-id>.json       # Worker／adapter 保存的結構化結果
  evidence/                      # 測試 logs、review 報告與版本證據
  receipts/                      # Runtime（Orca／OpenCode 等）與 GitHub 操作回執
```

YAML 適合人工維護設定與註解；run、assignment、result 使用有縮排的 UTF-8 JSON，固定欄位命名，讓人和程式都能讀。JSONL 是歷史紀錄，每行獨立可解析；當前狀態不需要人重讀整份 history 才能了解。

`run.json` 保存同一 run 的完整可變狀態，包含待發文項目及已匯入 result IDs。Results、receipts、evidence 以固定 ID/digest 引用，避免把大量 logs 塞進狀態檔。依 D24，`run.json` 內的 finding registry 是唯一權威狀態；GitHub 為發布與討論介面，其回饋由 controller 核對來源與 D09 closure 權限後匯入。

設定可由人編輯；controller 載入後驗證 schema 並記錄設定版本。人工裁決應透過有驗證的操作保存理由與來源，而非手改 gate 為 passed。這不影響直接閱讀、搜尋與比較 JSON 的用途。

## 最小一致性策略

1. 啟動時以 repo + feature identity 鎖防止同一 feature 被兩個 run IDs 控制，並取得 worktree writer lease；長任務持 run lock 更新 `run.json`。Project registry lock 只涵蓋登記／交接。Workers 只交自己的 result/evidence，不能直接改 controller 狀態。
2. 同一次邏輯變更，例如「匯入 review、加入 findings、建立待處理操作」，在記憶體產生完整下一版 snapshot，增加 revision。
3. 將 snapshot 寫到同目錄暫存檔，驗證完整內容、flush/fsync 後原子 rename/replace，再同步目錄。實作時需對支援的平台驗證持久性行為。讀者看到完整舊版或完整新版，不會讀到寫一半的 JSON。
4. 結果、logs 與 receipts 先完成保存，再讓 snapshot 引用它們。Crash 留下的未引用檔案不會自行變成已接受證據。
5. 發出派工或 GitHub 寫入前，先將 operation ID、內容與 pending 狀態保存到 snapshot。回應遺失時查原操作實況，不能直接再做一次。

跨檔恢復先 reconcile run，再更新 project 指標。Project 只引用 run ID/revision，feature gates 的現行判定仍在 run snapshot，不要求兩份 snapshot 原子提交。MVP 不把 tasks、gates、findings 各自拆成可獨立更新的權威檔案，因此不需要模擬任意多檔案 transaction。

## Event history 與 crash recovery

`run.json` 是 controller 的恢復依據；`events.jsonl` 是稽核紀錄，不另有一份可互相競爭的現行狀態。

建議在 snapshot 內包含尚未確認寫入 history 的事件，每個事件有穩定 ID 與 revision。先提交 snapshot，再將其中事件追加到 JSONL 並同步；確認保存後，在下一版 snapshot 清除已寫入的 pending history 項目。

- 若 crash 發生在 snapshot 更新前，原 snapshot 仍有效；尚未登記的外部操作不得已經發出。
- 若 snapshot 已更新但 history 未寫完，resume 從 pending history 補寫；遇到已存在的相同 event ID 不重複追加。
- 若 JSONL 最後一筆因中斷只寫一半，保留損壞 bytes 的診斷副本，在鎖內移除未完成尾筆，再從 pending history 恢復；中段損壞或同 ID 內容衝突則 Blocked。
- 若 result 已存在但尚未匯入，reconcile 核對 assignment、SHA 與 evidence 後匯入一次。
- 若 API 結果 unknown，保存原 operation 並查外部實況；檔案格式本身不提供 GitHub 或 agent runtime 的 exactly-once 保證。
- 若 `run.json` 不存在、無法解析或 schema 不相容，resume 明確報錯／Blocked，不覆寫成新的空 run。

本機預設檔案系統是第一個驗證範圍；共享網路磁碟的 lock、rename 與 durability 語意需另外驗證，不能直接宣稱支援多主機 writers。

## 驗收重點

正式 plan 將為同時啟動兩個 controller、snapshot replace 前後 crash、snapshot/history 間 crash、JSONL 尾筆中斷、重複 result、corrupt state、未知外部操作等情境提供可重現測試。可讀性也要驗收：打開 `run.json` 即可找到當前階段、三 gates 的理由、Blocker、版本與下一個 action。
