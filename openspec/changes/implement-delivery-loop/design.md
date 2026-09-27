# Design：implement-delivery-loop Controller（核准基準 v3）

> **D41／D42：scope revision pending（2026-09-27）**。使用者已同意收斂為 orchestrate skill 呼叫薄 controller；舊 S1 修正已停止並保存。本文的 D40 技術內容／AC 是歷史核准基準，尚未完成新 scope 的逐項映射，不是繼續舊計畫的派工授權。三 gates、版本與 finding 覆核維持；新 design／plan 仍須 review 及 D11 確認。歷史 approval.json 保持原樣，不代表本次修訂已核准。最新 [產品目標及邊界](../../../docs/project-intent.md)、[決策 D41／D42](../../../docs/decisions.md)。

> D11 已依 D40 取得使用者確認（2026-09-27）；三個 PR 分段交付，S1 可開始。技術本文沿用已覆核 v3；本文內的建議預設已核准，明列替代方案不代表選用，平台待實測仍需證據。
> 來源：[v3 候選及完整審查](../../../docs/reviews/2026-09-27-controller-detailed-design.md)；核准 hashes 與狀態標記變更見 [approval.json](approval.json)。這是正式 design；候選保留為不可變歷史。
> 本輪僅更新核准狀態、已選 repository 與待決清單；未改寫三 gates、技術算法或已驗證範圍。

## Context

- 已確認且本文不重開：三 gates（D01）、PR Pass 終點（D03）、單一 controller（D02/D08）、D09/D12 finding 規則、D13 上限（4h active、3 輪 correction、每項 infra 操作額外重試 2 次、實作並行度 1）、D14 JSON/YAML、D24–D28、D30/D38 runtime 解耦與 OpenCode 預設、D36/D39 本次由 Opus 5.5 Implementer + 獨立 GPT/Codex Reviewer 經協作者協調。
- 目前 orca-delivery 已連結 private `yschiang/orca-delivery`、無產品程式；OpenCode 1.18.32 只完成無推論 probe；精確 reviewer model、公司平台（Q-PLATFORM）；本次方法與 GitHub 目標已依 D40 確認。
- 本機可用：Python 3.12.13（uv）、OpenSpec 1.13.1、Superpowers 6.3.0、`gh`、`/usr/bin/sandbox-exec`（Darwin 27.0）。

## Goals / Non-Goals

**Goals**
1. 確定性、可用 fake adapters 覆蓋核心規則的 controller：狀態機、gates、findings、budget、outbox、恢復。
2. 窄 adapters：git、evidence runner、GitHub（`gh api`）、runtime（OpenCode 預設；其他選配）、sandbox launcher。
3. 人可讀狀態：`run.json` 或 `delivery status` 即見 phase、gates 理由、blockers、next action（AC-D01）。
4. Worker 寫入權限由 OS 層級邊界限制，能力未證明時如實 unverified／Blocked（DUR-02、GAT-05）。

**Non-Goals**
- 不做 daemon/dashboard/DB/多主機 writer/網路磁碟（AC-D11 明示不宣稱）；不驗 power-loss durability（§8 說明驗證範圍）。
- 不自動 merge/close/release/deploy（D03）；不在背景呼叫 user-only skills（D28）。
- 不以 LLM 判定 gate 的確定性部分；語意判斷只來自 Reviewer 結果或人工 decision。
- 本次不實作 Orca/Claude Code/Codex adapters，除非使用者選用（D38）。

## Decisions

### 1. 語言、形態與模組 [建議]

Python 3.12 本機 CLI `delivery`（uv），核心 stdlib；唯一第三方依賴 PyYAML（`safe_load`）讀 `workflow.yaml`。替代：零依賴改 JSON 設定（失去註解）；TypeScript（OpenCode 以 HTTP 接入，無優勢）。

| 模組 | 責任 |
| --- | --- |
| `store.py` | 原子 snapshot、write-once durable blobs、events.jsonl、引用完整性（§8） |
| `schema.py` | 各 JSON 的欄位驗證與 `schema_version` |
| `versions.py` | bindings、`VersionSet`、gate dependency sets、assessment 推導規則（§5） |
| `gates.py` | G1/G2/G3/Pass 純函式評估 |
| `findings.py` | registry、closure 權限、batch、dispute、recurrence（§7） |
| `budget.py` | active interval 聯集、unknown interval、feature 累計（§12） |
| `authority.py` | 主機層級 feature authority、flock、run lineage（§9.1） |
| `outbox.py` | operations 與分段恢復（§11） |
| `controller.py` | `step(run, observations) -> (run', ops)`、`reconcile()`、`resume()` |
| `sandbox.py` | 依 assignment 產生 launcher profile、preflight 負例套件（§10） |
| `adapters/runtime.py`、`adapters/github.py`、`adapters/git.py`、`runner.py` | 協定＋fake＋真實實作 |
| `cli.py` | `init/start/adopt/status/resume/decide/reconcile/preflight/evidence run/submit-result` |

核心規則在純函式；I/O 只經 adapters 與 outbox。Runtime、GitHub 協定各有 fake 與真實實作（D30 的正式接縫）。

### 2. 檔案布局 [建議]

```text
<repo>/workflow.yaml                         # 版控 policy（無 credential）
<repo>/.delivery/                            # gitignore；controller 主 repo（author repo）
  project.json                               # authority 的 repo-local 檢視（§9.1 修復）
  runs/<run-id>/
    run.json                                 # 唯一現行 authority
    events.jsonl                             # 稽核歷史（含 observations）
    inbox/<attempt-id>/                      # 該 attempt 唯一可寫的結果通道
    blobs/<sha256>                           # content-addressed durable blobs（assignment/result/evidence/receipt/log）
$XDG_STATE_HOME/orca-delivery/
  features/<feature-id>/authority.json       # 主機層級 authority locator＋run lineage（§9.1）
  features/<feature-id>/lock                 # flock
  attempts/<run-id>/<attempt-id>/clone/      # per-attempt 獨立 clone（§9.2）
  attempts/<run-id>/<attempt-id>/rt/         # 該 worker 的 runtime state/HOME/TMPDIR
```

`workflow.yaml` 範例（D13 上限為程式常數；只有未核准預設放設定並隨 D11 確認）：

