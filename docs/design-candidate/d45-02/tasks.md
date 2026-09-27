# Tasks：implement-delivery-loop 薄 controller（D45 候選 design-02）

> **狀態**：候選計畫，尚未 review，也未經 D11 開工確認。**不授權產品實作**。本檔是 OpenSpec 唯一的 tasks 權威候選，不另外產生平行 plan。
> **方法適配**：採用 Superpowers writing-plans 6.4.1 的做法，包括 scope、檔案與介面、test-first、Global Constraints、Review Focus，以及小而可審的 commit。與原版不同之處：
> - 路徑改為 OpenSpec `tasks.md`。
> - 依協調者指示，每個 task 只寫具名公開介面、命令、可觀察的 Red／Green 案例與相依關係，不內嵌完整實作或完整測試碼。完整測試碼在派工時由 Implementer 依本檔案例撰寫，Reviewer 對照本檔檢查。
> - 步驟用編號清單，不用巢狀 checkbox，避免 OpenSpec apply 把步驟誤算成 task。
> - Execution Handoff **不**呼叫 subagent-driven-development 或 executing-plans。D11 後，由 orchestrate（bootstrap 期間依 D39 由協作者）逐 task 派給 Opus 5.5 Implementer，再由 GPT Reviewer 獨立審查。
>
> 這是方法適配，不是原 skill 原樣呼叫。

**Goal**：在隔離的新工作區（D46）建立唯一入口 `loopctl`：可讀的 feature 狀態、執行許可與讀回、三 gates、findings 與預算規則，並以 fake 的外部程式證明 H1 核心與負例。

**Architecture**：controller 每次被呼叫都是短命的 CLI。外部效果由 `loopctl tool …` 以固定 argv 執行一次，並經 `loopctl.api` 記錄。規則單位依提取契約帶入舊碼，並附新測試。詳見 [design.md](design.md)。

**Tech Stack**：
- Python 3.12、uv、pytest、ruff、mypy（strict）；
- 唯一第三方依賴是 PyYAML；
- 真 git 用於暫存 repo 的測試；
- fake `herdr`／`gh` 是放在測試 PATH 上的可執行檔，只記錄 argv 並依情境檔回應。

**Spec**：
- 正式 specs 在 `openspec/changes/implement-delivery-loop/specs/**`，修訂候選見 [spec-delta.md](spec-delta.md)；
- 對照見 [coverage.md](coverage.md)；
- 驗證見 [validation.md](validation.md)；
- 清理見 [cleanup-map.md](cleanup-map.md)。

## Global Constraints

- 新樹只有一個 console script：`loopctl = loopctl.cli:main`。
  - 不存在 `delivery` 套件，也不存在 `legacy/`、`v2/`；
  - 不設定指向舊 src 的 PYTHONPATH，不用 editable 依賴（D46）。
- 核心程式碼不 import `subprocess` 與 `loopctl.tools`。外部呼叫只在 `loopctl/tools/`，每次執行恰好一次，不自行重試。
- 所有 CLI 的 stdout 是單一 JSON 物件，欄位固定為 `ok`、`revision`、`result`、`blocked`、`next_action`、`safety_actions`。
- Exit code：0 成功、1 拒絕、2 用法錯誤、3 Blocked 或被 guard 拒絕、4 not_owner、5 狀態不可信。
- `schema_version=1`。未知版本、缺檔或壞檔一律 exit 5，永不重建空狀態。
- 上限：
  - D13：4h active、3 輪 correction、每個 operation 最多 3 次嘗試（初次＋2 次）。
  - 每個已 begin 的 attempt 最多自動讀回 3 次，每次自動 reconcile 呼叫都計入，包括結果為 `in_progress` 的那次；到限就 Blocked，並停止自動讀回（D45-S06）。
  - 目前查無外部效果，不等於可以重試。Herdr socket 與 GitHub 請求時，client 已結束也不算證明（D45-S03）。
  - D47：線上以有界方式停止；離線時在恢復時如實計入並 Blocked。
  - 45/30/30 分鐘 timeout 是待 D11 確認的預設值。
- D48：原始 Red 必要，replay 與 transcript 只是補充。只承諾對「可核對的不一致」保存證據並 Blocked；不承諾偵測同一 OS 帳號下協同的整套偽造。
- D49：CI 政策來源是可讀的 repo 規則，或本 repo 人工 `policy_change` 決策綁定的 `workflow.yaml` 集合。403 不自動 fallback。check 集合是 D11 候選（validation.md §4）。
- **Red 必須是行為失敗**：先放介面 stub（`raise NotImplementedError`），再讓測試失敗。ImportError 或 collection error 不算 Red。提取的碼若帶缺陷，要先以「未修正的提取碼」重現缺陷（defect-red），再修正。
- **Bootstrap 證據**：H1 期間 `loopctl` 還無法自證。每個 task 的 Red／Green 原始輸出、命令、HEAD／tree、exit 與 hash，由協作者存到 `.delivery/bootstrap/thin-h1/evidence/<task-id>/`（不進 Git），索引放 `docs/validation/h1/index.md`。

## Review Focus

以下五類輸入不在 spec 明文中，最可能讓人踩到。每行指定一個負責的 task，並在該 task 加入測試：

