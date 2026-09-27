# 給 Herdr session：完成 controller 的 Design＋Plan

日期：2026-09-28。這是一份可直接交給接手 agent 執行的任務指示。使用者已授權本輪設計、規劃及按需派 subagents；產品實作仍待具體 design＋plan 的 D11 確認。

## 任務與完成終點

你接手 Loop Engineering controller 的設計與實作規劃。由 **Opus 5.5 high** 擔任主設計者與協調者；困難的狀態／證據取捨可用 **xhigh**。先核對實際模型與 runtime 支援的 effort，再派工。

**沿用 D45-04 revision-14 收斂，不從頭重寫。** 完成可供人一次確認、確認後即可派工的 design＋plan＋validation，包括具體執行預設、AC 驗法、任務依賴與模型配置，取得獨立文件覆核後交回使用者。尚未核准的選項清楚列出建議與影響。

此次終點是「設計與計畫可供 D11 確認」，不是 PR Pass。準備完整提案後才詢問 D11；D11 pending 不阻擋本輪研究與文件修訂。此次不執行 W1、產品實作、GitHub 寫入或 example 初始化。

## 先確認工作區與現況

| 位置 | 用途 |
| --- | --- |
| `/Users/johnson.chiang/workspace/loop-engineering` | 主 repo、決策、正式 OpenSpec 與交接紀錄 |
| `/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-04` | 現行候選：revision-14；不是另一份已核准規格 |
| `/Users/johnson.chiang/workspace/loop-engineering-thin` | 目前是普通目錄；W1 尚未把它接成 Git worktree |
| `/Users/johnson.chiang/workspace/gigaxfer` | 本次不修改、不接管；後續 example 才按流程引用適用需求 |

1. 讀取目標 repo 當下的 AGENTS.md／CLAUDE.md（若有），核對 cwd、Git status、HEAD、worktree 與正在使用的 session。原工作區有尚未提交的文件變更，按現況保留。
2. 本輪交接前主 repo HEAD 為 `4ce111011fde83c3a2784402cea111e52a954b3c`，origin 為 `yschiang/loop-engineering`；自行重查，不將這個快照視為永久事實。
3. 核對候選 `publication-manifest.json` 的發布 hashes。它已確認的 review 只適用該快照；後续修訂需要新覆核。
4. 先回報五行以內的接件摘要：工作區、採用版本、主模型／effort、這輪目標與真正阻擋事項，接著繼續工作。

## 閱讀順序與文件權威

先讀：

1. [Project intent](../project-intent.md)、[Decisions](../decisions.md)，特別是 D11、D19、D26、D27、D41–D52。
2. [目前 handoff](2026-09-27-controller-design.md) 最上方 checkpoint；後面的內容是歷史。
3. [候選入口](../../../loop-engineering-thin/docs/design-candidate/d45-04/README.md)，以及其中的 `design.md`、`tasks.md`、`validation.md`、`spec-delta.md`、`coverage.md`、`cleanup-map.md`。
4. [最終文件覆核](../../../loop-engineering-thin/docs/design-candidate/d45-04/review.md)及[修正紀錄](../reviews/2026-09-28-opus-review-d45-04-resolution.md)。需要問題背景時才回查原 Opus review 與中間 revisions。

準備完整規格對照時再一起讀：

- 主 repo `openspec/changes/implement-delivery-loop/specs/` 下的四份正式 spec。
- [D45-02 baseline spec delta](../../../loop-engineering-thin/docs/design-candidate/d45-02/spec-delta.md)。交接時 SHA256：`7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565`。
- [D45-04 現行 spec delta](../../../loop-engineering-thin/docs/design-candidate/d45-04/spec-delta.md)。交接時 SHA256：`a0ca23c6abb7a833bb830d18943c51151d97248efa96080699f02ebe4c7f59d5`。

**目前規格的需求已足以進入這次設計收斂，但正式文件尚未完成採用。** 當前提案的完整語意是「正式 specs＋D45-02 基準＋D45-04 覆寫」，再核對已確認決策。單讀目前正式 specs 或單一 delta 都不完整；遇到來源衝突要列明，不自行猜答案。D11 後才依 T0.1 採用完整、自足的正式 specs。

