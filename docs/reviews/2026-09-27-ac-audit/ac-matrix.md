# 88 AC：合理性、驗法與實現狀態逐項核對

本表是審核建議，沒有修改或刪除已確認需求。判定以 D50 候選＋D45-02 delta＋正式舊 scenario 合讀；原情境連結用於追溯，不表示舊文全數仍是生效的新規格。

**共同實現狀態：新版沒有 src/tests/orchestrate skill，尚无產品 AC 驗收。** Workflow 文件與 H0 小型 probes 已存在，但不等於已部署 skill 或正式 runtime profile 通過。舊 delivery code/tests 只作不可轉移的歷史候選。個別 mapping 與完整 scenario 見 [JSON ledger](ac-ledger.json)。

「主要情境明列」只表示計畫有相符的核心行為案例，不是測試已寫、完整 coverage 或 passed。「驗法部分」表示義務合理但現有 V/T 引用不足。「文件驗收待具體化」應用樣本與 rubric 驗收，不強迫寫成 controller unit test。

## Orchestration：逐項核對

| AC／原情境 | 建議歸屬 | 驗法評估 | 理由與最小補強 |
| --- | --- | --- | --- |
| [AC-O01 直接與 Implementer 協作](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:17) | Workflow／人工契約 | 驗法部分／缺情境 | 直接交付應可進 design/plan；V3 只驗沒有批准不派工，缺正向入口與不要求 Project Lead 轉達。 |
| [AC-O02 拒絕第二個外層 loop](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:21) | 保留核心行為 | 主要情境明列 | 保留唯一外層協調與正式 review 授權；V2、V6 主要負例合理。 |
| [AC-O03 引用既有文件](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:37) | 保留核心行為 | 驗法部分／缺情境 | 保留原生 locator/version；T2.2 只列 digest，須驗讀回原生文件、不改名及 task 不另成 PR。 |
| [AC-O04 權威來源衝突](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:41) | Workflow／人工契約 | 文件驗收待具體化 | 引用缺失可程式核對，語意矛盾由 agent／人判斷；需一個衝突交接案例，不能只測 hash。 |
| [AC-O05 新 feature 尚未批准](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:49) | 保留核心行為 | 主要情境明列 | 版本化開工批准必要；V3 明列草案／沉默／agent 身分不構成批准。 |
| [AC-O06 核准後按 plan 前進](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:53) | 保留核心行為 | 驗法部分／缺情境 | 除了批准紀錄，需正向測 approve→首次合法 assignment，含 AC／驗法及修正無逐 task 重批。 |
| [AC-O07 需求變更不混入修正](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:57) | 保留核心行為 | 主要情境明列 | scope/AC 變更回人合理；T2.2、V3 明列失效批准與停止。 |
| [AC-O08 已實作 pre-PR 接入](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:65) | 後續能力 | 延期未覆蓋 | 舊 feature adopt 合理但首片延期；unsupported 只驗拒絕，不能算 adopt 成功。 |
| [AC-O09 Adopt 缺口](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:69) | 後續能力 | 延期未覆蓋 | adopt 缺口路由隨 adopt 延後；保留不補造 Red／不接未知 writer 原則。 |
| [AC-O10 Pass 尚未接受或 merge](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:77) | 保留核心行為 | 驗法部分／缺情境 | Pass≠accept≠merge；V8 缺零 merge/close/release/deploy 副作用及 acceptance pending 斷言。 |
| [AC-O11 接受後的新版本](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:81) | 保留核心行為 | 驗法部分／缺情境 | 需要 V1 accepted→V2 pending 的正反案例；目前只寫 acceptance 綁定版本。 |
| [AC-O12 上游 accepted 但未 merge](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:89) | Workflow／人工契約 | 驗法部分／缺情境 | D27 必須保留；T8.0 有人工核對，還需 accepted 未 merged 時零下游派工的操作紀錄。 |
| [AC-O13 Merge 與 baseline 都適用](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:93) | Workflow／人工契約 | 驗法部分／缺情境 | 人工／skill 解除相依等待足夠；需驗已 merge 但 baseline 不含成果仍拒絕、適用時仍核對自身 D11。 |
| [AC-O14 重複接受事件](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:101) | 後續能力 | 延期未覆蓋 | Retro 候選與去重是後續 workflow 能力；不必強迫做 controller Retro operation。 |
| [AC-O15 暫停的 P03 試用](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:105) | 歷史限制 | 歷史，不作產品測項 | P03/session/Q-TARGET 是歷史限制；建議留 handoff，通用規則併入未授權不接管，勿寫產品特判。 |
| [AC-O16 Skills 交回 controller](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:113) | Workflow／人工契約 | 文件驗收待具體化 | skill 不另起 loop 合理；尚無 orchestrate SKILL 或實際 handoff，需 DOC 清單與一次結果交接。 |
| [AC-O17 另一 repo 的規則混入草稿](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:121) | Workflow／人工契約 | 文件驗收待具體化 | 規則來源歸屬合理；需跨 repo 規則混入的審查樣本與拒絕採用紀錄。 |
| [AC-O18 授權 Project Lead 協調與委派](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:25) | 後續能力 | 延期未覆蓋 | Project Lead 授權委派保留為後續能力；首片 delegate unsupported 不能算已驗收委派。 |
| [AC-O19 入口與 runtime 關係不授予決策權](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:29) | Workflow／人工契約 | 驗法部分／缺情境 | 角色／runtime 父子关系不授權；V2 只驗 claim，沒有角色權限負例。 |
| [AC-O20 從 project 分析拆出 features](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:129) | Workflow／人工契約 | 文件驗收待具體化 | Project research→milestone→features 是 workflow 產出物驗收，非 controller 功能；需成果樣本與人工 rubric。 |
| [AC-O21 單一 feature 的聚焦分析與交接](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:133) | Workflow／人工契約 | 文件驗收待具體化 | feature 聚焦分析及沿用 baseline 合理；需差異／未決交接樣本，不能用模板存在驗收。 |
| [AC-O22 Project Lead 提供初步 tasks](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:141) | Workflow／人工契約 | 驗法部分／缺情境 | Implementer 校準唯一 plan 合理；V3 草案拒絕只驗一半，缺 tasks 來源與校準後交接。 |
| [AC-O23 詳細設計發現跨 feature 影響](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:145) | Workflow／人工契約 | 文件驗收待具體化 | 跨 feature 影響回人保留；局部繼續的自動化可延期，不能把需求裁決本身移出首片。 |
| [AC-O24 專案與功能的分析深度](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:153) | Workflow／人工契約 | 文件驗收待具體化 | Project／feature SA 深度不同合理，與 O20/O21 可共用同一驗收樣本，避免重複文件。 |
| [AC-O25 文件齊全但需求仍有阻擋](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:157) | Workflow／人工契約 | 文件驗收待具體化 | 文件齊不等於 SA ready；需要未決問題仍存在時拒絕交接的人工／skill 樣本。 |
| [AC-O26 適用 SA 確認與開工確認分開](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:161) | Workflow／人工契約 | 驗法部分／缺情境 | SA 確認≠D11 合理；V3 沒有只給 SA 確認仍拒絕 implementation 的對照案例。 |
| [AC-O27 研究發現與使用者描述衝突](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:165) | Workflow／人工契約 | 文件驗收待具體化 | 現況與需求衝突應保留裁決；要看來源／影響／owner，不要求 controller 理解業務語意。 |
| [AC-O28 功能驗收與業務成果分開](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md:169) | Workflow／人工契約 | 文件驗收待具體化 | 功能驗收與業務成果分開合理；需文件樣本，不需新增產品 gate。 |

