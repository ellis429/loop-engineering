# Loop Engineering

建立可供多人使用與展示的 Loop Engineering：Project／Feature workflow、開源 skills、orchestrate 與可呼叫的薄 controller，再用 cross-node-file-transfer 展示多個 features、worktrees 與具證據的 PR gating。預設用 OpenCode 執行 agents，依角色選用 OpenAI／Claude models；Orca、Codex／ChatGPT 相關入口與 Claude Code 是選配。Controller 核心依賴共用 adapter 契約，角色、交接及 gates 共用，精確模型／接入能力仍需查證。

目前階段（2026-09-28）：薄 controller 第一片（D45-04 revision-17）已由 D53 核准，經 PR #3 採用進正式 OpenSpec change，正在 `delivery/thin-controller` 分支實作。D54、D55 定下 spec 的位置與 `project-lead`、`orchestrate` 兩個 skill 的分工。舊 S1 的 [PR #2](https://github.com/yschiang/loop-engineering/pull/2) 未合併，17 項獨立 review findings 尚未覆核關閉；不宣稱 PR Pass 或完整 E2E。完整成品與責任邊界見 [Project intent](docs/project-intent.md)。

接續狀態：[Controller handoff](docs/handoffs/2026-09-27-controller-design.md)；正式 change 的 [design](openspec/changes/implement-delivery-loop/design.md)、[tasks](openspec/changes/implement-delivery-loop/tasks.md)、[AC 驗證對照](docs/validation/implement-delivery-loop.md) 都指向 D53 採用的版本，D40 內容留在 Git 歷史。

目前優先事項（D33）：**先在 loop-engineering 測通 workflow、orchestrate 與預設工具組合，再啟動 cross-node-file-transfer**。新專案沿用既有需求／設計／roadmap 基準，核對來源並映射文件結構，省去重做完整 grill；從初始化開始留下新的交付證據。目的讓 member 沿同一入口與預設方法工作，不必各自挑 skills。詳見 [測通與新專案順序](docs/workflow/overview.md#101-先測通-orca-delivery再啟動新專案d33)。

## 文件

**第一次使用，先讀 [使用指南總覽](docs/workflow/user-guide.md)**：一張泳道全貌圖說明人與 Agent 的分工，再依角色選一份讀：帶專案讀 [Project Lead 指南](docs/workflow/user-guide-project-lead.md)，接 feature 讀 [Feature Builder 指南](docs/workflow/user-guide-feature-builder.md)。另有 [圖解頁](docs/workflow/user-guide-visual.html)。完整自動 loop 尚未完成，stacked PR 仍是待定政策下的目標流程。

維護設計或接續開發時，再讀 [文件導覽](docs/README.md)：

| 要了解什麼 | 入口 |
| --- | --- |
| 使用者如何開始、交接與驗收 | [總覽](docs/workflow/user-guide.md) · [Project Lead](docs/workflow/user-guide-project-lead.md) · [Feature Builder](docs/workflow/user-guide-feature-builder.md) |
| 專案目標與決策 | [Project intent](docs/project-intent.md) · [Decisions](docs/decisions.md) · [CONTEXT](CONTEXT.md) |
| Project／Feature 怎麼合作與交接 | [Workflow](docs/workflow/overview.md) · [Contracts](docs/workflow/contracts.md) · [Project Lead SA](docs/workflow/project-lead-sa.md) |
| 執行環境與工具如何接合 | [Harness 總覽](docs/harness/overview.md) · [Herdr 整合設計與架構圖](docs/harness/herdr-integration.md) |
| 研究、實驗、審查與驗證紀錄 | [證據與歷史入口](docs/README.md#研究歷史與證據入口) |

[Herdr 整合設計](docs/harness/herdr-integration.md)是早期提案；第一片實際採用的 Herdr profile 以 D53 核准的版本為準。文件整理不改變三 gates 或開工核准狀態。

## 工作層級

Project spec 定義共用契約；依 D54，feature spec 寫在 OpenSpec change 的 proposal 與 spec delta，ticket 只保存摘要與連結。每個可獨立驗收的 feature 對應一個 PR，implementation tasks 是該 PR 的派工單位。Review 同時對照適用的 project / feature specs。

角色統一為 **Project Lead Agent**（研究、SA、domain modeling、高層設計、roadmap 與 feature 規格）、**Implementer Agent**（詳細設計、最終 plan／tasks、實作與修正）、**Reviewer Agent**（獨立審查與覆核）。依 D23，Project Lead 負責專案協調，Implementer 負責功能交付，兩者以 spec／AC、依賴與成果交接；委派權依使用者明確授權，runtime 不綁定固定父子關係。使用者可直接與任一角色合作，共同入口不代表相同決策權。重大裁決與最終接受由使用者決定；orchestrate 維持唯一外層協調循環，controller 負責狀態與 gate 證據核查。詳見 [角色與控制權](docs/workflow/overview.md#2-角色與控制權)。

依 D32，Project Lead 先與使用者研究及分析系統、釐清領域與高層設計，再形成 roadmap／milestones、拆 features；準備單一 feature 時再做聚焦的 research／SA／grill，交出 spec／AC 與必要 high-level design。Implementer 承接後研究實作細節、完成 detailed design 與 plan；Project Lead 可提任務草案，由 Implementer 校準最終可執行 tasks。流程與交接見 [Project／Feature 準備](docs/workflow/overview.md#4-project-loop從基礎到可交付-features)。

D34 將使用者的 Project Lead prompt 納入 [Research／SA 階段契約](docs/workflow/project-lead-sa.md)：project 與 feature 共用分析方法、調整深度；SA 是活動，Spec 是成果。先有足夠 project SA 與高層設計才形成 roadmap；選定 feature 再聚焦需求。SA 可進入 Design 的使用者確認與 D11 開工確認分開。

規格與規劃工具組合已重新開放評估（D31／Q-METHOD）；既有 OpenSpec 文件保留，研究樣本不成為另一份權威。這次確認角色與流程，不鎖定 Matt、OpenSpec 或 Writing Plans 的整合方式。

PR Pass 必須同時滿足：G1 實作與 TDD 證據、G2 獨立 review 無未解決阻擋項、G3 必要 CI 檢查成功。結論綁定目前 PR head、review base 與適用規格版本。

依 D30／D38，單一本機持久化 controller 預設接 OpenCode；使用者可選已配置的 Orca／Codex／Claude Code 接入，不以這些工具存在作為啟動／resume 或派工的共同前置。停止於 Ready for human acceptance；merge、close issue、release、deploy 不在預設範圍。
