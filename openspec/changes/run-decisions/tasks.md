# Tasks

本檔是 `run-decisions` 唯一的實作計畫。它不放實作碼：每個 task 列出要寫的測試、每個測試斷言的行為、Red 應該失敗在哪個斷言、Green 的預期結果，以及執行指令（D68）。介面與不變式見 [design.md](design.md)，以下用 D1～D14 引用它的章節。

## 共同規則

- **模型與模式**（D52、D72）：
  - 每個 task 都用預設模式，plan 寫到設計、介面、不變式與測試為止。
  - Implementer 是 Claude Opus 5.5。Reviewer 是 GPT-6 Astra（另一家廠商），每個 task 在新 session、新 clone 上唯讀審查。
  - effort 依 D69 的表，逐 task 標在下方。
- **順序**：依序實作 1.1 → 2.1 → 3.1 → 4.1 → 5.1 → 6.1（D13 實作序列）。依賴只從前往後，沒有循環。
- **Red 的規則**（D68）：
  - Red 必須是所列斷言的比較失敗（AssertionError）。ImportError、usage error、unknown command，或停在呼叫上的例外，都不算。harness 的 `Result` 會把未攔截的例外記在 `exc`，所以程式崩潰時，失敗也會落在第一個斷言上。
  - 每個 Red 以同一 task 前面的測試已經 Green 為前提。
  - 標「突變」的測試，預期會因為前面的實作而一寫就 Green。這時要以一次不提交的突變證明它會失敗在所列斷言上：暫時破壞表中寫明的行為，記下失敗，再還原。突變與輸出存成 Red 證據。
  - 沒有標「突變」的測試一寫就 Green → 停下，回報計畫有誤，不自行改測試。
- **每個 task 的完成條件**：
  - 在 task 的 head 上，`uv run pytest && uv run ruff check . && uv run mypy src` 全部通過，前面 task 的測試也包含在內。1.1 與 2.1 另外要 `scripts/dist-smoke.sh` 通過。
  - 逐 task 審查沒有未解的 blocking finding。
- **指令**：每張測試表註明檔案；單一測試的指令是 `uv run pytest <檔案> -k <名稱>`。pytest 的政策由 `pyproject.toml` 提供，所以不加任何旗標。
- **證據**：每個 task 的 Red 與 Green 原始紀錄（命令、完整輸出、exit code、commit）存在 `.delivery/run-decisions/<task>/attempt-<n>/`，這個目錄不進 Git。逐 task 審查的結果貼在 #29。
- **Commit**：
  - 格式：`<type>(<scope>): <祈使句>`，英文，不超過 72 字元，scope 用模組名。
  - `feat`、`fix`、`refactor` 的 body 要有 `Why:` 與 `Behavior:`。
  - 沒有 `Co-Authored-By` 或任何 AI 署名。
  - 每個 task 一到幾個 commit，各自綠燈。task 的核取方塊在它最後一個 commit 勾選。

### 共用檔案（依序擁有，不並行修改）

| 檔案 | 擁有順序 | 規則 |
| --- | --- | --- |
| `pyproject.toml`、`uv.lock` | 1.1 建立 → 2.1 加 dev 依賴 pyyaml | 兩者在同一個 commit 更新；全新 clone 的 `uv sync --frozen` 仍成功 |
| `tests/conftest.py` | 1.1 建立（政策、`home`、`repo`、`cli`、`cli_proc`）→ 3.1 加 `started_run` | 只新增 fixture，不改既有 fixture 的行為 |
| `src/loopctl/cli.py` | 1.1 建立（parser 與全部 stub）→ 3.1、4.1、5.1 依序把自己命令的 stub 換成實作 → 6.1 在 `status` 加 policy 狀態 | 不改參數與 envelope；`tests/test_cli.py` 仍通過 |
| `src/loopctl/store.py` | 3.1 建立 → 4.1 加 transition 冪等、衝突與 `resolves` | 4.1 不改讀取時的不可信原因與提交順序（D4） |
| `src/loopctl/next.py` | 3.1 → 4.1（衝突）→ 5.1（plan 阻擋、`dispatch`）→ 6.1（`plan_superseded`） | 只插入自己的判斷，保持 D7 的順序 |
| `src/loopctl/state.py` | 3.1 → 4.1（`conflicts`）→ 5.1（plan、binding、核准）→ 6.1（policy） | 只新增視圖欄位 |
| `src/loopctl/decisions.py` | 4.1 建立（完整 kind 表）→ 5.1（register、`approve_plan`）→ 6.1（`scope_change`、`policy_change`） | 不改共同核對的順序與紀錄欄位（D2、D10） |

### 總覽

| Task | 交付 | 依賴 | Implementer／Reviewer effort | AC |
| --- | --- | --- | --- | --- |
| 1.1 | 專案骨架、測試政策、CLI 入口與 stub、共用 fixture、dist-smoke | — | high／high | G21 |
| 2.1 | CI `unit-linux` 與 `workflow.yaml` | 1.1 | medium／high | G21、G22（宣告） |
| 3.1 | 持久的 run 狀態：`init`、`claim`、`status`、`next` | 1.1 | xhigh／xhigh | D01、D02、D03、D09、D10、D11、O01、O15 |
| 4.1 | 人工決策紀錄：`decide`、冪等、衝突與解除、`unsupported` | 3.1 | xhigh／xhigh | D02、D03、D10、D11、D25、O19、O30 |
| 5.1 | 登記原生文件與開工確認，核准後回報 `dispatch` | 4.1 | xhigh／xhigh | O01、O03、O05、O19、O22、O26、O29、D01 |
| 6.1 | 範圍變更與政策核准 | 5.1 | xhigh／xhigh | O01、O07、O23、G22 |