```yaml
schema_version: 1
repo: {github: yschiang/orca-delivery, base: main}               # D40 已確認；GH 權限與 CI 規則仍需實測
g1:
  commands: [{id: unit, run: [uv, run, pytest, -q, "--junitxml={junit}"]}]
snapshot: {exclude: [".env*", "*.pem", "*.key"]} # 另受 .gitignore 與 assignment scope 限制
na: {doc_globs: ["docs/**", "**/*.md"]}         # 只作預篩
ci:
  required: [{name: test, app: github-actions, source: head}]   # source: head | merge（§6.3）
  allow_non_success: []
timeouts_min: {worker: 45, review: 30, ci: 30}   # [建議] 未核准預設
recurrence: {max_failed_rechecks: 2, block_on_reopen: true}   # [建議]
profiles:
  implementer: {runtime: opencode, provider: anthropic, model: claude-opus-5-5, sandbox: worker}
  reviewer:    {runtime: opencode, provider: openai, model: null, sandbox: reviewer}  # [待決] model
```

### 3. 狀態機 [建議；phase enum 沿用 workflow-contracts]

維度分開保存：phase、task execution、gate assessment、review verdict、publication、human acceptance、integration facts；另有 `waits[]` 與 `blockers[]`（原因、證據、需誰決定、最小恢復條件、`resume_to`）。

| From | 事件／guard | To |
| --- | --- | --- |
| intake | 新 feature 或 adopt 缺 design/plan | planning |
| intake | plan 存在但無該 plan binding 的 D11 decision | awaiting_approval |
| intake(adopt) | D11 適用、tasks 未完 / 已實作 G1 待驗 / G1 已核對 | implementing / validating / checking（AC-O08） |
| intake | authority 衝突、owner 未交接、未知 writer、必要來源不可讀或衝突 | blocked（AC-O04, O09, D03） |
| planning | C3 package 登記（design/tasks/validation bindings、task→AC） | awaiting_approval |
| awaiting_approval | `approve_plan` decision 指向**目前** bindings，且 ticket、依賴（D27）、budget、sandbox 能力通過 | implementing（AC-O05, O06, O13） |
| awaiting_approval | `revise` decision | planning |
| implementing | task 派工 → result 匯入 → `integrate` op 成功（§9.2）；下一 task 依序 | implementing |
| implementing | 全部 task 已整合 | validating |
| validating | G1 assessment passed → `push`、`pr_ensure` ops；PR 首次 binding 以 R-unaffected 推導 G1（§5.3） | checking |
| validating | G1 可修補缺失 | 回到產生該版本的工作單位（implementing 或 correcting），不新增 round |
| validating | 歷史 Red 不可得、N/A 被拒且無法補、red 無法重現 | blocked（AC-G07, G10） |
| checking | 當前 version_key 下三 gates 的 current assessment 皆 passed，Pass 前 re-read 一致 | ready_for_acceptance（AC-G01, G18） |
| checking | base_tip/merge_base 改變（head 同）→ G1 依 R-base 重驗；G2 stale；G3 依 check source 重讀（§5.3） | checking 或 correcting（base 衝突） |
| checking | 收齊同版本 G2/G3、有可修問題、rounds<3、未觸發 recurrence | correcting（AC-F05） |
| checking | verdict=blocked、爭議未解、rounds 用盡、unknown 無法恢復 | blocked（AC-G03, F07, F09） |
| correcting | correction result 完整且 `integrate` 成功產生新 head | validating（AC-F06, F10） |
| ready_for_acceptance | `accept` decision（綁 version_key） | 同 phase，acceptance=accepted → `retro` op（AC-O14） |
| ready_for_acceptance | `return` decision：原 AC 缺陷且預算足 | correcting（AC-F11） |
| ready_for_acceptance | 新 head/base/binding 變更 | 依 §5 回 validating/checking/awaiting_approval（AC-O11, G18） |
| 任一 | feature 累計 active 到 4h、ownership 衝突、state/引用不可信 | blocked（AC-D17, D11） |
| blocked | `unblock` decision 或外部條件恢復 | blocker 的 `resume_to` |

`step()` 是純函式；副作用只在 snapshot 提交後由 outbox 執行（§11）。

### 4. Schema 要點 [建議]

所有 JSON 帶 `schema_version`；未知版本 → Blocked（AC-D11）。`run.json` 頂層以人讀為先：

```json
{
  "schema_version": 1, "run_id": "r-…", "revision": 42, "feature_id": "sha256:…",
  "phase": "checking", "next_action": {"kind": "wait_ci", "detail": "test pending (attempt 2)"},
  "blockers": [], "waits": [],
  "versions": {"version_key": "sha256:…", "set": {"…": "§5.2"}},
  "gates": {"g1": {"current": "as-7"}, "g2": {"current": "as-9"}, "g3": {"current": null}},
  "assessments": {"as-7": {"gate": "g1", "version_key": "…", "status": "passed", "reasons": [],
                           "evidence": ["sha256:…"], "derived": {"from": "as-3", "rule": "R-unaffected",
                           "changed_fields": ["pr_number"]}}},
  "bindings": {"b-4": {"role": "issue_body", "locator": "OWNER/REPO#12", "content_digest": "sha256:…",
                        "adopted_at": "…", "adopted_via": "intake", "last_observed_at": "…"}},
  "acceptance": {"status": "pending", "version_key": null, "history": []},
  "budget": {"active_seconds": 5400, "open_activities": [], "unknown_intervals": [],
             "correction_rounds_used": 1, "infra_retries": {"op-17": 1}},
  "integration": {"branch": "delivery/<slug>", "tip": "…", "log": [{"task_id": "2.3", "attempt_id": "a-…",
                  "from": "T0", "to": "A", "op": "op-21"}]},
  "tasks": [{"task_id": "2.3", "ac_ids": ["AC-G11"], "change_class": "behavior", "status": "succeeded",
             "lease": "a-…", "attempts": ["a-…"], "red": ["sha256:…"]}],
  "findings": {}, "batches": [], "disputes": {}, "operations": {}, "imported_results": {},
  "decisions": [], "pass_history": [], "pending_history": []
}
```

- **Assignment**：contracts 欄位全數保留，另含 `profile`、`sandbox_profile_digest`、`clone_path`、`base_sha`（T0）、`scope.paths`、`inbox`、`marker`、`deadline`。
- **Result**：同 IDs、`execution_status` 與 `verdict` 分開、`observed`（cwd、head、base）、`evidence[]`、`findings[]`、`responses[]`、`producer`（agent 或 adapter＋native IDs＋actual_model）。
- **Evidence**：`kind`（red/green/regression/doc_check/replay_check/base_recheck）、command、env allowlist、時間、exit、輸出 blob digest、junit 摘要、`snapshot`（commit、tree、parent、included paths、out-of-scope dirty paths）、producer。
- **Decision**：kind（approve_plan/revise/adopt_binding/accept/return/resolve_finding/waive_finding/budget_extension/unblock/abandon_run/handoff/policy_change）、subject（IDs＋version_key/binding）、actor、source、choice、reason、created_at、impact。只經 `delivery decide`（人於 sandbox 外執行）寫入。

