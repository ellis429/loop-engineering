# Loop Engineering 使用指南

> 草案：流程已定，自動化還在做，現在可以照著人工演練。見[現在做到哪裡](#現在做到哪裡)。

**先決定要什麼，再一次交付一個 Feature；每交付一個，就回頭調整計畫。**

就是熟悉的 SDLC，只是大部分工作由 Agent 做，人負責做決定。

## 分層：人、Agent 與工具

```text
人          Lead、工程師、驗收人                       做決定：方向、順序、spec、開工、驗收
 │ 用自然語言交代、確認
ADE         Herdr、OpenCode、Claude Code（Orca 選配）   開 session 與 worktree，讓多個 Agent 並排工作
 │
Skills      project-lead、orchestrate、research-codebase、TDD、OpenSpec   告訴 Agent 照什麼方法做
 │
Agents      Project Lead Agent ⇄ Implementer ⇄ Reviewer（不同模型）      做實際的分析、實作與審查
 │
紀錄與核對  共用的狀態：人和 Agent 靠它交接，不靠聊天
            ├ 核對：controller 檢查版本、證據與三個 gates（第一片實作中）
            └ 保存：Git branch／worktree、OpenSpec 檔案、GitHub Issue／PR／CI
```

**Workflow** 是 Project、Feature 兩層的步驟與規則，貫穿所有層；**Harness** 是讓這些規則真的被執行的 ADE、skills 和 controller。

## 流程大地圖

### 三段與人的確認點

```text
1. 定方向   為什麼做、做到哪算成功、用什麼技術     ◆① 可進入設計（Lead）
2. 排順序   分成幾個 Milestone，各有哪些 Feature    ◆② 專案基準與 roadmap（Lead）
                                                    ◆③ 下一個 Feature（Lead）
3. 交付一個 Feature（重複）
     講清楚 → 做出來 → 驗收                       ◆④ spec（Lead）
                                                    ◆⑤ 開工（被授權的人）
                                                    ◆⑥ 接受或退回（驗收人）
     └─ 驗收後回到 2，調整順序
```

Lead 同時擔任工程師時，④ 併入 ⑤：spec、design、plan 一起確認一次。不同人擔任時分開，Lead 先確認 spec，工程師才開始設計。

### 展開成活動

```text
A. 定方向、排順序（開始時一次，之後偶爾回來修）
   A1 Project SA     為什麼做、做到哪算成功      ◆①
   A2 高層設計       用什麼架構與技術
   A3 Roadmap        Milestone → Feature          ◆②
        │ ◆③ 選下一個 Feature
        ▼
B. 交付一個 Feature（每個 Feature 一圈）
   講清楚  B1 開 Feature     建立這個 Feature 的 spec，開 ticket 追蹤
           B2 Feature SA     寫 spec：需求與 AC        ◆④（兼任工程師時併入 ⑤）
           B3 交接           交接包給工程師
   做出來  B4 Design＋plan   怎麼做、拆成哪些 task     ◆⑤
           B5 實作           逐 task：TDD、commit、局部 review
           B6 PR             G2 review＋CI → PR Pass
   驗收    B7 驗收、merge    人判斷是不是要的          ◆⑥
           B8 收尾           做完的需求併入現況、Retro、回 A3 調整
        │ 累積到一個 Milestone
        ▼
C. Milestone 驗收（跨 Feature 的整合驗證；怎麼控還在討論）
```

## 誰做什麼

| | 人 | Agent | 機制 |
| --- | --- | --- | --- |
| 定方向、排順序、講清楚、收尾 | **Lead**：給目標與限制、回答問題、做確認 ①–④ | **Project Lead Agent**（`project-lead` skill）：研究、SA、寫文件、提建議 | 文件與版本是交接權威，聊天不是 |
| 做出來 | **工程師**（Feature Builder）：安排技術交付；被授權時做確認 ⑤ | **Implementer**：design、plan、TDD、PR 與修正。**Reviewer**：獨立審查，不改被審 branch | **Orchestrate** 跑一個 Feature 的 loop；**controller** 核對版本、證據與 gates |
| 驗收 | **驗收人**：看 AC 的證據與 demo，做確認 ⑥ | — | — |

- **角色是工作，不是職位**。同一人兼任 Lead 與工程師是常態，這時 ④ 併入 ⑤。每個 Feature 開始時，寫明誰確認開工、誰裁決需求、誰驗收。
- **Lead 和 Project Lead Agent 不同**：Lead 做決定，Agent 做分析與建議。驗收人也不是 Reviewer Agent 的另一個名稱。
- **控制只往下走**：Project Lead 把交接包交給 orchestrate；orchestrate 不回頭呼叫 Project Lead，遇到需求或範圍問題就回報 Blocked，由人和 Project Lead 接手。

流程全貌與六個確認點見上方的[流程大地圖](#流程大地圖)；stacked PR 的現行規則與目標情境見[圖解頁](visual.html)。

## 專案的 repo 結構

每個產品一個 root repo 放規劃；只有一個 repo 的產品，root 就是它自己。

```text
<產品>-root/
├── openspec/             spec：現況，以及進行中的 Feature
├── docs/                 intent、roadmap、決策、設計
├── AGENTS.md、CLAUDE.md  共用的 agent 規則
├── repos.yaml            服務 repo 清單：名稱、URL、預設 branch、路徑、用途
└── repos/                同步指令依清單 clone 進來（root 不追蹤）
    ├── order-service/    各自的 origin、branch、PR、CI
    └── payment-service/
```

- 一個 Feature 可以跨 repo：一份 spec 放在 root，每個受影響的 repo 一個 PR（root 也算一個），都連到同一張 ticket。
- loop-engineering 是工具，不當產品的 root。

## 活動卡

每張卡是一個活動的正式定義：

- **目的**：一句話。
- **輸入**：開始前要有的東西。
- **步驟**：誰、做什麼、用什麼。「skill 第 N 步」指 [project-lead skill](../../skills/project-lead/SKILL.md) 的章節。
- **產出**：每一列一個產出，寫明位置、內容與由哪一步產生。controller 可用前，交付紀錄放在 ticket 留言；薄 controller 第一片已把開工確認與接受紀錄定在它自己的狀態檔，用它時以狀態檔為準，ticket 留言是摘要。
- **完成條件**：每一條都可以檢查。

標「工程師」的卡，只帶專案的人可以跳過。

### A1 Project SA

**目的**：確定為什麼做、做到哪裡算成功，作為後面所有取捨的依據。

**輸入**

- 問題描述與限制（人提供）
- 既有資料：repo、現成需求文件、設計（有的話）

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 人 | 交代要解決的問題、限制與既有資料 | 下方的開口句 |
| 2 | Agent | 讀既有資料，記下來源與版本 | skill 第 0–1 步（Project 模式） |
| 2a | Agent → 人 | 有現成需求文件時才做：提出「原章節 → 能力」對照；人確認拆法後，照原意搬進需求輸入並記下來源版本 | skill 第 1 步 |
| 3 | Agent | 研究現況，分清事實、推論與未知 | skill 第 2 步；research-codebase |
| 4 | Agent | 搭骨架：SA 七項，每一格標「假設」 | skill 第 3 步 |
| 5 | 人＋Agent | 由上往下問答，每輪 1–3 題 | skill 第 3 步；需要時用 grill-with-docs、domain-modeling |
| 6 | Agent | 每輪把答案寫進對應的文件 | skill 第 3–4 步 |
| 7 | Agent → 人 | 交一頁摘要，提出「可進入設計」；人確認（◆①） | skill 第 5 步 |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| 研究報告 | 專案的研究目錄（例如 `docs/research/`） | 現況與依據；事實、推論、未知 | 3 |
| project intent | 專案選定的位置（例如 `docs/project-intent.md`） | 問題與目標、範圍與不做、共用限制 | 6 |
| 共同詞彙 | `CONTEXT.md` | 共用的領域用語 | 6 |
| 需求輸入 | 專案自訂，例如 `docs/research/<日期>-import/` | 問出來的端到端情境、能力清單、關鍵規則與驗收方向；有現成需求文件時，另附它依能力拆分的內容、「原章節 → 能力」對照與來源版本 | 2a、6 |
| 決策與待決 | 決策紀錄（例如 `docs/decisions.md`） | 已確認的決策、待決事項與影響 | 5、6 |
| 確認紀錄 | 決策紀錄 | 誰、何時、原話、確認的版本 | 7 |

**完成條件**

- [ ] 目標、範圍、端到端情境、能力清單、共用限制都已確認
- [ ] 沒有擋住設計的待決；可延後的已列出影響與處理時點
- [ ] 人確認「可進入設計」（◆①），紀錄含版本

> 請用 project-lead skill 做 project 的 SA。Repo 在〈路徑〉，既有資料在〈位置〉。我想解決的問題是〈一兩句〉。

骨架怎麼搭、怎麼由上往下問，見參考的[需求是怎麼問出來的](reference.md#需求是怎麼問出來的)。

### A2 高層設計

**目的**：定下元件責任、主要資料流與技術選擇，roadmap 才切得出能單獨驗收的 Feature。

**輸入**

- A1 的 project intent、能力清單、共用限制
- 既有設計與 ADR（有的話）

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | Agent | 沿用或提出高層設計與方案比較 | skill 第 5a 步 |
| 2 | 人 → Agent | 人在方案之間做選擇；Agent 記進決策紀錄 | skill 第 5a 步 |
| 3 | Agent | 把重要取捨寫成 ADR | skill 第 5a 步 |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| 高層設計 | 既有設計文件的位置，或專案選定的位置（例如 `docs/design/`） | 元件責任、主要資料流、對外契約、技術棧 | 1 |
| 技術決策 | 決策紀錄 | 人的選擇與原話 | 2 |
| ADR | 既有 ADR 目錄（例如 `docs/adr/`） | 重要取捨與理由 | 3 |

**完成條件**

- [ ] 每個能力都有負責的元件
- [ ] 技術選擇有依據，重要取捨有 ADR

### A3 Roadmap

**目的**：決定先做什麼，讓每次只交出一個 Feature。

**輸入**

- 能力清單、共用限制（A1）
- 高層設計（A2）

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | Agent | 提出 Milestone：成果與完成條件 | skill 第 5a 步 |
| 2 | Agent | 切法有依據時，把當前 Milestone 切成 Feature：名稱、一句範圍、依賴、相關需求輸入；沒有依據時先只列交付能力 | skill 第 5a 步 |
| 3 | 人 → Agent | 人排順序、決定範圍，標出近期的 1–2 個；Agent 更新 roadmap 並記進決策紀錄 | skill 第 5a 步 |
| 4 | Agent → 人 | 交專案基準與 roadmap 的摘要；人確認（◆②） | skill 第 5a 步 |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| roadmap | 專案選定的位置（例如 `docs/roadmap.md`） | Milestone 的成果與完成條件；已切出的 Feature 的名稱、範圍、依賴、相關需求輸入、狀態（近期或暫定） | 1–3 |
| 範圍與順序的決策 | 決策紀錄 | 人的決定與原話 | 3 |
| 確認紀錄 | 決策紀錄 | 專案基準與 roadmap 的確認，含版本 | 4 |

**完成條件**

- [ ] 每個 Milestone 有成果與完成條件
- [ ] 已切出的 Feature 各自能用自己的 AC 驗收，每個受影響的 repo 一個審得動的 PR
- [ ] 近期的 1–2 個 Feature 已標出
- [ ] 人確認專案基準與 roadmap（◆②）

切多細、Feature 的定義，見參考的[工作層級](reference.md#工作層級milestonefeaturetask)與[Roadmap 要切多細](reference.md#roadmap-要切多細)。

### B1 開 Feature

**目的**：讓這個 Feature 有自己的 spec 位置與追蹤入口。

**輸入**

- roadmap 上這個 Feature 的一行

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 人 | 選這個 Feature（◆③），指定工程師 | — |
| 2 | Agent | 建立 spec 的位置 | skill 第 0 步（Feature 模式）；`openspec new change <id>` |
| 3 | Agent | 開 ticket，或把既有的 ticket 連上 spec；寫到 GitHub 前先問人 | skill 第 6 步的 ticket 欄位 |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| spec 的位置 | root 的 `openspec/changes/<id>/` | 之後放 proposal、spec、design、tasks | 2 |
| ticket | GitHub Issue | 目標、Milestone、spec 連結、Blocked by、狀態 | 3 |

**完成條件**

- [ ] `openspec/changes/<id>/` 已建立
- [ ] ticket 連到 spec，依賴寫清楚

### B2 Feature SA

**目的**：把這個 Feature 做到什麼算完成，寫成可以驗收的 spec。

**輸入**

- roadmap 上這個 Feature 的一行
- 相關的需求輸入與共用限制
- 專案基準（intent、設計、`openspec/specs/` 的現況）；交接時記錄它們的實際路徑與版本

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 人 | 請 Agent 準備這個 Feature | 下方的開口句 |
| 2 | Agent | 讀輸入、研究現況 | skill 第 1–2 步；research-codebase |
| 3 | Agent | 搭骨架：目標、不做、角色與流程、規則、例外、驗收、待決 | skill 第 3 步 |
| 4 | 人＋Agent | 由上往下問答，每輪 1–3 題 | skill 第 3 步 |
| 5 | Agent | 寫 proposal 與 spec，檢查格式 | skill 第 4 步；`openspec validate <id>` |
| 5a | Agent | 這個 Feature 需要新的高層設計邊界時，寫進專案的設計文件或 ADR，並在 proposal 引用；`design.md` 留給 Implementer | skill 第 4 步 |
| 6 | Agent → 人 | 交一頁摘要；人確認（◆④）。兼任工程師時不在這裡確認，改在 B4 一起確認 | skill 第 5 步 |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| proposal | `openspec/changes/<id>/proposal.md` | 為什麼、範圍與不做、待決與依賴、引用的設計邊界、SA 確認紀錄 | 5、5a、6 |
| 設計邊界（需要時） | 專案的設計文件或 ADR | 這個 Feature 需要的新元件責任或對外契約 | 5a |
| spec | `openspec/changes/<id>/specs/<能力>/spec.md` | 這次新增或修改的需求；每條需求附 Scenario，每個 Scenario 是一條帶 ID 的 AC | 5 |
| 一頁摘要 | 給人確認用，不另存 | 照意思排列，附連結與版本（見下方範例） | 6 |

**完成條件**

- [ ] SA 七項都有答案，或列為待決
- [ ] 沒有會改變核心範圍、行為或驗收的阻擋性待決；可延後的已寫明影響與承接者
- [ ] 每條需求至少有一個 Scenario
- [ ] `openspec validate <id>` 通過
- [ ] 人確認摘要（◆④），或註明併入 B4 的開工確認

> 請用 project-lead skill 準備〈Feature〉：補足 spec、AC、必要高層設計與依賴，引用專案基準的實際版本。

一頁摘要的樣子：

```text
目標：……                          → proposal.md#why
不做：……                          → proposal.md
規則：ING-01 ……、ING-02 ……        → specs/<能力>/spec.md
例外：AC-I03 重複寫入、AC-I04 逾時
待決：Q1 容量上限（阻擋設計，請你確認前先決定）
版本：<commit 或檔案 hash>
```

需求從哪來、spec 怎麼寫，見參考的[需求放在哪](reference.md#需求放在哪)與[Spec 怎麼寫](reference.md#spec-怎麼寫放哪)。

### B3 交接

**目的**：讓工程師不必回頭問，就能開始設計。

**輸入**

- B2 的 spec，以及 SA 確認紀錄或「併入開工確認」的註記
- 專案基準

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 人 | 指定誰批准開工、誰驗收（兼任時自己接） | — |
| 2 | Agent | 組交接包；獲授權時貼成一則 ticket 留言，未獲授權就交給人貼 | skill 第 6 步 |
| 3 | Agent 或人 | ticket 補上驗收 ID，狀態改為就緒；Agent 只在獲授權時寫 ticket | skill 第 6 步 |
| 4 | 工程師 | 核對交接包：能開始設計，或退回具體問題 | — |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| 交接包 | ticket 留言 | 工程師開始設計需要的一切：spec 與版本、每個受影響 repo 的起點與預定的 PR、SA 確認或「併入開工確認」的註記、依賴、待決與決策者（完整欄位見[交接契約](../workflow/contracts.md#角色交接摘要)） | 2 |
| ticket | GitHub Issue | 驗收 ID；狀態：就緒 | 3 |

**完成條件**

- [ ] 交接包每一欄都有內容，或寫明不適用
- [ ] 工程師已核對，能開始設計或已退回具體問題

各欄位的定義見參考的[交接](reference.md#交接)。

### B4 Design＋plan（工程師）

**目的**：決定怎麼做、拆成哪些 task。

**輸入**

- 交接包、spec
- 專案基準與高層設計

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 工程師，或獲授權的 Project Lead | 啟動這個 Feature 的 loop；Project Lead 只能在人授權的範圍內啟動 | 下方的開口句；orchestrate（可用前由人協調） |
| 2 | Implementer | 研究並寫 detailed design | OpenSpec 的 design |
| 3 | Implementer | 拆 tasks（每個一個 session 做得完），寫每條 AC 的驗法 | OpenSpec 的 tasks；驗證對照 |
| 4 | 被授權的人 | 確認開工（◆⑤；兼任時連 spec 一起確認）；確認記成一則 ticket 留言，獲授權才由 Agent 張貼，否則交人張貼 | orchestrate（可用前由協調的人寫） |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| design | `openspec/changes/<id>/design.md` | 模組介面、資料、失敗與恢復、測試策略 | 2 |
| tasks | `openspec/changes/<id>/tasks.md` | task 清單、順序、依賴、對應的 AC；多 repo 時每個 task 註明改哪個 repo | 3 |
| AC 驗法 | 專案的驗證文件，或 plan 裡明確的一段 | 每條 AC 的方法、環境、通過標準、證據位置 | 3 |
| 開工確認紀錄 | ticket 留言 | 誰、何時、原話、確認的 design＋plan 版本 | 4 |

**完成條件**

- [ ] 每個 task 一個 session 做得完
- [ ] 每條 AC 都有驗法
- [ ] 開工確認有紀錄

> 請用 orchestrate 承接〈Feature〉。先由 Implementer 讀取它引用的專案基準、spec／AC 與高層設計，提出 detailed design、可執行 tasks 及 AC 驗證方式，交我確認後開工。保留 worktree 與證據；終點是 PR Pass，等待人驗收。

### B5 實作（工程師）

**目的**：一個 task 一個 task 把行為做出來，每一步都能驗證。

**輸入**

- 確認過的 design 與 tasks

**步驟**（每個 task 重複）

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | Implementer | 先寫會失敗的測試（Red），再實作到通過（Green） | Superpowers TDD |
| 2 | Implementer | 提交一到幾個 commit，每個 commit 自己綠燈 | Git；Feature branch 或 worktree |
| 3 | Reviewer（不同模型、新 session） | 審這個 task 的 commit | 獨立 Reviewer，唯讀 |
| 4 | Implementer → Reviewer | 有 blocking 就修掉，Reviewer 覆核 | — |
| 5 | orchestrate | 每個 task 審完都記一則 ticket 留言，沒有 finding 也記；獲授權才張貼，否則交人張貼 | orchestrate |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| commits | 受影響 repo 的 Feature branch | 這個 task 的程式差異 | 1、2 |
| TDD 證據 | controller 保存（第一片實作中） | Red → Green 紀錄 | 1 |
| 局部 review 紀錄 | ticket 留言，每個 task 一則 | 審查者與模型、時間、審的 commit 範圍、verdict、findings、修正與覆核結果、連結 | 5 |

**完成條件**

- [ ] 每個行為 task 都有有效的 Red 與 Green；純文件或註解的 task 標 TDD N/A，附理由與檢查，並由獨立 Reviewer 確認
- [ ] 局部 review 的 blocking 已修好並覆核

### B6 PR（工程師）

**目的**：用獨立審查與 CI 證明整個 Feature 符合 spec。

**輸入**

- 所有 task 都完成的 Feature branch

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | Implementer | G1：在整合後的 head 跑最終 Green 與回歸；通過才 push 送審 | Superpowers TDD |
| 2 | Implementer | 每個受影響的 repo 開一個 PR，連到同一張 ticket並互相連結 | GitHub |
| 3 | Reviewer | G2：對照 spec 與 design，審整組 PR | 獨立 Reviewer |
| 4 | CI | G3：各 repo 跑必要 checks | GitHub Actions |
| 4a | Implementer | 修正批次，最多 3 輪；每次新 push 都重新評估三個 gates | orchestrate 派工 |
| 5 | orchestrate＋controller | 核對三個 gates 在同一組版本通過，整理驗收包，貼成一則 ticket 留言；獲授權才張貼，否則交人張貼 | orchestrate；controller |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| PR | GitHub，每個受影響的 repo 一個 | 程式差異與說明 | 2 |
| gates 證據 | controller 保存（第一片實作中）；CI 結果在 GitHub | G1–G3 的結果與適用版本 | 1、3、4、5 |
| PR Pass 驗收包 | ticket 留言，連到每個 PR | 驗收人判斷需要的一切：這次交付的原因與範圍、每條 AC 的結果與證據、各 PR 的版本、風險與連結（完整欄位見[交接契約](../workflow/contracts.md#角色交接摘要)） | 5 |

**完成條件**

- [ ] 每個 repo 的 G1、G3 都在它 PR 目前的 head 通過
- [ ] G2 對整組 PR 的目前版本通過；任一 PR 有新 push，就重評整組 G2
- [ ] 驗收包每一欄都齊

Gates 的證據要求、review-fix loop 與 Blocked，見參考的[做出來：工程師的細節](reference.md#做出來工程師的細節)。

### B7 驗收、merge

**目的**：由人判斷結果是不是真的是要的。

**輸入**

- PR Pass 驗收包

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | 驗收人 | 讀驗收包、看 demo，逐條對照 AC | — |
| 2 | 驗收人 | 接受或退回（◆⑥）。AC 沒達成就退回修正；需求要改，回 Project Lead 更新 spec | — |
| 3 | Agent | 把接受或退回記成一則 ticket 留言；未獲授權就交給人貼 | skill 第 7 步 |
| 4 | 人 | 只有接受、且版本仍適用時才 merge；多個 PR 依依賴順序、提供方先 | GitHub |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| 接受或退回紀錄 | ticket 留言 | 誰、何時、原話、理由、對應的版本 | 3 |
| merge | GitHub | — | 4 |

**完成條件**

- [ ] 每條 AC 都有證據
- [ ] PR Pass、接受、merge 分開記錄

### B8 收尾

**目的**：把做完的需求變成系統現況，並用這次的經驗調整後面的計畫。

**輸入**

- 接受紀錄（步驟 1、2 在接受後就做）
- 這個 Feature 的所有 PR 都已 merge（步驟 3 才需要）

**步驟**

| # | 誰 | 做什麼 | 用什麼 |
| --- | --- | --- | --- |
| 1 | Agent | 接受後，整理 1–3 個有證據的 Retro 候選，貼成一則 ticket 留言；未獲授權就交給人貼 | skill 第 7 步 |
| 2 | Agent | 重看並更新 roadmap、檢查依賴，提出下一個 Feature 的候選（選擇在 B1） | skill 第 7 步、第 5a 步 |
| 3 | Agent | 確認這個 Feature 的所有 PR 都已 merge 後，把 spec 併入現況 | skill 第 7 步；`openspec archive <id>` |

**產出**

| 產出 | 位置 | 內容 | 步驟 |
| --- | --- | --- | --- |
| Retro 候選 | ticket 留言 | 來源、原因、改善、owner、驗法 | 1 |
| roadmap 更新 | roadmap | 狀態與順序的調整 | 2 |
| 現況 spec | `openspec/specs/<能力>/spec.md` | 這次做完的需求 | 3 |
| 封存的 Feature 資料夾 | `openspec/changes/archive/<日期>-<id>/` | 原本的 proposal、spec、design、tasks | 3 |

**完成條件**

- [ ] `openspec/specs/` 與已 merge 的實作一致
- [ ] roadmap 已重看，下一個 Feature 的候選已提出

有依賴的 Feature 要等上游接受並 merge 後才開始實作。一個 goal 推進多個 Feature 的目標做法，見參考的[給一個 goal](reference.md#給一個-goal推進多個-feature)。

### C Milestone 驗收

待定：跨 Feature 的整合驗證怎麼控還在討論。Milestone 驗收不能把一串 PR 綠燈直接加總成完成。

## 用 cross-node-file-transfer 跟走一遍

這是後續演練路線，Feature 名稱與切法以示範專案確認的 roadmap 為準，本指南不另立產品 spec。示範專案分成 root repo `cross-node-root`（規劃、spec、ticket）與程式 repo `cross-node-file-transfer`（由 `repos.yaml` 拉進 `repos/`）。

1. **定方向、排順序（A1–A3）**：Project Lead 把 gigaxfer 的 `docs/spec.md` 依能力拆開，當作需求輸入並記錄來源版本，不放進 `openspec/specs/`；再整理 domain、設計、共用限制與 roadmap。人確認拆法與適用性。
2. **專案骨架（第一個 Feature）**：repo 骨架、CI 與工程規則。它沒有產品行為，但「乾淨 clone 能建置測試、PR 有必要 checks」可以單獨驗收，寫成工程能力（例如 `engineering-baseline`）的 spec，常稱 Sprint 0 或 bootstrap。在 orchestrate 可用前可以手動協調，歷程標明「人工協調」，再由人驗收。
3. **交付第一個產品 Feature（B1–B6）**：Project Lead 準備 spec 與交接包，工程師帶 Implementer 完成 PR；另一個 session 的 Reviewer 審查。
4. **驗證修正循環**：有真實 blocking finding 時，留下 finding → fix → re-review 的歷程。review 沒找到問題就如實記錄，不製造缺陷湊演示。
5. **驗收與收尾（B7–B8）**：人驗收後，Project Lead 整理 Retro 候選、提出下一個 Feature；確認 merge 後再把 spec 併入現況。
6. **接續下一個 Feature**：核對依賴、人工接受、merge 與基準；保存各 Feature 的 branch／worktree、文件與交付證據。
7. **展示 Milestone（C）**：執行跨 Feature 的整合情境。真正的 stacked PR 展示，要等 stacked PR 的規則決定、能力驗證之後再加入。

Demo 結束時，觀眾應能沿一條路徑找到：「目標 → Milestone → Feature／AC → design／tasks → worktree／PR → TDD／review／CI → 人的決策 → 併入現況的 spec」。

## 現在做到哪裡

截至 2026-09-28。這份手冊描述的是預期流程；下方的開口句是預期的自然語言請求，還不是驗證過的指令。

- **已有**：兩層 workflow 與交接設計、spec 的位置與格式、兩個 skill 的分工、工作三層、需求放置、角色與手動階段的紀錄位置；`project-lead` skill 草稿。
- **實作中**：薄 controller 第一片的 design＋plan 已核准並合進 main，正在 `delivery/thin-controller` 分支依 tasks 實作；它只管單一 Feature。
- **進行中**：cross-node-file-transfer 的 Project 層先用 project-lead skill 做，不等 orchestrate；專案骨架可手動並標明人工協調，第一個產品 Feature 等 orchestrate 可用。
- **尚未完成**：orchestrate 與 controller 的完整 loop、project-lead skill 的實際演練、cross-node-file-transfer 的多 Feature 演練、跨人驗證與 stacked gating。

設計核准與 skill 草稿都不代表已驗收。

## 想知道為什麼

本手冊只說怎麼做。規則本身、設計理由與取捨在內部設計文件：[決策紀錄](../decisions.md)、[交接契約](../workflow/contracts.md)、[流程設計](../workflow/overview.md)、[SA 階段契約](../workflow/project-lead-sa.md)；追實作讀[最新 handoff](../handoffs/2026-09-27-controller-design.md)。手冊和它們有出入時，以設計文件為準。

| 主題 | 依據 |
| --- | --- |
| 兩個 skill、控制只往下走 | D55 |
| spec 放在 OpenSpec；需求依狀態放置 | D54、D58 |
| 工作三層、Feature 的定義、每個 task 局部 review、小工作 | D57 |
| 角色是工作；兼任時 SA 確認併入開工確認 | D59 |
| 手動階段的交付紀錄放 ticket 留言 | D60 |
| 多 repo 的 root 結構與跨 repo 的 Feature | D61 |
| 有依賴的 Feature 等上游接受並 merge | D27 |
| 示範專案的 Project 層先行 | D56 |
| 薄 controller 第一片的核准 | D53 |