Effort 的依據（D69）：

- 2.1 只改 CI 與設定。
- 1.1 是一般行為。
- 3.1 與 4.1 出錯會遺失或損毀狀態，或破壞並行與故障恢復的保證。
- 5.1、6.1 守的是核准與政策這兩道授權；而且 5.1 涵蓋 6 列以上的 AC。

## 1. 共用測試骨架

- [ ] 1.1 建立專案骨架、測試政策、CLI 入口與 stub、共用 fixture；驗證：`uv run pytest && uv run ruff check . && uv run mypy src && scripts/dist-smoke.sh` 全部通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）high／high。

**交付**：

- `pyproject.toml`：
  - `uv_build`；`requires-python = ">=3.12,<3.13"`；`[project.scripts] loopctl = "loopctl.cli:main"`；
  - dev 依賴：pytest、ruff、mypy；
  - ruff 的 `select = ["E","F","I","B","UP"]`；mypy `strict = true`；
  - pytest 政策（D12）。
- `uv.lock`。
- `src/loopctl/{__init__,__main__,cli}.py`。parser 含 D2 的全部命令與參數，argparse 的錯誤轉成 exit 2 的 envelope。
- **stub 契約**：每個命令都回 exit 0，envelope 為 `ok: true`、`result: {}`，其餘欄位 `null`，不寫任何檔案。形狀正確，內容是空的；之後每個 Red 都能走到行為斷言。
- `tests/conftest.py`：
  - 政策 hook，平台由唯一的 `current_platform()` 決定；
  - autouse `home`：把 `LOOPCTL_HOME` 設到 `tmp_path`；
  - `repo`：範例文件（D13）；
  - `cli`：in-process；
  - `cli_proc`：子程序，支援 `prelude` 與 barrier。
- `scripts/dist-smoke.sh`。

**不在範圍**：任何狀態讀寫；`clock.py`，由 3.1 建立。

**擁有路徑**：上列各檔，以及 `tests/test_cli.py`、`tests/test_test_policy.py`。

**依賴**：無。base 是本計畫的 commit（`feature/run-decisions`：main `c91b774` 加上 spec、design 與本檔）。

**AC**：G21 的本機部分。

**Commits**：

1. `build: add the loopctl project skeleton and test policy`：pyproject、uv.lock、`__init__.py`、conftest 的政策與 `home`／`repo`、`test_test_policy.py`。
2. `feat(cli): add the loopctl entry point and JSON envelope`：其餘檔案。

`tests/test_test_policy.py`：以 pytester 開子 session。子 session 載入 repo 的 `tests/conftest.py` 與 `pyproject.toml` 的 `[tool.pytest.ini_options]` 原文，不另寫一份；平台以 `current_platform()` 模擬。

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_t1_only_on_foreign_platform_skips_and_session_passes` | 模擬 darwin 時，`only_on("linux")` 的案例 skip，另一個案例通過 | `ret == 0`：`only_on` 尚未註冊，`--strict-markers` 讓子 session 以 exit ≠ 0 結束 | skip 1、pass 1、`ret == 0` |
| `test_t2_skip_not_from_only_on_fails_session` | 參數：`only_on("linux")` 案例在 linux 上自行 `pytest.skip("missing tool")`；`skipif(True, reason="platform: linux only")`；`pytest.skip("platform")` | `ret != 0`：t1 的實作允許這些 skip，子 session exit 0 | `ret != 0`，summary 列出該案例 |
| `test_t4_zero_collected_fails_session` | 參數：空目錄；`-k` 全部濾掉 | 突變：暫時讓 `pytest_sessionfinish` 把 `NO_TESTS_COLLECTED` 改成 `OK` → 失敗在 `ret != 0` | `ret != 0` |
| `test_t5_xfail_and_xpass_fail_session` | 參數：一個 xfail、一個 xpass | `ret != 0`（xfail 參數）：非 strict 的 xfail 讓子 session exit 0 | 兩者 `ret != 0` |
| `test_t6_expected_platform_mismatch_fails_session` | `LOOPCTL_EXPECT_PLATFORM=linux`，模擬 darwin | `ret != 0`：尚未核對，exit 0 | `ret != 0`，summary 說明平台不符 |

`tests/test_cli.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_help_lists_every_command` | `--help` exit 0；stdout 以 `usage: loopctl` 開頭，列出 init、claim、status、next、register、decide、adopt、delegate | stdout 含 `usage: loopctl`：先建立空的 `main(argv) -> int`（回 0、不輸出） | 全部列出 |
| `test_each_command_prints_one_json_envelope` | 參數：8 個命令各帶最少的合法參數。stdout 恰一行 JSON 物件，鍵恰為 `ok, revision, result, blocked, next, safety`；stderr 為空 | stdout 恰一行：parser 已有子命令，但 handler 還沒輸出 | 每個命令都輸出單行 envelope；本測試不斷言 exit code，後面的 task 換掉 stub 後仍然成立 |
| `test_usage_errors_are_json_envelopes_with_exit_2` | 參數：沒有命令；`merge`；`init` 缺 `--repo`；`register other`；`--repo noslash`；`--repo ../x`；`--feature a/b`。每個都 exit 2，`ok` 為 false，`result.error == "usage"`，`result.message` 指出該參數或命令；stderr 沒有 argparse 的 usage 文字 | `result.error == "usage"`：argparse 預設丟出 `SystemExit(2)` 並寫 stderr，helper 記下 exit 2，但 stdout 是空的 | 全部參數通過 |
| `test_python_m_loopctl_matches_the_in_process_entry` | `cli_proc("--help")` 與 `cli_proc("status", …)` 的 exit 與 stdout，都和 in-process 相同 | `code == 0`：沒有 `__main__.py`，子程序 exit 1 | 相同 |

另外，`scripts/dist-smoke.sh`：

- Red：`[project.scripts]` 加入前，全新 venv 裡找不到 `loopctl`（exit 127）。
- Green：印出 `dist-smoke: ok`，exit 0；`import delivery` 失敗。

## 2. CI 與政策檔

- [ ] 2.1 建立 `unit-linux` 的 GitHub workflow 與 `workflow.yaml`，並檢查兩者的結構；驗證：`uv run pytest tests/test_ci.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）medium／high。

