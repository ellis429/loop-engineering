# Spec Delta

## Purpose

讓 review、CI 與人工驗收發現的問題在同一 run 中保持可追溯身份，透過有界修正與獨立覆核推進到 PR Pass 或附證據的 Blocked。本文是本 change 的D40 已核准的規格；D 編號為已確認政策，欄位與批次身份等細部採設計契約提案，實作依 D40 分 S1／S2／S3。

本 capability 的 AC 以穩定 ID 保存；驗證對照已在 `docs/validation/implement-delivery-loop.md` 補齊驗法、通過標準與預期／實際證據。目前尚無產品執行結果，不因規格存在而視為已驗收。

## ADDED Requirements

### Requirement: FIN-01 唯一 finding authority 與阻擋準則

Finding 狀態 SHALL 以 controller 單一 writer 維護的本機 JSON registry 為權威。每項 finding SHALL 保存 stable ID、source、severity/blocking、位置、問題、依據／預期、狀態、修正 commits、覆核 evidence 及人工裁決。違反 spec/AC、可證明正確性／安全缺陷、必要驗證缺失 SHALL 為 blocking；風格／命名偏好不得因 severity 自動成 blocking。GitHub 討論 SHALL 經來源、actor、版本與時間核對匯入，不能成為第二套 authority。（來源：D09、D12、D24；欄位為契約提案）

#### Scenario: AC-F01 分類 review 意見
- **WHEN** Reviewer 提出一項具證據的 AC 缺陷與一項命名偏好
- **THEN** registry 將前者記 blocking、後者記 nonblocking，severity 只影響優先順序；各項都有可追溯依據與穩定 ID

#### Scenario: AC-F02 保持 identity
- **WHEN** 相同問題隨修正移動行號、改名或進入新輪次
- **THEN** 沿用 finding ID 並保存歷史；相同位置的不同問題或文字相近的問題不由 controller 自動合併，語意判斷由 Reviewer／適用人工裁決支持

### Requirement: FIN-02 Blocking 解除權限

Implementer SHALL 對 finding 提出 `fix_submitted`（commit/evidence）或 `disputed`（依據／可重現結果），不得自行解除 blocking。只有 Reviewer 的適用覆核或使用者對指定 finding／版本的明確裁決 SHALL 解除阻擋並保存理由與證據。關閉 GitHub thread、重複通知、帳號的 approve 能力與實作者「修好」宣告 SHALL 不作 closure。（來源：D09、D24、D25）

#### Scenario: AC-F03 修正尚未覆核
- **WHEN** Implementer 提交修正 commit，並在 GitHub 將 thread resolved
- **THEN** registry 保留 blocking，等待獨立覆核；新 head 先完成適用 G1 再取得新的 review/CI

#### Scenario: AC-F04 有證據解除
- **WHEN** Reviewer 對適用版本確認修正，或使用者明確裁決指定 finding／版本
- **THEN** registry 保存 closure actor、來源、版本、理由與 evidence，才解除該 blocker；G2 仍須滿足其餘所有 finding 與適用 review 條件

### Requirement: FIN-03 合併 correction batch 與三輪上限

正常 checking SHALL 收齊同一適用版本的 review/CI 後，把 findings、CI failures、scope、AC、驗法及依賴合併成唯一 correction batch。Batch 開始派修才 SHALL 增加一次 correction round；同一 run 最多三輪，不能按 finding/subagent/CI job 重複計數，也不能以 infra retry 或新 run ID 迴避上限。Implementation SHALL 依序；完成新 head 後回 G1 再取得 G2/G3。（來源：D13；batch 語意來自契約提案）

#### Scenario: AC-F05 CI 先失敗仍收齊 review
- **WHEN** CI fail 已知、同版本 Reviewer 尚未完成，且尚未到適用 timeout 或明確中止條件
- **THEN** 系統可收集診斷但不先派競爭修正；review 完成後把兩邊問題組同一 batch，首次派修增加一輪

#### Scenario: AC-F06 完整回應批次
- **WHEN** correction result 對 batch 內部分 finding 缺少 fix_submitted 或 disputed 回應
- **THEN** result 視為不完整，列出未回應 ID，不能據此解除 findings 或判 clean

#### Scenario: AC-F07 三輪已用完
- **WHEN** 同一 run 已派三輪 correction，仍有待修缺陷或人工退回
- **THEN** 保存已做修正、未解 findings、evidence 與待決問題並 Blocked，不派第四輪；明確追加預算須保存使用者裁決而非偷偷重建 run

### Requirement: FIN-04 一次爭議覆核

