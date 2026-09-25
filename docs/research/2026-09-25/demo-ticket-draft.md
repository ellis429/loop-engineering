# Draft feature ticket: CLI 查詢 delivery run 狀態

狀態：已被 D15/D16 取代，僅保留歷史提案；使用者選擇另一個 gigaxfer session 的現有 feature，在 pre-PR 驗證 gating loop。本草稿未發布，沒有建立 GitHub repo 或 issue，亦不作為目前實驗的待辦。現行方案見 [PR gating experiment](../../experiments/pr-gating.md)。

## Problem

控制器可能在 review、CI、發文重試或人工 Blocked 階段等待。使用者需要從 Orca terminal 查明目前進度與下一步，不能只看某個 agent 最後一句「完成」。

## Proposed behavior

使用 `orca-delivery status <run-id>` 讀取指定 run，顯示 phase、issue/PR、評估的 head/base、三 gates、review/correction 輪次、活動 worker 與 Blocked 原因。`--json` 提供 versioned machine-readable 輸出。

## Acceptance criteria

| ID | 情境 | 預期行為 |
| --- | --- | --- |
| STATUS-01 | 已存在且執行中的 run | 顯示目前 phase、選定 issue/PR 及已知版本；尚未建立 PR 時明確顯示未建立 |
| STATUS-02 | 部分 gates 完成 | 分別顯示 G1/G2/G3 的状态與原因；不得以 agent completed 代替 passed |
| STATUS-03 | Run Blocked | 顯示原因、相關 evidence 位置及需要人的決策；既有結果仍可查 |
| STATUS-04 | Gate 證據已過期或外部狀態久未查詢 | 顯示過期/未知及 last observed 時間；歷史 Pass 不能被呈現為已確認的目前 Pass |
| STATUS-05 | `--json` | 輸出 parseable JSON、schema version、同一份 run snapshot；成功讀取回 exit 0，不能因 feature 尚未 Pass 就當查詢失敗 |
| STATUS-06 | Run ID 不存在或儲存讀取失敗 | 明確 error 與非零 exit code；不建立新 run、不觸發 dispatch/發文 |
| STATUS-07 | 查詢正在被 controller 更新的 store | 取得一致的 committed snapshot；不讀到半個 gate update、不阻止 controller 後續推進 |

## Scope

一個獨立 feature PR，涵蓋 CLI、唯讀 snapshot/query 介面、格式化、行為測試與操作說明。以已完成的 controller store/contracts 為基礎。文字輸出與 JSON 來自同一 snapshot。

本 feature 不加入 dashboard、merge、release 或 deploy；不把 `status` 命令變成另一個 reconcile/dispatch loop。控制器基礎必須先存在；這張 ticket 不承擔整個 orchestrator 的實作。

## Dependencies and validation

- 依賴已驗證的 run persistence、gate status/reason 契約及最小 CLI 入口。
- 在獨立 branch 以 TDD 實作，整合後跑完整相關回歸；由另一個 Codex reviewer 對照 project + feature specs 及完整 PR diff 審查。
- 必要 GitHub CI 預計包含測試、lint 與 type check；具體 check 名稱及命令隨 controller design 固定。
- Demo controller 從已完成基礎的固定版本執行；feature workspace 的修改不影響執行中的 controller。
- 真實 demo 需保留 review finding → fix → re-review 的完整證據。若 reviewer 沒有發現可成立的 blocking finding，應如實記錄 clean；不能虛構 finding 來宣稱 A13 完成。

## Publication preview

建議 repo：`yschiang/orca-delivery`，private。唯讀查詢目前沒有取得此 repo（`gh repo view` 回無法 resolve），尚未建立或設定 remote。建議 issue title：`Feature: inspect delivery run status, gates, and blocked decisions`。

此發布提案未被選用；目前不建立這個 repo／issue。
