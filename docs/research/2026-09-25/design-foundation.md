# Design foundation

狀態：完整 delivery loop 的設計準備稿；不是已批准的 design 或 implementation plan。持久化已依 D14 改為 JSON/YAML；D15/D16 選定先做 [gigaxfer pre-PR gating 實驗](../../experiments/pr-gating.md)。後續正式 artifacts 會吸收本稿，以 OpenSpec 為權威。

## 責任與最小實作方向

已選擇一個 lead agent、一個持久化 controller，以及 Orca supervised workers。Lead agent 協助需求與 finding 判斷；controller 擁有排程、版本驗證、狀態轉移、重試與發布。Orca Run/Task/Dispatch 只承擔執行身分與生命週期。

2026-09-26 依 D14 修訂：建議採 Python CLI、人可讀 JSON／YAML 與不可覆寫的 evidence files，移除 SQLite 提案。本機 Python 3.10.10、uv 0.11.24 已查核，正式最低 Python 版本會在 design 選定。狀態一致性使用單一 writer、檔案鎖與原子 snapshot 替換，詳見 [檔案狀態設計](../../file-state.md)。Runtime adapters 應位於窄介面後，state machine 不直接讀自由文字終端輸出。

測試邊界是對使用者有意義的行為：restart 不重派、舊版本不放行、部分結果保留、未解決阻擋不消失、發文失敗只重試發文。不要用驗證私有函式呼叫次數取代上述可觀察結果。

## 狀態與執行是不同維度

建議 run phase：`discovery → awaiting_design_approval → implementing → validating → reviewing → correcting → ready_for_acceptance`，任何 phase 可因明確原因轉 `blocked`。`reviewing` 同時追蹤獨立 review 和 CI，而不是先後串成單一 job。

- Task execution：`pending / running / succeeded / failed / blocked / unknown`。
- Gate assessment：`missing / pending / passed / failed / stale / unknown`。
- Review verdict：`clean / changes_required / blocked`。
- Publication：`pending / publishing / published / failed / outcome_unknown`。

例如 reviewer 成功完成但找到 bug：execution 是 succeeded、verdict 是 changes_required、G2 是 failed。CI 尚未完成時繼續等待相同版本的 CI，再建立合併修正批次。GitHub 發文失敗不清除已完成的 review，也不重新派 reviewer。

`ready_for_acceptance` 是針對一個明確版本的 PR Pass 紀錄。後來 push 不應改写歷史紀錄；應使目前 run 的現行 gates 失效並重新開始必要驗證。對外狀態必須顯示評估時間及版本，避免將歷史 Pass 當作現在的無條件保證。

## 版本集合

每個交接物引用完整版本集合，而非只存 branch name：

| 欄位 | 用途 |
| --- | --- |
| repository identity / PR number | 防止跨 repo、跨 PR 結果誤配 |
| PR head SHA | 最終整合程式版本 |
| target base tip SHA / review merge-base SHA | 清楚區分目前目標分支與完整 PR diff 的固定起點 |
| project spec / feature spec digests | OpenSpec baseline 與 change delta 的適用內容 |
| design / plan / workflow policy digests | 設計、派工範圍及判定規則的版本 |
| controller / skill bundle versions | 可追查使用哪個執行器與方法，不讓 runtime 自我更新 |

Spec 連結只負責定位；digest 對應讀到的實際 bytes，另保留可讀取 snapshot。Issue 本文被編輯，也會形成新的 feature spec 版本。Project 和 feature 衝突必須人工裁決，不能用最後修改時間自動勝出。

建議 MVP 保守規則：任一 head/base/spec/design/plan/policy 變更，都不沿用目前 G1/G2/G3 的最終 Pass；可保存歷史 Red 供重新判定 lineage。就算 CI 在相同 head 仍為 green，控制器也必須在新的版本集合重新查詢，不能直接使用上次 cache。正式 spec 應區分「gate 重評」與「GitHub CI rerun」：新 head 一定需新 head 的必要檢查；單純文件版本變更可重評同 head 的可適用 CI，但 review 必須讀新文件。

## 派工與結果契約

Assignment 至少包含 delivery run/task/attempt IDs、role、native Orca IDs、repo/worktree/branch、issue/PR、完整版本集合、允許修改 scope、dependencies、AC IDs、必要 skill manifest、結果輸出位置。