Implementer 的反證 SHALL 由 controller 送獨立 Reviewer 覆核一次，沿用 finding ID、原 batch 與適用版本，不另增加 correction round。Controller SHALL 保存反證 result、覆核 assignment/result 及已用次數；restart、重複結果、換 session 或換說法不得重置。仍有 blocking 爭議 SHALL Blocked 交使用者；scope/spec/AC 或設計變更直接沿 D11 回人。（來源：D25）

#### Scenario: AC-F08 Reviewer 接受反證
- **WHEN** 同一 blocker 首次 disputed，反證可重現且獨立 Reviewer 接受
- **THEN** 保存反證與覆核依據，依 FIN-02 更新 finding；沿用原 batch，correction round 不因釐清增加

#### Scenario: AC-F09 爭議仍在或重送
- **WHEN** 一次覆核後仍有 blocking 爭議，或 restart 後又收到同一反證
- **THEN** 顯示雙方依據及已使用的覆核，Blocked 交人，不另派第二次來重抽結論；基礎設施故障僅使用原操作的有界 infra retries

#### Scenario: AC-F10 反證伴隨新 head
- **WHEN** disputed 回應同時帶有程式修正造成新 head
- **THEN** 先取得新 head 的適用 G1，再將反證覆核與必要最新 review 合併；不以舊版本反證免除最新 review/CI

### Requirement: FIN-05 人工退回保留同一 run

使用者退回原 AC／已核准設計缺陷時，controller SHALL 以被退回版本保存 `source=human_acceptance`、actor、來源、時間、可重現差異與 stable finding；不要求此前已 accepted。既有 finding 沿用 ID，重複回饋按來源 identity 去重。退回 SHALL 失效目前 Pass、重評受影響 gates，沿用同一 run 與剩餘三輪預算。（來源：D09、D11、D13；人工 finding 具體化來自契約提案）

#### Scenario: AC-F11 首次驗收退回
- **WHEN** PR Pass 仍 acceptance pending，使用者指出原 AC 缺陷
- **THEN** 保存版本化退回與 finding，核對剩餘 correction 預算後才派修，解除仍須 Reviewer 覆核或明確人工裁決

#### Scenario: AC-F12 新需求或規格錯誤
- **WHEN** 人工回饋是原 scope 外的新想法或 spec/design 自身錯誤
- **THEN** 交 Project Lead 整理影響並由使用者選擇新 feature 或修訂版本；不當成普通修正默默降低 AC

### Requirement: FIN-06 Review 發布與可讀交接

Reviewer 結果 SHALL 先完整保存並經 controller 核對，再將完整 review 發到 PR，原 issue 發可採取行動的摘要與 PR review 連結。發布紀錄 SHALL 帶 run/review/result IDs、head/base/spec 版本與 finding IDs，可對回保存原文。Publication 狀態 SHALL 獨立於 review verdict；發文失敗不能清除 review 或假稱已發布。（來源：D24）

#### Scenario: AC-F13 完整 review 與摘要
- **WHEN** 適用 review 結果已保存，發布操作成功並可 read-back
- **THEN** PR 可讀到完整 findings/verdict，issue 可讀到需採取的動作與連結，兩者可追溯同一結果／版本；registry 仍是 finding authority

#### Scenario: AC-F14 發文失敗
- **WHEN** PR 或 issue 發文失敗，或回應 outcome unknown
- **THEN** 保存原 review 與個別 operation 的狀態，依 durable-delivery 的 outbox/reconcile 規則只恢復發布；不重做 review、重派修正或聲稱內容已上線

### Requirement: FIN-07 反覆 finding 的提前升級

Controller SHALL 追蹤每個 stable finding 的有效修正與 Reviewer 覆核次數，依核准 recurrence policy 辨識「修正後仍未解決」與「曾經確認解除後再出現」。達到反覆條件 SHALL 保存歷史、診斷摘要與待決選項並 Blocked 交人，不必耗盡三輪總額度才處理；重複通知、同一 result 重送與 infra retry 不得增加計數。Scope 明顯擴大仍直接沿 D11 回人。（來源：初始 handoff、workflow-contracts 反覆 finding 要求；具體閾值見 design 提案）

#### Scenario: AC-F15 連續修正仍留下同一 blocker
- **WHEN** 同一 finding 經不同 correction batches 的有效修正與獨立 re-review，仍未解除，並達到核准 policy 的反覆閾值
- **THEN** Controller 在下一次派修前 Blocked，顯示每輪 commit／覆核證據與尚餘總預算，要求診斷／裁決；不以換 ID、session 或 reviewer 重新起算

#### Scenario: AC-F16 已解除的 blocker 再次出現
- **WHEN** Reviewer 在新版本辨識到先前已確認解除的同一語意缺陷再次出現
- **THEN** 保存穩定 identity 的 reopen lineage，依 recurrence policy 提前 Blocked；新位置的新問題不得僅因文字相似被錯算為舊問題，語意關聯須有 Reviewer 依據
