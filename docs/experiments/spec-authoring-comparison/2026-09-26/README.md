# OpenSpec 與 Matt to-spec：同題規格比較

日期：2026-09-26。對象：Orca Delivery Loop MVP。**兩份都是比較草稿，沒有成為正式開工契約。** 使用者已確認的工具組合見 D31；此次沒有更改選擇或啟動 P03。

## 先看兩份產物

- [OpenSpec 版：proposal](openspec-candidate/openspec/changes/implement-delivery-loop/proposal.md)。四份 capability specs：[流程與交接](openspec-candidate/openspec/changes/implement-delivery-loop/specs/delivery-orchestration/spec.md)、[三 gates](openspec-candidate/openspec/changes/implement-delivery-loop/specs/delivery-gates/spec.md)、[finding／修正](openspec-candidate/openspec/changes/implement-delivery-loop/specs/finding-resolution/spec.md)、[持久化／恢復](openspec-candidate/openspec/changes/implement-delivery-loop/specs/durable-delivery/spec.md)。
- [Matt to-spec 版：單份 spec](matt-candidate/spec.md)。原生七節、40 個 user stories、40 個 AC，另含決策、提案與驗證映射。
- [共同輸入](shared-input.md)、[比較方法與限制](comparison-context.md)、[生成前檢核表](comparison-checklist.md)。

## 本次結果

**兩份都保留了三 gates、歷史 Red／當前 Green、版本失效、獨立 review、持久化與人工裁決等核心要求。主要差異在組織與交接方式；沒有根據可以宣稱某個工具普遍產生更好的 spec。**

我會繼續讓 OpenSpec 承擔正式可版本化的 feature 契約，同時吸收 Matt 版的「AC → 驗法 → 預期證據」對照與清楚分隔的決策／提案區。這是合併有用內容到同一份權威，不同時維護兩套會各自漂移的 spec。

| 面向 | 本次 OpenSpec 版 | 本次 Matt 版 | 實際影響 |
| --- | --- | --- | --- |
| 讀者入口 | 短 proposal，依四個 capability 分別讀條文 | 單檔由問題、方案、user stories 一路讀到 testing | Matt 適合連續審讀；OpenSpec 適合只看某項能力，但需在檔案間導航 |
| AC 表達 | 每條 SHALL requirement 配一至多個 WHEN/THEN scenario，各有 AC ID | 每個 story 附一段給定情境及結果的 AC；一段常含多個分支 | OpenSpec 已切出較細的回歸案例；Matt AC 落到 tests 時要再拆分分支 |
| 驗證交接 | Scenarios 有預期結果，但沒有逐 AC 的驗法／evidence 對照表 | Testing Decisions 已按 AC 群組對應操作與應保存 evidence | Matt 這版的驗證交接更直接；正式 OpenSpec 應補上這個映射 |
| 已確認 vs 提案 | Requirement/source 注記及 Purpose 區分；細部提案仍寫成候選 SHALL 契約 | Implementation Decisions 明分已確認 ID-M 與提案 IP-M，Testing seam 另標 pending | Matt 更容易一眼辨認決策狀態；OpenSpec 採用前需逐條確認提案部分 |
| 修改定位 | 例如 CI 適用性集中於 GAT-06、GAT-07 | 同一主題可能出現在 AC、Implementation Decisions 及 Testing Decisions | OpenSpec 對單項規則的改動定位較方便；Matt 修訂需同步多處，避免 drift |
| 可派工性 | 未生成 design/tasks | 未執行 to-tickets，沒有任務計畫 | 本輪兩者都不是可直接開工的 implementation plan，不能以此判一方不完整 |
| 長度 | 跨 proposal 與四份 specs；不是讀一個小檔就讀完整功能 | 雖為單檔，40 stories＋AC＋決策＋testing 也很長 | 單檔不代表輕量、多檔也不代表較完整；原始數量見下方產物統計 |

## 三個具體對照

1. **歷史 Red 與現在 head 不同。** OpenSpec 的 AC-G06 專門寫「R 的 Red 可以與 H 的 Green 組合，只要 lineage 可追」；Matt AC-M14 同樣完整保留這點，但同段還包含無效 Red、子 task 成功不等於 G1 等情境。內容一致，OpenSpec 較容易直接拆成獨立回歸測試。
2. **發文成功、回應遺失。** OpenSpec AC-D12/AC-D13 分開已找回與無法安全重試；Matt AC-M31 在一項 AC 內涵蓋兩種結果，Testing Decisions 再明列觀察副作用次數與 read-back。兩者都有關鍵故障語意；Matt 的驗證欄位值得沿用。
3. **上游 accepted 但未 merge。** OpenSpec AC-O12 與 Matt AC-M08 都明定只可準備 spec/design，不派相依實作。這不是 OpenSpec 或 to-spec 自帶的治理規則，而是兩者正確保留同一份來源的 D27。

## 主 agent 查出的待修內容

保留兩份生成稿原文，以下修訂建議獨立記錄；尚未回填成修正版或宣稱已核准。

