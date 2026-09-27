# Design：薄 controller 第一個可用切片（候選 design-04；revision-14）

> **作者提交狀態**：revision-13，回應 review-01 的 M5 殘留、R12-01、R12-02（見 `revision-13.json`）。目前的 review 狀態以 [README](README.md) 為準。
> **狀態**：候選，不是 D11 核准，也不授權實作。本文是自足的現行候選；本版新增的做法是提案，不是已核准政策。
> **政策**：D46–D51 已確認。仍待決定：CI check 集合與政策檔的核准、reviewer 的精確 model、timeout 預設、W1、D11。
> **範圍（D50）**：薄的、可由 skill 呼叫的 controller；單一 writer；有界的觀察；可信本機協作。不復活平台機制。

> revision-14：協調者依獨立覆核修正路徑判斷優先序；Opus revision-13 為其基礎。最新 review 狀態見 README。

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
  - O23 的部分接續：第一片 `scope_change` 讓整個 run 停下等批准；只停受影響工作、其餘繼續，延到 S2；
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
| `decide <kind>` | 記錄人工 decision。第一片支援：`approve_plan`、`revise`、`scope_change`、`accept`、`return`、`resolve_finding`、`waive_finding`、`reclassify_finding`、`resolve_operation`（§4）、`resolve_read`（§5）、`budget_extension`、`policy_change`、`handoff` |
| `write <op> --id` | 外部寫入（§4） |
| `observe pr\|ci\|worker\|native` | 唯讀的有界 fetch（§5） |
| `evidence red --command-id`（worker）/ `evidence green`（coordinator） | 只執行政策檔 `workflow.yaml`（§8）定義的命令 |
| `result import --attempt` / `assess` | 匯入結果；計算 gates、Pass 與 Pass package |

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
- **重試**：只在兩種情況允許，且每個 op 最多額外 2 次（D13）：
  - 已記錄確定未送達；
  - 有已驗證的原生冪等，例如同一 SHA 的一般 fast-forward `push`（不帶 force：遠端已是該 SHA 就是 no-op，遠端已移動就被拒）。以查詢結果判斷 PR 是否存在，**不算**冪等（D51-R01）。
  - not_found、client 已結束、Herdr socket 或 GitHub 的延遲生效，都不構成證明 → unknown 交人。
- **讀回**：只看既有的 write，不重發；每個 attempt 最多 3 次，每次都計入（包括「仍在執行」）。到上限 → `blocked(readback_exhausted)`。
- **Branch 歷史（active run）**：controller 管理中的 feature branch 只以一般 fast-forward push 更新；`write push` 的固定 argv 不含任何 force 選項。整合 base 用 merge commit（§8），不 rebase、不 squash、不 force-push。遠端拒絕 non-fast-forward → failed 並 Blocked 交人，不自動 rebase 或 force。這是受控 run 的規則，不是 repo 全域禁令。
- **PR 正向路徑**（AC-A04、DUR-06）：
  - G1 passed 之後才 `write push`，再 `write pr_ensure`。
  - **預期身份先持久化**：`pr_ensure` 在 `prepared` 時就寫入預期身份（repo、head repo＋branch、目前 head SHA H、base repo＋branch）與唯一的 operation marker（PR body 內的 `loopctl-op:<op_id>`），之後才呼叫外部。
  - **建立之前**，查詢該 repo 中這個 head branch 的所有 open PR（不限 base）：
    - 0 個 → 建立一次，body 帶 marker；
    - 恰一個，且 head repo／branch、head SHA、base repo／branch 全部相符 → 沿用，記 `origin=existing`（明示不是本次建立，也不宣稱有 marker）；
    - 恰一個但任一欄不符（例如同 branch、不同 base）→ Blocked（`pr_identity_mismatch`），**不另建**；
    - 多於一個 → Blocked。
  - 建立的結果 unknown 時，只讀回：
    - marker 與完整身份都相符 → succeeded，`origin=created`；
    - 有 marker 但身份不符，或身份相符但沒有 marker → Blocked 交人；
    - 查無 → 仍然 unknown，Blocked，**不再建立第二次**（請求可能晚一點才生效）。
  - 記錄 PR identity：number、node id、url、head repo／branch／SHA、base repo／branch、`origin`。
  - 之後觀察到 PR 的 head repo／branch 或 base repo／branch 與記錄不同（例如 PR 被改 base）→ Blocked，不自動改綁。
  - 正式 review 只在 PR identity 已記錄之後才派出。
