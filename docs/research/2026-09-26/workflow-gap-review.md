# Project / Feature 流程對照與 MVP 取捨

日期：2026-09-26。本文承接使用者提供的 [SDD 課程整理](../../references/spec-driven-development-workflow.md) 與我們的 [流程草案](../../workflow/history/orchestrate-workflow-draft.md)、[需求基線](../../project-intent.md)、[決策](../../decisions.md)、[檔案狀態設計](../../harness/history/file-state.md)。2026-09-27 歸入有日期的研究資料，原有比較內容保留。

## 更正比較的定位

先前將七項候選一律稱為「缺口」，混合了三件不同的事：課程沒有展開的細節、我們已要求的自動化能力、以及可選的流程治理。七項不全是必做工作，更不是課程不完整的證明。課程本來著重輕量的人機溝通、文件上下文與迭代；本文依使用者提供內容比較，未直接查看影片。

本專案已有明確的多 agent 交付目標，因此保留必要的 controller 驗證；這不等於要增加人為簽核、固定文件數量或企業級流程。下列輕量方案原為修訂後建議；使用者現已透過 D19 確認三項優先內容：AC 行為定義、AC → 驗證證據，以及文件位置與版本交接。其餘建議仍未自動定案。

## 三種來源分開處理

| 分類 | 內容 | 對 MVP 的意義 |
| --- | --- | --- |
| 課程提供的方法 | 訪談、憲章、feature plan / requirements / validation、人工 review、changelog、MVP 實驗、replanning | 值得沿用的人機工作方式；對應既有角色，不必照搬全部檔名 |
| 使用者已確認的要求 | 三 gates、歷史 TDD 證據、獨立 Codex review、版本綁定、finding closure、JSON/YAML 狀態、重試/預算、review/fix/re-review、PR Pass 終點 | 仍是必要需求，不能以簡化流程為由拿掉；多數查證工作由 helper/controller 處理 |
| 助理提出的額外治理 | 新 project-ready 人工 gate、逐 AC 量化治理矩陣、正式退回表單、milestone 額外簽收角色、每次 no-change 簽核 | 不列為預設 MVP；改用下表必要的輕量交接 |

## 七項建議如何縮到必要程度

D19 的已確認內容以 [流程設計](../../workflow/history/orchestrate-workflow-draft.md#已確認的優先設計ac驗證與交接) 為準，涵蓋 W01 的文件/版本入口與 W02 的輕量驗證對照；W03 的 AC 變更裁決沿用 D11。D21 確認加入 Retro，D28 確認人工驗收後自動整理改善候選，具體接入提案見 [Retro 設計](../../workflow/history/orchestrate-workflow-draft.md#retro-接入設計建議)。這不代表整張 W01–W07 表均已批准。

| ID / 階段 | 課程已涵蓋 | 修訂後的輕量建議 | 不增設的程序 |
| --- | --- | --- | --- |
| W01 Project 準備 | 憲章、人審、commit、重新載入 context | 保存 repo/worktree、適用文件與版本的入口；agent 自行讀取並指出真正缺失或衝突 | 不加獨立 Project-ready 人工簽核；使用者已有一次 project 基礎討論 |
| W02 Feature 規劃 | plan / requirements / validation 整體確認 | AC 保留可判定的驗證方式、結果與 evidence links，併入原本 design + plan 確認；必要環境依 feature 決定 | 不另開 scorecard approval gate，不要求所有成功標準數值化，也不強制單獨一檔 |
| W03 人工驗收 | 人看 diff 並要求修正 | Implementer Agent 預設接回修正；涉及 scope/spec/AC 或設計爭議時，沿既有 D11 回你與 Project Lead Agent 決定 | 不新增審批角色、退回表單；修程式不自動授權降低規格 |
| W04 文件收尾 | roadmap 更新、Changelog skill | 遵守 repo 慣例並更新實際受影響文件；PR summary 或既有 changelog 足以承載變更說明時直接沿用 | 不要求每次產生 README/migration/runbook 全套文件，也不替不適用文件開豁免流程 |
| W05 Phase 0 | 骨架、配置、啟動驗證 | 依專案型態留可執行 setup/build/test 指令與基本 smoke evidence；作為交付單位時仍遵守既有適用 gates | 不另做全面平台稽核；brownfield 只補當前需要的基礎 |
| W06 Milestone | 多 roadmap 項目的 MVP 實驗與驗證 | Roadmap 寫明 milestone 要展示的能力；你與既有 Project Lead Agent 檢查整合情境，依目標安排必要驗證 | 不新增簽收人或固定儀式；不因每個 PR 綠燈就宣稱整體能力已驗證 |
| W07 Replanning | feature 間更新憲章/roadmap/架構 | 有新知影響共用設計或後續順序時再修改；重大需求歧義當下回人。ADR 僅用於值得保留理由的決策 | 無變更不新增人工簽核、文件或分支；不要求每次開 ADR |

這份取捨不改變已確認的 scope/spec/AC 變更裁決規則。必要 AC 沒有證據仍不能 Pass；驗證結果、SHA 與 finding 的自動核對不需要使用者逐筆簽名。D19 採用的輕量驗證對照只是驗收方法與證據索引，不和 run state 各自決定 gate。

## 已有要求與真正的落地工作

- Project / feature / task 的語意角色、baseline + delta 的讀法、開工前一次人工確認已在文件中，不需要重複發明。
- G1/G2/G3、版本核對、恢復、通知去重與發布重試已有需求和設計，但尚未等於已實作或驗收。
- Skill/router 包裝、必要 helpers、runtime adapters、結構化交接和操作方式仍需實作。這些才是目前的具體落地工作。
- D24–D28 已收斂 finding 權威／發布、一次爭議覆核、TDD／非行為例外、相依 feature 與 Retro 觸發；CIT 依 D29 暫不處理。Runtime 選擇、必要 checks、timeout 與 active time 等需落入具體 design / plan；試用恢復前再確認 Q-TARGET。

## 已修正的實際文件不一致

先前舊藍圖仍寫「當前先做 PR 實驗」，已改成 D18「先完善流程與 skill，PR 試用暫緩」。README 已連到最新草案與參考。四個 delivery wrappers 與 router / references 都標為包裝候選，將在 implementation plan 選定一套實際結構。

P03 audit 中 validation 文件缺失是較早的快照；後續查檔已見其存在，文件已區分歷史與新觀察。這沒有改變任何 gate 結論。

人可直接編輯規格；讓 agent 編輯本身不能保證一致性。文件改動後，依實際語意與版本影響核對相關 plan、code 和 evidence，才是需要保留的行為。
