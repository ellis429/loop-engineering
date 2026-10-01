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