- **人工處理 unknown（`decide resolve_operation`）**：只記錄，不執行任何外部寫入，附 actor、原因與證據。兩種形式：
  - `--bind <observed>`：controller 以一次新的唯讀讀取核對該結果符合 op 已持久化的預期身份；相符才記為 succeeded（`resolved_by=human`；PR 沒有 marker 時記 `origin=existing`），不符 → 拒絕。
  - `--not-delivered`：人附上請求未送達的權威證據（例如連線前就失敗的 client 紀錄；DUR-06）。「查不到」本身不是證據；只附查無觀察 → 拒絕。記錄後 op 轉為 failed(確定未送達)；之後的重試仍受每 op 額外 2 次的上限，`pr_ensure` 重試前仍先做建立前查詢。

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
- 通用的 seq、版本水位、讀取預算與 `worker`／`native` 讀取由同一模組提供；`pr`／`ci` 在其上延伸（見 tasks 的共用檔案順序）。
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

- **Red 單位**：G1 在目前 head H 核對以下每一個單位都有合格的原始 Red（raw、exit、task／attempt、snapshot、provenance 逐項核對）：
  - 核准 plan 的每一個 task；task 集合為空 → fail；
  - 每一個**改變行為**的修正 attempt，包括 `pre_review_g1`、G2／G3 修正 batch、整合 base 時 Implementer 自己寫的解法（§8；匯入的 base 內容不算）、人工退回。這類 Red 必須另外綁定所處理的 finding ID 與 batch ID；batch 內每一個改變行為的 finding，至少要有一個列出它的 Red（GAT-03「同一 task／後續修正」、D01、D26）。
  - 修正是否改變行為，依實際 diff 判定；不改變行為的修正走下方 N/A 資格，不是自動豁免。
- **Red 的適用資格**（D51-R07）：以下每一項都獨立判定，任一不成立 → 該 Red 無效。即使 raw 與 producer 都正確，replay 也不能補救。
  - **scope**：snapshot 的變更與 attempt 的 commit 範圍，都在核准的 task scope（修正則為該 batch 的 finding 範圍）之內。整合 attempt 只檢查作者編輯的路徑；已驗證為原樣匯入的 base 內容不算作者編輯（§8「整合 attempt 的核對」）。
  - **原始 snapshot 屬於該 attempt**：snapshot 的 parent 與某個 commit 共有祖先，**並不足以**證明它屬於這個 task。必須有一份在捕捉 Red 時就記錄的對應：
    - 捕捉 provenance 帶著該 task 與 attempt 的 ID（修正另帶 finding 與 batch ID），而且 Red 是在該 attempt 的 worktree 中捕捉的；
    - 另外要有以下其中一種證據：snapshot 內的測試檔內容或 delta，出現在該 attempt 的 commit 中；或 snapshot commit 本身就在 attempt 的歷史上。
    - 原始 Red 可以在尚未 commit 時捕捉，靠這份記錄的對應連到 attempt；不要求 snapshot 必須是 attempt 的字面祖先，也不要求 Red 與 Green 在同一個 SHA。
  - **attempt 到目前 head**：attempt 的 commit 是目前 head H 的祖先。
- **Attempt 資格**：只有 commit 位於 H lineage 的 attempt 有資格。被停止或放棄的 attempt，其 Red 不轉移給別的 attempt；重做的 attempt 要在自己的 worktree 捕捉自己的原始 Red。
- **缺原始證據**：某個單位沒有合格的原始 Red（例如修正只有 Green；行為已進入 H，而唯一的 Red 屬於被放棄的 attempt）→ G1 不通過，feature Blocked 並附原因 `original_red_unavailable:<unit>`，交人裁決。不以 replay、回退程式重新捕捉或其他方式製造 Red 代替。
- **歷史被外部改寫**：新觀察到的 H 不是先前記錄 head 的後代（例如外部 rebase 或 force-push）→ 所有依 lineage 判定的 Red 資格失效，G1 Blocked（`history_rewritten`），不補造證據，交人。
- coordinator 以政策命令在目前 head 跑 Green 與 regression。replay 只在證據矛盾或有風險時作診斷；缺原始 Red → 依上方處理。
- **證據與文件分離（G05）**：
  - 證據存在 repo 追蹤範圍之外，tracked 驗收文件只引用 result 的 ID 與 digest，不要求引用自身 commit 的 SHA；
  - 程式 commit C 之後只改文件，產生 head D 時：原始 Red 依 lineage 仍然適用，但 G1 需要在 D 重跑 Green，並記錄「C→D 只有文件差異」這個適用理由。
