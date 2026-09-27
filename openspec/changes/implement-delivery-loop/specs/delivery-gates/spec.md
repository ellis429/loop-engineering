# Spec Delta

> **D41／D42：scope revision pending（2026-09-27）**。使用者已同意收斂為 orchestrate skill 呼叫薄 controller；舊 S1 修正已停止並保存。本文的 D40 技術內容／AC 是歷史核准基準，尚未完成新 scope 的逐項映射，不是繼續舊計畫的派工授權。三 gates、版本與 finding 覆核維持；新 design／plan 仍須 review 及 D11 確認。歷史 approval.json 保持原樣，不代表本次修訂已核准。最新 [產品目標及邊界](../../../../../docs/project-intent.md)、[決策 D41／D42](../../../../../docs/decisions.md)。

## Purpose

以可讀取且適用交付版本的證據分別判定實作/TDD、獨立 review 與必要 CI，只有三 gates 一致成立才提供 PR Pass。本文是本 change 的D40 已核准的規格；D 編號標示既有決策，細部 evidence/check 核對方式取自設計契約提案，測試 seam 以 design 的提案為準，已隨 D40 一次確認。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 `docs/validation/implement-delivery-loop.md` 補齊驗法、通過標準與預期／實際證據。目前尚無產品執行結果，不因規格存在而視為已驗收。

## ADDED Requirements

### Requirement: GAT-01 三 gates 與執行結果分離

Controller SHALL 先確認 G1，才正式送 G2；G2 與 G3 可並行。PR Pass SHALL 要求 G1 實作/TDD、G2 獨立 review、G3 必要 CI 均適用目前版本且通過。Task succeeded、agent 摘要、終端 idle、input accepted 或通知 SHALL 不作 gate 成功證據；missing、pending、failed、stale、unknown 等未通過狀態須保留原因。（來源：D01、D09、D13）

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

#### Scenario: AC-G04 摘要與證據不一致
- **WHEN** result 宣稱測試通過但原始 log 缺失、hash 不符、exit code 失敗或 snapshot 不適用
- **THEN** gate 不通過，逐項顯示缺失／衝突及 producer；不以摘要、測試總數或 plan 的預期輸出替代

#### Scenario: AC-G05 驗證與程式分離引用
- **WHEN** 最終程式版本的 evidence 在 runner result 中綁定實際 snapshot，tracked 驗收文件引用該 result
- **THEN** 系統可核對程式版本與證據關係，不要求文件以自身 commit SHA 自我引用；後續只改文件仍須保存差異與證據適用理由

### Requirement: GAT-03 歷史 Red 與目前整合 Green

G1 SHALL 對行為變更要求 Superpowers TDD 的歷史 Red：測試已存在、對應行為尚未實作／修正的 source snapshot、命令、失敗原因及原始輸出。Red SHALL 可早於最終 SHA，但必須追溯同一 task／後續修正與 Green/refactor；最終 Green 及必要 regression SHALL 適用目前整合 head。Task worktree 的成功不能直接推出整合成功。（來源：D01、D26）

#### Scenario: AC-G06 不同 SHA 的有效 Red 與 Green
- **WHEN** task 的 Red snapshot R 因目標行為缺失而失敗，修正／整合 lineage 可追至目前 head H，且 H 的必要驗證為 Green
- **THEN** G1 可採用 R 的歷史 Red 與 H 的 Green，不要求兩者同 SHA 或重新製造 Red

#### Scenario: AC-G07 缺歷史或錯誤的 Red
- **WHEN** 既有 feature 只有當前綠燈，或所稱 Red 只是語法／環境錯誤，或事後 replay 被稱作原始 test-first
- **THEN** G1 明列 missing／invalid；可補證據就補，無法取得歷史 Red 則 Blocked 待裁決；事後 replay 清楚標示其性質，不能冒充原始歷史

#### Scenario: AC-G08 整合回歸失敗
- **WHEN** 個別 task 都成功，但整合 head 的必要 regression 失敗
- **THEN** G1 不通過，保存 task commit 到 integration commit 的對應與實際失敗，要求修正整合版本

### Requirement: GAT-04 獨立 N/A eligibility

純文件／註解變更 SHALL 可提出附理由、diff 分類與必要文檔檢查的 TDD N/A 申請，由 controller 派獨立 Reviewer 核對實際行為影響；Implementer 不得自行豁免。Eligibility SHALL 先於整體 G1，其結果只免除適用範圍的 Red/Green，不能取代 G2 clean 或免除必要驗證/G3。設定、migration、test code SHALL 依真實行為判斷。（來源：D26）

#### Scenario: AC-G09 純文件 N/A 通過
- **WHEN** 獨立 Reviewer 對固定 diff 確認沒有行為影響，必要檢查可讀且通過
- **THEN** 系統保存 eligibility 決定、版本、理由與證據，依適用 N/A 完成 G1 後才正式 G2；G2 仍未自動通過

#### Scenario: AC-G10 行為變更或待核對的 N/A
- **WHEN** Implementer 對設定行為變更自行宣告 N/A，或 eligibility 尚未完成／被拒絕
- **THEN** G1 不因此通過，依拒絕原因補 TDD／證據或轉 Blocked；不能將「檔案類型是設定」視為豁免

### Requirement: GAT-05 獨立整合 review

