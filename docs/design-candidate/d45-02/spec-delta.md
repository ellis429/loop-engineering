# Spec delta 候選：implement-delivery-loop 四份 specs（Stage 02A）

> **狀態：候選文字，尚未套用到正式 `openspec/changes/implement-delivery-loop/specs/**`，也未經 D11。** review-05 的 D45-S01、S02，以及 review-06 在規格層的對應修正（S03–S06），已在 revision-04 提交，待原 Reviewer 覆核。
> **已核准**：D46（隔離重建）、D47（DN-1 A）、D48（DN-2 A）、D49（DN-3 B）。這些只是政策邊界。
> **尚未核准**：具體 check 名稱／app／workflow、完整 design／plan、D11 開工確認、任何產品 gate。
> **不代表**：任何 S1 finding 已關閉。

## 0. 套用規則

- 88 個 AC ID 與 requirement 名稱（ORC-xx、GAT-xx、DUR-xx、FIN-xx）一律保留，沒有刪除或改號，也沒有新增 AC ID。本 change 未歸檔，所以直接改寫各檔 `## ADDED Requirements` 內的區塊。
- 每處修改標一種分類：
  - **[不變]**：義務原文保留。
  - **[移交]**：品質義務不變，由誰執行改為 orchestrate 或工具，controller 仍負責核對。
  - **[取代平台承諾]**：舊的平台實作承諾被新機制取代，可觀察的保證仍在。
  - **[政策修訂 D4x]**：依已核准政策調整承諾，並寫明邊界。
  - **[新增約束]**：補上防止 S1 缺陷重現的具體條件，不減少任何義務。
- 以下只列需要改寫的 requirement 內文或 scenario。未列出的 scenario 原文保留。

### 0.1 四檔共用：取代開頭 banner

四份 spec 開頭的「D41／D42：scope revision pending」段，換成：

> **D41–D49 修訂（2026-09-27）**：
> - orchestrate 是同一 feature 唯一的外層協調循環；
> - 薄 controller 是狀態、交接／版本核對、gates 與 findings 的唯一寫入與判定入口；
> - 第一條實作路徑是 Herdr 原生 sessions／panes／worktrees（D45）。
>
> D47–D49 的政策邊界已併入相關 requirement。D40 的 approval、舊 S1 程式、測試與 review 只作歷史紀錄，不是本版的核准或證據。本版 specs 仍須獨立 review 與 D11 確認後，才可派產品實作。

---

## 1. delivery-orchestration

**Purpose [移交]**：將第一段末句「本文為本 change 的 D40 已核准的規格…並非已實作 API」換成：

> 本文是 D45 收斂後的規格。orchestrate 協調工作並以既有 runtime 工具派工；controller 核對授權與版本，並發出允許動作。D 編號是既有決策來源；操作名稱不代表已實作的 API。

### ORC-01 [移交]

requirement 內文中「唯一 controller SHALL 核對授權與核准 plan 後實際派工、管理狀態與 gates。」換成：

> Orchestrate SHALL 是同一 feature 唯一的外層協調循環，只在 controller 發出許可後以既有 runtime 工具派工。Controller SHALL 核對授權、核准 plan、scope、依賴與預算，並是狀態、gates 與 findings 的唯一寫入入口。Controller 每次被呼叫時，完成核對或狀態更新後即返回，SHALL NOT 常駐、啟動 agents 或執行 worker 提供的命令。

- **AC-O01 THEN**：「保留 feature owner 與 controller identity」換成「保留 feature owner 與協調者 identity」，其餘原文保留。
- **AC-O02 THEN** 換成：
  > 系統只接受經 controller 許可、由持有該 feature 協調權的 orchestrate 派出的 assignment。沒有協調權的 session 只能讀取狀態；局部 review 不能更新 G2，也不能繞過 controller。
- **AC-O18 THEN**：「controller 核對核准 plan、依賴、scope 與預算後派發」換成「controller 核對核准 plan、依賴、scope 與預算後發出許可，由 orchestrate 以工具派發」，其餘原文保留。
- **AC-O19**：[不變]。

### ORC-03 [移交]

- **AC-O06 THEN** 換成：
  > controller 依序發出 task 許可，由 orchestrate 派出；交接帶每項 AC ID 與驗法。正常的 finding 修正不需逐 task 再批准。批准必須綁定已登記的 plan 版本及其 producer／校準來源；從未批准狀態經公開入口批准後，可以取得第一個合法許可。