1. 兩個 `loopctl` 程序同時提交同一 feature → 只有一個成功，另一個回 `RevisionConflict`，也就是 exit 3，而不是寫壞檔案。（2.1）
2. `LOOPCTL_HOME` 路徑含空白或 Unicode → 所有命令仍正確。（1.1）
3. 系統時鐘倒退，或主機睡眠後恢復 → active time 不為負、不重複計算，gap 保守計入。（11.1）
4. 同名 check 來自不同 app、分頁超過 100 筆、舊 attempt 成功但新 attempt 仍 pending → 不放行。（9.1）
5. result 檔很大、不是 UTF-8 或不是 JSON object → 原件保存並拒絕，不 crash。（7.1）

## 切片與相依

| 群組 | 內容 | 相依 |
| --- | --- | --- |
| 0 | H1-0 前置（協作者） | 使用者採用本 plan＋D11 |
| 1–4 | 骨架、FeatureStore、協調權／epoch、operations | 0 → 1 → 2 → 3 → 4 |
| 5–7 | versions、decisions／plan、assignment／result | 4 |
| CP-1 | 核心整合 checkpoint | 1–7 |
| 8–11 | 證據與 Red、gates、findings／correction、budget | CP-1；9 依賴 8 |
| 12–13 | 下一步引擎、外部工具接合 | 8–11；13 依賴 12 |
| 14–15 | H1 情境、清理、文件、發佈物 smoke、H1 整合、獨立 review、bootstrap gate 紀錄 | 12–13；15.4 另需 D11 核准 check 集合與 `policy_change` 綁定 |
| 16–17 | H2／H3 範圍與能力標準（outline） | H1 accepted |

H1 只證明核心規則與 fake 負例，**不**證明真實 Herdr、runtime、GitHub 或 E2E。H2／H3 的義務在第 16、17 節。

## 0. H1-0 前置（協作者；需採用＋D11）

- [ ] 0.1 依 design §1 W1 建立 `loop-engineering-thin` 的 git worktree（branch `delivery/thin-controller`）；第一個 commit 移除舊 `src/delivery/`、`tests/` 與舊 CI 對 `delivery` 的設定，新增 `docs/implementation/removed-s1.md`。驗法：`git -C <thin> ls-files src tests` 為空；`removed-s1.md` 列出 `4ce1110`、`5d334d5`、PR #2 與證據封存路徑。
- [ ] 0.2 建立 `docs/implementation/extraction-manifest.json`（空陣列＋schema 說明）與 `docs/validation/h1/index.md`。驗法：JSON 可解析；index 列出所有 H1 task-id。
- [ ] 0.3 新增候選 CI workflow `.github/workflows/loopctl-ci.yml`（job 身份、checkout 與受測 SHA 規則見 validation §4）：
  - PR build 明確 checkout PR head SHA，push build 用 pushed SHA；
  - checkout 後比對實際 `git rev-parse HEAD` 與預期 SHA，不符就 fail；
  - 上傳 `tested-sha` 產物（D45-S08）。

  在 D11 核准集合、且 `policy_change` 綁定之前，G3 為 unknown。驗法：push 後 GitHub 可讀到三個 check-run 與各自的 `tested-sha` 產物；在 validation 記錄 run URL。

## 1. H1-1 骨架與單一入口

- [ ] 1.1 `loopctl` 套件、JSON envelope 與 exit code、清潔度守門測試、發佈物 smoke（D45-S07）。驗法：
  - `uv run pytest tests/test_cli.py tests/test_cleanliness.py -q` 通過，`uv run ruff check . && uv run mypy src` 為 0；
  - `scripts/dist-smoke.sh` 通過。它依序執行 `uv build`、在全新 venv 以 `pip install dist/*.whl` 安裝（不設 PYTHONPATH），再於 source checkout 外的暫存目錄執行已安裝的 `loopctl inspect --feature f-missing`：須回 exit 5 並輸出 JSON，且 `python -c "import loopctl.tools"` 成功。wheel 的 sha256 與命令／exit 記入證據。
  - **Files**：`pyproject.toml`、`src/loopctl/__init__.py`、`src/loopctl/__main__.py`、`src/loopctl/cli.py`、`src/loopctl/tools/__init__.py`（tools 套件骨架，只放 docstring，沒有行為；task 13 才加入工具模組，D45-S07）、`tests/test_cli.py`、`tests/test_cleanliness.py`、`scripts/dist-smoke.sh`
  - **Produces**：
    - `loopctl.tools` 套件骨架，讓發佈物 smoke 在 task 1.1 就能 `import loopctl.tools`；task 15.2 再對完整套件重跑 smoke
    - `cli.main(argv: list[str] | None = None) -> int`
    - `cli.emit(ok: bool, *, revision: int | None, result: dict, blocked: list, next_action: dict | None, safety_actions: list) -> str`
    - 常數 `EXIT = {"ok": 0, "rejected": 1, "usage": 2, "blocked": 3, "not_owner": 4, "untrusted": 5}`
  - **Red 案例**：
    - `inspect --feature f-missing` 在含空白與 Unicode 的 `LOOPCTL_HOME` 下回 exit 5，JSON 的 `result.error == "StateMissing"`，且欄位集合恰好是 envelope 六欄；
    - 缺參數時 exit 2；
    - AST 掃描核心沒有 `subprocess`／`loopctl.tools`；
    - `import delivery` 產生 ModuleNotFoundError；
    - `pyproject` 的 scripts 恰好是 `{"loopctl": "loopctl.cli:main"}`。
  - **Commit**：`feat(cli): single loopctl entry with JSON envelope and cleanliness guard`

