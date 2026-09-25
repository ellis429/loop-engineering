# Orca runtime probe

日期：2026-09-25。這是獲授權的本機能力驗證，不是產品 implementation、TDD 證據或 feature E2E。

## Scope

建立一個 Orca Run 與兩個 bounded tasks，分別請 Claude Code 和 Codex 讀 README、查實際 Git HEAD 與 runtime version、產出一份 JSON，再透過 native `worker_done` 回報。Worker 不得修改 tracked source、執行 GitHub 寫入、啟動其他 agents 或變更帳戶設定。

原始 receipt 保留於 gitignored `.delivery/capability-probe/`，目錄及檔案限制權限；對外證據只保存不含 dispatch capability 的欄位。執行檔固定 `/usr/local/bin/orca`，Orca 1.4.209 / protocol 36。

## Observed integration

| 能力 | 實際結果 | 設計影響 |
| --- | --- | --- |
| Run / Task 持久化 | 建立成功，後續獨立 CLI subprocess 可查回同一 IDs | Delivery store 可記錄 native IDs；native 狀態不等於 gate verdict |
| Claude supervised dispatch | `ctx_6f0f35db294f` 完成；result 的 HEAD 與 README SHA-256 經協調者重新計算吻合 | 結構化 artifact 與 native execution settlement 分開驗證 |
| Claude prompt delivery | 初始 preamble 被呈現為 pasted content，agent 等待確認；發送有界任務的明確指示後才執行 | `ready/input_accepted` 不是 agent 已執行；啟動 adapter 需觀察 task progress / blocked |
| 通知遺失時的 reconcile 基礎 | 尚未 consume inbox 時，已可讀取 result 與 settled worker；peek 可見 durable completion | 可不依賴通知判斷執行完成；尚未測完整 controller 漏訊息恢復 |
| 結果證據 | [Claude JSON](evidence/claude-probe-result.json) 與 native task/dispatch IDs 對應 | JSON 中宣告 success 仍需另讀證據核對 |
| 原生工作樹建立 | 第一個 attempt 在 `worktree_create` 失敗，錯誤 `spawn Unknown system error -86`，effects 與 residual resources 為空 | 本機預設 git 為不可執行的 Intel binary，與錯誤相符，但尚未證明 Orca 內部實際 spawn 的路徑；不可宣稱已修復 |
| Workspace identity | `current` 指 coordinator 的 Orca workspace；shell cwd 改變不會移動它 | 派工必須比對回傳 worktree path/identity，不能從 shell cwd 推論 |
| Existing terminal identity | `terminal create --worktree current` 建立在同 filesystem path 的主 workspace；`worker-start --worktree current --terminal …` 因 workspace suffix 不同而拒絕 | 必須用 terminal receipt 的完整 workspace ID；使用 inventory 中的 exact ID 後 Codex 派工成功 |
| 新 repo registration | `repo add` 成功；新 repo 的 explicit worker selector 未成功，folder setup 也尚未出現在可用 inventory | 新專案內的隔離 placement 仍未驗證；不能以 gigaxfer 的成功派工冒充 |
| Codex default launch | 第一 attempt 因 `agent-update-prompt` 在 readiness 失敗；native release 成功且 capture archive | 啟動互動提示是可辨識 infra failure，不能當成 agent 已接 task |
| Codex custom launch | 單次 argv 設 `check_for_update_on_startup=false`、`--sandbox workspace-write --ask-for-approval never`；再用 `worker-start --terminal` 納入 supervision，已成功 ready | 保留既有版本與全域設定；外部建立的 terminal 需由建立者在 native release 後清理 |
| Codex artifact | [Codex JSON](evidence/codex-probe-result.json) 存在，SHA / README digest 核對吻合，但 status 是 `blocked`，run ID 是 null | Native preamble 不能取代完整 delivery assignment；controller 必須明確傳入 run ID |
| Codex native completion | sandbox 內 `orca orchestration check/send` 回傳 `runtime_unavailable`；同時間外部 coordinator 能查詢同 runtime | 很可能是 sandbox 與 Orca IPC 的相容性缺口，確切根因未定位；不放寬 sandbox 來宣稱通過 |

原本預計完全使用新 repo 的 worktree。因上述 placement 缺口，真正執行 probe 的 cwd 是既有 `gigaxfer`，只讀既有 README/Git metadata，寫入本次專用 `.delivery/probe/*.json`。這不能證明隔離 worktree 或 reviewer branch protection。兩份結果已逐 byte 比對保存到本 repo 的 evidence 目錄，並清除 probe 自己建立的暫存檔及空目錄；上述原始 report paths 為歷史位置，目前以本頁連結的保存副本為準。

## Lifecycle ledger

Run：`run_95da348b16c4`。

- Claude task `task_e3f33b44e673`：初始 `ctx_a872c8b4fcd3` worktree creation failed，沒有建立 terminal；replacement `ctx_6f0f35db294f` succeeded，已由 `worker-release` 封存 transcript 並關閉它擁有的 terminal。
- Codex task `task_e6fca3e90785`：初始 `ctx_0a6cb777abe9` readiness failed，已 release / archive；replacement `ctx_29e2843ea918` 產出 blocked artifact 並嘗試回報，但 native send 失敗。Provider 活動已 done，transcript 記錄回報失敗。`worker-stop` 回傳 `stop_unknown`，因 terminal 是 external 而沒有關閉它；隨後明確 `worker-abandon` fence dispatch，再關閉本次 operator 自己建立的 exact terminal，receipt 確認 `ptyKilled: true`。
- 最終 [fleet snapshot](evidence/probe-final-fleet.json) 沒有 active dispatch 或 reclaimable terminal。External resource metadata 仍寫 retained / missing_status；這不是 terminal 存活證據。實際關閉依據是 `terminal close` receipt，沒有把缺少 status 解釋成成功。
- Claude completion 在 artifact 保存、核對與 release 後才 consume/ack：delivery `delivery_1162648513b1` 已 acknowledged。未代替 Codex 偽造 `worker_done` 或 completed。
- 未使用的本次 detached Git worktree 已用 `git worktree remove` 移除；未使用 force。
- 兩次 explicit-selector/terminal-workspace preflight rejection 不是品質失敗，不增加 feature correction rounds。它們仍需保留 infra diagnostics，且重试不能無上限。

## 尚未驗證

專用 shell controller identity 的恢復、app restart / host reboot、crash window 的 mutation recovery、重複 notification/outbox 去重、reviewer 寫入限制、新 repo 隔離工作樹、GitHub 發文與 read-after-write、真實 feature delivery 與 G1/G2/G3。

## 結論與下一步

Claude 的 dispatch → 可驗證 artifact → native completion → release 已通；Codex 的 dispatch → 可讀取 artifact 已通，但 native completion 未通。兩者都不是 feature gates 的證據。新 repo placement、sandbox 內 Orca IPC、明確 assignment IDs 是進入真實 demo 前需解決的整合缺口。

Adapter 設計必須先驗證指定 cwd、允許的工具與可用 lifecycle channel；若無法完成，報具體 Blocked。Artifact reconcile 應能保存部分成果，而不是因通知失敗重做工作。仍需研究保持 reviewer 隔離時可用的正式通知整合，不以 credentials / dispatch capability 搬運或關閉 sandbox 作替代。