### 5. 版本、binding 與 gate assessment [建議；集合沿用 GAT-07]

#### 5.1 Binding 與 observation 分離（DR-02）

- **Binding**（不可變）：每份採用來源一筆 `{role, locator, content_digest, adopted_at, adopted_via}`。`adopted_at` 是採用時間，建立後不變。Issue body 的 digest = API 回傳 body bytes 的 sha256（不正規化，保守）。
- **Observation**（不進版本）：每次讀取記 `last_observed_at`（run.json，binding 旁欄位）；只有 digest 與 binding 不同、或 resume 後第一次讀取時寫入 events.jsonl。相同 bytes 重讀 → version_key 不變。
- **變更**：讀到不同 digest → 建 candidate binding（未採用）、phase → awaiting_approval 並顯示差異；`adopt_binding` decision 才採用並產生新 version_key；此 decision 不影響任何 gate（§5.3，AC-O03, G17）。

#### 5.2 VersionSet

`VersionSet` = repo_id、pr_number、head_sha、base_ref、base_tip、merge_base、各 role 的 adopted `content_digest`（project_spec、feature_spec、issue_body、design、plan、validation、policy）、`skills`（**核准 plan 釘住**的 skill digests；本機安裝版本不在 VersionSet，與釘住值不符時不派工）、controller_version。**不含任何時間**。`version_key` = canonical JSON 的 sha256。

#### 5.3 Gate assessment 與推導規則（DR-03、DR-10）

Evidence 不可變，保留自己的來源身份（commit、tree、SHA、producing assignment 及其 skill refs）。Gate 判定是 **assessment**：`{gate, version_key, status, reasons, evidence, derived}`。每個 gate 的 current assessment 必須綁當前 version_key，Pass 才可能成立。VersionSet 改變時，controller 逐一比對「欄位 × gate」矩陣產生新 assessment；原 evidence 身份不改寫，推導規則與理由保存在 `derived`。

**完整依賴矩陣（fail-closed）**：
- 每個 VersionSet 欄位對每個 gate 都必須有一格。
- 矩陣內找不到的欄位或 skill 名稱，一律視為依賴：assessment stale。
- 實作以表格驅動，並用 schema 測試保證 VersionSet 欄位集合 = 矩陣列集合。

| 變更欄位 | G1 | G2 | G3 |
| --- | --- | --- | --- |
| repo_id | stale（run 內不應變；變則 Blocked） | stale（同左） | stale（同左） |
| pr_number | R-unaffected。理由：G1 evidence 只綁 head/tree，不含 PR 身份 | stale → 新 review | R-reobserve |
| head_sha | stale → 新 evidence | stale → 新 review | R-reobserve |
| base_ref／base_tip／merge_base | R-base | stale → 新 review（新 diff） | R-reobserve（merge-source 需新 M） |
| spec／issue_body／design／validation／plan binding | R-reevaluate（依新 plan 的 task→AC；新增 AC 缺 evidence → missing） | **stale → 新契約 review**（§6.2） | R-reobserve |
| policy | R-reevaluate＋policy 翻轉規則 | R-reevaluate＋policy 翻轉規則 | R-reobserve＋policy 翻轉規則 |
| skills（釘住 digest；只隨 plan binding 變） | R-reevaluate。產生 evidence 的 assignment 所用 skill 與新釘住值不同 → 該 evidence 標 `method_changed`，須由新契約 review 判斷適用性 | stale → 新契約 review | R-unaffected。理由：CI 由 GitHub 依 head tree 執行，不使用 agent skills |
| controller_version | R-reevaluate（新版 evaluator 由已存 evidence 重算；舊 evidence 無法解析 → stale） | R-reevaluate（只重算 controller 側：verdict、closure、isolation、profile；review 內容本身不隨 controller 改變） | R-reobserve |

| 規則 | 定義 |
| --- | --- |
| R-unaffected | 只適用於矩陣中明列理由的格子；以相同 status 推導，`derived` 記 changed_fields 與理由 |
| R-base | G1：`git merge-tree --write-tree <base_tip> <head>`；衝突 → G1 failed（`base_conflict`，進 correction batch）；乾淨 → controller 在該 merge tree 執行 `g1.commands`（evidence kind=base_recheck）後產生新 assessment；**不無條件沿用** |
| R-reevaluate | 以當前 bindings/policy/controller 的確定性 evaluator，從已存 evidence 重算。只能讀既有 evidence，不能產生或替代 evidence；不足即非 passed |
| R-reobserve | G3 一律對當前 key 重新查詢 GitHub checks 並依當前 policy 判定（§6.3）；不沿用舊 G3 assessment |
| policy 翻轉規則 | 任一 gate 由非通過轉通過**只因** policy 變更 → Blocked 待 `policy_change` decision |

**沒有人工 reuse 路徑（DR-10）**：v2 的 `R-reuse` 與 `adopt_binding.reuse` 已移除。
- `adopt_binding` decision 只採用新 binding，對任何 gate 都沒有效果。
- 新 G2 只能來自 controller 派出、符合 §6.2 全部條件、讀過新 binding 的獨立 Reviewer 結果。
- 人工 decision 在 G2 範圍內只保留 D09 既有權限：對指定 finding＋版本 resolve/waive，但不會產生 G2 clean。
- Schema 拒絕含 `reuse` 欄位的 decision，因此舊格式無法被靜默接受。

端到端路徑：
- **pre-PR → PR → Pass**：V1（pr=null）G1 passed → push＋pr_ensure → V2（pr=34）→ G1 經 R-unaffected 得 V2 assessment → G2 review 與 G3 checks 在 V2 取得 → 三者同 V2 → Pass。
- **base-only 變更**：V3 → G1 經 R-base 重驗（通過，或 failed → correcting）；G2 對新 diff 重 review；G3 重新觀察 → Pass、correcting 或 Blocked。
- **契約變更（S1 → S2 新增 AC）**：S1 下 G2 clean → S2 candidate → `adopt_binding` → V4。
  - G2 stale，須派新契約 review；
  - G1 R-reevaluate：新 AC 需先經 plan binding 對應 task，缺 evidence → missing → implementing；
  - 新 review clean 且新 evidence 齊全前不可能 Pass。
