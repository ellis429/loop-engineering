# Spec Delta

> **D53 採用（2026-09-28）**：本文依 D11（D53）採用，由「正式 specs 原文＋D45-02 spec-delta（sha256 `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565`）＋D45-04 spec-delta（sha256 `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b`）」依 D45-04 spec-delta §12 組成；逐項來源見 [source-map](../../adoption/source-map.md)。
> - orchestrate 是同一 feature 唯一的外層協調循環；
> - 薄 controller 是狀態、交接／版本核對、gates 與 findings 的唯一寫入與判定入口；
> - 第一條實作路徑是 Herdr 原生 sessions／panes／worktrees（D45）。
>
> D47–D49 的政策邊界已併入相關 requirement。D40 的 approval、舊 S1 程式、測試與 review 只作歷史紀錄，不是本版的核准或證據。

## Purpose

讓同一 feature 在單一本機以一份人可閱讀的狀態與可追溯的外部操作運作，在 worker、通知、檔案或網路失敗後，仍能辨識真實成果與協調權，安全續行或明確 Blocked。本文是 D45–D49 修訂後的規格；D14 的檔案持久化及已確認恢復語意保持，具體 crash 驗收取自設計提案，不指定語言或內部 store 布局。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 D53 採用的 `docs/design-candidate/d45-04/validation.md` 補齊驗法、通過標準與預期／實際證據。目前尚無產品執行結果，不因規格存在而視為已驗收。

## ADDED Requirements

### Requirement: DUR-01 人可閱讀且單一的現行狀態

MVP SHALL 使用人可閱讀的 JSON/YAML 保存設定與執行狀態，不以 SQLite 取代。使用者 SHALL 可直接找到目前階段、tasks、三 gates 理由、版本、blockers、publication、budget、ownership 與下一個允許 action；finding registry 使用 JSON。同一 repo＋feature SHALL 只有一份現行狀態 authority；run 或 epoch 只是其中的紀錄，不是另一份 authority。Project 狀態只引用 feature identity 與 revision，不維護可獨立分歧的第二份 gate。系統 SHALL 只有一套生效的狀態／CLI 入口，不與舊實作並存（D46）。（來源：D02、D08、D14、D24；readability 與 project reference 為檔案設計提案）

#### Scenario: AC-D01 直接檢視狀態
- **WHEN** 使用者打開目前 run 的狀態檔或請求 status
- **THEN** 可辨識當前進度、適用版本、gate/evidence 理由、需人或外部解決的項目及下一步，無須從整份歷史猜測目前結論

#### Scenario: AC-D02 手動修改不是決策
- **WHEN** 設定已變更或有人手改 gate 為 passed，但沒有可核對的 evidence／人工決策
- **THEN** 系統核對新設定 schema/版本並重評受影響結果，不把手改值當批准；合法 decision 經可驗證操作保存來源與理由。手改可被偵測，且永不當作決策。本版以可信本機協作為前提，不承諾抵抗同一 OS 帳號下的惡意整套偽造（D48）。

### Requirement: DUR-02 唯一派工權與安全重派

同一 repo＋feature SHALL 同時只有一個持有協調權的 orchestrate 能從 controller 取得派工許可。Run ID、epoch、session 或 clone 不同，SHALL NOT 產生第二份協調權或預算；實際 worktree SHALL 只有一個有效 writer。Workers SHALL 只能寫其授權 scope 與自己的 result／evidence 投遞位置，並由 runtime 權限設定拒絕呼叫狀態寫入命令。此限制 SHALL 以真實 runtime 負例驗證，未驗證的 profile SHALL NOT 被默認可用。系統 SHALL 對可核對的身份、版本、digest、lineage 或狀態竄改不符保存證據並 Blocked；不承諾偵測或阻止同一 OS 帳號下繞過 runtime 權限的惡意整套偽造（D48；D45-S02）。Timeout、lease 到期、runtime 不可查詢或無通知 SHALL 不等於舊 worker 已停止；只有確認停止或已安全解除執行權才可重派。（來源：D02、D08、D13、D23；ownership 具體化來自契約提案）

第一片中，每個 feature SHALL 只有一個 Implementer worktree，tasks 與 fix 依序執行。Reviewer SHALL 使用獨立的 clone 與 session。平行 writer **[延後 S2]** 需要另外定義規則，並經 D11 確認；第一片不提供。

#### Scenario: AC-D03 兩個 run 搶同一 feature
- **WHEN** 兩個 controller 以不同 run IDs 同時 start/adopt 同一 repo+feature
- **THEN** 最多一方取得協調權；另一方可讀狀態，但不能取得派工許可或新預算。衝突與現有協調者可查。