**交付**：

- `.github/workflows/loopctl-ci.yml` 與 `workflow.yaml`，內容照 D12。
- `tests/test_ci.py`。
- dev 依賴 pyyaml。
- runner label 與每個 action 的版本，依當時的 GitHub 文件核對，所用版本記在 commit body。label 不可用時回報，不自行替換。

**擁有路徑**：上列三個檔案，以及 `pyproject.toml`、`uv.lock`（依共用檔案規則）。

**依賴**：1.1，從它取得三個介面：

- 測試命令是不帶旗標的 `uv run pytest`，政策只來自 `pyproject.toml` 與 `tests/conftest.py`；
- `scripts/dist-smoke.sh` 可在任何 cwd 執行，exit 0 且印出 `dist-smoke: ok`；
- 全新 clone 上 `uv sync --frozen` 成功。

**AC**：G21 的 CI 部分；G22 的宣告部分（核准在 6.1）。

**Commit**：`ci: add the unit-linux required check and declare it in workflow.yaml`

`tests/test_ci.py`：讀檔的 helper 在檔案不存在時回 `{}`，所以 Red 落在斷言上。

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_workflow_yaml_declares_unit_linux_as_the_required_check` | `workflow.yaml` 的內容恰為 D12 的三個頂層鍵；`g3.required_checks == [{name: unit-linux, app: github-actions, workflow: .github/workflows/loopctl-ci.yml}]` | `required_checks` 相等：檔案不存在 | 相等 |
| `test_required_check_is_a_pull_request_job_running_the_policy_command` | 觸發、權限、runner 與 timeout 都照 D12；每個必要 check 都有同名 job，步驟順序照 D12；pytest 步驟的 `run` 恰為 `uv run pytest`，而且 env 有 `LOOPCTL_EXPECT_PLATFORM=linux`；每個 `uses:` 都釘到 40 位 SHA；沒有 commit-msg 步驟 | 「`unit-linux` 有同名 job」：CI 檔不存在 | 全部成立 |
| `test_pytest_policy_has_one_source` | 沒有 `pytest.ini`、`tox.ini`，`setup.cfg` 沒有 pytest 段，`tests/` 以外沒有 `conftest.py`；pyproject 含 `--strict-markers`、`xfail_strict = true` 與 `only_on` marker | 突變：暫時加一個 `pytest.ini` → 失敗在「沒有其他 pytest 設定檔」 | 成立 |

`unit-linux` 的實際執行在 to-pr 開 PR 時發生，是 G21 的 CI 證據。

## 3. 持久的 run 狀態

- [ ] 3.1 以 repo＋feature 為鍵的 history-first store，以及 `init`、`claim`、`status [--human]`、`next`；驗證：`uv run pytest tests/test_state.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `src/loopctl/store.py`：D3、D4。transition 冪等與衝突不在本 task，屬 4.1。
- `src/loopctl/state.py`：初始狀態、視圖、`--human`、token digest。
- `src/loopctl/next.py`：`derive`，本 task 只有 `unclaimed` 與 `plan_not_registered` 兩條。
- `src/loopctl/clock.py`。
- `cli.py` 裡 `init`、`claim`、`status`、`next` 的 handler。
- conftest 的 `started_run(repo, feature, actor) -> token`。
- token 用 `secrets.token_hex(32)`，以 `hmac.compare_digest` 比對。

**擁有路徑**：上列各檔，以及 `tests/test_state.py`。

**依賴**：1.1，從它取得三組介面：

- `main(argv) -> int`：只寫一行 envelope；exit code 照 D2。
- fixture：`cli`／`cli_proc` 回傳 `Result(code, out, stdout, stderr, exc)`；未攔截的例外使 `code is None`。另有 `home`、`repo`。
- `init`、`claim`、`status`、`next` 的參數固定，本 task 不改。

