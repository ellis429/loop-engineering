# Design：implement-delivery-loop 薄 controller（D45 候選 design-01）

> **狀態：候選，不是 design ready。** 本文由指定 Opus 5.5 Implementer 依 D45 提出。review-01（changes_required）指出的 D45-R01–R04 已在 revision-01 修正。review-02 驗證了 R03–R06；R01／R02 的殘留已在 revision-02 修正。review-03 指出的最後兩個窄殘留已在 revision-03 修正，待原 Reviewer 覆核；其他章節仍是 draft_pending_sync，尚未 D11 開工確認，也不授權產品實作。三項政策差異（4h 離線行為、證據信任邊界、G3 required policy）列為 decision_required，見 [decisions-needed.md](decisions-needed.md)；受其影響的設計段落以「⛔DN-x」標示，其餘部分照常完成。
> 輸入基準：`input_manifest_sha256=486c7941e30830499350043060dd1ab6c44e3b39730c9933dc8eecf395cd749c`（工作目錄含未提交 D45 文件），另加 steering-01／steering-02 與 source-inventory.json。舊 D40 approval、S1 review 與 v3 design 只作歷史基準。

## Context

- 動機與範圍見 [proposal](/Users/johnson.chiang/workspace/loop-engineering/.delivery/bootstrap/herdr-design-d45-01/inputs/openspec/changes/implement-delivery-loop/proposal.md)（Why／What Changes）；方向依 D41–D45，責任對照依 [scope-reconciliation](/Users/johnson.chiang/workspace/loop-engineering/.delivery/bootstrap/herdr-design-d45-01/inputs/docs/harness/scope-reconciliation.md)。本文不重述，只記錄影響設計的現況與限制。
- **舊 S1 程式現況（依 src 證據）**：`src/delivery/` 共 21 模組、2,991 行。靜態 import 顯示 19 模組可由 `delivery.cli:main` 到達，但實際呼叫路徑更窄：
  - `cli.py` 只用 `loop.start_run`／`loop.Context`；`step()`／`run_until_idle()` 只在 `tests/test_loop.py` 呼叫。`cmd_resume`、`cmd_reconcile` 對外部工作一律回 exit 3（`_unavailable`，`cli.py:247,257`）。也就是主迴圈、outbox 派工、整合與 G2/G3 在產品入口從未被驅動，只由測試執行。
  - `resume.resume()` 沒有任何產品呼叫者（inventory `not_reached_by_import`）。
  - 17 項 blocking findings 的根因分布於 `loop.py`、`outbox.py`、`store.py`、`authority.py`、`decisions.py`、`gates.py`、`findings.py`（逐項位置見 coverage.json（候選尚未產出：`coverage.json`） 的 `src_evidence`）。
- **新工作區（steering-02，使用者已確認）**：「要沿用的就包進 new worktree or dir 不要混了」。`/Users/johnson.chiang/workspace/loop-engineering-thin` 已由協作者建立，目前只有 README 與空 `docs/design-candidate`，不是 Git worktree 或 repo。正式規格仍以 `loop-engineering` 為權威。
- **H0 已驗能力（只引用這些）**，來源 [herdr-setup](/Users/johnson.chiang/workspace/loop-engineering/.delivery/bootstrap/herdr-design-d45-01/inputs/docs/research/2026-09-27/herdr-setup.md) 與其 JSON 證據：
  - Herdr 0.9.1、protocol 22；以明確 `--session` 操作具名 server，不依賴焦點。
  - `worktree create --branch --base --path` 回傳 JSON（含 `root_pane.pane_id`、`worktree.branch`）；`workspace close` 後 worktree 仍在，`worktree open` 重開時 pane ID 改變（`w2:p1`→`w3:p1`），舊 ID 查回 `pane_not_found`。
  - `pane wait-output --timeout` 逾時回 exit 1、`error.code=timeout`；`pane process-info` 可讀前景程序。
  - 對普通程序 `send-keys ctrl+c` 後 process-info 回到 shell、OS 查無原 PID。**Claude Code 例外**：sonnet 證據最後一次 `send-keys ctrl+c ctrl+c` 後 process-info 仍列出 `claude` PID 16747，之後直接 `server stop`；因此「送出按鍵」不等於停止，停止必須以 process-info 確認，確認不了就 Blocked。
  - `agent start --kind opencode|claude --pane … -- <runtime argv>` 可指定 model 與 native session（OpenCode `--session <id>` 明確續跑；Claude Code `--session-id <uuid>` 由呼叫端指定）。
  - `agent prompt --wait` 在 runtime 失敗時仍回 `agent_status=done`（OpenCode Vertex `invalid_grant`、Claude Code `ECONNREFUSED`），lifecycle 不是品質或完成證據。
  - Native 紀錄可讀回實際 model：OpenCode assistant message `providerID/modelID=openai/gpt-6-luna`；Claude Code transcript `message.model=claude-sonnet-5`。
  - **未驗證**：integration hook 回報 native ID／自動 restore、推論中取消、Reviewer 權限、正式 skills profile（H0 的 `--pure`／`--safe-mode` 只為 probe）、真實 GitHub／CI、完整 loop、公司 OpenCode-only 環境。

## Goals / Non-Goals

**Goals:**
1. 同一 feature 只有一份可讀現行狀態、一個協調者、一份預算；controller 每次 CLI 呼叫核對→更新→返回，不常駐。
2. 外部效果（Herdr 派工、git 整合、GitHub 發布）一律「先登記、單次執行、讀回收斂」；結果不明就停止並交人，不重放許可。
3. 保留 88 個 AC 的品質語意：三 gates、版本失效、歷史 Red＋目前 Green、finding 權威、有界修正、單一 writer、去重。
4. 以乾淨重建工作區交付**唯一一套** CLI／狀態／gate／協調入口；舊程式只經「來源提取契約」逐項帶入，舊平台程式與專屬測試不進新樹。
5. 17 項 S1 findings 都有新程式路徑與可重現的回歸測試；移除舊機制不算關閉。

**Non-Goals:**
- 不自建 OS sandbox、credential broker、通用程序 supervisor、事件重放平台、跨主機 ownership 或全面自動恢復（D41）。
- 不引入第二個外層 loop 或第三方 orchestrator 狀態機（D45）；不把平台責任換名藏進 transport helper（helper 只做固定 argv＋單次呼叫＋解析）。
- 不自動 merge／close／release／deploy（D03）；不在背景呼叫 user-only skills（D28）。
- 不宣稱抵抗有同等主機權限者的整套偽造（⛔DN-2 決定可接受程度）。
- 不處理 Q-STACK、Q-DEMO-PEOPLE（沿用待決，不阻擋單 feature 切片）；CIT 依 D29 暫緩。

## Decisions

### 1. 乾淨重建於隔離 worktree，選擇性提取舊規則

**方案比較（依 src 證據）**

