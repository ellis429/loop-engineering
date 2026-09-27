# Orca Delivery：Project intent

日期：2026-09-25。來源：使用者 agent handoff 及後續已確認決策。本文是已知需求基線，正式規格由 OpenSpec artifacts 承接。

## 2026-09-27：完整成品與本輪收斂（D41／D42）

**成品是可供多人依循、交接並展示的 Loop Engineering 專案**，結合 multi-person workflow、開源 skills、custom multi-agent controller 與 example project。Controller 是整套方法的工具之一；成功不以 controller 模組數量或單一 PR 測試全綠判定。

已確認的三項交付：

1. **方法與入口**：Project／Feature 兩層流程、角色及人工決策邊界；member 從 orchestrate 得知目前階段、適用方法、交接物與下一步。沿用開源 skills 的原生 artifacts 與限制，引用唯一權威版本，不要求每人自行重新挑選整套工具。
2. **薄 controller**：orchestrate skill 所在 agent 可呼叫的確定性程式；保存 JSON／YAML 狀態、驗證交接／證據適用性、計算三 gates、記錄 findings 與允許的下一步。Orchestrate 是每個 feature 的唯一外層協調循環；controller 是狀態及品質規則的唯一寫入／判定入口，不另起持續運作的 agent supervisor。
3. **可查閱的 example project**：依 D43，先在本 repo 測通最小真實 delivery loop，再以 Herdr、orchestrate skill 與薄 controller 執行 cross-node-file-transfer；依 D44，本機 OpenAI 使用 OpenCode，Claude 由 Herdr 直接啟動 Claude Code。沿用適用的既有基準，從 Project baseline、roadmap／milestones、Phase 0 到多個 features，留下新的 worktrees／branches、spec／design／plan、issues／PRs、review-fix-re-review、CI、人工決策及 Retro 歷程。人可在需要判斷的位置加入，從保存的文件及狀態接手；舊程式的驗證不能算成新 example 的交付證據。

使用者提出 multiple PR stacked gating 作為完整展示目標。多個獨立 PR 與基於未合併上游的 PR stack 必須區分：後者涉及 D27 變更、上游版本／review base、依賴失效及人工合併順序，具體政策見待回答的 Q-STACK。這個目標不表示 stacked scheduler 或多人執行平台要放回第一個 controller 切片。

### Orchestrate 與 controller 的責任

| 元件 | 負責 | 邊界 |
| --- | --- | --- |
| 人＋角色 agent | Project Lead 的 research／SA／spec／roadmap，Implementer 的 design／tasks／TDD，Reviewer 的獨立審查，人處理重要決策及驗收 | 角色可由不同 member 指揮；責任依授權及交接，非固定 runtime 父子階層 |
| Orchestrate skill／agent | 載入適用方法、呼叫 controller 取得允許動作、使用既有 runtime／工具派工、收回並提交結果、處理人工介入 | 同一 feature 只允許一個 active coordinator；不同 feature 可有各自 owner，不增加第二個同 feature 外層 loop |
| Controller CLI | 結構／身份／版本驗證、持久化狀態、gate 計算、finding lifecycle、輪次／預算檢查、下一步與 Blocked 原因 | 不以 agent 自述放行，不從結果檔執行任意 argv，不自行推論業務需求或修改品質政策 |
| Runtime／git／GitHub／CI | Agent sessions、既有隔離能力、worktree 操作、PR 發布、真實 check 結果 | 經窄工具介面取得證據；缺少必要能力時明示 Blocked，不由 controller 重建通用執行平台 |

Controller 每次呼叫讀取／核對輸入，完成一次狀態更新或判定後回傳；具體 CLI 命令與 schema 留給修訂 design，不把概念示例當成現有可用 API。Skills 提供工作方法；只有 orchestrate 組合外層流程，其他 skills 不另啟 feature loop。

### 第一個可驗證切片的收斂方向

保留三 gates、獨立 Reviewer、最新 head／review base／文件版本、TDD 原始 Red 與最終 Green 的追溯、finding 覆核、可讀持久化、必要的去重與單一 writer。正常 review/fix loop 仍要能自動前進；並非把日常搬運工作還給人。

先借用 runtime／git／GitHub 的既有能力，不自行建 OS sandbox、credential broker、分散式 ownership、通用程序 supervisor 或全面 crash 自動恢復。執行結果、writer 狀態、外部寫入是否成功無法核對時，保存待處理操作及證據，停止相關派工／重試並交人接手。保存 pending／result identity 與判重仍是必要契約；降低自動恢復承諾不等於容許重複派工、偽造證據或修改 reviewer branch。

多人流程先指跨角色、跨 session 的明確 owner、版本與交接；不宣稱已具備多租戶身份管理或跨主機協調。Worktree 的保留方式與位置納入操作文件，demo 不自動刪除展示所需工作區；repo 歷程與可分享證據另外保存，不能只依賴本機暫存目錄。

