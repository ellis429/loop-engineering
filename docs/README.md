# 文件導覽

**要用這套流程帶專案或做 feature，先讀 [使用指南](guide/user-guide.md)。** 它先用分層圖與流程大地圖說明整體，再照流程逐一說明每個活動的目的、分工、產出與完成條件；細節查 [參考](guide/reference.md)。附 cross-node-file-transfer 演練路線；完整自動 loop 尚未完成，stacked 政策仍待確認。

## 你要讀哪裡

| 你是 | 去哪 |
| --- | --- |
| 使用這套流程的人：Lead、工程師、驗收人 | [`guide/`](guide/README.md)：使用手冊 |
| 修改或實作這套流程的人 | [`decisions.md`](decisions.md)、[`workflow/`](workflow/overview.md)、[`harness/`](harness/overview.md)：規則與設計理由（手冊和它們有出入時，以它們為準） |
| Agent | [`../skills/`](../skills/)、[`../openspec/config.yaml`](../openspec/config.yaml) |
| 想追來源與過程的人 | `references/`、`research/`、`reviews/`、`handoffs/` |

這是本 repo 的文件安排，不強制下游專案搬動 OpenSpec 或其他 skills 的原生 artifacts。

> **目前進度（2026-09-28）**：[D45-04 revision-17](design-candidate/d45-04/README.md) 的 design＋plan 已由 [D53](decisions.md) 完成 D11 開工確認，文件經 PR #3 合進 main，薄 controller 第一片正在 `delivery/thin-controller` 分支依 tasks 實作，完成狀態以該分支的驗證紀錄為準。D54 定下 spec 的位置與回流（OpenSpec），D55 把 Project 層交給 `project-lead` skill、orchestrate 只跑單一 feature loop；第一片不受影響。D56 讓 cross-node-file-transfer 的 Project 層先開始。D57–D59 定下工作三層（milestone、feature、task）與每個 task 的局部 review、需求依狀態放置（`openspec/specs/` 只放已實作的行為），角色不等於人，以及手動階段的交付紀錄放在 ticket 留言（D60）；說明見[總覽指南的需求放在哪](guide/reference.md#需求放在哪)。[88 AC 審核](reviews/2026-09-27-ac-audit/README.md)、[Opus 初審](reviews/2026-09-28-opus-review-d45-04.md)與[修正紀錄](reviews/2026-09-28-opus-review-d45-04-resolution.md)保留歷史；接續以 [handoff](handoffs/2026-09-27-controller-design.md) 最新段為準。

## 先讀哪份

使用者入口是上面的 [使用指南](guide/user-guide.md)。以下供需要了解規則、維護設計或接續實作的人閱讀：

1. 了解目標：[Project intent](project-intent.md)、[已確認／待決事項](decisions.md)、[領域詞彙](../CONTEXT.md)。
2. 了解方法：[Workflow](workflow/overview.md)、[交接契約](workflow/contracts.md)；準備需求時讀 [Project Lead SA](workflow/project-lead-sa.md)。
3. 討論工具整合：[Herdr 設計](harness/herdr-integration.md)，包含四層概念圖、元件資料流與開工前缺項。它仍是提案；[範圍收斂對照](harness/scope-reconciliation.md) 逐項整理 88 個 AC 與 17 個未解 findings，作為正式修訂的輸入。
4. 接續實作前核對：[正式 OpenSpec change](../openspec/changes/implement-delivery-loop/proposal.md)、[checkpoint](handoffs/2026-09-27-controller-design.md) 及 [AC 對照](validation/implement-delivery-loop.md)。design／tasks 已指向 D53 採用的 revision-17，D40 內容留在 Git 歷史。

## 主要文件與狀態