| 評估項 | A：沿舊架構改造（原樹逐步修） | B：隔離工作區重建主流程／CLI／狀態契約，提取已覆核規則（**採用**） |
| --- | --- | --- |
| 需要替換的核心 | `loop.py` 616 行是單一大迴圈，混合 clone 派工、outbox session 分段、整合、Red replay（直接執行 worker 的 `rec["argv"]`，R01，`loop.py:233`）、Green、N/A、PR、reread 與修正。改為 Herdr agent 模型需重寫其大部分 | 新 `engine.py` 只算「下一個允許動作」，外部效果移到 tools；不背舊迴圈的耦合 |
| 派工模型 | `outbox.RuntimePort` 假設 `create_session/send_prompt/list_messages`（OpenCode HTTP 形），與 Herdr `agent start/prompt/get/read` 不同；session create 遇 unknown 會遞迴重建（R02，`outbox.py:163`） | 每個 Herdr 呼叫一個 operation、一次嘗試、讀回收斂 |
| 權威狀態 | per-run `run.json`＋主機層 `authority.json`＋`project.json` 檢視；預算以 run 保存、加總只在 authority 查詢，實際派工 guard 只看本 run（`loop.py:139-140`，R08） | feature 單檔 authority，epoch 取代 run，預算只有一份 |
| 需移除的平台程式 | `sandbox.py`、`outbox` 的 runtime 分段、`authority` 的 run lineage、`events.py`、`resume.py`、`cli` 的 S2 佔位命令，以及 `tests/os/*`、`test_loop.py`、`test_dispatch_recovery.py`、`test_resume.py` 等專屬測試（清單見 cleanup-map） | 不帶入；歷史在 Git／PR #2／checkpoint |
| 可沿用的規則 | `gates.py`、`versions.py`、`findings.py`、`correction.py`、`budget.py`、`results.py` 的識別核對、`runner.py` 的 snapshot、`store.py` 的原子寫入，合計約 1,050 行，但其中 R06/R13–R17 需修 | 相同候選，經缺陷覆核＋新測試逐項提取（見 cleanup-map 的提取契約） |
| 中途狀態 | 替換期間新舊入口、兩種狀態 schema 與兩套測試並存，容易留下只為舊測試存在的程式（steering-01 的擔憂） | 新樹從第一個 commit 就只有新入口；沒有 legacy／v2 並存 |
| 估計工作量（粗估，非量測） | 修 17 findings＋改派工模型＋刪平台碼＋重寫約 12 個測試檔；約等於重寫主流程，再加遷移與清理成本 | 新寫 engine／ops／claim／store／cli／tools 約 1,100–1,400 行＋提取約 900 行（含修正）＋新測試；沒有遷移與雙軌清理成本 |

**建議 B**，且 steering-02 已確認隔離工作區，故不再建議原樹逐步替換。理由：需替換部分（約 1,900 行：loop、cli、outbox、authority、events、sandbox、resume、controller 大半、decisions 大半、publication、integration、retro）大於可沿用部分，且可沿用部分本身也有 7 項 findings 要修；改造路徑的每一步都得同時維持舊測試綠燈，容易造成死碼。

**工作區接回同一 repo 的方案**（開工前由協作者／使用者確認執行；本輪不建立 repo、不動正式 source）：

| 方案 | 做法 | 評估 |
| --- | --- | --- |
| **W1（建議）** 同 repo 新 branch 的 git worktree | 先在 `loop-engineering` 提交已採用的 D45 文件與新版 OpenSpec artifacts（commit `B`）。將 `loop-engineering-thin` 現有 README／`docs/design-candidate` 移到旁邊保存（worktree 目的地需為空），執行 `git worktree add -b delivery/thin-controller <path> B`，再放回 candidate 文件。新 branch 第一個 commit 只做「移除 `src/delivery/`、`tests/`、舊 `pyproject` 的 delivery 設定，加 `docs/implementation/removed-s1.md` 指向 `4ce1110`／`5d334d5`／PR #2」 | 同一 repo 歷史、同一 PR 流程；新樹沒有舊程式；worktree 共用 object store，便於 Red snapshot 與提取時引用來源 commit |
| W2 孤兒 branch（`git worktree add --orphan`） | 空樹起步 | 與 main 無共同歷史，之後 PR 需 `--allow-unrelated-histories`，也失去規格文件同 branch 追蹤；不建議 |
| W3 新獨立 repo／純目錄 | `git init` 或保持無版控 | 違反「不擅自建 repo」；純目錄無法產生 G1 所需的 commit／snapshot 證據；不建議 |

W1 的規則：
- 正式 specs／proposal／design／tasks 仍只在 `openspec/changes/implement-delivery-loop/` 一處；thin branch 從 commit `B` 起帶著同一路徑。規格修訂只在一條 branch 上做（先在 `loop-engineering` 主 worktree 修訂並 commit，thin branch 再 rebase／merge），不在兩個 worktree 同時改規格。
- 新 venv 只安裝新套件；不設 `PYTHONPATH` 指向舊 src，不以 editable 方式依賴舊套件；新套件改名 `loopctl`，並以測試確保 `import delivery` 失敗（防止誤載舊碼）。
- 不建立 `legacy/`、`v2/` 目錄；最終只有一套入口 `loopctl`。

### 2. 單一入口 `loopctl`：核心與工具分層

一個 console script `loopctl`（Python 3.12，唯一第三方依賴 PyYAML）。子命令分兩群：

| 群 | 模組 | 可做 | 不可做 |
| --- | --- | --- | --- |
| 核心（狀態與規則） | `refs`、`home`、`store`、`schema`、`claim`、`ops`、`assignments`、`evidence`、`versions`、`gates`、`findings`、`correction`、`decisions`、`budget`、`engine`、`status`、`api`、`cli` | 讀寫 feature 狀態、驗證、計算 gates／下一步 | 不 import `subprocess`、不呼叫 git／gh／herdr、不執行測試或結果中的 argv（R01） |
| 工具（窄外部接合） | `tools/herdr.py`、`tools/git.py`、`tools/gh.py`、`tools/evidence_run.py`、`tools/result_submit.py` | 取得已登記 operation、呼叫固定 argv 一次、存 receipt／readback，經 `api.begin`／`api.record` 更新狀態 | 不保存另一份 ledger、不自行重試、不判定 gate、不解讀需求 |

核心不得 import `loopctl.tools`；工具只經 `loopctl.api` 的公開函式改變狀態。這兩條 import 規則以 `tests/test_cleanliness.py` 的 AST 檢查固定。

**執行權只在一處消耗（D45-R01）**：orchestrate 只做 `prepare`，接著呼叫一個 `loopctl tool …` 命令。tool 命令分兩種模式：

- **執行／重試模式**（`tool … --op OP`）：用於所有已登記 operation 的首次執行，**包含唯讀 observation**（如 `gh_observe`、`herdr observe`），以及明確失敗後允許的重試。每次執行都由該 tool 在同一程序內呼叫 `api.begin` 消耗一次；拿到 `execute:true` 才做一次原操作，最後 `api.record`。重試次數照常計入該 op 的額度（§6）。
- **讀回模式**（`tool … reconcile --op OP`）：只用於已經 begin、狀態為 `in_flight`／`outcome_unknown` 的既有 op，讀回該次 attempt 的外部實況，不重發原操作。**不呼叫 begin**，不消耗也不重放執行許可，只做唯讀查詢（marker、handle、process-info、ref、ls-remote），再經 `api.record_readback` 保存讀回結果，由 API 依 §6 轉為 succeeded、failed(proven_absent) 或 outcome_unknown。

orchestrate 不自行呼叫 begin；`begin`／`record`／`record_readback` 也不提供獨立 CLI 命令。這項行為以公開 CLI 驗證，有兩個案例：
1. 兩個 tool 程序同時對同一 op 執行，恰好一個呼叫外部，另一個回 `execute:false`。
2. 外部效果已完成但 receipt 遺失時，reconcile 能以讀回收斂，且外部副作用呼叫次數不增加。

AST 檢查無法證明這兩點。

### 3. Feature 單一 authority 與目錄配置（缺口 2）

```text
$LOOPCTL_HOME（預設 ~/.local/state/loopctl；不在任何 worker worktree 內）
  features/<feature_id>/
    feature.json            # 唯一現行狀態（含預算、findings、operations、gates）
    lock                    # 每次 CLI 呼叫的短命 flock
    history/<rev:08d>.json  # 每個 revision 的完整副本，write-once
    history/orphans/        # 中斷時未生效的 revision（保留診斷）
    objects/<sha256>        # content-addressed：assignment、result、evidence、receipt、observation、raw logs
    inbox/<attempt_id>/     # worker 唯一可寫的結果與證據投遞位置
    verify/                 # coordinator 的 Green／replay 暫用 checkout（用後移除）
    review/<attempt_id>/    # Reviewer 的獨立 clone（保留）
<repo>/workflow.yaml        # 版控 policy（無 credential）
<repo>/docs/validation/<feature>/  # 可分享證據索引（版控）
```

