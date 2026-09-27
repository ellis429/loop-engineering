# Design：薄 controller 第一個可用切片（候選 design-04；revision-17）

> **作者提交狀態**：revision-17（Opus 5.5 主持）。revision-15 以 revision-14 為基礎補上具體執行預設、內部介面契約與派工缺口（標 `[R15]`）；revision-16 回應 revision-15 獨立覆核的 R15-01–R15-10（標 `[R16]`）；revision-17 回應 revision-16 覆核的 R16-01、R16-02 與 R15-02 的剩餘部分（標 `[R17]`，見 `revision-17.json`）。目前的 review 狀態以 [README](README.md) 為準。
> **狀態**：候選，不是 D11 核准，也不授權實作。本文是自足的現行候選；本版新增的做法是提案，不是已核准政策。
> **政策**：D46–D52 已確認。本版提出、待 D11 核准的具體值：產品 profile（§6）、timeout 與讀取界線（§5、§10）、CI check 集合與 `workflow.yaml`（validation §6）、W1 基底（tasks T0.1）。彙整見 [D11 確認包](d11-confirmation.md)。
> **範圍（D50）**：薄的、可由 skill 呼叫的 controller；單一 writer；有界的觀察；可信本機協作。不復活平台機制。

> revision-14：協調者依獨立覆核修正路徑判斷優先序；Opus revision-13 為其基礎。

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
| `observe pr\|ci\|worker\|native [--purpose P]` | 唯讀的有界 fetch（§5）。`P` 預設為該來源的一般用途；Pass 前的確認觀察用 `--purpose pass`（§8）[R15] |
| `evidence red --command-id`（worker）/ `evidence green`（coordinator） | 只執行政策檔 `workflow.yaml`（§8）定義的命令 |
| `result import --attempt` / `assess` | 匯入結果；計算 gates、Pass 與 Pass package |
| `preflight --role R --out P` | 對已選 profile 做能力 probe（§6），不讀寫 feature 狀態 |

- Orchestrate skill 只依 `next` 與 `safety` 行動。
- 角色、runtime 的父子關係、共同入口，都不會授予額外的決策權（O19）；只有 `claim` 取得的 token 與人工 decision 算數。
- 未知的子命令或 op（包括 `merge`、`close`、`release`、`deploy`、`adopt`、`delegate`）→ exit 2 或 `unsupported`，0 次外部呼叫。

**`next` 的動作詞彙 [R15]**（完整集合；orchestrate skill 只認這些，未列者一律停下交人）：

| `next.action` | 參數 | orchestrate 的動作 |
| --- | --- | --- |
| `wait` | `poll_after_s`、`reason` | 等待後重新呼叫 `next` |
| `observe` | `source`、`purpose`、`read_key` | 呼叫對應的 `observe` |
| `write` | `op`、`id` | 呼叫 `write <op> --id` |
| `import` | `attempt` | 呼叫 `result import` |
| `evidence_green` | `head` | 呼叫 `evidence green` |
| `assess` | — | 呼叫 `assess` |
| `human` | `blockers`、`decision_kinds` | 停止自動前進，把 blockers 與可用的 `decide` 種類交給人 |
| `done` | `status`（`pass` 或 `accepted`） | 結束本輪；Pass 仍等人工 acceptance |

`safety` 回傳同一格式，只含到期 stop 與讀回等必須先做的動作；有 `safety` 動作時 `next` 不給其他動作（§10）。

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
- **模組間的內部契約 [R15]**（T2.1 建立，之後的 task 只呼叫、不改語意）：
  - `store.load(feature) -> (revision, state)`；不可信 → 拋出 `UntrustedState`（CLI 轉為 exit 5）。
  - `store.commit(feature, expected_revision, transition_id, mutate) -> revision`：在 lock 內核對 revision，套用 `mutate(state) -> state`，history-first 提交。同一 `transition_id` 已提交且內容相同 → 回傳原 revision，不重複生效；內容不同 → Blocked（`transition_conflict`）。
  - `store.put_object(bytes) -> digest`、`store.get_object(digest) -> bytes`：content-addressed 證據物件；狀態中的物件引用在提交時核對存在（s6）。
  - owner token：`claim` 產生明文 token 只回給呼叫者一次，狀態只存 digest；每個會寫入的命令以 `--token` 核對。
  - 各 task 新增的狀態欄位放在自己的頂層欄位下（例如 `writes`、`gates.g1`），不改其他 task 欄位的意義；`schema_version` 只在 T2.1 定義。

