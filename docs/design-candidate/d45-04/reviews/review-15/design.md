# Design：薄 controller 第一個可用切片（候選 design-04，AC audit 修訂；revision-10）

> review-13 的 D51-R01–R07 已在 revision-10 提交修正；其中 R03／R05／R07 的殘留已在 revision-11 修正，待獨立覆核。本文件的歷史修訂紀錄見 revision-09／10／11。

> **狀態**：候選，不是 D11 核准，也不授權實作。以 outputs-03＋review-12 為基準，套用使用者已接受的 AC audit 修正（AC-A01–A05 與矩陣逐項建議）。本文是自足的現行候選。
> **政策**：D46–D50 已確認。仍待決定：CI check 集合的核准、reviewer 的精確 model、timeout 預設、W1、D11。
> **範圍（D50）**：薄的、可由 skill 呼叫的 controller；單一 writer；有界的觀察；可信本機協作。不復活平台機制。

## 1. 範圍與界線

- **第一片交付**：一個新 feature 從批准的 plan 出發，依序 TDD，經 G1 → push → 建立或核對唯一的 PR → 獨立 review＋CI → fix → re-review → PR Pass。
  - 附證據的 Blocked 是安全停止，不算示範完成。
  - 這個 feature 要等 bootstrap PR 已人工 accepted、實際 merge，且登記了 baseline 之後才開始（D27；不自動 merge）。在此之前的真實執行，只算隔離的能力 probe。
  - 這個 feature 必須是 B1 尚未實作的新行為，由 D11 選定（D51-R04）；本文不代為選擇。
- **組成**：
  - 一個 Implementer worktree，tasks 與 fix 依序在其中執行；
  - 一個獨立的 Reviewer clone＋session；
  - 最小的 orchestrate skill、`loopctl`、Herdr transport。
- **不變的部分**：
  - 三 gates，且 G1 先於正式 G2；
  - 原始 Red＋目前 Green；
  - 最新版本綁定；
  - finding 由 Reviewer 或人關閉；
  - 單一 feature 狀態／writer／預算；
  - D47–D49；
  - unknown 就停下並交人。
- **延後項目**（不算完成，未支援的入口一律回 `unsupported`）：
  - 能力：adopt（O08、O09）、Project Lead 委派（O18）、Retro op（O14）、OpenCode-only（D20）、同一個 OpenCode 承載兩個角色（D24）；
  - CI：G15 的非 head 整合 SHA 正向映射；
  - 基礎：平行 worktree、跨 feature 依賴自動化。
- **歷史限制**：O15（P03／Q-TARGET）只保留在 handoff，不寫產品特判。通用規則是：沒有明確的 `init` 或授權，就不接管任何工作。

## 2. 公開介面：`loopctl`

每次呼叫都是短命的：核對 → 更新 → 返回。

- stdout 是 JSON 物件，欄位為 `ok`、`revision`、`result`、`blocked`、`next`、`safety`。
- Exit code：0 成功、1 拒絕、2 用法錯誤、3 Blocked、4 not_owner、5 狀態不可信。

| 命令 | 效果 |
| --- | --- |
| `init --repo --repo-id --feature --issue` / `claim --actor` | 建立 feature（接受使用者直接交付，不要求經過 Project Lead；O01）；取得協調權，token 只存 digest |
| `status [--human]` / `next` | 唯讀：phase、各 gate 的狀態與原因、blockers、下一個允許動作與安全動作（D01） |
| `register plan\|binding\|policy` | 登記原生 artifact 的 locator、版本、digest。plan 還要記 producer 與校準來源 |
| `decide <kind>` | 記錄人工 decision。第一片支援：`approve_plan`、`revise`、`scope_change`、`accept`、`return`、`resolve_finding`、`waive_finding`、`reclassify_finding`、`resolve_operation`、`resolve_read`、`budget_extension`、`policy_change`、`handoff` |
| `write <op> --id` | 外部寫入（§4） |
| `observe pr\|ci\|worker\|native` | 唯讀的有界 fetch（§5） |
| `evidence red --command-id`（worker）/ `evidence green`（coordinator） | 只執行 policy 定義的命令 |
| `result import --attempt` / `assess` | 匯入結果；計算 gates 與 Pass |

- Orchestrate skill 只依 `next` 與 `safety` 行動。
- 角色、runtime 的父子關係、共同入口，都不會授予額外的決策權（O19）；只有 `claim` 取得的 token 與人工 decision 算數。

## 3. 狀態與持久化

