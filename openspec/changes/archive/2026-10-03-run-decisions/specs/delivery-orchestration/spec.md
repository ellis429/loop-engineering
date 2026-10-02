## ADDED Requirements

### Requirement: ORC-01 共同入口、角色責任與授權

Controller SHALL 是 feature 狀態與人工決策紀錄的唯一寫入入口；每次被呼叫時完成核對或狀態更新後即返回，SHALL NOT 常駐、啟動 agents 或執行呼叫者提供的命令。可執行的動作 SHALL 只依協調權（claim token）與人工 decision 判定，SHALL NOT 由共同入口、session 名稱或 runtime 父子關係推定決策權。使用者 SHALL 可直接把 feature 交給 Implementer，不必經 Project Lead 轉達。未支援的入口（`adopt`、`delegate`）SHALL 明確回 `unsupported`，狀態不變。

#### Scenario: AC-O01 直接與 Implementer 協作
- **WHEN** 使用者直接把已選定的 feature 交給 Implementer，Implementer 以 `init` 建立 run
- **THEN** run 進入 design／plan 準備階段，保存協調者 identity；不需要 Project Lead 的交接紀錄，也不因此產生開工確認或 scope 變更的權限

#### Scenario: AC-O19 入口與 runtime 關係不授予決策權
- **WHEN** agent 使用與人相同的入口呼叫 `decide`，或自稱由 Project Lead 或使用者的 session 派出
- **THEN** 只有 actor 為 `human:<name>` 的 decision 被接受；其他 actor 一律拒絕且狀態不變，不從入口或父子關係新增委派權或 scope 變更權

#### Scenario: AC-O30 未支援的入口
- **WHEN** 呼叫 `adopt` 或 `delegate`
- **THEN** 回 `unsupported`，狀態的 revision 不變，也不略過任何開工確認或協調權的核對

### Requirement: ORC-02 單一交付單位與原生文件 binding

每個 run SHALL 綁定一個 repo 與一個 feature。登記的 plan 與文件 binding SHALL 保存角色、來源、locator、revision、digest 與採用內容，使用工具原生的文件名稱與實際位置，不另建同義副本；讀不到的文件 SHALL 拒絕登記。

#### Scenario: AC-O03 引用既有文件
- **WHEN** feature 以 issue 內文、既有的 plan 檔（例如 `docs/superpowers/plans/P03-ingest.md`）或 OpenSpec change 當作 binding 登記
- **THEN** 狀態保留實際位置、適用版本與 digest，並能讀回登記時的內容；檔案不被改名或搬移。locator 讀不到時拒絕登記，狀態不變

### Requirement: ORC-03 可驗證 AC 與一次開工確認

開工確認 SHALL 針對一個登記過的 plan 版本，由人以 `approve_plan` 做一次；plan SHALL 由 Implementer 校準，spec、AC 與 design 的 binding SHALL 已登記。沉默、逾時或 agent 的同意 SHALL NOT 視為批准。改變 AC、spec 或已核准設計 SHALL 經 `scope_change` 回到等待批准，舊核准失效。

#### Scenario: AC-O05 新 feature 尚未批准
- **WHEN** plan 已登記，但還沒有適用該版本的人工 `approve_plan`
- **THEN** `status` 顯示等待開工確認與待確認的 plan 版本，`next` 回報需要人工決策；經過任何時間或 agent 的表示都不產生核准

#### Scenario: AC-O29 binding 不齊時不能批准
- **WHEN** 人對一個 plan 版本執行 `approve_plan`，但 spec、AC 或 design 的 binding 有任何一項沒有登記
- **THEN** 拒絕並列出缺少的 binding，狀態不變；三者都登記後，同一個 plan 版本才能被批准

#### Scenario: AC-O07 需求變更不混入修正
- **WHEN** 發現需要改 AC、spec 或已核准的設計，或使用者提出範圍外的想法，由人記錄 `scope_change`
- **THEN** 保存影響與理由，撤銷目前的核准，run 回到等待批准，舊 plan 標為 superseded；登記新版本並重新批准後，`next` 才回報可以往下走

### Requirement: ORC-07 Retro 只產候選

Controller SHALL NOT 接管沒有以明確 `init` 啟動的工作，SHALL NOT 產生 Retro 候選或啟動 PR gating；Retro 候選由 project-lead skill 承接（D55）。產品 SHALL NOT 含針對特定歷史試用（例如 P03、Q-TARGET）的特判。

#### Scenario: AC-O15 暫停的 P03 試用
- **WHEN** 使用者只查看流程或規格，某個 feature 沒有以 `init` 建立 run
- **THEN** 對該 feature 的 `status`、`next`、`claim` 回報找不到 run，不建立狀態，也不接管其他 feature 的 run

### Requirement: ORC-11 詳細設計與最終任務計畫的責任

每個 run SHALL 只有一份現行 plan，由 Implementer 校準（登記時註明校準來源）。Project Lead 提供的草案 SHALL 可以登記作為來源，但 SHALL NOT 被批准；controller SHALL NOT 把草案作者、task checkbox 或共同目錄視為批准。任務調整需要改 AC、突破高層設計限制或改變其他 feature 依賴的契約時，SHALL 經 `scope_change` 讓整個 run 停下等待批准。

#### Scenario: AC-O22 Project Lead 提供初步 tasks
- **WHEN** Project Lead 交出初步工作包，Implementer 研究後合併、補充或重排任務
- **THEN** Implementer 登記的校準版 plan 成為唯一的現行 plan；Project Lead 產生的或沒有校準來源的 plan 不能被批准，狀態不會另存一份 Project Lead 的執行計畫

#### Scenario: AC-O23 詳細設計發現跨 feature 影響
- **WHEN** Implementer 發現任務調整需要改 AC、突破高層設計限制或改變其他 feature 依賴的契約，由人記錄 `scope_change`
- **THEN** 保存具體影響與待決事項，整個 run 停在等待批准，`next` 只回報需要人工決策，直到新版本被批准

### Requirement: ORC-12 Project Lead 的 Research 與 SA 階段契約

SA 確認 SHALL 可以作為 binding 登記並保存版本與確認來源，但 SHALL NOT 取代 D11 開工確認；controller SHALL 在 design＋plan 登記後，另外核對人工 `approve_plan`。

#### Scenario: AC-O26 適用 SA 確認與開工確認分開
- **WHEN** 已有適用的 SA 確認，以 SA 角色登記為 binding
- **THEN** 保存確認的版本與來源；run 仍在等待開工確認，只有對 plan 版本的人工 `approve_plan` 能產生核准