**AC**：D01（phase、owner、gate、blockers、next）、D02（手改）、D03、D09、D10（未提交的變更不被接受）、D11、O01（直接 `init` 後由 `claim` 保存協調者）、O15。

**Commit**：`feat(store): keep one durable state per repo and feature run`

`tests/test_state.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_init_creates_a_planning_run_per_repo_and_feature` | `init` exit 0、revision 1。`status` 回 repo、feature、issue、phase `planning`、owner `null`、三個 gate 為 `not_evaluated` 且原因非空、blockers `[unclaimed]`、next `{action: human, blockers: [unclaimed], decision_kinds: []}`。`runs/yschiang/loop-engineering/F-1/feature.json` 有相同的值，`history/1.json` 存在。另一個 repo 的同名 feature 也 exit 0，是另一個 run | `result.phase == "planning"`：stub 回 `{}` | 全部成立 |
| `test_status_human_renders_the_same_view` | `status --human` 的 `result.human` 逐行含 phase、owner（unclaimed）、每個 gate 的狀態與原因、blockers、next | `"human" in result` | 成立 |
| `test_init_never_overwrites_an_existing_run` | 同一 repo＋feature 再 `init`，issue 相同或不同都是 exit 1 `run_exists`；run 目錄的 bytes 不變 | `code == 1`：既有目錄讓 rename 失敗（記在 `exc`），或被覆寫 | 成立 |
| `test_uninitialised_run_is_not_found_and_nothing_is_created` | 另有 F-2 已 `init` 並 `claim`。對 F-9 執行 `status`、`next`、`claim` 都是 exit 1 `run_not_found`；`$LOOPCTL_HOME` 的快照不變 | `code == 1`（`next`）：stub 回 0 | 成立 |
| `test_exactly_one_concurrent_claim_wins_and_only_the_token_digest_is_stored` | 8 個 `cli_proc claim` 以不同 actor 同時開始：恰一個 exit 0，拿到 64 位 hex token；其餘 exit 1 `already_claimed`，並附得勝的 actor。落敗者執行 `status` 得到 exit 0、revision 2、得勝者為 owner。run 目錄裡沒有任何檔案含明文 token，`owner.token_digest` 是它的 sha256 | 得勝者恰為 1：stub 讓 8 個都 exit 0 | 成立 |
| `test_interrupt_after_history_keeps_the_new_revision_once` | `claim` 時以 prelude 把 `os.replace` 換成 `os._exit(9)` → exit 9。之後 `status` exit 0、revision 2、owner 已設定；再 `claim` → `already_claimed`；history 只有 `1.json`、`2.json` | `revision == 2`：讀取只看 `feature.json`，得到 1 | 成立 |
| `test_interrupt_before_history_keeps_the_old_revision` | 以 prelude 把 `os.link` 換成 `os._exit(9)` → exit 9；`status` 回 revision 1、owner `null`；再 `claim` exit 0、revision 2 | 突變：暫時改成先替換 `feature.json` 再寫 history → 失敗在 `revision == 1` | 成立 |
| `test_commit_with_a_stale_revision_writes_nothing` | `claim` 之後（rev 2），以 `store.commit(key, 1, …)` 提交 → `RevisionConflict`，run 目錄的 bytes 不變 | `pytest.raises(RevisionConflict)`；若 `claim` 已依 D4 核對 revision → 突變：暫時略過第 4 步 | 成立 |
| `test_untrusted_state_stops_with_reason_and_files` | 參數：刪掉 `feature.json`（`state_missing`）；壞 JSON（`state_corrupt`）；`schema_version: 9`（`unknown_schema:9`）；刪掉 `history/2.json`（`history_missing:2`）；空的 run 目錄（`state_missing`）。`status`、`next`、`claim`、`init` 都 exit 5，`result.error == "untrusted_state"`，`reason` 如上，`files` 等於現存檔案排序後的相對路徑；bytes 不變；`init` 不建立任何東西 | `code == 5`：讀取時的例外記在 `exc` | 成立 |
| `test_manual_edit_is_detected_and_never_trusted` | 參數：保持 JSON 與 schema 合法，但把 g1 改成 `passed`；把 phase 改成 `approved`；改 owner；插入一筆 `{kind: approve_plan, actor: human:x}` decision。`status`、`next`、`claim` 都 exit 5 `manual_edit`；輸出不含 `passed` 或 `approved`；bytes 不變 | `code == 5`：只核對 schema 時會照單全收 | 成立 |

## 4. 人工決策紀錄

