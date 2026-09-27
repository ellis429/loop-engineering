# Proposal

> **2026-09-27：proposal 收斂方向已確認（D45）**。第一條實作路徑採 Herdr 原生功能＋orchestrate＋薄 controller。Specs／design／tasks／validation 尚待對齊、獨立審查及 D11 開工確認；本次確認不是產品實作授權。舊 D40 approval 與 S1 review 證據保留，不作本輪批准或通過證明。

## Why

使用者目前要在 agents 間搬運規格、追蹤 findings 與 CI，再判斷 PR 是否可驗收。需要可追溯、會核對證據的 delivery loop，讓人集中處理需求取捨、設計確認與最終接受。

既有 S1 同時承擔流程編排與通用執行平台，已超出第一個可驗證切片。依 D41–D45，收斂為方法 skills 引導 agent 協調工作、既有 runtime 執行、薄 controller 保存狀態並確定性判斷品質；降低自建平台責任，保留交付與品質契約。

## What Changes

- 一個 orchestrate 入口涵蓋 Project／Feature 兩層。Project Lead 透過 research、SA、domain modeling、grill 與 high-level design 形成 project baseline、roadmap／milestones、feature spec／AC；Implementer 承接 detailed design、最終 plan／tasks、TDD 與修正；Reviewer 獨立審查及覆核，不修改被審 branch。角色的決策權依授權與交接，不綁 runtime 父子關係。SA 仍依 [階段契約](../../../docs/workflow/project-lead-sa.md)。
- Orchestrate 是同一 feature 的唯一外層協調循環：載入適用 skills、向 controller 取得允許動作、透過工具派工、收回及提交結果，推進正常 review／fix loop。沿用 skills 的原生 artifacts 與呼叫限制，以版本化引用維持唯一規格及 plan／tasks 權威。
- Controller 是 orchestrate 可呼叫的確定性程式：保存 JSON／YAML 可讀狀態、驗證 assignment／result 身份與版本、管理 findings、核對證據適用性、計算三 gates、執行輪次／預算檢查並回傳下一步。每次呼叫完成核對／狀態更新後返回，不另起持續運作的 agent supervisor。
- 第一條實作路徑使用 Herdr 原生 sessions／panes／worktree 能力，不引入另一套 orchestrator 外層循環。本機 OpenAI 經 Herdr → OpenCode → ChatGPT OAuth；Claude 經 Herdr → Claude Code → Claude 帳號。Provider／model／runtime 分別記錄；公司 OpenCode-only 路徑及 Orca 等選配接入仍保留，按環境另驗，不宣稱本機 probe 已覆蓋它們。
- 第一個可驗證切片為單一本機、單 repo、單一 feature／PR、依序實作與獨立 reviewer。新 feature 與既有 pre-PR adopt 保留為交付需求；具體切片須明列覆蓋範圍及原 owner 交接，不把尚未驗證的入口標成完成。
- 保留 G1 實作／TDD、G2 獨立 review、G3 必要 GitHub CI。G1 先於送審，G2／G3 可並行。歷史 Red 必須追溯同一 task／修正，最終 Green／回歸適用整合後 head；所有判定核對最新 head、review base 與適用文件／政策版本。缺項、未知、過期或 agent 自述完成均不能放行。
- 保留穩定 finding registry、reviewer 覆核或人工裁決、有界修正、一次爭議覆核及反覆 finding 升級。先保存結果，再發布 GitHub review／issue 摘要及通知；通知只用來喚醒，重複事件不得重複派工／發文，發布失敗保留結果並單獨處理發布。
- 保存單一 writer、待處理操作／結果身份與必要去重；重啟後核對外部實況。使用既有 runtime／工具能力，不自建通用 OS sandbox、credential broker、分散式 ownership 或全面自動恢復平台。執行結果、ownership 或外部寫入是否成功無法核對時，保存現況並 Blocked，由人接手，不盲目重試。既有 AC 的責任移交與承諾差異須逐項審查。
- 薄 project 層保存 baseline／feature refs、人工接受、相依啟動與 Retro 候選。多人交接、保留 worktrees 與 multiple PR stacked gating 維持完整成品目標；stack 政策及真實多人驗證方式仍待決，不擴張第一切片為跨主機平台。
- 驗證順序為 H0 能力 probe → H1 核心與假 adapter 負例 → H2 本 repo 真實 issue／TDD／review finding／fix／re-review／CI／PR Pass → H3 cross-node-file-transfer 的 Project 到多個 Feature 示範。每階段分開保存證據；沿用 example 的適用產品基準，新程式產生自己的交付歷程。

終點為 PR Pass／Ready for human acceptance 或附原因及證據的 Blocked；沒有自動 merge、close issue、release 或 deploy。CIT 依 D29 暫不處理。舊 gigaxfer PR／P03 試用維持暫緩，本次不接管 gigaxfer 或初始化 example。

## Capabilities

### New Capabilities

- `delivery-orchestration`: Project／Feature 入口、角色及原生 artifact 交接、人工授權、新 feature／adopt、接受／相依啟動與 Retro；orchestrate 呼叫 controller 及執行工具的責任邊界。
- `delivery-gates`: G1／G2／G3、TDD 與非行為例外、版本失效、AC 驗證對照與真實交付證據。
- `finding-resolution`: Finding authority、blocking／closure、批次修正、爭議覆核、反覆 finding、人工退回及 review 發布。
- `durable-delivery`: 可讀持久化、單一 writer、assignment／result／operation 身份、去重、外部實況核對、有界執行與 Blocked／人工接手；runtime 工具接合及其能力邊界。

### Modified Capabilities

無。2026-09-27 執行 `openspec list --specs` 未列出既有 capability；上述四項仍為此未歸檔 change 的新增 capabilities。

## Impact

Repo 已有舊 S1 的 `src/delivery/`、`tests/`、PR #2、CI／review 及停止 checkpoint；不是從零開始的空 repo。舊程式保留作重用評估，先對照新契約及未解 findings，再以測試證明適用性；不直接續跑舊 S1→S2→S3。17 項 blocking findings 不因縮 scope 自動關閉，移除機制亦須留下適用性依據。

受影響成果包含薄 controller 與窄工具接合、orchestrate skill／references、設定範例、操作說明、測試與 demo 證據。正式 specs／design／tasks 及 [validation](../../../docs/validation/implement-delivery-loop.md) 需依 [範圍對照](../../../docs/harness/scope-reconciliation.md) 對齊 88 個既有 AC 與 17 項 findings，區分保留、移交、替換及需人工裁決；不能把舊勾選任務或測試搬作新切片通過證明。

[H0 紀錄](../../../docs/research/2026-09-27/herdr-setup.md) 已包含 Herdr 基礎操作、Luna 經 OpenCode 與 Sonnet 5 經 Claude Code 的小型交接；它不證明正式 skills profile、Reviewer 權限、全部 timeout／隔離承諾或完整 E2E 已完成。正式 controller 工作仍由 Opus 5.5 承接詳細設計／plan／實作，GPT／Codex 獨立審查；廉價模型 probe 不改變此分工。

接續形成 spec 差異、design、tasks 與 AC → 驗法／環境／通過標準／證據對照，完成獨立文件審查及 D11 確認後才派產品實作。四小時 active 的執行承諾、runtime／證據信任邊界與 required CI policy 等尚待具體設計及必要裁決；OpenSpec 結構驗證不替代這些確認或產品 gates。