Result 至少包含對應 IDs、schema version、execution status、實際 cwd / SHA / version bindings、summary、evidence references、findings、pending decisions。對不存在或未取得的欄位要回報 blocked，不能猜測。

Controller 先保存 assignment 和 operation intent，再發出外部呼叫；回來保存 request ID 與 receipt。重啟遇到 `outcome_unknown` 必須查詢原 operation/native dispatch，禁止直接新派 editor。API 若不支援 caller-selected idempotency key，不能聲稱 exactly-once；需保存 operation marker、reconcile 或保守 Blocked。

Result 先寫完整檔案後以 atomic rename 發布，再通知；controller 讀取固定路徑、驗證 schema/ID/version/digest、檢查實際 evidence，才在鎖內將 result ID、相關 findings 和待執行操作一併寫入新的 `run.json` snapshot。同一 attempt 重送不同內容是衝突，不能 last-write-wins。

## Finding 與修正

Finding 保存穩定 ID、來源、blocking/severity、位置、問題依據、預期行為、狀態、修正 commit 與覆核 evidence。第一次建立 identity，後續 review 直接引用舊 ID；檔案改名或行號改變不能自動算新問題或自動結案。

實作者只能提出 `fix_submitted` 或 `disputed`。Reviewer 針對最新完整版本確認修正後才能變 `resolved`；人工裁決另存明確 actor、理由、版本與依據，不能冒充 reviewer clean。新問題仍需檢查，不只比對舊 findings。

Correction round 在同版本失敗結果形成一次修正批次時記一次，不依 finding 數、agent subprocess 數或 CI job 數計算。Infra retry 只處理已證明的基礎設施失敗，不得拿來包裝測試失敗，以繞過三輪上限。

## CI 判定

Required checks 來自明確 repo policy，並與可讀取的 GitHub protection/rules 核對。不能因 repo 沒有 branch protection 就把空 check 集合當成 clean。需要分辨 check-run 與 commit status、同名 check 的來源、舊 attempt 與新 attempt，並处理 pagination。

建議每項 policy 指定 check name/context、source/app（適用時）、接受的 conclusion。預設只接受 success；missing、pending、cancelled、timeout、neutral、skipped、unknown 均不通過。Repo-specific skipped/neutral 豁免必須是明確 policy，不從 agent 自述推導。

Pass 前重新取得 PR 的 head/base 與當前版本資訊，確認沒有變動；若變動，丟棄本次 Pass 轉移並 reconcile。GitHub 沒有跨多次讀取的整體 transaction，因此 Pass 應帶 observation timestamp，監控期間發現後續 push 就撤銷現行結論，不能宣稱外部世界永遠不會變動。

## 恢復與資源

一份原子替換的 `run.json` 保存現況與待執行操作；單一 controller lock 防止兩個 loop 同時控制一個 run。JSONL 事件紀錄與結果檔案、receipts 保留，通知只做 wakeup。定期 reconcile 查 result、Orca task/dispatch、PR revision 和 CI，處理遺失通知及 crash windows。狀態檔仍需 schema、revision 與完整性檢查，讀取失敗不能假設為空白新 run。

Worker timeout 不等於 worker dead。外部實況 unknown 時保留執行權與 worktree，不派競爭 editor；只有原生已失敗/停止的證據才允許 replacement。Resource cleanup 根據 ownership：原生建立的 terminal 用 native release；controller 自建且已解除 dispatch authority 的 terminal 才由自己關閉。

本機 probe 已揭露三項需在 adapter preflight 處理的真實風險：`current` 跟隨 coordinator workspace；預設 Git binary 不可執行；Codex sandbox 內 Orca IPC 尚未通。正式 plan 應把有界整合驗證安排在廣泛功能開發之前，失敗就帶證據呈現缺口，不用假 adapter 的通過掩蓋。

## 待本輪決定後完成

先依 D15/D16 完成 PR gating 接入的具體 design/plan，確認 Q-TARGET 與 Q-PUBLISH；已有實作的 G1 先查核原始證據，不以接入前未受 controller 追蹤為理由放行。一般化 Q-TDD 方法/N/A 政策留待完整流程定案。正式 artifacts 與執行計畫仍提交 D11 的一次具體開工前確認。