- `$LOOPCTL_HOME/features/<id>/feature.json` 是唯一的現行狀態。
  - 最小欄位：`phase`、`owner`、`plan`、`approval`、`versions`、`attempts`、`writes`、`observations`、`read_budget`、`gates`、`findings`、`batches`、`budget`、`decisions`、`acceptance`、`blockers`。
  - 證據與 raw 輸出存成 content-addressed 物件；文件 digest 欄位不被當作物件引用。
- **對外承諾（D09、D10）**：
  - 已提交的狀態不會遺失，也不重複生效；
  - 中斷時尚未提交的變更不被接受；
  - 讀者只會看到完整的舊版或新版。
  - 實作採 history-first（先 write-once 寫入 `history/<rev>`，再原子替換現行檔）。這是設計與測試的細節，不是 spec 承諾。
- **不可信狀態（D11）**：缺檔、壞 JSON、未知 schema、手改、transition 衝突 → exit 5 或 Blocked；原件保留、不重建空狀態、不清預算，也不產生任何派工或寫入。

## 4. 外部寫入

有限的種類：`worktree_create`、`agent_start`、`prompt`、`stop`、`push`、`pr_ensure`、`publish_pr`、`publish_issue`。**沒有** merge、close、release、deploy（O10）。

- **狀態流程**：`prepared → in_flight → succeeded | failed(確定未送達) | unknown`。
- `write` 在同一程序內：consume 一次 → 呼叫固定 argv 一次 → 記錄 receipt。
- **重試**：只在兩種情況允許：
  - 已記錄確定未送達；
  - 有已驗證的原生冪等，例如 `push --force-with-lease`。以查詢結果判斷 PR 是否存在，**不算**冪等（D51-R01）。
  - not_found、client 已結束、Herdr socket 或 GitHub 的延遲生效，都不構成證明 → unknown 交人。
- **讀回**：只看既有的 write，不重發；每個 attempt 最多 3 次，每次都計入（包括「仍在執行」）。到上限 → `blocked(readback_exhausted)`。嘗試次數上限 3（D13）。
- **PR 正向路徑**（AC-A04）：
  - G1 passed 之後才 `write push`，再 `write pr_ensure`。
  - `pr_ensure` **建立之前**，先以 head branch 查詢 open 的 PR：
    - 0 個 → 建立一次；
    - 恰一個 → 沿用；
    - 多於一個 → Blocked。
  - 建立的結果 unknown 時，讀回：
    - 查到相符的 PR → succeeded，並沿用它；
    - 查無 → 仍然 unknown，Blocked，**不再建立第二次**（請求可能晚一點才生效）。
  - 記錄 PR identity：number、node id、url、head、base。
  - 正式 review 只在 PR identity 已記錄之後才派出。

## 5. 唯讀觀察與讀取失敗預算

- **順序**：
  - fetch 之前先在 lock 內持久化 `seq`，匯入時依 `seq` 排序；
  - 請求脈絡（purpose、請求時的版本）與觀察到的事實分開保存；
  - 共用版本事實（head、base、merge_base、binding digests）由 feature 層級的 `version_seq` 保護：只有 `seq > version_seq` 的觀察能更新，晚到的舊觀察不論 purpose 都不能恢復舊版本；
  - 各 purpose 的結果快取分開保存，只在觀察到的版本等於目前版本時才可用於 gate。
- **讀取失敗預算（AC-A05，D16）**：
  - 以穩定的邏輯鍵 `read_key` 計數，例如 `ci:<repo>:<head>`、`pr:<number>`、`worker:<attempt>`、`native:<attempt>`。
  - `read_budget[read_key].consecutive_failures` 持久化在 feature 狀態中，**不隨新的 seq、session 或 restart 重置**。
  - 傳輸失敗（timeout、5xx、連線錯誤）時加 1。只要有一次成功取得（即使內容是 pending）就歸 0。
  - 達到 3 次（初次＋2 次重試）→ `blocked(read_exhausted:<read_key>)`，`next` 與 `safety` 不再提供該讀取，也不會自動取得新的額度。
  - 人工恢復：`decide resolve_read <read_key>` 附上原因，授予**一次**新的 3 次額度。它不重置預算或其他計數，並留下紀錄。
- **Pending 輪詢**：成功取得但內容是 pending，不算失敗。以輪詢間隔、角色 timeout（候選 CI 30 分鐘）與 D47 active 預算為界；timeout 後依 D47 處理。

## 6. Runtime、writer 結束與獨立性

- **第一片的 profile**：
  - Implementer：Herdr＋Claude Code＋`claude-opus-5-5`；
  - Reviewer：Herdr＋OpenCode＋核准的 OpenAI model（待 D11）；
  - transport、runtime、provider、model 分欄保存。