| 位置 | 責任與目前狀態 |
| --- | --- |
| [guide/user-guide.md](guide/user-guide.md) | 使用指南：大圈包小圈的流程圖、誰做什麼、外圈與內圈的活動卡；細節、範例演練與工具分層見 [參考](guide/reference.md) |
| [project-intent.md](project-intent.md) | 本專案目標、需求基線、D41／D42 成品與責任邊界 |
| [decisions.md](decisions.md) | 已確認決策及未決項目，保留原決策 ID 與沿革 |
| [workflow/overview.md](workflow/overview.md) | Project／Feature 流程、角色、人工介入、Retro；舊平台責任仍依 D41／D42 待對照 |
| [workflow/contracts.md](workflow/contracts.md) | Project／Feature 產出物及版本、assignment、result、finding、gates 的交接語意；提案欄位不等於已實作 API |
| [workflow/project-lead-sa.md](workflow/project-lead-sa.md) | Research／SA 工作指引與進入 Design 的交接；不是已安裝 skill |
| [harness/overview.md](harness/overview.md) | C1–C8 交接位置、skills／tools 導覽；沿 D41／D42 核對舊執行承諾 |
| [harness/herdr-integration.md](harness/herdr-integration.md) | 本輪 Herdr 整合提案及兩張架構圖；未實作、未核准開工、未完成獨立 review |

Project-level 與 Feature-level 都屬於 Workflow。Harness 包含 orchestrate、Herdr、controller、skills／runtime 接合；目錄裡放的是設計，實際程式與已安裝 skills 維持原生位置。

Multica 團隊協作與 GitHub／Azure DevOps 正式 Ticket 是架構中的關注層，目前放在 Herdr 整合提案中討論，尚未各自建立 adapter 或平行的狀態權威。

正式 feature 規格由 OpenSpec change 承接；本表是閱讀導覽，不另產生一份規格。遇到衝突或待決內容，核對適用決策與版本，不以最後修改時間推定核准。

## 目錄

```text
docs/
├── README.md                       # 本導覽
├── project-intent.md               # 專案目標、範圍與需求基線
├── decisions.md                    # 已確認與待決事項
├── guide/                          # 使用手冊：使用指南、參考、圖解
├── workflow/                       # Project／Feature 方法與交接契約
│   ├── overview.md
│   ├── contracts.md
│   ├── project-lead-sa.md
│   └── history/                    # 早期流程草案及推導
├── harness/                        # 執行環境與工具接合
│   ├── overview.md
│   ├── herdr-integration.md
│   └── history/                    # 較早的實現藍圖與狀態設計
├── implementation/                 # 既有實作操作文件
├── handoffs/                       # 有日期的接續與 checkpoint
├── research/                       # 環境、工具與方案查核
├── references/                     # 外部方法整理
├── experiments/                    # 比較實驗、候選稿及證據
├── reviews/                        # Review 紀錄、固定候選及快照
└── validation/                     # AC 對照與執行驗證紀錄
```

`history/` 保存早期推導；不表示引用其中的已確認決策全部失效，也不將尚未通過的交付標為完成。現行規則仍須對回 decisions 與正式規格。

Repo 根目錄的責任維持：

