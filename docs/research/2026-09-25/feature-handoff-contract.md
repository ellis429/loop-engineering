# Feature 交接契約：欄位草案

狀態：依已確認的 project / feature / task 層級整理。語意已確認，以下欄位命名與表示法是待 design 採用的草案；不是新建 ticket、OpenSpec change 或另一份權威需求。

## 層級與權威來源

| 層級 | 定義 | 交接方式 |
| --- | --- | --- |
| Project spec | 共用行為契約、全域限制、跨功能保證 | 可讀取且固定版本的文件集合 |
| Feature spec | 本次交付行為、範圍、驗收條件、依賴、需求增量 | Feature issue 本文或它明確引用的規格 |
| Feature design | 滿足需求的責任邊界、介面、狀態與故障處理 | 引用上述兩層規格的設計 |
| Implementation plan | 可派工 tasks、依賴、scope、測試與完成條件 | 一份權威 plan；不複製維護同義 tasks |
| Feature PR | 整合後可驗收的交付變更 | 多個 task 可以共同交付一個 PR，三 gates 對此 PR 評估 |

Issue 本文足以描述需求時即可作為 feature spec。OpenSpec change 的 delta 則必須連同 baseline 讀取。Project spec 和 feature spec 不相容時需人工裁決並明確更新契約；不採「較新的文件自動優先」規則。

## Feature ticket 應交接的內容

1. **交付能力**：使用者或其他系統會得到什麼可觀察的能力。
2. **規格依據**：適用的 project requirement IDs、feature spec 位置、版本與已確認決策。
3. **範圍與排除項**：本次 PR 的完成邊界。
4. **行為與驗收條件**：正常、故障、重試、恢復等適用情境；每項有穩定 AC ID。
5. **依賴**：哪些已完成交付或版本是開工／整合前提，與僅相關的工作分清。
6. **尚待裁決事項**：會影響 scope、外部行為、相容性或驗收的歧義不可藏進假設。
7. **Design / plan 連結**：在接票與設計階段補齊，維持與 feature spec 相符。

程式檔案清單、測試命令、task scope 與派工依賴放在 plan；ticket 連回 plan。這些實作資料不替代 AC。

## 示意：控制器重啟後接續同一交付 run

以下只用於說明粒度，尚未選為 demo feature，也沒有發布 issue。

**Project 契約**：狀態持久化；通知只用來喚醒；版本過期不可 Pass；不能重複派工或發文。

**Feature 行為**：控制器重新啟動後能恢復未完成 run，核對外部實況，接續必要工作。

| AC | 情境 | 可觀察結果 |
| --- | --- | --- |
| RESUME-01 | 控制器退出時 worker 仍執行中 | 重啟後辨識原 task/attempt/dispatch，保留執行權，不啟動競爭的實作者 |
| RESUME-02 | Worker 已保存結果，但喚醒遺失 | Reconcile 找到並驗證結果；該結果只匯入一次 |
| RESUME-03 | Review 已完成，GitHub 發布失敗 | 恢復待發布紀錄，只重試發布並讀回驗證，不重做 review |
| RESUME-04 | 停機期間 PR head 或適用規格改變 | 保留歷史證據，將受影響 gate 視為過期，不能沿用舊結論 Pass |
| RESUME-05 | Orca 暫時無法查詢 worker | 顯示實況未知，保留原 attempt；不能把連線錯誤推論成 worker 已終止並重派 |

可能的 implementation tasks 會涵蓋儲存、reconcile、adapter 與故障測試，仍共同服務上述 feature PR。具體 task 切分須由正式 design/plan 決定。

## 送審資料關係

- Review package 固定 project spec、feature spec、design、plan 的適用版本，以及 PR base/head。
- Implementation task 的測試證據對應 task ID 和 feature AC；歷史 Red snapshot 可早於最終 head，但 lineage 要能查驗。
- 最終 Green / regression、review verdict 與 CI 必須適用整合後的目前版本。
- Reviewer 檢查每項 feature AC 及適用 project 契約；未驗必要 AC 的政策待 grill，不可先假設為 nonblocking。
- Spec 更新後保存新版本與裁決，評估並失效相關 gate；不能只更新連結文字而繼續沿用舊 review。