## 2. H1-2 FeatureStore

- [ ] 2.1 History-first 提交、typed BlobRef、不可信狀態錯誤、手改偵測與 restore、以 `transition.id` 拒絕同 ID 不同內容。驗法：`uv run pytest tests/test_store.py -q` 通過。
  - **Files**：`src/loopctl/store.py`、`tests/test_store.py`
  - **Extraction**：X-01 `src/delivery/store.py` 的 `_full_fsync`、`_write_tmp`、`put_blob` 的 link 協定（design §4、cleanup-map §4）。
  - **Produces**：
    - `digest(data: bytes) -> str`
    - `blob(d: str) -> dict`
    - `feature_id(repo_id: str, feature_key: str) -> str`
    - `FeatureStore(root: Path)`，方法：
      - `.put(data) -> dict`
      - `.get(ref) -> bytes`
      - `.locked()`
      - `.create(state) -> int`
      - `.load() -> Loaded(state, revision, warnings)`
      - `.commit(state, expect_revision) -> int`
      - `.restore_committed(now) -> int`
    - 例外：`StateMissing`、`StateCorrupt`、`SchemaMismatch`、`IntegrityError`、`ManualEditDetected`、`RevisionConflict`
  - **Red 案例**：
    - S1-R06：字串欄位 `*_digest` 不必存在於 objects，create 成功；BlobRef 指向不存在的物件時 commit 拋 IntegrityError。
    - S1-R04：patch `os.replace` 讓它在寫完 history 後中斷 → load 仍是 rev 1，並出現 warning `orphan_revision:2`；下一次 commit 成功，orphan 移到 `history/orphans/`。
    - S1-R03：同一 `transition.id` 以不同內容提交 → IntegrityError。
    - AC-D11：缺檔、壞 JSON、`schema_version=9` 分別拋對應例外，原檔不變、不建立新檔。
    - AC-D02：直接改 `feature.json` → ManualEditDetected；`restore_committed` 後現行內容等於最後提交版本，被拒內容存成 blob。
    - Review Focus 1：兩個 process 以同一 `expect_revision` 提交，恰好一個成功。
  - **Commit**：`feat(store): history-first revisions and typed blob refs (S1-R03/R04/R06)`

## 3. H1-3 Feature 初始化、協調權與 epoch

- [ ] 3.1 `init-feature`、`claim`（只存 token digest）、人工 handoff、`abandon_epoch`；預算只在 feature 層。驗法：`uv run pytest tests/test_claim.py -q` 通過。
  - **Files**：`src/loopctl/state.py`、`src/loopctl/api.py`（本 task 起逐步擴充）、`tests/test_claim.py`
  - **Produces**：
    - `api.init_feature(home, *, repo_path, repo_id, feature_key, issue, integration_branch, now) -> dict`
    - `api.claim(home, fid, *, actor, now) -> tuple[dict, str]`
    - `api.inspect(home, fid, *, now) -> dict`
    - `state.require_owner(state, token) -> None`（不符拋 `NotOwner`）
    - CLI：`init-feature`、`claim`、`inspect`、`status`
  - **Red 案例**：
    - 第二次 `init-feature` exit 1，不覆蓋既有狀態；
    - 已有 active 協調者時，第二個 claim exit 4，並回傳現任 actor；
    - 狀態檔中找不到 token 明文；
    - 兩個 CLI 程序同時 claim，恰好一個取得 token（AC-D03）；
    - `abandon_epoch` 沒附 stop／fencing 證據時 exit 1；
    - S1-R08：設定 rounds=3 後 abandon 再開新 epoch，`budget.correction_rounds_used` 仍是 3，epochs 長度為 2。
  - **Commit**：`feat(state): single feature authority, coordinator claim and epochs (S1-R08)`

## 4. H1-4 Operation 與執行許可

- [ ] 4.1 prepare／begin／record／record_readback 的狀態轉移與重試上限。驗法：`uv run pytest tests/test_ops.py -q` 通過。
  - **Files**：`src/loopctl/ops.py`、`src/loopctl/api.py`、`tests/test_ops.py`
  - **Produces**：
    - `ops.prepare_op(state, kind, target_key, payload_digest, now, **detail) -> dict`
    - `ops.begin_op(state, op_id, now) -> {"execute", "attempt", "reason"}`
    - `ops.record_outcome(state, op_id, outcome: "succeeded" | "failed", receipt, now)`
    - `ops.record_readback(state, op_id, found: "present" | "absent" | "unknown", readback, now)`
    - `ops.MAX_ATTEMPTS = 3`，例外 `OpConflict`
    - `api.prepare`、`api.begin`、`api.record`、`api.record_readback`（後三者不是 CLI 命令）
  - **Red 案例**：
    - 同一 `payload_digest` 重送 prepare 回同一筆；不同 digest 拋 OpConflict；
    - 第二次 begin 回 `execute:false` 且原因含 `in_flight`；
    - 三次明確失敗後第四次 begin 回 `retries_exhausted`，並 Blocked（AC-D16、S1-R02）；
    - 已 begin、尚未 record 時做 readback `present` → succeeded，嘗試次數仍為 1（D45-R01）；
    - D45-S03，重試安全條件依 kind 判定：
      - `worktree_create`（Herdr socket 請求）讀回 `absent`，且 begin 持有者的 pgid 已不存在 → 仍是 outcome_unknown＋Blocked，begin 不給 attempt 2（D45-S03）。只有記錄了權威的未送達證據才可重試；
      - D45-S06，持有者仍存活：pgid 仍存活 → `in_progress`，狀態不變，但每次都佔一個讀回名額。連續三次 `in_progress` 後轉為 `blocked(readback_exhausted)`，第四次自動讀回被拒；active／unknown 保留，也不重送；
      - `agent_start`／`prompt`／`stop` 讀回 `absent` → 一律 outcome_unknown＋Blocked，不給重試；
      - `gh_publish_pr` 讀回查無 marker，且 begin 持有者的 pgid 已不存在 → 仍是 outcome_unknown＋Blocked（遠端請求可能晚到）。只有 begin 持有者記錄了確定未送達時，才是 failed 並可重試；
    - readback `unknown` → outcome_unknown＋Blocked，begin 被拒（AC-D13）；
    - D45-S06：同一 attempt 第 4 次自動讀回被拒，op 轉為 `blocked(readback_exhausted)`；人工 `resolve_operation recheck` 後可再讀回 3 次；
    - 對 `prepared` 狀態做 readback → OpConflict。
  - **Commit**：`feat(ops): single-consumer begin and readback without replay (S1-R02, D45-R01)`

