# Agent 傳訊與 opencode 查核

日期：2026-09-26。範圍：核對本輪變更請求中的 runtime 主張，供 adapter 設計使用；不是採用新 runtime 的決策，也不是 V4 執行證據。D08 的 Orca workers 維持。

## 版本與查核方式

- opencode 官方 repository 為 `anomalyco/opencode`；本次讀取的 source checkout 位於交接請求旁的 `scratchpad/oc`，commit 為 `545f51d26cc39a907d2867492d498d9607ea5fa4`，對應 2026-09-21 的 [v1.18.32 release](https://github.com/anomalyco/opencode/releases/tag/v1.18.32)。沒有執行該 checkout 的程式。
- 本機 PATH、`/opt/homebrew/bin/opencode`、`/usr/local/bin/opencode`、`~/.opencode/bin/opencode` 與 `/Applications/OpenCode.app` 均未找到可用安裝。這是所查位置的結果，不聲稱搜尋了整台電腦。
- Orca bundle 仍為 Stably Orca 1.4.209；來源固定在已查明的 build commit `ee1c52207000c7d70282549c73e9945bd1cec1e8`。本輪讀取已安裝 CLI/shared modules 及同 commit 的官方 source，沒有啟動 worker、發訊息、安裝 opencode 或讀取 credentials。

## opencode：可證明的能力與限制

| 主題 | 原始碼／文件證據 | 對我們的含義 |
| --- | --- | --- |
| Task tool | 預設 foreground，建立帶 parentID 的子 session 或續用 task_id；一般結果取最後一個 text part。背景模式須 experimental flag；支援延續背景 task。[task.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/tool/task.ts) | 原生 task 回傳不是完整 review result／證據契約；不能讓 Implementer 透過它派出 G2 |
| 對等傳訊 | 已讀 Task／tool registry 未提供完整 agent peer mailbox 契約；Question tool 面向使用者，不能當成子 agent 向父 agent 的對等問答。[registry.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/tool/registry.ts)、[question.txt](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/tool/question.txt) | 這是對已查 surface 的結論；不擴張為所有 plugin 都不可能傳訊 |
| 背景完成 | Task 完成會向父 session 提交 synthetic prompt。背景 job registry 明確為 process-local，重啟或 scope 結束會失去 job 狀態及中斷活躍工作。[task.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/tool/task.ts)、[background-job.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/core/src/background-job.ts#L113) | Controller 必須另存結果、ownership 與恢復狀態；不把此限制誤寫成所有 session/messages 都不持久化 |
| Server／SDK | `opencode serve` 提供 HTTP API；可建立 session、讀 messages，使用 `prompt_async` 提交 prompt；輸入可指定 agent/model。[Server](https://opencode.ai/docs/server/)、[session routes](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/server/routes/instance/httpapi/groups/session.ts)、[prompt.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/session/prompt.ts) | 若未來採用，可由外部 controller 為各角色建獨立 session；不使用 Task tool 作 G2 的外層派工 |
| Async 完成 | HTTP handler fork prompt，立即回 NoContent；非同步錯誤另發 Session.Error。[handler](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/server/routes/instance/httpapi/handlers/session.ts#L311) | HTTP 接受不是成功；需持續查回 messages、errors 與對應 assignment |
| Idle event | `session.status` 可報 idle；runner 取消或離開 busy 也會設 idle。[status.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/session/status.ts)、[run-state.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/session/run-state.ts) | `/event` 只喚醒讀取；controller 還要核對完整 result/evidence，不能以 idle 通過 gate |

Agent Teams 請求 [#12661](https://github.com/anomalyco/opencode/issues/12661) 的 GitHub API 本輪回傳 `closed`、`state_reason=not_planned`、`closed_at=2026-08-07T03:00:10Z`。它提供產品方向背景，不足以單獨證明所有 runtime 能力。ACP 的官方定位是 editor/IDE 與 coding agent 的通訊協定，不定義我們的 agent 對等交手或 gates。[ACP Introduction](https://agentclientprotocol.com/get-started/introduction)

## Busy session：修正請求中的過度斷言

不能把背景完成一律寫成「當輪結束後才追加 prompt」。本版本 `prompt` 先寫 user message，再進入 session loop；runner 處於 Running 時會等待既有 run 的結果，Shell 則有 ShellThenRun 路徑。這不是已證明的逐請求 FIFO，也不是必然拒絕；訊息何時被本輪採用、切換 agent/model 的時機、取消／重啟後的結果關聯仍需實測。[prompt.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/session/prompt.ts#L1052)、[runner.ts](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/opencode/src/effect/runner.ts#L115)

## 權限與認證

- 官方設定支援 agent 權限與 `edit`／`bash` 規則；Reviewer 應禁用 edit。Bash 若開放，需足以防止寫入作者分支及繞過限制的白名單與隔離；也可由 controller 的 test runner 執行指定驗證。只 deny edit 不等於所有工具都唯讀。[Permissions](https://opencode.ai/docs/permissions/)
- 若 runtime 只回原生 messages，adapter 保存原文並寫 result，記錄 adapter、session/message IDs 與 digest；Reviewer 不需為了交 result 而取得一般檔案寫入權。結果寫檔與真正證據有效性分開驗證，見 [執行契約](../../workflow/contracts.md#派工與結果)。
- 官方 OpenAI provider 文件列出 ChatGPT 登入及 API key；原生 Anthropic provider 的 API key 路徑有文件依據。本版本文件同時留有 Pro/Max 登入敘述與「1.3.0 起不再內建相關 plugin」說明，不能把前者當成已支援或已授權的登入方式。本輪未登入或測試任一 provider，也未改 credential 設定。[Providers](https://opencode.ai/docs/providers/)、[固定版本 provider 文件](https://github.com/anomalyco/opencode/blob/545f51d26cc39a907d2867492d498d9607ea5fa4/packages/web/src/content/docs/providers.mdx#L332)

## Orca：同版本查證與更正

Durable enqueue、pull/check 與 ack 的既有研究沿用 [orca-capabilities.md](../2026-09-25/orca-capabilities.md#notifications-durable-mailbox-semantics-documented-delivery-not-exercised)，此處只補差異：

1. **Run 群組有範圍，但存在例外。** `@all`／`@idle` 等依 sender 的 Run 選收件者，未綁定 Run 或要求不一致 Run 會拒絕；`@worktree:<id>` 是明示 workspace 的例外，不能概括為所有群組都僅限同 Run。[send-group.ts](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/main/runtime/rpc/methods/orchestration/messaging/send-group.ts#L118)
2. **未綁定 Run 的 sender 並非一律拒絕。** 同版本有 terminal-to-terminal、雙方皆未在 Run 內的測試，訊息保存到 `run_unbound`。因此變更請求的概括敘述未照抄；本輪沒有實際發送來驗證投遞。[send-unbound-terminals.test.ts](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/main/runtime/rpc/methods/orchestration/messaging/send-unbound-terminals.test.ts#L8)
3. **本版本 worker-start 的 model override 不支援 opencode。** Launch preferences 需要 catalog 宣告能力；本機及對應 source 的 catalog 不含 opencode。這只界定 Orca 這個 launch override，不能推論 opencode 自身不支援選模型。[worker-launch-preferences.ts](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/main/runtime/rpc/methods/orchestration/worker/worker-launch-preferences.ts)、[catalog](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/shared/agent-session-option-catalog.ts)
4. **已讀 status plugin 是狀態／內容預覽上報。** 它接收 opencode events、查 session lineage，再向 Orca 上報 lifecycle/attention/message previews；未在此 plugin 證明 Orca → opencode 的任務結果交手。它也不代表 Orca 其他 CLI/mailbox 通道不存在。[factory](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/main/opencode/status-plugin-factory-source.ts)、[lifecycle](https://github.com/stablyai/orca/blob/ee1c52207000c7d70282549c73e9945bd1cec1e8/src/main/opencode/status-plugin-lifecycle-source.ts)

因此「經 controller、以檔案交接」是我們維持結果驗證、去重與單一控制權的設計，不以「兩個產品都完全無法傳訊」作為前提。D14 約束 delivery controller 的持久化；這次沒有決定第三方 runtime 的內部儲存技術。

## 採用候選前的實證缺口

本機尚無可用 opencode runtime。以下為研究列出的測試缺口，尚未批准採用或啟動 V4：

- Reviewer 的 edit 與非白名單 bash 真正被拒絕；可執行的驗證工具不能繞過 branch 隔離。
- 各角色 requested model 與實際 provider/model 一致；不同 session 不混用設定。
- Busy 時 `prompt_async` 的採用順序、結果關聯、取消與恢復，不因 HTTP 204 就重派或宣告成功。
- Idle 後讀回完整結果；分頁、原生錯誤、只有最後 text part 與真正完整 messages 的差異有處理。
- Permission/question 事件可由外部 controller 正確識別與回覆，特別是子 session 的詢問；未知權限問題不默認批准。
- 結果先落檔再通知；crash、遺失事件、同 attempt 重複回傳及外部狀態不明仍符合既有 controller 契約。

Runtime 候選的研究不等於已選 runtime。後續 D30 確認 workflow／controller 核心與底層 runtime/model 實作解耦；使用者已撤回「改用 model」的誤輸入，因此「獨立 Codex」的 runtime/model 定義及是否採用 opencode 仍待選定。這項架構原則不改變上述固定版本研究事實。正式 V4 範圍仍以 [Workflow Design v1](../../workflow/overview.md#10-驗證與交付順序) 為準。
