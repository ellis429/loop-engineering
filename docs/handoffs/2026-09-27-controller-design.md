# Handoff：設計 Review 後接續 Controller 規劃

## 最新狀態：D40 已核准，準備 S1 core

D40 已記錄使用者對 v3 design/tasks/validation、技術預設、三個 feature PR 與 private `yschiang/orca-delivery` 的確認。遠端與本機 origin 已建立。正式 design、tasks 與 docs/validation 對照已採用；凍結候選與獨立 GPT 文件 review（DR-01–DR-10 verified）保留。S1 core 可開工；S2 adapters 與 S3 orchestrate/E2E 仍需上游 accepted＋merged＋baseline adopted（D27）。未自動 merge／close／release／deploy。

下一步：commit/push 文件基準，建立 S1 issue，建立隔離 clone 後派既有 `opus` session 實作 task groups 1–2，以 Superpowers TDD 留原始 Red/Green。協作者 bootstrap 派工，不宣稱產品 controller 已完成。G1 後取得獨立 GPT review 與真實 CI。尚無產品測試／PR Pass／E2E 證據。

以下是早期研究／派工歷史（截至 design-02），其待D11、未建遠端、未收件字樣已由本節與 D40 取代；不可用歷史限制阻擋已授權 S1。

日期：2026-09-27。這是 compact／新 session 的接續入口，不是產品派工 assignment 或開工批准。

## 本輪接續更新（D38／D39）

使用者要求依本 workflow 開發 controller，並進一步確認：**OpenCode 為預設 agent runtime，依角色選 OpenAI／Claude models；Orca、Codex／ChatGPT 相關入口及 Claude Code 都是選配。** D36 的 Opus 5.5 是模型指定，不是 Claude Code 必要依賴。Controller 本體仍是確定性程式，先完成 detailed design／plan 再依 D11 確認開工。

D39：本次 bootstrap 先由協作者協調 Opus 5.5 Implementer 與獨立 GPT／Codex Reviewer；產品 D38 不變，OpenCode 登入不是本次設計派工前置。前次 Claude Code 唯讀設計 intake 因本機 proxy 未監聽而失敗，沒有模型輸出，需確認可用 Opus 通道；見 [bootstrap 紀錄](../research/2026-09-27/controller-bootstrap.md)。本機 OpenCode 1.18.32 已安裝，無推論的 health／session／重啟讀回 probe 通過，模型推論及隔離尚未驗證；見 [安裝紀錄](../research/2026-09-27/opencode-setup.md)。GitHub owner/repo 仍待回答，未建立 ticket／PR。

以下原文件 review 結論只覆蓋當時固定快照；新增 D38／D39 的修訂經本輪一致性檢查，尚未重做獨立文件 review。OpenSpec design／tasks 仍缺，不將設計 intake 失敗或新決策當成開工批准。

## 現在做到哪裡

已更新整體 workflow、交接契約與正式 OpenSpec specs，完成兩個獨立文件 reviewer 的初審與覆核。Standards、Spec 各 1 項 finding，均指向 CI 狀態例外的文件歧義；修正後兩軸未解 blocking 均為 0。完整範圍、固定快照、原 finding 與覆核見 [review report](../reviews/2026-09-27-design-review.md)。

尚未建立此 change 的 `design.md`、`tasks.md` 與具體 AC validation 對照；尚未實作 controller／orchestrate，也沒有真實 E2E 證據。OpenSpec strict validate 只確認目前產物的結構。未 commit／push 本輪文件，未建立 GitHub ticket／PR 或初始化新專案。

## 工作範圍與閱讀順序

目標 repo：`/Users/johnson.chiang/workspace/orca-delivery`。原 session cwd 是 gigaxfer，但本工作只改 orca-delivery；勿將 gigaxfer 的 AGENTS 規則無條件當成此 repo 的已核准政策。接續時先查本 repo 是否新增工作規範，核對 working tree 與文件現況。