- **未選用的接入（D23）**：Orca、Codex CLI、其他 profile 不在 preflight 範圍。即使它們缺失或故障，也不阻斷已選的兩條路徑，也不會被自動改用。
  - 這與「已選 profile 本身缺少或 unverified → Blocked」是兩回事。
  - OpenCode-only 部署的變體延到 S2。
- **同一 runtime 承載兩個角色（D24）**：延後。第一片 R1 的 profile 組合不能證明這個情境。
- **Capability preflight**（最早執行）：
  - 載入核准 skills 的正式 profile（不使用 safe-mode）；
  - 讀回 native model 與 marker；
  - 權限負例：寫出範圍、`git push`、`gh`、`herdr`、`loopctl decide` 都被拒；
  - stop 後以 process-info 確認停止。
  - 結果只綁定該版本與該 profile；未驗證 → Blocked。它不證明能抵抗同一 OS 帳號的偽造（D48）。
- **真實 writer 的前置**：worker 狀態讀取與 D47 stop／預算的 fake 情境都要先通過。
- **Writer 結束的判定（D04）**：必須有權威證據，**不能**只看 terminal idle、Herdr 的 `done` 或 `idle`。可接受的證據二選一：
  - 該 attempt 的結果已匯入，**且** native 紀錄顯示這次 attempt 的 turn 已完成（marker 之後有最終 assistant message，且沒有執行中的 tool call）；
  - stop 已經由 process-info 確認停止。

  未確認就不派下一個 attempt；unknown → Blocked。
- **Native-only 結果（D06）**：沒有結果檔、也沒有通知時，工具從 native transcript 擷取 marker 之後的最終結果，寫成 result，並記錄：
  - `producer=tool`；
  - native session 與 message IDs；
  - 原文的 digest。

  無法解析時是 unknown，不捏造結果。
- **Handle round-trip（D21）**：attempt 保存 `{herdr_session, pane, agent_name, native_session_id}`；Claude 的 native ID 是 uuid，OpenCode 是 `ses_…`。
  - result 以 attempt ID 對回；
  - native ID 不符 → 拒收；
  - 不為任何 runtime 補造 ID。
- **Reviewer**：使用獨立 clone，沒有寫作者 branch 的路徑。
- **拒收並保存原件**：身份、cwd、head、scope 不符；worker 提供的 argv；producer 不符；版本過期。

## 7. 證據與 G1

- 核准 plan 的**每一個** task 都要有原始 Red：raw、exit、task／attempt、snapshot、provenance 逐項核對。task 集合為空 → fail。
- **Red 的適用資格**（D51-R07）：以下每一項都獨立判定，任一不成立 → 該 Red 無效。即使 raw 與 producer 都正確，replay 也不能補救。
  - **scope**：snapshot 的變更與 attempt 的 commit 範圍，都在核准的 task scope 之內。
  - **原始 snapshot 屬於該 attempt**：snapshot 的 parent 與某個 commit 共有祖先，**並不足以**證明它屬於這個 task。必須有一份在捕捉 Red 時就記錄的對應：
    - 捕捉 provenance 帶著該 task 與 attempt 的 ID，而且 Red 是在該 attempt 的 worktree 中捕捉的；
    - 另外要有以下其中一種證據：snapshot 內的測試檔內容或 delta，出現在該 attempt 的 commit 中；或 snapshot commit 本身就在 attempt 的歷史上。
    - 原始 Red 可以在尚未 commit 時捕捉，靠這份記錄的對應連到 attempt；不要求 snapshot 必須是 attempt 的字面祖先，也不要求 Red 與 Green 在同一個 SHA。
  - **attempt 到目前 head**：attempt 的 commit 是目前 head H 的祖先。
- coordinator 以 policy 命令在目前 head 跑 Green 與 regression。replay 只在證據矛盾或有風險時作診斷；缺原始 Red → fail。
- **證據與文件分離（G05）**：
  - 證據存在 repo 追蹤範圍之外，tracked 驗收文件只引用 result 的 ID 與 digest，不要求引用自身 commit 的 SHA；
  - 程式 commit C 之後只改文件，產生 head D 時：原始 Red 依 lineage 仍然適用，但 G1 需要在 D 重跑 Green，並記錄「C→D 只有文件差異」這個適用理由。