## 4. 外部寫入

有限的種類：`worktree_create`、`agent_start`、`prompt`、`stop`、`push`、`pr_ensure`、`publish_pr`、`publish_issue`。**沒有** merge、close、release、deploy（O10）。

`evidence green` 在本機建立與移除的臨時 checkout（§7）不是外部寫入：它不經 Herdr server 或 GitHub，由 loopctl 自己的子程序同步完成，受 §7 的執行界線管理，不適用本節的 op 狀態機 [R16]。

- **狀態流程**：`prepared → in_flight → succeeded | failed(確定未送達) | unknown`。
- `write` 在同一程序內：consume 一次 → 呼叫固定 argv 一次 → 記錄 receipt。
- **重試**：只在兩種情況允許，且每個 op 最多額外 2 次（D13）：
  - 已記錄確定未送達；
  - 有已驗證的原生冪等，例如同一 SHA 的一般 fast-forward `push`（不帶 force：遠端已是該 SHA 就是 no-op，遠端已移動就被拒）。以查詢結果判斷 PR 是否存在，**不算**冪等（D51-R01）。
  - not_found、client 已結束、Herdr socket 或 GitHub 的延遲生效，都不構成證明 → unknown 交人。
- **讀回**：只看既有的 write，不重發；每個 attempt 最多 3 次，每次都計入（包括「仍在執行」）。到上限 → `blocked(readback_exhausted)`。
- **外部呼叫的時限 [R15]**：每次外部寫入的子程序有固定時限（`workflow.yaml` `limits.write_call_s`，提案 60 秒；`push` 與 `pr_ensure` 為 120 秒）。超過時限時終止子程序，結果記為 **unknown**，不是 failed：請求可能已送出，之後只走讀回。
- **Op 紀錄與 adapter 回傳 [R15]**（T2.3 定義；T6.1、T6.2 只新增 op 種類與對應的 tool 函式）：
  - `writes[op_id]`：`kind`、`prepared`（預期身份、固定 argv 的 digest、marker）、`status`、`attempts[]`（每次的開始時間、結束時間、outcome、receipt 物件引用）、`readbacks[]`（seq、觀察結果的物件引用）、`resolved_by`。
  - tool 函式只回傳 `{outcome: succeeded|failed_not_delivered|unknown, receipt, evidence}`；是否可重試、何時讀回由 `writes.py` 依本節規則決定，tool 函式不自行重試。
  - `assignments[attempt_id]`：`task_id` 或 `batch_id`、`finding_ids`、role、profile、worktree、branch、目前 head、PR identity（若已有）、spec／design／plan／AC digests、AC IDs 與驗法、scope（允許的路徑）、結果位置、整合 attempt 另帶釘住的 H 與 B（§8）。G1（§7）與 review（§8）只讀這些欄位。
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
- **Pending 輪詢**：成功取得但內容是 pending，不算失敗。以輪詢間隔、角色 timeout（§10）與 D47 active 預算為界；timeout 後依 §10 處理。
- **讀取與輪詢的界線 [R15]**（值在 `workflow.yaml` `limits`，提案值如下，D11 核准）：
  - 單次讀取子程序時限 30 秒；超過 → 算一次傳輸失敗（計入讀取失敗預算）。
  - GitHub 讀取每頁 100 筆並讀完所有分頁；任一頁失敗 → 整次讀取算一次失敗，不採用部分結果。
  - 輪詢間隔：`worker`／`native` 30 秒；`pr`／`ci` 60 秒。`next` 以 `wait.poll_after_s` 回傳，orchestrate 不自行決定間隔。
  - GitHub `mergeable=null` 的等待包含在 CI 的等待時限內（§10），不另設時鐘。
  - 理由：Herdr 與 native transcript 是本機讀取，30 秒足以及時偵測 turn 結束；GitHub 每次觀察約需數次 API 呼叫，60 秒間隔在 30 分鐘視窗內遠低於每小時 5000 次的速率限制。

## 6. Runtime、writer 結束與獨立性