- **N/A（G09、G10、D26）**：依 diff 的實際行為判定，不以檔名或檔案類型一律排除。
  - 由獨立 Reviewer 做 eligibility，並通過與 G2 相同的身份、model、權限核對；Implementer 不能自行豁免。
  - 例：YAML 或測試檔只改註解，可以申請；改 config 值、測試斷言、migration 或任何行為 → 不合格。
  - 接受 → 只免除 Red／Green，G2／G3 不會因此自動通過；
  - 自我宣告、還在 pending、被拒絕、model 不符、Reviewer 判定有行為變更 → G1 不通過。
- **正式 review 前 G1 失敗**：可歸因且可修正 → `pre_review_g1` batch（計一輪，修正 attempt 依上方需要綁定 batch 的原始 Red）；缺原始 Red 或需要改 spec → Blocked。同一機制也承接原因為 `base_integration` 的整合（§8）。

## 8. G2、G3、Pass、版本失效

- **G2**：
  - assignment 與 result 都綁定：PR identity、完整 diff（base…head）、適用的 spec／design／AC digests、先前的 findings。
  - 以下全部成立才 passed：授權且獨立的 Reviewer、完整範圍、目前版本、verdict 為 `clean`、沒有未解的 blocking。
  - `changes_required` → failed；`blocked` → G2 unknown，**且 feature Blocked**，不開修正輪（AC-G03）；缺 verdict、格式錯、部分 diff → 不 passed。
- **G3 政策來源（AC-A01，D49）**：
  1. 可讀的 repo 規則。
  2. 規則讀取回 403 或不可讀時：只有在 `repo == yschiang/loop-engineering`，**且**存在一份以 `policy_change` 人工核准、綁定政策檔 digest 的宣告集合時，才採用該集合，並標示 `github_rules_verified=false`。
  3. 其他情況 → unknown＋Blocked，不耗修正輪：沒有政策、政策未核准、digest 不符、或是其他 repo。
- **政策檔**：repo 根目錄的 `workflow.yaml`，是 loopctl 的政策檔，不是 GitHub workflow。內容：必要 checks（app、GitHub workflow 路徑與其 blob digest、job／check 名稱）、`source: head`、例外（第一片為空）、`evidence` 的 command IDs。由 T1.1 建立；之後的改動需要新的 `policy_change`。H 上的 `.github/workflows/loopctl-ci.yml` 與政策檔記錄的 digest 不符 → unknown＋Blocked。
- **G3 只認 head（第一片）**：
  - check 只有在 `head_sha==H` 且該 job 的 tested SHA 產物等於 H 時才計入；
  - 必要 check 的來源若是非 head 的整合 SHA → unknown（`unsupported_integration_source`），不能 Pass；
  - G15 的正向映射延到 S2。
