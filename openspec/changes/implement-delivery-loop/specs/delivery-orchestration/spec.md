# Spec Delta

## Purpose

讓使用者透過共同 orchestrate 入口，將單一 feature 從新建或既有成果接入交付流程，並在 project 層保有來源引用、人工接受、相依啟動與有證據的 Retro 候選。本文為本 change 的D40 已核准的規格；D 編號是既有決策來源，操作名稱及細部驗收為規格化提案，並非已實作 API。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 `docs/validation/implement-delivery-loop.md` 補齊，包含 D32 的 AC-O20–AC-O23 與 D34 的 AC-O24–AC-O28，均需對應驗法與預期／實際證據。目前尚無執行結果，不因文件更新而視為驗收通過。

## ADDED Requirements

### Requirement: ORC-01 共同入口、角色責任與授權

系統 SHALL 提供共用 `orchestrate` 入口處理 project 準備、feature start/adopt、status/resume、decision 及 Retro 意圖。Project Lead Agent SHALL 負責專案及 feature 的研究、SA／domain 釐清／grill、高層設計、roadmap／milestones、feature 拆分與 spec 準備；Implementer Agent SHALL 承接實作研究、detailed design、最終 plan／tasks 與功能交付，兩者以 spec／AC、高層設計邊界、依賴及成果交接。Project Lead SHALL 僅在使用者明確授權範圍內安排優先順序、協調及提出委派意圖；Implementer SHALL 在已核准的 scope／design 內作實作決策，超出範圍的問題交回裁決。唯一 controller SHALL 核對授權與核准 plan 後實際派工、管理狀態與 gates。系統 SHALL 允許使用者直接與任一角色協作，不綁定固定的 runtime 父子關係，也不由共同入口或父子關係推定相同決策權；D11 人工裁決與 G2 Reviewer 獨立性維持。（來源：D02、D08、D17、D20、D23、D32）

#### Scenario: AC-O01 直接與 Implementer 協作
- **WHEN** 使用者直接交付已選定的 feature 給 Implementer
- **THEN** 系統允許進入 design/plan 準備，保留 feature owner 與 controller identity，不要求經 Project Lead 轉達，也不因此取得開工確認或 scope 變更權限

#### Scenario: AC-O02 拒絕第二個外層 loop
- **WHEN** Implementer 的 skill、Project Lead 或另一個 session 請求派發同一 feature 的外層實作／正式 review
- **THEN** 系統只接受經 controller 核對 plan、scope、依賴與預算的 assignment；局部 review 不可更新 G2 或繞過 controller

#### Scenario: AC-O18 授權 Project Lead 協調與委派
- **WHEN** 使用者明確授權 Project Lead 在指定 roadmap／feature 範圍內協調順序與委派工作
- **THEN** Project Lead 可在該範圍提出帶授權來源的安排，controller 核對核准 plan、依賴、scope 與預算後派發；Implementer 接收 spec／AC 與依賴、交回成果及待決事項，授權不代替 D11 開工確認或最終接受

#### Scenario: AC-O19 入口與 runtime 關係不授予決策權
- **WHEN** agents 使用相同入口，或 runtime 將 Project Lead 與 Implementer 顯示為父子 sessions
- **THEN** 系統仍依角色責任與使用者明確授權判定可執行動作，不從入口／父子標記新增委派權或 scope 變更權，也不因此要求使用者直接交付的 feature 先經 Project Lead；正式 Reviewer 仍符合 G2 獨立契約

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

系統 SHALL 記錄所採 authoring／planning 方法與唯一 spec、design、plan／tasks 的原生 binding，不因不同角色或技能各產生一套可獨立漂移的權威。D31 的 Matt to-spec／OpenSpec／Writing Plans 組合已重新評估；既有 OpenSpec 文件 SHALL 保留其來源與身份，工具候選不視為已選定或已驗證整合。整合 SHALL 保存 skill 引用版本、觸發／user-only 限制及格式／execution handoff 的調整，工作結果交回唯一 controller，不自動啟動另一套外層 loop；D26 的 TDD／例外要求維持，Retro 自動化須明示整合方法與輸出契約。（來源：D02、D07、D19、D26、D28；D31 選型狀態修訂、D32）

