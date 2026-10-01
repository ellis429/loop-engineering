# Orca 作為 loopctl runtime 的查核

日期：2026-10-01。狀態：研究，只描述現況與證據，不設計 loopctl、不做決定。

- 對象：本機 Orca `1.4.215`（`/usr/local/bin/orca` → `/Applications/Orca.app/Contents/Resources/bin/orca`），build `1.4.215-3eb1adec20ff90503196ebfd1fe6dbaaefaad736-arm64`，daemon protocol 36（`Resources/orca-local-build.json`）。App 在執行中（`orca status --json`：`runtime.state: ready`）。
- 基準：loop-engineering `main@0ab55de`。Feature 1 design 讀自 `loop-engineering-run-decisions/openspec/changes/run-decisions/design.md`（進行中，唯讀）。
- 判定標記：
  - **實測**：本次執行命令或讀檔觀察到。
  - **文件**：Orca 隨版 skill（`orca skills get orchestration --full`）、`--help`、`orca agent-context --json` 的 schema notes，或官方 repo 文件。
  - **文件（原始碼）**：安裝版 bundle 的字串摘錄。是實作證據，但不是行為實測。
  - **未實測**：需要被禁止的命令，只能依文件。
  - **未知**：查不到，或原始碼未查完。
- 原始碼位置：`app.asar` 內的 `out/main/index.js`（minified；以 Python 解析 asar header 後讀到 scratchpad），以及 `app.asar.unpacked/out/cli/handlers/orchestration/*.js`。
- 既有研究：[2026-09-25 orca-capabilities](../2026-09-25/orca-capabilities.md)（1.4.209）、[2026-09-25 runtime-probe](../2026-09-25/runtime-probe.md)（當時真實跑過 `worker-start`）、[2026-09-27 planning-preflight](../2026-09-27/planning-preflight.md)（1.4.212）。本文只在版本已變或問題不同時重查；沿用的舊結論標明出處。

## 0. 探測紀錄與 scratch IDs

### 0.1 探測前狀態

| 項目 | 值 |
| --- | --- |
| 本 terminal | `ORCA_TERMINAL_HANDLE=term_1bf1a70d-64d0-4524-9edf-d46be8bc3470`。這是父 Claude Code session 所在的 Orca terminal。環境變數 `TERM_PROGRAM_VERSION=1.4.214`，app 已是 1.4.215（terminal 開啟後 app 升級過） |
| `orchestration run-current --json`（兩次，皆在建立之前） | `"result": {"run": null}`：本 terminal 沒有綁定任何 Run |
| `orchestration run-list --json` | `run_95da348b16c4`（2026-09-25 舊 probe，`coordinator_handle: term_f20fd678…`，`consumer_generation: 1`）與 `run_legacy_local`（`legacy: 1`） |

### 0.2 本次建立的物件（全部在 scratch Run 內）

| 種類 | ID | 備註 |
| --- | --- | --- |
| Run | `run_b6098d2f6bed` | objective `loopctl-research-probe-2026-10-01`，coordinator 為本 terminal，`consumer_generation: 1` |
| Task | `task_28f9f3d7de99` | 從未派工；目前 `ready` |
| Gate | `gate_db1fc9318fa0` | options `["approve","revise"]`；目前 `resolved`，resolution `approve` |
| Messages | `msg_0664f048923c`（send）、`msg_d774c86f5ecc`（reply）、`msg_5ec636c87b2e`（帶自訂 `--retry-request` 的 send） | 都寄到 `run:run_b6098d2f6bed` |
| Deliveries | `delivery_6729af63192f`（已 ack）、`delivery_94aeb4f4459b`（未 ack，保留） | — |
| Mutation request IDs | `5cfa731c…`（run-create）、`1733a424…`（task-create）、`b0e44897…`（gate-create）、`b9f55a2b…`、`cca76ebe…`（兩次 gate-resolve）、`641877ae…`（send）、`bc5a4060…`（reply）、`762ba2d9-98b9-4f10-8ce9-b8ebdccf947c`（自訂 UUID）、`1e2b9c83…`（被拒的 ask） | — |

### 0.3 探測後狀態

- 本 terminal 仍綁定 `run_b6098d2f6bed`（`run-current` 實測）。探測前是「未綁定」；`run-use` 只能綁到既有 Run，沒有解除綁定的命令，所以無法還原成 `null`。
- 之後在這個 terminal 不帶 `--run` 執行的 orchestration 命令，會落在這個 scratch Run。
- 只有建立新 Run（`run-create`）或 `run-use` 其他 Run，才會讓本 terminal 離開它；兩者都沒有執行。
- 沒有執行 `reset`、`worker-*` 的寫入命令、`dispatch`、`terminal send|close|create|split`、`worktree create|rm`，也沒有碰其他 Run。對 `run_95da348b16c4` 只做了 `run-show`、`task-list`、`gate-list`、`worker-list` 四個讀取。

