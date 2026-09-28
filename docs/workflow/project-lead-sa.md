# Project Lead：Research 與 SA 階段契約

日期：2026-09-27。來源：使用者提供的 Project Lead prompt，以及要求納入 workflow 的「更新？」。D34 確認本階段方法與交接；Q-METHOD 的工具組合仍待比較與試用。本文是 [workflow-design.md](overview.md) 的階段 reference，也是 [project-lead skill](../../skills/project-lead/SKILL.md) 要遵守的契約（D55）；skill 是執行程序，規則以本文與決策紀錄為準。它不是已批准的產品 implementation plan。

## 何時使用與工作邊界

準備 project 需求、準備選定 feature，或因新證據需要重新分析需求時，使用者以 project-lead skill 進入本階段（D55）；orchestrate 只跑單一 feature loop，不呼叫 Project Lead。先辨識本次層級、初始意圖與上游依據：

| 層級 | 輸入 | 分析深度與下一步 |
| --- | --- | --- |
| Project | 初始問題／希望改善的結果、已知限制、repo 與既有需求／設計 | 形成專案目標、責任邊界、核心情境與共用需求；足以進入 high-level design，再安排 roadmap／milestones 與 feature 候選，不預先細化所有 features |
| Feature | 選定的 feature、所屬 milestone、適用 project baseline、既有設計限制與依賴 | 聚焦本次可獨立驗收切片，形成行為、重要例外及 AC；必要高層設計由 Project Lead 補足，再交 Implementer 做 detailed design／plan |

SA 是分析活動，Spec 是分析成果；不要求各自建立一份重複文件。Roadmap 是專案交付路徑，milestone 是其中可驗證的成果節點，feature 是達成果所需的可交付能力。順序為足夠的 project SA → high-level design → roadmap／milestones → 選定 feature 的聚焦 SA／spec；相關活動可依新證據迭代，不把未完成的全部 feature specs 當成排 roadmap 的前置條件。

本階段研究需求、釐清系統責任與業務規則、協助關鍵決策、更新領域語言並整理 Spec。Detailed design、implementation plan 與產品程式碼修改屬後續階段。需求成立與否依賴技術可行性時可查證；需要 prototype 或變更環境時，先提出驗證目的與範圍，依適用授權處理，不默默擴張工作。

既有可信成果先核對來源、版本及適用性後引用；只補查差異與未知。依 D33 匯入既有專案時，保留原未決事項與可追溯來源，避免重做已確認需求的完整 grill；舊實作的測試結果不成為新實作的驗收證據。

## 執行步驟

### 1. 確認意圖與適用規範

讀取 repository 的 AGENTS.md／其他工作規範、相關需求、CONTEXT.md、存在時的 Context Map 與適用 ADR。記錄本次 project／feature 層級、repo 與適用上游來源的位置及版本；milestone／feature 身份在該層級適用時才填寫。

初始意圖已存在時直接研究；尚未提供時，先詢問要解決的問題與希望改善的結果。不要因本契約被引用，就把其他專案或示例 prompt 當成當前任務。

查明本機 grill-with-docs 及其依賴的 grilling／domain-modeling 是否可用，核對真實指令與觸發限制。有適用 skill 就依契約使用；缺少時說明並依本階段方法繼續，不假稱已執行。使用者的範圍、互動節奏與交付要求優先；不為湊齊 SA 而串接全部 skills。

完成條件：本次意圖、分析層級與可用來源可辨識；阻擋性缺口已明列。

### 2. 先研究，再依決策需要深入

使用者於 2026-09-28 指定 codebase 研究採 [HumanLayer 衍生的 research-codebase skill](../../skills/research-codebase/SKILL.md)；[來源版本與適配](../../skills/research-codebase/references/source.md) 隨 skill 保存。它先記錄現況、程式依據與限制，研究結果再供本階段的 SA／domain／grill 使用；不由研究工具直接決定未來需求或批准 Spec。本機已安裝 skill，不代表 orchestrate 接合或 example 演練已通過。