**規劃狀態**：D41／D42 已確認方向；精確的新切片、CLI／schema、AC 差異與 implementation plan 尚待整理及 review，沿 D11 確認後才重新派工。D40 的舊 design、88 項 AC、S1→S2→S3 計畫及已寫程式保留為歷史基準，不再繼續擴充它們的執行平台承諾。舊 PR 的 17 項 blocking findings 仍保留，逐項標示新範圍內需修、替換後需重新驗證或已移除機制的適用性證據；不能因縮 scope 就視為 review clean。

目前 [PR #2](https://github.com/yschiang/orca-delivery/pull/2) 停在未合併狀態。Opus 已保存第一輪修正 checkpoint；14 項僅為 fix_submitted、3 項未完成，沒有獨立覆核或 PR Pass。既有 CI 成功也不解決尚待決定的必要 check policy 讀取限制。

以下為原需求基線；涉及 controller 自動派工／全面恢复的實作承諾由本節收斂，其餘品質要求維持。正式 OpenSpec 修訂需逐項對照，不默默刪除既有 AC。

## 2026-09-27：收斂後政策（D47–D49）

使用者已接受：協調 session 離線期間不保證 4h 準時停止，恢復時保守核算、處理仍執行的 worker 並 Blocked；第一版採可信本機協作的威脅邊界，仍驗 runtime 權限、原始 Red／目前 Green 與獨立 review；本 repo 可採人工核准且版控的 G3 checks 政策，明示 GitHub rules 未核對。具體 checks 及設計／plan 仍待 D11，`test` 只是未核准範例。完整邊界見 [決策 D47–D49](decisions.md)，不將這次政策批准當產品 gate 或完整設計批准。

## 2026-09-27：第一個可用切片（D50）

先查核選用 runtime 的交接與 Reviewer 能力，再以一個 feature、序列 Implementer worktree、獨立 Reviewer 跑通真實 TDD→PR→review／CI→fix→re-review→Pass／Blocked。Minimum orchestrate 與必要工具納入同一交付切片；fake 測試仍先驗困難狀態，但不將全部通用 controller 功能列為真實 loop 的前置。三 gates 與證據維持，Project／跨 feature 等後續自動化明確延後，不算已完成。具體 [D50 候選](../../loop-engineering-thin/docs/design-candidate/d45-03/README.md) 已完成限定範圍文件覆核，未通過 D11。

## Problem

目前人需要在 Claude Code 與 Codex agents 之間搬運 context、追蹤 review、通知實作者修正，再核對 CI 與 review 是否適用最新變更。Agent 的完成訊息不足以證明交付可驗收。

## Outcome

使用者透過預設 OpenCode 或選配的 Orca 等入口，選擇含有或引用 feature spec 的 GitHub issue。系統協助研究與設計、產生可派工 plan、執行 TDD、整合 PR、獨立審查並查核 CI，再以 review/fix loop 推進到 PR Pass，或帶證據轉交人裁決。

Project spec 定義共用契約，feature spec 定義該交付的範圍與驗收。Feature ticket 可直接承擔 feature spec；每個可獨立驗收 feature 對應一個 PR，tasks 為派工單位。

依 D20／D32，Project Lead Agent 與使用者先做 research、SA、domain modeling、grill 與 high-level design，形成 project baseline、roadmap／milestones 並拆 features；每個 feature 再經聚焦分析，準備 spec／AC、設計邊界與 ticket。Implementer Agent 繼續研究，負責 detailed design、最終 plan／tasks、TDD 實作、整合與修正；Project Lead 可提工作包或任務草案，由 Implementer 校準。Reviewer Agent 獨立審查與覆核；依 D41，orchestrate 透過既有 runtime 執行派工，唯一 controller 管理派工許可、狀態與 gates；重要變更沿 D11 回人，不新增逐 task 簽核。

依 D33，先在本 repo 測通 workflow、orchestrate 與預設工具組合，讓 member 可依同一入口及可追溯交接工作。後續用 cross-node-file-transfer 從既有需求／設計基準初始化，再跑完整 feature loop；文件保留來源與未決狀態，不重做已確認需求的完整 grill，新實作保存新證據。具體工具組合仍依 Q-METHOD 收斂。

## Confirmed constraints

1. G1 先通過才送審。G2 獨立 review 與 G3 CI 可並行，任一不通過都不可 PR Pass。
2. Gate 判定讀取結構化結果及實際證據，不能依 agent 自述、終端閒置、通知或 task completed 判定。
3. 結論綁定 PR head、review base、project / feature specs、design 與適用 plan 版本；變更時評估相關失效。
4. Red 來自歷史 snapshot，可早於最終 head，但需追溯到同一 task / 修正；最終 Green 與 regression 適用整合後 head。
5. Missing/pending/cancelled/timed-out/unknown/stale 不能當 success；skipped/neutral 必須有明確政策。
6. Findings 保留穩定 identity、來源、severity/blocking、位置、依據、預期行為、狀態、fix commit 與覆核證據。實作者無權自行解除 reviewer 阻擋。
7. 先保存結果，再發布與通知。Reconcile 可在通知遺失後找回成果；重複事件不重複派工／發文。GitHub 發布失敗只重試發布。
8. 正常情況收齊同版本 review / CI 後合併成一個修正批次；stuck work 有 timeout 與有界 recovery。
9. 狀態持久化，重啟後核對外部實況再接續；runtime／接入服務不可查詢時不能推論 worker 已停止並派出競爭實作者。
10. 並行修改使用隔離 worktrees，依賴工作依序整合；review 與 CI 針對最終整合 PR。Reviewer 不修改被審查 branch。
11. Skills 不擁有 feature gate；D41 的 orchestrate 是唯一外層協調入口，其他工作 skills 不另啟 dispatch loop。沿用現有方法並以薄封裝統一契約，保留已安裝版本的呼叫限制。
12. MVP 使用既有 agent 入口及 GitHub，不建立新 dashboard；OpenCode 是預設 runtime，Orca／Codex／Claude Code 為選配；交付終點 PR Pass，不包含 merge、close issue、release 或 deploy。
13. 每個 feature 在 design+plan 完成後開工前由使用者確認一次；後續 scope/spec/AC 變更、設計缺陷或阻擋爭議回到使用者。
14. 違反 spec/AC、可證明的正確性/安全缺陷、必要驗證缺失屬 blocking；風格偏好不阻擋。實作依序，review 與 CI 並行；每個 run 主動執行最多 4 小時、最多 3 輪 correction、每項 infra 操作最多額外重試 2 次，到限轉 Blocked。
15. 設定與執行狀態採人可閱讀的 JSON／YAML 檔案；不用 SQLite 作為 MVP 的持久化實作，仍需維持恢復、版本判定與去重語意。

## Environment and chosen integration

獨立 repo，既有規劃文件使用 OpenSpec，authoring／planning 組合依 D31／Q-METHOD 重新評估。依 D41，由 orchestrate 呼叫薄 controller 核對狀態與允許動作，再使用選定工具執行派工；agent 承接語意工作。D38 的預設接法由 OpenCode adapter 執行獨立角色 sessions、選用 OpenAI／Claude models；Orca／Codex／Claude Code 是可選入口或 runtime 接入。啟動／resume、worktree 及結果回收不依賴這些選配工具；模型指定也不綁定同廠牌 runtime。共用契約與 G2 獨立性維持，精確 reviewer model 與能力仍須查證。

2026-09-25 的查核為歷史快照，見 [research](research/2026-09-25/research.md)；2026-09-27 的本機版本與限制見 [planning preflight](research/2026-09-27/planning-preflight.md)。公司 OpenCode 版本、模型與工具尚未查核，本機結果不代替公司實測。

## Acceptance scenarios

| ID | 情境 | 必須觀察到的行為 |
| --- | --- | --- |
| A01 | 正常 feature | Issue → design/plan → TDD → PR → review/CI → Pass，全程有版本化證據 |
| A02 | Blocking finding | 派修、更新 PR、重新驗證及 review，由覆核解除阻擋 |
| A03 | Review clean、CI fail | 不可 Pass，修正後查核最新版本 |
| A04 | CI green、review fail | 不可 Pass，CI 不取代 review |
| A05 | 自述 TDD 完成但缺證據 | G1 不通過，指出需補的可驗證資料 |
| A06 | 舊 SHA 晚到或 Pass 前 push | 舊結果不能放行，刷新版本並失效相關 gates |
| A07 | Missing/pending/cancelled check | 不誤判 CI clean，保存原因 |
| A08 | 重複事件或遺失通知 | 不重複派工/發文，reconcile 可恢復進度 |
| A09 | Agent crash 或 controller restart | 讀持久化狀態、核對外部實況再 resume 或安全重派 |
| A10 | 上限或爭議 | Blocked，附原因、證據與需要人的決策 |
| A11 | GitHub 發布失敗 | 保留結果，可重試發布，不重做 review、不假裝已發布 |
| A12 | Reviewer 與作者隔離 | Reviewer 可檢查與驗證，不能修改 author branch 或自行關閉品質 gate |
| A13 | 真實端到端展示 | 至少一次真實 review finding → fix → re-review，並證明最新 PR 的三 gates |

## Open decisions

D32 已確認研究／分析／高層設計與詳細設計／tasks 的分工；graphiphy、research-codebase、domain-modeling、grilling 及 spec／plan 工具是候選方法，需查明實際版本與交接契約，不能將本輪流程確認當成整套工具已定案。

依 D33，目前在 orca-delivery 完成及驗證工具流程，後續完整試用方向為 cross-node-file-transfer。D15／D16／D18 的 gigaxfer pre-PR 接入保留暫緩，不再是預設下一步；只有日後重新選擇它才核對 Q-TARGET 與控制權交接。P03 Retro 依 D22 等使用者明確開始，本輪不接管 gigaxfer。

D24–D28 已確認 finding 權威／發布、一次爭議覆核、TDD／非行為例外、相依 feature 與自動 Retro 候選；CIT 依 D29 暫不處理，G3 維持必要 CI。預設 runtime 依 D38 為 OpenCode；精確模型／環境與具體執行預設落入 design / plan，Q-TARGET 僅在另行恢復舊 PR 試用前核對；政策見 [decisions](decisions.md)，交接範圍見 [實驗文件](experiments/pr-gating.md)。
