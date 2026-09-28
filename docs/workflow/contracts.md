# Workflow 執行與交接契約 v1

> **2026-09-27 範圍更新（D41／D42）**：已確認改為 orchestrate 呼叫薄 controller，完整成品包含多人 Project／Feature 流程及 cross-node-file-transfer 多 feature 示範。見 [Project intent](../project-intent.md)。本文涉及 controller 自動派工、全面恢復及平台責任的舊設計待逐項對照，不能直接據此續派；三 gates、證據／版本及 finding 覆核仍保留。

> **2026-09-28 更新（D54／D55）**：Spec 的位置與回流採 OpenSpec（D54）。Project 層改由 project-lead skill 承擔，orchestrate 只跑單一 feature loop，控制方向由 Project Lead 往下（D55，修訂 D17、D28）。直接相關的段落已更新；其他舊敘述若與此衝突，以本註記與 D54、D55 為準。

日期：2026-09-26。配套 [workflow-design.md](overview.md) 的實作提案；欄位／enum 名稱尚未成為已實作 API。已確認語意以 [decisions.md](../decisions.md) 為準，包含 D24–D28 的 finding、TDD、相依 feature 與 Retro 政策；timeout 等未決實作預設另標示。

## 文件 binding 與控制權

每份 artifact reference 至少保存 role、provider、locator、revision、content digest 與可讀 snapshot；issue 內文另存 issue identity、採用的 body 與觀察時間。Project / feature 規格衝突時回人，不依最新 mtime 或工具名字自動勝出。

建議 `workflow.yaml` 是 repo 的可版控政策，`.delivery/project.json` 保存 project binding、roadmap refs、feature run 指標與人工接受紀錄；feature gate 的唯一現行判定在 `.delivery/runs/<run-id>/run.json`。Project 只引用 run ID/revision，不再複製一份可獨立改動的 gate。

Runtime results、logs、native receipts 與 secrets 不自動進入 Git。Skill／設定範例可版控；可分享的證據另行保存不含敏感資料的副本。Credential 沿用 runtime 與 GitHub 的認證方式，不寫進 assignment、Markdown 或 YAML。

控制鎖不只鎖 run ID：啟動時以 repo + feature identity 防止同一 feature 用兩個 run IDs 重複控制，並取得實際 worktree writer lease。同時持有 project registry lock 的時間只涵蓋登記／交接；長任務使用 run lock。跨檔恢復先 reconcile run，再更新 project 指標，不要求 project snapshot 和 run snapshot 多檔原子提交。

依 D23，Project Lead 負責專案協調、Implementer 負責功能交付，透過 spec／AC、依賴與成果交接。Project Lead 提出優先順序或委派意圖時，須附使用者授權來源及適用範圍；Implementer 在已核准的 scope／design 內作實作決策，超出範圍的問題交回裁決。Controller 核對授權、核准 plan、scope、版本、依賴與預算後實際派發，維持 feature 的唯一派工權。共同入口或 runtime 父子關係不能作為決策授權證據；角色授權不取代 D11 人工決策或 G2 獨立性。

依 D32，Project Lead → Implementer 的準備交接包含適用 project baseline、研究來源／重要未知、feature spec／AC、high-level design／必要限制、依賴與已決定／待決事項。Implementer 繼續研究，交回 detailed design 與最終 plan／tasks；Project Lead 提出的工作包或 tasks 保留為草案，經 Implementer 校準才成為可執行計畫。文件 producer 與角色責任分開記錄；不因任務草案已存在就視為已取得 D11 開工確認。更新 plan 時保留 revision，controller 依核准邊界核對，不能把草案直接當 assignment。

