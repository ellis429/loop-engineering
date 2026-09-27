# 本次擬採用與 D11 開工範圍

狀態：供使用者確認；沒有把前一輪「All ok」擴張成開工授權。前一輪僅批准 D47–D49 的三項政策。

## 擬採用的文件

- [Spec 修改提案](spec-delta.md)：四份既有 OpenSpec specs 的責任與政策修訂，保留 88 AC。
- [Design](design.md)、[H1 tasks](tasks.md)、[Validation](validation.md)、[Coverage](coverage.md)、[Cleanup](cleanup-map.md)。
- [獨立文件 review](review.md)：H1 候選沒有未解阻擋；所有驗證案例仍是 planned。

## 本次實作

1. 依 W1 接回同 repo 的 `delivery/thin-controller` worktree，保留現有候選文件；新樹移除舊產品樹，只提取確認可用的程式與必要行為測試，原 branch／PR／歷史保持可查。
2. Python 3.12、uv、pytest、ruff、mypy、PyYAML；唯一 CLI `loopctl`。完成 H1 核心狀態、交接、三 gates 判定、finding／修正路由、預算與有限次外部工具接合；fake 外部程式＋真 git 驗證。
3. Opus 5.5 實作，獨立 GPT Reviewer 審查；協作者 bootstrap 協調本身的 PR，留下原始 Red、目前 Green、review、真實 CI 證據。未自動 merge／close／release／deploy。
4. 有界讀回最多 3 次（含 in_progress），不確定就保存並交人。Worker／review／CI timeout 候選為 45／30／30 分鐘；4h active、3 輪修正、每個 infra 操作額外 2 次重試依既定政策。

## 擬核准的 CI 集合

`.github/workflows/loopctl-ci.yml`，app `github-actions`；必要 jobs 為 `unit-linux`、`unit-macos`、`static`。Static 包含 lint/type/cleanliness、build wheel、全新環境安裝後從 source tree 外執行 CLI。沒有 skipped／neutral 例外。

PR 使用明確 head checkout，push 使用該次 pushed SHA；核對實際受測 SHA、check-run／workflow 關係，不將 merge snapshot 靜默標成 head。採用後保存版本綁定的人工 policy decision；G3／Pass package 明示 GitHub rules 未核對。完整條件見 validation §4。

## 保留界線

- H1 的本身 PR 可依真實 bootstrap 證據判 gates；fake 成功不代表產品自動 loop 已完成。
- H2 真實 runtime／權限／GitHub 接合與 E2E、H3 example project 仍是 outline，後續補可派工計畫，不由本次批准自動開工。
- 舊 S1 17 findings 仍 open，需新程式、適用證據与 Reviewer 明確覆核；不因重建或文件 review 而關閉。
- 不改 gigaxfer，不初始化 cross-node-file-transfer。本目錄目前仍是純目錄，W1 尚未執行。