## 5. H1-5 版本與 binding

- [ ] 5.1 提取 VersionSet、binding／observation 與依賴矩陣，並固定 skills×G3 為 R-reobserve。驗法：`uv run pytest tests/test_versions.py -q` 通過。
  - **Files**：`src/loopctl/versions.py`、`tests/test_versions.py`
  - **Extraction**：X-02 `src/delivery/versions.py` 的 `version_key`、`matrix_rows`、`observe_binding`、`derive`。
  - **Produces**：`version_set(state)`、`version_key(vs)`、`matrix_rows()`、`observe_binding(state, role, locator, content, now)`、`derive(assessment, old_vs, new_vs, reevaluate=None, base_recheck=None)`
  - **Red 案例**：
    - 相同 bytes 重讀 10 次 key 不變；改 1 byte → candidate＋`awaiting_approval`（AC-O03、G17）；
    - 矩陣的列等於 VersionSet 全部欄位，未列欄位 → stale；
    - base 改變但沒有 base_recheck → G1 stale；
    - 任何 key 改變時 G3 都是 pending（R-reobserve）；
    - 晚到的 H1 assessment 不能套用到 H2（AC-G16、D15）。
  - **Commit**：`feat(versions): extract version matrix with G3 always re-observed`

## 6. H1-6 Plan 登記與人工 decisions

- [ ] 6.1 `register`（plan＋tasks JSON＋producer／calibration 來源）與 `decide` 的各 kind。驗法：`uv run pytest tests/test_decisions.py -q` 通過。
  - **Files**：`src/loopctl/decisions.py`、`src/loopctl/api.py`、`tests/test_decisions.py`
  - **Produces**：
    - `api.register(home, fid, token, *, kind, role, locator, content, tasks=None, producer, now)`
    - `api.decide(home, fid, decision, *, now)`
    - `decisions.apply_decision(state, decision)`
    - 支援的 kind：approve_plan、revise、scope_change、adopt_binding、accept、return、resolve_finding、waive_finding、resolve_operation、budget_extension、policy_change、abandon_epoch、handoff、delegate、unblock
  - **Red 案例**：
    - S1-R07、AC-O06（本地轉移，CP-1 前可完成）：從未批准的狀態，經 `api.register` 與 `api.decide(approve_plan(plan_digest))` 之後：
      - `approval.plan_digest` 等於登記的 digest；
      - plan 的 producer 與校準來源保存下來；
      - phase 為 `implementing`；
      - 以 digest 不符的 plan 批准會被拒。

      「批准後公開路徑的第一個 next action」的整合斷言移到 12.1（D45-S10）；
    - AC-O22：producer 為 project_lead 的草案 plan，approve 被拒；
    - S1-R10、AC-O07：在 implementing 時送 scope_change 不 crash，approval 失效，回到 awaiting_approval；
    - `actor_kind=agent` 或缺 actor 時 exit 1；
    - AC-O10、O11：accept 必須指向目前 Pass 的 key，V2 的 acceptance 為 pending；
    - AC-F11：return 的 ac_defect 產生 `source=human_acceptance` 的 finding 並使 Pass 失效；
    - AC-F12：非 AC 缺陷 → Blocked，路由給 Project Lead；
    - AC-O18：delegate 範圍外的提議被拒；
    - D49：`policy_change` 綁定 policy binding digest。
  - **Commit**：`feat(decisions): plan provenance and human decisions via public path (S1-R07/R10)`

## 7. H1-7 Assignment 與 result 匯入

