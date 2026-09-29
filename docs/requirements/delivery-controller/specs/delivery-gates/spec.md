# Spec Delta

> **D53 採用（2026-09-28）**：本文依 D11（D53）採用，由「正式 specs 原文＋D45-02 spec-delta（sha256 `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565`）＋D45-04 spec-delta（sha256 `81ce7366894349d9d56493ddd1c01901a641746897c7cdf9d8aaced87e6e284b`）」依 D45-04 spec-delta §12 組成；逐項來源見 [source-map](../../adoption/source-map.md)。
> - orchestrate 是同一 feature 唯一的外層協調循環；
> - 薄 controller 是狀態、交接／版本核對、gates 與 findings 的唯一寫入與判定入口；
> - 第一條實作路徑是 Herdr 原生 sessions／panes／worktrees（D45）。
>
> D47–D49 的政策邊界已併入相關 requirement。D40 的 approval、舊 S1 程式、測試與 review 只作歷史紀錄，不是本版的核准或證據。

## Purpose

以可讀取且適用交付版本的證據分別判定實作/TDD、獨立 review 與必要 CI，只有三 gates 一致成立才提供 PR Pass。本文是 D45–D49 修訂後的規格。evidence 與 check 的核對方式由 design 具體化，測試接縫以修訂後的 design 為準。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 D53 採用的 `docs/design-candidate/d45-04/validation.md` 補齊驗法、通過標準與預期／實際證據。目前尚無產品執行結果，不因規格存在而視為已驗收。

## ADDED Requirements

### Requirement: GAT-01 三 gates 與執行結果分離

Controller SHALL 在 G1 通過前拒絕發出正式 G2 review 的許可；G2 與 G3 可並行。PR Pass SHALL 要求 G1 實作/TDD、G2 獨立 review、G3 必要 CI 均適用目前版本且通過。Task succeeded、agent 摘要、終端 idle、input accepted 或通知 SHALL 不作 gate 成功證據；missing、pending、failed、stale、unknown 等未通過狀態須保留原因。（來源：D01、D09、D13）

#### Scenario: AC-G01 正常交付
- **WHEN** G1 通過後，獨立 review 與必要 CI 的適用結果都通過
- **THEN** controller 核對當前版本並保存三 gates 的證據／理由後才記錄 PR Pass；此前不因任一 task completed 放行

#### Scenario: AC-G02 單一 gate 失敗
- **WHEN** review clean 但 CI fail，或 CI success 但 review changes_required
- **THEN** 不產生 PR Pass，分別保留成功與失敗 gate 的實際結果，將適用問題交同一版本的 correction 流程

#### Scenario: AC-G03 Review 執行成功但無法裁決
- **WHEN** reviewer task succeeded，品質 verdict 卻是 blocked
- **THEN** G2 保持 unknown 並令 feature Blocked，保留待決問題；不以 task 成功判 clean，不僅因 blocked verdict 新增 correction round

### Requirement: GAT-02 真實 evidence 與 AC 可追溯

Gate evidence SHALL 可讀取並核對 task/AC/attempt、producer identity、目的、command/environment、起迄時間、exit code、原始輸出及 digest、source snapshot/tree 與交付 lineage。Controller SHALL 核對存在性、完整性、身份與版本；Reviewer 核查測試是否有效證明 AC。手寫摘要或符合 JSON schema SHALL 不自動成為執行證據。（來源：D01、D09、D19；evidence 欄位為契約提案）

Evidence 的 producer identity SHALL 來自核准的證據捕捉工具或 runtime 原生紀錄，worker 的自述只作說明。本版以可信本機協作為前提（D48）：
- 系統 SHALL 偵測並拒絕可核對的身份、版本、digest、lineage 不符，以及狀態竄改；
- 系統 SHALL NOT 承諾抵抗同一 OS 帳號下的惡意整套偽造；
- 無法驗證的 runtime profile SHALL NOT 被默認為可用。

