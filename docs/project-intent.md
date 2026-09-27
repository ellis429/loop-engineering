# Orca Delivery：Project intent

日期：2026-09-25。來源：使用者 agent handoff 及後續已確認決策。本文是已知需求基線，正式規格由 OpenSpec artifacts 承接。

## Problem

目前人需要在 Claude Code 與 Codex agents 之間搬運 context、追蹤 review、通知實作者修正，再核對 CI 與 review 是否適用最新變更。Agent 的完成訊息不足以證明交付可驗收。

## Outcome

使用者透過預設 OpenCode 或選配的 Orca 等入口，選擇含有或引用 feature spec 的 GitHub issue。系統協助研究與設計、產生可派工 plan、執行 TDD、整合 PR、獨立審查並查核 CI，再以 review/fix loop 推進到 PR Pass，或帶證據轉交人裁決。

Project spec 定義共用契約，feature spec 定義該交付的範圍與驗收。Feature ticket 可直接承擔 feature spec；每個可獨立驗收 feature 對應一個 PR，tasks 為派工單位。

依 D20／D32，Project Lead Agent 與使用者先做 research、SA、domain modeling、grill 與 high-level design，形成 project baseline、roadmap／milestones 並拆 features；每個 feature 再經聚焦分析，準備 spec／AC、設計邊界與 ticket。Implementer Agent 繼續研究，負責 detailed design、最終 plan／tasks、TDD 實作、整合與修正；Project Lead 可提工作包或任務草案，由 Implementer 校準。Reviewer Agent 獨立審查與覆核，唯一 controller 管理確定性的派工與 gates；重要變更沿 D11 回人，不新增逐 task 簽核。

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
11. Skills 不擁有 feature gate 或外層 dispatch loop。沿用現有方法並以薄封裝統一契約，保留已安裝版本的呼叫限制。
12. MVP 使用既有 agent 入口及 GitHub，不建立新 dashboard；OpenCode 是預設 runtime，Orca／Codex／Claude Code 為選配；交付終點 PR Pass，不包含 merge、close issue、release 或 deploy。
13. 每個 feature 在 design+plan 完成後開工前由使用者確認一次；後續 scope/spec/AC 變更、設計缺陷或阻擋爭議回到使用者。
14. 違反 spec/AC、可證明的正確性/安全缺陷、必要驗證缺失屬 blocking；風格偏好不阻擋。實作依序，review 與 CI 並行；每個 run 主動執行最多 4 小時、最多 3 輪 correction、每項 infra 操作最多額外重試 2 次，到限轉 Blocked。
15. 設定與執行狀態採人可閱讀的 JSON／YAML 檔案；不用 SQLite 作為 MVP 的持久化實作，仍需維持恢復、版本判定與去重語意。

## Environment and chosen integration

獨立 repo，既有規劃文件使用 OpenSpec，authoring／planning 組合依 D31／Q-METHOD 重新評估。單一持久化 controller 決定狀態與派工，agent 承接語意工作。D38 的預設接法由 OpenCode adapter 執行獨立角色 sessions、選用 OpenAI／Claude models；Orca／Codex／Claude Code 是可選入口或 runtime 接入。啟動／resume、worktree 及結果回收不依賴這些選配工具；模型指定也不綁定同廠牌 runtime。共用契約與 G2 獨立性維持，精確 reviewer model 與能力仍須查證。

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
