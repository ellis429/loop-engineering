# Spec Delta

## Purpose

讓使用者透過共同 orchestrate 入口，將單一 feature 從新建或既有成果接入交付流程，並在 project 層保有來源引用、人工接受、相依啟動與有證據的 Retro 候選。本文為未採用的比較草稿；D 編號是既有決策來源，操作名稱及細部驗收為規格化提案，並非已實作 API。

## ADDED Requirements

### Requirement: ORC-01 共同入口與同層角色

系統 SHALL 提供共用 `orchestrate` 入口處理 project 準備、feature start/adopt、status/resume、decision 及 Retro 意圖。Project Lead Agent、Implementer Agent、Reviewer Agent SHALL 為同層協作角色；只有唯一 controller 依核准 plan 派工、管理交付狀態與 gates。Project Lead 代理安排工作 SHALL 限於使用者明確授權的範圍。（來源：D02、D08、D17、D20、D23）

#### Scenario: AC-O01 直接與 Implementer 協作
- **WHEN** 使用者直接交付已選定的 feature 給 Implementer
- **THEN** 系統允許進入 design/plan 準備，保留 feature owner 與 controller identity，不要求經 Project Lead 轉達，也不因此取得開工確認或 scope 變更權限

#### Scenario: AC-O02 拒絕第二個外層 loop
- **WHEN** Implementer 的 skill、Project Lead 或另一個 session 請求派發同一 feature 的外層實作／正式 review
- **THEN** 系統只接受經 controller 核對 plan、scope、依賴與預算的 assignment；局部 review 不可更新 G2 或繞過 controller

### Requirement: ORC-02 單一交付單位與原生文件 binding

系統 SHALL 將 delivery run 綁定選定的 repo、feature issue 與一個 feature PR；implementation tasks 是該 PR 內的派工單位，過大 feature 須先回使用者拆成可獨立驗收切片。Feature spec SHALL 引用 project spec，使用工具原生文件名稱及實際位置，不另維護同義規格副本。每份引用 SHALL 可核對角色、來源、locator、revision、digest 與採用內容；issue 內文包含 issue identity 與觀察時間。（來源：D04–D07、D19；binding 欄位取自契約提案）

#### Scenario: AC-O03 引用既有文件
- **WHEN** feature 使用 issue 內文與 `docs/superpowers/plans/P03-ingest.md` 等既有原生文件
- **THEN** 交接保留實際位置與適用版本，能讀回採用內容；不因採用 OpenSpec 而把舊成果重新命名或把 task 各自建立為 PR

#### Scenario: AC-O04 權威來源衝突
- **WHEN** project spec 與 feature spec 對同一行為互相矛盾，或必要引用不可讀取
- **THEN** 系統列出衝突／缺口與所見版本並停止依該歧義派工，交使用者裁決；不依檔案時間或工具名稱自動選勝方

### Requirement: ORC-03 可驗證 AC 與一次開工確認

Feature 的 AC SHALL 使用穩定 ID 描述情境、操作與可觀察結果，並連結驗證方法及其後的實際 evidence。系統 SHALL 在完整 design+plan、task→AC、依賴、scope、驗法與文件更新內容具備後，取得使用者對該版本的一次開工確認。核准 scope 內的正常實作／修正 SHALL 持續執行；scope/spec/AC 變更、設計缺陷或需人工裁決的 blocker SHALL 回到使用者與 Project Lead，不得降低 AC 掩蓋缺陷。（來源：D11、D19）

#### Scenario: AC-O05 新 feature 尚未批准
- **WHEN** design/plan 已準備但沒有適用版本的明確使用者確認
- **THEN** 狀態顯示等待開工確認及待確認版本，不派 implementation worker；沉默、timeout 或 agent 同意不視為批准

#### Scenario: AC-O06 核准後按 plan 前進
- **WHEN** 使用者確認 design+plan 版本，且 scope、依賴與預算符合要求
- **THEN** controller 可依序派 task，交接每項 AC ID 與驗法；正常 finding 修正不逐 task 再要求批准

#### Scenario: AC-O07 需求變更不混入修正
- **WHEN** 修正需要改 AC、spec 或已核准設計，或使用者提出範圍外想法
- **THEN** 系統保存未完成項與影響，提出獨立 feature 候選或版本化 scope 決策；取得適用確認後才依新契約派工

### Requirement: ORC-04 Adopt 保留成果與控制權邊界

系統 SHALL 支援已選定既有 feature 的 pre-PR adopt，先唯讀核對原 owner/session、workers、原生外層 loops、未提交內容、repo/branch/head/base、artifacts、D11 確認及 G1 證據。只有原 owner 明確交出派工權且無未知 writer 時 SHALL 接手；已有適用成果須沿用，缺口如實呈現，不重做整個 feature、不補造歷史 Red。（來源：D09、D15、D16、D18；adopt 路由來自設計提案）