G2 SHALL 由 controller 派出的獨立 Reviewer assignment/session，對照適用 spec、design、AC、完整 PR diff、相關 codebase、工程規範、舊 findings 與修正／反證。Reviewer SHALL 能隔離驗證並保存結果，但不得修改作者 branch、直接關 gate 或由 Implementer 的 subagent 取代。既有獨立 Codex review 要求 SHALL 保留；依 D38 預設由 OpenCode 的獨立 session 承載核准 reviewer model，Codex CLI 非必要前置。精確 provider/model 與隔離能力 SHALL 在選用前核對，不能以任意 OpenAI model、不同 model 或角色名稱即宣稱符合。（來源：D01、D09、D20、D23、D30、D38）

#### Scenario: AC-G11 有效獨立 review
- **WHEN** controller 派出符合核准 runtime/model 與隔離限制的 Reviewer，結果已驗證且沒有未解除 blocking finding
- **THEN** 只有適用目前版本的 clean verdict 可使 G2 通過，並保存 assignment/session、完整 review、覆核 evidence 與版本

#### Scenario: AC-G12 局部 review 或隔離無法證明
- **WHEN** 提供的是 Implementer 呼叫的 review subagent 結果，或 Reviewer 的工具可改作者 branch，或獨立性／隔離尚無可核對證據
- **THEN** 不採為 G2；顯示獨立性或 adapter 能力缺口，不默默放寬權限，也不因只禁用 edit 工具便聲稱所有工具安全

### Requirement: GAT-06 必要 CI 與非成功狀態

G3 SHALL 從 GitHub 查核明示且與可讀 repo 規則核對的 required check 集合；空集合不得自動成功。每項 SHALL 核對 name/context、app/provider、source SHA、head/base 關係、attempt 時序、status/conclusion 與可讀 URL，涵蓋完整分頁。Missing、pending、cancelled、timed-out、failed、unknown、stale SHALL 不視為成功；skipped/neutral 只有明確適用 policy 允許才可接受，不能套用未批准的例外。（來源：D01、D29；check identity 細節來自契約提案）

#### Scenario: AC-G13 非成功 check 與空集合
- **WHEN** required 集合未設定／為空，或任一 required check missing、pending、cancelled、timed-out、failed、unknown、stale
- **THEN** G3 不通過並逐項顯示原因；skipped/neutral 無明確接受 policy 時也不通過

#### Scenario: AC-G14 舊成功不能蓋過新 attempt
- **WHEN** 同名 check 的舊 attempt success，但目前適用 attempt pending/failed，或同名結果來自未知 provider
- **THEN** G3 採目前適用 attempt 與核准來源，不以舊 success 或名稱相同的其他來源放行

#### Scenario: AC-G15 衍生整合 snapshot
- **WHEN** CI 使用不同於 PR head 的 integration snapshot
- **THEN** 只有可驗證的 head/base 映射與適用接受規則成立才採用；不能只比名稱或因 SHA 字串不同一概接受／拒絕，無法確認時為 unknown

### Requirement: GAT-07 版本變更使結論失效

Gate 判定 SHALL 綁定 repo/PR、head、實際 base ref/tip、review merge-base、project/feature spec、design/plan/policy digests 及執行 skill/controller 版本。新 head SHALL 重新取得目前版本的 G1 最終驗證、G2 結論與 G3 checks，歷史 Red 保留 lineage。Base/spec/design/AC/plan/skill/policy 變更 SHALL 評估相關失效及任何證據沿用理由，不得只改規則來消除 blocker。需 D11 確認的變更先回 planning/awaiting approval。（來源：D01、D11、D19；版本集合與失效路由來自契約提案）

#### Scenario: AC-G16 舊結果晚到
- **WHEN** 目前為 H2，而 H1 的 review、CI 或 result 才送達
- **THEN** 保存 H1 的歷史證據但不拿來放行 H2；H2 從需要重評的 G1 或 G2/G3 續行，不重置 finding／budget

#### Scenario: AC-G17 Base 或規格改變
- **WHEN** head 相同但 base/merge-base 或適用 spec/design/AC 改變
- **THEN** 系統重建 diff／整合風險或驗法並要求 Reviewer 讀新契約；CI 若沿用須保存適用理由，需人工確認時停止依舊版本派工

#### Scenario: AC-G18 Pass 前後發生 push
- **WHEN** Pass 前重新讀到的 head/base/artifacts 不一致，或已保存 Pass 後出現新 push
- **THEN** 前者放棄本次 Pass 並 reconcile；後者保存舊 Pass 版本及觀察時間而失效當前結論，重新驗證；不宣稱跨外部多次讀取具全域 transaction

### Requirement: GAT-08 驗收證據區分模擬與真實交付

驗收報告 SHALL 明確區分可控制測試、真實 adapter 能力與完整交付 E2E。真實驗收 SHALL 包含至少一次成立的 finding → fix → re-review 與最新 PR 的三 gates 證據，並證明遺失通知或 restart 後可續行而不重派／重貼；未執行階段如實列出。測試 SHALL 驗可觀察行為，不以 enum／實作步驟重述替代。（來源：D10、D19；可觀察恢復展示來自試用設計）

#### Scenario: AC-G19 模擬通過但 adapter 缺證據
- **WHEN** 可控制測試通過，但 Codex native completion、Reviewer 全工具隔離或正確 workspace placement 尚未驗證
- **THEN** 報告保留個別能力缺口，不聲稱 V4 或完整 E2E 通過，不以較強權限 workaround 補寫成功

#### Scenario: AC-G20 真實 review 沒有 finding
- **WHEN** 已授權真實試用的 review clean，沒有成立的 finding 可供修正
- **THEN** 如實保存 clean 結果並把 finding → fix → re-review 驗收列為未覆蓋，不虛構 blocker；本規格與測試條件不自行啟動 trial
