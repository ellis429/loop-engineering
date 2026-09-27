# Proposal

## Why

使用者目前需人工搬運 agent context、追 findings 與 CI，且 agent 完成訊息不能證明最新 PR 可驗收。需要一個可恢復的 delivery controller，將已確認的三 gates、版本與人工邊界落成可交接的單一 feature 流程。

本文件是 **比較草稿，未採用、未批准開工**。既有 D01–D30 政策照常有效；此處將其轉成 specification，並明標設計文件的具體化提案，不代表新的 D11 確認。

## What Changes

- 提供 project/feature 共用 `orchestrate` 入口；薄 project 層保留 baseline、feature references、人工接受、相依啟動與 Retro 候選。單一 feature 綁定一個 repo、issue、PR，由唯一 controller 執行派工與狀態規則。
- 支援新 feature，以及保留原成果的 pre-PR adopt：核對 owner、版本、plan 確認與歷史證據後，從真正缺少的階段續行。
- G1 保留歷史 Red lineage 與當前整合 Green，G2 使用獨立 Reviewer，G3 查核必要 CI；三 gates 都適用目前版本才可 PR Pass。
- 持久化 stable findings、correction batches、一次爭議覆核、人工裁決與發布作業，執行有界 finding → fix → re-review。完整 review 發 PR，原 issue 發摘要與連結。
- 以人可閱讀的 JSON/YAML 設定及狀態提供 ownership、結果去重、外部 unknown、crash/reconcile 與預算恢復；runtime/model 透過 adapter 與設定接入。
- 將 AC、驗法、實際證據和原生文件位置／版本連結；OpenSpec 承接 spec/design/tasks，Writing Plans 方法銜接 tasks，Superpowers TDD 管實作，自有 controller 保有唯一外層 loop。

本次只建立 proposal 與 specs。Design/tasks、產品程式、部署、真實 trial 不在本輪；本 MVP 終點為 PR Pass／Blocked，不自動 merge、close、release 或 deploy。Dashboard、多 repo swarm、完整 roadmap 平台及 CIT 不在範圍內。D18 PR trial 暫停、D22 P03 Retro 未開始，Q-TARGET 未答，這份文件不觸發接管。

## Capabilities

### New Capabilities

- `delivery-orchestration`: 共用入口、角色與人工授權、版本化交接、新 feature/adopt，以及薄 project 的接受／依賴／Retro。
- `delivery-gates`: 可驗證 G1/G2/G3、TDD N/A、版本失效與 PR Pass 證據。
- `finding-resolution`: Finding authority、blocking/closure、合併修正、一次爭議覆核、人工退回及 review 發布。
- `durable-delivery`: 人可讀狀態、唯一 ownership、assignment/result、crash/reconcile、outbox、預算與 adapter 邊界。

### Modified Capabilities

無。本次隔離 planning root 的 `openspec list --specs` 回傳無既有 specs；本草稿以共同 baseline 文件作來源，不聲稱已修改正式 repo 的規格。

## Impact

目標為既有獨立 repo `/Users/johnson.chiang/workspace/orca-delivery`；預期影響其未來的 orchestrate skill、controller、檔案 store、Orca/Git/GitHub/CI adapters 及操作文件；目前沒有被本 change 修改的 production code 或已存在 API。實際語言、產品命令、檔案布局與 API schema 將留給 design/tasks；下列 `start/adopt/status/resume/decision` 表示操作意圖，並非已選定 CLI。

Spec scenarios 是驗收條件，沒有執行結果。建議日後由公開 controller 操作搭配可控制的 fake agent/GitHub/CI adapters 驗核心與故障，再獨立留存真實 adapter/E2E 證據；**此測試 seam 尚待確認**。Runtime/model、G2 Codex 的具體定義、repo-specific required checks、timeout/active-time 算法與能力缺口均未定案。完整規劃完成後仍須對具體 design+plan 作 D11 一次開工確認。