- **第一片的產品 profile [R15 提案，待 D11]**：loopctl 管理的 attempts（R1–R3 與 T8）使用以下兩個 profile，定義在 `workflow.yaml` 的 `profiles`，由 `policy_change` 綁定 digest：

  | 欄位 | `implementer` | `reviewer` |
  | --- | --- | --- |
  | transport | Herdr 0.9.1 | Herdr 0.9.1 |
  | runtime | Claude Code（`claude`） | OpenCode（`opencode`） |
  | provider／model | `anthropic`／`claude-opus-5-5` | `openai`／`gpt-6-astra` |
  | effort | `--effort high` | `--variant xhigh` |
  | 權限設定檔 | `profiles/implementer.claude-settings.json`（`--settings`） | `profiles/reviewer.opencode.json`（OpenCode agent 權限） |
  | 可寫範圍 | 被指派的 feature worktree、自己的 result 位置 | 自己的 review clone、自己的 result 位置 |
  | 明確拒絕 | `git push`、`gh`、`herdr`、`evidence red` 以外的所有 `loopctl` 子命令（含 `decide`）、worktree 外的寫入 | `git push`、`gh`、`herdr`、所有 `loopctl` 子命令、clone 外的寫入（含作者 worktree） |

  - 理由：Implementer 沿用 D36／D52 的預設 Opus；Reviewer 採 GPT-6 Astra xhigh，是 revision-14 與 revision-15 文件覆核實際使用、以 Codex native metadata 核對過的模型，符合 GAT-05「既有獨立 Codex review 要求」由核准 OpenAI model 在 OpenCode 承載的寫法。兩者是不同的實際模型（D52）。
  - transport、runtime、provider、model、effort 分欄保存。
  - **不同模型核對**：`workflow.yaml` 中 `reviewer` 與 `implementer` 的 model 相同 → preflight `unverified`（f4）。這只核對核准設定；獨立性仍靠獨立 session、clone 與權限負例（§6 preflight、r1）。
  - **Effort 的讀回**：model 必須由 native 紀錄讀回相符才算 verified；effort 記錄要求值，native 紀錄有提供時一併核對，沒有提供時標 `effort_verified=false`，並列在 Pass package 的限制中，不單獨造成 Blocked。
  - OpenCode 的 `openai/gpt-6-astra` 在本機 model 清單中存在（2026-09-28 查詢），但尚未經 OpenCode 實際推論驗證；R1 未通過 → Blocked，不自動改用 Codex CLI 或其他 model。
- **Bootstrap 開發的分工不是產品 profile**：T0–T7 的程式由協作者依 D52 派給 agents 撰寫與審查（tasks.md「派工與模型」），那些 sessions 不受 loopctl 管理，也不構成上表 profile 的能力證據。
- **未選用的接入（D23）**：Orca、Codex CLI、其他 profile 不在 preflight 範圍。即使它們缺失或故障，也不阻斷已選的兩條路徑，也不會被自動改用。
  - 這與「已選 profile 本身缺少或 unverified → Blocked」是兩回事。
  - OpenCode-only 部署的變體延到 S2。