- [ ] 7.1 建立 assignment（修正與覆核附完整 finding 快照）、result 身份核對、去重與衝突。驗法：`uv run pytest tests/test_results.py -q` 通過。
  - **Files**：`src/loopctl/assignments.py`、`tests/test_results.py`
  - **Extraction**：X-03 `src/delivery/results.py` 的 `_identity_problems`，以及 duplicate／conflict 判定。
  - **Produces**：
    - `build_assignment(state, unit, role, profile, worktree, now) -> dict`
    - `identity_problems(result, assignment) -> list[str]`
    - `import_result(state, store, attempt_id, raw) -> ImportOutcome`
    - `api.record_result`
    - CLI：`record-result`、`tool result submit`（write-once）
  - **Red 案例**：
    - AC-D05：cwd、head、attempt 或 scope 不符 → 保留原件並拒絕，列出差異；
    - AC-D08：同 bytes 重送不產生新 revision；不同 bytes → 雙方都保存並 Blocked；
    - Review Focus 5：非 UTF-8 或非 object 的 result 被拒且原件保存；
    - S1-R12：fix 與覆核 assignment 內含每項 finding 的 problem、basis、expected、location、history、上次 review 與 fix evidence 的 BlobRef；
    - AC-D06：只有 native message 時，由工具寫成的 result 標 `producer=tool`，保存 native IDs；
    - AC-D21：外部 handles 與 run／task／attempt 分欄保存。
  - **Commit**：`feat(assignments): complete finding snapshots and deduplicated result import (S1-R12)`

**CP-1 核心整合 checkpoint**：
- 執行 `uv run pytest -q && uv run ruff check . && uv run mypy src`，本機與 CI 都跑；
- 更新 extraction manifest；
- 協作者核對 1–7 的 Red／Green 證據；
- 不做獨立 review，也不宣稱任何 gate。

## 8. H1-8 證據工具與原始 Red 核對

- [ ] 8.1 `tool evidence red|run` 只接受 policy 的 `command_id`；提取 snapshot 邏輯；逐項核對 Red。驗法：`uv run pytest tests/test_evidence_tool.py tests/test_evidence.py -q` 通過。
  - **Files**：`src/loopctl/tools/evidence.py`、`src/loopctl/evidence.py`、`tests/test_evidence_tool.py`、`tests/test_evidence.py`
  - **Extraction**：X-04 `src/delivery/runner.py` 的 `snapshot_worktree`、`_drifted`、`_classify`、`_case_ids`。
  - **Produces**：
    - `tools.evidence.run_policy_command(kind, command_id, policy, assignment, cwd) -> dict`
    - `evidence.red_problems(record, raw, attempt, policy, head, green_ids, is_ancestor, replay) -> list[str]`
    - CLI：`tool evidence red --assignment P --command-id ID`、`tool evidence run --op OP`
  - **Red 案例**：
    - S1-R01：傳入任意 argv（未知 command_id 或 `--` 後的命令）→ exit 1，且命令未執行（以 marker 檔不存在證明）；
    - snapshot 在真 git 中的行為：untracked 測試納入、已 stage 的排除檔略過、scope 外 → 拒絕且沒有 ref、測試期間檔案被改 → drift；
    - S1-R13：以 parametrize 逐一污染 stdout digest、stderr digest、exit、status、task_id、attempt_id、command_id／argv、producer、snapshot parent、failing id、replay，每一項都各自被拒；
    - AC-G07：只有 replay、沒有原始 Red → missing；
    - AC-G08：worker 回報的 green 不被採用。
  - **Commit**：`feat(evidence): policy-only commands and per-field original Red checks (S1-R01/R13)`

## 9. H1-9 Gates 與 Pass

- [ ] 9.1 提取 G1／G2／G3／Pass，加上獨立性核對、G3 route 與 D49 政策來源。驗法：`uv run pytest tests/test_gates.py tests/test_pass.py -q` 通過。
  - **Files**：`src/loopctl/gates.py`、`tests/test_gates.py`、`tests/test_pass.py`
  - **Extraction**：X-05 `src/delivery/gates.py` 的 `evaluate_g1`、`evaluate_g2`、`evaluate_g3`、`decide_pass`。
  - **Produces**：
    - `evaluate_g1(plan_tasks, green, head, is_ancestor, red_problems)`
    - `independent_review_ok(review, state, profile, capability) -> list[str]`
    - `evaluate_g2(...)`
    - `evaluate_g3(policy_source, head, base_tip, merge, checks, exceptions, decisions) -> {"status", "route", "reasons", "github_rules_verified"}`
    - `pass_blockers(state, observation) -> list[str]`
  - **Red 案例**：
    - S1-R11：plan 的 task 集合為空，或只看有變更的 task → G1 不 passed；
    - S1-R15、AC-G10：N/A eligibility 的 producer 是 implementer 或 model 不符 → 被拒；
    - AC-G11、G12：G2 需 reviewer session 獨立、model 從 native 讀回相符、capability 報告為 verified、read_digests 等於現行值；缺任一項 → unknown；
    - AC-G03：verdict 為 blocked → unknown，不開修正輪；
    - AC-G13：七種非成功狀態與空集合都不通過；
    - Review Focus 4：同名但不同 app、分頁、舊 attempt 成功而新 attempt pending，都不放行；
    - AC-G15：merge snapshot 的 parents 不符 → stale；
    - D45-S08：H≠M 的 PR 中，check-run metadata 的 `head_sha==H`，但 `tested-sha` 產物是 M 或缺失 → 不計入 head 來源，G3 為 stale／unknown；`tested-sha==H` 才計入；
    - S1-R14：403 且沒有 decision → `route=policy_unknown`；
    - D49：有 `policy_change` 的宣告集合且全部 success → passed，並帶 `github_rules_verified=false`；換成其他 repo 仍是 unknown；
    - S1-R17：例外設定含 failure，或沒有 decision → policy_invalid；
    - AC-G18、D45-R04：`pass_blockers` 在發布未完成、觀察早於判定，或觀察到的 key 不同時，都回非空。
  - **Commit**：`feat(gates): extract gates with independence, G3 routing and D49 source (S1-R11/R14/R15/R17)`