## A. 持久化

| 問題 | 答案 | 證據 | 判定 |
| --- | --- | --- | --- |
| 存在哪裡 | 單一 SQLite 檔 `~/Library/Application Support/orca/orchestration.db`，WAL 模式（另有 `-wal`、`-shm`） | `file`：`SQLite 3.x database, user version 42`；`PRAGMA journal_mode` → `wal` | 實測 |
| 涵蓋哪些實體 | Run、Task、Dispatch、message、gate、delivery、問題串、worker 資源與 mutation receipt 全在同一個 DB | `.tables` 共 26 個，包括 `runs`、`run_coordinator_handles`、`tasks`、`dispatch_contexts`、`worker_dispatches`、`messages`、`deliveries`、`question_threads`、`decision_gates`、`mutation_receipts`、`worker_terminal_resources`、`worker_terminal_archives`、`attempt_observation_facts` | 實測 |
| 格式與可讀性 | 只能用 SQLite 讀，沒有 JSON／YAML 檔案。部分欄位內含 JSON 字串（`tasks.result`、`worker_dispatches.start_options`、`messages.payload`、`mutation_receipts.receipt`） | 用 `sqlite3 -readonly` 讀 DB 副本；例如 `tasks.result`：`{"provenance":"worker_report","outcome":"succeeded","messageId":…,"filesModified":[],"reportPath":null,"completedAt":…}` | 實測 |
| 不經 runtime 可讀嗎 | 檔案可以唯讀開啟，但 schema 是內部實作：`user_version 42`，版本間會 migration（例如 `dispatch_contexts` 的註解「Null on rows written before v37」） | DB schema 註解 | 實測 |
| 官方讀取介面 | CLI `--json`，需要 runtime 在跑 | `orca --help`：「Most commands require a running Orca runtime」 | 文件 |
| 跨 app 重啟與升級 | 保留。`run_95da348b16c4` 建於 2026-09-25（1.4.209）。目前 app 程序 2026-09-30 07:55 起跑（`SingletonLock`、`orca-runtime.json` 的 mtime），版本已到 1.4.215，`run-show`／`task-list` 仍讀得到該 Run 的 task 與 `worker_done` 結果 | `run-show --id run_95da348b16c4 --json` → `created_at: 2026-09-25T11:56:00Z`；`task-list` 有 `task_e3f33b44e673.status: completed` | 實測（間接：跨過重啟與升級，但沒有做受控重啟） |
| Worker 程序跨重啟 | 一般 quit、update 或 app crash 之後，PTY 由背景 daemon 保留；host reboot 或 daemon crash 會結束它們 | 2026-09-25 研究 S9（官方 session-restore 頁） | 文件（沒有為新版重查） |
| Receipt 保留 | mutation receipt 會被清除；`request-show` 的說明列出「or its receipt was pruned」 | `request-show` schema notes；DB 目前 45 筆，最早一筆是 2026-09-25 | 文件／實測（筆數） |
| 不開 desktop app | `orca serve` 是前景 headless runtime：「Start an Orca runtime server without opening a desktop window」 | `orca serve --help` | 文件；未實測 |
| Linux 支援 | 支援 macOS、Windows、Linux；授權是 MIT | [stablyai/orca README](https://github.com/stablyai/orca)：「Supported platforms: macOS, Windows, and Linux」「free and open source under the MIT License」 | 文件 |
| Headless Linux 的要求 | 以 AppImage 安裝，必須先裝 Xvfb；state 放在 `~/.config/orca`。serve 模式不自動更新 | [headless-linux-server.md](https://github.com/stablyai/orca/blob/main/docs/reference/headless-linux-server.md)：「Xvfb must be installed first」「Orca serve never updates itself」 | 文件 |
| Headless Linux 的限制 | serve 模式不跑 desktop renderer，而 agent-completion detection 在 renderer 裡。這會不會影響 orchestration 的 settlement，文件沒有說 | 同上：「agent-completion detection runs in the desktop renderer, which is not started in serve mode」 | 文件；對 orchestration 的影響：未知 |
| Linux CI | loopctl 的 `unit-linux`（D53）只跑測試與靜態檢查，設計上不啟動 runtime（Feature 1 design D1：「不開子程序，不啟動 agent」）。所以 CI 不需要 Orca。在 GitHub runner 上跑 `orca serve`＋agent 沒有人試過 | — | 未實測 |

## B. Coordinator 排他

| 問題 | 答案 | 證據 | 判定 |
| --- | --- | --- | --- |
| 一個 Run 幾個 coordinator | 一個。`runs` 只有一組 `coordinator_handle`、`coordinator_pane_key`、`coordinator_orca_session_id`。gate、consuming check 等命令都要求呼叫者是 current consumer | `runs` schema。原始碼 `gj(...)`：`requireCurrentConsumer` 時，若呼叫者綁的不是指定 Run → `consumer_fenced: This coordinator terminal is bound to …, not …` | 實測（schema）／文件（原始碼） |
| 一個 terminal 幾個 Run | 一個。`run-create`／`run-use` 會先執行 `unbindOtherRunsForCoordinator`：清空原 Run 的 coordinator，把它的 `consumer_generation` 加 1，並 fence 它未 ack 的 delivery | 原始碼 `FHn`：`UPDATE runs SET coordinator_handle = NULL, … consumer_generation = consumer_generation + 1 …`，接著 `fenceUnacknowledgedMailboxDeliveries('run:'+id)` | 文件（原始碼） |
| 第二個 terminal 對同一 Run 下 `run-use` | 直接接手，不需舊 coordinator 同意，也不檢查舊 coordinator 是否還活著。接手時：<br>• `consumer_generation` 加 1；<br>• 改寫 coordinator 欄位；<br>• fence 該 Run mailbox 未 ack 的 delivery。<br>舊 terminal 之後的 gate、check 會得到 `consumer_fenced`。<br>只有 legacy adopted Run 有 `--takeover-legacy` 的額外條件。Skill 的「Never take over while the original coordinator is actively coordinating」是給 agent 的守則，程式不強制 | 原始碼 `uHn`（`bindRun`）：`UPDATE runs SET coordinator_handle = ?, … consumer_generation = consumer_generation + 1 …`，接著 `fenceUnacknowledgedMailboxDeliveries('run:'+runId)` | 文件（原始碼）；未實測（建立第二個 terminal 需要 `terminal create`，禁止） |
| 同一 terminal 重新 `run-use` | generation 不變 | `run-use --id run_b6098d2f6bed` 後，`run-show` 仍為 `consumer_generation: 1`；本次 check 仍看到原本的未讀訊息 | 實測 |
| Lock／lease／epoch | 有 epoch（`consumer_generation`），沒有 lease、到期或 lock，取得方式是最後綁定者勝出。`run_coordinator_handles` 會保留所有曾綁定過的 handle，作為 mailbox 路由的歷史 | schema 與 trigger `trg_runs_remember_coordinator_*` | 實測（schema）／文件（原始碼） |
| 誰能當 coordinator | 具穩定 pane identity 的 Orca terminal。Orca terminal 以外的程序必須帶 `--from <handle>`；錯誤訊息自己承認帶別人的 handle 就會操作別人的 mailbox，所以這個身分是信任本機呼叫者，不是驗證 | 去掉全部 `ORCA_*` 環境變數後跑 `run-current --json` → `no_active_sender_terminal`：「Pass --from with your own terminal's handle — another pane's handle would act on its mailbox — or run the command inside a live Orca terminal with ORCA_TERMINAL_HANDLE set」 | 實測 |

## C. Decision gates

全部在 `run_b6098d2f6bed`／`task_28f9f3d7de99` 內實測。

| 問題 | 答案 | 證據 | 判定 |
| --- | --- | --- | --- |
| 記錄哪些欄位 | `id`、`run_id`、`task_id`、`question`、`options`（JSON 字串陣列）、`status`（`pending`／`resolved`／`timeout`）、`resolution`（自由文字）、`created_at`、`resolved_at`（精度到秒） | `gate-create` 的回傳：`{"id":"gate_db1fc9318fa0",…,"options":"[\"approve\",\"revise\"]","status":"pending","resolution":null,…}` | 實測 |
| 誰解決 | 沒有記錄。gate 列沒有 resolver 欄位；只有 `mutation_receipts` 留下 `caller_fingerprint`，而 receipt 會被清除 | 回傳的 gate 物件；schema；DB 副本 `mutation_receipts` 有兩筆 `orchestration.gateResolve` | 實測 |
| resolution 是否限定在 options 內 | 不限定 | `gate-resolve --resolution "not-an-option"` → `ok: true`、`"status":"resolved","resolution":"not-an-option"` | 實測 |
| 已解決的 gate 能否再解決 | 可以，而且會直接覆寫，gate 列不留前一次的值 | 接著 `gate-resolve --resolution "approve"` → `ok: true`；`gate-list` 只剩 `"resolution":"approve"`。前一次的值只留在會被清除的 receipt 中 | 實測 |
| 綁定版本或 digest | 沒有欄位。digest 只能寫在 question 或 resolution 文字裡，Orca 不核對 | 本次 question 寫 `approve_plan plan=sha256:aaaa design=sha256:bbbb?`，Orca 原樣保存 | 實測 |
| Agent 能否解決 | 能。本次是 agent（Claude subagent）在 coordinator terminal 內解決的。程式只檢查呼叫者是不是該 Run 的 current coordinator（`requireCurrentConsumer: true`），不區分人或 agent | 上兩次 resolve 都成功；原始碼 `gateResolve` handler | 實測 |
| 對 task 的效果 | `gate-create` 把 task 轉成 `blocked`，並對該 task 執行 `completeActiveDispatchesForTask`；若 supervised worker 仍 active 則拒絕（`task_not_startable`）。`gate-resolve` 把 task 轉回 `ready` | task 狀態實測為 `ready` → `blocked` → `ready`；原始碼 `createGate`／`wLn` | 實測／文件（原始碼） |
| UI 是否把 gate 呈現給人 | 沒有查 | — | 未知 |
| 用途定位 | 文件把 gate 定位為 coordinator 擁有的 Task-DAG 決策 | messaging 參考：「Use a gate only for a coordinator-owned Task-DAG decision」 | 文件 |

## D. Worker lifecycle

依文件、help、schema 與舊資料；`worker-start` 在本次禁止執行。

| 問題 | 答案 | 證據 | 判定 |
| --- | --- | --- | --- |
| 支援的 agent | `claude`、`codex`、`cursor`、`antigravity`、`muse`、`zcode`、`opencode`、`opencode2` | `worker-start` 的 schema note：「--agent takes an Orca agent id enabled on the worker server, such as claude, codex, cursor, antigravity, muse, zcode, opencode, or opencode2」。這行在 1.4.209 的 schema 快照中沒有（見 G） | 文件 |
| 指定 model／effort | `--model` 收 opaque provider id，只支援 Claude、Codex、Cursor、Antigravity、Muse。`--effort` 需要 `--model`，兩者都不能與 `--terminal` 併用。**opencode 不收 `--model`**，用自己設定檔裡的 model | schema note：「Other agents, including opencode and zcode, launch with the model from their own config」；coordinator-loop 參考：「Other agents, including `opencode`, reject `--model`」 | 文件 |
| 讀回 model／effort | Orca 在 `worker_dispatches.start_options` 記錄 `launch.requested` 與 `launch.effective`。`effective` 是 Orca 實際放進啟動的值，不是從 native transcript 讀回的推論 model。從 transcript 讀回 native model，沒有找到專用欄位 | DB：`"launch":{"requested":{"agent":"claude","model":null,"effort":null},"effective":{…}}`；skill：「Compare `launch.requested` with `launch.effective`; never claim a model or effort from requested arguments alone」 | 實測（欄位）／文件（語意）；native 讀回：未實測 |
| 權限與 sandbox | `worker-start` 沒有權限或 sandbox 旗標；啟動方式依使用者對新 agent tab 的設定，「there is no flag for it」。<br>要自訂 argv 有兩條路：<br>• `terminal create --command` 加 `dispatch --inject`，worker 不受 supervision；<br>• `worker-start --terminal`，但不能再帶 `--model`／`--effort` | schema note；2026-09-25 runtime-probe 用 `terminal create` 自訂 Codex `--sandbox workspace-write`，再以 `worker-start --terminal` 納管 | 文件；自訂路徑在 1.4.209 實測過 |
| Sandbox 內呼叫 Orca | 1.4.209 時，Codex sandbox 內的 `orca orchestration check/send` 回傳 `runtime_unavailable`，所以無法送出 `worker_done` | 2026-09-25 runtime-probe「Codex native completion」列 | 舊實測；1.4.215 未重測 |
| Worktree 位置 | `--worktree current\|<selector>\|new-child\|new-top-level`，另有 `--name`、`--repo`、`--base-branch`、`--setup`。新 worktree 預設會跑 setup。`current` 指 coordinator 的 workspace，不是 shell cwd | schema；placement 參考；2026-09-25 runtime-probe 的「Workspace identity」列 | 文件／舊實測 |
| `worker_done` payload | `send --type worker_done` 必須帶 `--outcome succeeded\|failed`，可以帶 `--task-id`、`--dispatch-id`、`--files-modified`、`--report-path`。只有從被派的 pane 送出才會 settle task。寫入 `tasks.result` 的 JSON 有 `provenance`、`outcome`、`messageId`、`reportedBy`、`subject`、`body`、`completedBy`、`filesModified`、`reportPath`、`completedAt` | `send` 的 schema notes；舊 Run `task_e3f33b44e673.result` | 文件／實測（讀舊資料） |
| Liveness | 分兩層：<br>• `worker-list` 的 `projection.liveness` 是 fleet 判定，取值 `live`／`unverifiable`／`exited`；<br>• `worker-show` 的 `observation.status` 只反映 PTY。<br>`unverifiable` 不授權 stop 或 retry | skill「Authority and safety floor」；舊 Run 的 `worker-list` 有 `{"verdict":"unverifiable","reason":"missing_status"}` 與 `{"verdict":"exited","source":"resource_release"}` | 文件／實測（讀舊資料） |
| stop／abandon | `worker-stop` fence 該 Dispatch，只關它擁有的 agent terminal，不刪 worktree。`worker-abandon` 只 fence，不動任何程序或檔案。同一 task 連續失敗三次後 circuit-break | schema notes；recovery 參考 | 文件；未實測 |
| Timeout | `worker-start --timeout-ms` 是啟動就緒的時限（舊 probe 為 `"timeoutMs":30000`）。沒有找到 worker 執行時限、active 預算或到期自動 stop | schema；DB `start_options` | 文件；執行時限：未知（原始碼未查） |
| Heartbeat | worker 依 preamble 指定的節奏送 `--type heartbeat`，寫入 `dispatch_contexts.last_heartbeat_at`；「A heartbeat proves liveness, not completion」 | worker-contract 參考；schema | 文件 |
| Native session ID | `worker-read --source auto\|transcript` 在有 hook 回報的 transcript 時讀它；skill 要求「Never guess a provider session ID」。Orca 有沒有把 native session ID（Claude uuid、OpenCode `ses_…`）列成欄位，沒有查到 | recovery 參考 | 未知 |

## E. Messaging

| 問題 | 答案 | 證據 | 判定 |
| --- | --- | --- | --- |
| 定址方式 | `run:<id>`（coordinator mailbox）、`dispatch:<id>`（單一 attempt）、群組（`@all`、`@idle`、`@claude`、`@codex`、`@opencode`、…、`@worktree:<id>`）、legacy terminal handle。沒有以人取的名稱定址；task 的 `display_name` 不是地址 | `send` schema notes；messaging 參考 | 文件 |
| 寄給 Run mailbox | 可以；回傳 `to_handle: run:run_b6098d2f6bed`，`delivered_at: null` | `send --to run:run_b6098d2f6bed` → `msg_0664f048923c` | 實測 |
| 送達保證 | `send` 成功只代表訊息已持久排入佇列；wake 與 nudge 是 best-effort，不證明對方讀過 | skill：「A successful `orchestration send` proves durable enqueue」 | 文件 |
| Ack 與 replay | consuming `check` 回傳最舊的 FIFO delivery，`--ack` 之前會重複回傳同一批。`--ack` 的回應同時給出下一批。每個 mailbox 同時只有一個 outstanding delivery，由 DB trigger 保證 | 兩次 `check` 都回 `deliveryId: delivery_6729af63192f`；`check --ack delivery_6729af63192f` → `acknowledged: delivery_6729af63192f`，並回下一批 `delivery_94aeb4f4459b`；trigger `trg_deliveries_one_outstanding` | 實測 |
| Reply | 產生新訊息，`thread_id` 指向原訊息，寄回 Run mailbox | `reply --id msg_0664f048923c` → `msg_d774c86f5ecc`，`thread_id: msg_0664f048923c` | 實測 |
| Ask | 必須有 active 的 supervised Dispatch；coordinator 不能自問 | `ask --to run:… --timeout-ms 3000` → `dispatch_inactive: ask requires an active supervised Dispatch` | 實測（拒絕路徑）；正常 ask／resume：未實測 |
| 冪等（`--retry-request`） | 呼叫者可以自帶 UUID；同一 UUID、同一內容重送回傳原結果並標 `replayed: true`；同一 UUID、內容不同 → `request_mismatch`；非 UUID 字串 → `invalid_argument`。`request-show` 回 `completed`／`pending`／`absent`，`absent` 不代表沒發生 | 自訂 `762ba2d9…` → `msg_5ec636c87b2e`，`replayed: false`；改 body 重送 → `request_mismatch`；以 `641877ae…` 重送原 send → 同一個 `msg_0664f048923c`，`replayed: true`；`request-show 641877ae…` → `state: completed` | 實測 |
| Coordinator 換人時 | 未 ack 的 delivery 被 fence；未讀訊息改道到 Run mailbox | 原始碼 `bindRun`／`FHn`、`routeAllUnreadDirectMessagesToRunMailbox` | 文件（原始碼） |

## F. 對照表：loopctl 的責任與 Orca 的能力

「loopctl 仍需負責」只寫事實落差，不是 design。

### Feature 1（人工決策與下一步）

| loopctl 責任（Feature 1 design） | Orca | 證據 | loopctl 仍需負責 |
| --- | --- | --- | --- |
| `claim`：每個 repo＋feature 一個 owner；token 只存 digest；寫入命令核對 token（D3、D4） | 部分。Orca 有「一個 Run 一個 coordinator＋generation」，但：<br>• 取得方式是最後綁定者勝出，不需舊 coordinator 同意；<br>• 身分是 terminal pane，不是 actor；<br>• Orca terminal 以外的程序要自帶 `--from`，等於信任呼叫者；<br>• 沒有 repo＋feature 的鍵 | §B | feature 層級的協調權與 token；Orca Run 和 feature 的對應；Orca 換 coordinator 時的處理 |
| `decide`：只收 `human:<name>`；記 actor、source、reason、impact；以 `decide:<id>` 冪等；內容不同時記衝突並 Blocked（D5、D6、D10） | 否。gate 不記 resolver，resolution 是自由文字且不核對 options，可以覆寫，agent 也能解決 | §C 實測 | 全部 |
| `approve_plan`：釘住 plan 與 spec、ac、design 的 digest；`scope_change` 讓核准失效（D9、D10） | 否。gate 沒有版本或 digest 欄位 | §C 實測 | 全部 |
| `next`／`status`：由狀態衍生唯一允許的下一步（D7、D8） | 否。Orca 的 `task-list --ready` 只是 DAG 就緒，`worker-list` 的 `projection.nextAction` 只管 worker 資源清理；兩者都不是 delivery 的下一步 | schema；recovery 參考 | 全部 |
| 持久狀態：人可讀的 JSON、history-first、偵測手改、中斷只見完整新舊版（D3、D4；project-intent 限制 15 不用 SQLite） | 部分。Orca 的狀態可靠持久、跨重啟保留，但它是 SQLite 內部 schema，會 migration，也不偵測外部修改 | §A | 全部的 feature 狀態。Orca 的 Run／Task／Dispatch ID 可以當成外部事實記錄 |

### Feature 2（派工與結果回收）

| loopctl 責任（roadmap Feature 2、D45-04 §4–§6、§10） | Orca | 證據 | loopctl 仍需負責 |
| --- | --- | --- | --- |
| 派工（`agent_start`、`prompt`、worktree） | 提供（未實測）。`worker-start` 一次完成 task、attempt、placement、就緒與 prompt 注入；支援 claude、codex、opencode | §D；1.4.209 實測過 claude 成功、codex 需自訂 argv | 決定何時派、派哪個 assignment；先登記再呼叫 |
| Assignment 與 result identity（`assignments[attempt]` 帶 spec、design、plan、AC digest、head、scope；result 以 attempt 對回，D21 handle round-trip） | 部分。Orca 有 Task／Dispatch ID、dispatch capability；`worker_done` 只能從被派的 pane 送出；被取代的 worker 收到 `consumer_fenced`。但 `worker_done` 只帶 outcome 與 report path，不帶版本或 digest | §D；worker-contract 參考 | assignment 內容、result 檔驗證、attempt 與 Orca Dispatch 的對應；native session ID（§D 未知） |
| 外部寫入登記（prepared → in_flight → succeeded／failed／unknown；讀回；unknown 交人） | 部分，只涵蓋 Orca 自己的 mutation。`--retry-request` 可自帶 UUID、可 replay、內容不同時拒絕；`request-show` 三態語意與 D45-04 §4 的 unknown 相近。receipt 會被清除；不涵蓋 `push`、`pr_ensure` | §E 實測 | registry 本身、GitHub 寫入、receipt 被清除後的判斷 |
| `observe worker\|native`（有界讀取、讀取失敗預算、seq） | 部分。有 `worker-list`、`worker-show`、`worker-read`（`--source transcript\|terminal`、cursor），liveness 分 `live`／`unverifiable`／`exited`。沒有讀取預算 | §D | 讀取預算、seq、版本水位；pr／ci 觀察 |
| Writer 結束判定（D04：result 已匯入且 native turn 完成，或 stop 經 process-info 確認） | 部分。`worker_done` 加上 Task settlement；`exited` liveness；`worker-stop` 有 stop verdict（capability `orchestration.worker-stop-verdict.v1`）。skill 同樣規定 absence 不授權任何動作 | §D；`orca status` capabilities | 判定規則與證據組合 |
| Active 預算 4h、worker 時限 45 分、到期 stop | 否。只有啟動時限與三次失敗的 circuit breaker | §D | 全部 |
| Preflight R1：兩個 profile（Claude Code＋`claude-opus-5-5` high；OpenCode＋`openai/gpt-6-astra` xhigh），native model 讀回、cwd 核對、權限負例、stop 確認 | 部分或否：<br>• Claude：可以 `--model`／`--effort`，有 `launch.effective`，但沒有 native 讀回；<br>• OpenCode：不收 `--model`，model 只能靠 OpenCode 設定，要求的 variant 無從表達；<br>• `worker-start` 沒有權限旗標 | §D | 整個 preflight 與 receipt；權限設定改由 runtime 自身設定承載 |
| 使用者介入 | Orca 的 `ask` 是 worker 問 coordinator，不是問人 | §E | `next: human` 與 `decide` |

### 結論（依證據，不是決定）

- Feature 1 的五項責任，Orca 一項都不能取代：gate 沒有 actor、digest 綁定、冪等或防覆寫，Run binding 是最後綁定者勝出。所以 Feature 1 的 spec 範圍不受「是否改用 Orca」影響。
- Feature 1 只在一點上與 runtime 有交集：誰呼叫 loopctl。如果 orchestrate 跑在 Orca coordinator terminal 中，Orca 與 loopctl 各自有一個協調權：Orca 的 Run binding 與 loopctl 的 claim token。兩者不會自動一致。這會成為 Feature 2 的整合點，不會改動 Feature 1 已寫的契約。
- 改用 Orca 主要影響 Feature 2 與已核准的決策：
  - D53 的 profile 把 transport 定為 Herdr 0.9.1；
  - D45-04 §6 的 D21 handle 欄位 `{herdr_session, pane, agent_name, native_session_id}`；
  - reviewer 的 OpenCode model 無法經 Orca 指定。

## G. 風險

| 風險 | 證據 | 判定 |
| --- | --- | --- |
| 版本變動快、會自動更新 | 1.4.209（09-25）→ 1.4.212（09-27）→ 1.4.214（本 terminal 啟動時）→ 1.4.215（今天），六天四版。`orca status --json`：`"remoteUpdateSupport":{"installMode":"interactive","automatic":true,…}`。README：「we ship daily」 | 實測／文件 |
| 命令與語意變動 | 與 1.4.209 的 schema 快照比對：新增 `host name`、`profile state exports`、`profile state rollback`；`worker-start` 的 notes 改成支援 opencode、Antigravity、Muse。`coordinator-start`／`coordinator-stop` 已退役：「This command performs no effects」。DB 註解顯示 schema migration（v34、v37…，目前 user_version 42） | 實測（diff `docs/research/2026-09-25/evidence/orca-command-schema.json` 與今天的 `agent-context --json`） |
| 依賴 app 或 runtime | CLI 需要 runtime 在跑；serve 模式不跑 renderer 的 completion detection；serve 不自動更新，GUI 會。Orca terminal 以外的程序沒有 coordinator 身分（§B） | 實測／文件 |
| Linux | 官方支援 AppImage，headless 需要 Xvfb；orchestration 在 headless 下是否完整，文件沒有說 | 文件／未知 |
| 授權與原始碼 | MIT，GitHub `stablyai/orca` 公開；安裝版 commit `3eb1adec…` | 文件 |
| 與 D52（reviewer 必須是不同的實際模型、獨立 session）的關係 | 經 Orca 派的 opencode worker 由 OpenCode 設定決定 model，`launch.effective` 不會是 native 讀回；Claude 也只有 effective。D52 的「實際模型」仍得靠 native 紀錄核對（D45-04 §6），Orca 沒有提供這一層。獨立 session 由每個 Dispatch 一個新 agent terminal 提供（文件），並未實測 | 文件；native 讀回：未實測 |
| 與 project intent 的關係 | 限制 12：OpenCode 是預設 runtime，Orca 為選配；「Environment」段：「啟動／resume、worktree 及結果回收不依賴這些選配工具」；限制 15：不用 SQLite 作 MVP 持久化。把 Orca 當 runtime，會和第一條、第二條直接相關；只要 loopctl 不把 Orca DB 當自己的狀態，就不碰第三條 | 文件（本 repo） |
| 共享 terminal 的副作用 | 本 terminal 已被綁到 scratch Run，且無法解除（§0.3）。同一 terminal 中的任何 agent 都能以 coordinator 身分操作這個 Run，包括 resolve gate | 實測 |
| Sandbox 與 Orca IPC | 1.4.209 時，Codex sandbox 內無法呼叫 Orca IPC，送不出 `worker_done`。D45-04 §6 的權限設定檔拒絕 `herdr`；改成 Orca 後，worker 至少要能呼叫 `orca orchestration send/check` | 舊實測（runtime-probe）；新版：未實測 |

## 事實、推論、未知

**事實**（本次實測或文件明文）

1. Orca 的 orchestration 狀態存在一個 SQLite DB（`user_version 42`、WAL），跨 app 重啟與升級保留。Orca 沒有 JSON／YAML 投影。
2. 一個 Run 只有一個 coordinator，以 `consumer_generation` 作 epoch。任何 Orca terminal 執行 `run-use` 都能直接接手，沒有 lease 或同意；同一 terminal 重新 `run-use` 不會遞增 generation。
3. Gate 只記 question、options、status、resolution 與時間：
   - 不記 resolver；
   - resolution 不受 options 限制；
   - 可以覆寫；
   - 沒有 digest；
   - 當時的 coordinator 不論是人或 agent，都能解決。
4. Mailbox 是持久的 FIFO delivery，ack 前重複回傳；`--retry-request` 支援呼叫者自帶的 UUID，內容不同時拒絕。`ask` 需要 active 的 supervised Dispatch。
5. `worker-start` 支援 claude、codex、opencode 等；`--model`／`--effort` 不適用於 opencode；沒有權限旗標；只有啟動時限。
6. Orca 是 MIT 授權，支援 Linux；headless 需要 Xvfb。本機六天四個版本，並開啟自動更新。

**推論**（由事實推得，未驗證）

1. loopctl 的 claim、decide、approve_plan、next、狀態檔都不能交給 Orca；Feature 1 的 spec 不因 runtime 選擇而需要改。
2. Orca 能取代 Herdr 在 Feature 2 中的 transport 角色：派工、attempt identity、worker 觀察、stop。但 reviewer profile（OpenCode＋指定 model 與 variant）和 R1 的 native 讀回，Orca 都沒有直接提供。
3. 用 Orca 時，loopctl 需要把 Orca 的 Run ID 與 `consumer_generation` 當成外部事實來核對；否則另一個 terminal 執行 `run-use` 可能在 loopctl 不知情時改變 mailbox 的消費者。
4. Orca 的 `request-show` 語意（`absent` 不代表沒發生）與 D45-04 §4 的 unknown 處理一致，可以直接對應到 `agent_start`／`prompt`／`stop` 的讀回。

**未知**

1. 第二個 terminal 接手時，舊 coordinator 實際收到的錯誤與 mailbox 狀態（只讀了原始碼）。
2. 1.4.215 經 `worker-start` 派出的 opencode worker：實際 model、`launch.effective` 的內容、能否讀回 native session ID 與 model。
3. Headless `orca serve` 下的 orchestration 完整性（renderer 的 completion detection 是否影響 settlement）。
4. Worker 執行時限：原始碼未查。
5. 自動更新能否關閉、如何關閉；desktop UI 是否把 gate 呈現給人。
6. 1.4.215 的 sandbox 內能否呼叫 Orca IPC。

## Project Lead 待決的問題

1. **Feature 2 的 transport 是否從 Herdr 改成 Orca？**
   - 選項：
     - (a) 維持 D53 的 Herdr；
     - (b) 改 Orca，需要新的決策，修訂 D45／D53 的 profile 與 D21 handle 欄位；
     - (c) Feature 2 先做 transport 中立的 adapter 介面，Herdr 與 Orca 各跑一次 R1 再選。
   - 證據：§F Feature 2 表；project-intent 限制 12 與「不依賴選配工具」；§G 的版本變動。
2. **改用 Orca 時，reviewer profile 怎麼承載？**
   - 選項：
     - (a) OpenCode，以專用 OpenCode 設定固定 `openai/gpt-6-astra`，R1 必須能讀回 native model；
     - (b) 改用 Orca 的 `codex` agent 帶 `--model`，等於改 D53 的 reviewer runtime；
     - (c) reviewer 留在 Herdr。
   - 證據：§D（opencode 不收 `--model`）、D52、D53、2026-09-25 的 Codex sandbox 問題。
3. **協調權的單一來源。**
   - 選項：
     - (a) 只有 loopctl 的 claim token 算數，Orca Run binding 只是 transport，generation 變動即 Blocked；
     - (b) 只使用 Orca 的 coordinator binding，等於放棄 Feature 1 的 token，Feature 1 的 spec 要改；
     - (c) Feature 1 不動，這個問題延到 Feature 2 的 design。
   - 證據：§B 的「最後綁定者勝出」與 `--from` 的信任；Feature 1 design D3、D4、Risks「token 遺失」。
4. **人工決策的入口。**
   - 選項：
     - (a) 只用 `loopctl decide`，不使用 Orca gate；
     - (b) `decide` 為權威，另在 Orca 建 gate 只作 UI 提示；
     - (c) 以 Orca gate 作權威，但這不滿足 approve_plan 的 digest、actor 與防覆寫要求。
   - 證據：§C 實測。
5. **版本與自動更新政策。**
   - 選項：
     - (a) 接受自動更新，每次 Orca 版本改變就重跑 R1，並記錄版本；
     - (b) 查出並關閉自動更新、釘住版本，方法目前未知；
     - (c) 不採用 Orca。
   - 證據：§G（六天四版、`remoteUpdateSupport.automatic: true`、schema 變動、retired commands）。
