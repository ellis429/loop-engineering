# Spec Delta

> **D41／D42：scope revision pending（2026-09-27）**。使用者已同意收斂為 orchestrate skill 呼叫薄 controller；舊 S1 修正已停止並保存。本文的 D40 技術內容／AC 是歷史核准基準，尚未完成新 scope 的逐項映射，不是繼續舊計畫的派工授權。三 gates、版本與 finding 覆核維持；新 design／plan 仍須 review 及 D11 確認。歷史 approval.json 保持原樣，不代表本次修訂已核准。最新 [產品目標及邊界](../../../../../docs/project-intent.md)、[決策 D41／D42](../../../../../docs/decisions.md)。

## Purpose

讓單一本機 controller 以人可閱讀的狀態與可追溯外部操作，在 worker、通知、檔案或網路失敗後仍能辨識真實成果與控制權，安全續行或明確 Blocked。本文是本 change 的D40 已核准的規格；D14 的檔案持久化及已確認恢復語意保持，具體 crash 驗收取自設計提案，不指定語言或內部 store 布局。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 `docs/validation/implement-delivery-loop.md` 補齊驗法、通過標準與預期／實際證據。目前尚無產品執行結果，不因規格存在而視為已驗收。

## ADDED Requirements

### Requirement: DUR-01 人可閱讀且單一的現行狀態

MVP SHALL 使用人可閱讀的 JSON/YAML 保存設定與執行狀態，不以 SQLite 取代。使用者 SHALL 可直接找到目前階段、tasks、三 gates 理由、版本、blockers、publication、budget、ownership 與下一個允許 action；finding registry 使用 JSON。Project 狀態 SHALL 引用 run/revision，feature 的現行 gate 只由 run authority 決定，不維護可獨立分歧的第二份 gate。（來源：D02、D08、D14、D24；readability 與 project reference 為檔案設計提案）

#### Scenario: AC-D01 直接檢視狀態
- **WHEN** 使用者打開目前 run 的狀態檔或請求 status
- **THEN** 可辨識當前進度、適用版本、gate/evidence 理由、需人或外部解決的項目及下一步，無須從整份歷史猜測目前結論

#### Scenario: AC-D02 手動修改不是決策
- **WHEN** 設定已變更或有人手改 gate 為 passed，但沒有可核對的 evidence／人工決策
- **THEN** 系統核對新設定 schema/版本並重評受影響結果，不把手改值當批准；合法 decision 經可驗證操作保存來源與理由

### Requirement: DUR-02 唯一派工權與安全重派

同一 repo+feature SHALL 同時只有一個 controller 擁有派工權，實際 worktree SHALL 只有一個有效 writer；不能因 run ID 不同繞過。Workers SHALL 只能寫其被授權 scope 與自己的 result/evidence，不能直接改 run/gates/findings authority。Timeout、lease 到期、runtime 不可查詢或無通知 SHALL 不等於舊 worker 已停止；只有確認停止或已安全解除執行權才可重派。（來源：D02、D08、D13、D23；ownership 具體化來自契約提案）

#### Scenario: AC-D03 兩個 run 搶同一 feature
- **WHEN** 兩個 controller 以不同 run IDs 同時 start/adopt 同一 repo+feature
- **THEN** 最多一方取得派工權，另一方可讀狀態但不得派 writer；衝突及現有 owner 可查

#### Scenario: AC-D04 Worker 狀態 unknown
- **WHEN** worker 超時且 runtime／接入服務無法查詢，或只見 terminal idle／缺少 status
- **THEN** 保存 unknown、原 dispatch identity 與需查明事項，不派競爭 writer；確認停止或有效 fencing 的證據存在後才允許替代 attempt

### Requirement: DUR-03 Assignment 與結果身份契約

Assignment SHALL 保存 run/task/attempt/role、核准 runtime/model 設定、repo/worktree/branch、issue/PR、版本、scope/tools、依賴、AC IDs、skill 版本、結果位置與限制。Result SHALL 可對回相同身份與實際 cwd/head/base/artifacts，將 execution status 與品質 verdict 分開，引用可核對 evidence。Runtime 的原生結果經 adapter 捕捉時 SHALL 保留原文、native session/message IDs、producer 與 digest；不能偽造 native completion。（來源：D01、D02、D08、D19、D30；欄位是契約提案）

#### Scenario: AC-D05 結果未符合派工
- **WHEN** result 的 repo/workspace、attempt、snapshot 或 scope 與 assignment 不符
- **THEN** 系統保留原件並拒絕作適用 gate evidence，顯示具體身份／版本差異，不因 worker 宣稱完成就匯入成功

#### Scenario: AC-D06 只有原生 assistant message
- **WHEN** runtime 完成輸出只能由 adapter 讀 native messages，且 notification 未到
- **THEN** adapter 保存原文與來源 identity，controller 可據完整 result/evidence 核對成果；原生 lifecycle／停止證據不足就如實記未確認，不捏造 Orca worker_done 或其他 runtime 的完成證據

### Requirement: DUR-04 結果先保存且去重匯入