追查與目標相關的流程及上下游，不要求全 repo 盤點。關注角色／觸發、主要與例外流程、模組與系統責任、外部依賴、核心資料／狀態／介面／資料來源、業務規則／權限／限制，以及相關測試、既有能力與缺口。

現況結論附上可追溯的檔案路徑、symbol、測試或文件依據，分清已查證事實、推論／未驗證假設、未來需求／建議。程式碼代表實際行為，不自動代表正確需求；code、文件與使用者描述衝突時呈現差異，交由相應決策者確認。

先提供足以展開討論的摘要，再按待決問題補查；不等所有研究完成才互動。完成條件：下一輪需求決策已有依據，查不到的部分與其影響清楚。

### 3. 漸進 grill，持續保存共識

- 能從 codebase／文件查證的事項自行查；需要業務判斷與取捨才問使用者。
- 按影響與依賴排序，先目標、scope、系統責任、核心情境及影響驗收的問題，再問其依賴細節。
- 每輪問 1–3 個相關問題，說明現在需要決定的原因、選項、主要影響與建議，等回答後再展開依賴該決策的下一輪。
- 暫時無法回答時，列出能否延後、阻擋哪些工作及可用查證方法；不受影響的研究可繼續。
- 每輪更新對應文件，簡述重要變更與剩餘阻擋；已確認內容不重問，新證據推翻前提才說明原因重新確認。
- 沉默不代表同意；建議、假設與未決事項保持明確狀態，不能寫成共識或填入未經同意的量化目標。

完成條件：關鍵選擇有可追溯的決定，或有明列影響的待決事項；無隱藏假設。

### 4. 維護共同領域語言

優先更新既有 CONTEXT.md／詞彙表；沒有時從本次核心概念建立。保留領域名稱與簡介、標準用語與簡短定義、易混淆用語、必要概念區別及適用範圍。

用具體情境與邊界案例釐清模糊概念，再與 codebase 交叉核對，不只整理縮寫。已確認定義即時記錄並用於後續 Spec；未確認定義留在待決事項。修改共用定義前確認對其他使用情境的影響；同名異義保留領域邊界，必要時才拆 Context 與 Context Map。

CONTEXT.md 只保存可跨需求沿用的領域語言；本次需求、研究證據、工作進度與實作決策保存於相應文件。完成條件：核心用語足以支持本次需求討論，未決語意有明確標示。

### 5. 整理 SA／Spec 的七項內容

依 repo 慣例更新唯一權威 Spec；七項是內容要求，不強制七個檔案或固定七章。情境、規則與 AC 互相引用，不維護多份重複清單。

| 內容 | 必須能回答 |
| --- | --- |
| 問題與目標 | 為誰解決什麼問題、現況痛點、希望改善與業務成功條件；無依據的量化目標標待確認 |
| 範圍與非範圍 | 涵蓋與明確排除的能力／情境，以及與既有系統的責任分界 |
| 角色與端到端情境 | 誰在什麼前提下、為何觸發、經哪些作業到什麼結果；包含必要的系統自動觸發 |
| 功能行為與業務規則 | 可觀察的輸入輸出、狀態轉換、權限、判斷規則與資料責任；不提前綁內部實作 |
| 例外與必要限制 | 相關的缺資料、重複、逾時、部分失敗；效能、相容性、安全、可靠性、稽核與不可破壞的既有行為 |
| 驗收條件 | 在哪些前提、操作／事件下，得到何種可觀察結果；涵蓋主流程與重要例外，可對回需求。分開記功能符合要求與業務改善達成 |
| 假設、依賴與待決事項 | 已確認與未確認內容、依賴系統／角色、影響、是否阻擋 Design，以及預定解決階段 |

七項放進四個位置（D54，採 OpenSpec）：