- **N/A（G09、G10）**：只有純文件或註解的 diff 才能申請，而且必須由獨立 Reviewer 做 eligibility，並通過與 G2 相同的身份、model、權限核對。
  - 接受 → 只免除 Red／Green，G2／G3 不會因此自動通過；
  - 自我宣告、還在 pending、被拒絕、model 不符、diff 含行為設定（config、migration、test code）→ G1 不通過。
- **正式 review 前 G1 失敗**：可歸因且可修正 → `pre_review_g1` batch（計一輪）；缺 Red 或需要改 spec → Blocked。

## 8. G2、G3、Pass、版本失效

- **G2**：
  - assignment 與 result 都綁定：PR identity、完整 diff（base…head）、適用的 spec／design／AC digests、先前的 findings。
  - 以下全部成立才 passed：授權且獨立的 Reviewer、完整範圍、目前版本、verdict 為 `clean`、沒有未解的 blocking。
  - `changes_required` → failed；`blocked` → unknown，不開修正輪；缺 verdict、格式錯、部分 diff → 不 passed。
- **G3 政策來源（AC-A01，D49）**：
  1. 可讀的 repo 規則。
  2. 規則讀取回 403 或不可讀時：只有在 `repo == yschiang/loop-engineering`，**且**存在一份以 `policy_change` 人工核准、綁定該 `workflow.yaml` digest 的宣告集合時，才採用該集合，並標示 `github_rules_verified=false`。
  3. 其他情況 → unknown＋Blocked，不耗修正輪：沒有政策、政策未核准、digest 不符、或是其他 repo。
- **G3 只認 head（第一片）**：
  - check 只有在 `head_sha==H` 且 `tested-sha==H` 時才計入；
  - 必要 check 的來源若是非 head 的整合 SHA → unknown（`unsupported_integration_source`），不能 Pass；
  - G15 的正向映射延到 S2。
- **例外**：spec 的通用機制只允許 skipped／neutral，而且每一項都必須綁定一個核准的 decision；failure、cancelled、timed_out、unknown 永遠不能被例外放行。第一片的候選政策**不設任何例外**，所以 skipped／neutral 在第一片一律 fail。
- **Attempt 選擇（G14，D51-R03）**：第一片只支援 GitHub Actions 的 check-run。
  - **預期身份**：app `github-actions`，加上 workflow 檔案路徑（`.github/workflows/loopctl-ci.yml`），加上 job／check 名稱。三者都相符才是候選；同名但來自其他 workflow 或 app → 不計入。
  - 取得所有分頁。
  - **Attempt 順序**：先依所選 workflow 內的 `run_number` 排序 run，再依同一 run 的 `run_attempt` 排序重跑，取最大者。
    - `run_id` 只用來識別，不代表先後。
    - 不使用 `started_at`，所以還在 queued、沒有開始時間的較新 attempt，仍然是最新的。
    - 識別或順序資訊缺失或有歧義 → unknown。
  - 無法排序或有歧義 → unknown，不回退到舊的 success。歧義例如：同一個 H 有兩個 run 且無法排序、缺 run 或 attempt 的身份。
  - 只以 commit status 回報的必要 check → unknown（第一片不支援）。
  - 具體的 check 集合待 D11 核准。
- **版本失效（G17、D15；head 不變時的規則）**：

  | 變更項目 | G1 | G2 | G3 | 批准 |
  | --- | --- | --- | --- | --- |
  | base tip／merge_base | 在 **H 本身**重跑必要的 Green 與 regression，並綁定新的 base（D51-R02）。若需要整合新 base（衝突或相容性修正），必須由修正產生新的真實 head，所有 gates 重來。第一片不以暫時合併的 snapshot 作為 Green | 失效，以新的 base…H diff 重新 review | 重新觀察 | 不需要 |
  | spec／AC／design／plan／skill pin 的 binding | 依新的 task→AC 重評；新 AC 缺證據 → missing | 失效，以新契約重新 review | 重新觀察 | 要 `approve_plan`（新 digest）；等待期間不派工 |
  | policy | 以新政策重評 | 以新政策重評 | 重新觀察 | 要 `policy_change`；某個 gate 單純因政策改變而轉為通過，必須有這筆 decision |
  | controller 版本 | 以已存證據重算 | 以已存證據重算 | 重新觀察 | 不需要；不沿用舊結論 |

  resume 時觀察到版本改變 → 依上表處理。**acceptance 不沿用到新版本**，也不重新初始化狀態。