## 10. H1-10 Findings 與 correction

- [ ] 10.1 提取 registry、batch、一次爭議與反覆門檻；R16 reopen；修正資格包含文件缺陷與必要驗證缺失（D45-S01）。驗法：`uv run pytest tests/test_findings.py -q` 通過。
  - **Files**：`src/loopctl/findings.py`、`tests/test_findings.py`
  - **Extraction**：X-06 `src/delivery/findings.py`；X-07 `src/delivery/correction.py`。
  - **Produces**：
    - `import_review(registry, review, version_key)`、`submit_fix`、`close`、`open_blocking`
    - `ready_for_batch(g2, g3)`、`open_batch(state, version_key, finding_ids, ci_fixables)`、`check_responses`、`record_recheck`、`request_dispute`、`settle_dispute`
  - **Red 案例**：
    - AC-F01–F04：分類、`matches` 沿用 ID、thread resolved 不算 closure；
    - AC-F05：同版本 review 與 CI 收齊才開 batch，policy_unknown 不構成修正項；
    - D45-S01：Reviewer 指出文件中必要命令錯誤（`category=spec_ac`，只涉及文件）或缺必要驗證 → 可進 batch，round+1；
    - D45-S05：`open_batch(kind="pre_review_g1")` 不需要 G2／G3，登記時 round+1；rounds=3 時被拒；
    - AC-F06：回應缺項 → 不完整；
    - AC-F07：第四輪被拒；
    - AC-F08–F10：一次爭議、重送不重置次數、伴隨新 head 時先回 validating；
    - AC-F15：`failed_rechecks≥2` 在下次派修前 Blocked；
    - S1-R16、AC-F16：`matches` 指到 resolved → reopen，closure 移入歷史並 Blocked。
  - **Commit**：`feat(findings): extract registry and correction with reopen and document-defect eligibility (S1-R16, D45-S01)`

## 11. H1-11 預算與時間

- [ ] 11.1 提取 active 聯集；gap 計入、deadline、overrun、延長（D47）。驗法：`uv run pytest tests/test_budget.py -q` 通過。
  - **Files**：`src/loopctl/budget.py`、`tests/test_budget.py`
  - **Extraction**：X-08 `src/delivery/budget.py` 的 `active_seconds`、`on_resume`、`failure_route`，並選擇性提取 `test_overlapping_worker_and_ci_count_once`（cleanup-map §5）。
  - **Produces**：`open_activity`、`close_activity`、`active_seconds`、`account_gap(budget, last_touch, now, external_ends)`、`deadline_for(state, role, now)`、`exhausted(state, now)`、`failure_route(kind)`
  - **Red 案例**：
    - worker 與 CI 時間重疊只算一次；
    - 離線 3h 仍有未關閉 activity → 整段計入，超過 4h 時記錄 `overrun.seconds`；
    - Review Focus 3：時鐘倒退時計入值不為負；
    - deadline 等於 `min(role_timeout, remaining)`；
    - 只有 `budget_extension` 能延長。
  - **Commit**：`feat(budget): online deadlines and honest offline gap accounting (D47, S1-R09)`

## 12. H1-12 下一步引擎

- [ ] 12.1 `next_action` 與 `safety_actions`：到期 stop 優先、phase 路由、發布先於 Pass 觀察、adopt 與依賴。驗法：`uv run pytest tests/test_engine.py -q` 通過。
  - **Files**：`src/loopctl/engine.py`、`src/loopctl/api.py`、`tests/test_engine.py`
  - **Produces**：
    - `engine.next_action(state, now) -> {"next_action": dict | None, "safety_actions": list}`
    - `api.prepare` 只接受上述 ID
  - **Red 案例**（D45-R02）：
    - 到期的 active attempt 加上一個無關的 in-flight op，再加上既有 blocker → 第一個 action 是同一 attempt 的 stop；
    - stop 已 prepared → 執行同一 op_id；
    - stop 為 in_flight／unknown → reconcile，不重送；
    - stop failed 且沒有「安全重送」證據 → Blocked；
    - stop succeeded 但沒有停止證據 → Blocked；
    - D45-S06：stop 讀回用盡 3 次後，`safety_actions` 不再包含它，next action 為 Blocked，並附 `resolve_operation` 選項。
  - **Red 案例**（phase 與路由）：
    - S1-R07、AC-O06，公開路徑回歸（從 6.1 移來，D45-S10）：以 CLI 執行 `init-feature` → `claim` → `register` → `decide approve_plan` → `inspect`，`next_action` 是第一個 task 的 `worktree_create`。這一步不 mock engine；
    - AC-O01、O26：沒有 D11 → 0 個派工；
    - AC-O04：來源衝突 → Blocked；
    - AC-O08、O09：adopt 路由；
    - AC-O12、O13：依賴未 merge → wait；
    - AC-O23：受影響的 task 停派；
    - AC-O14：accept 只產生 1 個 retro op；
    - AC-O15：沒有明確開始就不產生 P03 action；
    - AC-F13、D45-R04：checking 且 gates 全過時，順序為 `gh_publish_pr` → `gh_publish_issue` → `gh_observe(pass)`；
    - D45-S04：版本 V 不變，CI 依序為 pending → pending → success 時，每個 succeeded 的週期之後 next action 都是 `observe_seq+1` 的新週期；重送 prepare 或 infra 重試沿用原 ID，不增加週期；Pass 觀察的 purpose 為 `pass`，是另一個週期；
    - D45-S05：validating 階段整合 Green 失敗且可歸因 → next action 是 `pre_review_g1` 的修正派工，不是 push 或正式 review；修正後重做 G1，passed 後才出現第一個正式 G2；缺原始 Red → Blocked；
    - AC-D04：worker 狀態 unknown → 不派替代 attempt；
    - AC-D14：部分完成時只接續剩餘工作。
  - **Commit**：`feat(engine): next action with due-stop priority and publication ordering (D45-R02/R04)`