原 16 項 Opus findings 及新增 R12-01／R12-02 已 verified；這是限定範圍文件覆核，不表示 88 AC 的驗法全部充分。88 AC 仍 planned，17 舊 S1 findings 仍 open。本輪新增的 D52 分工決策未包含在 revision-14 的覆核內，需納入新的設計／計畫一致性檢查。

## 已確認邊界

- 成品是 Project／Feature 兩層 workflow、開源 skills、orchestrate、薄 controller 與後續 cross-node-file-transfer example。首片集中於單一 feature 的交付，不先打造通用 agent 平台。
- Orchestrate 是唯一外層協調 loop；controller 以程式核對可讀 JSON／YAML 狀態、交接、版本、gates、findings 與允許的下一步；Herdr／runtime 提供執行能力。
- 保留 G1 原始 TDD＋目前 Green、G2 獨立 review、G3 必要 CI；全部綁定適用版本，unknown／過期／缺證據不能 Pass。Reviewer 或明確人工裁決才能解除 blocking finding。
- 一個 feature 的 writer 依序工作，Reviewer 使用獨立環境；review 與 CI 可並行。原始 Red 來自較早版本且可追溯，不能補造。
- D47–D49 的有界執行、可信本機與 repo-scoped CI 政策維持。產品預算仍為 4h active、最多 3 輪修正、每個 infra 操作額外重試 2 次；不因換模型／session 重置。
- D46 隔離重建：新程式與舊 `src/delivery` 分開。舊碼只按已核對的來源與行為選擇性重用，舊測試通過不算新證據。
- 首片終點 PR Pass／Ready for human acceptance；不自動 merge、close issue、release 或 deploy。
- 依賴 feature 仍遵循 D27：上游 accepted＋merged＋baseline 採用後才開始實作。Q-STACK、跨人展示方式及通用工具選型可保留後續；不阻擋本次 controller 規劃，也不宣稱已完成。

## Herdr 與模型派工

接收 session 被使用者稱為「herdr」；**先確認當前 Herdr session／pane 身分，不據此猜測 server 名稱或別人的 agent ID**。在 Herdr 管理的 pane 中讀取 `herdr --skill`，按已安裝版本的 CLI 查詢與操作；不在管理環境中時停止 Herdr 控制，仍可完成不依賴它的文件研究。不得偽造 `HERDR_ENV` 或接管不明 session。

若接收者目前不是 Opus 5.5，讓接收者只負責啟動／交接給 Opus lead，由 Opus 統一協調；不要兩個 lead 同時各跑外層 loop。主設計者要讀完整規格來源及所有子任務結果，親自整合。

本次設計與後續實作的派工預設如下；**這是模型配置，不是所有列都必須啟動 agent**：

| 工作 | 預設 model／effort | 派工條件與輸出 |
| --- | --- | --- |
| 主持 design＋plan、處理取捨、整合文件 | Opus 5.5 high；必要時 xhigh | 必要。維持唯一整合者與人工決策介面 |
| 任務依賴、介面對照、AC 驗法缺口 | GPT-6 Sol high | 有可獨立處理的範圍才派；回傳具體缺口／建議，不寫共同候選文件 |
| 路徑、CLI、技能版本等窄範圍查證 | 優先直接腳本；需要 agent 時 GPT-6 Luna medium 或 Sonnet 5 medium | 只查證事實，不裁決 gates、需求或設計 |
| 獨立 design＋plan 覆核 | GPT-6 Astra xhigh | 必要；fresh session、固定完整輸入、只寫 review 結果 |
| D11 後的產品程式實作／修正 | **預設 Opus 5.5 high**；困難 task 可 xhigh；適合時 GPT-6 Sol high 或 Astra high／xhigh | 本輪只提出配置，不開始寫產品碼 |
| D11 後的產品 PR review | **預設 GPT-6 Astra xhigh** | 必須與被審實作使用不同的實際模型，且為獨立 session |

模型選擇依 task 的複雜度與風險，不把全部工作固定交給最便宜或最高 effort。主模型 Opus 5.5 是使用者指定；無法使用時清楚回報，不默默替換。其他選項也要查核 runtime 上實際可用的 provider/model ID 與 effort；名稱不是能力證據。