- **controller 升級**：所有 gate 以 R-reevaluate／R-reobserve 重算，不直接沿用；新 evaluator 更嚴時，原本 passed 的 assessment 可能轉 failed。

Version_key 不符的晚到結果只存歷史（AC-G16）。Pass 前 re-read head/base/bindings，不一致即放棄這次轉移；不宣稱全域 transaction（AC-G18）。Acceptance 綁 version_key（AC-O11）。

### 6. Gates

#### 6.1 G1：歷史 Red＋目前 Green [建議]

**Red snapshot 程序（DR-04 v3）**：`git stash create` 不收 untracked 檔；v2 複製 worker index 的做法會把 staged 的 scope 外或排除檔帶入 snapshot。兩者皆不再使用。

**語意（何者進 snapshot）**：
- **Baseline B** = attempt clone 的 `HEAD` tree，也就是 T0＋worker 已 commit 的內容。它提供外部程式所需的全部 repo 內容。
- **Overlay** = 執行測試當下**工作樹**中、相對 B 有變更的路徑，且須同時滿足：在 `scope.paths` 內、未被 `.gitignore` 忽略、不符合 `snapshot.exclude`。
- **Staged 與 unstaged 不區分**：一律以工作樹內容為準，因為測試讀的是磁碟上的檔案。Worker index 的內容永不讀入 snapshot；只存在 index、不在工作樹的內容也不收。
- **snapshot.exclude 對 baseline 已 tracked 的檔案**：B 內原有、未修改者照 B 保留（例如 repo 本來就 tracked 的 `.env.example`），不新增資料。已被修改或刪除者 → 拒絕 snapshot（`excluded_tracked_modified`），因為無法同時排除它又忠實呈現執行內容。

**程序**（runner 在 attempt clone 內、執行測試**前**）：
1. **已 commit 範圍預檢**：`git diff --name-only T0 HEAD` 的每個路徑須在 scope 內、且不符 exclude；否則拒絕（`committed_scope_violation`），因為 B 本身已含違禁內容。
2. `GIT_INDEX_FILE=$IDX git read-tree HEAD`：暫存 index 從 B 起算，不複製 worker index。
3. `GIT_INDEX_FILE=$IDX git status --porcelain=v2 -z -uall`：得到工作樹相對 B 的變更集合 C（含 untracked 非 ignored）。此步不寫入任何 git 物件。
4. 逐一分類 C：
   - 符合 exclude 且不在 B → 略過（記路徑名到 `omitted_excluded`，不讀內容）；
   - 符合 exclude 且在 B → 拒絕；
   - scope 外 → 拒絕（`scope_violation`）；
   - 其餘 → allowed。
   另把「worker index 與 B、工作樹都不同」的路徑名記為 `index_only`，僅作資訊，永不收入。
5. **有任何拒絕**：立即停止，**不執行 `git add`**，不寫 tree/commit/ref，也不執行測試。Evidence 記 `snapshot_refused`（invalid），只含路徑名與原因，不含檔案內容。Worker 清理後重跑 Red。
6. `GIT_INDEX_FILE=$IDX git add -A -- ':(literal)<allowed 路徑>'…`：只為 allowed 路徑寫 blob。
7. **寫 tree 前驗證**：`GIT_INDEX_FILE=$IDX git diff-index --cached --name-only HEAD` 必須恰等於 allowed 集合；不等 → 中止、不寫 tree（防實作錯誤）。
8. `write-tree` → `commit-tree -p HEAD` → `update-ref refs/delivery/red/<task>/<attempt>/<n>`；刪除 IDX。
9. 執行測試並捕捉 junit；執行後重算 allowed 路徑的內容 hash，與 snapshot 不同（測試期間被改動）→ 該 Red invalid（`snapshot_drift`）。

Controller 只 fetch red ref（只傳可達物件），worker clone 中既有的 staged blob 不會進入 controller repo。

**本機 tmp probe**（本輪，真 git，見 finding-responses.json DR-04）：
- (A) 已 stage 的 `.env.fake`、untracked 新測試、stage 後又改動的 `src/app.py` → snapshot 含新測試與 `app.py` 的**工作樹版本**、不含 `.env.fake`；worker index hash 與 `git status` 不變；controller repo fetch red ref 後不含 `.env.fake` 的 blob；replay 得相同 failing ID。
- (B) 已 stage 的 scope 外 `outside.txt` → 拒絕，未建立 ref，worker index 不變。
- (C) 修改 baseline 已 tracked 的 `.env.example` → 拒絕。
- (D) 未修改的 tracked `.env.example` → 以 baseline 保留。
- 重現 reviewer 的 `review/staged-exclude-probe.json` 反例（staged 的排除檔留在 tree），v3 已不成立。

**Red 有效性（確定性）**：blob durable 且 digest 符合、producer=runner、exit≠0、junit 有 failure 且 0 collection/usage error（否則 invalid，AC-G07）、非 `snapshot_refused`/`snapshot_drift`、snapshot tree 相對 parent 的差異 ⊆ scope 且無 exclude 路徑（controller 匯入時以 `git diff-tree` 再驗一次）、snapshot parent P 是整合 head H 的祖先（§9.2 lineage）、failing IDs 在 H 的 Green 中存在且通過。

**Replay check [建議，always-on]**：controller 匯入時從 attempt clone fetch red ref，在自有 verification checkout 重跑，須以相同 IDs 失敗；標 `replay_check`，只作佐證。無法重現 → G1 unknown → Blocked 待決。

**Green**：controller 在整合 head H 的乾淨 checkout 執行 `g1.commands`（含 regression），producer=controller-runner。Worker 回報的 green 不算數（AC-G08）。

**Adopt 無歷史 Red** → missing → Blocked；只有 decision 明示接受 replay 替代時記 `red_source=replay_by_decision`（AC-G07, O09）。**N/A eligibility**：預篩（變更 ⊆ `na.doc_globs`）→ 派獨立 Reviewer（同 §10 reviewer 邊界）→ 結果綁 diff digest；接受只免 Red/Green 要求，`g1.commands` 仍執行，G2/G3 照常（AC-G09, G10）。

#### 6.2 G2：獨立 review [建議；isolation 依 §10]