#### Scenario: AC-O16 Skills 交回 controller
- **WHEN** plan、TDD 或局部 review 方法完成一個工作單位
- **THEN** 結果與 evidence 交 controller 核對並記錄，不由 skill 自訂 feature Pass 或另啟排程；自動 Retro 不在背景呼叫 user-only 原版 skill

### Requirement: ORC-09 文件來源與政策適用範圍

系統 SHALL 交接每份規格／工程規則的目標 repo、來源、版本、適用範圍與決策狀態；agent 從其他工作環境取得的規則，不得被當成此 feature 已核准的產品政策。新政策或語意衝突 SHALL 經 D11 的明確決策處理；controller 核查引用與批准身份，語意適用性由 agent 提出依據供 review。（來源：D11、D19、D30；比較 R02 的修正設計）

#### Scenario: AC-O17 另一 repo 的規則混入草稿
- **WHEN** 產出的 spec 將其他 repo 的工程規則標為本次已確認政策，卻沒有適用來源或使用者決策
- **THEN** 審查指出來源與狀態差異，交接列為待澄清提案，controller 不把它加入核准 policy 或據此派工；保留原來源，不以 cwd 或角色名稱推定適用

### Requirement: ORC-10 研究與分析支持 project／feature 規格

Project Lead SHALL 在形成 roadmap／milestones、拆 features 與整理 feature spec 前，根據適用來源進行 research、SA、domain modeling、grill 與必要 high-level design。這些活動 SHALL 可迭代、引用已有適用成果，不要求為每個 feature 重做整個 project。Project 層 SHALL 記錄主要使用情境、系統邊界、共用需求、設計取捨、風險及依賴，據此安排 milestone 成果與 feature slices；單一 feature SHALL 再聚焦相關 codebase／baseline，形成行為、scope／非目標、AC、必要限制及高層設計引用。重要未知 SHALL 明列並回使用者釐清，不藏入實作假設。這是 agent 的分析與交接要求，不擴張 controller 成為自動管理整個 backlog 的排程器，也不增加逐文件簽核或強制檔名。（來源：D04、D05、D11、D17、D19、D32）

#### Scenario: AC-O20 從 project 分析拆出 features
- **WHEN** 使用者與 Project Lead 準備新 project 或接手既有 project，安排近期交付
- **THEN** 產物可追溯研究來源、domain／SA 結論、高層設計與待決事項，並說明 milestone 成果、feature slices、順序及依賴；roadmap、milestone、feature 與 implementation task 的身份分開，不由 task 清單取代需求與架構分析

#### Scenario: AC-O21 單一 feature 的聚焦分析與交接
- **WHEN** 選定 feature 引用既有 project baseline，且相關研究與設計部分仍適用
- **THEN** Project Lead 引用適用內容、補查本 feature 的差異與未知，再交出 spec／AC、必要高層設計及限制；不強制重做整個 project，會改變 scope／AC／架構的重要未知先回人，不由 Implementer 默默決定需求

### Requirement: ORC-11 詳細設計與最終任務計畫的責任

Implementer SHALL 承接 feature spec／AC、project baseline 與高層設計，繼續研究並完成 detailed design，負責校準及維護唯一的最終可執行 plan／tasks。Project Lead SHALL 可提供工作包、跨 feature 依賴或任務草案；Implementer SHALL 核對其介面、粒度、scope、依賴、task→AC 與驗法後再交 D11 開工確認。Controller SHALL 只依適用核准計畫派工，不將草案作者、task checkbox 或共同 artifact 目錄視為批准。核准邊界內的實作細節不新增逐 task 簽核；改變 spec／AC、已核准設計邊界或跨 feature 契約 SHALL 保存影響，交 Project Lead 分析並由使用者裁決。（來源：D02、D11、D19、D23、D32）