#### Scenario: AC-G04 摘要與證據不一致
- **WHEN** result 宣稱測試通過，但原始 log 缺失、hash 不符、exit code 失敗、snapshot 不適用，或 producer 不是核准的捕捉工具
- **THEN** gate 不通過，逐項顯示缺失／衝突及 producer；不以摘要、測試總數或 plan 的預期輸出替代

#### Scenario: AC-G05 驗證與程式分離引用
- **WHEN** 最終程式版本的 evidence 在 runner result 中綁定實際 snapshot，tracked 驗收文件引用該 result
- **THEN** 系統可核對程式版本與證據關係，不要求文件以自身 commit SHA 自我引用；後續只改文件仍須保存差異與證據適用理由。程式之後只改文件的新 head，SHALL 在新 head 重跑 Green，並記錄「只有文件差異」這個適用理由；tracked 文件 SHALL NOT 被要求引用自身的 commit SHA。

### Requirement: GAT-03 歷史 Red 與目前整合 Green

G1 SHALL 對行為變更要求 Superpowers TDD 的歷史 Red：測試已存在、對應行為尚未實作／修正的 source snapshot、命令、失敗原因及原始輸出。Red SHALL 可早於最終 SHA，但必須追溯同一 task／後續修正與 Green/refactor；最終 Green 及必要 regression SHALL 適用目前整合 head。Task worktree 的成功不能直接推出整合成功。（來源：D01、D26）

歷史 Red SHALL 是實作前捕捉的原始紀錄，逐項核對 raw、exit、task／attempt、snapshot、provenance。

**需要 Red 的單位** [R12]：核准 plan 的每個 task，以及每個改變行為的修正 attempt（含正式 review 前的 G1 修正、review／CI 修正、整合 base 時作者自己寫的解法、人工退回）。修正的 Red SHALL 另外綁定所處理的 finding ID 與 batch ID；batch 內每個改變行為的 finding SHALL 至少有一個列出它的 Red。是否改變行為依實際 diff 判定。

Red SHALL 另外滿足三項適用資格，每項獨立判定，任一不成立即無效（D51-R07）：
- snapshot 的變更與 attempt 的 commit 範圍 SHALL 位於核准的 task（或 batch 的 finding）scope 內；整合 attempt 只以作者編輯計算 scope，可重現地驗證為原樣匯入的 base 內容不算作者編輯 [R13]；
- 原始 snapshot SHALL 有捕捉當時記錄的、對應到該 task／attempt 的適用紀錄：捕捉 provenance 帶有該 task／attempt，並且 snapshot 的測試內容或 delta 出現在 attempt 的 commit 中，或 snapshot 本身位於 attempt 的歷史上。只有共同祖先 SHALL NOT 足夠。尚未 commit 時捕捉的原始 Red，可以經由這份記錄的對應連到 attempt；
- attempt SHALL 是目前 head 的祖先。

**被放棄的 attempt** [R12]：不在目前 head lineage 的 attempt，其 Red SHALL NOT 轉移給其他 attempt。某個單位沒有合格的原始 Red 時，G1 SHALL 不通過，feature SHALL Blocked 並附原因；SHALL NOT 以 replay 或回退程式重新捕捉的方式製造 Red。

**歷史被改寫** [R12]：目前 head 不是先前記錄 head 的後代時，依 lineage 判定的 Red 資格 SHALL 失效並 Blocked，SHALL NOT 補造證據。

raw 與 producer 正確，SHALL NOT 補足這些資格；replay 也 SHALL NOT 補足。本條不要求 Red 與 Green 在同一 SHA，也不要求強制 replay。

Red、Green 與 regression SHALL 只以核准政策定義的命令產生；最終 Green 與 regression SHALL 由協調方在目前實際的 head H 的獨立乾淨 checkout 執行，SHALL NOT 在 Implementer worktree 執行；controller SHALL NOT 執行 worker 或 result 提供的命令。以暫時合併的 snapshot 取得的結果，SHALL NOT 當作 H 的 Green（D51-R02）[R15：保留 D45-02 的「獨立 checkout」與「只以核准命令」]。