- **同一 runtime 承載兩個角色（D24）**：延後。第一片 R1 的 profile 組合不能證明這個情境。
- **Capability preflight**（最早執行）：
  - 以 `workflow.yaml` 的 profile 與權限設定檔啟動一個專用 session，載入核准 skills 的正式 profile（不使用 safe-mode）；
  - 讀回 native model 與 marker；
  - **位置核對 [R16]**：從 native session 紀錄讀回實際工作目錄（Claude Code transcript 的 `cwd`、OpenCode session 的 `directory`），再以 git 讀該目錄的 repo toplevel、remote 與 branch，逐項比對 profile 要求的 repo、worktree 路徑與 branch。只有 prompt 被接受（input accepted）而沒有 native turn、讀不到 native 工作目錄、或任一項不符 → `unverified`。不以 shell cwd、`current` 或角色名稱推定（AC-D18）；runtime 不提供可讀的 native 工作目錄時，R1 就是 unverified 並 Blocked；
  - 權限負例：寫出範圍、`git push`、`gh`、`herdr`、`loopctl decide` 都被拒；每一項都要觀察到「被拒」**且**資源未改變（檔案不存在、遠端 ref 未變、fake 或真實的呼叫紀錄沒有新增）；
  - stop 後以 process-info 確認停止。
  - 結果只綁定該版本與該 profile；未驗證 → Blocked。它不證明能抵抗同一 OS 帳號的偽造（D48）。
  - **Receipt [R15；R16 補位置]**：`--out` 寫出 JSON：role、profile digest、`workflow.yaml` digest、Herdr／runtime 版本、native session ID、讀回的 model（與 effort，若有）、要求與實際的 repo／worktree／branch、每個負例的命令、觀察到的拒絕與資源檢查、stop 的 process-info、`verdict: verified|unverified` 與逐項原因。每個負例與位置項目各自獨立判定，任一項不成立即 unverified。
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
- **Green 的執行位置 [R15]**：`evidence green` 在 `$LOOPCTL_HOME` 下以 `git worktree add --detach <tmp> H` 建立 H 的乾淨 checkout，在其中執行政策命令，結束後移除；不在 Implementer worktree 執行，所以未追蹤或未提交的檔案不影響結果（D45-02 GAT-03「獨立 checkout」保留）。結果記錄實際 checkout 的 `git rev-parse HEAD`，必須等於 H。
- **證據命令的執行界線 [R16]**（`evidence red` 與 `evidence green` 相同）：
  - 開始前先在狀態寫入一筆 `activities` 紀錄（種類 `evidence`、開始時間），完成後寫入結束時間；這段時間計入 active（§10）。
  - 子程序以獨立的 process group 執行，時限為 `min(limits.evidence_call_s, budget.remaining(state, now))`（T2.3 提供的純函式）[R17]；`limits.evidence_call_s` 提案 900 秒（與 CI job 的 15 分鐘相同）。
  - 到限時終止整個 process group，記錄已用時間與截斷的輸出，結果是 `evidence_timeout`：該次 Red 無效或 G1 不通過，不產生任何 passed。若是剩餘 active 預算用完，接著走 §10 的到期路徑；否則 feature Blocked（`evidence_timeout`）交人，0 次派新 worker，不自動重跑。
  - 臨時 checkout 在 `finally` 中移除；移除失敗時把路徑記入 `blockers` 供人清理，不影響已記錄的判定。
  - coordinator 在 `evidence green` 執行期間不會回到 orchestrate 的迴圈，所以這個時限同時是期間內 safety 檢查的上限；到限後下一次 `next` 先處理 §10 的到期 stop。
- **G1 的輸入與輸出 [R15]**：G1 只讀 `assignments`（§4）中的 `task_id`／`batch_id`／`finding_ids` 與整合的 H、B，以及已匯入的 evidence；不建立 batch 或 finding。G1 的輸出是 `gates.g1`：`passed|failed|blocked`、逐單位的原因（例如 `original_red_unavailable:<unit>`、`integration_regression`、`history_rewritten`）。開 `pre_review_g1` batch 由 T5.1 依這些原因決定（§8、§9）。
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
  - **Review assignment 與 result 的欄位 [R15]**（T5.1）：
    - assignment：§4 的共同欄位，加上 diff 範圍 `base_sha…head_sha`、review 用的獨立 clone 路徑、先前 findings 的快照（格式與下方「修正 assignment 的快照」相同：每項的完整內容與狀態、先前的 review result ID 與版本、先前的修正 commits 與證據引用，以及整份快照的 digest；派出後不隨 registry 改變，r10）、結果 schema 版本。爭議覆核的 assignment 同樣帶這份快照，另加被爭議 finding 的反證回應 [R17；FIN-03 對派修與覆核 assignment 的要求]。
    - result：`verdict`（`clean`、`changes_required`、`blocked`）、`findings[]`（新的或以 `matches` 指認的問題：`category`、`blocking` 由 controller 依分類計算、位置、依據、預期）、`dispositions[]`、`read_digests`（實際讀取的 spec／design／AC digests 與 `base_sha`、`head_sha`）、native session／message IDs、producer。`read_digests` 不等於目前版本集合 → 不 passed。
    - `dispositions[]` [R16]：assignment 快照中每一個未關閉的 finding 恰好一筆：`finding_id`、`status`（`verified_fixed`、`still_open`、`dispute_accepted`、`dispute_upheld`）、`head_sha`、證據（位置、測試或 result 的引用）、理由。
      - 只有 `verified_fixed` 或 `dispute_accepted`，且 `head_sha` 等於目前 H、附證據，才關閉該 finding（F04）；`clean` verdict 本身不關閉任何 finding。
      - 缺少任一個未關閉 finding 的 disposition → 該 finding 不關閉，而且 result 不完整：G2 不 passed，列出缺漏的 ID。`head_sha` 不是目前 H → 該筆不關閉。
      - 爭議覆核的 result 只含被爭議 finding 的 disposition（F08–F10）。