## 13. H1-13 外部工具接合（真 git；fake herdr／gh 可執行檔）

- [ ] 13.1 `tools/common.execute_op` 與 `reconcile_op`；git worktree 與 integrate；herdr／gh 的 argv 與解析。以 PATH 上的 fake 可執行檔驗證。驗法：`uv run pytest tests/test_tools.py -q` 通過。
  - **Files**：
    - `src/loopctl/tools/common.py`、`src/loopctl/tools/git.py`、`src/loopctl/tools/herdr.py`、`src/loopctl/tools/gh.py`
    - `tests/fakes/bin/herdr`、`tests/fakes/bin/gh`、`tests/test_tools.py`
  - **Extraction**：X-09 `src/delivery/integration.py` 的檢查順序與 CAS。
  - **Produces**：
    - `execute_op(home, fid, token, op_id, call) -> dict`：內部 begin，執行一次，再 record。
    - `reconcile_op(home, fid, token, op_id, read) -> dict`：不經 begin。
    - CLI：`tool herdr|git|gh … --op` 與 `tool … reconcile --op`
  - **Red 案例**：
    - D45-R01：兩個 `loopctl tool gh observe --op X` 程序同時執行，fake `gh` 的呼叫計數恰為 1；
    - receipt 遺失後，`tool gh reconcile` 能收斂，副作用呼叫數不增加；
    - D45-S03 反例（不加產品測試 hook）：A 以 `tool herdr start --op X` begin 後呼叫 fake `herdr`。fake 在「真正建立 agent 之前」等待一個 release 檔；此時 B 執行 `tool herdr reconcile --op X`，fake 的查詢回 not found；接著建立 release 檔放行 A。斷言：B 只得到 `in_progress` 或 outcome_unknown，永遠拿不到重試許可；fake `herdr` 的 `agent start` 呼叫次數恰為 1；
    - D45-S06：fake `herdr pane process-info` 持續錯誤，或持續回報程序存活 → reconcile 呼叫次數固定為 3，之後 CLI 回 exit 3，op 為 `blocked(readback_exhausted)`；
    - D45-S06，持有者仍存活：`tool gh publish --op P` 呼叫 fake `gh` 後卡住不結束，begin 持有者仍存活。之後連續三次 `tool gh reconcile --op P` 都得到 `in_progress`，第四次 `inspect` 的 next action 與 safety actions 都不再包含它；fake `gh` 的發布呼叫次數仍是 1，op 為 `blocked(readback_exhausted)`；
    - D45-S03，Herdr socket：`tool herdr worktree --op W` 讓 fake `herdr` client 在送出後立即結束，fake server 延後才建立 worktree。reconcile 查無路徑 → outcome_unknown＋Blocked，沒有第二次 create；之後 server 完成建立，也沒有重複的 worktree；
    - S1-R05：worktree 的 path 已存在但 branch 或 HEAD 不符 → Blocked；
    - AC-G08、AC-D04：integrate 的 CAS，舊 attempt 不整合；
    - herdr argv 與 H0 形式相符（快照比對）；
    - `tool gh observe` 對每個 check-run 取回 `tested-sha` 產物並存入 observation（D45-S08）；
    - AC-D12、F14：publish 時 marker 已存在 → 不重貼；
    - 核心在 PATH 上沒有 `herdr` 時，`inspect`／`decide`／`assess` 仍可用（AC-D20 的 H1 部分）。
  - **Commit**：`feat(tools): single-shot git/herdr/gh operations with readback (S1-R05, D45-R01)`

## 14. H1-14 H1 情境測試

- [ ] 14.1 以 CLI 子程序跑 fake 端到端與負例清單（validation §3 的 V-H1-S*）。驗法：`uv run pytest tests/test_scenarios.py -q` 通過，並產生 junit。
  - **Files**：`tests/test_scenarios.py`、`tests/fakes/scenarios/*.json`
  - **Red 案例**：
    - 正常路徑到 Pass；
    - review clean 但 CI fail；
    - CI 綠但 review 失敗；
    - 自述 TDD 但缺證據；
    - 晚到的舊 SHA；
    - Pass 前 push；
    - 必要 check 缺或被取消；
    - 通知遺失；
    - 重複 result；
    - prompt 結果 unknown；
    - 發布失敗；
    - 協調程序中斷並 resume（含 prepare 後中斷的 stop）；
    - 修正輪次到限；
    - 文件或驗證 finding → fix → 獨立 re-review（D45-S01）；
    - 整合回歸 → pre-review 修正 → Green → 第一次正式 G2（D45-S05）；
    - 同一版本 CI 多週期觀察直到 success（D45-S04）；
    - 403 且無政策。

    每一項都斷言狀態欄位與外部呼叫次數。
  - **Commit**：`test(scenarios): H1 fake end-to-end and negative matrix`