**Review 的模型獨立性**：換 session、改 effort、改別名都不算換 model。預設 Opus 實作→Astra review；GPT 實作可由獨立 Opus review。若同一 PR 混用 Opus 與 Sol 實作，可保留未參與實作的 Astra 做完整 PR review。提前保留至少一個適合且未參與被審範圍寫作的 review model；Reviewer 不能改作者 branch 或自行修完再批准。對已修正 finding 的覆核仍由合格的獨立 Reviewer 完成。

Claude 模型沿用本機 Herdr→Claude Code；OpenAI 模型沿用 Herdr→OpenCode。不要把 Claude 訂閱改接 OpenCode。若特定 GPT model／effort 在目前接法不可用，先回報精確缺口與可行方案；不能把此環境限制寫成產品已支援其他接法。Controller 本身仍與模型解耦。本次 bootstrap 可選不同模型，不等於首版產品必須新增任意 runtime／角色互換能力。

子任務依賴滿足才派；查證可並行，共同文件維持單一 writer。建議 lead 加最多兩個活動 helper，避免為每份文件建立一個 agent。沒有獨立工作可做就依序完成。子 agent 不再派下一層外層 orchestrator。

## 工作順序

### 1. 核對 spec 是否足以完成規劃

把未決事項分成三類：會改變需求／AC 的阻擋；能由設計提出具體預設的選項；不影響首片的後續事項。能從 repo、CLI 或既有證據查明的自行查明。真正需要人的問題每輪最多 1–3 個，附建議與影響；其他工作繼續。

重點核對 D52 與候選 `tasks.md`、B1 的固定 Opus／GPT 措辭，以及產品 profile 與本次 bootstrap 分工的區別。列清楚需改的文件，保留當時 review 的效力範圍，不覆寫歷史報告。

完成條件：本輪要採用的來源版本明確；需求矛盾與設計選項分開；沒有把延期能力當作已完成或把候選當批准。

### 2. 完成最小可實作設計

沿現有 design 核對公開介面、狀態與結果契約、gate 適用性、finding 覆核、未知結果／停止／resume、Herdr 與 GitHub 邊界。優先移除不必要機制；確定性邏輯由程式處理，判斷與理解留給 agent。

把以下預設寫成具體提案，集中列入最後的 D11 確認包：

- 實作者／Reviewer 的 runtime、實際模型、effort、獨立性核對及替換條件。
- 必要 CI checks 的名稱、app／workflow、平台、驗證命令、tested SHA、skipped／neutral 政策與 `workflow.yaml`。現有 `unit-linux`、`unit-macos`、`static` 是候選，不是已批准集合。
- Worker／review／CI timeout、單次讀取／等待的界線與到限路徑。45／30／30 分鐘是既有候選，可論證沿用，不能寫成使用者已批准。
- W1 的隔離、來源保存與正式規格採用順序；確認沒有並行的現行 spec／plan 權威。

完成條件：每個設定有具體值或可核對的選定方式、理由與失敗路徑；無需下一位實作者再猜核心流程。維持 D50 精簡範圍，不因發現缺口自動增加常駐服務、安全平台、測試 registry 或通用排程框架。

### 3. 校準可派工 plan 與 AC 驗法

維護既有 `tasks.md`，不要另外再開一份平行 Writing Plans 計畫。每項 task 至少包含：scope／非 scope、owned paths、輸入輸出與相鄰介面、依賴、適合的 model／effort、AC／驗法、測試命令、完成條件與交接位置。

每個本片適用 AC 對到：可觀察行為、正例與關鍵反例、驗證環境、通過門檻、證據位置和 task owner。檢查測試是否真的會在行為錯誤時失敗，不以 ID 全有列出或檢查原始碼字串代替驗法。文件／workflow 用現有樣本與 rubric；後續能力保留 deferred。保留 88 AC 與 17 舊 findings 的 ID 及追溯，不維護逐測試登記平台。

依目前 tasks 的共用檔案表核對順序；有依賴的 writer 串行，final gates 針對整合後 PR。分清 bootstrap B1、能力 probes 與真正交付 T8：T8 需另選 B1 未做的新行為並經自己的 D11，且等待 B1 accepted＋merged＋baseline。

完成條件：每個派工單位可單獨交給 fresh-context agent；介面一致、無循環依賴，第一個 task 到實際 B1／T8 的路徑可執行。當前尚未實作的命令與測試只列 planned。

