# Retro：使用者提供的雙影片整理與本機 skill 查核

收錄／查核日期：2026-09-26。這是來源紀錄與接入研究，不是影片全部主張的採納，也沒有執行任何另一個 session 的 Retro。

## 使用者提供的整理

使用者將微觀的執行品質回顧歸於 Matt Pocock，將宏觀的 SDD Replanning 歸於 Paul Everett。影片網址、原始逐字稿及完整版本尚未提供；以下僅摘要使用者所貼內容，本 agent 未觀看影片，不能把轉述當成已驗證原話。

| 層次 | 整理中的時點 | 主要主張與產物 |
| --- | --- | --- |
| Micro / Execution Retro | PR / task 審查後或每週 | 把重複 review 意見轉成測試、lint、模組改善、review 規範；改善 navigation、prompt 與工具成本 |
| Macro / Replanning | Feature、MVP、milestone 之間 | 以 replanning branch 更新 mission / tech / roadmap；封裝重複步驟為 skills；重新整理 context |

整理另主張 reviewer 專讀 coding-standards.md 並自行 commit 修正、CLI + skills 優於 MCP、feature 結束固定 clear，以及回顧能持續降低人的負擔。這些是來源觀點；效果要以實際再犯、誤報、修正與 review 成本觀察，不能保證人的負擔隨規模自動遞減。

## 本機 Matt retro 的實際契約

- 路徑：`/Users/johnson.chiang/.agents/skills/retro/SKILL.md`。
- 安裝 lock：`/Users/johnson.chiang/.agents/.skill-lock.json`，source 為 `mattpocock/skills`；updatedAt `2026-09-05T08:57:43.953Z`。`skillFolderHash` = `5831252c5e3692fa01645b0279ea5c444facec9d`，是安裝器資料夾 hash，不能當 Git commit 或 release version。
- 本次 SKILL.md SHA-256：`264f3330f1e2382af89610ed048ba0ed6d08883eb69f596a8f1df3f1e1a4c6a1`。本輪唯讀查核，未更新或安裝 skill。
- 呼叫限制：frontmatter `disable-model-invocation: true`；`agents/openai.yaml` 的 `allow_implicit_invocation: false`。不可由模型默默選用；這次設計接入不等於已執行該 skill。
- 輸入與步驟：先套用 writing-for-agents，讀使用者指定 session 的 primary sources（未指定時為當前 session）；檢查 navigation、自動檢查、coding standards、global AGENTS、tool economy、無效指令與資訊取得。
- 產出：按嚴重度呈現改善候選。沒有規定自動 commit fixes、修改全域設定、建立 follow-up issues、治理 project roadmap 或宣告改善已驗證。
- 原版推薦 `CODING_STANDARDS.md` 供 review 讀取、AGENTS / CLAUDE.md 少量導航，並假設 reviewer context 壓力較低。它的文件名大小寫與使用者整理不同，不能視為通用必備檔名；我們的 reviewer 仍需完整 spec / design / codebase context，而不只是 diff。

本機另有 `/Users/johnson.chiang/.claude/skills/gstack/retro/SKILL.md`，frontmatter version 2.0.0，描述為每週 commit history / work patterns / metrics 及趨勢回顧。本輪僅查看其 frontmatter / 開頭以辨識同名工具，未執行 preamble、更新、telemetry 或完整 skill。

## 我們的接入取捨

- 保留 Execution Retro 與 Replanning 的不同問題範圍，沿用既有 project / feature 控制權，沒有新增雙重派工 loop。
- 當前缺陷即時修正；feature 收尾整理可重用改善；真正涉及共用基準才 Replanning。Retro 不新增 G4。
- Reviewer Agent 獨立覆核，Implementer Agent 修正；實作必要規範對 implementer 可取得，完整 review 清單按需載入。
- 偏好可以驗證的最小改善，不把每個人類偏好升級為 blocker 或 lint。選定自動檢查要證明已知壞例失敗、有效例成功；抽象測試品質不保證能被一條 lint 規則全面辨識。
- 版本、未結 findings 與證據先保存，再按需要開 fresh session；CLI / MCP 與 branch / 檔名採實際 repo 能力和慣例。

具體提案：[Retro 接入設計](../workflow/history/orchestrate-workflow-draft.md#retro-接入設計建議)。政策確認來源：[decisions.md](../decisions.md)。

使用者後續補充的 Matt 演講完整主題摘要，另收錄於 [Fixing the PR Bottleneck](fixing-the-pr-bottleneck.md)，包含三層品質控制、依風險調整人工 review 與視覺化 PR 說明。該份來源也未獨立觀看查核。