| 位置 | 七項中的哪幾項 | Project 層 | Feature 層 |
| --- | --- | --- | --- |
| Why | 問題與目標 | project intent／mission | change 的 `proposal.md` `## Why` |
| Scope | 範圍與非範圍 | project intent／mission | `proposal.md` `## What Changes` 加「不做」 |
| Requirements | 角色與情境、行為與規則、例外與限制、驗收條件 | `openspec/specs/<能力>/spec.md` | change 的 `specs/<能力>/spec.md` delta |
| Open items | 假設、依賴與待決 | 決策紀錄／project intent | `proposal.md` 的待決與依賴 |

- **能力的切法**：一個能力是一組會一起改變的行為，不是元件、頁面或 feature。一個 feature 可改多個能力；跨 feature 的共用限制自成一個能力。既有專案先沿用現有章節切法，只拆開明顯混雜的部分，並保存「原章節 → 能力」對照與來源版本。
- **ID**：需求 ID 每個能力一個前綴，Scenario 是帶 ID 的 AC；用過不重用，archive 後不變。
- **非範圍與待決歸 Project Lead**：寫在 proposal，不放 Implementer 負責的 `design.md`。
- **格式檢查**：以 `openspec validate` 檢查；內容是否正確由人與 Reviewer 判斷。

Project SA 以共用契約與近期成果為尺度，不強制產出所有未來 features 的詳細 AC；Feature SA 對本次關鍵需求提供穩定需求／AC ID、可觀察通過條件與對應關係。沿 D19，design／plan 再補具體驗法、環境、任務與證據位置，執行後才填實證；SA 文件完成不代表驗證已通過。

內容深度依本次需求調整；不為填滿章節新增功能。必要技術限制可引用適用設計／ADR；未決方案留到 Design 分析，不由規格整理工具補定。

## 完成、確認與交接

Project Lead 在以下條件成立後，提出「SA 可進入 Design」的判斷及理由，由使用者確認：

1. 問題、目標、範圍與系統責任已形成共識。
2. 核心領域用語沒有影響需求理解的歧義。
3. 主要情境、關鍵規則與重要例外足以支持本層級的設計。
4. 關鍵需求有對應可驗收條件；project 層不要求所有未來 feature 的細節。
5. 沒有會改變核心 scope、行為或驗收的阻擋性未決事項。
6. 可延後問題已列明影響、後續處理階段與承接者。

確認時，Project Lead 給使用者一頁照意思排列的摘要，每項附位置連結與版本；使用者讀摘要，不必逐一打開檔案：

```text
目標：……                          → proposal.md#why
不做：……                          → proposal.md
規則：ING-01 ……、ING-02 ……        → specs/<能力>/spec.md
例外：AC-I03 ……、AC-I04 ……
待決：Q1 ……（阻擋 Design，等你決定）
版本：<commit 或檔案 hash>
```

確認紀錄寫明誰、何時、原話與確認的版本：feature 記在 proposal 的簡短區段，project 記在決策紀錄。

不必決定全部實作細節，也不以七章填滿作為完成證明。保存判斷與使用者對適用版本的確認；這是需求階段交接，不能取代 D11 的 feature design＋plan 一次開工確認，不增加逐文件／逐 task 簽核。已有適用的 SA 成果及確認時沿用；新證據改變其核心需求才重新釐清。

交接摘要至少包含：

- 分析層級、repo／project 身份與適用上游 baseline references；feature 交接另含 feature 身份及所屬 milestone。
- 已確認 scope、需求／AC IDs、實際 Spec／CONTEXT／research／必要設計的位置、版本及來源。
- 已確認決策、可延後問題、依賴與剩餘 blockers；每個未決項列影響及下一位 owner。
- SA readiness 的理由、使用者確認來源與適用版本、下一階段及負責人。

Project SA 交 Project Lead 進行 high-level design 與 roadmap；Feature SA 完成後，Project Lead 補齊必要高層設計邊界，再交 Implementer 做 detailed design／最終 tasks。需人判斷的範圍／AC／架構變更沿 D11 回人。