### 4. 獨立覆核及修正

固定 spec 來源、design、tasks、validation、coverage 與本輪新增決策，保存一份輸入 hash manifest，再交給未參與撰寫的 Astra xhigh session。審查需求一致性、可實作性、驗法充分性、過度設計與人機邊界。既有 18 項按修改影響核對，不盲目宣告前輪結論對所有新內容仍有效。

Review 結果需有穩定 finding ID、位置、問題／依據、預期修正、blocking 與否、適用輸入版本和 verdict。Opus 整理修正；Reviewer 覆核後才 verified。保存結果，再通知接收者；通知與 idle／done 都不是 review clean 的證據。Timeout 時先查原任務與保存結果，不因收不到通知就重複派工。

文件修正採有界循環；建議最多三輪，仍有需求／架構爭議則交回人並附決策摘要。這是本輪規劃執行的建議上限，不改產品的既有 correction 計數政策。

### 5. 交付一次可閱讀的 D11 確認包

更新現行候選與主 repo handoff，列出本輪真正修改、獨立 review 結果、必要待決值與下一步。提交給人的摘要先回答：首片能做什麼、如何驗收、採哪些具體預設、哪些留待後續。需要人批准的只有具體取捨和開工，不要求逐 task 簽核。

D11 之後才依 T0.1 組成完整正式 specs、獨立核對來源映射、保存基準 B 並執行 W1。此次只準備這段操作，不提前執行，也不把「可以開始 design＋plan」解讀成「批准產品實作」。

## Skills 與輸出位置

- [Writing-for-agents](/Users/johnson.chiang/.agents/skills/writing-for-agents/SKILL.md)：用於交接可讀性、明確步驟與完成條件。
- [Superpowers writing-plans 6.4.1](/Users/johnson.chiang/.claude/plugins/cache/claude-plugins-official/superpowers/6.4.1/skills/writing-plans/SKILL.md)：核對實際可用版本，沿用本候選已明示的適配方式（scope、owned paths、介面、相依、具體驗法；本輪不寫產品碼）。不另存重複 plan、不啟動其另一套外層 execution loop，也不宣稱逐條照原版執行。
- [OpenSpec update-change](/Users/johnson.chiang/.agents/skills/openspec-update-change/SKILL.md)：需要修訂正式 artifacts 時才依它及 repository 規則處理；本輪修改候選，正式採用留在 D11 後。查詢時依 CLI 實際回報的 artifact paths，別假設 schema。
- Superpowers TDD 仍為後續實作方法；現在規劃證據與行為案例，不生成假的 Red／Green。
- Research、domain、grill 按實際缺口選用；不重新訪談已確認的完整需求，不繞過 user-only skill 的觸發限制。

使用 `.delivery/herdr-design-plan-20260928/` 保存本輪 assignment／結果、固定輸入及候選修訂中間稿；它是工作紀錄，不是另一套正式規格。子任務寫自己的結果，由 Opus 整合候選共同文件。沿用已存在的格式即可，不為本輪另造派工框架。

派工至少記錄 task／attempt、角色、實際 model／effort、runtime／session、輸入版本、允許路徑、依賴、驗收與輸出位置。結果包含 execution status、所處理版本、摘要、證據／findings／待決項；把成功執行與 review clean 分開。模型記錄使用可觀察設定／metadata，不讀取私密 chain-of-thought。

最終更新同一個 D45-04 候選入口並增加明確 revision，保留 revision-14 與它的 review；不要建立一串新的平行 design 資料夾。更新 publication manifest，實際修訂需新的 review，狀態不能沿用舊 clean。正式採用後現行權威才轉回主 repo 的 OpenSpec 與採用文件。

最終回報：

1. Spec readiness：已清楚／阻擋／可延後，附具體理由。
2. Design＋plan 的入口與相對 revision-14 的重要變更。
3. 角色／模型／effort 分工及實際核對限制。
4. Review 輪次、verified／未解 findings 與適用版本。
5. 一次 D11 需確認的具體選項，以及批准後的第一個 task。

維持 workflow 使用者指南為預期流程草案；實作與 example 真實跑過後，再補可重現的完整操作步驟。
