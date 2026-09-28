# Userflow：使用指南 review 與視覺化

任務 ID：`userflow-guide-review-20260928-01`。使用者要求交給既有 `userflow` session review，並 visualize 得更好懂。

交接狀態（2026-09-28）：已透過 Orca 將本任務送入既有 `userflow` session，確認訊息已提交、session 進入 Working，後續活動顯示正在尋找視覺化工具。這是接件證據，不代表 review 或指南修訂完成。

## 目的與輸入

讓首次接觸 Loop Engineering 的人，能從角色與目標找到下一步，並跟著 `cross-node-file-transfer` 範例理解兩層流程。主要輸入是 [使用指南](../workflow/user-guide.md)，規則依據是 [workflow](../workflow/overview.md)、[交接契約](../workflow/contracts.md)、[決策紀錄](../decisions.md) 及 [Project Lead SA](../workflow/project-lead-sa.md)。先讀實際文件，再 review，不沿用舊 session 的快照。

使用者希望看見：

1. 人有哪些角色，各自在 Project／Feature 層負責什麼；與 Agents 的差別。
2. Lead 如何完成 project level：research → SA／domain／grill → high-level design → roadmap／milestones。
3. Lead 如何把第一個 feature 的 spec、AC、依賴與版本交給工程師。
4. 工程師如何讓 Implementer 完成詳細設計、plan、TDD、PR，以及獨立 Reviewer／CI 的 review-fix loop，最後交人驗收。
5. 工程師給一個 goal 後產生 stacked PR 等人 review 的目標使用情境；清楚標示現行能力與待決政策。

## 可以修改與必須保留

直接改善 `docs/workflow/user-guide.md`；需要可互動示意時，可在 `docs/workflow/` 增加小型自包含視覺檔並由指南連結。同步入口連結限 `README.md`、`docs/README.md`。另留簡短 review 紀錄於 `docs/reviews/2026-09-28-userflow-guide-review.md`，包括實際發現、修正與未決問題。

用總覽加逐情境流程／泳道圖降低閱讀負擔；箭頭應表示觸發、交接物或退回原因。讓人看出誰決定、誰執行、何時需人介入。避免把 schema／內部狀態堆進主流程。按需使用可用的 visualize skill；靜態 Mermaid 足夠時不必另造網站。實際檢查圖的可讀性與連結。

保留：G1 先於送審；G2 與 G3 獨立且可並行；結果適用於最新版本；Reviewer 不直接修改被審 branch；PR Pass、人工接受與 merge 分開；每個 feature 一個協調 loop；Orca 選配、roles 不綁 runtime。現行 D27 與待決 Q-STACK 不可被示意圖默默改成已可用的 stacked gating。既有 D11 確認邊界照文件，不新增逐 task 簽核。

不要修改產品程式、tests、正式 OpenSpec、controller 候選或 gigaxfer。Herdr session 正在進行另一條 design／plan 工作；本任務是使用指南 review 與呈現，不接管其任務。

## 本輪工具補充

使用者已指定 `research-codebase` 來源為 [HumanLayer research_codebase](https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/research_codebase.md)，不是 Matt 的 research skill。Workflow builder 正在建立 `skills/research-codebase/SKILL.md` 並安裝本機；本任務可先進行指南 review，工具表在 skill 出現後核對。

此 skill 研究「目前如何運作」，研究輸出再供 SA／domain／grill 判斷需求；不把 research 當成批准的 spec 或未來 design。來源版本與可攜化差異將隨 skill 保存。Workflow builder 只同步 `project-lead-sa.md` 與 `docs/harness/overview.md` 的來源說明，`user-guide.md` 由本任務負責，避免同時寫入。

更新：`skills/research-codebase/SKILL.md` 已建立；本機 `~/.agents/skills`、`~/.codex/skills`、`~/.claude/skills` 的同名入口指向這份來源。Skill 格式、來源 hash、三個安裝入口及相關文件連結已檢查；尚未以真實研究任務驗證完整流程。工具表可據此標為已安裝、整合待驗。

## 完成回報

回報主要發現、已改的指南／視覺檔路徑、怎麼看、驗證方式，以及仍需使用者決定的事項。不要把文件呈現完成宣告成 controller 或 example 已驗收。開始時先簡短確認接件；完成後在本 session 回報並保存 review 紀錄。
