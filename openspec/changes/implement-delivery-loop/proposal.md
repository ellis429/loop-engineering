# Proposal

## Why

使用者目前要自行在 agents 間搬運規格、追蹤 findings 與 CI，再判斷目前 PR 是否可驗收。需要一個可恢復、會核對證據的 delivery loop，讓人集中處理需求取捨、設計確認與最終接受。

本 change 將既有決策與設計具體化為正式規劃文件，包含 D32 的分析／設計分工、D34 的 Research＋SA 階段契約與 D37／D38 的 OpenCode 預設接入、runtime／model 分離及其他入口選配；D31 的 authoring／planning 組合已重新開放評估，不作固定工具要求；**D40 已核准 v3 design／tasks／validation 與三個切片；目前準備 S1 實作**。驗證對照沿用 D19 的 AC → 驗法 → 通過標準 → 預期／實際證據要求，已在 `docs/validation/implement-delivery-loop.md` 具體化；使用者對對照方法的「Ok」不視為尚未提出之技術設計已獲批准。

## What Changes

- 一個 orchestrate 入口涵蓋 project 與 feature 範圍；Project Lead 負責專案協調、Implementer 負責功能交付，委派權依使用者授權，runtime 不綁固定父子關係；唯一 controller 依核准 plan 派工。
- Project Lead 以 research、SA、domain modeling、grill 與 high-level design 形成 project baseline、roadmap／milestones 並拆 features；單一 feature 再聚焦分析並準備 spec／AC 與設計邊界。Implementer 承接 detailed design、校準並維護最終 plan／tasks；Project Lead 可提任務草案，不直接當成已核准 assignment。
- Project／Feature SA 共用七項需求內容與漸進互動，深度依層級調整；保存可進入 Design 的判斷、適用使用者確認與交接來源，不取代 D11 開工確認。完整方法見 [SA 階段契約](../../../docs/project-lead-sa.md)。
- 單 repo、已選定 issue、單一 feature PR；支援從頭執行及既有 pre-PR adopt，保留成果與原 owner 交接。
- 以 Superpowers TDD 證據、獨立 Codex review、必要 GitHub CI 三 gates 判定適用版本的 PR Pass。
- 穩定 finding registry、有界修正／一次爭議覆核、反覆 finding 的提前升級與人工裁決。
- JSON/YAML 可讀狀態、單 writer、outbox、reconcile、重啟恢復與去重；runtime/model 經 adapter 接入。OpenCode 是預設 agent runtime，可依角色選用 OpenAI／Claude models。Orca、Codex／ChatGPT 相關入口及 Claude Code 為選配；直接派工、回收、管理工作區與 resume 不依賴這些選配工具，亦不因此放寬 G2 的獨立性與模型核准政策。
- 薄 project 層保存 baseline/feature refs、人工接受、相依啟動與 Retro 候選，不擴張成新 dashboard 或完整專案管理平台。
- Design／plan 已將規格內的 AC 逐項映射到驗法、環境、判定標準與證據位置；目前尚未執行，實作後回填實際適用版本。

終點為 PR Pass／Ready for human acceptance 或附原因的 Blocked。沒有自動 merge、close issue、release、deploy；CIT 依 D29 暫不處理。依 D33，先在 orca-delivery 測通 workflow、orchestrate 與預設工具組合，再啟動 cross-node-file-transfer，匯入適用的既有產品基準並驗完整交付。D18 的舊 PR trial 保留暫緩，Q-TARGET 非目前前置；D22 P03 Retro 仍等使用者開始，本輪不接管 gigaxfer 或初始化新 repo。

## Capabilities

### New Capabilities

- `delivery-orchestration`: 入口、分析／設計／tasks 的角色交接與授權、來源／人工授權、新 feature/adopt、接受／相依啟動與 Retro。
- `delivery-gates`: G1/G2/G3、TDD N/A、版本失效、驗證對照與真實交付證據。
- `finding-resolution`: Finding authority、blocking/closure、批次修正、一次爭議覆核、反覆 finding、人工退回及 review 發布。
- `durable-delivery`: 可讀狀態、ownership、assignment/result、crash/reconcile、outbox、預算與 adapter 邊界。

### Modified Capabilities

無。正式 repo 的 `openspec list --specs` 目前沒有既有 capability；本次新增上述四項。

## Impact

本 repo 目前只有規劃、研究與 OpenSpec 設定，沒有 controller production code 或產品測試。新增範圍預計為 Python controller、窄 adapters、orchestrate skill/references、設定範例、測試與操作文件；具體技術設計與執行任務尚待形成；現有 OpenSpec 文件保留，Q-METHOD 收斂後記錄所選方法及原生 artifact binding，維持唯一 plan／tasks 權威。

驗證對照尚待 design／plan 階段補齊，以四份 specs 的穩定 AC IDs 對應驗法與證據；目前沒有已完成的 validation 文件或執行證據。[比較原稿與審校發現](../../../docs/experiments/spec-authoring-comparison/2026-09-26/README.md) 保留為研究，不是第二份權威。OpenSpec 結構驗證不能證明 controller、runtime 能力或真實 E2E 已完成。