1. [Decisions](../decisions.md)：已確認 D01–D39、Q-METHOD／Q-RUNTIME／Q-PLATFORM；不要把候選當成定案。
2. [Harness 總覽](../delivery-harness-overview.md)、[Workflow Design](../workflow-design.md)、[執行契約](../workflow-contracts.md)：兩層流程、角色與交接。
3. [Project Lead SA](../project-lead-sa.md)、[檔案狀態](../file-state.md)：分析方法與持久化提案。
4. [OpenSpec proposal](../../openspec/changes/implement-delivery-loop/proposal.md) 及同 change 的 `specs/`：唯一正式 feature 規格；比較稿留在 experiments，不是另一套權威。
5. [本輪 review](../reviews/2026-09-27-design-review.md)、[planning preflight](../research/2026-09-27/planning-preflight.md) 與其引用研究：分清歷史 probe、現行能力與尚未實測。

## 已確認，不重新開題

- Project／Feature 兩層，共用 orchestrate 入口；Project Lead 研究、SA、domain、high-level design、roadmap／features／spec。Implementer 承接 detailed design 與最終 plan／tasks；Project Lead 可提任務草案。角色不綁固定 runtime 父子關係，決策權依使用者授權。
- 唯一 controller 管派工、狀態、證據／版本、三 gates、預算及恢復。Implementer／Reviewer 經已保存結果交接，不各開外層 loop；Reviewer 不修改被審 branch。
- JSON／YAML 人可讀持久化，不用 DB。G1 歷史 TDD＋目前整合 Green、G2 獨立 review、G3 真實 CI 都要成立；舊 SHA／缺證據／agent done 不放行。修正 3 輪、infra 各 2 次額外重試、4h active；counter 不因換 session／run 歸零。
- Controller 本次實作指定 **Opus 5.5**；核對明確 model ID 與實際執行身份，不默默替換。這不是未來所有 feature 的 model 規則，也不是讓 LLM 代替確定性 gate 判定。
- D38：OpenCode 是預設 runtime，依角色選模型；Orca／Codex／Claude Code 均選配。共用契約，能力與驗收各自查證；G2 的精確 reviewer model 與工具隔離尚待核對，不把 Codex CLI 作必要條件。
- 先完成並測通 orca-delivery harness／controller，**之後**才用新 workflow 從頭啟動 cross-node-file-transfer 作完整 Project＋Feature 驗證與操作練習。沿用 gigaxfer 適用的專案基準、來源版本及文件映射；新程式產生自己的 TDD／review／CI／驗收歷程。不為既有共識重做完整 grill，僅釐清新衝突。
- 現有 gigaxfer PR／P03 試用維持暫緩，不接管或修改該 repo。PR Pass 停在等待人工接受；merge／close issue／release／deploy 未包含在預設授權。
- SA 進入 Design 的確認和 D11 的具體 design＋plan 開工確認不同；已有適用確認可沿用。Compact 不補出缺少的批准。

## 未決與未查證

| 項目 | 目前狀態／下一步 |
| --- | --- |
| Q-METHOD | 原組合重新開放評估。候選是 Matt research／grill／domain 方法＋同一 OpenSpec change＋Writing Plans 方法細化唯一 tasks；工具觸發與交棒須明示適配。Superpowers TDD 的 D26 維持已定。問題已提出，尚無新回答 |
| Q-RUNTIME | D38 已確認 OpenCode 預設、其他接入選配；OpenCode 本機安裝與無推論 probe 已完成；待核對 provider/model IDs、既有 Codex 審查要求的 reviewer profile 與隔離能力，不再重問 Codex CLI 是否必要 |
| Q-PLATFORM | 已問公司初版 OS／部署範圍，尚無回答。本機 macOS 不證明 Linux／Windows 可用 |
| GitHub 目標 | 最近 `git remote -v` 無輸出；帳號唯讀查詢成功不等於具目標 repo／PR／checks 權限。後續確認 repository 與 feature 切片，再開或沿用 ticket；先可寫本地草稿 |
| Opus 5.5 | Claude Code 設計 intake 已嘗試但連線失敗，沒有實際模型回應；D39 先確認可用 Opus 派工通道。保留 D36 指定，不因所選 adapter 改變而換模型；不要求先完成 OpenCode 登入 |
| Runtime／隔離 | Orca 1.4.212、Claude Code 2.1.283 的 help 已讀；舊 probes 是 1.4.209 快照。本機已安裝 OpenCode 1.18.32；公司版本與接入待查。無推論 session 持久化已測，native 模型 completion、Reviewer 全工具隔離與 workspace placement 仍需實測 |
| 詳細設計 | Controller 語言／API／schemas、技能包裝、timeout／active-time／recurrence、required CI、平台與 adapter 驗收，需在 design／tasks／validation 定出可執行提案；未決預設不標為已批准 |