## Gates：逐項核對

| AC／原情境 | 建議歸屬 | 驗法評估 | 理由與最小補強 |
| --- | --- | --- | --- |
| [AC-G01 正常交付](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:17) | 保留核心行為 | 主要情境明列 | 三 gates 合取與新鮮版本是核心；V8＋R3 主要成功路徑合理，尚未實跑。 |
| [AC-G02 單一 gate 失敗](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:21) | 保留核心行為 | 驗法部分／缺情境 | 必須補 review clean/CI fail 與 review fail/CI green 兩個獨立矩陣案例；V8 目前只有發布與 push。 |
| [AC-G03 Review 執行成功但無法裁決](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:25) | 保留核心行為 | 主要情境明列 | task succeeded 不等於品質 clean；V6 已明列 blocked→unknown、不得開修正輪。 |
| [AC-G04 摘要與證據不一致](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:33) | 保留核心行為 | 主要情境明列 | 逐項 raw/exit/digest/snapshot/producer 核對必要；V5＋design 已列主要污染情境。 |
| [AC-G05 驗證與程式分離引用](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:37) | 保留核心行為 | 驗法部分／缺情境 | 合理地避免文件 SHA 自我引用；V5 未驗 evidence 外置、文件後補 commit 的適用性。 |
| [AC-G06 不同 SHA 的有效 Red 與 Green](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:45) | 保留核心行為 | 主要情境明列 | 原始 Red 早於 head、目前 Green 合理；正常不 replay 與矛盾診斷路徑已明列。 |
| [AC-G07 缺歷史或錯誤的 Red](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:49) | 保留核心行為 | 主要情境明列 | 缺歷史／錯誤 Red 不接受；V5 明列 replay 不能補造原始 Red。 |
| [AC-G08 整合回歸失敗](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:53) | 保留核心行為 | 主要情境明列 | 單一 worktree 仍須 head regression；V5 的 pre_review_g1 修正路由合理。 |
| [AC-G09 純文件 N/A 通過](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:61) | 保留核心行為 | 驗法部分／缺情境 | N/A eligibility 合理；應補正向 eligibility→G1，但 G2/G3 未自動通過的案例。 |
| [AC-G10 行為變更或待核對的 N/A](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:65) | 保留核心行為 | 驗法部分／缺情境 | T3.1 只寫獨立 eligibility，需明列 self/pending/rejected/錯 model／行為設定等負例。 |
| [AC-G11 有效獨立 review](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:73) | 保留核心行為 | 主要情境明列 | V6 已補 full diff/current/clean/獨立身份，正式 R1 能力仍未執行。 |
| [AC-G12 局部 review 或隔離無法證明](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:77) | 保留核心行為 | 主要情境明列 | V6＋R1 權限負例方向合理；clone 及異模型本身不算隔離證明。 |
| [AC-G13 非成功 check 與空集合](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:85) | 保留核心行為 | 矛盾或錯配 | D49 允許特定 repo 的人工政策，但 design 寫「403 或政策 unknown→Blocked」；須改成沒有適用政策才 Blocked，並補 required 全狀態矩陣。 |
| [AC-G14 舊成功不能蓋過新 attempt](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:89) | 保留核心行為 | 驗法部分／缺情境 | 目前只驗 observation 順序；還須同 check 舊 success／新 pending、不同 app、分頁與最新 attempt 選擇。 |
| [AC-G15 衍生整合 snapshot](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:93) | 改寫／下移細節 | 矛盾或錯配 | 原 AC 保留可驗證 integration SHA 映射；新版一律要求 check/head/tested SHA 相等。須明定首片 head-only 並延期映射，或補映射支援，不能宣稱現測項已覆蓋。 |
| [AC-G16 舊結果晚到](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:101) | 保留核心行為 | 主要情境明列 | 跨 purpose 的版本順序與晚到結果案例已明列，屬必要判定。 |
| [AC-G17 Base 或規格改變](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:105) | 保留核心行為 | 驗法部分／缺情境 | V7 主要只測 head；需 head 不變時 base/spec/AC/plan/skill/controller 版本改變的失效／批准案例。 |
| [AC-G18 Pass 前後發生 push](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:109) | 保留核心行為 | 主要情境明列 | 發布後新觀察、Pass 前後 push 失效已明列，不需全域 transaction。 |
| [AC-G19 模擬通過但 adapter 缺證據](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:117) | 驗收證據規則 | 文件驗收待具體化 | 這是驗收報告誠實性要求；需按 profile 區分 probe、權限、E2E 證據，不是多一個產品 gate。 |
| [AC-G20 真實 review 沒有 finding](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md:121) | 驗收證據規則 | 主要情境明列 | 沒有 finding 不捏造，demo 缺覆蓋就維持 open；R3 已正確區分安全 Blocked 與成功展示。 |