- **G2 與 G3 各自獨立（G02）**：review clean 加 CI fail → 沒有 Pass，開一個修正 batch；CI green 加 `changes_required` → 沒有 Pass。
- **Pass**：
  - 三 gates 在同一 `version_key` 都通過，沒有未解的 blocking；
  - 必要發布已完成並讀回：先 PR review，再 issue 摘要；
  - 之後再做一次新的 `purpose=pass` 觀察，結果一致。
  - Pass 不會觸發 merge、close、release 或 deploy。

## 9. Findings 與修正

- **分類（F01）**：Reviewer 提供 `category`（`spec_ac`、`correctness_security`、`missing_verification`、`preference`）與依據。
  - controller 只做確定性的對應：前三類 → blocking，`preference` → nonblocking；severity 只用於排序。
  - controller 不從文字推斷分類；人可以用 `reclassify_finding` 改分類，並附理由。
- **身份（F02）**：Reviewer 以 `matches` 指認同一 finding；位置移動仍用同一 ID。同一行但是不同問題、且沒有 `matches` → 新 ID。controller 不依位置或文字自動合併。
- **關閉（F04）**：只有兩種方式能關閉 finding，都必須附 actor、版本與證據：
  - 由目前版本的獨立 Reviewer 覆核，附上 result；
  - 人工以 `resolve_finding` 或 `waive_finding` 指定該 finding 與版本。

  Implementer、GitHub thread、通知都不能關閉 finding。
- **Batch（F05、F06）**：
  - 同版本的 review 與 CI 都收齊才開；文件缺陷可修；policy unknown 與 infra 問題不算修正項。
  - 回應必須涵蓋 batch 內每一個 ID：缺項 → 拒收、列出 missing IDs，也不解除任何 finding。
- **上限**：3 輪（F07）；反覆出現的 finding（`failed_rechecks≥2` 或 reopen）→ Blocked（F15、F16）。
- **爭議（F08–F10）**：每個 finding 只有一次獨立覆核，而且不計輪：
  - 接受 → 依覆核關閉；
  - 維持 → Blocked 交人；
  - 重送或 restart → 不會派第二次覆核；
  - 反證伴隨新 head → 先重跑 G1，再做最新的 review 與 CI。
- **人工退回（F11、O11）**：
  - acceptance pending 時以 `return` 退回：`source=human_acceptance`，同一個 feature 預算，Pass 失效；
  - 已 accepted 的 V1 在出現 V2 時，V2 的 acceptance 為 pending，不繼承 V1；
  - `accept` 必須指向目前 Pass 的 version_key；
  - 屬於 scope 外或 spec 錯誤 → Blocked，交給 Project Lead 與人裁決（F12）。
- **發布（F13、F14）**：
  - 發布內容：PR review 帶完整 verdict、finding 表（ID、分類、blocking、位置、依據、預期）、result ID、head、base、spec digest；issue 摘要帶待處理事項、blocking 的 ID，以及 PR review 的連結。
  - 讀回時核對 body digest 與 marker。
  - 發布失敗只重試該筆發布，不重做 review。
- **接續（D07、D14、F14）**：情境是 worker 已完成、review 已保存、issue 仍 pending、通知遺失。
  - resume 只補發 pending 的 issue 摘要；
  - 不重新派工、不重做 review、不重置預算或 findings。

## 10. 預算（D47）

- 4h active 以時間區間聯集計算，換 session 也不重置。
- 到期的 stop 優先於其他 blocker；已 prepared 的 stop 執行同一個 op；stop 讀回用盡 → 等人。
- 協調者離線的時間，在恢復時計入並記錄超出量，然後 Blocked。
- unknown 不等於已停止。

## 11. 驗證政策

驗證依時點分成兩層（D51-R05）：

- **本機驗證與 G1**：coordinator 在本機 head 跑適用的完整測試套件。
  - 平台專屬案例只用一般的 pytest 平台條件（`skipif(sys.platform …)`）選擇。
  - 以下情況 G1 都不通過：套件缺失或收集不完整（例如收集到 0 個）、有無法以平台條件解釋的 skip、有任何 failure。
  - G1 **不需要**、也不等待遠端 CI。
- **遠端 CI 與 G3**：push 並建立 PR 之後，必要的 GitHub CI job／check 是否齊全、是否成功，屬於 G3 的判定（§8）。
- 不另建逐測試的 registry、owner 標記、跨 job 計數程式或逐樣本簽核。
- 不為了變綠而放寬斷言。

## 12. 風險

- [preflight 不通過] → 在大量實作前就 Blocked。
- [只認 head 的 CI] → 若必要 check 是對 merge commit 執行的，G3 會是 unknown；候選 workflow 因此 checkout head。
- [單一 worktree] → 第一片接受；平行 writer 屬於 S2。