G2 passed 需同時成立：
1. Reviewer assignment 由 controller 建立，profile 符合 `profiles.reviewer`；native 回報 actual model = requested（AC-D18, D24）。
2. Reviewer session ≠ 任何 implementer session，且非其子 session（OpenCode 父子欄位待以 `/doc` 核對；無法核對 → 此條 unverified）。
3. **Isolation = verified**：僅依 §10.3 條件成立。Clone、env 清理與事後 ref 比對**不能**使其升格；事後比對只作額外的竄改偵測（DR-01）。
4. Verdict=clean、version_key 為當前、所有 blocking findings 已依 §7 closure（AC-G11）。
5. **讀過當前契約（DR-10）**：
   - Review assignment 列出當前 VersionSet 的全部 binding digests（spec、issue body、design、plan、validation、policy、釘住的 skills）與 head/base；
   - result 回報實際讀取的 digests，須與 assignment 及當前 VersionSet 完全相符；
   - 任一不符或缺漏 → 此 review 不能支持當前 key。

**新契約 review**（binding 變更後的 G2 來源）：
- 它是一般 G2 assignment，條件 1–5 全部適用，另外輸入舊 binding→新 binding 的差異、舊 review 與舊 findings，並要求 Reviewer 判斷：新契約下既有測試是否仍證明各 AC、新增 AC 的覆蓋，以及 skill 變更使 evidence 標 `method_changed` 時的適用性。
- 它可以只聚焦差異，但輸出是當前 key 的完整 verdict；舊 verdict 不會帶入。
- 這是取得新 G2 的唯一途徑，人工 decision 不能取代（§5.3）。

任一不成立 → G2 unknown 並列缺口；verdict=blocked → G2 unknown、phase blocked、不開 round（AC-G03）；Implementer 呼叫的 subagent review 永不匯入（AC-G12, O02）。Bootstrap（D39）的 review 由協作者手動協調，不冒充產品 G2。

#### 6.3 G3：必要 CI [建議]

- Required 集合 = `ci.required`，與 repo branch protection／rulesets（`gh api`）核對；空集合、rules 不可讀或不一致 → 不通過並 Blocked 待 `policy_change`（AC-G13）。`repo.github` 未決（null）時 G3 = unknown，reason `github_target_undecided`。
- **候選 source SHA 發現（DR-08）**：
  - H：`pulls/{n}` read-back 的 `head.sha`，須等於 controller 最後推送的整合 tip。
  - M（test merge）：讀 `pulls/{n}` 的 `merge_commit_sha`／`mergeable`，並 `git fetch origin pull/{n}/merge` 至 controller repo，驗 `M^1 == 當前 base_tip` 且 `M^2 == H`。保存 mapping `{M, parents, base_tip, head, observed_at}`。GitHub 尚未計算或 parents 不符 → M 為 unknown/stale，在 CI timeout 內輪詢。
  - 每個 required check 依 policy 的 `source` 取對應 SHA，查 check-runs（`filter=all`、完整分頁）與 statuses；只接受 app 相符者；同名取最新 attempt（`started_at`，平手依 id）（AC-G14, G15）。
- 判定：completed＋success 才過；skipped/neutral 僅在 `allow_non_success` 有對應 decision 時接受；其餘狀態逐項列 reason；舊 M（base 已移動）→ stale。
- CI 等待超過 `timeouts_min.ci` → rerequest 作為 infra op（≤2 次額外重試），用盡 → Blocked（AC-D16）。

#### 6.4 Pass

三 gates 的 current assessment 皆 passed 且同一 version_key、無未解 blocking finding、re-read 一致 → 寫 `pass_history` 並產生 PR Pass package（AC-O10）。Task succeeded、通知、idle、input_accepted 永不進入 gate 計算（AC-G01, G02）。

### 7. Finding lifecycle [建議；權威與權限為已定]

欄位：`id`（controller 配發 `F-0001`）、source、severity、blocking、location、problem、basis、expected、status、fix_commits、rechecks、dispute、closure、lineage。

```text
open ──fix_submitted──> fix_submitted ──reviewer recheck ok──> resolved
  │                          └──recheck still failing──> open (failed_rechecks+1)
  ├──disputed──> disputed ──一次獨立覆核接受──> resolved
  │                   └──覆核維持──> dispute_upheld → Blocked
  ├──human waive/resolve decision──> waived / resolved
resolved ──reviewer 以依據標為同一缺陷再現──> reopened → open（reopen_count+1）
```

- Closure 只接受當前版本的 Reviewer 結果或指定 finding＋版本的人工 decision（AC-F03, F04）。
- Identity：Reviewer 以 `matches: F-000x` 指認同一問題，未指認者配新 ID；不以位置或文字自動合併（AC-F02, F16）。偏好類不得 blocking（AC-F01）。
- Correction batch：收齊同版本 G2/G3 後建立；**派修 operation 登記時** round+1；result 缺任一 finding 回應 → 不完整（AC-F05–F07）。Base 衝突（§5.3 R-base）作為 batch 項目。
- Dispute：每 finding 至多一次覆核，restart 不重置，不增 round；伴隨新 head 先過 G1（AC-F08–F10）。
- Recurrence [建議]：`failed_rechecks ≥ 2` 或任一次 `reopened` → 下次派修前 Blocked（AC-F15, F16）。
- 人工退回：`source=human_acceptance`、來源 identity 去重、失效 Pass、沿用 feature 剩餘 rounds（AC-F11）；scope 外或 spec 錯誤 → 交 Project Lead/使用者（AC-F12, O07）。

### 8. 持久化：snapshot、durable blobs、events（DR-09）[建議]

**Durable blob 協定** `put_blob(bytes) -> (path, digest)`：
1. 需要時建立目錄；新建目錄後 fsync 其父目錄。
2. 同目錄以 `O_CREAT|O_EXCL` 建 tmp，寫入全部 bytes，`fsync`（macOS 用 `F_FULLFSYNC`）。
3. `os.link(tmp, final)` 做不可覆寫發布。已存在時比對 digest：相同 → 冪等成功；不同 → 保留雙方（`*.conflict-<sha>`）並 Blocked（AC-D08）。
4. fsync 目錄 → unlink tmp → 再 fsync 目錄。
5. 只有 1–4 全部成功才回傳 durable handle。任何錯誤（ENOSPC、EIO）都中止該次轉移。

