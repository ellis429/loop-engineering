# Validation：第一個可用切片（D50 候選 design-03；revision-07）

> **全部是 planned，沒有任何項目已執行，也沒有 gate 結論。**
> - 每個 ID 的處置以 [coverage.md](coverage.md) 為準；check 集合待 D11 與人工核准。
> - fake 證據不改標為 real；B1 不等於自我託管。
> - 附證據的 Blocked 不算示範完成。

## 1. 環境

| 代號 | 內容 |
| --- | --- |
| ENV-F | 本機 macOS＋Linux CI、Python 3.12（uv）、真 git；PATH 上放 fake `herdr`／`gh` |
| ENV-R | Herdr 0.9.1、Claude Code（Opus 5.5 Implementer）、OpenCode（Reviewer；model 待 D11） |
| ENV-GH | `yschiang/loop-engineering` 的 PR／issue／Actions |

## 2. 第一片情境（ENV-F）

- **門檻**：failure、error、skipped 都是 0；外部呼叫次數依表中斷言。
- **證據**：`.delivery/bootstrap/thin-s1/evidence/<task>/` 加上 CI junit。

| ID | 命令 | 必須觀察到的結果 |
| --- | --- | --- |
| V1 | `uv run pytest tests/test_cli.py tests/test_preflight.py -q && scripts/dist-smoke.sh` | 未知 feature 回 exit 5；缺項 profile 為 unverified；安裝後的 wheel 在 checkout 外可用 |
| V2 | `uv run pytest tests/test_state.py -q` | 中斷後不重複生效；手改回 exit 5；同時提交或 claim 恰一方成功 |
| V3 | `uv run pytest tests/test_decisions.py -q` | 草案 plan 或沉默不構成批准；scope_change 不 crash；adopt／delegate 回 `unsupported` |
| V4 | `uv run pytest tests/test_writes.py -q` | 同時寫入時外部呼叫 1 次；延後生效或查無 → unknown＋Blocked、0 次重送；第 4 次讀回被拒（含「仍在執行」）；前一個 writer 未確認結束時 0 次派工；argv 或 scope 不符 → 拒收 |
| V5 | `uv run pytest tests/test_g1.py -q` | 任意 argv 未被執行；各種 Red 污染各自無效；**正常路徑不做 replay 也 G1 passed**；**矛盾路徑觸發 replay 作診斷，失敗 → Blocked**；缺 Red → fail；整合失敗 → `pre_review_g1`，且在 G1 通過前 0 次 G2 |
| V6 | `uv run pytest tests/test_review.py -q` | 只有完整範圍、目前版本、`clean` 且沒有 blocking 時 G2 才 passed；`changes_required` → failed；`blocked` → unknown，不開修正輪；缺 verdict、只審部分 diff → 不 passed；文件缺陷 → fix → 獨立 re-review；第 4 輪為 0；reopen → Blocked |
| V7 | `uv run pytest tests/test_observe.py -q` | `seq` 在 fetch 之前就持久化；**亂序完成**：`seq=1` 的 H1 晚到，只存歷史，不能恢復 H1；**新 head**：以 H1 發出的請求看到 H2，仍會讓 H1 的 gates 失效；**跨 purpose**：`pass` 的觀察（`seq=10`，H1）在 `pr` 的觀察（`seq=11`，H2）之後才到 → head 維持 H2，Pass 不成立；pending→pending→success；`tested-sha≠H` 不計入；403 且沒有政策 → Blocked |
| V8 | `uv run pytest tests/test_publish_pass.py -q` | 發布順序；發布 unknown 時 0 次重貼；有新 push → Pass 失效 |
| V9 | `uv run pytest tests/test_budget.py -q` | 到期 stop 優先；已 prepared 的 stop 送出 1 次；離線超時 → Blocked；unknown 不算已停止 |

V7 與 V9 必須在 R2 之前通過（D50-R01）。

## 3. 真實證據與界線

| ID | 內容 | 前置 | 通過標準 | 證據 |
| --- | --- | --- | --- | --- |
| R1 | 兩個 role 的正式 profile preflight（受限的能力 probe） | V1 | model、marker 讀回一致；負例全部被拒；stop 確認停止 | `docs/validation/s1/preflight/` |
| R2 | 隔離的真實能力 probe：在 `probe/s1-g1` branch 上用 fixture task 跑到 G1。不是交付 feature，不 merge | R1、V5、V7、V9 | G1 依證據判定，或附證據 Blocked。只算能力證據 | `docs/validation/s1/probe/` |
| R3 | 第一個有用的交付：bounded feature 走完 review→fix→re-review，途中中斷一次 | B1 已 accepted、已 merge、baseline 已登記（D27、tasks 8.0） | **完成條件**：真實 finding→fix→re-review、三 gates 在目前版本都通過、中斷後成功接續。附證據的 Blocked 是安全停止，但 R3 維持未完成；沒有真實 finding → 維持 open | PR、issue、CI URL、狀態 export |

- **Bounded feature 候選**（待 D11）：`loopctl status --human`（AC-D01）。
- **未覆蓋**：OpenCode-only、公司環境、adopt、跨 feature 自動化、Project／Retro 自動化、平行 worktree（S2／S3）。

## 4. D49 CI 候選（未核准）

- **Workflow**：由 tasks 1.1 建立 `.github/workflows/loopctl-ci.yml`，名稱 `loopctl-ci`，app `github-actions`，`source: head`。
- **必要 checks**：
  - `unit-linux`（ubuntu-24.04）與 `unit-macos`（macos-15）：`uv run pytest -q`；
  - `static`：`ruff`、`mypy`，以及 `scripts/dist-smoke.sh`。dist-smoke 會 `uv build`，在全新 venv 安裝 wheel，並在 checkout 外執行 `loopctl`。
- **Checkout**：
  - PR 事件 checkout `github.event.pull_request.head.sha`；push 事件 checkout `github.sha`；
  - 若 `git rev-parse HEAD` 與預期 SHA 不符，job 失敗；
  - 上傳 `tested-sha` 產物。
- **G3 計入條件**：check-run 的 `head_sha==H` 且 `tested-sha==H`。沒有例外：skipped／neutral 一律拒絕。
- **生效條件**：D11 核准這個集合，並記錄 `policy_change` 綁定。G3 與 Pass package 顯示 `github_rules_verified=false`。這份核准可以用於 B1。