## 15. H1-15 清理、文件與 H1 整合／獨立 review

- [ ] 15.1 清理完成條件（cleanup-map §6）：每個模組都有非測試的生產呼叫者；extraction manifest 涵蓋所有重用列；`docs/implementation/cli.md` 改寫為 loopctl 命令。驗法：`uv run pytest tests/test_cleanliness.py -q` 通過，含 `test_every_module_has_production_caller` 與 `test_manifest_covers_reuse_rows`。
- [ ] 15.2 H1 整合：本機與候選 CI 全綠，`scripts/dist-smoke.sh` 通過（D45-S07），並在 `docs/validation/h1/index.md` 記錄每個 task 的 Red／Green 證據路徑、CI run URL、`tested-sha` 與 wheel sha256。驗法：validation §3 各門檻成立；註明 check 集合在 D11 時的核准狀態。
- [ ] 15.3 獨立 review checkpoint：GPT Reviewer 以 head、base 與文件 digest 審查 H1 diff 與證據，依 D24 發布到 PR 與 issue。驗法：review 結果已保存，blocking findings 走修正與覆核循環。這是 bootstrap review，不冒充產品自己託管的 G2；S1-R01–R17 只有 Reviewer 能關閉。
- [ ] 15.4 H1 自身 PR 的 bootstrap gate 紀錄（D39、D45-S09）：協調者在 `docs/validation/h1/bootstrap-gates.md` 依實際要求逐項判定，不自動給過：
  - G1：每個 task 的原始 Red／Green 證據與 head 的 CI Green；
  - G2：15.3 對同一 head／base／文件 digest 的 clean 結論，且沒有未解的 blocking；
  - G3：D11 核准的集合加上 H1 期間記錄的 `policy_change` 綁定；head 上每個 check 都 success，且 `tested-sha==H`，顯示 `github_rules_verified=false`。

  缺政策核准或綁定、或缺有效 check 證據，G3 就是 unknown。紀錄交獨立 Reviewer 審查。驗法：紀錄已保存並經 Reviewer 審查；三 gates 同一 head 都成立，才可列為「bootstrap PR Pass 候選，待人工接受」。這不主張 loopctl 已能自我託管，H2 的 runtime、capability 與 self-hosted E2E 仍待證。

## 16. H2 範圍（outline；H1 accepted 後再細化成可派工 tasks）

每一項都要有真實證據；fake 證據不能沿用。

- [ ] 16.1 Herdr preflight 與 runtime profile：固定 Herdr／OpenCode／Claude Code 版本；說明正式 profile 如何在不使用 `--safe-mode`／`--pure` 的情況下載入核准 skills；固定 native transcript 讀回命令。能力標準：以真實 agent 讀回 model 與 marker。
- [ ] 16.2 Implementer 與 Reviewer 的權限負例：寫出 worktree／inbox、`git push`、`gh`、`herdr`、`loopctl decide|record` 都被拒，允許的動作成功。能力標準：產生 capability report，未驗證就 G2 unknown（AC-G12、D19、D24）。
- [ ] 16.3 真實 stop 與讀回：Claude Code 與 OpenCode 在推論中收到 stop，以 process-info 確認；確認不了就 Blocked（AC-D04、D17）。
- [ ] 16.4 gh 真實：分頁、app、attempt、merge mapping；403 的紀錄；marker 查回（AC-G13–G15、D12、F13、F14）。
- [ ] 16.5 CI 政策：沿用 H1 期間已記錄的 `policy_change` 綁定；若尚未記錄，就在 D11 核准後記錄。由 loopctl 自己計算 G3，Pass package 顯示 `github_rules_verified=false`（D49）。
- [ ] 16.6 orchestrate skill 與 references（AC-O16、O17）；DOC 審查清單。
- [ ] 16.7 本 repo 真實 E2E：issue → D11 → TDD → PR → review／CI → 至少一次真實 finding → fix → re-review → PR Pass，並示範中斷後 resume；沒有真實 finding 就記為未覆蓋（AC-G19、G20、A13）。

## 17. H3 範圍（outline）

- [ ] 17.1 cross-node-file-transfer 的 Project baseline、Phase 0、多個 features、人工驗收與 Retro，保留 worktrees 與證據（D43、AC-O20、O21、O24、O28）。Q-STACK 與 Q-DEMO-PEOPLE 仍待決；公司 OpenCode-only 環境（AC-D20、D22）列為未覆蓋。

## 自檢

- **Spec coverage**：每個 AC 與 S1 finding 都在 coverage.md 有規劃驗證。H1-F 項目落在 1–15；H2、H3、DOC 項目落在 16、17。
- **Placeholder scan**：沒有 TBD 或「類似 Task N」；未提供完整實作與完整測試碼是本次方法適配。
- **Type consistency**：`api.*`、`ops.*`、`engine.next_action`、`tools.common.execute_op`／`reconcile_op` 的名稱在各 task 一致。
- **Review Focus**：5 項都已落在各自負責的 task。