- AC-O05、AC-O07：[不變]。AC-O07 的「不 crash」由 validation 經公開入口驗證（S1-R10）。

### ORC-04 [新增約束]

- **AC-O09 THEN** 末尾加上：
  > G1 以完整的核准 task／AC 集合判定；空集合或只含本次建立項目的集合 SHALL NOT 通過。
- AC-O08：[不變]。

### ORC-08 [移交]

requirement 內文中「工作結果交回唯一 controller，不自動啟動另一套外層 loop」換成：

> 工作結果交回 controller 核對與記錄；只有 orchestrate 維持外層 loop，其他 skills SHALL NOT 啟動另一套外層 loop。

- AC-O16：[不變]。

### 未改的 requirement

ORC-02、ORC-05、ORC-06、ORC-07、ORC-09、ORC-10、ORC-11、ORC-12：[不變]。其中 ORC-06（AC-O12／O13）照原文保留，Q-STACK 仍待決。

---

## 2. delivery-gates

**Purpose [移交]**：「本文是本 change 的D40 已核准的規格…已隨 D40 一次確認。」換成：

> 本文是 D45–D49 修訂後的規格。evidence 與 check 的核對方式由 design 具體化，測試接縫以修訂後的 design 為準。

### GAT-01 [移交]

「Controller SHALL 先確認 G1，才正式送 G2；」換成：

> Controller SHALL 在 G1 通過前拒絕發出正式 G2 review 的許可；

其餘原文保留。AC-G01、G02、G03：[不變]。

### GAT-02 [政策修訂 D48]＋[新增約束]

在 requirement 內文末尾加上：

> Evidence 的 producer identity SHALL 來自核准的證據捕捉工具或 runtime 原生紀錄，worker 的自述只作說明。本版以可信本機協作為前提（D48）：
> - 系統 SHALL 偵測並拒絕可核對的身份、版本、digest、lineage 不符，以及狀態竄改；
> - 系統 SHALL NOT 承諾抵抗同一 OS 帳號下的惡意整套偽造；
> - 無法驗證的 runtime profile SHALL NOT 被默認為可用。

- **AC-G04 WHEN** 換成：
  > result 宣稱測試通過，但原始 log 缺失、hash 不符、exit code 失敗、snapshot 不適用，或 producer 不是核准的捕捉工具
- **AC-G04 THEN**：[不變]。
- **AC-G05**：[移交]，由工具捕捉、controller 核對。文字不變。

### GAT-03 [政策修訂 D48]＋[新增約束]

在 requirement 內文末尾加上：

> 歷史 Red SHALL 是實作前捕捉的原始紀錄。raw output、exit code、task／attempt、snapshot 與 provenance 缺一不可，且每一項獨立核對；任一項污染 SHALL 使該 Red 無效，目前 Green 也不能掩蓋。Coordinator 從 snapshot 重放與 transcript 核對只能作為補充，SHALL NOT 取代或補造原始 Red。Red、Green 與 regression SHALL 只以核准 policy 定義的命令產生；controller SHALL NOT 執行 result 內的任意命令。最終 Green 與 regression SHALL 由協調方在整合 head 的獨立 checkout 執行。

- **AC-G06 THEN** 末尾加上：「coordinator 以核准命令從 R 重放得到相同失敗，只作為佐證。」
- **AC-G07 THEN** 換成：
  > G1 明列 missing／invalid。能補證據就補；無法取得原始歷史 Red 則 Blocked 待裁決。事後 replay、重建的 snapshot 或 transcript 核對 SHALL NOT 補足缺失的原始 Red，只能標明其性質作為補充。
- **AC-G08**：[移交]，Green 由協調方工具在整合 head 執行，文字不變。

### GAT-04 [移交]＋[新增約束]

「由 controller 派獨立 Reviewer 核對實際行為影響」換成：

> 由 controller 發出 eligibility review 許可、orchestrate 派出獨立 Reviewer，核對實際行為影響。Eligibility 結果 SHALL 通過與正式 G2 相同的獨立性核對：producer 角色、核准 model、session 獨立、權限能力；否則不予採用。

- **AC-G10 WHEN** 換成：
  > Implementer 對設定行為變更自行宣告 N/A；或 eligibility 尚未完成、被拒絕；或其 producer／model／獨立性未通過核對