#### Scenario: AC-D04 Worker 狀態 unknown
- **WHEN** worker 超時且 runtime／接入服務無法查詢，或只見 terminal idle／缺少 status
- **THEN** 保存 unknown、原 dispatch identity 與需查明事項，不派競爭 writer；確認停止或有效 fencing 的證據存在後才允許替代 attempt。已知 active 的 worker 到期時，可以對它發停止並讀回；確認停止前不派替代 attempt。

  「確認停止或 idle」SHALL 以可核對的權威證據判定，二選一：
  - 該 attempt 的結果已匯入，**且** native 紀錄顯示該 turn 已完成；
  - stop 已經過 process-info 確認。

  terminal idle、runtime 的 idle／done 狀態，SHALL NOT 單獨作為 writer 已結束的證據。

### Requirement: DUR-03 Assignment 與結果身份契約

Assignment SHALL 保存 run/task/attempt/role、核准 runtime/model 設定、repo/worktree/branch、issue/PR、版本、scope/tools、依賴、AC IDs、skill 版本、結果位置與限制。Result SHALL 可對回相同身份與實際 cwd/head/base/artifacts，將 execution status 與品質 verdict 分開，引用可核對 evidence。Runtime 的原生結果經 adapter 捕捉時 SHALL 保留原文、native session/message IDs、producer 與 digest；不能偽造 native completion。（來源：D01、D02、D08、D19、D30；欄位是契約提案）

外部 handles（Herdr session／workspace／pane／agent name、runtime native session ID）SHALL 與 run／task／attempt identity 分欄保存。name 只用於定位，不作身份證據。

#### Scenario: AC-D05 結果未符合派工
- **WHEN** result 的 repo/workspace、attempt、snapshot 或 scope 與 assignment 不符
- **THEN** 系統保留原件並拒絕作適用 gate evidence，顯示具體身份／版本差異，不因 worker 宣稱完成就匯入成功

#### Scenario: AC-D06 只有原生 assistant message
- **WHEN** runtime 完成輸出只能由 runtime 讀回工具 讀 native messages，且 notification 未到
- **THEN** runtime 讀回工具 保存原文與來源 identity，controller 可據完整 result/evidence 核對成果；原生 lifecycle／停止證據不足就如實記未確認，不捏造 Orca worker_done 或其他 runtime 的完成證據

### Requirement: DUR-04 結果先保存且去重匯入

Results、receipts 與 evidence SHALL 在被現行狀態引用前完整保存。相同 attempt 的同一結果 SHALL 只匯入一次；相同 identity 卻有不同內容須保留衝突原件並 Blocked，不能最後一份覆蓋。Implementer 與 Reviewer SHALL 經 controller 交接，通知只帶已保存 result ID/path 喚醒 reconcile，不承載權威 finding/verdict。（來源：D09、D24；atomic result 與衝突語意來自契約提案）

#### Scenario: AC-D07 結果存在但通知遺失
- **WHEN** result 已完整保存但 worker 通知遺失，或 controller 在匯入前 crash
- **THEN** orchestrate 經 controller 讀回核對 assignment、versions、digests 與 evidence 後匯入一次，保留原 attempt，不因漏通知重派

#### Scenario: AC-D08 重複與衝突結果
- **WHEN** 同一 result 重複到達，或同一 attempt 帶不同 bytes 的結果
- **THEN** 同內容只喚醒 reconcile、不重複 state transition／派工／發布；不同內容保留雙方證據並 Blocked 待裁決

### Requirement: DUR-05 Crash 後讀到完整可核對狀態

已確認的 state 更新 SHALL 可在支援的本機檔案系統上持久恢復；讀者只能看到完整舊版或新版，不得讀到半份現行 JSON。Run state SHALL 是恢復 authority，歷史不能形成第二份現行狀態。缺失、無法解析或 schema 不相容 SHALL 明確報錯／Blocked，不覆寫為空 run。此需求的 crash 情境是 file-state 設計提案的可觀察契約；具體寫入、鎖與歷史格式留給 design。（來源：D14 與持久恢復要求；具體化提案）

#### Scenario: AC-D09 State 提交前後 crash
- **WHEN** controller 在更新 state 提交前或提交後被中斷，再次 resume
- **THEN** 讀到完整舊版或新版；已提交版本可恢復，未引用 evidence 不自動成為已接受結果，且不發出未先持久登記的外部操作