## Durability／runtime：逐項核對

| AC／原情境 | 建議歸屬 | 驗法評估 | 理由與最小補強 |
| --- | --- | --- | --- |
| [AC-D01 直接檢視狀態](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:17) | 保留核心行為 | 驗法部分／缺情境 | 可讀狀態必要；V2 沒有斷言使用者可見 gate 原因／blocker／下一步，R3 human status 仍只是候選。 |
| [AC-D02 手動修改不是決策](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:21) | 保留核心行為 | 主要情境明列 | 可信本機前提下偵測可核對手改合理，V2 有負例；不擴張為惡意同 UID 防偽。 |
| [AC-D03 兩個 run 搶同一 feature](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:29) | 保留核心行為 | 主要情境明列 | 同 feature 只有一個 owner／budget 必要；V2 同時 claim/commit 有主要反例。 |
| [AC-D04 Worker 狀態 unknown](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:33) | 保留核心行為 | 驗法部分／缺情境 | V4 不派競爭 writer 正確；design 的「idle」需限定權威 runtime 完成／停止證據，不能退回 terminal idle 即可接手。 |
| [AC-D05 結果未符合派工](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:41) | 保留核心行為 | 主要情境明列 | V4＋design 有身份、cwd/head/scope 拒收並保留原件。 |
| [AC-D06 只有原生 assistant message](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:45) | 保留核心行為 | 驗法部分／缺情境 | R2 仍走一般 fixture result；需 native-message-only 且通知缺失的擷取／來源保存案例。 |
| [AC-D07 結果存在但通知遺失](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:53) | 保留核心行為 | 驗法部分／缺情境 | V4 的重複／unknown 寫入不能代替漏通知後發現已保存結果；缺公開接續入口的案例。 |
| [AC-D08 重複與衝突結果](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:57) | 保留核心行為 | 主要情境明列 | T2.3 有相同結果去重及衝突保留／Blocked，方向合理。 |
| [AC-D09 State 提交前後 crash](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:65) | 保留核心行為 | 驗法部分／缺情境 | V2 的「中斷不重複」太籠統；要分提交前／已提交後並驗完整舊或新版及不丟已確認 state。 |
| [AC-D10 歷史尚未完成](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:69) | 改寫／下移細節 | 驗法部分／缺情境 | 持久一致的目的合理；候選改為 history-first 寫入順序，這是設計／回歸約束，可與 D09 共驗，不必成通用產品承諾。 |
| [AC-D11 無法信任的 state](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:73) | 保留核心行為 | 驗法部分／缺情境 | 應明列 missing/malformed/unknown schema/conflict、不清 budget 且零派工；V2 目前主要只有手改。 |
| [AC-D12 發文成功但回應遺失](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:81) | 保留核心行為 | 驗法部分／缺情境 | V8 只列未知不重貼；要驗 GitHub 已接受但 receipt 遺失後查回原 URL、單次內容且不重 review。 |
| [AC-D13 Unknown 無法安全重試](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:85) | 保留核心行為 | 主要情境明列 | V4 包含 delayed effect/not_found 不足以重試及零重送，必要且合理。 |
| [AC-D14 Controller restart](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:93) | 保留核心行為 | 驗法部分／缺情境 | V9 是預算停止，不是恢復完成 worker＋既存 review＋pending issue 發布；R3 一次中斷也未指定此狀態。 |
| [AC-D15 恢復時版本已改](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:97) | 保留核心行為 | 驗法部分／缺情境 | 版本失效本身有 V7；需 resume 入口組合案例，確認不沿用 acceptance／不重新初始化。 |
| [AC-D16 Infra retry 用盡](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:107) | 保留核心行為 | 驗法部分／缺情境 | 寫入 attempts/readback 有上限，但純 fetch 只寫每次呼叫三次；需耗盡→Blocked 且新 seq/session 不洗掉同一失敗預算。 |
| [AC-D17 Active budget 到限與恢復](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:111) | 保留核心行為 | 主要情境明列 | D47 線上停止／離線保守核算合理；V9 有主要反例，R1 單次 stop 不能單獨驗本 AC。 |
| [AC-D18 正確 workspace 與設定](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:119) | 保留核心行為 | 主要情境明列 | V4 身份比對＋R1 native model/marker/workspace；仍只是計畫，H0 不替代正式 profile。 |
| [AC-D19 能力缺口與替換](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:123) | 保留核心行為 | 主要情境明列 | 能力不足就 Blocked、不默換 runtime 合理；V1/R1 有基本判斷。 |
| [AC-D20 僅有 OpenCode 的部署](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:127) | 後續能力 | 延期未覆蓋 | 公司 OpenCode-only 需求合理，D50 首片延期且未驗收；保留 future owner，不要求首片打造全平台。 |
| [AC-D21 Runtime 身份不取代共用身份](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:131) | 保留核心行為 | 驗法部分／缺情境 | 共用 identity 與外部 handles 分欄必要；需兩種 native handle 的 round-trip，不只一般 result 身份拒收。 |
| [AC-D22 兩種接法分別驗證](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:135) | 驗收證據規則 | 文件驗收待具體化 | 不同接法分別報告合理；既有 H0 報告有示例，尚無正式 profiles 驗收，不能共用 passed。 |
| [AC-D23 未選用的接入故障](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:139) | 改寫／下移細節 | 矛盾或錯配 | 要求未選接入失敗不阻斷合理；現文綁 OpenCode 單獨部署，V1 缺 profile 測試不等價。首片改成已選兩路中未選選配故障／明列 OpenCode-only 延期。 |
| [AC-D24 同一 runtime 的不同角色與模型](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md:143) | 後續能力 | 矛盾或錯配 | 同 OpenCode 的雙角色配置不是首片 Claude Code Implementer＋OpenCode Reviewer；R1 無法證明該情境，應延期或增加專屬 profile，勿標 S1 已規劃覆蓋。 |