- [ ] 4.1 `decide` 的共同核對與紀錄、transition 冪等與衝突、`resolve_conflict`、`budget_extension`、`revise`、`handoff`，以及 `adopt`／`delegate` 與後續 kind 的 `unsupported`；驗證：`uv run pytest tests/test_decisions.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `src/loopctl/decisions.py`：D10 的完整 kind 表與 D2 的核對順序。
  - `approve_plan`、`scope_change`、`policy_change` 在本 task 只做共同核對並記錄；它們的檢查與效果由 5.1、6.1 加上。這樣後面的 Red 會落在行為斷言上，不是 `unsupported`。
- `store.py`：D4 第 2、3 步、`resolves`、D6。
- `next.py`：衝突的 blocker。
- `state.py`：`conflicts` 視圖。
- `cli.py`：`decide`、`adopt`、`delegate` 的 handler。

**擁有路徑**：上列各檔，以及 `tests/test_decisions.py`。

**依賴**：3.1，從它取得：

- **store**：
  - `load(key) -> (rev, state)`，錯誤是 `RunNotFound`、`UntrustedState(reason, files)`；
  - `commit(key, expected_revision, transition_id, payload, mutate)`：在 flock 內核對 revision，history-first（先 `os.link` 再 `os.replace`）；`derive(mutate(state))` 等於現況時是 no-op；`mutate` 必須是純函式，拋出 `Rejected` 時不寫任何檔；
  - 呼叫端遇到 `RevisionConflict` 時重讀重做。
- **順序限制**：transition 冪等與衝突插在 revision 核對之前（D4），不改不可信原因與寫入順序。
- **fixture**：`started_run` 回傳 token。

**AC**：D02（decision 只經 `decide` 產生，帶來源與影響）、D03（寫入要 token）、D10、D11（衝突）、D25、O19、O30。

**Commit**：`feat(decisions): record human decisions once with their provenance`

`tests/test_decisions.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_a_human_decision_is_recorded_with_its_provenance` | 參數 `revise`、`handoff`：`human:alice` 帶齊欄位 → exit 0、revision +1；`status` 與 `feature.json` 的 `decisions[id]` 含 kind、actor、target、reason、source、impact、at、`seq == 1`；phase、owner、gates 不變 | `decisions[id].source == <值>`：stub 什麼都沒記 | 成立 |
| `test_only_human_actors_can_decide` | actor 為 `agent:implementer`、`project_lead`、`session:lead/child-1`、`human:`、`Human:alice`，kind 為 7 種 → exit 1 `actor_not_human`；revision 與 bytes 不變 | `code == 1`：前一個測試的實作照單全收 | 成立 |
| `test_missing_fields_are_rejected` | id、actor、target、reason、source、impact 逐一缺少 → exit 1 `missing_fields`，並列出缺的欄位；另外 `approve_plan`、`policy_change` 缺 `--version` 也一樣；狀態不變 | `code == 1`：缺的欄位記成 `null` | 成立 |
| `test_writes_need_the_coordinator_token` | 沒有 token 或 token 不符 → exit 4 `not_owner`，bytes 不變；同一個呼叫者 `status` exit 0 | `code == 4`：尚未核對 token | 成立 |
| `test_resending_a_decision_takes_effect_once` | 同一筆 decision 送兩次 → 第二次 exit 0、`result.duplicate` 為 true、revision 不變、只有一筆、`seq` 不變。另一情境：第一次以 prelude 讓 `os.replace` 中斷，重送後結果相同，revision 等於已提交的那版 | revision 不變：3.1 的 store 對同一個 id 再提交一次 | 成立 |
| `test_same_decision_id_with_other_content_blocks_the_run` | id X 先以 reason `a` 送出，再以 reason `b` 送出 → exit 3 `transition_conflict`。`conflicts[cid]` 含 transition_id、已提交的 revision 與 reason `b` 的完整 payload；`decisions[X].reason` 仍是 `a`。`status`、`next` 都 exit 3，blockers `[transition_conflict:<cid>]`、kinds `[resolve_conflict]`，`files` 含 `feature.json` 與 history。另一筆新的 decide → exit 3，不寫。重送 X/`a` → exit 0、duplicate | `code == 3`：前一個測試的實作把它當重送 | 成立 |
| `test_a_human_resolve_conflict_clears_the_block` | 接著人工 `resolve_conflict --target <cid>` → exit 0；`resolved_by` 等於該 decision 的 id，嘗試的 payload 仍保存；`status` exit 0，next 回到衝突前的值；新的 decide 可以寫入。agent 送出 → exit 1，仍 Blocked；未知的 `cid` → exit 1 `unknown_target` | `code == 0`：所有寫入都被擋，exit 3 | 成立 |
| `test_budget_extension_only_records_a_human_ruling` | 目標 `active:60`、`rounds:+1`、`attempts:1.1:+1`、`ci_wait:<40 hex>` → 各 exit 0，各一筆帶 actor 與 reason 的紀錄；`repo/workflow.yaml` 的 bytes 不變；`feature.json` 除了 `decisions`、`transitions`、`revision` 以外都不變。會被拒的（exit 1，revision 不變）：agent actor；缺 reason；目標 `active:0`、`rounds:+2`、`wallclock:30`、`ci_wait:abc` | `code == 1`（`rounds:+2`）：尚未核對目標 | 成立 |
| `test_adopt_delegate_and_later_kinds_are_unsupported` | 頂層 `adopt --repo R --feature F`、`delegate --to x`；`decide adopt`、`delegate`、`accept`、`return`、`resolve_read`、`resolve_operation`、`resolve_finding`、`nonsense`，帶與不帶 token → 都 exit 2，`result.error == "unsupported"` 並指出命令或 kind；`$LOOPCTL_HOME` 的 bytes 不變（owner、核准、revision 都相同） | `code == 2`：stub 回 0 | 成立 |

## 5. 登記原生文件與開工確認

- [ ] 5.1 `register plan|binding|policy`、`approve_plan` 的檢查與效果、`status` 顯示版本與核准，以及核准後的 `dispatch`；驗證：`uv run pytest tests/test_approval.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `decisions.py`：D9 的登記、D10 的 `approve_plan`，以及已核准時的 `scope_change_required`。
- `cli.py`：`register` 的 handler。在邊界讀取 locator 或 `--content-from`，並存成物件。
- `next.py`：D7 的 plan 阻擋與 `dispatch`（D8）。
- `state.py`：plan、binding、核准的視圖與 `--human` 的文字。