- AC-G09：[不變]。

### GAT-05 [移交]＋[取代平台承諾]

requirement 內文換成：

> G2 SHALL 由經 controller 許可、orchestrate 以核准 profile 派出的獨立 Reviewer session 完成。Reviewer 對照目前版本的 spec、design、AC、完整 PR diff、相關 codebase、工程規範、舊 findings 與修正／反證，並回報實際讀取的版本 digests；digests 必須等於目前版本集合。Reviewer SHALL 能隔離驗證並保存結果，但 SHALL NOT 修改作者 branch、直接關閉 gate，也 SHALL NOT 由 Implementer 的 subagent 取代。
>
> 實際 model SHALL 從 runtime 原生紀錄讀回。Reviewer 的隔離 SHALL 由所選 runtime 既有的權限能力提供，並以真實負例驗證；本系統不自建 OS sandbox。無法驗證就是 G2 unknown。
>
> 既有獨立 Codex review 要求保留：OpenCode 仍是預設 runtime（D38）；本機第一條路徑經 Herdr 啟動 OpenCode（OpenAI models）或 Claude Code（Claude models）（D44）。精確 provider/model 與隔離能力 SHALL 在選用前核對，不能以任意 OpenAI model、不同 model 或角色名稱就宣稱符合。（來源：D01、D09、D20、D23、D30、D38、D44、D45）

- AC-G11、AC-G12：WHEN／THEN 原文保留；「controller 派出」一律讀作「經 controller 許可、由 orchestrate 派出」。

### GAT-06 [政策修訂 D49]＋[新增約束]

requirement 內文換成：

> G3 SHALL 從 GitHub 查核必要 check 集合，空集合 SHALL NOT 自動成功。集合的政策來源依序為：
> 1. 可讀的 repo 規則；
> 2. 只限於 repo 規則不可讀（例如 HTTP 403）的 `yschiang/loop-engineering`：人工核准、版控、綁定版本與批准來源的必要 checks 設定。G3 結果與 PR Pass package SHALL 明示「GitHub rules 未核對」。
>
> 403 或規則不可讀 SHALL NOT 自動授權改用任何設定；此政策來源 SHALL NOT 泛用到其他 repo。必要 check 的名稱／app／workflow SHALL 在該設定中列明並經核准，範例名稱不構成核准。政策來源不可用或不一致時，G3 SHALL 為 unknown 並 Blocked，SHALL NOT 開啟修正批次或增加修正輪次。
>
> 每項 check SHALL 核對 name/context、app/provider、source SHA、head/base 關係、attempt 時序、status/conclusion 與可讀 URL，涵蓋完整分頁。Missing、pending、cancelled、timed-out、failed、unknown、stale SHALL NOT 視為成功。只有 skipped／neutral 可以例外，且必須有明確核准、綁定 decision 的例外設定；其他 conclusion SHALL NOT 被例外設定放行。（來源：D01、D29、D49）

- **AC-G13 THEN** 換成：
  > G3 不通過並逐項顯示原因。規則不可讀且沒有適用的人工政策時，G3 為 unknown 並 Blocked，不消耗修正輪。沒有明確核准例外的 skipped／neutral 也不通過；failure、cancelled、unknown 永遠不因例外設定通過。
- AC-G14、AC-G15：[不變]。

### GAT-07 [新增約束]

- **AC-G16 THEN** 換成：
  > 保存 H1 的歷史證據，但不拿來放行 H2。H2 從需要重評的 G1 或 G2/G3 續行，不重置 finding／budget。與 H1 結果不同，新取得的外部觀察會更新觀察到的版本事實，並依版本規則使相關 gates 與 Pass 失效；只有已被更晚觀察取代的觀察才只存歷史。
- **AC-G18 THEN** 換成：
  > 前者放棄本次 Pass 並 reconcile。Pass 只能在一筆晚於三 gates 判定的新外部觀察確認版本一致、且必要發布已完成後記錄；不以快取時間窗代替新觀察。後者保存舊 Pass 版本及觀察時間，使目前結論失效並重新驗證；不宣稱跨多次外部讀取具全域 transaction。
- AC-G17：[不變]。

### GAT-08 [移交]＋[取代平台承諾]

在 requirement 內文末尾加上：