## Findings：逐項核對

| AC／原情境 | 建議歸屬 | 驗法評估 | 理由與最小補強 |
| --- | --- | --- | --- |
| [AC-F01 分類 review 意見](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:17) | 保留核心行為 | 驗法部分／缺情境 | blocking 與 severity 分離必要；V6 缺 AC bug vs 命名偏好的分類對照。 |
| [AC-F02 保持 identity](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:21) | 保留核心行為 | 驗法部分／缺情境 | stable ID 必要；需同問題移行仍同 ID、同位置不同問題不得合併，不能只寫 matches。 |
| [AC-F03 修正尚未覆核](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:29) | 保留核心行為 | 主要情境明列 | T5.1 明列 GitHub resolved 不代表 closure；Implementer 不可自解 blocker。 |
| [AC-F04 有證據解除](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:33) | 保留核心行為 | 驗法部分／缺情境 | 需要 closure actor/version/evidence 的完整正反例；V6 的 clean 不等於已測 closure 授權。 |
| [AC-F05 CI 先失敗仍收齊 review](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:41) | 保留核心行為 | 主要情境明列 | T5.1 同版本收齊再開 batch，文件缺陷可修、policy unknown 不開輪，主要規則合理。 |
| [AC-F06 完整回應批次](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:45) | 保留核心行為 | 驗法部分／缺情境 | V6 未列 batch 兩 finding 只回一項的拒收；要回報 missing IDs、保留全部阻擋。 |
| [AC-F07 三輪已用完](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:49) | 保留核心行為 | 主要情境明列 | V6 第四輪零派工與 V9 保留 budget 為必要案例。 |
| [AC-F08 Reviewer 接受反證](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:57) | 保留核心行為 | 驗法部分／缺情境 | 一次反證只是上限；缺接受反證解除條件與不多計一輪的正向案例。 |
| [AC-F09 爭議仍在或重送](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:61) | 保留核心行為 | 驗法部分／缺情境 | 缺反證不被接受／restart 重送不再派第二次覆核的組合案例。 |
| [AC-F10 反證伴隨新 head](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:65) | 保留核心行為 | 驗法部分／缺情境 | 缺 dispute 同時新 head→先 G1→最新 review/CI，不得拿舊反證免新 gate 的案例。 |
| [AC-F11 首次驗收退回](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:73) | 保留核心行為 | 驗法部分／缺情境 | V8 acceptance 綁定不等於 pending 驗收時人工退回；缺 source=human_acceptance、同預算、失效 Pass 的案例。 |
| [AC-F12 新需求或規格錯誤](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:77) | Workflow／人工契約 | 文件驗收待具體化 | 新需求／spec 錯誤回 Project Lead 合理；Blocked 是第一步，還需交接影響及裁決紀錄。 |
| [AC-F13 完整 review 與摘要](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:85) | 保留核心行為 | 驗法部分／缺情境 | 發布順序有 V8，但需 read-back 核对完整 review、issue 動作摘要、同 result/head/finding IDs 與連結。 |
| [AC-F14 發文失敗](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:89) | 保留核心行為 | 驗法部分／缺情境 | unknown 不重貼有測項；還缺已保存 review 不重跑，只恢復失敗的那一處發布。 |
| [AC-F15 連續修正仍留下同一 blocker](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:97) | 保留核心行為 | 主要情境明列 | T5.1 定義 recurrence 與上限，V6 有提前 Blocked；實作時須驗重送不計數。 |
| [AC-F16 已解除的 blocker 再次出現](/Users/johnson.chiang/workspace/loop-engineering/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md:101) | 保留核心行為 | 主要情境明列 | reopen→Blocked 有主要案例；是否同語意問題由 reviewer 證據支援，與 F02 共驗。 |