- `feature_id = sha256("<repo_node_id>\n<feature_key>")`。`repo_node_id` 用 GitHub node ID（H2 以 `gh api` 取得）；H1 由 `init-feature --repo-id` 明確給定。只改 repo 名稱／路徑時更新 `repo.locator`，不產生新 feature。
- **Run 改為 epoch**：`feature.json.epochs[]` 記錄每次開始／放棄；預算、finding、dispute 計數都在 feature 層，換 epoch、換 session、換 run ID 都讀同一欄位。`abandon_epoch` 只能由附停止／fencing 證據的人工 decision 觸發，新 epoch 繼承全部已用額度（R08、AC-D03、AC-D17、AC-F07）。
- 沒有 `project.json` 檢視副本；project 薄層（H3）只保存 feature_id＋revision 引用與人工接受紀錄，不保存 gate。

### 4. 提交協定：history-first、typed refs、手改偵測（R03、R04、R06；AC-D02、D09–D11）

`FeatureStore.commit(state, expect_revision)`，在持有 `lock` 時：
1. 讀現行 `feature.json`，確認 revision == `expect_revision`，且 bytes 與 `history/<rev>.json` 相同；否則 `RevisionConflict` 或 `ManualEditDetected`。
2. 新狀態帶 `revision=rev+1`、`prev_state_digest=sha256(舊 bytes)`、`transition={id, kind, op_id|decision_id|record_id}`。
3. 驗證新狀態引用的每個 **BlobRef**（`{"blob":"sha256:…"}` 物件）都已在 `objects/` 且 digest 相符。文件版本 digest 是字串欄位（`*_digest`），**不**被當成 blob 掃描（R06 根因：舊 `store._refs` 以 regex 把所有 `sha256:` 字串當 blob，`store.py:103-110`）。
4. 先寫 `history/<rev+1>.json`（tmp→fsync→`os.link` 不覆寫；若已存在不同 bytes，先移到 `history/orphans/` 再寫），fsync 目錄。
5. 再以 tmp→fsync→`os.replace` 更新 `feature.json`，fsync 目錄。

結果：
- 讀者只會看到完整舊版或新版（AC-D09）。「現行狀態已提交而歷史缺失」在此順序下不會發生；只可能留下未生效的 `rev+1` 歷史，load 時列為 `orphan_revision` 診斷，不生效（AC-D10、R04）。
- 同一 `transition.id` 在歷史中出現不同內容 → `IntegrityError`，Blocked（R03）。
- `load()`：缺檔 `StateMissing`、壞 JSON `StateCorrupt`、未知 `schema_version` `SchemaMismatch`、引用物件缺失或不符 `IntegrityError`、現行檔與同 revision 歷史不同 `ManualEditDetected`。這些一律 CLI exit 5，不建立空狀態、不重置預算（AC-D11）。
- 手改：`loopctl repair restore-committed` 由人執行，將現行檔恢復為 `history/<rev>.json` 並把被拒的內容存成物件、記一筆 `manual_edit_rejected`；gates 下次 `assess` 從證據重算，手改值永不當決策（AC-D02；可抵抗程度 ⛔DN-2）。

### 5. 協調者 claim：同 feature 唯一外層 loop（AC-O02、O19、D03）

- `loopctl claim --feature F --actor A` 在無 active 協調者時產生隨機 token，只輸出一次；`feature.json` 只存 `sha256(token)`。所有會改狀態的非人工命令（`prepare/begin/record/assess` 與 `tool *`）都需 `--token`，不符回 exit 4 `not_owner` 並列出現任協調者。
- 第二個 orchestrate session、Implementer 的 skill 或 Project Lead 沒有 token，只能 `inspect`／`status`。這防止意外的第二個外層 loop；**不**防止同 UID 程序讀取協調 session 環境變數等惡意行為（⛔DN-2）。
- 交接：人工 `decide handoff`（relinquish）把 claim 設為 `relinquished`，保存未完成 operations 與待辦；有 `in_flight`／`outcome_unknown` operation 時 handoff 仍可記錄，但新協調者 claim 後 next action 一律先處理這些 operation，不自動接管 worker。
- Project Lead 委派（AC-O18）：`decide delegate` 保存使用者授權來源與 task 範圍；engine 只在該範圍內對 Project Lead 顯示可提議的派工，實際 permit 仍由持 token 的協調者取得。

### 6. Operation：可重送的 prepare、只能消耗一次的 begin（缺口 1；R02、R05；AC-D12、D13、D16）

```text
prepared ──begin(第1個呼叫者)──> in_flight(attempt n) ──record succeeded──> succeeded
   ^                                   │ record failed(明確失敗) ──> failed ──begin（n<3）──> in_flight(n+1)
   │                                   │ record unknown／process 中斷未記錄
   │                                   v
   │                             outcome_unknown ──reconcile readback──> succeeded │ failed(proven_absent) │ blocked
   └─ prepare 重送：同 op_id、同 payload_digest 回傳同一筆；不同 digest → OpConflict
```

- `op_id` 由 `(kind, target_key)` 決定，例如 `op-prompt-T2.a1`，所以 `prepare` 可重送且無副作用。
- `begin` 在 lock 內把 `prepared|failed` 轉為 `in_flight` 並回 `{"execute": true, "attempt": n}`；對 `in_flight`、`outcome_unknown`、`succeeded`、`blocked` 一律回 `execute:false` 與原因。兩個 caller 不可能同時拿到 `execute:true`。`begin` 用於每個已登記 operation 的首次執行（含唯讀 observation）與允許的重試，唯一呼叫者是執行模式的 tool 命令（§2）。只有對既有 `in_flight`／`outcome_unknown` 的讀回不經 begin。
- 每個 `in_flight` attempt 恰好對應一次外部呼叫；工具不得在內部重試或遞迴（R02）。明確失敗才可再 `begin`，同一 operation 最多 3 次（初次＋2 次，D13），第 4 次 `begin` 回 `retries_exhausted` 並 Blocked（AC-D16）。
- 程序中斷使 operation 停在 `in_flight`：`inspect` 標為 `unreconciled`，next action 是 `reconcile`。讀回模式的工具不呼叫 begin，只做**讀回**、不重做，並經 `api.record_readback` 保存結果（§2）。以 marker／handle 查：查得 → `succeeded`；可證明不存在（例如 `herdr agent get <name>` 回 not found 且 `workspace list` 可讀）→ `failed(proven_absent)`，可在額度內重試；查不清 → `outcome_unknown` → Blocked，等 `decide resolve_operation`（`retry` 計一次額度／`abandon_attempt` 附停止或 fencing 證據）（AC-D13）。
- 分類：測試／review 失敗屬 correction，不能包裝成 infra retry（`budget.failure_route`，AC-D16）。

Operation 種類與讀回：

