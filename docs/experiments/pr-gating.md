# Gigaxfer pre-PR gating experiment

狀態：**依 D33 保留為暫緩方案，不是預設下一步**。目前先在 orca-delivery 測通 workflow、orchestrate 與預設工具組合，之後以 cross-node-file-transfer 匯入既有基準、從初始化跑完整流程。下文保留 D15／D16 的舊接入設計；只有使用者另行恢復此方案才重查 Q-TARGET 與原 owner。Controller 尚未實作，本文未啟動 review/fix loop。

## Scope

原 gigaxfer session 繼續完成它正在開發的 feature。到 pre-PR 時，交接固定版本的程式、規格與實作驗證證據；本次實驗從 G1 intake 接入，測 PR 建立/更新、獨立 Codex review、CI、finding/CI 修正、re-review 和 PR Pass／Blocked。

既有 project/feature spec 與 implementation plan 直接引用其適用版本。本實驗不重做原 feature 的研究、設計或初始派工，也不建立先前提議的 orca-delivery status feature。

## Pre-PR 交接：原實作 session 執行

**Trigger：** 使用者指定此 feature 為實驗目標，且原 session 完成初始實作、準備送 PR。交接前維持原工作責任；此文件本身不是對任何未知 terminal 的派工。

1. **固定交付版本。** 記錄 repo、issue、worktree、branch、head SHA、預定 PR base ref/base tip 與 review merge-base；完成相關提交，列出任何尚未提交的內容。Stacked feature 列出上游 PR，不自行改成 main。
2. **列出規格依據。** 提供 project spec、feature spec/issue、design、plan 的可讀取位置和內容版本；列出驗收條件與已確認範圍，不在交接時靜默補大 scope。
3. **交付 G1 證據。** 每項行為變更對應 task/AC、實際 Red snapshot、測試命令/退出碼/log、後續 Green 與 refactor 紀錄；最終驗證與回歸對應交接 head。歷史 Red 可以早於 head。沒有原始證據就記 missing，不能把 plan 的預期輸出或事後編寫的摘要當作已執行的 TDD。
4. **列出限制。** 區分未執行的環境驗收、已知 finding、執行失敗及需要人的決策。將真正無法驗證的必要條件交回 gate policy，不自行列為 nonblocking。
5. **明確交接下一步。** 回報「pre-PR ready」及以上資料，原 session 等待 gating 結果。接手方確認 intake 後，只有一個外層 loop 指派 PR review／fix。既有 SDD、patrol 或 finishing workflow 不應同時另派最終 reviewer 或修正。

**完成條件：** 可辨識的 issue/session、固定的 code/spec 版本、可讀取 evidence 和實作責任人均已交接。`pre-PR ready` 是接入通知，不是 G1 或 PR Pass 的結論。

**Blocked：** 缺版本、缺測試證據、仍有相關修改未提交、base 不明或驗收歧義時，保留成果並列出需補項目，等待補齊；不重做整個 feature。

## Gating loop：接手方執行

1. 讀取交接資料與外部實況，以 JSON 保存 run/versions/ownership。驗證 G1；缺資料記 missing/blocked，先要求可驗證補件。重跑目前測試能證明當前 Green，不能自行證明歷史 test-first 過程。
2. G1 通過後建立或接續同一 feature PR，固定 head/base。新 Reviewer 必須與原實作者隔離，由 controller 派獨立 session，符合既有獨立 Codex review 要求，使用完整 spec/design/diff package。依 D30，契約與底層實作解耦；Codex 指 runtime 或 model 及本次具體 adapter 仍需在試用前選定並驗證，不由本文件默認選擇。
3. Review 與真正 GitHub CI 並行；先保存結構化結果，再發布/通知。CI 用 API/CLI 讀取必要 checks，agent 的 console 結語不是 CI 證據。
4. 收齊同版本結果後形成一次修正批次。優先派回已確認的原實作 owner；若 owner 不可接續，先確認舊執行權已解除，才派替代 worker。Controller 與 Reviewer Agent 不直接修改作者 branch。
5. 修正產生新 head 後重新跑 G1、必要 CI 和獨立覆核。Finding 保留 ID，實作者提交 fix/evidence；reviewer 驗證後才解除阻擋，爭議交人裁決。
6. Pass 前再次核對 PR head/base 及適用規格版本；三 gates 都適用且通過才記錄 PR Pass。發布失敗保留結果只重試發布，仍需完成原 issue 的可讀取 review 紀錄。

限制沿用 D13：主動執行最多 4h、最多 3 輪修正、每項 infra 操作額外重試 2 次。Phase 1 停在 PR Pass／Blocked；不自動 merge、close、release 或 deploy。

## 可觀察的實驗成功條件

- 真實 feature 的 G1、獨立 review、GitHub CI 均有可讀取且版本適用的證據。
- 至少一次成立的 review finding → fix → re-review；保留穩定 finding ID 與兩版 head 的對應。
- 依 D24，本機 JSON finding registry 為權威；PR 保存完整 review，原 issue 保存可採取行動的摘要與連結，兩者可對回同一結果與版本。
- 保存 JSON 狀態與證據後可 resume；至少驗證一次遺失通知或重啟不重派、不重貼。
- 若未找到真實 blocking finding，如實報 review clean，不虛構問題來宣稱循環驗收完成。

先以可控 adapters 驗證 stale SHA、缺 check、crash、重複事件與發文失敗；這些測試和真實 feature 的 demo 證據分開保存。

## 已查核的候選；尚待使用者選定

2026-09-26 唯讀查核到 P03 / [issue #12](https://github.com/yschiang/cross-dc-xfer/issues/12)，branch `p03-ingest`，worktree `/Users/johnson.chiang/workspace/gigaxfer/.worktrees/p03-ingest`。

- 查核時 head `8839a95022fa0ea3632b5f2a34089779260eabe7`，另有未提交的 scanner/NAS/test 變更；這是觀察快照，不是可送審 head。
- 當時尚無 P03 open PR；[PR #11](https://github.com/yschiang/cross-dc-xfer/pull/11) 仍 open，issue #12 明列以它作 stacked base。
- Plan：`docs/superpowers/plans/P03-ingest.md`。Task 8 預計產出 `docs/validation/P03-validation.md`；本次讀取尚未見該檔案。Plan 內預期測試數及草稿副本驗證不能替代本次提交的實際證據。
- `.github/workflows/ci.yml` 定義 `CI` workflow、`test` job，以 Temurin 21 跑 `mvn -B -ntp verify`。真正 required check 的識別與結果須在交接時重新查核。
- 使用本機可執行的 `/opt/homebrew/bin/git`；既有 plan 已記錄 Java/PATH 前置條件。驗證時依現況讀取，不能直接沿用其他 feature 的 logs。

目前只做唯讀查核，未向該 session 送指令、未改它的檔案、未建立 PR、未接管其派工。