replay SHALL 只在證據矛盾或有風險時作為診斷，SHALL NOT 補造 Red。

#### Scenario: AC-G06 不同 SHA 的有效 Red 與 Green
- **WHEN** task 的 Red snapshot R 因目標行為缺失而失敗，修正／整合 lineage 可追至目前 head H，且 H 的必要驗證為 Green
- **THEN** G1 可採用 R 的歷史 Red 與 H 的 Green，不要求兩者同 SHA 或重新製造 Red。正常路徑不需要 replay；只有矛盾或風險時才以 replay 作診斷，而且不能補造原始 Red。

#### Scenario: AC-G07 缺歷史或錯誤的 Red
- **WHEN** 既有 feature 只有當前綠燈，或所稱 Red 只是語法／環境錯誤，或事後 replay 被稱作原始 test-first
- **THEN** G1 明列 missing／invalid。能補證據就補；無法取得原始歷史 Red 則 Blocked 待裁決。事後 replay、重建的 snapshot 或 transcript 核對 SHALL NOT 補足缺失的原始 Red，只能標明其性質作為補充。

#### Scenario: AC-G08 整合回歸失敗
- **WHEN** 個別 task 都成功，但整合 head 的必要 regression 失敗
- **THEN** G1 不通過，保存 attempt commit 範圍到整合 head 的對應與實際失敗，要求修正整合版本

### Requirement: GAT-04 獨立 N/A eligibility

純文件／註解變更 SHALL 可提出附理由、diff 分類與必要文檔檢查的 TDD N/A 申請，由 controller 發出 eligibility review 許可、orchestrate 派出獨立 Reviewer，核對實際行為影響。Eligibility 結果 SHALL 通過與正式 G2 相同的獨立性核對：producer 角色、核准 model、session 獨立、權限能力；否則不予採用；Implementer 不得自行豁免。Eligibility SHALL 先於整體 G1，其結果只免除適用範圍的 Red/Green，不能取代 G2 clean 或免除必要驗證/G3。設定、migration、test code SHALL 依真實行為判斷。（來源：D26）

#### Scenario: AC-G09 純文件 N/A 通過
- **WHEN** 獨立 Reviewer 對固定 diff 確認沒有行為影響，必要檢查可讀且通過
- **THEN** 系統保存 eligibility 決定、版本、理由與證據，依適用 N/A 完成 G1 後才正式 G2；G2 仍未自動通過

#### Scenario: AC-G10 行為變更或待核對的 N/A
- **WHEN** Implementer 對設定行為變更自行宣告 N/A；或 eligibility 尚未完成、被拒絕；或其 producer／model／獨立性未通過核對
- **THEN** G1 不因此通過，依拒絕原因補 TDD／證據或轉 Blocked；不能將「檔案類型是設定」視為豁免

### Requirement: GAT-05 獨立整合 review

G2 SHALL 由經 controller 許可、orchestrate 以核准 profile 派出的獨立 Reviewer session 完成。Reviewer 對照目前版本的 spec、design、AC、完整 PR diff、相關 codebase、工程規範、舊 findings 與修正／反證，並回報實際讀取的版本 digests；digests 必須等於目前版本集合。Reviewer SHALL 能隔離驗證並保存結果，但 SHALL NOT 修改作者 branch、直接關閉 gate，也 SHALL NOT 由 Implementer 的 subagent 取代。

實際 model SHALL 從 runtime 原生紀錄讀回。Reviewer 的隔離 SHALL 由所選 runtime 既有的權限能力提供，並以真實負例驗證；本系統不自建 OS sandbox。無法驗證就是 G2 unknown。

