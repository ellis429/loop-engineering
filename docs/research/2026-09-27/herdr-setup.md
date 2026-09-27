# Herdr 本機安裝與 H0 實測

日期：2026-09-27。狀態：**小型能力測試已完成：Luna 經 OpenCode、Sonnet 5 經 Claude Code 的真實交接均通過；整合 hooks、Reviewer 權限與完整 delivery loop 仍未驗證。**

## 安裝與只讀 preflight

| 項目 | 本機結果 |
| --- | --- |
| Herdr | `0.9.1`，macOS ARM64 binary |
| 安裝位置 | `/Users/johnson.chiang/.local/bin/herdr` |
| Binary SHA256 | `5fc7a7e7adfaca56fa80aa89dcb025693357268dab8285b9ce2d08a2313c89de` |
| Server protocol | `22`；本機 CLI 顯示 endpoint／protocol compatible |
| OpenCode | `1.18.32`；其他 API 能力見 [OpenCode setup](opencode-setup.md) |
| 認證觀察 | 初始 OpenCode 無保存的登入；後續已完成 ChatGPT OAuth，Luna 呼叫成功。Claude Code 已有 Claude Max 帳號登入，Sonnet 呼叫成功 |

採用 [官方 installer](https://herdr.dev/install.sh) 下載預編譯檔並驗證 manifest checksum。沒有編譯 Rust，也沒有修改 shell rc。Installer 遇到 PATH 內無法執行的 Intel checksum 工具後，改用系統 PATH 完成校驗與安裝，沒有略過 checksum。

[Preflight evidence](herdr-setup/preflight.json) 保留安裝後 version／help 與認證摘要；它是 H0 控制執行前的快照。後續真實操作見 [transport evidence](herdr-setup/transport.json)，兩者不是同一時點。

## 第一輪：具名 CLI 與無推論啟動

本輪以外部 script／CLI 的專用 session `le-h0-544w2nok` 驗證 [官方 CLI 介面](https://herdr.dev/docs/cli-reference/)。所有控制命令都有相同 `--session` selector 及已查回的 IDs；沒有使用 focused/default session，也沒有冒充在 Herdr pane 中執行的原生 skill。

[Bundled Herdr skill](https://github.com/herdrdev/herdr/blob/master/skills/herdr/SKILL.md) 要求協調 agent 自身具有 `HERDR_ENV=1`。本協作者仍在 Herdr 外；未偽造環境變數。被 Herdr 啟動的 Python fixture 則實際取得 `HERDR_ENV=1` 與 pane/workspace/tab IDs，記在 result。原生 pane-only skill 與外部 CLI 接法需在 orchestrate profile 中明確區分。

| 測項 | 真實結果與適用範圍 |
| --- | --- |
| Headless server | 啟動成功，named session 使用自己的 socket；protocol 22 相容 |
| Workspace／worktree | 建立暫時 repo workspace 與 `h0/probe` worktree，讀回實際 cwd、branch 與 SHA |
| 結構化檔案交接 | 固定 Python fixture 讀 assignment、核對 cwd/head、寫 result；外部逐項驗 run/task/attempt/head。這是確定性 fixture，不是 agent 生成的結果 |
| 輸出與 timeout | 讀到 fixture 完成 marker；等待從未輸出的 marker，CLI exit 1 且 error code `timeout` |
| 普通程序停止 | 對自己啟動的 waiter 送 Ctrl+C，讀到 interrupted；process-info 回到 shell，OS 查驗原 waiter PID 不存在 |
| OpenCode 啟動辨識 | `agent start h0-opencode --kind opencode ... -- --pure` 成功；agent 為 idle、interactive_ready，cwd 正確。未發送 prompt |
| OpenCode 停止 | agent send-keys Ctrl+C 後，畫面及 process-info 均回到 shell；只驗空閒 TUI 退出，沒有驗推論取消 |
| 關閉／重開 | `workspace close` 後 git worktree 仍在，重新 open 成功；pane 從 `w2:p1` 改為 `w3:p1`，舊 ID 查詢回 `pane_not_found` |
| 環境調整後重啟 | server 停止／重啟後保留原始 repo workspace。這不是 agent session resume，也沒有實測 client detach／reattach |
| 收尾 | 測試 server 已停止；worktree、branch、結果檔保留。沒有使用 worktree remove |

OpenCode 畫面顯示 `Claude Sonnet 4.6 / Vertex (Anthropic)`，只是預選模型的 UI 顯示；未推論、未觀察 native conversation ID，也未驗證官方 integration。`--pure` 的這次啟動不能證明 integration hook、模型權限或 resume 已可用。

## 實測發現與設計影響

1. **啟動 PATH 必須可用。** 第一次 worktree create 回 `worktree_create_failed: Bad CPU type in executable`。查到 `/usr/local/bin/git` 只有 Intel 架構；確認 checkout 未建立後，停止測試 server，以系統 PATH 重啟並重試成功。這是本機工具鏈根因，不更改產品行為或降級驗證。
2. **完成訊息只作喚醒。** Marker、pane run exit 0 與 agent idle 都不能代替 assignment/result 及版本核對。Probe 的 result 明列 `producer=deterministic_python_fixture`、`inference=false`，不作 G1／G2／G3 證據。
3. **重開時重新核對 handle。** 同一 worktree 可取得新 pane ID；保留 checkout 不代表可沿用舊 agent／pane 身分。
4. **環境值有優先順序。** 首次 server 同時傳入 named session 與 socket override，實際仍使用 named session 的 socket。正式接法應保存 observed locator，本次後續只使用明確 `--session`。

本機重跑所需啟動條件是讓 `/usr/bin` 優先於有問題的 `/usr/local/bin`，並保留 `~/.local/bin` 以找到 Herdr／OpenCode。只對測試 server 設定 PATH；沒有改使用者全域設定。測試設定採 `/bin/sh` non-login、關閉背景更新及自動 agent restore，避免啟動時混入其他程序。

## 第二輪：Luna 與 Sonnet 真實模型交接

使用者指定只用 GPT-6 Luna、Claude Sonnet 5.0 做小型能力測試；測通後停止擴充輪次。本機接法依 [D44](../../decisions.md)：OpenAI 經 Herdr＋OpenCode，以 ChatGPT 帳號登入；Claude 經 Herdr 直接啟動 Claude Code，使用既有 Claude Max 登入。

| 模型／接法 | 結果與原生證據 |
| --- | --- |
| GPT-6 Luna／OpenCode 1.18.32 | 讀 assignment、查 git HEAD、讀 README、寫 JSON。`luna-01` 輸入 3／5／8 得 16，IDs／SHA／heading 均核對成功；原生 assistant messages 為 `openai/gpt-6-luna`。另已完成停止後明確 `--session` 續跑，`luna-02` 用新輸入 2／7／11 得 20，沒有沿用舊結果。見 [Luna evidence](herdr-setup/luna.json) |
| Sonnet 5／Claude Code 2.1.283 | 相同任務經 Read、Bash、Write 完成；結果為 16，IDs／SHA／heading 正確。原生 assistant messages 為 `claude-sonnet-5`，effort low；只完成一個成功任務，未加做 Sonnet resume。見 [Sonnet evidence](herdr-setup/sonnet-claude.json) |

原生 sessions：Luna `ses_f1d8c6311ffeZE2kCvT8P52ocj`；Sonnet `a548ce24-b7d8-4ecc-ac89-60d3e7f76815`。模型結論來自原生紀錄，不只讀 UI 名稱。兩路的 tracked files 與 HEAD 均未改動；測試 agent／server 已停止，worktree 與結果保留。

### 遇到的限制與處理

- OpenCode 的第一次 ChatGPT 裝置授權逾時；第二次成功並查回 OpenAI OAuth。文件不保存 tokens 或裝置碼。Runtime 記錄 cost 0 不代表不消耗訂閱額度。
- OpenCode／Vertex Sonnet 實際送入任務後回 `invalid_grant`，沒有模型成果；Herdr 仍回 done，實證 lifecycle 不能當品質成功。既有 Vertex 環境變數指向不存在的檔案；本機另有 ADC，但呼叫時授權失敗。使用者隨後明確改選 Herdr＋Claude Code，這條 Vertex 接法不再是本機 Sonnet 待辦。
- Claude Code 第一個 attempt 載入使用者設定的 localhost API 位址，遇 `ECONNREFUSED`。中止且確認無結果後，另起 attempt，以 `--setting-sources ''` 排除該 session 的 user/project/local 自訂設定；全域設定檔未改動，Claude Max 登入維持可用。
- Sonnet 成功測試使用 `--safe-mode`、低 effort 及 Read／Write／Bash 工具；runtime 顯示 auto permission mode，組合 shell 指令由 auto classifier 允許。這不是 Reviewer 寫入隔離或完整工具權限驗收。
- **Safe mode 僅用於本次能力測試。** 它會停用 skills／hooks 等自訂內容，不能直接當作正式 orchestrate profile，後續需載入核准方法與必要設定。
- OpenCode 工作中讀 `recent-unwrapped --lines 60` 曾回 `agent_not_idle`；改讀 visible 可觀察同一任務，沒有重送 prompt。
- Luna resume 是查回原生 ID 後明確傳入 OpenCode；尚未驗證 Herdr integration 自動回報身份與自動 restore。

## 尚未完成與下一步

- 正式 orchestrate 所需的 skills／hooks 載入與 runtime profile；本次小型模型交接已完成。
- Integration 回報的 native ID／lifecycle、自動 restore、推論取消與 Reviewer 權限；明確 OpenCode session resume 已測通。
- Reviewer 隔離、真實 GitHub／CI、三 gates 及 review→fix→re-review loop。

使用者要求的一輪 Sonnet 與 Luna 基本交接已足以支持接合設計，本輪到此停止。接著收斂薄 controller／orchestrate 的正式 design 與 plan；以上未驗證能力依實際產品需要排入驗收，不把小型 probe 放大成整套執行平台。

## 證據與保留位置

- [Transport evidence](herdr-setup/transport.json)：逐次 CLI 結果（含預期失敗）、fixture 原始內容、assignment/result、digest、最終 SHA 與停止／保留查驗。
- 本機暫時 repo：`/private/tmp/le-herdr-h0-544w2nok/repo`。
- 保留的 worktree：`/private/tmp/le-herdr-h0-544w2nok/worktree`，branch `h0/probe`，head `7dfc7be5a721787bd49cf036c3119caeb7857db9`。
- Named session metadata：`~/.config/herdr/sessions/le-h0-544w2nok/`；server 已停止，沒有清除 metadata。

暫時目錄不是長期 demo 的保存保證；可分享證據已複製進本 repo。Example 的 worktrees 應依正式配置保留，不能把這個 H0 暫時 repo 當成 cross-node-file-transfer。

## 與後續 example 的關係

沿 [D43／D44](../../decisions.md)，cross-node-file-transfer 由 Herdr 承接工作空間，搭配 orchestrate＋薄 controller；本機 OpenAI 使用 OpenCode、Claude 使用直接 Claude Code 接法，在 loop-engineering 測通後啟動。當前 controller bootstrap 仍沿 D39 的 Opus／GPT 分工。H0 部分能力通過不替代 Herdr 底座選型、正式 design／plan review 或 D11 開工批准。