- **例外**：spec 的通用機制只允許 skipped／neutral，而且每一項都必須綁定一個核准的 decision；failure、cancelled、timed_out、unknown 永遠不能被例外放行。第一片的候選政策**不設任何例外**，所以 skipped／neutral 在第一片一律 fail。
- **Run／attempt 選擇（G14，D51-R03）**：第一片只支援 GitHub Actions 的 check-run。
  - **觸發與事件身份**：候選 GitHub workflow 只由 `pull_request`（opened、synchronize、reopened；目標為預期 base branch）觸發，不由 push 觸發。check-run 要成為候選，須全部相符：app `github-actions`；workflow 路徑 `.github/workflows/loopctl-ci.yml`；job／check 名稱；所屬 run 的 `event=pull_request`、`head_sha=H`，且關聯的 PR number 等於已記錄的 PR。
    - 同名但來自其他 app 或其他 workflow → 不是本政策的 check，不計入；
    - 同一 workflow 路徑、`head_sha=H`，但 event 不是 `pull_request`，或關聯到其他 PR → unknown（`unexpected_event_context`），不忽略，不能 Pass。
  - 取得所有分頁。
  - **每個 run 內**：依 `run_attempt` 取最新的 attempt；較早的 attempt 被取代，不再要求。`run_id` 只作識別；不使用 `started_at`，所以 queued、沒有開始時間的較新 attempt 仍是最新。
  - **同一 H 有多個 PR run**（例如 close／reopen 後再跑）：依 `run_number` 列出，每個 run 的最新 attempt 都計入。全部 success 才算 success；任一 pending／queued → pending；任一失敗類 → 以該狀態不通過。因此，舊 run 在新 run 之後被重跑、結果是 failure 或 pending 時，G3 不會依新 run 的 success 通過。只看 H；舊 head 的 run 不計。
  - 識別或順序資訊缺失（缺 run 身份、`run_number` 或 `run_attempt`）、同一 workflow 出現重複的 `run_number` → unknown，不回退到舊的 success。
  - 只以 commit status 回報的必要 check → unknown（第一片不支援）。
  - **每個 job 的 tested SHA**：每個 job 上傳唯一名稱的產物 `tested-sha-<job>-<run_attempt>`，內容為 run_id、run_attempt、job 名稱、check 名稱、tested SHA。check-run 依 run_id／run_attempt／job 對到產物，並讀取產物內容逐欄比對（不只看名稱）；全部欄位相符且 SHA 等於 H 才計入；缺產物或任一欄不符 → unknown，不能 pass。這是保守規則：只重跑失敗 job 時，其他 job 可能沒有同一 attempt 的產物，需要改為重跑全部 jobs。controller 不新增任何 rerun 功能。
  - 具體的 check 集合待 D11 核准。
- **為什麼不會誤放行**：原 review 的「PR run 失敗、push run 成功」在本政策下不會出現 push run；若出現，屬 `unexpected_event_context` → unknown。舊 PR run 被重跑成失敗或 pending，屬於同一 H 的 run，計入後 G3 不通過。
- **版本失效（G17、D15；head 不變時的規則）**：

  | 變更項目 | G1 | G2 | G3 | 批准 |
  | --- | --- | --- | --- | --- |
  | base tip／merge_base | 沒有整合觸發時：在 **H 本身**重跑必要的 Green 與 regression，並綁定新的 base（D51-R02）；這只更新綁定，不驗證與新 base 的整合結果。有觸發時依下方「整合 base」產生新 H，所有 gates 重來。第一片不以暫時合併的 snapshot 作為 Green | 失效，以新的 base…H diff 重新 review | 重新觀察；H 未變時沿用 H 的 head-only 結果，並記錄適用理由「只認 head、H 未變」（AC-G17） | 不需要 |
  | spec／AC／design／plan／skill pin 的 binding | 依新的 task→AC 重評；新 AC 缺證據 → missing | 失效，以新契約重新 review | 重新觀察 | 要 `approve_plan`（新 digest）；等待期間不派工 |
  | policy | 以新政策重評 | 以新政策重評 | 重新觀察 | 要 `policy_change`；某個 gate 單純因政策改變而轉為通過，必須有這筆 decision |
  | controller 版本 | 以已存證據重算 | 以已存證據重算 | 重新觀察 | 不需要；不沿用舊結論 |

  resume 時觀察到版本改變 → 依上表處理。**acceptance 不沿用到新版本**，也不重新初始化狀態。
- **整合 base 的觸發**：只在以下之一成立時整合：
  - GitHub 讀到 `mergeable=false`（衝突）；
  - Reviewer finding 判定與新 base 不相容；
  - 人工 decision（`revise`，理由註明整合 base）。

  `mergeable` 尚在計算（null）→ 當作 pending，依輪詢規則等待；到 timeout 仍未知 → Blocked。沒有觸發 → 不整合，只依上表重新綁定 base。