> 舊 S1 實作的測試、CI、review 與 bootstrap 證據 SHALL NOT 作為新實作的交付證據（D46）。

- **AC-G19 WHEN** 換成：
  > 可控制測試通過，但所選 Herdr＋runtime profile 的原生完成讀回、Reviewer 權限能力或正確 workspace placement 尚未驗證
- AC-G19 THEN、AC-G20：[不變]。

---

## 3. durable-delivery

**Purpose [移交]**：「讓單一本機 controller 以…」換成：

> 讓同一 feature 在單一本機以一份人可閱讀的狀態與可追溯的外部操作運作，在 worker、通知、檔案或網路失敗後，仍能辨識真實成果與協調權，安全續行或明確 Blocked。

「本文是本 change 的D40 已核准的規格」換成「本文是 D45–D49 修訂後的規格」。

### DUR-01 [取代平台承諾]

「Project 狀態 SHALL 引用 run/revision，feature 的現行 gate 只由 run authority 決定，不維護可獨立分歧的第二份 gate。」換成：

> 同一 repo＋feature SHALL 只有一份現行狀態 authority；run 或 epoch 只是其中的紀錄，不是另一份 authority。Project 狀態只引用 feature identity 與 revision，不維護可獨立分歧的第二份 gate。系統 SHALL 只有一套生效的狀態／CLI 入口，不與舊實作並存（D46）。

- **AC-D02 THEN** 末尾加上：
  > 手改可被偵測，且永不當作決策。本版以可信本機協作為前提，不承諾抵抗同一 OS 帳號下的惡意整套偽造（D48）。
- AC-D01：[不變]。

### DUR-02 [移交]＋[政策修訂 D48]

requirement 內文前兩句換成：

> 同一 repo＋feature SHALL 同時只有一個持有協調權的 orchestrate 能從 controller 取得派工許可。Run ID、epoch、session 或 clone 不同，SHALL NOT 產生第二份協調權或預算；實際 worktree SHALL 只有一個有效 writer。Workers SHALL 只能寫其授權 scope 與自己的 result／evidence 投遞位置，並由 runtime 權限設定拒絕呼叫狀態寫入命令。此限制 SHALL 以真實 runtime 負例驗證，未驗證的 profile SHALL NOT 被默認可用。系統 SHALL 對可核對的身份、版本、digest、lineage 或狀態竄改不符保存證據並 Blocked；不承諾偵測或阻止同一 OS 帳號下繞過 runtime 權限的惡意整套偽造（D48；D45-S02）。

後句「Timeout、lease 到期…才可重派。」保留原文。

- **AC-D03 THEN** 換成：
  > 最多一方取得協調權；另一方可讀狀態，但不能取得派工許可或新預算。衝突與現有協調者可查。
- **AC-D04 THEN** 末尾加上：
  > 已知 active 的 worker 到期時，可以對它發停止並讀回；確認停止前不派替代 attempt。

### DUR-03 [移交]

在 requirement 內文末尾加上：

> 外部 handles（Herdr session／workspace／pane／agent name、runtime native session ID）SHALL 與 run／task／attempt identity 分欄保存。name 只用於定位，不作身份證據。

- **AC-D06 WHEN／THEN**：「adapter」一律換成「runtime 讀回工具」，其餘原文保留。
- AC-D05：[不變]。

### DUR-04

- **AC-D07 [移交]**：「resume/reconcile」換成「orchestrate 經 controller 讀回核對」，其餘原文保留。
- AC-D08：[不變]。

### DUR-05 [取代平台承諾]

- **AC-D10** 整個 scenario 換成：
  > - **WHEN** 現行 state 更新時被中斷，或同一 transition 被重複提交
  > - **THEN** 每個 revision 在成為現行狀態前 SHALL 先完整保存到歷史；中斷留下、尚未生效的 revision 只保留為診斷，不生效也不重複生效；同一 transition identity 內容不同時 Blocked。系統不以事件重放作為第二份現行狀態來源。
- AC-D09、AC-D11：[不變]。

### DUR-06 [新增約束]

在 requirement 內文末尾加上：