## 接續工作

1. 讀取以上文件與實際 git 狀態，保留既有修改；如內容與本 handoff 不同，核對差異，不以 snapshot 覆寫新工作。
2. 延續已提出的 1–3 題決策；可自行查的環境／repo／skills 資訊先查。需使用者答案的部分保持未決，其他設計可並進。
3. 完成正式 `design.md`、唯一 `tasks.md` 與 AC → 驗法／環境／通過標準／證據位置的對照。沿 OpenSpec 分步指令取得當前 instructions；採用的 skill 需讀實際版本並記錄適配，不另啟外層 loop。
4. Controller／adapters／orchestrate 是正式產品交付。規格／切片清楚後建立或沿用 GitHub feature issue；過大先拆可驗收 features，tasks 放各 feature plan。當前文件研究不必等 ticket，不能把本地草稿算已發布。
5. 具體 design＋plan 交 D11 確認後，才派指定 Opus 5.5 實作；首次 bootstrap 由目前協作者協調，獨立 Reviewer 與真實 CI 分開留證據，不能假裝由未完成的 controller 自動帶完。
6. 先用 fake adapters 驗核心與恢復，再保存真實 runtime／GitHub 接入與技能交接證據。測通後才啟動 cross-node-file-transfer；真實 finding → fix → re-review 若尚未發生，明列未覆蓋，不造 blocker 補展示。

## Compact 與權限

現在適合 compact 或開新 session：本輪文件 review 已收尾，下一階段有清楚入口。此文件只是保存交接，沒有自行清除 session；接續時仍須讀實際 artifacts。可用的接續句：

> 讀取 orca-delivery 的 `docs/handoffs/2026-09-27-controller-design.md`，接續詳細設計與 implementation plan；先處理其中未決事項，保留 D11 開工確認，暫不啟動 cross-node-file-transfer 或接管 gigaxfer。

原 session 的可寫 root 不含 orca-delivery，因此跨 repo 寫入曾使用有 digest 衝突檢查的已批准 helper；新 session 宜直接以 orca-delivery 作 workspace。不要因先前授權或此交接而繞過當前 filesystem sandbox。

## 已交接 opus session（design-02）

使用者指定 Orca workspace `opus`。已核對對應 Claude terminal 畫面為 Opus 5.5／xhigh，向該 terminal 發送限於設計草稿的 assignment；Orca receipt 顯示 `input_accepted` 與 `turn_started`，後續畫面已見讀取快照。這證明派工已開始，不是任務完成、actual inference model 最終核對或 gate 通過。

- 工作包與固定輸入：`/private/tmp/orca-controller-bootstrap-20260927/opus-session-design-02/`，含 assignment、input-manifest、prompt、dispatch-receipt。
- 輸出：同目錄 `outputs/` 下的 design.md、tasks.md、validation.md、result.json；目前待收件。
- Session 的原 cwd 是 gigaxfer；assignment 只允許寫上述 outputs，不修改任何產品 repo、全域設定或 GitHub。尚未授權產品實作。
- 使用者要求代答範圍內的例行 Y／proceed；協作者核對提示再處理，D11 的具體 design＋plan 開工確認仍保留。
- 收件後核對輸入版本與完整88個AC，再交獨立GPT reviewer；不可只憑 console 完成訊息放行。
