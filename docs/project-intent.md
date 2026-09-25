# Orca Delivery：Project intent

日期：2026-09-25。來源：使用者 agent handoff 及後續已確認決策。本文是已知需求基線，正式規格由 OpenSpec artifacts 承接。

## Problem

目前人需要在 Claude Code 與 Codex agents 之間搬運 context、追蹤 review、通知實作者修正，再核對 CI 與 review 是否適用最新變更。Agent 的完成訊息不足以證明交付可驗收。

## Outcome

使用者從 Orca 選擇含有或引用 feature spec 的 GitHub issue。系統協助研究與設計、產生可派工 plan、執行 TDD、整合 PR、獨立審查並查核 CI，再以 review/fix loop 推進到 PR Pass，或帶證據轉交人裁決。

Project spec 定義共用契約，feature spec 定義該交付的範圍與驗收。Feature ticket 可直接承擔 feature spec；每個可獨立驗收 feature 對應一個 PR，tasks 為派工單位。

## Confirmed constraints

1. G1 先通過才送審。G2 獨立 review 與 G3 CI 可並行，任一不通過都不可 PR Pass。
2. Gate 判定讀取結構化結果及實際證據，不能依 agent 自述、終端閒置、通知或 task completed 判定。
3. 結論綁定 PR head、review base、project / feature specs、design 與適用 plan 版本；變更時評估相關失效。
4. Red 來自歷史 snapshot，可早於最終 head，但需追溯到同一 task / 修正；最終 Green 與 regression 適用整合後 head。
5. Missing/pending/cancelled/timed-out/unknown/stale 不能當 success；skipped/neutral 必須有明確政策。
6. Findings 保留穩定 identity、來源、severity/blocking、位置、依據、預期行為、狀態、fix commit 與覆核證據。實作者無權自行解除 reviewer 阻擋。
7. 先保存結果，再發布與通知。Reconcile 可在通知遺失後找回成果；重複事件不重複派工／發文。GitHub 發布失敗只重試發布。
8. 正常情況收齊同版本 review / CI 後合併成一個修正批次；stuck work 有 timeout 與有界 recovery。
9. 狀態持久化，重啟後核對外部實況再接續；Orca 不可查詢時不能推論 worker 已停止並派出競爭實作者。
10. 並行修改使用隔離 worktrees，依賴工作依序整合；review 與 CI 針對最終整合 PR。Reviewer 不修改被審查 branch。
11. Skills 不擁有 feature gate 或外層 dispatch loop。沿用現有方法並以薄封裝統一契約，保留已安裝版本的呼叫限制。
12. MVP 使用既有 Orca 與 GitHub，不建立新 dashboard；交付終點 PR Pass，不包含 merge、close issue、release 或 deploy。
13. 每個 feature 在 design+plan 完成後開工前由使用者確認一次；後续 scope/spec/AC 變更、設計缺陷或阻擋爭議回到使用者。
14. 違反 spec/AC、可證明的正確性/安全缺陷、必要驗證缺失屬 blocking；風格偏好不阻擋。實作依序，review 與 CI 並行；每個 run 主動執行最多 4 小時、最多 3 輪 correction、每項 infra 操作最多額外重試 2 次，到限轉 Blocked。

## Environment and chosen integration

獨立 repo，使用 OpenSpec；Orca lead agent 協助判斷，單一持久化 controller 決定狀態與派工，Orca supervised workers 執行 tasks。控制器先從專用 Orca terminal 啟動。

本機已查核 Stably Orca 1.4.209、Claude Code 2.1.282、Codex CLI 0.153.4、GitHub CLI 權限與 skills。細節與未驗證能力見 [research](research/2026-09-25/research.md)。

## Acceptance scenarios

| ID | 情境 | 必須觀察到的行為 |
| --- | --- | --- |
| A01 | 正常 feature | Issue → design/plan → TDD → PR → review/CI → Pass，全程有版本化證據 |
| A02 | Blocking finding | 派修、更新 PR、重新驗證及 review，由覆核解除阻擋 |
| A03 | Review clean、CI fail | 不可 Pass，修正後查核最新版本 |
| A04 | CI green、review fail | 不可 Pass，CI 不取代 review |
| A05 | 自述 TDD 完成但缺證據 | G1 不通過，指出需補的可驗證資料 |
| A06 | 舊 SHA 晚到或 Pass 前 push | 舊结果不能放行，刷新版本並失效相關 gates |
| A07 | Missing/pending/cancelled check | 不誤判 CI clean，保存原因 |
| A08 | 重複事件或遺失通知 | 不重複派工/發文，reconcile 可恢復進度 |
| A09 | Agent crash 或 controller restart | 讀持久化狀態、核對外部實況再 resume 或安全重派 |
| A10 | 上限或爭議 | Blocked，附原因、證據與需要人的決策 |
| A11 | GitHub 發布失敗 | 保留結果，可重試發布，不重做 review、不假裝已發布 |
| A12 | Reviewer 與作者隔離 | Reviewer 可檢查與驗證，不能修改 author branch 或自行關閉品質 gate |
| A13 | 真實端到端展示 | 至少一次真實 review finding → fix → re-review，並證明最新 PR 的三 gates |

## Open decisions

TDD 粒度／例外、finding authority／發布呈現與真實 demo target 尚待本輪 grill；timeout 等詳細預設會隨 design 提交。見 [decisions](decisions.md)。