**擁有路徑**：上列各檔，以及 `tests/test_approval.py`。

**依賴**：4.1，從它取得三組介面：

- `decide` 的共同核對：順序依 D2；錯誤是 `unsupported`／`missing_fields`／`actor_not_human`／`not_owner`。
- 紀錄欄位與 `decide:<id>` 的 payload 冪等。
- 未解的衝突會擋下所有寫入，`register` 也包括在內。

3.1 的 store 與 `derive` 照舊。本 task 只把 `approve_plan` 的檢查與效果加進 mutate，不改共同核對。

**AC**：O01（直接交付不需要交接紀錄，協調者不能自己批准）、O03、O05、O19（`approve_plan` 的情境）、O22、O26、O29、D01（版本與核准）。

**Commit**：`feat(decisions): approve a calibrated plan with its bindings`

`tests/test_approval.py`：以 `repo` fixture 的文件為準。

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_native_documents_are_registered_in_place_and_read_back` | 登記：plan `tasks.md`（implementer，帶 `--calibrated-from`）；兩份 spec、ac、design；locator 為 issue URL、內容來自 `--content-from issue-29.md` 的 binding。每筆 exit 0，登記項的 role、locator（原樣）、version、source、`digest == sha256(內容)` 與物件引用都正確；`objects/<hex>` 的 bytes 等於登記的內容，改掉原檔之後仍然相等；`repo` 的檔案清單不變 | `plan.locator == "tasks.md"`：stub 沒有登記 | 成立 |
| `test_unreadable_documents_are_not_registered` | 參數：locator 不存在；locator 是目錄；URL 但沒有 `--content-from`；`--content-from` 不存在；`policy` 帶 `--content-from` → exit 1 `locator_unreadable`，revision 不變。另外，沒有 token 或 token 不符的 `register` → exit 4 `not_owner`，bytes 不變 | `code == 1`：讀檔的例外記在 `exc` | 成立 |
| `test_status_shows_versions_and_awaiting_approval` | 登記完成後：phase `awaiting_approval`；plan 的 locator、version、digest、producer、`calibrated_from`；spec、ac、design 各自的 version；`approval` 為 `{status: not_approved, plan_version: V}`；next 為 `human`、`[plan_not_approved]`、`[approve_plan]`；`feature.json` 相同；`--human` 含 plan、spec、design 的版本與核准這一行 | `result.approval == {status: not_approved, plan_version: V}`：視圖還沒有核准欄位 | 成立 |
| `test_only_a_human_approve_plan_on_a_calibrated_plan_approves` | run 以直接 `init` 建立，由 `agent:implementer` `claim`，沒有任何交接紀錄。<br>(a) 沒有 decision，時鐘前進 30 天 → 仍未核准。<br>(b) 登記帶 source 的 `sa` binding → 仍是 `awaiting_approval`。<br>(c) `approve_plan --actor agent:implementer` → `actor_not_human`。<br>(d) plan 由 `project_lead` 登記 → `plan_not_calibrated`。<br>(e) implementer 的 plan 沒有 `--calibrated-from` → `plan_not_calibrated`。<br>(f) target 或 version 不是登記的 plan → `plan_version_mismatch`。<br>(g) 校準後的 plan 取代草案，人工 `approve_plan` → exit 0、phase `approved`；`approval` 含 decision、actor、at、plan 的釘選與 binding digest；狀態裡只有一份 `plan`；再以另一個 id 送 `approve_plan` → exit 1 `already_approved` | (d) `result.error == "plan_not_calibrated"`：4.1 只記錄，exit 0 | 全部成立 |
| `test_approve_plan_needs_spec_ac_and_design_bindings` | 已校準的 plan，只登記 spec、ac、design 的 7 種不完整子集 → exit 1 `missing_bindings`，恰好列出缺的角色，revision 不變，next 列出 `missing_binding:<role>`。三者都登記後，同一個 plan version 可以批准 | `code == 1`：前一個測試的實作不看 binding | 成立 |
| `test_next_after_approval_reports_dispatch` | 核准後 next 為 `{action: dispatch, plan: {locator, version, digest}, approval: <id>}`，blockers `[]`；`status` 與 `feature.json` 相同 | `next.action == "dispatch"`：`derive` 對核准還沒有規則 | 成立 |
| `test_changing_an_approved_document_needs_scope_change` | 核准後，以下都 exit 1 `scope_change_required`，核准與 revision 不變：新的 plan version；同一個 plan locator 但 bytes 改了；spec、ac、design 的內容改了；新增一份 spec。內容相同的重登 → exit 0、revision 不變。登記 `sa` 或 `policy` → exit 0，核准保留 | `code == 1`：登記會直接取代 | 成立 |

## 6. 範圍變更與政策核准

- [ ] 6.1 `scope_change` 撤銷核准並取代 plan，`policy_change` 綁定政策檔的 digest，`status` 顯示 policy 狀態；驗證：`uv run pytest tests/test_scope_policy.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `decisions.py`：`scope_change`、`policy_change` 的檢查與效果，以及重登已被取代的 plan 時回 `plan_superseded`（D9）。
- `approve_plan` 加上「未被取代」的檢查。
- `next.py`：`plan_superseded`。
- `state.py`／`cli.py`：policy 狀態，依 D11 在讀取時計算。