| 位置 | 用途 |
| --- | --- |
| [CONTEXT.md](../CONTEXT.md) | 共用領域語言，保留 domain-modeling 慣例 |
| [openspec/](../openspec/) | 原生 proposal／specs／design／tasks |
| [skills/](../skills/) | 本專案的 skills：`project-lead`（D55，草稿）、`research-codebase` |
| [.agents/skills/](../.agents/skills/)、[.claude/](../.claude/) | 原生 agent skills／commands |
| `src/delivery/`、`tests/` | 舊 S1 controller 與測試，在未合併的 [PR #2](https://github.com/yschiang/loop-engineering/pull/2) 分支，不在 main；薄 controller 第一片在 `delivery/thin-controller` 分支實作中 |
| `.delivery/`、`.worktrees/` | 本機執行狀態與工作區，已 gitignore；可分享的證據另外保存 |

本輪不新增空的 mission／tech／roadmap 文件。Project 產出物的語意與要求見 [產出物契約](workflow/contracts.md#project-與-feature-產出物)，需要獨立維護時再沿責任拆檔。

## 研究、歷史與證據入口

| 要查的內容 | 入口 |
| --- | --- |
| Herdr 原生能力、安裝與 H0 進度 | [方案研究](research/2026-09-27/herdr-orchestrators.md) · [本機 setup／H0](research/2026-09-27/herdr-setup.md) |
| Skills 現況與契約 | [Skills research](research/2026-09-25/skills.md) · [規劃 preflight](research/2026-09-27/planning-preflight.md) |
| OpenCode 接入與限制 | [傳訊研究](research/2026-09-26/agent-messaging-and-opencode.md) · [本機 setup](research/2026-09-27/opencode-setup.md) |
| 初始環境查核 | [Research](research/2026-09-25/research.md) · [Orca 能力](research/2026-09-25/orca-capabilities.md) · [Runtime probe](research/2026-09-25/runtime-probe.md) · [整合限制](research/2026-09-25/integration-gaps.md) |
| 早期交接與 controller 設計推導 | [Feature handoff](research/2026-09-25/feature-handoff-contract.md) · [Loop 藍圖](harness/history/loop-engineering.md) · [檔案狀態](harness/history/file-state.md) |
| 早期流程草案與 Retro 提案 | [Orchestrate 草案](workflow/history/orchestrate-workflow-draft.md) · [輕量流程取捨](research/2026-09-26/workflow-gap-review.md) |
| 外部方法來源 | [SDD](references/spec-driven-development-workflow.md) · [PR Bottleneck](references/fixing-the-pr-bottleneck.md) · [雙層 Retro](references/dual-loop-retro.md) · [Roadmap 規劃](references/roadmap-planning.md) |
| Spec 寫作對照 | [OpenSpec／Matt 實驗](experiments/spec-authoring-comparison/2026-09-26/README.md)；候選稿不是另一份現行規格 |
| 暫緩的既有 PR 接入 | [gigaxfer pre-PR 實驗](experiments/pr-gating.md) |
| 舊 controller 設計及 bootstrap | [設計 review](reviews/2026-09-27-design-review.md) · [詳細設計 review](reviews/2026-09-27-controller-detailed-design.md) · [Bootstrap](research/2026-09-27/controller-bootstrap.md) |
| 舊 S1 實作與操作 | [CLI 文件](implementation/cli.md) · [S1 驗證](validation/s1-bootstrap-20260927.md) · [AC 驗證對照](validation/implement-delivery-loop.md) |

研究或 review 結論適用於其日期及固定版本。文件整理未重跑第三方工具、controller 測試或 GitHub CI，不能推定過去的 review 已涵蓋新設計。

## 維護方式

- 主要規則更新對應既有文件；新研究按日期保存，不再在 docs 根目錄新增一份「整體最新版」。
- 工具接合設計放 harness；查核證據放 research。只有內容需要獨立維護時才拆檔。
- 正式 feature artifacts 與 skills 留在工具原生位置，以引用及版本交接。
- 原始 review 結果、固定候選、manifest、hash、approval、archive 與測試輸出維持原樣；可閱讀文件的導覽連結隨本次搬移更新。
- 有日期的 handoff 保存當時狀態。接續前核對工作目錄與外部實況，不用舊「可開工」文字恢復已停止的工作。

## 2026-09-27 路徑調整

搬移使用工作目錄中的最新內容，保留原有未提交修訂；本次整理不改決策、AC 或核准狀態。歷史紀錄中的舊路徑／行號／hash 保留，對應當時 Git 版本或保存的 snapshot；不拿現行文件 bytes 替代舊證據。

| 舊路徑 | 新位置 |
| --- | --- |
| `docs/workflow-design.md` | [workflow/overview.md](workflow/overview.md) |
| `docs/workflow-contracts.md` | [workflow/contracts.md](workflow/contracts.md) |
| `docs/project-lead-sa.md` | [workflow/project-lead-sa.md](workflow/project-lead-sa.md) |
| `docs/orchestrate-workflow-draft.md` | [workflow/history/orchestrate-workflow-draft.md](workflow/history/orchestrate-workflow-draft.md) |
| `docs/delivery-harness-overview.md` | [harness/overview.md](harness/overview.md) |
| `docs/design/herdr-integration.md` | [harness/herdr-integration.md](harness/herdr-integration.md) |
| `docs/loop-engineering.md` | [harness/history/loop-engineering.md](harness/history/loop-engineering.md) |
| `docs/file-state.md` | [harness/history/file-state.md](harness/history/file-state.md) |
| `docs/workflow-gap-review.md` | [research/2026-09-26/workflow-gap-review.md](research/2026-09-26/workflow-gap-review.md) |

CONTEXT、OpenSpec、skills、原始證據、程式、測試、執行狀態與 worktrees 均保留原位。原本的 `docs/design/` 在唯一文件搬入 harness 後移除空目錄。本次未修改 Git branch、index、commits 或遠端設定。