Results、receipts 與 evidence SHALL 在被現行狀態引用前完整保存。相同 attempt 的同一結果 SHALL 只匯入一次；相同 identity 卻有不同內容須保留衝突原件並 Blocked，不能最後一份覆蓋。Implementer 與 Reviewer SHALL 經 controller 交接，通知只帶已保存 result ID/path 喚醒 reconcile，不承載權威 finding/verdict。（來源：D09、D24；atomic result 與衝突語意來自契約提案）

#### Scenario: AC-D07 結果存在但通知遺失
- **WHEN** result 已完整保存但 worker 通知遺失，或 controller 在匯入前 crash
- **THEN** resume/reconcile 核對 assignment、versions、digests 與 evidence 後匯入一次，保留原 attempt，不因漏通知重派

#### Scenario: AC-D08 重複與衝突結果
- **WHEN** 同一 result 重複到達，或同一 attempt 帶不同 bytes 的結果
- **THEN** 同內容只喚醒 reconcile、不重複 state transition／派工／發布；不同內容保留雙方證據並 Blocked 待裁決

### Requirement: DUR-05 Crash 後讀到完整可核對狀態

已確認的 state 更新 SHALL 可在支援的本機檔案系統上持久恢復；讀者只能看到完整舊版或新版，不得讀到半份現行 JSON。Run state SHALL 是恢復 authority，歷史不能形成第二份現行狀態。缺失、無法解析或 schema 不相容 SHALL 明確報錯／Blocked，不覆寫為空 run。此需求的 crash 情境是 file-state 設計提案的可觀察契約；具體寫入、鎖與歷史格式留給 design。（來源：D14 與持久恢復要求；具體化提案）

#### Scenario: AC-D09 State 提交前後 crash
- **WHEN** controller 在更新 state 提交前或提交後被中斷，再次 resume
- **THEN** 讀到完整舊版或新版；已提交版本可恢復，未引用 evidence 不自動成為已接受結果，且不發出未先持久登記的外部操作

#### Scenario: AC-D10 歷史尚未完成
- **WHEN** 現行 state 已提交但歷史尚未完整保存，或存在已保存事件的重複重放
- **THEN** 系統從已持久化事件 identity 補齊歷史且不重複生效；若採 append-only 歷史，損壞尾筆保留診斷原文並安全恢復，中段損壞或同 ID 衝突則 Blocked

#### Scenario: AC-D11 無法信任的 state
- **WHEN** resume 遇到 run state 缺失、無法解析、schema 不相容或衝突
- **THEN** 顯示具體原因與現存檔案，停止派工且保留原資料，不建立空 run 以抹去歷史／budget；未驗證的共享磁碟或多主機 writer 不宣稱受支援

### Requirement: DUR-06 外部操作先登記後執行

派工與 GitHub 寫入 SHALL 在發出前持久保存 operation identity、目標、payload digest、pending 狀態與可查 marker，並保存原生 receipt 與 read-back。外部 outcome unknown SHALL 先查原 operation 的實況；能辨識已完成就收斂到既有結果，無法確認安全重試則 Blocked。檔案 store SHALL 不宣稱可單獨提供外部 exactly-once。（來源：D09、D24；operation 契約為設計具體化提案）

#### Scenario: AC-D12 發文成功但回應遺失
- **WHEN** GitHub 已接受發文，controller 未收到回應而 restart
- **THEN** 依原 marker 查回內容／URL並保存 receipt，更新同一 outbox operation，不再貼一份；review 不重做

#### Scenario: AC-D13 Unknown 無法安全重試
- **WHEN** 外部請求結果 unknown，查不到 marker 且無法證明未執行或可去重
- **THEN** 保留 outcome unknown 與查詢證據並 Blocked，不盲目再派或再貼；明確失敗時只在原操作 retry budget 內恢復

### Requirement: DUR-07 Resume 核對外部實況

Resume SHALL 載入持久 state、核對 ownership、workers、PR/artifacts、results 與待執行 operations，重評版本後只接續最小必要工作。外部變更、停止、未知與既有完成成果 SHALL 分開處理，不能把所有 task 重設 pending。Project 指標落後 SHALL 以已 reconcile 的 run 修復，不覆蓋 feature gate authority。（來源：D08、D14、D24；恢復順序為契約提案）

#### Scenario: AC-D14 Controller restart
- **WHEN** controller 重啟時部分 worker 已完成、某 review 已保存、issue 發布仍 pending
- **THEN** 核對並匯入完成結果，保留適用 review，只恢復 pending 發布及必要工作；不重派完成 task、不清空 findings 或 budget

#### Scenario: AC-D15 恢復時版本已改
- **WHEN** resume 發現外部 head/base/spec 與保存版本不一致
- **THEN** 保存所見版本及失效原因，依 delivery-gates 重評並選擇允許的下一步；不能沿用舊 Pass 或舊 human acceptance 放行

### Requirement: DUR-08 有界時間與操作重試

每個 run SHALL 保存累計主動執行時間、correction round 與逐操作 infra retry 次數；上限為 4h 主動執行、3 輪 correction、每項 infra 操作額外重試 2 次。Implementation 並行度 SHALL 為 1，review 與 CI 可並行。到限 SHALL 停止新派工、處理仍有執行權的 workers，保存理由／證據並 Blocked。Resume、新 session 或另建 run ID 不得自動重置上限。（來源：D13）