- **修正 result 的回應 [R16]**（Implementer，batch attempt）：`responses[]`，batch 內每個 finding ID 恰好一筆：`finding_id`、`kind`（`fix_submitted` 或 `disputed`）、commits、證據引用（綁定該 finding 與 batch 的 Red、H 上的 Green 等 result ID）、依據。缺任一 ID → 拒收並列出 missing IDs（F06），不解除任何 finding。
- **共同 result envelope [R16]**（T2.3 定義並驗證）：`schema_version`、`attempt_id`、role、producer、native IDs、`versions`（head、base、digests）、`body_kind`、`body`。T2.3 只驗 envelope 與身份；`body_kind` 為 `review`、`correction` 時，由 T5.1 在 `assignments.py` 的驗證表加入對應的 body 驗證函式（共用檔案表）。
- **修正 assignment 的快照 [R16]**：每個 finding 的完整內容（分類、位置、依據、預期、狀態）、先前的 review result ID 與其版本、先前的修正 commits 與證據引用，以及整份快照的 digest；派出後不隨 registry 改變（r10）。
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
  - 取得所有分頁；每個計入的 check 保存 name、app、workflow 路徑、run_id、run_attempt、run_number、event、head_sha、status／conclusion 與可讀的 check URL。缺可讀 URL → unknown [R15]。
  - **每個 run 內**：依 `run_attempt` 取最新的 attempt；較早的 attempt 被取代，不再要求。`run_id` 只作識別；不使用 `started_at`，所以 queued、沒有開始時間的較新 attempt 仍是最新。
  - **同一 H 有多個 PR run**（例如 close／reopen 後再跑）：依 `run_number` 列出，每個 run 的最新 attempt 都計入。全部 success 才算 success；任一 pending／queued → pending；任一失敗類 → 以該狀態不通過。因此，舊 run 在新 run 之後被重跑、結果是 failure 或 pending 時，G3 不會依新 run 的 success 通過。只看 H；舊 head 的 run 不計。
  - 識別或順序資訊缺失（缺 run 身份、`run_number` 或 `run_attempt`）、同一 workflow 出現重複的 `run_number` → unknown，不回退到舊的 success。
  - 只以 commit status 回報的必要 check → unknown（第一片不支援）。
  - **每個 job 的 tested SHA**：每個 job 上傳唯一名稱的產物 `tested-sha-<job>-<run_attempt>`，內容為 run_id、run_attempt、job 名稱、check 名稱、tested SHA。check-run 依 run_id／run_attempt／job 對到產物，並讀取產物內容逐欄比對（不只看名稱）；全部欄位相符且 SHA 等於 H 才計入；缺產物或任一欄不符 → unknown，不能 pass。這是保守規則：只重跑失敗 job 時，其他 job 可能沒有同一 attempt 的產物，需要改為重跑全部 jobs。controller 不新增任何 rerun 功能。
  - 具體的 check 集合：提案為 `unit-linux`（測試套件＋ruff、mypy、dist-smoke）與 `unit-macos`（測試套件），兩者都執行 §11 的測試政策；GitHub workflow 與 `workflow.yaml` 全文見 validation §6，待 D11 核准並記錄 `policy_change` [R15；R16]。
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
  - 之後再做一次新的 `purpose=pass` 觀察，結果一致：`observe pr --purpose pass` 與 `observe ci --purpose pass`，兩者的 seq 都晚於三 gates 的判定，head、base 與 check 結果都與判定時相同 [R15]。
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

## 10. 預算與 timeout（D13、D47）