> 登記同一外部操作可以重送且無副作用；但每次執行（包含唯讀 observation 的首次執行，以及明確失敗後允許的重試）的許可 SHALL 只被一個呼叫者消耗。對已送出但結果未記錄或不明的操作，讀回 SHALL NOT 消耗或重放執行許可，也 SHALL NOT 重發原操作。目前讀不到外部效果 SHALL NOT 單獨作為可重試的證明；只有能證明原嘗試不可能再生效時才可重試，限以下三種情況：
>
> - 在本機程序內直接、同步完成的操作，其原執行程序已不存在，且查無效果；
> - 已有權威證據證明未送達，或已完成且排除之後才生效；
> - 外部操作有已驗證的原生冪等保證。
>
> 經常駐 server 或遠端處理的請求（例如 Herdr socket API、GitHub 發布），SHALL NOT 僅因本機 client 程序已結束且查無效果就重試；其他情況 SHALL 維持 unknown 並 Blocked 交人（D45-S03）。
>
> 自動讀回 SHALL 有次數上限，且每次自動讀回（包括原執行程序仍在執行、結果未定的那次）都計入。到限仍無法確認時 SHALL Blocked，並停止自動讀回，直到人工核准再次檢查；worker 維持 active／unknown，不重送（D45-S06）。同一版本上重複的外部觀察 SHALL 以新的觀察週期識別，使先前觀察結果 pending 時仍能再次觀察（D45-S04）。

- **AC-D12 WHEN**：「controller 未收到回應而 restart」換成「協調者未收到回應即中斷，之後再續行」。
- AC-D13：[不變]。

### DUR-07 [移交]

- **AC-D14 THEN** 換成：
  > orchestrate 經 controller 核對並匯入已完成的結果，保留適用的 review，只恢復 pending 發布與必要工作；不重派已完成的 task，不清空 findings 或 budget。無法確認 worker、worktree 或協調者狀態的部分停止並交人，不承諾自動修復。
- AC-D15：[不變]。

### DUR-08 [政策修訂 D47]

第一段末句「到限 SHALL 停止新派工…不得自動重置上限。」之後加上：

> 協調 session 在線時，系統 SHALL 以有界等待檢查期限，對已知 active 的 worker 發停止，並以讀回確認；這些停止與讀回 SHALL NOT 被其他 blocker 或無關的進行中操作阻擋。協調 session 離線期間，系統不保證準時停止。恢復時 SHALL 將無法排除的活動期間計入、記錄超時量、處理仍在執行的 worker，並 Blocked 交人；unknown SHALL NOT 被視為已停止。停止的讀回同樣有次數上限；到限仍無法確認時 SHALL Blocked 交人，不重送停止，也不無限輪詢（D45-S06）。本版不新增常駐 watchdog，也不預設加硬截止 wrapper（D47）。

第二段「Active time 算法…待 D11 確認後才採用。」換成：

> Active time 算法、未知區間的計入方式，以及 worker/review/CI 的 45/30/30 分鐘候選 timeout，由 design 提出並隨 D11 確認；確認前不視為已核准。

- **AC-D17** 整個 scenario 換成：
  > - **WHEN** 累計主動時間達 4h 時協調 session 在線；或到限發生在協調 session 離線期間，之後恢復；或 restart 後讀回已到限的 run
  > - **THEN** 不再派新工作。在線時對已知 active worker 發停止並讀回確認；離線時在恢復時計入無法排除的期間、記錄超時量，並處理仍在執行的 worker。之後保存 unknown 區間與 Blocked 原因；停止無法確認時維持 active／unknown，不視為已停止。要調整預算，需保存明確的使用者裁決，不因等待而自動歸零。
- AC-D16：[不變]。

### DUR-09 [移交]

「系統 SHALL 預設由 OpenCode adapter 執行 agents，依角色設定 provider/model；」換成：

> OpenCode SHALL 仍是預設 runtime（D38），依角色設定 provider/model。第一條本機實作路徑 SHALL 由 Herdr 原生 sessions／panes／worktrees 啟動 OpenCode（OpenAI models）與 Claude Code（Claude models）（D44／D45），不引入另一套外層 orchestrator。Transport、runtime、provider 與 model SHALL 分欄保存；Herdr SHALL NOT 成為所有部署環境的必要依賴。