| kind | 外部呼叫（一次） | 讀回／收斂依據 |
| --- | --- | --- |
| `worktree_create` | `herdr worktree create` | `herdr worktree list`＋`git worktree list --porcelain`：路徑、branch、HEAD==T0、乾淨才收斂；存在但不符 → Blocked（R05） |
| `agent_start` | `herdr agent start <name> …` | `herdr agent get <name>`：pane、cwd、argv 相符 |
| `prompt` | `herdr agent prompt <name> <text>`（不用 `--wait`） | native 紀錄中含 marker 行的 user message（Claude transcript；OpenCode session messages）；查不到且無法證明未送達 → `outcome_unknown`，**不重送同一 session** |
| `stop` | `herdr agent send-keys <name> ctrl+c`（每個 attempt 只送一次） | 讀回模式以 `herdr pane process-info` 查：只剩 shell 才 `stopped_confirmed`。已送過 stop 就只讀回原 stop op，不重送。`failed` 只在已證明重送安全且仍有 infra 額度時重試同一 op。確認不了 → unconfirmed，attempt 維持 active 並 Blocked，不當成已停止。各狀態的完整規則見 §9 |
| `integrate` | `git update-ref <branch> A T0`（CAS） | 讀 ref：==A 收斂、==T0 可重做、其他 → Blocked |
| `evidence_green`／`evidence_replay` | `loopctl tool evidence run`（policy 命令） | 產物已在 `objects/` 即收斂 |
| `gh_observe` | `gh api` 讀取（完整分頁） | 讀取無副作用；失敗可重試 |
| `gh_pr_ensure`／`gh_publish_pr`／`gh_publish_issue` | 建立 PR／留言 | body marker `<!-- loopctl op=… feature=… result=… -->` 查全部分頁 |
| `push` | `git push --force-with-lease=<b>:<old>` | `git ls-remote` |

### 7. CLI 契約

所有命令 stdout 為一個 JSON 物件：`{"ok": bool, "revision": int|null, "result": {...}, "blocked": [...], "next_action": {...}|null, "safety_actions": [...]}`（`safety_actions` 見 §9）；人讀輸出只有 `status`。Exit code：0 成功；1 拒絕（驗證失敗、decision 無效、OpConflict）；2 用法錯誤；3 feature Blocked 或動作被 guard 拒絕；4 `not_owner`；5 狀態不可信。

| 命令 | 權限 | 效果 |
| --- | --- | --- |
| `init-feature --repo PATH --repo-id ID --feature KEY --issue REF --integration-branch B` | 人／協調者 | 建立 feature.json（phase `intake`）；已存在則拒絕，不覆蓋 |
| `claim --feature F --actor A` | 人／協調者 | 見 §5 |
| `inspect --feature F` | 任何人，唯讀 | 現行狀態摘要、未完成 operations、`next_action`、blockers |
| `status --feature F` | 任何人，唯讀 | 人讀摘要（AC-D01） |
| `register --kind plan|binding|policy --role R --file P --producer JSON` | token | 保存原生 artifact 的 locator＋digest＋內容物件；plan 另存 producer／calibration provenance（R07） |
| `prepare --action ACTION_ID` | token | 把 `next_action` 轉成 operation（可重送） |
| （無 `begin`／`record`／`record_readback` 命令） | — | 只以 `loopctl.api` 函式存在：`begin`＋`record` 由執行模式的 `tool … --op` 呼叫，`record_readback` 由讀回模式的 `tool … reconcile --op` 呼叫（§2、§6） |
| `record-result --attempt A --file P` | token | 從 inbox 匯入 result 與 evidence（去重、衝突、身份核對） |
| `assess [--pass-observation OBS]` | token | 依證據重算 gates；Pass 需新觀察（§11） |
| `decide --kind K --actor A --source S --reason R --subject JSON` | 人（`actor_kind=human`） | 寫入人工 decision（⛔DN-2 決定是否需要額外確認） |
| `repair restore-committed` | 人 | §4 |
| `tool herdr worktree|start|prompt|observe|stop --op OP` / `tool herdr reconcile --op OP` | token | 前者為執行模式（經 begin）；後者為讀回模式（不經 begin）；§2、§14 |
| `tool git integrate|push --op OP` / `tool git reconcile --op OP` | token | 同上；§2、§16 |
| `tool evidence run --op OP` / `tool evidence red --assignment P --command-id ID` | coordinator 用 token；worker 用後者（無 token，只寫自己的 inbox） | §10 |
| `tool result submit --inbox P --file F` | worker | write-once 投遞（沿用舊 `cmd_submit` 行為） |
| `tool gh observe|pr-ensure|publish --op OP` / `tool gh reconcile --op OP` | token | 同上；§2、§15 |

### 8. 資料契約（schema_version=1）

`feature.json` 頂層（人讀優先；`next_action` 是衍生值，僅為可讀性而存）：

```json
{
  "schema_version": 1, "feature_id": "f7c1…", "revision": 12,
  "prev_state_digest": "sha256:…", "transition": {"id": "t-12", "kind": "record_result", "op_id": "op-prompt-T2.a1"},
  "repo": {"node_id": "R_kgDO…", "locator": "yschiang/loop-engineering", "path": "/…/loop-engineering-thin"},
  "feature_key": "issue-7", "issue": "yschiang/loop-engineering#7", "controller_version": "loopctl 0.1.0",
  "coordinator": {"actor": "orchestrate@opus", "token_digest": "sha256:…", "status": "active", "claimed_at": "…"},
  "epochs": [{"epoch": 1, "started_at": "…", "ended_at": null, "end_reason": null}],
  "phase": "checking", "next_action": {"id": "observe:ci:vk:…", "kind": "gh_observe"},
  "plan": {"digest": "sha256:…", "blob": {"blob": "sha256:…"}, "producer": {"role": "implementer", "actor": "…"},
           "calibrated_from": [{"role": "project_lead", "digest": "sha256:…"}],
           "tasks": [{"task_id": "2.1", "ac_ids": ["AC-G04"], "scope": ["src/loopctl/evidence.py"], "change_class": "behavior", "depends_on": []}]},
  "approval": {"decision_id": "DEC-…", "plan_digest": "sha256:…"},
  "bindings": {"feature_spec": {"locator": "openspec/…/spec.md", "content_digest": "sha256:…", "blob": {"blob": "sha256:…"}, "adopted_at": "…", "adopted_via": "register"}},
  "candidates": {}, "pending_scope": [],
  "versions": {"repo_id": "R_kgDO…", "pr_number": 9, "head_sha": "…", "base_ref": "main", "base_tip": "…", "merge_base": "…",
               "bindings": {"feature_spec": "sha256:…"}, "skills": {"superpowers:test-driven-development": "sha256:…"}, "controller_version": "loopctl 0.1.0"},
  "version_key": "vk:…",
  "tasks": {"2.1": {"status": "integrated", "attempts": ["2.1.a1"], "lease": "2.1.a1"}},
  "attempts": {"2.1.a1": {"role": "implementer", "assignment": {"blob": "sha256:…"}, "worktree": {"path": "…", "branch": "le/f7c1/2.1.a1", "t0": "…"},
                          "handles": {"herdr_session": "le-main", "workspace": "w2", "pane": "w2:p1", "agent_name": "le-f7c1-2.1.a1", "native_session_id": "…"},
                          "deadline_at": "…", "result": {"blob": "sha256:…"}, "status": "result_imported"}},
  "operations": {"op-prompt-2.1.a1": {"kind": "prompt", "state": "succeeded", "payload_digest": "sha256:…", "attempts": [{"n": 1, "begun_at": "…", "receipt": {"blob": "sha256:…"}}]}},
  "gates": {"g1": {"status": "passed", "version_key": "vk:…", "reasons": [], "evidence": [{"blob": "sha256:…"}]}, "g2": {}, "g3": {}},
  "findings": {"seq": 3, "items": {}}, "batches": [], "disputes": {},
  "budget": {"activities": {}, "unknown_intervals": [], "correction_rounds_used": 1, "extensions": [], "last_touch_at": "…", "overrun": null},
  "observations": {}, "pass": {"current": null, "history": []},
  "acceptance": {"history": []}, "decisions": [], "blockers": [], "waits": [], "dependencies": [],
  "integration": {"branch": "delivery/issue-7", "tip": "…", "log": [{"task_id": "2.1", "attempt_id": "2.1.a1", "from": "T0", "to": "A", "op_id": "op-integrate-2.1.a1"}]}
}
```

