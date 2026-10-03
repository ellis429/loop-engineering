# Orca 重新分析：Project Lead 的回答

| # | 問題 | 回答（原話） | 日期 |
| --- | --- | --- | --- |
| 1 | Feature 2 派工改用 Orca 嗎？ | 「改用 Orca」 | 2026-10-02 |
| 2 | Astra reviewer 用什麼跑？ | 先問派工方式；之後選「Codex」（Orca 直接指定模型與 effort，兩者都讀得回） | 2026-10-02 |
| 3 | 派工方式：一個 session 一直用，或每個 task 新 session？ | 問了好壞，提出「同一個 session 一直用，但 engineer 換新 feature 時 clear 一次？」 | 2026-10-02 |
| 4 | engineer 什麼時候 clear？ | 「Feature 2 實驗兩種」（每個 task 前 clear 與每個 Feature 前 clear 各用一半，比較壓縮次數與 finding 數） | 2026-10-02 |
| 5 | 協調權以誰為準？ | 問「有必要鎖嗎」「由人操控，有矛盾時告知讓人處理，會不會不一定要實現鎖」「確定這是改動最小又實作成本最小嗎」；最後選最小組合「採用」：Feature 1 的 token 不改；Feature 2 不加鎖、不比對 Orca binding，Orca 回 `consumer_fenced` 就停下交人 | 2026-10-02 |
| 6 | 人工決策從哪裡輸入？ | 「decide 為準，Orca gate 只當提示」 | 2026-10-02 |
| 7 | Orca 的版本更新怎麼處理？ | 「照常更新，版本變了就重跑 preflight」 | 2026-10-02 |
| 8 | 照摘要記成 D76 並開 PR？ | 「照這份」 | 2026-10-02 |

工作區：固定名稱的 Orca 工作區 `engineer`、`reviewer`；派工送進該工作區（`worker-start --terminal` 或 `--worktree name:`）。

## 本日目標（2026-10-02）

| # | 問題 | 回答（原話） |
| --- | --- | --- |
| D1 | Feature 2 要縮成只登記嘗試與匯入結果嗎？ | 「我想先看一下現在規劃的流程 人會 by feature 派下去 也可能寫一個本日目標 裡面包含多個 feature，會產生 stacked pr」 |
| D2 | 本日目標跑的時候你在不在？ | 「常不在，要能自己跑完」→ 預算、逾時、卡住自動停下留在 M1；Feature 2 不縮小 |
| D3 | 多個 Feature 的開工確認怎麼做？ | 「先把計畫都寫好，你一次確認」 |
| D4 | 上游改了下游怎麼辦？ | 「feature 應該只會跑沒有 dependency 的」；確認「對」：互不依賴、各自從 main 開、並行、各自 PR，不需要 stacked；D27 不改，Q-STACK 維持 M2 |
| D5 | 同時跑還是依序？ | 先問「PR 應該還是人來決定？」（是：merge 一律由人）；之後「同時跑，設上限」：merge 一個後其他 PR 自動更新 base 並重跑檢查，衝突才停 |
| D6 | 本日目標放在 roadmap 哪裡？ | 「M1 最後一個 Feature」 |
| D7 | 只有 OpenCode 的環境（有 Orca）放在哪裡？ | 先說明「我有兩個環境 一個只有 opencode 一個就是我現在有 claude/codex」、「有 Orca」；選「M1 裡另切一個小 Feature」（放在 Feature 2 之後） |
| D8 | 照摘要記成 D77、重切 M1？ | 「照這份」 |