既有獨立 Codex review 要求保留：OpenCode 仍是預設 runtime（D38）；本機第一條路徑經 Herdr 啟動 OpenCode（OpenAI models）或 Claude Code（Claude models）（D44）。精確 provider/model 與隔離能力 SHALL 在選用前核對，不能以任意 OpenAI model、不同 model 或角色名稱就宣稱符合。（來源：D01、D09、D20、D23、D30、D38、D44、D45）

G2 SHALL 只在以下全部成立時通過：經授權的獨立 Reviewer、對目前版本的完整 PR diff、適用的 spec／design／AC 以及先前 findings 做了 review、verdict 為 `clean`、沒有未解的 blocking。

`changes_required` SHALL 為 failed；`blocked` SHALL 使 G2 為 unknown，**且 feature SHALL Blocked**，不開修正輪 [R12]；缺 verdict、格式錯誤或只審部分 diff SHALL NOT 通過。

正式 review SHALL 在 PR identity 已記錄之後才派出 [A04]。

#### Scenario: AC-G11 有效獨立 review
- **WHEN** 經 controller 許可、由 orchestrate 派出符合核准 runtime/model 與隔離限制的 Reviewer，結果已驗證且沒有未解除 blocking finding
- **THEN** 只有適用目前版本的 clean verdict 可使 G2 通過，並保存 assignment/session、完整 review、覆核 evidence 與版本

#### Scenario: AC-G12 局部 review 或隔離無法證明
- **WHEN** 提供的是 Implementer 呼叫的 review subagent 結果，或 Reviewer 的工具可改作者 branch，或獨立性／隔離尚無可核對證據
- **THEN** 不採為 G2；顯示獨立性或 adapter 能力缺口，不默默放寬權限，也不因只禁用 edit 工具便聲稱所有工具安全

### Requirement: GAT-06 必要 CI 與非成功狀態

G3 SHALL 從 GitHub 查核必要 check 集合，空集合 SHALL NOT 算成功。政策來源依序為：
1. 可讀的 repo 規則；
2. 規則讀取回 403 或不可讀時，**只有** `yschiang/loop-engineering`，而且存在一份以人工 `policy_change` 核准、綁定政策檔（repo 根目錄 `workflow.yaml`，不是 GitHub workflow）digest 的宣告集合，才採用該集合；此時 G3 與 Pass package SHALL 標示 GitHub rules 未核對。

沒有適用政策（缺少、未核准、digest 不符、其他 repo）時，G3 SHALL 為 unknown 並 Blocked，SHALL NOT 開修正批次或增加修正輪次。403 本身 SHALL NOT 自動授權任何集合，此政策來源 SHALL NOT 泛用到其他 repo。必要 check 的名稱、app 與 workflow SHALL 在政策檔列明並經核准；範例名稱不構成核准。

每項必要 check SHALL 核對 name/context、app/provider、workflow 來源、source SHA、head/base 關係、run 與 attempt 的身份及順序、status/conclusion 與可讀 URL，涵蓋完整分頁。Missing、pending、cancelled、timed-out、failed、unknown、stale SHALL NOT 視為成功。

第一片 SHALL 只採用來源是 PR head 的 check：metadata 的 head SHA 與該 job 實際受測的 SHA 都 SHALL 等於 head。每個 job 的受測 SHA SHALL 以唯一對應該 run、attempt、job 與 check 的紀錄證明；缺少或不符 SHALL NOT 通過 [R12]。

本機 G1 與每個必要 CI job SHALL 套用同一套收集／skip／失敗政策：收集數為 0、任何不是由 `only_on` 在非所屬平台產生的 skip、xfail／xpass 都 SHALL 使測試 session 失敗；skip reason 的文字 SHALL NOT 作為平台條件的證據 [R12；R13 修正措辭]。

例外機制 SHALL 只允許 skipped／neutral，而且每一項 SHALL 綁定一個核准的 decision；failure、cancelled、timed_out、unknown SHALL NOT 被例外放行。具體採用的政策可以不設任何例外；第一片的候選政策就是如此。（來源：D01、D29、D49、D51）