**提交屏障**：`commit_snapshot(next)` 驗證 `next` 引用的每個 blob 都是本 process 取得的 durable handle，或 load 時已驗證存在且 digest 相符，否則拒絕提交。Snapshot 本身：tmp → fsync → `os.replace` → fsync 目錄。外部操作只在登記它的 snapshot 提交**後**執行（§11）。Assignment、原始 log、receipt 全部走同一協定。

**Resume 引用完整性**：run.json 引用的每個 blob 必須存在且 digest 相符；缺失或損壞 → Blocked（state 不可信），保留現場，不繼續派工（AC-D11）。

**平台保證 [平台待實測]**：Linux ext4/xfs 上，file＋directory fsync 足以讓內容與名稱持久。macOS APFS 的 `fsync` 不清裝置快取，需對檔案用 `F_FULLFSYNC`；目錄 fd 是否支援 `F_FULLFSYNC` 待測，不支援時退回 `fsync` 並在能力報告標示。

**驗證範圍**（誠實區分）：
- (a) process 層級：以 SIGKILL 在隨機時點中斷的迴圈測試，檢查每次重啟後的不變式：snapshot 可解析、引用皆存在且 digest 相符、未登記 op 未發出。
- (b) 呼叫順序：在 Linux CI 以 `strace -f -e trace=fsync,fdatasync,link,rename,openat` 驗證所有 blob 與目錄的 fsync 都早於 snapshot rename。
- (c) 主機斷電或儲存 crash 的 durability **未驗證**，需 VM 硬重置環境，列為未覆蓋；`os._exit` 測試不宣稱驗過 power-loss。

**手改偵測**：載入時記 digest，提交前於鎖內比對；不符 → `manual_edit_detected`，以 schema 驗證後從 evidence＋decisions 重算 assessments，手改值不當決策（AC-D02）。Workers 因 §10 無法寫入 `.delivery/`；此偵測針對人工或 sandbox 外的修改。

**Events**：`pending_history` 隨 snapshot 提交，之後 append＋fsync，再於下一版清除；以 event ID 去重；尾筆殘缺 → 保存診斷副本並截斷；中段損壞或同 ID 內容衝突 → Blocked（AC-D10）。

### 9. Ownership、authority 與整合模型

#### 9.1 Feature authority locator 與預算 lineage（DR-06）[建議]

- `feature_id` = sha256(canonical repo_id＋feature_key)。repo_id 優先用 GitHub `owner/repo`；repo 目標未決或無 remote 時，用首個 commit SHA＋主 repo realpath，並記錄日後 remote 綁定的遷移 decision。
- 主機層級 `features/<feature_id>/authority.json` 保存 `{repo_id, feature_key, active_run_id, runs:[{run_id, state_dir, repo_path, status: active|terminal|abandoned, created_at}]}`：
  - 以 §8 協定寫入，只在持有 `features/<feature_id>/lock`（flock）時修改；
  - 位於 §10 對 workers 的拒寫區；
  - process 結束後仍保留，可供核對。
- **start/adopt**：先取 lock，再讀 authority。
  - 沒有 authority → 建立並登記新 run。
  - 有 active run，且呼叫端 repo_path 相符 → resume 該 run。
  - 有 active run，但 repo_path 不同（另一個 clone）→ 拒絕，並輸出已登記的 state_dir/repo_path。
  - 登記的 state_dir 缺失或不可讀 → Blocked，不建立空白替代 run。只有 `abandon_run` decision 可結束舊 run；該 decision 需附舊 worker handles 已停止或已 fenced 的證據。
- **預算 authority**：每個 run.json 保存自己的消耗。Feature 層的 active time、correction rounds、dispute 次數 = authority.runs 全部 run 的加總，D13 上限套用在這個加總上。任一 lineage run 不可讀 → Blocked。新 run 繼承已用額度（AC-D17, F07）。
- Repo-local `project.json` 只是檢視；run reconcile 後依 authority 修復，不能據它建立或覆蓋 authority（DUR-07）。
- 同一主機內可防止換 clone 取得第二份控制權；跨主機不支援，明示（AC-D11）。
- Process 存活由 flock 表示，只用於防止同時 step；控制權歸屬以 authority.json 為準。

#### 9.2 單一整合模型（DR-05）[建議]

- **唯一 writer**：整合 branch `delivery/<feature-slug>`（也是 PR head branch）在 controller 主 repo，只有 controller 寫；§10 使 workers 無法寫主 repo。
- **Attempt**：controller 以 `git clone --no-hardlinks --branch <integration> <主 repo> attempts/<run>/<attempt>/clone` 建立獨立 clone。起點 `T0` = 當時的整合 tip，記入 assignment。Worker 在自己的 clone commit，runner 在該 clone 寫 red refs。
- **`integrate` operation**（新 op kind）：
  1. `git fetch <clone> HEAD:refs/delivery/attempts/<run>/<attempt>` 與 red refs，可重做。
  2. 驗證 attempt 是 task 的當前 lease、`T0` 是 A 的祖先、`git diff --name-only T0..A` ⊆ scope。
  3. `git update-ref refs/heads/<integration> A T0`：以 old-value 做 compare-and-swap，只允許 fast-forward。
  4. 記 `integration.log` `{task, attempt, from: T0, to: A, op}`。
- **Crash 恢復**：op 為 in_flight 時讀 ref：== A → succeeded；== T0 → 重做；其他 → Blocked（`integration_conflict`）。依序兩個 task 時，task 2 的 T0 = task 1 整合後的 A。
- **Lineage**：task→integration mapping 即 `integration.log`。Red 的 parent P 必須是 A 的祖先；assignment 要求 worker 不改寫 P 以下的歷史。
- **舊 attempt 晚到**：attempt_id ≠ lease → 結果只存歷史；其 clone 不再 fetch，不能影響整合來源。這就是 fencing（AC-D04）。
- **整合 regression 失敗**：controller 在 H 的 Green 失敗 → G1 failed → correction（AC-G08）。
- **Push**：`push` op 用 `git push --force-with-lease=<integration>:<remote_old> origin <integration>`，以 `ls-remote` 查回；repo 目標未決時 push 為 Blocked。

### 10. Worker 的 OS 權限邊界（DR-01）[建議；平台待實測]

#### 10.1 邊界規則（每個 worker 皆適用：implementer、reviewer、N/A eligibility、retro）

Controller 以 sandbox launcher 啟動該 worker 的 runtime process。Profile 由 `sandbox.py` 依 assignment 產生，digest 記入 assignment 與 dispatch receipt。規則依序套用，後者優先：