| 交接物 | 必要欄位（在 contracts 既有語意上的具體化） |
| --- | --- |
| Assignment | `schema_version`、`feature_id`、`epoch`、`task_id`、`attempt_id`、`role`、`profile`（transport=herdr、runtime、runtime_version、provider、requested_model、permission_profile_digest）、`repo`、`worktree`（path、branch、t0）、`issue`／`pr`、`versions`（version_key＋全部 binding digests＋skills）、`scope.paths`、`depends_on`、`ac_ids`、`commands`（policy 命令 id→argv，含 policy digest）、`inbox`、`result_path`、`deadline_at`；修正／覆核另含 `findings`（完整 finding 快照）、`prior_review`、`fix_evidence`（R12） |
| Result | 同組 IDs、`execution_status`（succeeded／failed／blocked）與 `verdict`（review 才有）分開、`observed`（cwd、head、base、read_digests）、`changed_paths`、`evidence`（inbox 相對路徑）、`findings`／`responses`／`rulings`／`closures`、`open_questions`、`producer.declared`（worker 自述，僅供說明） |
| Evidence | `kind`（red／green／regression／replay_check／base_recheck／doc_check）、`task_id`、`attempt_id`、`command_id`、`argv`、`policy_digest`、`cwd`、`started_at`／`ended_at`、`exit_code`、`status`、`failing_ids`／`passing_ids`、`stdout_digest`／`stderr_digest`（raw 存 objects）、`snapshot`（commit、tree、parent、ref、included）、`producer`（`tool=loopctl-evidence`、tool version、`invoked_by`＝worker|coordinator、attempt handles） |
| Receipt | `op_id`、attempt n、argv、exit code、stdout／stderr 物件、解析後 handles、`observed_model`（從 native 紀錄讀回）、時間 |
| Observation | `observation_id`、`after_revision`、`head_sha`、`base_ref`、`base_tip`、`merge_base`、`pr_number`、重讀的 binding digests、`rules`（`readable`／`forbidden`／`error`＋required 集合）、`checks`（全部分頁，含 app、attempt、SHA、status、conclusion、URL）、`merge_mapping`、raw 回應物件 |
| Decision | `decision_id`、`kind`、`actor`、`actor_kind=human`、`source`、`reason`、`created_at`、`subject`（含指向的版本／finding／operation／plan digest）、`impact` |
| Finding | `id`（`F-0001`）、`source`、`category`、`severity`、`blocking`、`location`、`problem`、`basis`、`expected`、`status`、`fix_commits`、`rechecks`、`failed_rechecks`、`reopen_count`、`closure`、`closure_history`、`lineage`、`history` |

### 9. Phase 與下一步引擎

`engine.next_action(state, now) -> Action` 是純函式。每次回應除了 `next_action`，也一律附上 `safety_actions` 清單，內容是全部到期 stop（新 prepare 或執行已 prepared 的同一 op）、stop 讀回與 in-flight 讀回，不論 feature 是否 Blocked。`api.prepare` 只接受 `next_action.id`，或 `safety_actions` 裡的 action id，因此 orchestrate 不能跳過 guard。

主路徑沿 contracts：`intake → planning → awaiting_approval → implementing → validating → checking → ready_for_acceptance`，`checking → correcting → validating`，任一階段可進 `blocked`。

判斷順序（D45-R02）：到期停止優先；安全收尾動作不受無關 blocker 或無關 in-flight op 阻擋，blocker 只擋正常工作。
1. **到期 stop 優先**：某個已知 active attempt 已到 `deadline_at`，或預算已用盡時，不論 feature 是否 Blocked、也不論是否有不相關的 in-flight op：
   每個 attempt 只有一個 stop op（固定 `op_id`），不會另開第二個。依該 op 的狀態決定動作：
   - 沒有 stop op → `prepare` 一次該 attempt 的 stop。
   - `prepared` → 以執行模式執行**同一** stop op：經 begin，只送一次。只有 op 存在不代表已送出；是否可能已送出，看 begin 之後的狀態。
   - `in_flight`／`outcome_unknown` → 只以 process-info 讀回**同一** op，不重送。
   - `failed` → 只有同時滿足兩個條件時，才以執行模式重試同一 op：已證明重送安全（例如讀回證明按鍵未送達），且該 op 仍有剩餘 infra 額度（§6）。否則 Blocked 交人。
   - `succeeded` → 必須附停止證據（process-info 只剩 shell）才關閉 activity。若後續觀察矛盾（例如程序仍在），就 Blocked 交人核對，不重開 stop。

   停止確認不了的 attempt 維持 active 並列為 blocker，unknown 不當成 stopped；只有確認停止的 attempt 會關閉 activity。

   **驗證案例（prepare 後 crash 再 resume）**：
   1. 以 fake Herdr 建立一個 active attempt，時鐘推到超過 `deadline_at`，另保留一個不相關的 in-flight op。
   2. `inspect` 給出 stop，執行 `prepare`，得到 stop op 狀態為 `prepared`。
   3. 在呼叫 tool 前中斷協調程序。
   4. 重新執行 `inspect`，檢查：
      - next action 是執行**同一** stop `op_id`，不是讀回，也沒有新 stop op；
      - 它排在不相關 in-flight op 的讀回之前。
   5. 執行 tool，檢查：
      - fake Herdr 的 `send-keys` 呼叫次數恰為 1；
      - 讀回確認停止後 activity 關閉。
   6. 反例：讀回顯示程序仍在時，檢查：
      - `send-keys` 仍是 1 次；
      - attempt 維持 active；
      - feature 為 Blocked。
2. 其他 `in_flight` 且未記錄結果的 operation → `reconcile <op>`，只做讀回、不重做。
3. 有 `blockers` 時，next action 為 `blocked`，內容列出原因、證據、需誰決定、可選 decision kinds 與 `resume_to`。1、2 類動作仍照常列在 `safety_actions`（例如 CI policy unknown 使 feature Blocked，但 reviewer 仍在執行，到 deadline 仍可 stop）。預算用盡本身也記為 blocker `active_budget_exhausted`（⛔DN-1 只決定離線部分）。
4. 以上都不成立時，依 phase 決定：
   - `intake`／`planning`：`wait_human`（準備 design＋plan 並 `register`）。
   - `awaiting_approval`：`wait_human approve_plan`，顯示待確認 plan digest；沉默、timeout、agent 同意不算（AC-O05）。
   - `implementing`：依 plan 順序、並行度 1：`worktree_create` → `agent_start` → `prompt` → `wait_result` → `record-result` → `integrate` → 下一個 task。任一 task dispatch 前檢查 claim、approval 綁定目前 plan digest、plan producer 為 implementer、ticket、skills pin、依賴（D27）、預算、跨 feature 影響標記。
   - `validating`：N/A eligibility review（若有）→ `evidence_green`（整合 head，coordinator 執行）→ `evidence_replay`（每個 worker Red）→ `assess g1` → `push` → `gh_pr_ensure`。
   - `checking`：正式 review（G1 passed 後才給）與 `gh_observe`（CI）並行；兩者都到終態才 `assess`。若三 gates 同 key 通過，依序執行：
     1. 先處理 review 匯入時已登記、尚未 succeeded 的 `gh_publish_pr`；
     2. 再處理依賴其 URL 的 `gh_publish_issue`；
     3. 兩者都 succeeded 後，才給 `gh_observe(purpose=pass)`，接著 `assess --pass-observation`（D45-R04）。

     發布失敗或 unknown 時，只對原 operation 重試或讀回，不重做 review，也不另建佇列；到上限就 Blocked。gates 未全過時開 correction batch；待處理的發布 operation 與派修並列在 next action 中，不會被略過（AC-F13、F14）。
   - `correcting`：fix unit 派工（同 implementing 流程），整合後回 `validating`。
   - `ready_for_acceptance`：`wait_human accept|return`；orchestrate 可提出 `gh_observe` 以發現 Pass 後 push（AC-G18）。