#### Scenario: AC-G13 非成功 check 與空集合
- **WHEN** required 集合未設定／為空，或任一 required check missing、pending、cancelled、timed-out、failed、unknown、stale
- **THEN** G3 不通過並逐項顯示原因。規則不可讀、**且沒有適用的已核准政策**時，G3 為 unknown 並 Blocked，不消耗修正輪。沒有明確核准例外的 skipped／neutral 也不通過；failure、cancelled、timed-out、unknown 永遠不因例外設定通過。

#### Scenario: AC-G14 舊成功不能蓋過新 attempt
- **WHEN** 同名 check 的舊 attempt success，但目前適用 attempt pending/failed，或同名結果來自未知 provider
- **THEN** G3 採目前適用 attempt 與核准來源，不以舊 success 或名稱相同的其他來源放行

  第一片只支援 GitHub Actions 的 check-run，且候選 workflow 只由 PR 事件觸發。
  - 候選 SHALL 同時符合預期的 app、workflow 路徑、check 名稱，以及 run 的事件類型、head SHA 與已記錄的 PR；
  - 同一 workflow、同一 head，但事件或 PR 不符的 run SHALL 為 unknown，SHALL NOT 被忽略；
  - 每個 run 內 SHALL 以最新的 run attempt 為準；同一 head 有多個 run 時，每個 run 的最新 attempt 都 SHALL 計入，全部成功才算成功；run ID 只作識別；不依開始時間；
  - 會讀完所有分頁；
  - 無法識別、無法排序或有歧義時 SHALL 為 unknown，SHALL NOT 回退到舊的 success；
  - 只以 commit status 回報的必要 check SHALL 為 unknown。

#### Scenario: AC-G15 衍生整合 snapshot
- **WHEN** CI 使用不同於 PR head 的 integration snapshot
- **THEN** 第一片：該必要 check SHALL 為 unknown（不支援的來源）並顯示原因，SHALL NOT Pass。**[延後 S2]**：只有可驗證的 head/base 映射與適用接受規則成立才採用；不能只比名稱或因 SHA 字串不同一概接受或拒絕，無法確認時為 unknown。

### Requirement: GAT-07 版本變更使結論失效

Gate 判定 SHALL 綁定 repo/PR、head、實際 base ref/tip、review merge-base、project/feature spec、design/plan/policy digests 及執行 skill/controller 版本。新 head SHALL 重新取得目前版本的 G1 最終驗證、G2 結論與 G3 checks，歷史 Red 保留 lineage。Base/spec/design/AC/plan/skill/policy 變更 SHALL 評估相關失效及任何證據沿用理由，不得只改規則來消除 blocker。需 D11 確認的變更先回 planning/awaiting approval。（來源：D01、D11、D19；版本集合與失效路由來自契約提案）

#### Scenario: AC-G16 舊結果晚到
- **WHEN** 目前為 H2，而 H1 的 review、CI 或 result 才送達
- **THEN** 保存 H1 的歷史證據，但不拿來放行 H2。H2 從需要重評的 G1 或 G2/G3 續行，不重置 finding／budget。與 H1 結果不同，新取得的外部觀察會更新觀察到的版本事實，並依版本規則使相關 gates 與 Pass 失效；只有已被更晚觀察取代的觀察才只存歷史。