若有阻擋，回報原因、證據、受影響工作、需人的具體決定或最小恢復條件及可繼續的部分；未讀到來源或查證失敗時列限制，不宣告完成。機器欄位與儲存方式仍由 [workflow-contracts.md](contracts.md) 的實作設計決定。

## Roadmap 怎麼規劃

Roadmap 是持續演化的文件：milestone 是可展示的成果節點，feature 是達成它的交付能力，切片是一個可獨立驗收、對應一個 PR 的交付單位。業界做法與出處見 [Roadmap 規劃參考](../references/roadmap-planning.md)。

「切細」有三個層次，成本差很多，只有第一層可以提早做：

| 層次 | 內容 | 何時做 |
| --- | --- | --- |
| Roadmap 切片 | 名稱、一句範圍、依賴 | 當前 milestone 有依據時可以整個切完；沒有依據時先停在 feature |
| Feature spec | Proposal、spec delta、帶 ID 的 AC | 只做接下來 1–2 片 |
| 詳細設計與 plan | Design、tasks | 開工前，由 Implementer 做 |

- **狀態**：每個切片標「近期」或「暫定」。近期是接下來要寫 spec 的 1–2 片；暫定只有名稱、範圍和依賴，不寫 spec。暫定升為近期，就開始該片的 SA；SA 確認並備妥交接包，才算可以交給 feature loop。
- **切多細的依據**：切法有依據（例如既有實作、穩定的設計），而且需要全貌來規劃平行、依賴或 demo 時，當前 milestone 可以整個切到切片層。內容要看前面的結果才知道、設計還不確定，或牽涉未決政策時，保持在 feature 層。後面的 milestone 只列 feature。
- **何時重切**：每個切片驗收後（和 Retro 一起）、寫 spec 時發現切片太大、依賴改變，以及進入新的 milestone。
- **紀錄**：小調整靠 git 歷史；改變範圍、順序或 milestone 的調整，記進決策紀錄並經使用者確認。

## 文件與決策分工

| 內容 | 權威位置 |
| --- | --- |
| 跨需求的共同用語 | CONTEXT.md／適用領域 context |
| 現況、程式依據、差異與查證限制 | Research 文件 |
| 本次需求、已確認業務規則、AC 與待決事項 | Spec 的實際 binding |
| 後續技術設計及重要取捨 | Design；需要持久取捨理由時才 ADR |
| 交付路徑、milestone 成果與 feature 順序 | Roadmap 的實際 binding |

需求決定直接更新 Spec，不為每個回答建立 ADR。既有 ADR 是研究依據；若需重評，先保存原因與影響，交 Design 處理。優先更新既有文件，不強制改名或平行保存同義版本。

## 工具接合

依 D55，本階段由 [project-lead skill](../../skills/project-lead/SKILL.md) 執行，它按需叫用以下工具；工具提供方法與格式，不替代人的需求決策：

- **研究**：[research-codebase](../../skills/research-codebase/SKILL.md)，使用者於 2026-09-28 指定。
- **grill 與領域語言**：Matt 的 grill-with-docs、grilling、domain-modeling，按實際可用版本使用。
- **Spec**：依 D54 採 OpenSpec。Project Lead 寫 proposal 與 spec delta；Implementer 在同一個 change 接續 detailed design 與 tasks，不複製一份 spec 或 plan。不能因工具能一次產出全部 artifacts，就越過 Implementer 的詳細設計責任，或把 artifacts 存在當成確認。
- **收尾**：人工接受並 merge 後以 OpenSpec archive 把 delta 併回 `openspec/specs/`；Retro 候選由 project-lead 整理（D55 修訂 D28）。
- Matt to-spec 保留為比較候選，不是預設步驟。Writing Plans 與 OpenSpec tasks 的接合仍屬 Q-METHOD；D26 的 Superpowers TDD 與三 gates 不因此重開。

project-lead skill 目前是草稿，尚未實際演練。