- **R01／兩版共同：重複 finding 的提前升級路徑不夠明確。** 來源 workflow-contracts 明定同一 finding 重複出現或 scope 明顯擴大時要提出原因及裁決需求。兩版都有三輪上限、stable ID 與 disputed 一次覆核，但未明確寫出「修正後同一問題反覆出現」如何觸發診斷／Blocked／人工裁決。它不等同 Implementer 主動 disputed。正式稿應新增一個可觀察情境，並在 design 確認何謂反覆及計數方式，不能默認一直修到第三輪才處理。
- **R02／Matt：另一 repo 的規則混入『已確認』政策。** Testing Decisions 把 production hooks、sleep/retry、flaky exclusions 等列為已確認原則。作者已確認它們來自本 session 注入的 gigaxfer AGENTS 指示，並非共同產品來源或 to-spec 條文；詳見 [作者 provenance 補記](matt-candidate/author-notes.md#審校後-provenance-補記繼承的-agents-規則)。規則可能合理，仍須確認適用於 Orca 或改標提案。正式 orchestrate 交接應明列目標 repo 與規則適用範圍，避免把工作環境指示誤寫為產品決策。這是本次生成／context 管理發現，不證明 Matt skill 普遍較差。
- **R03／OpenSpec：AC 到具體驗法的映射尚待補。** ORC-03 正確要求未來 features 的 AC 有驗法，但這份 controller 規格本身只給 scenarios 和整體驗證方向。進 design/plan 時應為本稿每組 AC 補上驗證操作／環境／證據對應，可直接借鏡 Matt Testing Decisions；兩版尚未確認的 seam 仍保留待決。

Runtime/model、45/30/30 timeout、active-time 計法、required checks 與 trial target 都被兩版列為未決；這是正確保留未決狀態，不能當成工具遺漏。它們仍須在具體 design/plan 和開工確認前依影響收斂。

## 核心需求覆蓋定位

以下 18 組均能在兩稿找到相應條件與可觀察結果；這是閱讀審核，不是測試通過。Matt 的 M 編號指 AC-M，IP 指提案。R01–R03 為上述額外內容审校，不以找到關鍵字當作零缺陷。

| 檢核 | 需求 | OpenSpec 定位 | Matt 定位 |
| --- | --- | --- | --- |
| C01 | 入口／同層角色／唯一 controller | ORC-01 | M01、M05、M37 |
| C02 | 交付單位、AC、原生文件交接 | ORC-02、ORC-03 | M02–M04、M12 |
| C03 | D11 人工邊界與交付終點 | ORC-03、ORC-05 | M06–M07、M34 |
| C04 | Adopt 與試用暫停 | ORC-04、AC-O15 | M09–M10、M40 |
| C05 | 三 gates 順序及結果維度 | GAT-01 | M17、M21–M22、M33 |
| C06 | 歷史 Red／當前整合 Green | GAT-02、GAT-03 | M10、M13–M14 |
| C07 | N/A eligibility 先於 G1 | GAT-04 | M15 |
| C08 | 獨立 Reviewer／作者 branch 保護 | GAT-05 | M16–M17 |
| C09 | 必要 CI 身份／attempt／非成功 | GAT-06 | M18–M19 |
| C10 | 版本失效／Pass 前重查 | GAT-07、AC-O11 | M20–M21、M34 |
| C11 | Finding authority／closure／dispute | FIN-01、FIN-02、FIN-04 | M23–M25 |
| C12 | 合併批次／三輪／重試／4h | FIN-03、DUR-08 | M22、M26–M27 |
| C13 | 先保存後發布／unknown／去重 | FIN-06、DUR-06 | M30–M31 |
| C14 | Assignment/result/evidence 身份及衝突 | GAT-02、DUR-03、DUR-04 | M13、M29、IP-M04 |
| C15 | Restart／ownership／corrupt state | DUR-02、DUR-05、DUR-07 | M11、M28–M32 |
| C16 | Accepted／merged／Retro | ORC-06、ORC-07 | M08、M35–M36 |
| C17 | 未決選型不冒充已決定 | 各 Purpose、DUR-08、DUR-09、author notes | Implementation Decisions 提案區、Further Notes |
| C18 | Fake 與真實 E2E 分開 | GAT-08 | M39、Testing Decisions |

## 驗證與產物狀態

| 產物 | 本次數量 | 文件驗證 |
| --- | --- | --- |
| OpenSpec | 5 份：proposal＋4 specs；31 requirements／69 scenarios；467 行，41,625 UTF-8 bytes | 作者與主 agent 各跑一次 strict validate，通過；status 只有 proposal/specs done，design/tasks 未完成 |
| Matt | 1 份 spec；40 user stories／40 AC；253 行，39,786 UTF-8 bytes | 原生七節、US/AC 唯一且連續、無程式片段／實作路徑；來源混入另列 R02 |

數量只描述這批文件，不是 coverage 分數、token 成本或速度。Matt 一個 AC 含多個情境，不能拿 40 與 69 直接比較完整度。產品測試與 E2E 都沒有執行；結構驗證不會檢查政策正確性。

原始作者紀錄：[OpenSpec](openspec-candidate/author-notes.md)、[Matt](matt-candidate/author-notes.md)。原始檢查：[OpenSpec strict validation](openspec-candidate/tool-records/validation.json)、[Matt 結構檢查](matt-candidate/validation-notes.json)。[逐檔來源雜湊](input-manifest.json)、[原始來源及 skill 快照](source-snapshot.tar.gz)、[方法紀錄](method.json)、[文件數量](metrics.json) 可供追溯。封存內的 `baseline/` 對應作者筆記中的共同來源路徑；工具原始輸出保留生成時 TMP 路徑，並非正式執行設定。

此處只保存比較稿。正式 `implement-delivery-loop` change 目前只有 scaffold，未將任一稿直接升格為批准內容；design、implementation plan 與 D11 確認仍待完成。PR trial／P03 Retro 維持暫停。