### 10. 版本與證據核對（缺口 4；R01、R13；AC-G04–G08、G16、G17）

- **VersionSet／依賴矩陣**：提取舊 `versions.py` 的 binding／observation 分離、`version_key`、「欄位×gate」矩陣與推導規則（R-unaffected／R-base／R-reevaluate／R-reobserve），G3 一律 R-reobserve。提取前以新測試覆核矩陣完整性與 S1 驗證紀錄中的 skills×G3 歧義（採 R-reobserve）。
- **命令只來自 policy**：`workflow.yaml` 的 `g1.commands` 以 `command_id` 定義 argv；assignment 帶 policy digest。`tool evidence red` 只接受 `--command-id`，拒絕任意 argv。Controller 核對 evidence 的 `argv` 與 policy 定義完全相同；Red replay 與 Green 由 coordinator 以 policy argv 在 `verify/` checkout 執行，從不執行 result 中的 argv（R01；舊 `loop._verify_red` 以 `rec["argv"]` 重跑，`loop.py:233`）。
- **Red 捕捉**：worker 在自己的 worktree 執行 `loopctl tool evidence red`，沿用舊 `runner.snapshot_worktree` 的 baseline＋overlay 方法（temp index、scope／exclude、拒絕時不寫物件、drift 偵測），寫入 `inbox/<attempt>/evidence/`。Snapshot commit 與 ref `refs/le/red/<task>/<attempt>/<n>` 寫在共用 object store。
- **Red 有效性（每項獨立拒絕，R13）**：raw stdout／stderr 物件 digest 相符；`exit_code==1` 且 junit 有 failure、無 collection error（`status=test_failed` 必須與 exit／junit 一致）；`task_id`／`attempt_id` 與該 attempt 相同；`command_id`、`argv`、`policy_digest` 相符；`producer.tool=loopctl-evidence`；snapshot tree 相對 parent 的變更 ⊆ scope 且無 exclude；parent 是整合 head 的祖先；failing IDs 在 H 的 Green 中存在且通過；coordinator replay 以相同 IDs 失敗。任一不成立 → invalid 並列出該項，Green 正確也不能掩蓋。
- **可信程度**：以上可證明 snapshot 是 lineage 上真實存在、以核准命令失敗的狀態；不能證明 worker 在 session 中「先寫測試」的時間順序。補強：assignment 要求 worker 在實作前執行 Red，receipt 保存 native session ID；Reviewer 檢查 native transcript 中 Red 工具呼叫早於實作檔修改（G2 checklist）。是否足夠 ⛔DN-2。
- **Green／regression**：只採 coordinator 在整合 head 的 `verify/` checkout 執行的 policy 命令（`invoked_by=coordinator`）；worker 報告的 green 不採用（AC-G08）。
- **晚到的工作結果（D45-R03）**：assignment 產生的 result、review 或 evidence，若其 version_key 不是現行 key，或 attempt 不是現行 lease，就只存歷史，不能授權現行 gates，也不影響 findings 與 budget（AC-G16、AC-D04 fencing）。
- **新的外部觀察不是「晚到結果」**：observation 表示外部現況。每筆都以其 prepare 時的 `after_revision` 排序，這是 feature.json 既有的 revision 序，不另建 authority。規則如下：
  - 比已記錄的最新 observation 更新 → 更新觀察到的 head／base／merge_base／binding 事實。
  - 若事實與現行 VersionSet 不同 → 依 §10 矩陣產生新 key：失效相關 gates 與 `pass.current`，並回 validating／checking／awaiting_approval（AC-G17、G18、D15）。
  - 只有已被更晚 observation 取代者（`after_revision` 較小，且較新者已記錄）才只存歷史、不生效。

### 11. Gates、Pass 與 Pass 前觀察（缺口 5；R14、R15、R17；AC-G01–G03、G09–G15、G18）

- **G1**：提取舊 `gates.evaluate_g1`，改兩點：輸入為**核准 plan 的全部 tasks**（不再只取整合 log 有變更者，R11 根因 `loop.py:396-399`）；Red 驗證改用 §10 的完整檢查。N/A：`change_class=na_requested` 只有在獨立 eligibility 通過 §11 的獨立性檢查後才免除 Red／Green（R15：舊 `_na_eligibility` 只比 diff digest，`loop.py:381`）。
- **獨立性檢查（G2 與 N/A 共用 `independent_review_ok`）**：由本 feature 協調者取得 permit 的 reviewer attempt；`observed_model`（native 讀回）== 核准 reviewer model；native session 與所有 implementer sessions 不同、非其子 session；Reviewer permission profile 有已驗證的能力報告（H2 真實 probe，見 §14），receipt 中的 profile digest 相符；result 回報的 `read_digests` 等於現行 VersionSet 全部 binding digests。
- **G2**：verdict=`clean`＋無未解 blocking finding＋獨立性通過 → passed；`changes_required` → failed；`blocked` → unknown、feature Blocked、不開 round（AC-G03）。Implementer subagent 或未經 permit 的 review 永不匯入 G2（AC-G12、O02）。
- **G3**：提取 `evaluate_g3`，修正：
  - 回傳 `route`：`fix`（真實 check failure）、`wait`（pending）、`policy_unknown`（rules 不可讀、集合不一致、例外未核准）、`infra`（查詢失敗）。只有 `fix` 可進 correction batch；`policy_unknown` → Blocked，不增 round（R14：舊實作 unknown 也被視為終態進 batch，`correction.py:11,18`＋`loop.py:549-550`）。
  - `allow_non_success` 每筆必須是 `{name, conclusions ⊆ {skipped, neutral}, decision_id}`，且 decision 存在於 `decisions` 且 kind=`policy_change`；含其他 conclusion 或無 decision → `policy_invalid`，G3 unknown＋Blocked（R17：舊實作接受任意 conclusion，`gates.py:170-175`）。
  - Rules 讀取 403 → `rules.status=forbidden` → `policy_unknown`（⛔DN-3 決定是否允許經人工 decision 宣告的集合）。
- **Pass**（寫入 `pass.current` 的唯一路徑）：三 gates current assessment 皆 passed 且同一 `version_key`；無 open blocking finding；必要發布（PR review、issue 摘要）operation 已 succeeded；無 `in_flight`／`outcome_unknown` operation；且提供一筆 `purpose=pass` 的 observation，其 `after_revision` 大於三個 gate assessment 的 revision，其重讀的 version_key 等於現行 key，且 G3 以**這筆** observation 重算仍 passed。不以時間窗快取代替新觀察；不宣稱跨 GitHub 讀取有全域交易（AC-G18）。
- Pass 後的新 observation（依 §10 的 `after_revision` 排序，且未被更晚 observation 取代）若 key 改變 → `pass.current` 移入 history 標 `invalidated_at`，依矩陣回 validating／checking／awaiting_approval；acceptance 綁 key，不移植（AC-O11）。

### 12. Findings、correction、爭議、反覆與人工退回（R12、R16；AC-F01–F16）