- 4h active 以時間區間聯集計算，換 session 也不重置。
- 到期的 stop 優先於其他 blocker；已 prepared 的 stop 執行同一個 op；stop 讀回用盡 → 等人。
- 協調者離線的時間，在恢復時計入並記錄超出量，然後 Blocked。
- unknown 不等於已停止。
- **Active 區間的定義 [R15；R16 補證據命令；R17 調整擁有者]**：狀態中的 `activities[]` 每筆有種類、開始與結束時間，由擁有該活動的 task 寫入。T2.3 建立 `budget.py` 的兩個純函式：`active_used(state, now)`（區間聯集；尚未結束的活動計到 `now`）與 `remaining(state, now)`（核准上限加上已生效的 `active` 延長，減去已用）；之後的 task 只呼叫、不改語意。T7.1 延伸到期 stop、角色 timeout 與延長的效果。以下活動從開始到確認結束的區間取聯集：
  - worker attempt：`agent_start` 進入 prepared → §6 的 writer 結束證據成立（T2.3）；
  - review attempt：同上（T2.3）；
  - 證據命令：`evidence red`／`evidence green` 的子程序開始 → 結束或到限終止（T3.1，§7）；
  - CI 等待：`push` 讀回為 succeeded 後的第一次 `observe ci` → 全部必要 check 終態或逾時（開始由 T6.1 寫入；逾時判定由 T7.1）。
  
  狀態為 Blocked、awaiting_approval、acceptance pending，且沒有未結束的活動時，不計時。恢復時仍未結束、結束時間無法確認的活動，從它的開始計到恢復時的觀察時間（D47）。
- **角色 timeout [R15 提案，待 D11]**：每個 attempt 或等待視窗從開始起算的牆鐘時間，值在 `workflow.yaml` `timeouts`：

  | 對象 | 提案值 | 到限路徑 |
  | --- | --- | --- |
  | worker attempt | 45 分鐘 | `safety` 發出該 attempt 的 `write stop` → process-info 讀回（最多 3 次，間隔 10 秒）→ 確認停止後 attempt 記為 `timed_out`。同一單位（task 或 batch）可派新的 attempt，最多額外 2 次（沿用 D13 的每項操作額外重試 2 次；不計修正輪；新 attempt 要有自己的原始 Red，§7）。第 3 次逾時 → Blocked（`attempt_timeout_exhausted:<unit>`）。stop 無法確認 → Blocked，不派新 attempt |
  | review attempt | 30 分鐘 | 同上；G2 在此期間維持 pending，逾時用盡 → G2 unknown 並 Blocked |
  | CI 等待 | 30 分鐘 | 仍有必要 check 未到終態（含 `mergeable=null` 未算出）→ G3 unknown（`ci_timeout`）並 Blocked。controller 沒有 rerun 功能；人在 GitHub 處理後，以 `decide budget_extension --target ci_wait:<H>` 給一次新的 30 分鐘視窗 |

  - 理由：45／30／30 是 D45-02 起沿用的候選。第一片的 task 依 writing-plans 切成單一 TDD 單位，45 分鐘足夠一次 Red→Green；review 讀完整 diff 與契約約需 10–20 分鐘；CI 的兩個 job（`unit-linux` 另含 ruff、mypy、dist-smoke）估計各在 10 分鐘內完成，30 分鐘涵蓋 runner 排隊。這些時間都是估計，以實際執行為準 [R17]。三者都在 4h active 內計入，最壞情況（worker 3 次逾時）約 135 分鐘，仍留下 review、CI 與一輪修正的時間。
- **人工延長（`decide budget_extension`）[R15；R16 補效果規則]**：每次只針對一個目標並附理由：`active:<分鐘>`、`rounds:+1`、`attempts:<unit>:+1`、`ci_wait:<H>`。不重置其他計數，也不改 `workflow.yaml`（改政策仍需 `policy_change`）。
  - 效果以 decision ID 冪等：同一筆 decision 在重送、replay 或 restart 後只生效一次。
  - 延長只放寬該目標的上限，不解除 writer unknown、stop 未確認、policy unknown 等其他 blockers；這些仍依原規則處理。
  - 效果的擁有者：`active`、`attempts`、`ci_wait` 由 T7.1；`rounds` 由 T5.1（修正輪數的判定所在）。

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
- [OpenCode＋`gpt-6-astra` 尚未實際推論驗證] → R1 在任何真實派工之前驗證；不通過 → Blocked 交人，不自動換 runtime 或 model [R15]。
- [private repo 的 macOS runner 計費倍率較高] → `unit-macos` 預期每次數分鐘；若成本不可接受，D11 可改選不含 macOS 的集合（見 D11 確認包），不影響 G3 規則 [R15]。