**擁有路徑**：上列各檔，以及 `tests/test_scope_policy.py`。

**依賴**：5.1，從它取得：

- **登記項的形狀**：`plan`、`versions.bindings[role][locator]`、`versions.policy`，登記項帶 `path`、`digest`。
- **`approval` 的形狀**。
- **`approve_plan` 的檢查順序**：「未被取代」插在「已校準」之後、「version 相符」之前。
- **已核准時的 `scope_change_required`**。
- **`derive` 的順序**：`plan_superseded` 放在 plan 阻擋中，不改其他條件的位置。

**AC**：O01（協調者不能自己做 scope 變更）、O07、O23、G22。

**Commit**：`feat(decisions): revoke approval on scope_change and bind policy`

`tests/test_scope_policy.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_scope_change_stops_the_run_and_supersedes_the_plan` | 參數：已核准、等待核准。人工 `scope_change`，帶 impact、reason 與兩個 `--open-question` → exit 0。紀錄含 impact、reason、`open_questions` 與 `supersedes`（舊 plan 的釘選）；`approval` 為 `null`；phase `awaiting_approval`；`plan.superseded_by` 等於該 id；next 為 `human`、`[plan_superseded:<id>]`、`[]`。`agent:implementer` 送出 → `actor_not_human`，核准保留 | `approval is None`（已核准的參數）：4.1 只記錄 | 成立 |
| `test_only_a_new_plan_version_is_approvable_after_scope_change` | 接續前一個測試：批准舊 plan → `plan_superseded`；以相同的 version 與 digest 重登 → `plan_superseded`。登記新 version 後，next 回 `approve_plan`；人工批准 → `approved`，next 為 `dispatch` | `code == 1`（批准舊 plan）：`approve_plan` 還不看是否被取代 | 成立 |
| `test_policy_is_approved_only_by_policy_change_on_its_digest` | 未登記時 `policy.status` 為 `not_registered`，此時 `policy_change` → `policy_not_registered`。登記 `workflow.yaml` 後為 `not_approved`，帶 digest。以下都被拒：agent → `actor_not_human`；digest 不符 → `policy_digest_mismatch`；locator 不符 → `policy_digest_mismatch`。人工且正確 → exit 0，狀態 `approved`，帶 decision id 與 digest。`next` 不受 policy 影響 | `result.policy.status == "not_registered"`：視圖還沒有 policy | 成立 |
| `test_policy_changed_after_approval_is_not_approved` | 接續前一個測試：改動 `workflow.yaml` → `digest_mismatch`，帶核准時與目前的 digest；刪檔 → `unreadable`；還原後以改過的內容重登 → `not_approved`；對新 digest 做 `policy_change` → `approved` | `policy.status == "digest_mismatch"`：前一個測試的實作只看狀態，回 `approved` | 成立 |

## 驗收驗證

- 每條 AC 都由下表的測試在 G1（全新 clone、完整套件）與 PR 上的 `unit-linux` 通過來證明。
- to-pr 把結果彙整到 #29 的 PR Pass package，每條 AC 附測試名稱、Red 與 Green 的證據位置，以及 CI run 的連結。
- 「通過」指下表的每個測試都 Green，而且整個 session 依測試政策以 exit 0 結束。