- **AC-D20 THEN**：「controller 可直接啟動／resume、派發及核對 OpenCode 任務」換成「orchestrate 可經 OpenCode-only 的工具接法啟動／resume、派發，並由 controller 核對 OpenCode 任務」。
- **AC-D21 WHEN**：「Orca dispatch 或 OpenCode session/message」換成「Herdr handles、Orca dispatch 或 OpenCode session/message」。
- **AC-D22 WHEN**：「Orca 接法已驗證通過…或反之」換成「任一接法（Herdr、OpenCode-only、Orca）已驗證通過，而另一接法的模型、隔離或 lifecycle 尚未驗證」。
- AC-D18、D19、D23、D24：[不變]。

---

## 4. finding-resolution

**Purpose [移交]**：刪去「實作依 D40 分 S1／S2／S3」，改為「驗證依 H1／H2／H3 分階段」。

### FIN-03 [新增約束]

在 requirement 內文末尾加上：

> 核准 scope／spec／AC／design 內可修正的 findings（包括文件缺陷、必要驗證缺失）及可修正的 CI failures 可進入 correction batch；CI 政策來源 unknown 或基礎設施失敗不作為修正項目，SHALL NOT 因其本身開啟批次或增加輪次。需改 scope／spec／AC／design 者仍沿 D11 回人（D45-S01）。G1 在正式 review 前因可歸因且可修正的整合問題而不通過時（例如整合 head 回歸失敗、Red 測試在 head 未通過），系統 SHALL 以同一 correction 機制開一次修正（派修登記時計一輪，共用同一上限），修正後重做整合 G1，通過後才進正式 G2；此路徑不需等待 review／CI。缺原始 Red、infra unknown 或需改 spec／design 時 SHALL Blocked 交人（D45-S05）。派修與覆核的 assignment SHALL 附每項 finding 的完整內容、依據、預期行為、先前 review 與 fix 證據引用，使接收者只憑 assignment 與其引用即可工作。

- **AC-F05 THEN** 末尾加上：「CI policy unknown 不構成可修項目；review 提出的文件缺陷或必要驗證缺失可與 CI 可修問題組成同一 batch。」
- AC-F06、AC-F07：[不變]。AC-F07 的「換 run 不重置」由單一 feature 狀態保證。

### FIN-04 [移交]

「Implementer 的反證 SHALL 由 controller 送獨立 Reviewer 覆核一次」換成：

> Implementer 的反證 SHALL 只取得一次由 controller 發出、orchestrate 派出的獨立 Reviewer 覆核

其餘原文保留。AC-F08、F09、F10：[不變]。

### FIN-06 [移交]

「再將完整 review 發到 PR」換成：

> 再由 orchestrate 經 GitHub 工具將完整 review 發到 PR

並在 requirement 內文末尾加上：

> PR Pass 前，本版本必要的 PR 發布與 issue 摘要 SHALL 已完成並可讀回。

AC-F13、F14：[不變]。

### 未改的 requirement

FIN-01、FIN-02、FIN-05、FIN-07：[不變]。AC-F16 的 reopen 保留 closure 歷史並阻擋；原文已涵蓋，S1-R16 以新測試驗證。

---

## 5. 各主題的落點

| 主題 | 修改位置 |
| --- | --- |
| 4h 離線（D47） | DUR-08、AC-D17、AC-D04 |
| 可信本機邊界（D48） | GAT-02、DUR-02、AC-D02 |
| 原始 Red（D48） | GAT-03、AC-G06、AC-G07 |
| Repo 專用 CI 政策來源（D49） | GAT-06、AC-G13、FIN-03 |
| Orchestrate 與 controller 分工 | ORC-01、ORC-03、ORC-08、GAT-01、GAT-04、GAT-05、DUR-07、FIN-04、FIN-06 |
| D46 重建 | DUR-01（單一入口）、GAT-08（舊證據不算）；重建程序本身屬 design，不寫入 spec |
| 獨立 Reviewer 與目前版本 | GAT-05、GAT-04、GAT-07、AC-G16、AC-G18 |
| 許可只消耗一次、讀回不重發 | DUR-06 |
| 修正資格含文件缺陷與必要驗證缺失（D45-S01）；正式 review 前 G1 失敗的修正路徑（D45-S05） | FIN-03、AC-F05 |
| 可核對不一致才承諾偵測（D45-S02） | DUR-02 |
| 查無不等於可重試（D45-S03）、觀察週期（D45-S04）、有界讀回（D45-S06） | DUR-06、DUR-08 |

check 名稱／app／workflow 集合都沒有在此核准。S1-R01–R17 仍全部 open。