#### Scenario: AC-D10 歷史尚未完成
- **WHEN** 現行 state 更新時被中斷，或同一 transition 被重複提交
- **THEN** 已提交的 revision SHALL 可恢復，而且不重複生效；中斷時尚未提交的變更 SHALL NOT 被接受，只可保留作診斷；同一 transition identity 內容不同時 SHALL Blocked。系統 SHALL NOT 以事件重放作為第二份現行狀態來源。

#### Scenario: AC-D11 無法信任的 state
- **WHEN** resume 遇到 run state 缺失、無法解析、schema 不相容或衝突
- **THEN** 顯示具體原因與現存檔案，停止派工且保留原資料，不建立空 run 以抹去歷史／budget；未驗證的共享磁碟或多主機 writer 不宣稱受支援

### Requirement: DUR-06 外部操作先登記後執行

派工與 GitHub 寫入 SHALL 在發出前持久保存 operation identity、目標、payload digest、pending 狀態與可查 marker，並保存原生 receipt 與 read-back。外部 outcome unknown SHALL 先查原 operation 的實況；能辨識已完成就收斂到既有結果，無法確認安全重試則 Blocked。檔案 store SHALL 不宣稱可單獨提供外部 exactly-once。（來源：D09、D24；operation 契約為設計具體化提案）

**外部寫入**限於有限種類：worktree 建立、派工、prompt、stop、push、PR ensure、PR 與 issue 發布。每種 SHALL 先登記，再只被一個呼叫者執行一次，並保存 receipt。結果不明時，SHALL 只讀回原操作，SHALL NOT 重發。以下情況 SHALL NOT 作為重試證明：查不到效果、client 已結束、經常駐 server 或遠端處理的請求。只有在以下情況才可重試：已有權威證據證明原請求未送達，或已完成且排除之後才生效；或外部操作有已驗證的原生冪等。否則 unknown 並 Blocked。以查詢判斷 PR 是否存在 SHALL NOT 視為冪等：建立 PR 的結果不明、之後又查不到時，SHALL NOT 再建立第二次（D51-R01）。自動讀回每次 SHALL 計入上限（包括原操作仍在執行、結果未定的那次）；到限仍無法確認時 SHALL Blocked 並停止自動讀回，直到人工 decision 授權一次新的讀取核對；worker 維持 active／unknown，SHALL NOT 重送（D45-S06）。

**PR ensure 的身份** [R12]：外部呼叫之前，SHALL 先持久化預期身份（repo、head repo 與 branch、目前 head SHA、base repo 與 branch）與唯一的 operation marker。沿用既有 PR SHALL 要求上述身份全部相符，並記錄為既有 PR，SHALL NOT 記成本次建立；任一欄不符（包括同 branch、不同 base）SHALL Blocked，SHALL NOT 另建。結果不明後的讀回 SHALL 同時要求 marker 與完整身份相符，才算本次建立成功。

**人工處理 unknown** [R12]：人工 decision SHALL 只記錄，SHALL NOT 執行外部寫入。綁定觀察到的結果時，SHALL 先以新的讀取核對它符合預期身份；標記未送達時，SHALL 附上未送達的證據，查不到效果本身 SHALL NOT 算證據。之後的重試仍受原有的重試上限。

**Branch 歷史** [R12]：受控 run 期間，feature branch SHALL 只以一般 fast-forward push 更新；SHALL NOT rebase、squash 或 force-push。這不是 repo 全域規則。整合 base 所用的 merge commit 是 feature branch 上的本機 git 操作，SHALL NOT 被視為或需要 GitHub PR merge 權限；外部寫入種類 SHALL NOT 因此增加 merge（AC-O10 不變）。

**唯讀觀察** SHALL NOT 需要執行許可。每次取得之前 SHALL 先持久化一個單調遞增的順序識別，並依此順序匯入；請求脈絡與觀察到的事實 SHALL 分開保存。共用的版本事實 SHALL 由 feature 層級、跨所有目的的水位保護：只有比水位新的觀察才能更新，而且更新時 SHALL 使相關 gates 與 Pass 失效；晚到的舊觀察 SHALL NOT 恢復舊版本。各目的的快取 SHALL 分開保存，只在觀察到的版本等於目前版本時才可作為 gate 依據。

**讀取失敗預算**：同一個邏輯讀取目標（目的＋對象）的連續傳輸失敗 SHALL 持久計數，SHALL NOT 因新的順序識別、session 或 restart 而重置。初次加兩次重試都失敗後 SHALL Blocked，並停止自動讀取，也 SHALL NOT 自動取得新的額度。之後只有明確的人工 decision 能授予一次新的有界額度，而且不重置其他計數。成功取得但內容為 pending，不算失敗。