依 D34，[SA 階段交接](project-lead-sa.md#完成確認與交接) 另辨識 project／feature 層級、所屬 milestone、上游 baseline、穩定需求／AC IDs、來源文件版本、readiness 理由與適用使用者確認；未決項帶影響、是否阻擋、處理階段及下一位 owner。確認可進入 Design 不代表已取得 D11 開工確認。沿用既有確認前核對版本及適用性；具體 JSON／YAML 欄位在實作設計決定，文件存在或七章填滿不能由 controller 自動判 SA 已確認。

依 D30，assignment/result 的角色與品質語意不綁特定 runtime 或 model；adapter 將核准的執行設定映射至原生 API／CLI，再保存原生 identity、結果與能力證據。Runtime 與 model 是分開的設定，不從角色名推定；是否滿足既有 G2 Codex 要求，仍依後續選定的 runtime/model 政策驗證。Adapter 不可自行改 gate、默默降低隔離或選用不符合核准限制的替代工具。

依 D37／D38，OpenCode 是預設 runtime，Orca、Codex／ChatGPT 相關入口及 Claude Code 是選配；公司與本機共用契約。Controller run/task/attempt identity 與原生 session/message/dispatch handles 分開，Orca 專有欄位不成為共用必填條件。角色 profile 分別保存入口／transport、runtime 名稱與版本、provider、requested model、實際回報 model 及能力證據；如 Orca 負責 transport，仍保存底層真正的 runtime。OpenCode 可承載不同 provider/model 的獨立角色 sessions；既有 Codex 審查要求依核准 reviewer model／隔離能力核對，不以 Codex CLI 或任意 OpenAI model 代替。Credentials 沿用已核准接入的認證機制，binding 只存引用，不存 credential 值。

Preflight 只要求所選 profile 的依賴；未選用的 Orca／Codex／Claude Code 缺失或斷線不阻斷 OpenCode。切換接入仍需明確設定、身份與隔離核對，不能因本機發現某工具就自動使用或默默 fallback。沒有可用 agent runtime 時，controller 仍可讀狀態及執行不依賴該 runtime 的核查；需要該 worker 的 action 明確 Blocked，不能補造成功。

Adopt 先唯讀查核：原 owner、workers、未提交內容、原生 SDD / patrol loop、版本及證據。已確認原 owner 交出派工權且沒有未知 writer，才建立 active lease。Timeout 或 runtime／接入服務不可查詢不是舊 writer 已停止的證據。

## Project 與 Feature 產出物

本節將 D04／D19／D32 的文件角色與交接具體化，供 project-lead、Project Lead、Implementer 與 Reviewer 共用。內容角色沿用已確認需求；下列路徑只是示例，完整預設 layout／schema 仍待設計收斂。產出物不等於固定檔案數，也不要求 project SA 時完成全部技術設計或未來 features 的詳細規格。

### Project baseline

| 產出物角色 | 內容與範圍 | 準備者／主要讀取時機 | 檔案與整合原則 |
| --- | --- | --- | --- |
| Repo 清單 | 產品的 root repo 與各服務 repo：名稱、URL、預設 branch、本機路徑、用途 | Project Lead 維護；所有角色開工前先同步 | root 的 `repos.yaml`，由同步指令拉進 `repos/`；單一 repo 的產品省略（D61） |
| Mission／intent | 目標對象、問題、改善方向、範圍與非目標、業務成功條件；尚未實作的跨 feature 共用限制（列出並指向輸入） | Project Lead 與使用者；project intake、feature 選擇及 Replanning | 沿用如本 repo 的 `docs/project-intent.md`；`mission.md` 是可選名稱 |
| Domain language／領域分析 | 核心概念、標準用語、語意區別與適用領域；領域規則與情境由適用 Spec 承載 | Project Lead 維護；所有角色在相關領域工作前讀取 | Matt domain-modeling 的 `CONTEXT.md` 保留原名與 glossary 職責；跨 context 才按需建立多份 CONTEXT 與 Context Map。複雜關係可在適用 Spec 引用模型圖，不強制另建 `domain-model.md` |
| 需求輸入 | 人或上游提供、尚未承諾要做的需求；匯入專案時的上游 spec | Project Lead 整理並記錄來源版本；feature SA 從中挑出本次要做的需求 | 保留原檔，或依能力拆分並保存「原章節 → 能力」對照與來源版本；不放進 `openspec/specs/`（D58） |
| Project spec | 系統目前已實作並被接受的行為，包含已成立的跨 feature 共用限制 | 由 archive 寫入；feature SA、design 與 review 讀取 | 依 D54、D58 為 `openspec/specs/<能力>/spec.md`，一個能力一份；只由人工接受並 merge 後的 archive 寫入，新專案開始時為空。共用限制由第一個讓它成立的 feature 以 ADDED 帶入，之後以 MODIFIED 擴充；mission／tech 不代替它 |
| Architecture／tech | 主要元件責任、資料流、對外契約、技術棧、工程限制與重要取捨 | Project Lead 高層設計；Implementer detailed design、Reviewer 檢查設計邊界 | `tech.md`、既有 system design 與適用 ADR 可共同承載；不要求全部複製到單檔 |
| Roadmap／milestones | 可展示的成果節點、完成條件、feature 候選、優先順序與依賴；只有 milestone 與 feature 兩層，細節看穩定度（見 [SA 指引](project-lead-sa.md#roadmap-怎麼規劃)） | Project Lead 與使用者；選 feature、檢查 milestone、驗收後 Replanning | 保留實際 roadmap 路徑；project repo 路徑引用 binding；分開記 Pass／accepted／merged，不以各 PR 綠燈代替跨 feature 成果驗證 |
| 工程與驗證基準 | 適用工程規則、可重現 setup／build／test、必要 CI checks、相關環境與限制 | Project Lead 查明，Phase 0／Implementer 建立所需能力；規劃、實作與 review 使用 | 引用 AGENTS／CLAUDE、工程文件及實際 scripts／CI；只保存必要入口與理由，不複製易過期的工具設定 |
| Research／重要決策 | 現況證據、假設與限制、決策理由、尚未解決問題 | Project Lead／相關分析者；按當前決策與改動領域讀取 | Research、Spec 的待決段及必要 ADR 各自保存對應內容；不把研究結論全塞進 CONTEXT，也不要求每個回答建立 ADR |

Domain model 是對領域的理解，可涉及概念、關係、規則與邊界；`CONTEXT.md` 是其中可共用的語言入口，不是完整需求或實作模型。沿 D19 保留工具原生檔名，讓角色透過 binding 找到它；我們的 convention 規範責任、引用及版本，不為統一外觀更名成另一套 glossary。若既有 repo 使用不同詞彙表路徑，優先指向既有權威，再明示適配 skill 的讀取位置，不維護兩份定義。

### Feature requirements／design／plan／validation

使用者引用的 SDD 三種產出物已由既有文件角色涵蓋；我們另保留 design，內容與執行證據分開：

| SDD 產出物 | 本流程對應 | 最小內容與負責人 | 檔名／狀態 |
| --- | --- | --- | --- |
| requirements | Feature spec／AC | A4 由 Project Lead 或 Engineer 帶 `feature-to-spec` 定義行為、scope、依賴、重要例外、限制及可驗收結果，Project Lead 確認（D64、D66）；引用 project intent、高層設計與 roadmap 的版本 | 依 D54 以 change 的 specs delta 承載行為與 AC，ticket 只保存摘要與引用；proposal 承載動機、範圍、「不做」與待決；由執行 `feature-to-spec` 的人（Project Lead 或 Engineer）帶 Agent 寫，Project Lead 確認，不放 design。不再複製 requirements.md |
| 原三檔未獨立列出 | Design | Project Lead 提供必要高層邊界，Implementer 完成 detailed design／介面／失敗恢復／測試策略 | 可共用一份 design 或引用既有適用設計，標明責任與版本 |
| plan | Implementation plan／tasks | Implementer 校準 task groups、順序／依賴、scope、AC 對應、具體步驟與完成驗法；Project Lead 可提草案 | 保留 OpenSpec tasks 或選定方法的原生路徑，唯一可派工計畫；草案與 checkbox 不代表開工批准。依 D57，每個 task 一個 session 做得完、不開 ticket；commit 以 task 為單位且各自綠燈；每個 task 完成後由獨立 Reviewer 做局部 review，不取代 G2 |
| validation | AC 驗證對照＋實際 evidence references | SA 定義可觀察通過條件；Implementer 在 design／plan 階段補方法、環境、通過標準、證據位置，執行後填結果；Reviewer 核查有效性 | 可用既有 validation 文件或 plan 中明確區段；不宣稱它是 OpenSpec 原生必有 artifact。實際 gate 結論由 controller state 保存 |

Validation 最小對照為 AC ID → 驗證方法／步驟 → 必要環境 → 通過標準 → 預期證據位置；執行後補結果、實際證據與適用版本。方法可含自動化測試、curl 或 UI／人工檢查，按 AC 選擇；成功標準需可判定，不強制每項數值化。業務改善與功能符合要求分開記錄；人工 UI 檢查不代替適用 TDD／CI，檢查清單勾選也不取代三 gates 的證據。

目前內容與交接契約已涵蓋；D40 的 proposal／specs／design／tasks／validation、S1 程式與歷史驗證證據均已存在。D41／D42 收斂後的正式修訂、Herdr 接合與完整 E2E 尚未完成；[範圍對照](../harness/scope-reconciliation.md) 是修訂輸入。文件存在、歷史測試通過、新設計核准與實際交付驗收是不同狀態。

### 角色交接摘要

| 交接 | 接收者至少要拿到 |
| --- | --- |
| Project Lead → feature loop（交接包） | Change ID 與檔案版本、每個受影響 repo 的 base branch 與 commit，以及預定要開的 PR（D61）、SA 確認（同一人兼任時註明併入開工確認，D59）、project baseline 引用、spec／AC、設計邊界、依賴與 base branch、未決問題與下一位 owner、開工與驗收的決策者（驗收人預設是 Project Lead，需求由別人提出時是那個人，D62） |
| Implementer → 開工確認 | Detailed design、最終 tasks、scope、AC 驗法、必要環境、風險與執行限制 |
| Orchestrate → 執行角色 | Run／task／attempt、角色、worktree／branch、允許範圍、文件版本、base／head、驗收與結果位置 |
| Implementer → Reviewer | Spec／design、完整 PR 與 review base／head、實作證據及尚未覆核 findings |
| Reviewer → 修正循環 | 穩定 finding ID、問題與依據、blocking 與否、預期行為、適用版本；後續修正及覆核證據 |
| Feature loop → 人／Project Lead | PR Pass 驗收包或 Blocked 原因、AC 結果與限制；每個受影響 repo 的 PR、base／head commit、CI 與 review 連結（D61）；worktree、run ID（手動階段寫執行的人）、已用的修正輪數 |

### 手動階段的紀錄位置（D60）

| 紀錄 | 產生的 skill | 位置 |
| --- | --- | --- |
| SA 確認 | Project：project-lead；Feature：feature-to-spec（D66） | Feature：proposal 的確認段；Project：決策紀錄 |
| 交接包 | feature-to-spec（D66） | ticket 留言；ticket 本文的「交接包」連到它 |
| 開工確認 | spec-to-plan（D69） | ticket 留言 |
| 局部 review 結果 | plan-to-code（D69） | ticket 留言，每個 task 一則 |
| PR Pass 驗收包 | to-pr（D69） | ticket 留言，連到 PR |
| 接受或退回 | project-lead | ticket 留言 |
| Retro 候選 | project-lead | ticket 留言 |

每則留言寫明誰、何時、原話或結果、適用版本與連結。ticket 本文的狀態、下一步與驗收勾選，由寫對應紀錄的 skill 一併更新（D67）。寫到 GitHub 需要授權；controller 可用後是否改由它保存另議。薄 controller 第一片已把開工決定與接受紀錄定在 `$LOOPCTL_HOME/features/<id>/feature.json`，PR Pass 驗收包由它產生（[D45-04 design](../design-candidate/d45-04/design.md)）；用它時以狀態檔為準，ticket 留言是摘要。

### 共用入口與版本交接

project-lead（依 D55）保存／引用 project artifact index，feature 保存自己採用的 baseline references；沿用本文件既有 binding 欄位，不另建第二份內容權威。路徑可先由 README 導覽與既有交接記錄承載，機器 index 的 JSON／YAML 形式在 implementation design 定案。

每次 project resume、feature 準備／start 或 reviewer handoff，先讀適用指令與 artifact index，再載入 mission、domain、project spec 及與本次相關的設計／工程約束；選下一個 feature 時讀 roadmap，讀研究與 ADR 則依當前範圍。每項採用內容固定實際位置、版本、來源與決策狀態，必讀來源缺失／衝突時顯示原因，不靠聊天記憶補造。

新 baseline 經明確決策更新後，保留既有版本並評估對活躍 features、spec／plan 及 gate evidence 的影響，不只讓所有 run 改讀最新版。下一個 feature 引用核對後的 baseline；文件名不同可映射，需求衝突或適用性未確認不可只靠路徑映射解決。

## 狀態分開保存

| 維度 | 建議值／內容 |
| --- | --- |
| Feature phase | intake、planning、awaiting_approval、implementing、validating、checking、correcting、ready_for_acceptance、blocked；任何 phase 都可因明確原因進入 blocked |
| Task execution | pending、running、succeeded、failed、blocked、unknown |
| Gate | missing、pending、passed、failed、stale、unknown |
| Review verdict | clean、changes_required、blocked |
| Publication | pending、publishing、published、failed、outcome_unknown |
| Human acceptance | pending、accepted、returned；帶 code/spec/design 版本 |
| Integration | observed branch/base/PR facts，包括 GitHub merged 事實；不是由 agent 宣稱 |

例：review task `succeeded` + verdict `changes_required` → G2 `failed`；verdict `blocked` → G2 `unknown`、feature phase `blocked`，交人工裁決或等待外部條件恢復，不據此新開 correction batch 或增加修正輪次，既有已計輪次保留。發文 `failed` 不清掉完成的 review。Reviewer 尚未完成、CI fail 時先收集診斷，除明確中止／timeout 路徑外，仍等待同版本 review 結果再整批派修。

## 派工與結果

| 交接物 | 必要內容 |
| --- | --- |
| Assignment | schema_version、run/task/attempt IDs、role、runtime 名稱／版本與原生 IDs、核准角色 profile（入口／transport、runtime、provider/model 各自的身份與限制）、repo/worktree/branch、issue/PR、versions、allowed scope/tools、dependencies、AC IDs、skill refs/digests、結果與證據位置、timeout/budget |
| Result | 相同 IDs、execution status、實際 cwd/head/base/artifact versions、摘要、evidence refs/digests、findings、待決事項；品質 verdict 與執行狀態分開 |
| Evidence | task/AC/attempt、目的、command/env、start/end time、exit code、raw output ref/digest、source snapshot/tree、與修正或整合版本的關係 |
| Finding | stable ID、source、severity/blocking、位置、問題/依據/預期、狀態、fix commits、覆核 evidence、人工裁決（若有） |
| Human decision | 指定問題/版本、actor、明確選擇與理由、來源、時間、採用後影響；不能把沉默或 timeout 當批准 |
| Operation | ID、目標、payload digest、pending/outcome、idempotency marker、native request / receipt 與 read-back |

Worker 只能交自己的結果，不能直接改 run/gates/findings authority。結果先完整寫入並 atomic rename，再通知；controller 驗證 ID、snapshot、digest 與實際 evidence 後匯入一次。同一 attempt 的不同結果 bytes 視為衝突，保留原件並 Blocked，不能最後一份覆蓋。Implementer 與 Reviewer 不直接傳訊、不互相呼叫；交接通知僅帶 result ID/path 喚醒 controller，不承載權威 finding、verdict 或回應內容。

Runtime 只以原生 assistant messages 回傳結果時，由 adapter 保存原文、寫成 result；producer 記 adapter identity、原生 session/message IDs 與來源 digest。這是 runtime 結果捕捉，不是 agent 對等傳訊；只寫入 JSON 不證明內容正確。

測試 runner / adapter 捕捉命令、環境、source snapshot、exit code 與原始輸出，保存 producer identity；agent 的摘要只作說明。Controller 驗證 evidence 的存在、內容 hash、producer、task/版本關係與必要結果；語意上的失敗是否對應 AC 由 Reviewer 核查。既有 feature 匯入的手寫測試摘要要與可讀取原始紀錄區分，不能因符合 JSON schema 就升格成可信執行證據。

最終程式 commit 的 SHA 不適合用來自我引用其自身 tracked 驗收檔：runner 的 result 綁定實際 snapshot，文件指向該結果。之後只有文件改動也須記錄差異與適用評估；不要為追更新自我 SHA 而無限產生 docs commits。

## TDD 與非行為變更

歷史 Red 應留下測試存在而對應行為尚未實作／修正時的 source snapshot、命令與失敗原因。無關的語法／環境錯誤不是有效行為 Red。Green 與 refactor 證據保留 lineage；最終整合 regression 綁定現在 head。

各 task 在隔離 worktree 的成功不直接推出整合成功；controller 保留 task commit → integration commit 的對應，再對整合版本跑必要測試。缺歷史 Red 時如實記 missing，不把 retroactively replay 的紅測試冒充原始 test-first 紀錄。

依 D26，方法採 Superpowers TDD。純文件／註解可附理由、diff 分類與必要文檔檢查申請 N/A，由獨立 Reviewer 確認並保存適用版本／例外規則與證據；設定/migration/test code 依實際行為判定。Implementer 只可提出 N/A，不能自我豁免。

Controller 先派獨立 Reviewer 做 N/A eligibility 檢查，核對真實 diff、行為影響與適用檢查；結果只決定該範圍是否免除 TDD Red/Green 要求，不免除必要驗證、G2 或 G3。再完成整體 G1，之後才正式 G2；eligibility 不是 G2 clean，避免循環等待。待確認時 G1 未決，拒絕時依原因補實作／證據或 Blocked，不默認接受。

## Gate 評估與版本失效

版本集合包含 repo、PR head、實際 base ref/tip、review merge-base（多 repo 的 Feature 依 D61 逐 repo 各記一組：G1、G3 逐 repo 判定，G2 對整組 PR 判定，PR Pass 以 Feature 為單位；任一 PR 版本改變，整組的 G2 與 PR Pass 都要重評）、project/feature specs、design/plan/policy digests，以及執行的 skill/controller 版本。差異按來源語意評估，不只對 branch 名稱或檔名。

| 變更 | 必要動作 |
| --- | --- |
| 新 head（包含整合與修正） | 重新取得現在版本的 G1 最終驗證、G2 結論、G3 checks；歷史 Red 保留 lineage |
| Base / merge-base 改變 | 重新建立完整 diff、review 與整合風險；CI 是否需重跑依 check 的適用性契約判斷 |
| Spec / design / AC 改變 | 保留人工裁決與新版本，更新驗法並重評 G1；Reviewer 讀新契約；同 head 的 CI 能否沿用須有適用理由 |
| Plan / skill / policy 改變 | 核對 scope、先前執行方法及證據能否成立；不能只改判定規則來消除現有 blocker |

Required checks 由 repo policy 明示並核對可讀取的 GitHub 設定，空集合不自動成功。每項核對 name/context、來源（app/provider）、實際 source SHA、head/base 對應、attempt 時序、status/conclusion 與 URL；取回完整分頁，舊成功不能蓋過目前 pending/failed attempt。同名未知來源不能冒充 required check。

若檢查綁定的是衍生 integration snapshot，adapter 必須提供可核對的 head/base 關係與接受規則；不能只比名稱或因不是 head 字串就盲目接受/拒絕。不能確認對應時記 unknown。

Final Pass 前重新讀 head/base 與適用 artifacts。觀察不一致時放棄該次 Pass 轉移、reconcile；保存 Pass 的版本與觀察時間，不宣稱跨 GitHub 多次讀取具全域 transaction。後來有 push 就失效當前 Pass，保留歷史結論。失效後，需重評 G1 的版本回 `validating`；G1 有明確沿用理由而 G2/G3 需重查時回 `checking`，派出或查回最新適用結果。Scope/spec/design 變更需 D11 確認時，先回 `planning` / `awaiting_approval`。Human acceptance 保留原版本歷史，新版本重新成為 `pending`，不能將舊 accepted 移植到新版本。

## Finding、修正輪次與發布

依 D24，finding 狀態的唯一權威是本機 JSON registry，納入 run state，由 controller 單一 writer 更新。PR 與 issue 是可讀發布紀錄；GitHub 討論匯入為帶來源、actor、版本與時間的證據／裁決，經 controller 核對 D09 後才更新狀態。關閉 GitHub thread 或 Implementer 宣稱修好均不自動解除 blocking。

每個 checking 版本收齊 review/CI 後產生唯一 correction batch ID，相關 findings、CI failures、scope、AC、驗法與依賴全部明列。Batch 開始派修才增加 correction round，不能依每個 finding／subagent／CI job 計一次，也不能把 code fix 包裝成 infra retry 逃避上限。修正 result 必須對 batch 內每個 finding 回 `fix_submitted`（commit/evidence）或 `disputed`（依據/可重現結果）；缺項視為 result 不完整，不可據此解除 finding。若需改 scope/spec，task 回 `blocked` 並依 D11 交人，保存未完成項目。

依 D25，`disputed` 反證由 controller 送獨立 Reviewer 覆核一次；沿用 finding ID、原 correction batch 與版本，持久化 counter-evidence result ID、覆核 assignment/result IDs 和已使用次數。重啟、重複結果、換 session 或新措辭不得重置同一爭議的次數。未改 code 時針對同一版本覆核；有新 head 時先取得適用 G1，再與必要的最新版本 review 合併。這次釐清不另開 batch、不增加 correction round；基礎設施失敗仍按 D13 的操作重試上限處理。Reviewer 接受反證時附依據更新 finding；仍有 blocking 爭議則 Blocked 交人，不自動進行第二次。範圍／規格／AC 或設計變更直接沿 D11 回人，不以一次覆核取代人工決策。

人工驗收退回既有 AC 缺陷時沿用同一 run 與三輪上限；以被退回的交付版本為基準，不要求此前已 accepted。Controller 保存 `source=human_acceptance`、回饋 actor/來源/時間、版本與可重現差異；若是既有 finding 就沿用 ID，否則配置一次新的 stable ID，重複回饋以來源 identity 去重。退回使當前 Pass 失效，對受影響 gate 記錄原因並重評；先核對剩餘 correction 預算，再組 batch 派修，到限轉 Blocked。解除阻擋仍遵守 D09。

已確認最多三輪 correction；同一 finding 重複出現或修正明顯擴大 scope 時先提出原因與裁決需求，不能無限重抽 reviewer。Infra 操作各最多兩次額外重試；診斷出是程式或測試錯誤就回 correction 流程。

依 D24，Reviewer 結果先保存，再由 publication adapter 將完整 review 發到 PR；原 issue 發可採取行動的摘要與 PR review 連結。每份紀錄帶 run/review/result ID、head/base/spec 版本與 finding IDs，可對回原文。GitHub 上使用 comment 或 review 不影響獨立性的定義，也不以帳號是否可按 approve 作 clean 證據。

發文先保存 outbox operation 與可查 marker，再寫入並 read-back。回應 unknown 時先依原 marker 查是否已存在；查不到且無法確認安全重試就 Blocked，而不是重貼。發文失敗只重試該操作，不重做 review；重複通知只喚醒 reconcile。

## Project 收尾與相依 feature

依 D27，相依 feature 開始實作前，controller 核對上游指定版本已有人工接受紀錄、GitHub 已 merge，且本次採用的 baseline 包含所依賴成果；不以舊 accepted 或 merged 標記替代版本核對。等待時可準備 spec/design；條件不足就保留等待原因，不派依賴它的實作工作。Merge 仍依 D03 由人處理。

依 D28，人工接受事件觸發一次 Retro 候選整理，輸入接受的 feature／版本、交付與 review/CI 證據及人工回饋。以 acceptance identity 與版本持久化 operation/result 去重；重啟或重複事件不重複產出。Project Lead 彙整有依據的改善候選與必要 Replanning 建議，落地仍按 scope／決策權限。這是 project 收尾，不新增 PR gate；P03 提前試用仍依 D22 等使用者開始。

## 恢復、預算與環境

採 [file-state.md](../harness/history/file-state.md) 的單一 writer、atomic snapshot、pending event 與不覆寫 evidence 策略。Resume 的順序是載入 state → 檢查 ownership → 讀 workers / PR / artifacts / results / outbox → 重評版本 → 接續最小必要工作。恢復不是把所有 tasks 標 pending 再跑。

已確認 active time 上限 4h；建議計算至少一個 worker、CI wait 或 controller 交付操作在執行的 wall-clock 聯集，不因並行重複計時。等待使用者的時間暫停 active clock，但已派出的 worker 仍需計時。Crash 期間記錄 unknown interval，保守計入直到 external timestamps 證明可扣除；restart 不把累計歸零。超時後停止新派工，處理仍存活 workers，再保存 Blocked。

Worker / review / CI 的 45 / 30 / 30 min 為未核准 timeout 預設。達限先查狀態，只有確認已停止或已安全解除執行權，才可重派；明確人工增加 budget 保存裁決，不能靠新 run ID 規避。

Runtime preflight 核對安裝版本、工具權限、正確 repo/workspace/branch、登入可用性及結果通道，不輸出 credentials。既有 probes 未證明 Codex native completion、reviewer 全工具隔離或新 repo placement 成功；不能以 console idle、`input_accepted` 或設定檔存在推論成功。

## Skills 交接契約

依 D55（修訂 D17），Project 層與 Retro 由 `project-lead` skill 承擔，feature 準備依 D66 由 `feature-to-spec` 承擔，單一 feature 的交付依 D69 由 `spec-to-plan`、`plan-to-code`、`to-pr` 依序承擔，`orchestrate` 可用後把三者串起來；每一步只需一個入口。控制方向往下：project-lead 選 feature，feature-to-spec 交出交接包，內圈 skills 不回頭呼叫它們，也不另起競爭的外層 loop。

| 分支 | Trigger / input | 方法與工具範圍 | 輸出／完成／Blocked |
| --- | --- | --- | --- |
| Project／`project-lead` | Start project；mission、repo、既有成果 | Research → SA／domain／grill／high-level design 可迭代；research-codebase、grill-with-docs、grilling、domain-modeling 按實際可用版本使用 | 有來源的分析、baseline、roadmap／milestones 與 feature 候選；重要歧義明列，不擅自選 scope |
| Feature preparation／`feature-to-spec`（D66） | 選定 feature；project intent、高層設計、roadmap、相關 code/docs/issues | 在 root 的 `feature/<id>` branch（D67）聚焦 research／SA／grill 與必要高層設計，依 D54 寫 OpenSpec proposal 與 spec delta，`openspec validate` 檢查格式；依授權開 root repo 的 ticket 並維持薄格式 | 唯一 spec／AC、設計邊界、依賴、研究來源及決策；交接包；重要未知不得藏入假設 |
| Design / plan／Implementer | Feature spec／AC、高層設計、baseline、repo、deps、可選 tasks 草案 | 研究實作與測試接縫，完成 detailed design；Writing Plans／OpenSpec tasks 的整合為 Q-METHOD 候選 | 校準後唯一 plan、task IDs／DAG、scope、task→AC、介面、Red/Green 步驟、驗法與文件更新；交一次 design+plan 確認 |
| Implement / fix | 已授權 assignment；task或finding batch | Superpowers TDD、review-response / debugging；只寫指定隔離 scope | Code/commit、實際 evidence、結構化 result、逐 finding 的 fix_submitted／disputed 回應；缺依賴或 scope 不符回 Blocked |
| N/A eligibility | G1 前的純文件／註解 N/A 申請；理由、diff、適用檢查 | Controller 派獨立 Reviewer 核對實際行為影響；唯讀審查與隔離驗證 | 版本化接受／拒絕與證據；資訊不足回 Blocked，不產生 G2 clean |
| Review | G1 通過、版本固定；spec/design/AC、完整 diff、舊 findings、經 controller 匯入的 disputed 依據（依 D25 一次覆核） | 由 controller 派出獨立 Codex session，按需讀 repo 規範與 context；隔離驗證 | Verdict/findings/verification refs；不寫作者分支、不自行更新 gate |
| Adopt / resume | Existing feature 或 run ID | 讀外部實況、ownership、state/results；確定性核對由 helper | 保存真正缺口與唯一 next action；未知 writer 不重派 |
| 收尾與 Retro／`project-lead` | Retro：人工接受後，或使用者明確指定 feature；archive：人工接受且 merge 已核實後；證據與回饋 | 接受後明示整合 Matt 方法與必要 research，只產出 Retro 候選；merge 核實後以 OpenSpec archive 併回 project spec | 有依據時選 1–3 項 evidence→改善→owner→驗法；資料不足列限制，無改善不造待辦 |

Matt to-spec、to-tickets、retro 的 user-only 呼叫限制必須保留。D28（依 D55 修訂）由 project-lead 在人工接受後產出 Retro 候選，採明示整合方法的 reference，註明來源、版本與相對原版的觸發／交接差異；不在背景呼叫原版 user-only skill，也不暗中移除其限制。候選不自動成為規範或實作授權。

D31 的方法組合已重新開放評估（Q-METHOD）。若採 Writing Plans 方法銜接 OpenSpec tasks，需明示任務格式、scope、依賴、介面、測試與自檢的映射，保留唯一 plan 權威；其預設檔案路徑可調整，不代表 execution handoff 已自動相容。原版要求的 subagent-driven-development／executing-plans 交棒若改由 controller 承接，必須記錄差異，不能聲稱原封不動執行原 skill。局部 task reviews 不擁有全 feature Pass 權；Matt 方法也不得以技能名稱隱式切換 TDD 或派工權。選型完成後固定套件與引用內容版本，後續更新用新版本啟動 run。

## 驗收情境如何落地

| 情境 | 應驗證的可觀察結果 |
| --- | --- |
| 正常／review finding／CI fail／review fail | 只有三 gates 同版本通過才 Pass；修正保留 finding ID 和新版本覆核 |
| 缺 Red／無效測試／未核准 N/A | G1 明列缺失或待裁決，不以最終綠燈補造過程 |
| 舊 SHA 結果晚到／Pass 前 push／base 或 spec 改變 | 不放行舊結果，保存歷史並重評目前版本 |
| 必要 check missing / pending / cancelled / timed-out / failed / unknown / stale | 一律不通過，逐項顯示原因；policy 不能將這些狀態豁免成成功 |
| 必要 check skipped / neutral | 只有明確且適用的 policy 允許才可接受；未設定或未核准例外時不通過 |
| 通知丟失／重複／只接受輸入 | Result reconcile 恢復，不因通知判成功或重派 |
| 發文失敗／回應未知 | 保留 review，按 operation marker 查回並安全重試，避免重貼 |
| Worker crash／controller restart／兩個 run 搶一個 feature | 保留執行權證據、去重匯入、拒絕競爭 writer |
| 到限／爭議／人工退回／新增需求 | 有證據的 Blocked 或明確路由，無自動擴張 scope |
| PR Pass 尚未 merged／accepted 後又 push | Project 不把能力當 main 已有；接受與 Pass 都帶版本 |
| 純文件 N/A／行為設定變更 | 獨立 eligibility 先於 G1；適用 N/A 不免除必要驗證或 G2/G3，設定變更不一律豁免 |
| 同一 blocker disputed／重啟再送反證 | 只覆核一次、不另計 correction round；仍有爭議→Blocked，重啟不重置次數 |
| 上游 accepted 但未 merge／等待相依 feature | 可準備 spec/design，不派相依實作；接受、merge 與 baseline 均可核對才放行 |
| 重複人工接受事件／Retro 候選 | 依接受版本去重整理，不自動改規範或 code、不隱式呼叫原版 user-only skill |
| P03 Retro／下一 feature | 先界定真實已完成階段；改善有落地驗證，不宣稱已完成尚未執行的 E2E |

核心先用 fake adapters 驗證難以穩定製造的故障；真實 runtime/GitHub 接入與 finding→fix→re-review 分開留證據。實作 tests 應驗行為，不只核對 enum 或重述實作步驟。