- **整合 finding 與去重**：觸發成立時，controller 記錄一個 blocking finding，`source=base_integration`。它的 ID 由（base repo／branch、釘住的 base tip B、目前 head H）決定。同一組值重複觀察到 `mergeable=false`，或重複的人工 decision，都對到同一個 ID，最多只有一個未結的整合 batch。Reviewer 的不相容 finding 保留自己的 ID，放進同一個 batch。整合 Red 綁定的就是這個 ID 與 batch ID。
  - blocking 來自觸發本身，不是從文字推斷分類。
  - 關閉仍依 F04：新 H 的獨立 Reviewer 覆核，或人工裁決。
- **路徑選擇（對目前 H，依以下優先順序判斷）**：
  - 先套用 D47 active-time／stop 規則、修正輪數上限、owner 與 writer 安全條件；下面任何路徑都不能繞過這些限制。預算耗盡或停止狀態不明 → Blocked，不派修。
  1. **前置整合優先**：整合觸發已成立，而且適用 G1 尚未通過，或任一必要 G2／G3 已過時、尚不能啟動、已確定不可用或逾時 → 走既有 `pre_review_g1`（原因 `base_integration`）。PR 衝突而沒有候選 CI run 屬於此項；即使 review 還在執行，也不等待不存在的 CI。已過時的 review 結果只保留歷史，收到的 findings 保留。
     - controller 不再為舊 H 派新的 G2。各 gate 保存真實原因；只有衝突造成 CI 不可用時，G3 才記 `unknown(ci_unavailable_conflict)`。缺 CI 永遠不算 success。
  2. **一般收齊**：只有適用 G1 已在 H 通過，**且 G2、G3 每一個都有同版本的終態結果或確實在途、可取得的執行**，才等待在途項目，在各自 timeout 內收齊後開一個 batch。若兩者都已是終態，就直接合併已收到的問題與整合 finding；不再等待。
     - 等待中若任一結果失效或確定不可用，重新依第 1 項判斷；正常有效的在途結果不被任意跳過。終態的 policy unknown／review blocked 等獨立 blockers 仍按原規則處理，不因整合需求而清除。
  - 兩條路徑的共同規則：
    - 派修前，Implementer 不能有 active attempt（依 §6 的 writer 結束證據）；unknown → 依 D47 停止或 Blocked，不派競爭 writer；
    - 一個 batch，實際派修時計一輪；
    - H 上未完成或已過時的 G2／G3 結果標為 obsolete，只存歷史；已收到的 findings 保留在 registry；
    - 整合後的新 H 從頭取得完整的 G1、G2、G3。
- **整合 assignment**：assignment 釘住先前的 feature head H，以及協調方以唯讀 fetch 取得的確切 base tip B（SHA）。它授權兩件事：
  - 原樣匯入 B 相對於 merge-base(H, B) 的變更；
  - 作者編輯，只限衝突路徑，以及 batch 內各 finding 的核准 scope。

  Implementer 只在本機 feature worktree 以 `git merge` 產生 merge commit M；它沒有 push 或 GitHub 權限。之後由協調方以 `write push` 做一般 fast-forward push，產生新 H。
  - 這是 feature branch 上的本機 git merge，**不是** GitHub PR merge：不呼叫 GitHub merge API，外部寫入種類不增加 merge，也不取得或需要合併 PR 的權限（O10）。
- **整合 attempt 的核對**（用既有 git 物件即可重現，不需要語意 diff 框架或逐檔 registry）：
  - M 的 parents 必須恰好是 [H, B]，而且第一個 parent 是 H；不符 → 拒收。
  - controller 以 `git merge-tree --write-tree H B` 重算自動合併的 tree 與衝突路徑清單，存進 attempt provenance。然後逐路徑比對 M 的 tree：
    - 與自動合併結果相同 → **原樣匯入**，不是作者編輯；
    - 不同，而且是衝突路徑 → **作者的衝突解法**；
    - 不同，而且不是衝突路徑 → **作者的額外編輯**。
  - 作者編輯（兩種都算）必須在上述授權 scope 內。藏在 base 匯入裡、與 batch 無關的作者編輯，會因為和自動合併結果不同而被找出，拒收。需要超出 scope 才能解決 → Blocked，回 D11。
  - **Red**：
    - 沒有作者編輯的純機械匯入 → 不需要為上游行為補造 Red，也不宣稱行為 N/A。先前 task 的 Red 經第一個 parent H 的 lineage 仍可追溯。
    - 作者編輯改變行為 → 需要綁定整合 finding ID 與 batch ID 的原始 Red（§7），缺少 → G1 不通過並 Blocked。
    - 作者編輯不改變行為 → 走 §7 的 N/A 資格。
  - 不論哪種，新 H 都需要 Green／regression、完整 G2 與 G3。兩個 parent 都保留，舊 attempt 的 commit 仍是 H 的祖先。