| 類別 | 路徑／資源 | 規則 |
| --- | --- | --- |
| 預設 | 其他檔案 | 可讀 |
| 可寫 | 該 attempt 的 `clone/`、`rt/`（runtime state、HOME、TMPDIR）、`.delivery/runs/<run>/inbox/<attempt>/` | allow write |
| 拒寫 | controller 主 repo（含 `.git` common dir 與其 worktrees）、`.delivery/`（inbox 例外）、`$XDG_STATE_HOME/orca-delivery/features/`、其他 attempts、使用者全域設定目錄 | deny write |
| 拒讀 | `~/.config/gh`、`~/.ssh`、`~/.git-credentials`、`~/.netrc`、controller 的 token 檔 | deny read |
| env | 移除 `GH_TOKEN`、`GITHUB_TOKEN` 等；runtime 只拿到自身 LLM 認證 | scrub |
| 繼承 | runtime 的所有子程序、孫程序 | 同一 profile（sandbox 由 kernel 繼承） |

Reviewer 另外只有自己 clone 的寫權，沒有任何 push 路徑。Implementer 只能寫自己 clone，整合一律經 §9.2。

#### 10.2 Launcher 候選

| 平台 | 機制 | 現況 |
| --- | --- | --- |
| macOS | `sandbox-exec` Seatbelt profile（`deny file-write*`／`allow` 子路徑、`deny file-read*`） | 本輪 Darwin 27.0 tmp probe：直接寫、孫程序寫、寫 controller state、讀 credential 檔、把 inbox 改名移出皆被拒；寫自己 inbox 與工作目錄成功。Apple 標示 `sandbox-exec` 為 deprecated（風險）。未測：OpenCode server 在其下運作、keychain（`gh` 預設把 token 存 keychain）、網路 |
| Linux | bubblewrap（`--ro-bind / /`、`--bind` 可寫目錄、`--tmpfs` 遮蔽 credential 目錄）或 Landlock | 本機未安裝，未測（Q-PLATFORM） |
| 替代 | 每角色專用 OS UID＋檔案權限 | 需帳戶設定，屬使用者決定；本輪不做 |

#### 10.3 Verified 條件與失敗路徑

`isolation.status` 以 `(launcher, profile 模板 digest, OS 版本, runtime 名稱+版本)` 為 key 保存於 preflight 能力報告。只有同時滿足以下條件才是 `verified`：
1. 以該 launcher 與 profile 執行 §10.4 負例套件：所有拒絕項以 EPERM/EACCES（或 `gh`/`git` 的認證失敗）被拒，所有允許項成功。
2. 本次 assignment 的 dispatch receipt 證明 runtime process 由該 launcher 以相符 profile digest 啟動（launcher PID、argv、profile digest）。

未滿足時：
- Reviewer → isolation `unverified` → G2 unknown、Blocked 並列能力缺口。
- Implementer → 無法滿足 DUR-02 → 派工 Blocked。
- 不以事後 ref 比對、clone 或 env 清理升格，不默默放寬（AC-G12, D19）。

#### 10.4 負例套件（preflight 與 task 4.3）

每項以直接 shell 與孫程序（`python -c subprocess.run(...)`）各跑一次：
- 寫主 repo 工作樹檔案；
- 在主 repo 執行 `git update-ref refs/heads/<integration> …`；
- 寫 `.delivery/runs/<run>/run.json` 與 `blobs/`；
- 寫其他 attempt 的 inbox 與 clone；
- 寫 `authority.json`；
- 讀 `~/.config/gh/hosts.yml`；
- `gh auth token`；
- `git push origin`。

允許項：寫自己 clone、寫自己 inbox、在 clone 內跑測試。套件結果保存為 evidence（按平台、runtime 分開，AC-D22）。

**Controller authority 的保護**：因 workers 被拒寫 `.delivery/` 與 authority，偽造 state、evidence 或 decision 的路徑被 OS 拒絕。`delivery decide` 由人在 sandbox 外執行。

### 11. Outbox、dispatch 分段與 idempotency [建議]

Operation：`op_id`、`kind`（dispatch/integrate/push/pr_ensure/pr_comment/issue_comment/rerequest_ci/stop/retro）、target、payload_digest、marker、depends_on、`state`、`stage`（多段操作用）、attempts（receipt refs）、retries_used、readback。

通用流程：登記（pending）→ 執行前提交 in_flight → 呼叫 adapter → durable receipt → read-back → 提交終態。Crash 後 in_flight 一律視為 outcome_unknown，先以 marker 查回：查得 → 收斂；確定不存在 → 在 D13 預算內重試；查詢本身失敗 → 計入同 op 重試，用盡 → Blocked（AC-D12, D13）。

**Dispatch 分段（DR-07）**：每一段完成時各自提交 snapshot。

| Stage（持久化） | 外部動作 | Crash／unknown 後的恢復 |
| --- | --- | --- |
| `session_pending` | 建立 session（title 含 marker=attempt_id） | 以 marker 查 session：1 個 → `session_created`；多於 1 → Blocked；0 個 → 只有 preflight 證明 session 列表一致時才重建，否則 Blocked |
| `session_created(session_id)` | 尚未送 prompt | 直接送 prompt |
| `prompt_sending(prompt_marker, payload_digest)` | 送 prompt；首行為 `orca-delivery attempt=<id> payload=<digest>` | 列該 session messages：有 marker 且 digest 相符的 user message → `prompt_accepted`；找不到 → **不重送到同一 session**，發 `stop` 並確認停止後 fence 此 attempt，以新 attempt（新 clone）重派，計一次 infra retry；stop 無法確認 → Blocked |
| `prompt_accepted(native_message_id)` | runtime 已接受 | receipt 未存時由 messages 列表補存 |
| `running` → `completed/failed` | 等待 result／status | 完成只看 inbox result 或 adapter collect；idle ≠ completed |

外部呼叫次數不變式（測試斷言）：每個 attempt 建立 session ≤1 次，除非查回已證明 0 個；每個 session 送 prompt ≤1 次。舊 attempt 即使事後收到 prompt，也因 §9.2 fencing 無法影響整合。

**Marker 表**：

| 操作 | Marker 與查回 |
| --- | --- |
| GitHub comment／review | 內文 `<!-- orca-delivery op=<op_id> run=<run_id> result=<result_id> -->`；列全部分頁比對 |
| pr_ensure | body marker＋以 head branch 查 PR |
| push | `ls-remote` 比對 |
| integrate | 讀整合 ref（§9.2） |
| retro | acceptance decision ID＋version_key（AC-O14） |