- 提取 `findings.py`（`matches` 沿用 ID、blocking 依 category、closure 權限）與 `correction.py`（同版本收齊、batch 登記時 round+1、回應完整性、一次爭議、recurrence 門檻 `failed_rechecks≥2` 或 `reopen_count≥1`）。
- **R16 修正**：`import_review` 遇 `matches` 指向 `resolved`／`waived` 的 finding 時，必須附 Reviewer `reopen_basis`；狀態回 `open`、`reopen_count+1`、舊 closure 移入 `closure_history`、lineage 記錄 result 與版本，並立即觸發 recurrence Blocked（舊實作只覆寫欄位、保持 resolved，`findings.py:19-31`）。
- **R12 修正**：fix assignment 的 `findings` 內含每項完整快照（problem、basis、expected、location、severity、blocking、history、上次 review result 物件、先前 fix evidence），並帶 batch 的 CI failures 與 AC；覆核 assignment 帶同一 batch 的快照、Implementer 回應與 fix evidence。只憑 assignment 與其 BlobRef 就能工作（舊 `add_fix_task` 的 `spec=None`、`ac_ids=[]`，`loop.py:460-463`）。
- 爭議：`disputes[fid].reviews_used` 在 feature 層，不因 epoch／session／重送重置；伴隨新 head 先回 validating 再合併最新 review（AC-F10）。
- 人工退回：`decide return`，`source=human_acceptance`、以 feedback identity 去重、失效 Pass、沿用 feature 剩餘 rounds；非 AC 缺陷 → Blocked 交 Project Lead／使用者（AC-F11、F12、O07）。

### 13. 預算與時間（缺口 3；⛔DN-1；R09；AC-D16、D17）

- **Active time**：activity 區間的聯集。`begin` 派工／CI 等待／coordinator 驗證類 operation 時開啟，對應結果匯入、stop 確認、CI 終態時關閉；等待人工且無活動時不計。沿用舊 `budget.active_seconds`／`on_resume` 的算法（提取並覆核）。
- **每次 CLI 呼叫的 gap 計入**：`last_touch_at` 到本次呼叫之間若有未關閉 activity，全額計入 `unknown_intervals`，直到外部時間戳證明可扣除（例：native transcript 最後一則 assistant message 時間）。
- **Deadline**：每個 assignment 帶 `deadline_at = now + min(role_timeout, remaining_budget)`；role timeout 45／30／30 min 仍是待 D11 確認的技術預設。
- **線上執行**：orchestrate 的等待是有界切片（`tool herdr observe --op … --max-wait 60s`），每片返回後必須呼叫 `inspect`；engine 在 `now ≥ deadline_at` 或預算用盡時，只對已知 active attempt 給 `stop`；已送過就只讀回原 stop op。即使 feature 已因其他原因 Blocked、或有其他 in-flight op，也照樣優先給（§9 第 1 點、`safety_actions`）。
- **離線（⛔DN-1）**：協調 session 關閉或主機睡眠時沒有程序會在 4h 時刻停止 worker。下次任何 `loopctl` 呼叫會把整段計入、記錄 `budget.overrun={seconds, detected_at}`、只允許 stop 與 Blocked。是否接受「離線時超時後才發現、如實記錄」作為 D13 的實作語意，或要求 per-worker 硬停止 wrapper（需 H2 probe），由使用者決定；未決前 AC-D17 不標完成，spec 文字不預先弱化。
- **預算延長**：只接受 `decide budget_extension`；新 epoch／run ID 不重置（R08）。

### 14. Herdr transport 與 runtime profile（D44；AC-D18–D24）

`tools/herdr.py` 只有三件事：從 operation 建固定 argv、呼叫一次、解析 JSON。所有命令帶 `--session <locator.herdr_session>`。

| 操作 | argv（依 H0 實測形式） |
| --- | --- |
| worktree | `herdr --session S worktree create --workspace W --branch le/<fid8>/<attempt> --base <T0> --path <p> --label <attempt> --no-focus` |
| 啟動（OpenAI） | `herdr --session S agent start <name> --kind opencode --pane <pane> --timeout 20000 -- --model openai/<model> [--session <native>]` |
| 啟動（Claude） | `herdr --session S agent start <name> --kind claude --pane <pane> --timeout 20000 -- --model <model> --session-id <uuid5(feature_id, attempt_id)> --settings <permission_profile_path>` |
| 派入 | `herdr --session S agent prompt <name> "<marker>\n<固定模板：讀 assignment 路徑、寫 result 路徑>"` |
| 觀察 | `herdr --session S agent get <name>`；`herdr --session S pane process-info --pane <pane>` |
| 停止 | `herdr --session S agent send-keys <name> ctrl+c`，再 process-info 確認 |

- Marker 第一行：`LOOPCTL op=<op_id> attempt=<attempt_id> payload=<payload_digest>`。Agent name 只作定位；身份以 native session ID＋marker 讀回為準（pane 可能換 occupant）。
- **Native 讀回**：Claude Code 由指定 `--session-id` 找 transcript，讀 user marker 與 `message.model`；OpenCode 由 native session ID 讀 messages 的 `modelID`。H2 固定兩者的讀取命令與路徑並保存為 preflight 證據；讀不到就 `outcome_unknown`，不猜。
- **Profile**：`workflow.yaml` 的 `profiles.<role>` 分欄保存 transport、runtime、runtime_version、provider、model、permission profile 路徑與 digest。Implementer 依 D36 為 `claude-opus-5-5`；Reviewer model 待核准（精確 ID 屬 D11 確認的設定）。不自動換 runtime／model，未選用接入缺失不影響本 profile（AC-D19、D23）。
- **Reviewer 隔離靠 runtime 既有權限能力**：Claude Code settings 的 permissions deny、OpenCode permission 設定；worker profile 只允許寫自己的 worktree 與 inbox，拒絕 `git push`、`gh`、`herdr`、`loopctl decide|record|begin|prepare`；Reviewer 在獨立 clone、無寫作者 branch 路徑。H2 以真實 agent 執行負例清單產生能力報告；任一負例成功或無法執行 → `unverified` → G2 unknown／Implementer 派工 Blocked（AC-G12、D19）。Prompt 中的「read-only」或 pane 名稱不算證據。
- **正式 profile 不用 `--safe-mode`／`--pure`**：它們會停用 skills／hooks；H2 需驗證載入核准 skills 的 profile（H0 未驗）。

### 15. GitHub 工具邊界（AC-F13、F14、G13–G15、D12）

- `tool gh observe`：PR（head、base、merge_commit_sha、mergeable）、`git fetch` 後本地計算 merge-base、branch protection／rulesets（403 → `forbidden`）、check-runs（`filter=all`、完整分頁）與 statuses、issue body（重算 digest）、test merge mapping（`M^1==base_tip`、`M^2==H`）。全部 raw 回應存物件，observation 只是讀取，失敗可在額度內重試。
- 發布：controller 在 review 匯入時登記 `gh_publish_pr`，issue 摘要依賴其 URL。engine 在 Pass 觀察前把這兩個 operation 排進 next action（§9 checking，D45-R04）；工具以 marker 先查再寫、寫後讀回。失敗只重試該 operation，不重做 review；publication 狀態與 verdict 分欄。
- 不 merge、不 close、不 approve。

### 16. 工作區、整合與保留（R05；AC-G08、D04、O08）

- Implementer：每個 attempt 一個 Herdr worktree，branch `le/<fid8>/<attempt>`，起點 T0 = 整合 branch tip。完成後 `tool git integrate`：確認 attempt 是 task 現行 lease、T0 是 A 祖先、`diff T0..A` ⊆ scope，再 `update-ref refs/heads/<integration> A T0`（CAS，只允許 fast-forward）。提取舊 `integration.integrate` 的檢查順序，但移除 clone fetch（worktree 共用 refs）。
- 因 worktree 共用 ref store，worker 技術上能移動整合 ref：每次 `assess`／integrate 前比對 ref 與 `integration.log` 最後 `to`，不符 → Blocked `integration_ref_moved`（偵測，不是防止；⛔DN-2）。
- Reviewer：`git clone --no-hardlinks` 到 `review/<attempt>/`，不共用 refs；Herdr 以該路徑開 workspace（H2 驗）。
- 保留：不呼叫 `worktree remove`；關閉 run 只關 workspace 視圖；清理需使用者決定。
- Adopt（AC-O08／O09、R11）：`init-feature --adopt facts.json` 先唯讀記錄原 owner、未提交內容、branch／head／base、artifacts、D11 與 Red；缺 D11 → awaiting_approval；缺 Red、未固定 base、未知 writer → Blocked；G1 用完整核准 task 集合，空集合不能通過。

