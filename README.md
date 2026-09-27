# Orca Delivery

建立 Project／Feature Delivery Harness，將選定的 feature issue 推進到具備證據的 PR Pass。預設用 OpenCode 執行 agents，依角色選用 OpenAI／Claude models；Orca、Codex／ChatGPT 相關入口與 Claude Code 是選配。Controller 核心依賴共用 adapter 契約，角色、交接及 gates 共用，精確模型／接入能力仍需查證。

目前階段：D40 已核准 controller v3 design／tasks，private `yschiang/orca-delivery` 已建立，準備 S1 core 實作。S2 adapters、S3 orchestrate／E2E 依序交付；尚無產品 gate 或端到端通過證據。

接續狀態：[Controller handoff](docs/handoffs/2026-09-27-controller-design.md)；正式 [design](openspec/changes/implement-delivery-loop/design.md)、[tasks](openspec/changes/implement-delivery-loop/tasks.md)、[AC 驗證對照](docs/validation/implement-delivery-loop.md)。

目前優先事項（D33）：**先在 orca-delivery 測通 workflow、orchestrate 與預設工具組合，再啟動 cross-node-file-transfer**。新專案沿用既有需求／設計／roadmap 基準，核對來源並映射文件結構，省去重做完整 grill；從初始化開始留下新的交付證據。目的讓 member 沿同一入口與預設方法工作，不必各自挑 skills。詳見 [測通與新專案順序](docs/workflow-design.md#101-先測通-orca-delivery再啟動新專案d33)。

## 文件

- [2026-09-27 設計 Review：findings、修正、覆核與證據](docs/reviews/2026-09-27-design-review.md)
- [Controller bootstrap：派工、連線失敗及 OpenCode 預設路徑](docs/research/2026-09-27/controller-bootstrap.md)
- [Compact／新 session 交接：接續 controller 詳細設計與 plan](docs/handoffs/2026-09-27-controller-design.md)
- [Delivery Harness 總覽：流程、八個交接位置、skills 與 tools](docs/delivery-harness-overview.md)
- [同題規格實驗：OpenSpec 與 Matt to-spec 的兩份草稿及比較](docs/experiments/spec-authoring-comparison/2026-09-26/README.md)
- [整體 Workflow Design v1：流程、角色、驗收與 Retro](docs/workflow-design.md)
- [Project Lead：Research／SA 階段契約、七項 Spec 內容與 Design 交接](docs/project-lead-sa.md)
- [Project／Feature 產出物：mission、domain、roadmap 與 requirements／plan／validation](docs/workflow-contracts.md#project-與-feature-產出物)
- [Workflow 執行契約：版本、結果、gates、恢復與 skills](docs/workflow-contracts.md)
- [Orchestrate：project / feature 流程草案與文件比較](docs/orchestrate-workflow-draft.md)
- [外部參考：Spec-Driven Development 工作流程](docs/references/spec-driven-development-workflow.md)
- [Retro 接入設計：feature 收尾與 project Replanning](docs/orchestrate-workflow-draft.md#retro-接入設計建議)
- [外部參考與本機查核：雙層 Retro](docs/references/dual-loop-retro.md)
- [外部參考：Fixing the PR Bottleneck 與品質層次對照](docs/references/fixing-the-pr-bottleneck.md)
- [Project / Feature 流程對照與 MVP 取捨](docs/workflow-gap-review.md)
- [保留的暫緩方案：gigaxfer pre-PR gating loop](docs/experiments/pr-gating.md)
- [Loop Engineering：完整流程與實現藍圖](docs/loop-engineering.md)
- [JSON／YAML 檔案狀態與恢復設計](docs/file-state.md)
- [需求意圖與已確認邊界](docs/project-intent.md)
- [決策狀態](docs/decisions.md)
- [領域詞彙](CONTEXT.md)
- [環境查核與 baseline evidence](docs/research/2026-09-25/research.md)
- [Orca 控制介面](docs/research/2026-09-25/orca-capabilities.md)
- [Agent 傳訊與 opencode：版本查核、限制與未實證項目](docs/research/2026-09-26/agent-messaging-and-opencode.md)
- [真實 agent 派工 probe 與能力缺口](docs/research/2026-09-25/runtime-probe.md)
- [Codex sandbox / Orca IPC 與 workspace 整合查核](docs/research/2026-09-25/integration-gaps.md)
- [Skills 契約與版本查核](docs/research/2026-09-25/skills.md)
- [Feature 交接欄位草案](docs/research/2026-09-25/feature-handoff-contract.md)

## 工作層級

Project spec 定義共用契約；feature ticket 的內文或引用文件承擔 feature spec。每個可獨立驗收的 feature 對應一個 PR，implementation tasks 是該 PR 的派工單位。Review 同時對照適用的 project / feature specs。

角色統一為 **Project Lead Agent**（研究、SA、domain modeling、高層設計、roadmap 與 feature 規格）、**Implementer Agent**（詳細設計、最終 plan／tasks、實作與修正）、**Reviewer Agent**（獨立審查與覆核）。依 D23，Project Lead 負責專案協調，Implementer 負責功能交付，兩者以 spec／AC、依賴與成果交接；委派權依使用者明確授權，runtime 不綁定固定父子關係。使用者可直接與任一角色合作，共同入口不代表相同決策權。重大裁決與最終接受由使用者決定；controller 負責唯一派工、狀態與 gate 證據核查。詳見 [角色與控制權](docs/workflow-design.md#2-角色與控制權)。

依 D32，Project Lead 先與使用者研究及分析系統、釐清領域與高層設計，再形成 roadmap／milestones、拆 features；準備單一 feature 時再做聚焦的 research／SA／grill，交出 spec／AC 與必要 high-level design。Implementer 承接後研究實作細節、完成 detailed design 與 plan；Project Lead 可提任務草案，由 Implementer 校準最終可執行 tasks。流程與交接見 [Project／Feature 準備](docs/workflow-design.md#4-project-loop從基礎到可交付-features)。

D34 將使用者的 Project Lead prompt 納入 [Research／SA 階段契約](docs/project-lead-sa.md)：project 與 feature 共用分析方法、調整深度；SA 是活動，Spec 是成果。先有足夠 project SA 與高層設計才形成 roadmap；選定 feature 再聚焦需求。SA 可進入 Design 的使用者確認與 D11 開工確認分開。

規格與規劃工具組合已重新開放評估（D31／Q-METHOD）；既有 OpenSpec 文件保留，研究樣本不成為另一份權威。這次確認角色與流程，不鎖定 Matt、OpenSpec 或 Writing Plans 的整合方式。

PR Pass 必須同時滿足：G1 實作與 TDD 證據、G2 獨立 review 無未解決阻擋項、G3 必要 CI 檢查成功。結論綁定目前 PR head、review base 與適用規格版本。

依 D30／D38，單一本機持久化 controller 預設接 OpenCode；使用者可選已配置的 Orca／Codex／Claude Code 接入，不以這些工具存在作為啟動／resume 或派工的共同前置。停止於 Ready for human acceptance；merge、close issue、release、deploy 不在預設範圍。