Publication 與 verdict 分離：pr_comment → issue_comment（`depends_on` PR comment URL）；失敗只重試該 op（AC-F13, F14）。通知只觸發 reconcile（AC-D07, D21）。不宣稱外部 exactly-once。

### 12. 預算、timeout 與 native retries [D13 已定；算法為建議]

- **Active time**：活動區間（worker running、CI wait、controller op in_flight）的聯集；等待人工且無活動時不計。上限套用在 feature 累計值（§9.1）。
- **Crash 間隔**：崩潰前開啟的活動區間 `[last_persisted_at, resume_at]` 全額計入 unknown；只有所有開啟活動都有外部結束時間，才截至其最大值（AC-D17）。
- **到限**：停止新派工 → 對存活 workers 發 stop 並確認 → Blocked。只有 `budget_extension` decision 可延長；新 run 不重置。
- **Timeout**（45/30/30，未核准預設）：查 status → stop → 確認停止才算一次 infra 失敗並重派；status unknown → Blocked（AC-D04）。
- **Infra vs correction**：runner 或 adapter 可分類的程式或測試失敗走 correction；傳輸、逾時、服務不可用走 infra retry（AC-D16）。
- **Native retries**：屬於單一 controller 操作 attempt 的內部行為，不計入 D13 次數，但計入 timeout 與 active time。Receipt 記錄可得的次數，可設定的 native 上限設為有限值；實際行為待 preflight 實測。

### 13. Adapters 與選配 runtime [D30/D38 已定；介面為建議]

Runtime 協定：`preflight(profile)`、`create_session(marker)`、`find_sessions(marker)`、`send_prompt(session, text)`、`list_messages(session)`、`status(session)`、`stop(session)`、`collect(session)`。Dispatch 由 outbox 依 §11 分段呼叫。缺 result 檔時由 adapter 從最後一則 assistant message 擷取，producer 記 adapter（AC-D06）。

- **OpenCode（預設）**：每個 worker 一個 `opencode serve`，經 §10 launcher 啟動（localhost、隨機 Basic auth、該 attempt 的 `rt/`）。所需能力：health、建立與列 session、以 `{provider, model}` 送 prompt、列 messages、abort。**具體 path 從 1.18.32 `/doc` 快照釘住，本設計不假設**；actual model 欄位、session 父子關係、session 列表一致性、native retry 設定皆待核對。
- **選配**：Orca、Claude Code、Codex CLI 只在被選用時載入與 preflight；未選用者的缺失不影響（AC-D20, D23）。Native IDs 放 `attempt.native`（AC-D21）；各接法的能力報告與 isolation 報告分開保存（AC-D22）。
- **GitHub**：`gh api`（controller 在 sandbox 外執行），分頁取完；fake 支援回應遺失、5xx、分頁、多 attempt、未知 app、merge mapping。
- **Git／runner**：clone、fetch、ancestry、merge-tree、temp-index snapshot、update-ref CAS、ls-remote、push。

### 14. 方法與 skills 接合 [Q-METHOD 候選，建議]

- 以 OpenSpec `tasks.md` 為唯一 plan，補 Writing Plans（Superpowers 6.3.0，sha256 `48508f44…`）的 Files、Interfaces、Red/Green、驗法。不沿用其預設路徑；Execution Handoff 改由 controller 或協作者承接；OpenSpec apply 只能以指定 task IDs 受限呼叫。
- TDD 採 Superpowers test-driven-development（D26，sha256 `bf1b8216…`）；其「設定檔可例外」不適用，豁免只走 N/A eligibility。
- `orchestrate` skill 是薄 router，呼叫 `delivery` CLI；user-only skills 不在背景呼叫（D28）。

## Risks / Trade-offs

- [`sandbox-exec` 已被 Apple 標 deprecated；Linux 需 bubblewrap] → verified 只綁已測的 launcher/OS/runtime；未通過即 Blocked，不降級。替代為專用 UID（需使用者決定帳戶設定）。
- [Sandbox 需允許 runtime 自身的 state 與網路] → runtime 寫入導向 `rt/`；runtime 若需要其他寫入路徑，須在 preflight 列出並經負例套件核對，不直接放寬。
- [Red replay 在環境相依測試上無法重現] → G1 unknown 交人裁決。
- [任何 binding digest 變更都回 awaiting_approval，且 G2 必須新契約 review] → 人工確認與 review 成本較多；換來新契約不會取得舊 G2 clean（DR-10）。新契約 review 可聚焦 binding 差異，但仍是完整的獨立 G2 assignment。
- [Snapshot 遇 scope 外或被修改的 tracked 排除檔即拒絕] → worker 須先清理才能留 Red；換來違禁內容不會先存入 snapshot 再判 invalid（DR-04）。
- [R-base 的 merge-tree＋重跑增加 CI 前成本] → 換來 base 變動不無條件沿用 G1。
- [Per-attempt clone 佔磁碟] → run terminal 後清理（保留 evidence 與 refs）。
- [Authority 只在單一主機] → 跨主機不支援，明示。
- [Dispatch 無法證明 prompt 未送達時以 fence＋新 attempt 取代重送] → 耗一次 infra retry；換來同一 session 不會重複收到 prompt。
- [3 PR 切片受 D27 等待] → 等待期可準備 spec/design。
- [Bootstrap 期間 controller 不存在] → 協作者依相同契約協調，證據標 `coordinated_by=collaborator`。

## Migration Plan

新 repo 內新增程式，無既有資料遷移。`schema_version=1` 起算；後續變更需 migration 函式與測試，resume 遇未知版本 Blocked。Repo 目標未決期間的 `repo_id`（first commit＋realpath）改綁 GitHub 時，以 decision 記錄遷移。回滾 = 不使用 controller（狀態檔保留為紀錄）。

## Open Questions

D40 已確認 v3 技術方案、三個 PR 與 private `yschiang/orca-delivery`；其餘問題按切片處理，不重問 D11：

- S1：實作 N-V3-01 澄清與測試，G1 做確定性證據核對，method_changed 的語意由新契約 G2 審查；不得形成 G1/G2 依賴循環。
- S2 前：核對 OpenCode reviewer 精確 provider/model、sandbox/keychain/網路能力；指定 GitHub adapter 測試 repo。缺能力維持 fail-closed。
- Linux launcher／Windows 與 power-loss 的限制依原設計保留；候選機制與小型 probe 不等於產品驗收。