| AC | 驗證的測試（task） | 通過代表 |
| --- | --- | --- |
| O01 | 3.1 `…exactly_one_concurrent_claim…`；5.1 `…only_a_human_approve_plan…`；6.1 `…scope_change_stops…` | 直接 `init` 就進入 planning；協調者 identity 由 `claim` 保存；沒有交接紀錄也能走到開工確認，但協調者既不能批准，也不能做 scope 變更 |
| O03 | 5.1 `…registered_in_place…`、`…unreadable_documents…` | 登記保存原生 locator、version、digest，登記時的內容可讀回；原檔不改名、不搬移；讀不到就拒絕，狀態不變 |
| O05 | 5.1 `…status_shows_versions…`、`…only_a_human_approve_plan…`(a)(c) | 顯示等待開工確認與待確認的 plan 版本；時間經過或 agent 的表示都不產生核准 |
| O07 | 6.1 前兩個測試 | `scope_change` 保存影響與理由、撤銷核准、舊 plan 標為被取代；新版本批准後 next 才是 `dispatch` |
| O15 | 3.1 `…uninitialised_run_is_not_found…` | 沒有 `init` 的 run：查不到、不建立、不接管其他 run |
| O19 | 4.1 `…only_human_actors_can_decide…`；5.1 (c)；6.1 agent 參數 | 非 `human:<name>` 的 actor 一律被拒，狀態不變 |
| O22 | 5.1 (d)(e)(g) | 只有 Implementer 校準過的 plan 能被批准，而且只有一份現行 plan |
| O23 | 6.1 前兩個測試（兩種起點） | 保存影響與待決事項；整個 run 停在等待批准，直到新版本被批准 |
| O26 | 5.1 (b) | `sa` binding 保存版本與來源，但不產生核准 |
| O29 | 5.1 `…needs_spec_ac_and_design_bindings…` | 缺任一 binding 就拒絕並列出，三者都有之後同一個 plan 版本可以批准 |
| O30 | 4.1 `…unsupported…` | `adopt`、`delegate` 回 `unsupported`，revision、owner、核准都不變 |
| G21 | 1.1 t1、t2、t4、t5、t6；2.1 三個測試；PR 上的 `unit-linux` run | 違反政策時，本機的測試 session 以失敗結束；`unit-linux` 執行同一個命令、同一份設定，而且 t1～t6 在 Linux 上也通過 |
| G22 | 2.1 `…declares_unit_linux…`；6.1 兩個 policy 測試；驗收示範（見下） | 宣告了必要 check，但沒有綁定目前 digest 的 `policy_change`，或核准後檔案被改 → `status` 顯示未核准或 digest 不符 |
| D01 | 3.1 `…creates_a_planning_run…`、`…status_human…`；5.1 `…status_shows_versions…` | 狀態檔與 `status`（含 `--human`）都直接顯示 phase、owner、版本、核准、gate 的狀態與原因、blockers、next |
| D02 | 3.1 `…manual_edit…`；4.1 `…recorded_with_its_provenance…`、`…missing_fields…` | 手改被偵測、不覆寫，也不被當成決策；decision 只能經 `decide` 產生，並保存決策者、來源、理由與影響 |
| D03 | 3.1 `…exactly_one_concurrent_claim…`；4.1 `…need_the_coordinator_token…`；5.1 `…unreadable_documents…`（`register` 的 token） | 恰一方取得協調權；另一方可以讀取，但寫入被拒 |
| D09 | 3.1 兩個 interrupt 測試、`…stale_revision…` | 中斷後讀到完整的舊版或新版；revision 會被核對 |
| D10 | 3.1 `…interrupt_before…`；4.1 `…takes_effect_once…`、`…blocks_the_run…`、`…resolve_conflict…` | 已提交的不重複生效；未提交的不被接受；內容不同時 Blocked，保留兩份內容，直到人工 decision 解除 |
| D11 | 3.1 `…untrusted_state…`、`…never_overwrites…`；4.1 `…blocks_the_run…` | 顯示具體原因與現存檔案，原檔不變；`init` 不覆寫，也不建立空 run |
| D25 | 4.1 `…budget_extension…` | 四種目標各寫入一筆人工紀錄，`workflow.yaml` 與其他狀態不變；agent、缺理由、未知目標都被拒 |

**G22 的驗收示範**：由 Project Lead 在驗收時執行，把本 repo 的 `workflow.yaml` 實際綁定一次。

1. 以 `uv build` 出的 wheel 安裝到暫存 venv，`LOOPCTL_HOME` 指向暫存目錄。
2. `init`、`claim` 一個示範 run。
3. `register policy --locator workflow.yaml`，`status` 顯示 `not_approved`。
4. Project Lead 親自執行 `decide policy_change --actor human:<name>`，`status` 顯示 `approved`。

輸出記在驗收留言。Feature 2 起，由 loopctl 管理的 run 各自登記並綁定。

## 範圍

- 只改 `yschiang/loop-engineering`，一個 PR（D61、D14）。
- 產品檔案只有：`pyproject.toml`、`uv.lock`、`src/loopctl/`、`tests/`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`workflow.yaml`。
- 勾選本檔的核取方塊由 plan-to-code 處理。
- 不做的事見 proposal 的「不做」。

## 環境

- **本機**：macOS（Darwin arm64）；uv 0.11.24；CPython 3.12.13（uv 管理）；git 2.54。測試不需要網路。`scripts/dist-smoke.sh` 第一次執行可能要下載 `uv_build`。
- **CI**：GitHub Actions 的 `ubuntu-24.04`；uv 釘版；只由 `pull_request` 觸發。
- 兩個平台跑同一套測試。`fcntl.flock`、`os.link`、`F_FULLFSYNC` 在兩邊的行為都由 3.1 的測試覆蓋。

## 風險

- 產品層的風險見 design 的「Risks / Trade-offs」。
- **並行測試（3.1）**：8 個程序加 barrier；斷言「恰一個得勝」與排程無關。若 flaky，追根因，保留嚴格斷言，不加 retry。
- **突變 Red**：標「突變」的測試（t4、`…has_one_source`、`…interrupt_before…`，可能還有 `…stale_revision…`）靠一次不提交的突變證明 Red。Reviewer 要核對突變與輸出。
- **`unit-linux` 第一次實跑在 to-pr**：結構已由 2.1 在本機檢查；實跑失敗走 to-pr 的修正迴圈。
- **3.1、4.1 的份量**：各約一個 session。任一個超出時，依 D71 在 task 內部重排步驟，不拆成只做一層的 task。

## 執行界線

- 依 D13：主動執行時間最多 4 小時；修正最多 3 輪；每個 infra 操作額外重試最多 2 次。到限時保存現況，轉 Blocked 交人（D70）。
- 每個 task 最多 3 次 attempt，修正也算在內（plan-to-code）。