Active time 算法、未知 crash interval 計法及 worker/review/CI 的 45/30/30 分鐘候選 timeout 尚待 design+plan 確認；本規格不把 design 的提案視為已批准；待 D11 確認後才採用。

#### Scenario: AC-D16 Infra retry 用盡
- **WHEN** 同一 infra operation 初次失敗及兩次額外重試均無法完成
- **THEN** 保存三次 attempts 與 evidence 並 Blocked；不把診斷出的程式／測試缺陷繼續包裝成 infra retry，改回受三輪限制的 correction 流程

#### Scenario: AC-D17 Active budget 到限與恢復
- **WHEN** 依已核准的計時政策累計主動時間達 4h，或 restart 後讀回已到限 run
- **THEN** 不再派新工作，保存存活 worker／未知 interval 與 Blocked 原因；需調整預算時保存明確使用者裁決，不以等待後自動歸零

### Requirement: DUR-09 Adapter 與 runtime/model 解耦

核心 SHALL 依穩定角色、assignment/result 及能力契約執行，runtime 與 model 為分開的核准設定。系統 SHALL 預設由 OpenCode adapter 執行 agents，依角色設定 provider/model；Orca、Codex／ChatGPT 相關入口及 Claude Code SHALL 為選配，使啟動／resume、派工、結果回收與工作區管理不依賴這些選配程式、設定、帳戶或服務。選配入口的產品名稱不代表已提供可派工 API；僅可使用已查證的接入能力。核心 run/task/attempt identity SHALL 與外部 handles 分開，Orca 專有 Run/Dispatch/terminal 欄位不能成為共用契約的必填條件。派工前 SHALL 核對安裝版本、工具權限、實際 repo/workspace/branch、認證可用性與結果通道；能力不足應具體 Blocked，不自動換用未批准工具或放寬隔離。Credentials、dispatch capabilities 與未清理 runtime logs SHALL 不寫入交接文件或自動進 Git。（來源：D08、D30、D37、D38；preflight 與敏感資料約束為契約提案）

#### Scenario: AC-D18 正確 workspace 與設定
- **WHEN** adapter 的 requested workspace/model 與回傳 identity 或實際執行設定不一致，或只有 input_accepted
- **THEN** 不宣稱派工／工作成功，保存差異與原生 IDs；不能從 shell cwd、`current` 或角色名稱推定實際 placement/model

#### Scenario: AC-D19 能力缺口與替換
- **WHEN** 目前 adapter 不能在核准隔離條件下取得可信結果／lifecycle，而候選 runtime 尚未核准
- **THEN** 系統顯示具體 Blocked 與最小能力需求，保留已取得成果；替換工具仍須符合既有 gates 與獨立 Codex 政策，不把研究報告當成成功實證

#### Scenario: AC-D20 僅有 OpenCode 的部署
- **WHEN** 環境沒有 Orca、Codex CLI、Claude Code 的程式、設定或服務，而已配置並核准 OpenCode、適用模型與必要工具
- **THEN** controller 可直接啟動／resume、派發及核對 OpenCode 任務、回收結果並管理隔離工作區；相同版本、ownership、gates、budget 與持久恢復規則仍成立，不暗中呼叫 Orca、Codex CLI 或 Claude Code

#### Scenario: AC-D21 Runtime 身份不取代共用身份
- **WHEN** 同一 controller 核心分別接收 Orca dispatch 或 OpenCode session/message 的原生識別
- **THEN** 結果可對回自己的 run/task/attempt 與來源 runtime，保留原生回執，不為 OpenCode 補造 Orca ID；通知或任一 runtime 的 idle 狀態仍不能放行 gate

#### Scenario: AC-D22 兩種接法分別驗證
- **WHEN** Orca 接法已驗證通過，但公司 OpenCode 的模型、隔離或 lifecycle 尚未驗證，或反之
- **THEN** 報告按接法保存可用能力與缺口，不共用成功標記；不能藉替換 runtime 自動放寬獨立 Codex review 政策或冒稱完整 E2E 已完成

#### Scenario: AC-D23 未選用的接入故障
- **WHEN** run 選用已核准且可用的 OpenCode profile，而未選用的 Orca、Codex 或 Claude Code 不存在、未登入或連線失敗
- **THEN** controller 不以該選配接入失敗阻斷核心或 OpenCode 路徑，仍按原 profile 核對版本、gates 與預算；不能自動改派其他 runtime/model

#### Scenario: AC-D24 同一 runtime 的不同角色與模型
- **WHEN** Implementer 與 Reviewer 都透過 OpenCode，但各有符合核准角色政策的 provider/model 與獨立 assignment/session
- **THEN** 系統分別保存 runtime 與 requested/actual model 身份，不要求 Claude model 經 Claude Code 或 OpenAI model 經 Codex CLI；只有 Reviewer 模型、完整工具隔離及結果契約均可核對才接受 G2，不能因 runtime 相同就拒絕，也不能因 model 不同就自動宣告獨立