#### Scenario: AC-D12 發文成功但回應遺失
- **WHEN** GitHub 已接受發文，協調者未收到回應即中斷，之後再續行
- **THEN** 依原 marker 查回內容／URL並保存 receipt，更新同一 outbox operation，不再貼一份；review 不重做

#### Scenario: AC-D13 Unknown 無法安全重試
- **WHEN** 外部請求結果 unknown，查不到 marker 且無法證明未執行或可去重
- **THEN** 保留 outcome unknown 與查詢證據並 Blocked，不盲目再派或再貼；明確失敗時只在原操作 retry budget 內恢復

### Requirement: DUR-07 Resume 核對外部實況

Resume SHALL 載入持久 state、核對 ownership、workers、PR/artifacts、results 與待執行 operations，重評版本後只接續最小必要工作。外部變更、停止、未知與既有完成成果 SHALL 分開處理，不能把所有 task 重設 pending。Project 指標落後 SHALL 以已 reconcile 的 run 修復，不覆蓋 feature gate authority。（來源：D08、D14、D24；恢復順序為契約提案）

#### Scenario: AC-D14 Controller restart
- **WHEN** controller 重啟時部分 worker 已完成、某 review 已保存、issue 發布仍 pending
- **THEN** orchestrate 經 controller 核對並匯入已完成的結果，保留適用的 review，只恢復 pending 發布與必要工作；不重派已完成的 task，不清空 findings 或 budget。無法確認 worker、worktree 或協調者狀態的部分停止並交人，不承諾自動修復。

#### Scenario: AC-D15 恢復時版本已改
- **WHEN** resume 發現外部 head/base/spec 與保存版本不一致
- **THEN** 保存所見版本及失效原因，依 delivery-gates 重評並選擇允許的下一步；不能沿用舊 Pass 或舊 human acceptance 放行

### Requirement: DUR-08 有界時間與操作重試

每個 run SHALL 保存累計主動執行時間、correction round 與逐操作 infra retry 次數；上限為 4h 主動執行、3 輪 correction、每項 infra 操作額外重試 2 次。Implementation 並行度 SHALL 為 1，review 與 CI 可並行。到限 SHALL 停止新派工、處理仍有執行權的 workers，保存理由／證據並 Blocked。Resume、新 session 或另建 run ID 不得自動重置上限。（來源：D13）

協調 session 在線時，系統 SHALL 以有界等待檢查期限，對已知 active 的 worker 發停止，並以讀回確認；這些停止與讀回 SHALL NOT 被其他 blocker 或無關的進行中操作阻擋。協調 session 離線期間，系統不保證準時停止。恢復時 SHALL 將無法排除的活動期間計入、記錄超時量、處理仍在執行的 worker，並 Blocked 交人；unknown SHALL NOT 被視為已停止。停止的讀回同樣有次數上限；到限仍無法確認時 SHALL Blocked 交人，不重送停止，也不無限輪詢（D45-S06）。本版不新增常駐 watchdog，也不預設加硬截止 wrapper（D47）。

Active time 以 design 定義的活動區間聯集計算；未知區間的計入方式、worker／review／CI 的 timeout 與到限路徑，以 D11 核准的 design 與政策檔 `workflow.yaml` 的 `timeouts` 為準；變更 SHALL 經人工 `policy_change`。讀回上限只適用於外部寫入；唯讀觀察依 DUR-06 的讀取失敗預算。

#### Scenario: AC-D16 Infra retry 用盡
- **WHEN** 同一 infra operation 初次失敗及兩次額外重試均無法完成
- **THEN** 保存三次 attempts 與 evidence 並 Blocked；不把診斷出的程式／測試缺陷繼續包裝成 infra retry，改回受三輪限制的 correction 流程

#### Scenario: AC-D17 Active budget 到限與恢復
- **WHEN** 累計主動時間達 4h 時協調 session 在線；或到限發生在協調 session 離線期間，之後恢復；或 restart 後讀回已到限的 run
- **THEN** 不再派新工作。在線時對已知 active worker 發停止並讀回確認；離線時在恢復時計入無法排除的期間、記錄超時量，並處理仍在執行的 worker。之後保存 unknown 區間與 Blocked 原因；停止無法確認時維持 active／unknown，不視為已停止。要調整預算，需保存明確的使用者裁決，不因等待而自動歸零。

### Requirement: DUR-09 Adapter 與 runtime/model 解耦

