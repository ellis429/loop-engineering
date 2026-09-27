# Spec-Driven Development：外部工作流程參考

收錄日期：2026-09-26。

## 來源與用途

來源為使用者在對話中提供的英文 SDD 總覽、中文 Project Constitution 詳解與中文 Feature Loop 詳解。原始網址、作者、工具名稱與版本尚未提供，因此本文不將這些約定視為所有 SDD 工具的共同標準。

本文合併重複內容、調整標題層級，移除對話式推薦尾句；保留來源的工作流程主張與明示檔名，不是逐字逐句的原文存檔。來源中的 immutable / living document、修改 spec、清除 context、merge 等說法均保留為參考觀點，尚未全部採納為本專案政策。

我們的分析與候選改進見 [Orchestrate 流程草案](../orchestrate-workflow-draft.md#外部-spec-driven-development-流程對照2026-09-26)；已確認政策見 [決策紀錄](../decisions.md)。本文的步驟不授權任何 agent 直接執行、修改既有規格或合併 PR。

## 一、整體模式

Spec-Driven Development 將規格的 what / why 與實作的 how 分開。來源將人類定位為提供藍圖與監督的資深架構師，AI agent 則負責執行；流程包含 project-level constitution、feature-level Plan → Implement → Validate，以及 features 之間的 Replanning。

## 二、Project Level：定義 Constitution

### 目的與定位

- **全局契約與標準：** 定義人類、AI agents、團隊及利益相關者共享的高層級需求、架構決策與不可變標準。
- **持久上下文：** 來源認為對話增長會造成 context decay，憲章讓新啟動的 agent 能重新取得全局背景與方向。
- **Agent-agnostic：** 來源將結構化憲章與單一 `agents.md` 比較，主張憲章更具結構性、且不依賴特定 agent。

### 三份核心文件

來源明確指定放在專案 `specs/` 目錄：

```text
specs/
├── mission.md
├── tech.md
└── roadmap.md
```

| 檔案 | 責任 | 內容 |
| --- | --- | --- |
| `specs/mission.md` | Why | 專案願景、核心問題、功能想法、目標受眾、產品範疇 |
| `specs/tech.md` | 工程標準與限制 | 開發/部署技術、依賴、架構模式、工程約束與技術取捨 |
| `specs/roadmap.md` | 分階段交付順序 | 將專案分成小步驟的功能 phases；每個 phase 後續形成獨立 feature spec；此檔是 living document |

### Greenfield：從零建立

1. 開發者提供概念、基本描述或例如 `readme.md` 的輸入。
2. Agent 透過互動訪談釐清目標、產品風格、技術選擇、資料庫偏好與 roadmap 粒度。
3. 根據訪談產生 mission、tech、roadmap。

### Brownfield：既有專案

1. Agent 探索程式碼、目錄結構、`README.md`、`to-do.md` 與 issue tracker。
2. 逆向整理現有架構、需求與規範，產生憲章。
3. 後續 feature 使用該憲章維持與既有 codebase 的一致性。

### 人工審閱與版本控制

1. 開發者檢查三份憲章文件是否完整。
2. 來源建議透過對話要求 agent 修改、同步相關文件，避免手動修改造成 drift；例如補目標受眾或更改資料庫。
3. 將審閱完成的憲章 commit 到 Git，作為後續 feature branch 的基準。

來源一方面使用「不可變標準」，另一方面明確允許 Replanning 更新憲章；這兩種描述均屬來源內容，我們如何解讀其版本與變更控制另見流程草案。

## 三、Feature Level：Plan → Implement → Validate

### 開發前準備

1. 每個 roadmap feature 建立獨立 Git feature branch，保持主幹乾淨與變更可管理。
2. 開始新 feature 前執行 `/clear` 清除 agent context，避免殘留快照或上下文混淆；英文總覽亦在由 Plan 進入 Implement 時建議使用 fresh context。
3. 重新讀取 mission、tech、roadmap；來源稱這三者為唯一權威的全局上下文。

### Plan：建立 Feature Spec

在寫程式前先進行 feature interview，釐清該 roadmap item 的範圍、套件版本、技術約束、界面需求及測試方式。

來源稱 feature spec 包含三份 Markdown 文件：

| 來源名稱 | 責任 |
| --- | --- |
| `plan` | 任務組 Task Groups、執行順序與具體步驟 |
| `requirements` | 技術行為、依賴、邊界條件與限制，避免指定變數名稱等低階細節 |
| `validation` | 可量化成功標準與驗證步驟，如 curl、自動化測試、畫面渲染檢查 |

**檔名界線：** 補充文字只明示 `plan`、`requirements`、`validation`；雖然稱為 Markdown 文件，尚未提供確切副檔名、前綴、feature 目錄或命名模板。不能據此宣稱來源強制使用 `specs/<feature>/plan.md` 等路徑。

人機修訂步驟：

1. 開發者審閱三份文件。
2. 有新增或遺漏的需求時，透過對話要求 agent 同步更新 plan、requirements、validation。
3. 將完成的 feature spec 文件 commit 到 Git，再進入實作。

### Implement：按任務組實作

1. Agent 依 plan 的 Task Groups 分批撰寫程式，較大功能可先執行部分群組，以控制每次變更大小。
2. 人類在 console、IDE diff 或 commit 視窗即時監督，提早發現偏離規格的情況。
3. 來源強調小步執行降低錯誤累積；所提供文字沒有明確要求每次行為變更的 Red → Green → Refactor 證據契約。

### Validate：人機協作驗證

1. **高層級 code review：** 對照 spec、結構與元件責任，避免陷入命名或樣式偏好。
2. **雙向修正：** 來源認為 code 缺失常來自 plan 漏洞，建議同時修改規格與程式，保持一致。
3. **測試與偵錯：** 執行自動化測試、啟動應用、檢查行為，必要時透過 debugger 逐步觀察。
4. **Sub-agent audits：** 複雜 feature 可派 specialized subagents 做深度品質或全專案審查，利用獨立 context 降低主 agent 的上下文負擔。

所提供文字未定義必要 CI checks 的集合、review 與 CI 的版本綁定、finding closure 權限或持久化恢復契約；這是此份材料的範圍界線，不代表所有 SDD 方法皆未處理。

### 收尾

1. 以 changelog skill 等方式更新變更紀錄；來源沒有指定 changelog 的確切檔名。
2. 將 `roadmap.md` 中的對應功能標為完成。
3. 將測試通過的 feature branch merge 回 `main`。

## 四、Inter-feature Replanning

在 feature 與 feature 之間回顧新知、調整後續計畫：

1. **更新憲章：** 跨功能要求、測試框架、responsive design 規範或 tech stack 改變時，於 replanning branch 更新全局文件。
2. **調整 roadmap：** 依新回饋重新排序、分組或細化未來 phases。
3. **保留版本脈絡：** 透過 Git 記錄哪個版本的憲章對應所產生的 code。
4. **Context 與人的負擔：** 切換 feature 時清除 context、適度休息，避免 agent context 混淆及人的 review 疲勞。

Replanning 是修改既有憲章與 roadmap 的階段；來源沒有規定一定新增 `replanning.md`。

## 五、自動化與工具原則（英文總覽補充）

- 用 custom skills 包裝 spec interview、changelog、lint / validation 等重複流程。
- 來源偏好 CLI + skills，認為可降低相較於大型 MCP 服務的 context 與設定負擔，並以 Context7 作例子。
- 將探索性想法、資料庫評估等研究放到獨立 research files / backlog；未指定固定檔名。
- 來源提到 `agents.md`、Agent Skills 與 ACP 作為跨 agent / IDE 協作標準，目標是在 Claude Code、Codex、OpenCode 等環境維持相同工作流程。

以上為來源主張的收錄。CLI / MCP 的取捨、ACP 實際範圍，以及它們和我們 controller / gates 的關係，已在 [流程草案的比較段落](../orchestrate-workflow-draft.md#外部-spec-driven-development-流程對照2026-09-26) 另作分析。


## 六、使用者補充：課程定位與涵蓋程度

來源：使用者後續針對七項比較的補充，尚未由本 agent 直接觀看課程影片查核。課程定位是個人/小團隊使用的輕量 SDD 實踐，重點在 Human-Agent 溝通與 context 管理，並未宣稱提供完整工程治理規範。先前我們提出的七項補強是為自身工作流推導的候選，不應倒過來當成課程必須涵蓋卻遺漏的內容。

| 階段 | 使用者補充的課程實際內容 | 未由課程明定的進階規範 |
| --- | --- | --- |
| Project 準備 | 訪談生成 mission / tech / roadmap，人審後 commit；新 session 清 context 並重讀憲章 | 門檻式 project-ready 清單、正式批准版本機制、強制啟動讀取程序 |
| Feature 規劃 | 產生 plan / requirements / validation，由人整體檢查確認 | 每條 AC 嚴格對應方法、環境與量化門檻的治理矩陣 |
| 人工驗收 | 人看 commit diff，要求同步修 spec/code 或請 subagent 深度審查 | 缺陷、新需求與規格錯誤的正式分流與權責程序 |
| 文件收尾 | 勾選 roadmap，示範自訂 Changelog skill | README、migration、操作手冊的統一責任清單與 changelog 適用政策 |
| Phase 0 | 示範 Next.js / Hono 等骨架初始化、基本配置與驗證服務啟動的腳本 | 完整 setup / build / test / CI 證據契約 |
| Milestone | 將多個 roadmap 項目組成一次 MVP 實驗並驗證 | 正式整合 demo 規範、接受人與跨 feature 整合測試定義 |
| Replanning | 在 feature 間以獨立 branch 更新憲章、roadmap 或架構標準 | ADR 與「維持 baseline 不變」的簽核流程自動化 |

此表補充來源範圍，不代表本專案應全部增加右欄規範。MVP 的取捨另見 [流程對照與 MVP 取捨](../workflow-gap-review.md)。