#### Scenario: AC-G17 Base 或規格改變
- **WHEN** head 相同但 base/merge-base 或適用 spec/design/AC 改變
- **THEN** 系統重建 diff／整合風險或驗法並要求 Reviewer 讀新契約；CI 若沿用須保存適用理由，需人工確認時停止依舊版本派工

  head 不變而 base 改變、且沒有整合觸發時，SHALL 在 H 重跑必要的 Green 與 regression，並綁定新的 base，同時重新 review；這不代表已驗證與新 base 的整合。G3 沿用 H 的 head-only 結果時，SHALL 保存適用理由。整合觸發只有：GitHub 回報不可合併、Reviewer finding 判定不相容、人工 decision；可合併性尚未算出時 SHALL 等待，逾時 SHALL Blocked。整合以保留歷史的本機 merge commit 產生新的真實 head，所有 gates 重新判定 [R13 修訂如下]：
  - **路徑 [R14]**：先套用 owner／writer 安全、D47 預算／stop 與修正輪數限制，SHALL NOT 因整合而繞過。觸發成立且適用 G1 未通過，或任一必要 G2／G3 已過時、無法啟動、已確定不可用或逾時時，SHALL 優先走既有正式 review 前的 G1 修正機制（原因 base 整合）；即使另一 gate 仍在途，也 SHALL NOT 等待無法取得的結果。只有適用 G1 通過，且 G2、G3 各自都有同版本終態結果或確實在途且可取得的執行，才 SHALL 照常收齊，併為同一 correction batch；均為終態時直接合併。終態的 policy unknown／review blocked 等獨立 blockers SHALL 保留。各 gate 保存真實原因，缺少 CI SHALL NOT 算成功。
  - **共同規則**：兩者都 SHALL 只有一個 writer、一個 batch，實際派修時計一輪；派修前 SHALL 確認先前的 writer 已停止（unknown 依 DUR-08）；過時的結果只存歷史，已收到的 findings SHALL 保留。
  - **去重**：整合需求 SHALL 以（base、釘住的 base tip、目前 head）決定的穩定 finding identity 記錄並去重，作為整合 Red 的綁定對象。
  - **整合 assignment**：SHALL 釘住先前的 feature head 與確切的 base tip，分別授權原樣匯入該 base 的變更，以及作者編輯（限衝突路徑與 batch finding 的 scope）。merge commit SHALL 以這兩者為 parents。
  - **Red 與 scope**：原樣匯入 SHALL 以可重現的 git 自動合併結果核對。純匯入 SHALL NOT 要求補造上游 Red，也不宣稱 N/A；作者編輯改變行為時 SHALL 有綁定整合 finding 與 batch 的原始 Red；超出 scope 的作者編輯 SHALL 被拒收，需要時回 D11。

#### Scenario: AC-G18 Pass 前後發生 push
- **WHEN** Pass 前重新讀到的 head/base/artifacts 不一致，或已保存 Pass 後出現新 push
- **THEN** 前者放棄本次 Pass 並 reconcile。Pass 只能在一筆晚於三 gates 判定的新外部觀察確認版本一致、且必要發布已完成後記錄；不以快取時間窗代替新觀察。後者保存舊 Pass 版本及觀察時間，使目前結論失效並重新驗證；不宣稱跨多次外部讀取具全域 transaction。

### Requirement: GAT-08 驗收證據區分模擬與真實交付

驗收報告 SHALL 明確區分可控制測試、真實 adapter 能力與完整交付 E2E。真實驗收 SHALL 包含至少一次成立的 finding → fix → re-review 與最新 PR 的三 gates 證據，並證明遺失通知或 restart 後可續行而不重派／重貼；未執行階段如實列出。測試 SHALL 驗可觀察行為，不以 enum／實作步驟重述替代。（來源：D10、D19；可觀察恢復展示來自試用設計）

舊 S1 實作的測試、CI、review 與 bootstrap 證據 SHALL NOT 作為新實作的交付證據（D46）。

#### Scenario: AC-G19 模擬通過但 adapter 缺證據
- **WHEN** 可控制測試通過，但所選 Herdr＋runtime profile 的原生完成讀回、Reviewer 權限能力或正確 workspace placement 尚未驗證
- **THEN** 報告保留個別能力缺口，不聲稱 V4 或完整 E2E 通過，不以較強權限 workaround 補寫成功

#### Scenario: AC-G20 真實 review 沒有 finding
- **WHEN** 已授權真實試用的 review clean，沒有成立的 finding 可供修正
- **THEN** 如實保存 clean 結果並把 finding → fix → re-review 驗收列為未覆蓋，不虛構 blocker；本規格與測試條件不自行啟動 trial