#### Scenario: AC-O22 Project Lead 提供初步 tasks
- **WHEN** Project Lead 交出 feature spec 與初步工作包，Implementer 研究後發現需要合併、補充或重排任務
- **THEN** Implementer 在需求與設計邊界內校準，保存最終 tasks／介面／依賴／AC 驗法及版本，再依 D11 一次確認；controller 不依尚未確認的草案提前派工，也不另建一份 Project Lead 的執行計畫

#### Scenario: AC-O23 詳細設計發現跨 feature 影響
- **WHEN** Implementer 發現任務調整需要改 AC、突破高層設計限制或改變其他 feature 依賴的契約
- **THEN** 保存具體影響與待決事項，交 Project Lead 分析並回使用者裁決；未取得適用決策前不依該變更派工，核准範圍內未受影響的工作可依現有計畫繼續

### Requirement: ORC-12 Project Lead 的 Research 與 SA 階段契約

系統 SHALL 在 project 需求準備、feature 需求準備或重開需求分析時，讓 Project Lead 依 [SA 階段契約](../../../../../docs/project-lead-sa.md) 工作，記錄層級、適用 baseline、需求／AC IDs、來源版本與待決影響。Project Lead SHALL 先查證，再每輪提出 1–3 個需使用者取捨的問題，區分事實、假設、建議與已確認需求；研究、CONTEXT、Spec 與 Design／ADR 各保存其責任內容，不建立同義權威副本。SA SHALL 以七項內容的實質充分性判斷能否進入 Design，交使用者確認適用版本；核心 scope／行為／驗收仍有阻擋或僅填滿模板時不得宣告 ready。已有適用來源與確認 SHALL 可沿用；此確認不得取代 D11 開工確認。SA 範圍 SHALL 不包含 detailed design、implementation plan 或產品程式碼修改；必要可行性查證可進行，prototype／環境變更先提出目的及範圍並依適用授權處理。工具候選不構成已選定或已驗證的方法。（來源：D19、D31、D32、D34；七項內容及交接語意由使用者 prompt 具體化）

#### Scenario: AC-O24 專案與功能的分析深度
- **WHEN** Project Lead 準備 project roadmap，之後再準備其中一個 feature
- **THEN** project SA 形成足以支持高層設計及 milestone 成果的需求基線，不先細化全部 features；選定 feature 的 SA 引用 baseline／milestone，補齊其關鍵情境、規則、重要例外及穩定 AC，保留來源與適用版本

#### Scenario: AC-O25 文件齊全但需求仍有阻擋
- **WHEN** 七項內容已填入文件，但仍有會改變核心 scope、行為或驗收的未決問題，或使用者尚未確認可進入 Design
- **THEN** 交接列出實際阻擋或等待確認、證據與下一位 owner，不以模板完整、沉默或 agent 自述當作 ready；不受影響的研究可繼續

#### Scenario: AC-O26 適用 SA 確認與開工確認分開
- **WHEN** 當前 SA 已滿足完成條件且有適用使用者確認，或引用的既有成果與確認經核對仍適用
- **THEN** 保存 readiness 理由、版本及確認來源並交下一階段，不重做已確認的完整 grill；controller 仍須在 feature design＋plan 完成後核對 D11，不能依 SA 確認直接派 implementation worker

#### Scenario: AC-O27 研究發現與使用者描述衝突
- **WHEN** code、文件與使用者描述對同一行為有差異，或可行性查證需要 prototype／環境變更
- **THEN** Project Lead 提供可追溯依據、區分現況與需求並提出需人決定的影響；必要 prototype／環境變更先提出目的與範圍，依授權執行，不自行把現有 bug 或推論升為已確認規格

#### Scenario: AC-O28 功能驗收與業務成果分開
- **WHEN** 功能行為已可用 AC 驗證，但業務改善尚無量測結果或目標未確認
- **THEN** Spec 與交接分開記錄功能符合要求與業務成功條件，未確認目標及未執行證據保留其狀態，不以測試通過代替業務改善達成，也不捏造數字補齊模板