核心 SHALL 依穩定角色、assignment/result 及能力契約執行，runtime 與 model 為分開的核准設定。OpenCode SHALL 仍是預設 runtime（D38），依角色設定 provider/model。第一條本機實作路徑 SHALL 由 Herdr 原生 sessions／panes／worktrees 啟動 OpenCode（OpenAI models）與 Claude Code（Claude models）（D44／D45），不引入另一套外層 orchestrator。Transport、runtime、provider 與 model SHALL 分欄保存；Herdr SHALL NOT 成為所有部署環境的必要依賴。Orca、Codex／ChatGPT 相關入口及 Claude Code SHALL 為選配，使啟動／resume、派工、結果回收與工作區管理不依賴這些選配程式、設定、帳戶或服務。選配入口的產品名稱不代表已提供可派工 API；僅可使用已查證的接入能力。核心 run/task/attempt identity SHALL 與外部 handles 分開，Orca 專有 Run/Dispatch/terminal 欄位不能成為共用契約的必填條件。派工前 SHALL 核對安裝版本、工具權限、實際 repo/workspace/branch、認證可用性與結果通道；能力不足應具體 Blocked，不自動換用未批准工具或放寬隔離。Credentials、dispatch capabilities 與未清理 runtime logs SHALL 不寫入交接文件或自動進 Git。（來源：D08、D30、D37、D38；preflight 與敏感資料約束為契約提案）

#### Scenario: AC-D18 正確 workspace 與設定
- **WHEN** adapter 的 requested workspace/model 與回傳 identity 或實際執行設定不一致，或只有 input_accepted
- **THEN** 不宣稱派工／工作成功，保存差異與原生 IDs；不能從 shell cwd、`current` 或角色名稱推定實際 placement/model

#### Scenario: AC-D19 能力缺口與替換
- **WHEN** 目前 adapter 不能在核准隔離條件下取得可信結果／lifecycle，而候選 runtime 尚未核准
- **THEN** 系統顯示具體 Blocked 與最小能力需求，保留已取得成果；替換工具仍須符合既有 gates 與獨立 Codex 政策，不把研究報告當成成功實證

#### Scenario: AC-D20 僅有 OpenCode 的部署
- **WHEN** 環境沒有 Orca、Codex CLI、Claude Code 的程式、設定或服務，而已配置並核准 OpenCode、適用模型與必要工具
- **THEN** orchestrate 可經 OpenCode-only 的工具接法啟動／resume、派發，並由 controller 核對 OpenCode 任務、回收結果並管理隔離工作區；相同版本、ownership、gates、budget 與持久恢復規則仍成立，不暗中呼叫 Orca、Codex CLI 或 Claude Code
- **切片**：[延後] 由後續切片負責，第一片不算完成（D45-04 spec-delta §8）。

#### Scenario: AC-D21 Runtime 身份不取代共用身份
- **WHEN** 同一 controller 核心分別接收 Herdr handles、Orca dispatch 或 OpenCode session/message 的原生識別
- **THEN** 結果可對回自己的 run/task/attempt 與來源 runtime，保留原生回執，不為 OpenCode 補造 Orca ID；通知或任一 runtime 的 idle 狀態仍不能放行 gate

#### Scenario: AC-D22 兩種接法分別驗證
- **WHEN** 任一接法（Herdr、OpenCode-only、Orca）已驗證通過，而另一接法的模型、隔離或 lifecycle 尚未驗證
- **THEN** 報告按接法保存可用能力與缺口，不共用成功標記；不能藉替換 runtime 自動放寬獨立 Codex review 政策或冒稱完整 E2E 已完成

#### Scenario: AC-D23 未選用的接入故障
- **WHEN** run 選用已核准且可用的 profiles（第一片：Herdr＋Claude Code 的 Implementer、Herdr＋OpenCode 的 Reviewer），而未選用的接入（Orca、Codex CLI 或其他 profile）不存在、未登入或連線失敗
- **THEN** controller SHALL NOT 以未選用接入的失敗阻斷已選路徑，仍按原 profile 核對版本、gates 與預算，SHALL NOT 自動改派其他 runtime／model。已選 profile 本身不可用或未驗證時 SHALL Blocked。只用 OpenCode 的部署下同一情境 **[延後 S2，隨 AC-D20]**。

#### Scenario: AC-D24 同一 runtime 的不同角色與模型
- **WHEN** Implementer 與 Reviewer 都透過 OpenCode，但各有符合核准角色政策的 provider/model 與獨立 assignment/session
- **THEN** 系統分別保存 runtime 與 requested/actual model 身份，不要求 Claude model 經 Claude Code 或 OpenAI model 經 Codex CLI；只有 Reviewer 模型、完整工具隔離及結果契約均可核對才接受 G2，不能因 runtime 相同就拒絕，也不能因 model 不同就自動宣告獨立

- **切片**：[延後] 由後續切片負責，第一片不算完成（D45-04 spec-delta §8）。