#### Scenario: AC-O08 已實作 pre-PR 接入
- **WHEN** 原 owner 已交接，版本固定，既有 design/plan 有適用確認，程式已完成而 G1 尚待核對
- **THEN** 系統從 G1 驗證開始；若 G1 已證明適用則核對／建立 PR 並進 checking，不重跑初始研究與實作派工

#### Scenario: AC-O09 Adopt 缺口
- **WHEN** 接入資料缺 D11 確認、歷史 Red、固定 base，或有相關未提交內容／未知 writer
- **THEN** 系統分別顯示需補的確認／證據／版本／ownership；缺確認回 planning 或 awaiting approval，其他無法安全續行項目 Blocked，不能以 pre-PR ready 通知判 G1 通過

### Requirement: ORC-05 交付與人工接受分離

系統 SHALL 將 task execution、gate verdict、publication、feature phase、human acceptance 與 GitHub merge 事實分開呈現。PR Pass SHALL 交付含版本、三 gates 理由與 evidence、findings、限制及發布狀態的可讀 package，等待使用者接受；不自動 merge、close issue、release 或 deploy。人工決策 SHALL 保存 actor、來源、時間、問題／版本、選擇、理由與影響。（來源：D03、D09、D11、D19）

#### Scenario: AC-O10 Pass 尚未接受或 merge
- **WHEN** 目前版本三 gates 已通過而使用者尚未接受
- **THEN** 系統呈現 PR Pass / ready for human acceptance 與 acceptance pending；merge 仍依真實 GitHub 事實呈現，不執行 merge/close/release/deploy

#### Scenario: AC-O11 接受後的新版本
- **WHEN** 使用者已接受版本 V1，之後 PR head、適用 spec 或 design 改成 V2
- **THEN** 保存 V1 的接受歷史，V2 的 acceptance 為 pending 並重評相關 gates；不把 V1 accepted 移植到 V2

### Requirement: ORC-06 相依 feature 的啟動條件

系統 SHALL 在有依賴的下一 feature 開始實作前，核對上游指定版本已人工接受、GitHub 已 merge，且本次採用 baseline 包含所依賴成果。等待期間 SHALL 允許準備 spec/design；Project 薄層保存 refs 與等待原因，不以 PR Pass、accepted 或舊 merged 標記代替三項核對。（來源：D27）

#### Scenario: AC-O12 上游 accepted 但未 merge
- **WHEN** 上游已 accepted，PR 仍 open
- **THEN** 系統允許下游準備 spec/design，顯示等待 merge，且不派依賴該成果的實作

#### Scenario: AC-O13 Merge 與 baseline 都適用
- **WHEN** 上游指定版本已接受及 merge，本次 baseline 可核對含有所依賴成果
- **THEN** 系統解除相依等待；下游仍依其自身 D11 確認、ownership 與預算才派工

### Requirement: ORC-07 Retro 只產候選

系統 SHALL 於版本化人工接受事件後自動整理一次 Retro 改善候選，由 Project Lead 彙整交付、review/CI 與人工回饋證據，列出改善、承接者與驗法；資料不足 SHALL 明列限制，沒有有據改善不得捏造待辦。候選及 Replanning 建議 SHALL 不自動修改 code、spec、roadmap 或 gate policy，不新增 PR gate。（來源：D21、D28；候選欄位為設計具體化提案）

#### Scenario: AC-O14 重複接受事件
- **WHEN** 同一 acceptance identity／版本被重送或於 restart 後讀到
- **THEN** 系統查回同一 Retro operation/result，不重複產出；輸出明列證據與尚未涵蓋階段，變更是否落地仍依既有決策權限

#### Scenario: AC-O15 暫停的 P03 試用
- **WHEN** 使用者只查看流程／此規格，尚未明確開始 P03 Retro 或恢復 PR trial，也未回答 Q-TARGET
- **THEN** 系統不接管 P03、不啟動 Retro 或 PR gating；保留待確認 feature/session、交接版本與原 owner 資訊

### Requirement: ORC-08 方法交接不新增排程器

系統 SHALL 由 OpenSpec 管 spec/design/tasks，以 Writing Plans 的任務、介面、測試與自檢方法銜接 tasks，實作採 Superpowers TDD。Matt 釐清/domain 方法按需使用；Matt implement/implement-spec 只供參考，不直接啟動外層 loop。整合 SHALL 保留工具原生檔名、skill 引用版本與 user-only 限制；Retro 自動化須明示整合方法與輸出契約。（來源：D02、D07、D19、D26、D28；shared-input 的最新使用者 Ok）

#### Scenario: AC-O16 Skills 交回 controller
- **WHEN** plan、TDD 或局部 review 方法完成一個工作單位
- **THEN** 結果與 evidence 交 controller 核對並記錄，不由 skill 自訂 feature Pass 或另啟排程；自動 Retro 不在背景呼叫 user-only 原版 skill