### 17. Orchestrate skill 契約（AC-O01–O28 的 agent 側；H2 交付）

- `skills/orchestrate/SKILL.md`：啟動時讀 artifact index、`loopctl inspect`，只依 `next_action` 與 `safety_actions`（到期 stop 與讀回；不論是否 Blocked）行動。每一步先 `prepare`，再依動作執行一個 tool：
  - 已登記 operation 的首次執行（含唯讀 observation）或允許的重試，用 `loopctl tool … --op OP`；begin、單次執行、record 都在該 tool 內完成。
  - 對既有 `in_flight`／`outcome_unknown` operation 的讀回，用 `loopctl tool … reconcile --op OP`；不經 begin，不重發原操作，經 `api.record_readback` 保存（§2）。

  其餘規則：等待用有界切片；遇 `blocked` 呈現選項給人，不自行選。
- 依 phase 載入方法 references（Project Lead SA 契約、OpenSpec、Writing Plans、Superpowers TDD、review／review-response、Retro 整合方法），記錄 skill 版本 digest；其他 skills 不另啟外層 loop；user-only skills 不在背景呼叫。
- Writing Plans 方法適配（本輪 tasks.md 已使用）：採 scope／files／interfaces／test-first／global constraints／review focus；路徑改為 OpenSpec `tasks.md`；Execution Handoff 不啟動 subagent-driven-development 或 executing-plans，改由核准後 orchestrate（bootstrap 期間由協作者依 D39）派工。

### 18. OpenCode-only 路徑（缺口 6；AC-D20、D22、D23）

核心契約不依賴 Herdr：`Assignment`／`Result`／operation 與 native handle 分欄；Herdr 是 `profiles.<role>.transport` 的一個值。公司環境若只有 OpenCode，可新增 `transport=opencode-direct` 的工具模組（同樣固定 argv＋單次＋讀回）。本 change 的第一切片只驗 Herdr 接法；AC-D20／D22／D23 在 validation 列「未覆蓋（需公司環境）」，不因 H2 通過勾完成。

### 19. 證據信任邊界（⛔DN-2）

本設計能保證的：
- 狀態只經 `loopctl` 寫入，每個 revision 有歷史與 hash chain，手改可偵測、不當決策。
- Worker 沒有 token，不能 prepare／begin／record；runtime permission profile（H2 驗證）拒絕其呼叫 `loopctl` 狀態命令與寫出 worktree／inbox。
- Gate 只從 tool 捕捉的證據與 native 讀回重算；worker 自述只作說明。

不能保證的：同一 OS 使用者下，繞過 runtime permission 的程序可以讀 token、寫 `$LOOPCTL_HOME`、偽造 evidence 物件或以人工身分呼叫 `decide`。舊 v3 以 OS sandbox 拒寫處理，D41 已排除自建 sandbox。可接受的信任程度是使用者決策（選項見 decisions-needed）。

### 20. G3 required policy（缺口 7；⛔DN-3）

`loop-engineering` 私有 repo 的 rules API 回 403（S1 紀錄）。現行設計 fail-closed：`forbidden` → G3 unknown＋Blocked、不耗修正輪（R14）。H2 要到 PR Pass，需要使用者擇一：讓 rules 可讀（權限／方案），或以明確 `policy_change` decision 宣告必要 check 集合並在 Pass package 顯示「GitHub rules 未核對」。未決前 H2 的 PR Pass 任務 blocked。

### 21. 七個設計缺口的解法索引

| 缺口（scope-reconciliation 末尾） | 解法 | 位置 | 狀態 |
| --- | --- | --- | --- |
| 1 許可不等於可重送的 dispatch | prepare 可重送、begin 只給第一個 caller、in_flight 不可再 begin、unknown 只讀回 | §6 | 已設計 |
| 2 同 feature 唯一狀態／預算 | feature 單檔 authority、epoch 取代 run、claim token | §3、§5 | 已設計 |
| 3 4h 與非長駐 controller | 有界等待切片、deadline、gap 計入、overrun 記錄 | §13 | 線上部分已設計；離線語意 ⛔DN-1 |
| 4 原始 TDD 與身份證據 | policy 命令、worker 捕捉＋coordinator replay、逐項驗證、native model 讀回 | §10、§14 | 已設計；可信程度 ⛔DN-2 |
| 5 Pass 前外部觀察 | `purpose=pass` observation 須晚於 assessments 且重算 G3 | §11、§15 | 已設計 |
| 6 OpenCode-only | transport 分欄、未覆蓋如實列 | §18 | 已設計；實測需公司環境 |
| 7 G3 required policy | fail-closed＋policy_unknown 路由 | §11、§20 | 路由已設計；放行條件 ⛔DN-3 |

## Risks / Trade-offs

- [重建比改造多寫新碼] → 只重建主流程／CLI／狀態；規則以提取契約帶入並附新測試，不從空白重寫 gate 語意。
- [提取時把舊缺陷一起帶入] → 提取契約要求每個 symbol 列出適用 findings 與新回歸測試；R06、R13–R17 的測試先 Red 再改。
- [Herdr `agent prompt` 無 per-turn 完成語意] → 完成只看 inbox result＋身份核對；`done`／idle 不進 gate。
- [Claude Code 停止可能不生效（H0 已觀察）] → stop 以 process-info 確認，否則 Blocked；不派競爭 attempt。
- [Native transcript 讀回路徑依 runtime 版本] → H2 preflight 固定並存證；版本改變需重驗，讀不到即 unknown。
- [worktree 共用 refs，worker 可動整合 ref] → 每次整合／評估前比對 log；偵測後 Blocked（防止程度 ⛔DN-2）。
- [feature 狀態在 repo 外，分享不便] → `docs/validation/<feature>/` 保存可分享索引與去敏證據副本；本機狀態不是唯一可分享紀錄。
- [每次 binding 變更都回 awaiting_approval] → 較多人工確認；換來新契約不沿用舊 G2。
- [離線無即時停止] → 如實記錄 overrun 並 Blocked；是否需要更強保證由 DN-1 決定。

## Migration Plan

1. 協作者依 §1 W1 在 D11 後建立 worktree（需使用者確認執行；本輪不做）。第一個 commit 移除舊 `src/delivery/`、`tests/`、舊 CI 對 `delivery` 的引用，並新增 `docs/implementation/removed-s1.md`（來源 commit、PR #2、checkpoint 路徑、S1 證據封存位置）。
2. H1 依 tasks.md 在新樹實作；每個提取 commit 在 `docs/implementation/extraction-manifest.json` 登記（契約見 cleanup-map）。
3. H1 完成後新樹只有 `loopctl`；`docs/implementation/cli.md` 改寫為新命令（同一切片內）。
4. 舊 S1 狀態不遷移：沒有需沿用的產品資料；`.delivery/bootstrap/**` 與 S1 證據封存保持不動。
5. 回滾：不使用 thin branch；舊 PR #2 與 checkpoint 仍可查閱。新 feature 狀態目錄保留為紀錄。
6. 17 項 findings 在新程式、新證據與獨立覆核後才可解除；H1 只提供修正與回歸測試，不自行關閉。

## Open Questions

以下可延後，不改變 specs、做法或 task 拆分：
- OpenCode native messages 的讀取命令（CLI export 或 server API）在 H2 preflight 固定。
- Herdr 開啟非 worktree 的 Reviewer clone 的確切命令（`workspace create --cwd` 或 `worktree open`）在 H2 固定。
- Linux 上的 flock／fsync 行為沿用 Q-PLATFORM：本次只驗 macOS，Linux 由 CI 跑同一測試集。