- **G2 與 G3 各自獨立（G02）**：review clean 加 CI fail → 沒有 Pass，開一個修正 batch；CI green 加 `changes_required` → 沒有 Pass。
- **Pass**：
  - 三 gates 在同一 `version_key` 都通過，沒有未解的 blocking；
  - 必要發布已完成並讀回：先 PR review，再 issue 摘要；
  - 之後再做一次新的 `purpose=pass` 觀察，結果一致。
  - Pass 不會觸發 merge、close、release 或 deploy。
- **Pass package**（ORC-05、D49）：由 `assess` 從 feature 狀態投影成人可讀的 JSON（`status --human` 可顯示），不另存一份權威，也不能單獨放行。內容：
  - version_key、PR identity（含 `origin`）、head、base；
  - 三 gates 的理由，以及 result ID 與 digest；
  - findings：未解 blocking 為空；列出未解 nonblocking，以及已關閉項的 closure 引用；
  - G3 政策來源：`rules`，或 `approved_policy`＋`workflow.yaml` digest＋`policy_change` decision ID；以及 `github_rules_verified`；
  - 限制：例如 GitHub rules 未核對、只認 head、延後項目；
  - 發布狀態與 receipts、`purpose=pass` 觀察的 seq；
  - acceptance 為 pending。

  任何被引用的紀錄改變 → 重新投影；package 與狀態不一致時以狀態為準。

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
  - 同版本的 review 與 CI 都收齊才開；例外是 §8 的 `base_integration` 路徑 2，不等待無法開始的 G2 或因衝突不會出現的 CI。文件缺陷可修；policy unknown 與 infra 問題不算修正項。
  - 派修的 assignment 帶 batch ID 與 finding IDs；改變行為的修正依 §7 需要綁定的原始 Red。
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

同一套收集／skip／失敗政策，同時用於本機 G1 與每一個 CI job（D51-R05）：

- **執行方式**：只用 test-only 設定，不是產品 hook，也不是 registry：
  - `pyproject.toml` 的 pytest 設定：`--strict-markers`、`xfail_strict=true`；
  - `tests/conftest.py` 提供唯一的平台 marker `only_on(<platform>)`，並在 session 結束時檢查，以下任一 → session 失敗（exit ≠ 0）：
    - 收集數為 0；
    - 任何不是由 `only_on` 在非所屬平台產生的 skip（包括測試內自行 `pytest.skip`，即使 reason 寫著 platform）；
    - 任何 xfail 或 xpass；
    - CI job 設定的預期平台（`LOOPCTL_EXPECT_PLATFORM`）與實際 `sys.platform` 不符。
  - 所以「reason 寫著 platform」不算證據；標為 Linux 專屬的案例在 Linux 上 skip（例如缺工具）→ 該 job 失敗。
- **本機與 G1**：coordinator 在本機 head 用同一命令跑完整套件；session 失敗 → G1 不通過。G1 **不需要**、也不等待遠端 CI。
- **遠端 CI 與 G3**：每個必要 job 用同一命令；job 失敗 → G3 不通過（§8）。
- 不另建逐測試的 registry、owner 標記、跨 job 計數程式或逐樣本簽核。
- 不為了變綠而放寬斷言。

## 12. 風險

- [preflight 不通過] → 在大量實作前就 Blocked。
- [只認 head 的 CI] → 若必要 check 是對 merge commit 執行的，G3 會是 unknown；候選 workflow 因此 checkout head。
- [同一 H 的舊 run 失敗] → 需要重跑該 run 或推新 head 才能 success；這是為了不隱藏同一 H 上的真實失敗。
- [單一 worktree] → 第一片接受；平行 writer 屬於 S2。
