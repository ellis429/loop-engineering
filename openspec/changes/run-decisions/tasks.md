# Tasks

本檔是 `run-decisions` 唯一的實作計畫。它不放實作碼：每個 task 列出要寫的測試、每個測試斷言的行為、Red 應該失敗在哪個斷言、Green 的預期結果，以及執行指令（D68）。介面與不變式見 [design.md](design.md)，以下用 D1～D14 引用它的章節。

## 共同規則

- **模型與模式**（D52、D72）：
  - 每個 task 都用預設模式，plan 寫到設計、介面、不變式與測試為止。
  - Implementer 是 Claude Opus 5.5。Reviewer 是 GPT-6 Astra（另一家廠商），每個 task 在新 session、新 clone 上唯讀審查。
  - effort 依 D69 的表，逐 task 標在下方。
- **順序**：依序實作 1.1 → 2.1 → 3.1 → 4.1 → 4.2 → 5.1 → 6.1（D13 實作序列）。依賴只從前往後，沒有循環。每張測試表的列序就是撰寫順序。
- **Red 的規則**（D68）：
  - Red 必須是所列斷言的比較失敗（AssertionError）。ImportError、usage error、unknown command，或停在呼叫上的例外，都不算。
  - harness 的 `Result` 會把未攔截的例外記在 `exc`；巢狀欄位用不會拋例外的方式取值（D13）。所以程式崩潰或缺欄位時，失敗也會落在所列的斷言上。
  - 每個 Red 都以同一 task 前面的測試已經 Green 為前提。
  - 標「突變」的測試，預期會因為前面的實作而一寫就 Green。這時以一次不提交的突變證明它會失敗在所列斷言上：照表中寫明的方式暫時破壞行為，記下失敗，再還原。突變與輸出存成 Red 證據。
  - 沒有標「突變」的測試一寫就 Green → 停下，回報計畫有誤，不自行改測試。
- **每個 task 的完成條件**：
  - 在 task 的 head 上，`uv run pytest && uv run ruff check . && uv run mypy src` 全部通過，前面 task 的測試也包含在內。1.1 與 2.1 另外要 `scripts/dist-smoke.sh` 通過。
  - 逐 task 審查沒有未解的 blocking finding。
- **指令**：每張測試表註明檔案；單一測試的指令是 `uv run pytest <檔案> -k <名稱>`。pytest 的政策由 `pyproject.toml` 提供，所以不加任何旗標。
- **證據**：每個 task 的 Red 與 Green 原始紀錄（命令、完整輸出、exit code、commit）存在 `.delivery/run-decisions/<task>/attempt-<n>/`，這個目錄不進 Git。逐 task 審查的結果貼在 #29。
- **Commit**：
  - 格式：`<type>(<scope>): <祈使句>`，英文，不超過 72 字元，scope 用模組名（`store`、`state`、`decisions`、`cli`、`next`）。
  - 例外：`build` 與 `ci` 不帶 scope，寫成 `build: …`、`ci: …`。
  - `feat`、`fix`、`refactor` 的 body 要有 `Why:` 與 `Behavior:`。
  - 沒有 `Co-Authored-By` 或任何 AI 署名。
  - 每個 task 一到幾個 commit，各自綠燈。task 的核取方塊在它最後一個 commit 勾選。

### 共用檔案（依序擁有，不並行修改）

| 檔案 | 擁有順序 | 規則 |
| --- | --- | --- |
| `pyproject.toml`、`uv.lock` | 1.1 建立 → 2.1 加 dev 依賴 pyyaml | 兩者在同一個 commit 更新；全新 clone 的 `uv sync --frozen` 仍成功 |
| `tests/conftest.py` | 1.1 建立（政策、`home`、`repo`、`cli`、`cli_proc`、`cli_proc_many`）→ 3.1 加 `started_run` | 只新增 fixture，不改既有 fixture 的行為 |
| `src/loopctl/cli.py` | 1.1 建立（parser、`HANDLERS` 與全部 stub）→ 3.1、4.1、5.1 依序把自己命令的 stub 換成實作 → 6.1 在 `status` 加 policy 狀態 | 不改參數與 envelope；`tests/test_cli.py` 仍通過 |
| `src/loopctl/store.py` | 3.1 建立（授權優先、讀取不寫檔、物件引用、fsync）→ 4.1 加重送冪等與前移 → 4.2 加衝突、`resolves` 與 `TransitionRejected` | 冪等與衝突只插在授權之後（D4 第 3、4 步），前移只在第 8 步開頭；不改讀取時的不可信原因與寫入順序 |
| `src/loopctl/next.py` | 3.1 → 4.2（衝突）→ 5.1（plan 阻擋、`dispatch`）→ 6.1（`plan.superseded_by` 的衍生與 `plan_superseded`） | 只插入自己的判斷，保持 D7 的順序 |
| `src/loopctl/state.py` | 3.1 → 4.1（`decisions`）→ 4.2（`conflicts`）→ 5.1（plan、binding、核准）→ 6.1（policy） | 只新增視圖欄位 |
| `src/loopctl/decisions.py` | 4.1 建立（完整 kind 表、共同核對、只記錄的 kind）→ 4.2（`resolve_conflict` 的三種選擇，撤銷時標 `voided`）→ 5.1（register、`approve_plan` 與它的清除規則）→ 6.1（`scope_change`、`policy_change`，以及 `policy_change` 的清除規則） | 不改共同核對的順序與紀錄欄位（D2、D10） |

### 總覽

| Task | 交付 | 依賴 | Implementer／Reviewer effort | AC |
| --- | --- | --- | --- | --- |
| 1.1 | 專案骨架、測試政策、CLI 入口與 stub、共用 fixture、dist-smoke | — | high／high | G21 |
| 2.1 | CI `unit-linux` 與 `workflow.yaml` | 1.1 | medium／high | G21、G22（宣告） |
| 3.1 | 持久的 run 狀態：`init`、`claim`、`status`、`next` | 1.1 | xhigh／xhigh | D01、D02、D03、D09、D10、D11、O01、O15 |
| 4.1 | 人工決策紀錄：`decide`、授權、重送冪等、history 前移、`unsupported` | 3.1 | xhigh／xhigh | D02、D03、D09、D10、D25、O19、O30 |
| 4.2 | 衝突與解除：Blocked、非 owner 不能製造衝突、`resolve_conflict` 的三種選擇 | 4.1 | xhigh／xhigh | D03、D10、D11 |
| 5.1 | 登記原生文件與開工確認，核准後回報 `dispatch` | 4.2 | xhigh／xhigh | O01、O03、O05、O19、O22、O26、O29、D01、D10 |
| 6.1 | 範圍變更與政策核准 | 5.1 | xhigh／xhigh | O01、O07、O23、G22、D10 |

Effort 的依據（D69）：

- 2.1 只改 CI 與設定。
- 1.1 是一般行為。
- 3.1、4.1、4.2 出錯會遺失或損毀狀態，或破壞並行、授權與故障恢復的保證。
- 5.1、6.1 守的是核准與政策這兩道授權；而且 5.1 涵蓋 6 列以上的 AC。

## 1. 共用測試骨架

- [x] 1.1 建立專案骨架、測試政策、CLI 入口與 stub、共用 fixture；驗證：`uv run pytest && uv run ruff check . && uv run mypy src && scripts/dist-smoke.sh` 全部通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）high／high。

**交付**：

- `pyproject.toml`：
  - `uv_build`；`requires-python = ">=3.12,<3.13"`；`[project.scripts] loopctl = "loopctl.cli:main"`；
  - dev 依賴：pytest、ruff、mypy；
  - ruff 的 `select = ["E","F","I","B","UP"]`；mypy `strict = true`；
  - pytest 政策（D12）。
- `uv.lock`。
- `src/loopctl/{__init__,__main__,cli}.py`：
  - parser 含 D2 的全部命令與參數，parser 與 handler 的分工照 D2 的表；
  - 以 `HANDLERS` 派送；
  - argparse 的錯誤轉成 exit 2 的 envelope。
- **stub 契約**：每個命令的 handler 都回 exit 0，envelope 為 `ok: true`、`result: {}`，其餘欄位 `null`，不寫任何檔案。形狀正確，內容是空的；之後每個 Red 都能走到行為斷言。
- `tests/conftest.py`：
  - 政策 hook，平台由唯一的 `current_platform()` 決定；
  - autouse `home`：把 `LOOPCTL_HOME` 設到 `tmp_path`；
  - `repo`：範例文件（D13）；
  - `cli`：in-process；
  - `cli_proc`、`cli_proc_many`：子程序。
- `scripts/dist-smoke.sh`：三項具名檢查（D12）。

**不在範圍**：任何狀態讀寫；`clock.py`，由 3.1 建立。

**擁有路徑**：上列各檔，以及 `tests/test_cli.py`、`tests/test_test_policy.py`。

**依賴**：無。base 是本計畫的 commit（`feature/run-decisions`：main `c91b774` 加上 spec、design 與本檔）。

**AC**：G21 的本機部分。

**Commits**：

1. `build: add the loopctl project skeleton and test policy`：pyproject、uv.lock、`__init__.py`、conftest 的政策與 `home`／`repo`、`test_test_policy.py`。
2. `feat(cli): add the loopctl entry point and JSON envelope`：其餘檔案。

`tests/test_test_policy.py`：以 pytester 開子 session。子 session 載入 repo 的 `tests/conftest.py` 與 `pyproject.toml` 的 `[tool.pytest.ini_options]` 原文，不另寫一份；平台以 `current_platform()` 模擬。t5 排在 t2 之前：先寫 t2 的話，它的 skip 政策可能已經擋下 xfail，t5 就沒有 Red。

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_t1_only_on_foreign_platform_skips_and_session_passes` | 模擬 darwin 時，`only_on("linux")` 的案例 skip，另一個案例通過 | `ret == 0`：`only_on` 尚未註冊，`--strict-markers` 讓子 session 以 exit ≠ 0 結束 | skip 1、pass 1、`ret == 0` |
| `test_t5_xfail_and_xpass_fail_session` | 參數：一個 xfail（非 strict 標記、測試本身失敗）、一個 xpass | `ret != 0`（xfail 參數）：t1 的實作只處理 `only_on`，非 strict 的 xfail 讓子 session exit 0 | 兩者 `ret != 0`，summary 列出該案例 |
| `test_t2_skip_not_from_only_on_fails_session` | 參數：`only_on("linux")` 案例在 linux 上自行 `pytest.skip("missing tool")`；`skipif(True, reason="platform: linux only")`；`pytest.skip("platform")` | `ret != 0`（第一個參數）：t5 的實作只擋 xfail／xpass，一般的 skip 仍讓子 session exit 0 | `ret != 0`，summary 列出該案例 |
| `test_t4_zero_collected_fails_session` | 參數：空目錄；`-k` 全部濾掉 | 突變：暫時讓 `pytest_sessionfinish` 把 `NO_TESTS_COLLECTED` 改成 `OK` → 失敗在 `ret != 0` | `ret != 0` |
| `test_t6_expected_platform_mismatch_fails_session` | `LOOPCTL_EXPECT_PLATFORM=linux`，模擬 darwin | `ret != 0`：尚未核對，exit 0 | `ret != 0`，summary 說明平台不符 |

`tests/test_cli.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_help_lists_every_command` | `--help` exit 0；stdout 以 `usage: loopctl` 開頭，列出 init、claim、status、next、register、decide、adopt、delegate | stdout 含 `usage: loopctl`：先建立空的 `main(argv) -> int`（回 0、不輸出） | 全部列出 |
| `test_parsed_arguments_reach_the_handler_and_its_envelope_is_printed` | 參數：每個命令帶齊全部參數，例如：`init … --issue X --actor agent:impl`；`register binding … --role spec --content-from P`；`decide revise … --choice original --open-question q1 --open-question q2`；`adopt --anything x`。以 `monkeypatch.setitem(cli.HANDLERS, <命令>, <記錄用的假 handler>)` 換掉 handler，假 handler 回 `(7, <六欄的 envelope>)`。假 handler 恰被呼叫一次，收到的每個值都等於輸入（`open_question == ["q1", "q2"]`；`adopt` 的其餘參數原樣保留）；`main` 回 7；stdout 恰為假 envelope 的一行 JSON | `received.repo == "a/b"`：help 測試的實作只解析、不派送，假 handler 沒被呼叫，取值得到 `None` | 全部參數通過 |
| `test_adopt_and_delegate_keep_arguments_that_start_with_h` | 回歸（審查 T1.1-01）。參數：`adopt`、`delegate` 各帶 `-host example.com`；`--help=foo`；`--to x -hx`。以記錄用的假 handler 換掉 handler，假 handler 回 `(7, <六欄的 envelope>)`。假 handler 恰被呼叫一次，`command` 是該命令，`rest` 與輸入完全相同；`main` 回 7；stdout 恰為假 envelope 的一行 JSON | 假 handler 被呼叫一次：argparse 把 `-host` 讀成 `-h`，印出 usage、回 0；`--help=foo` 成為 usage 錯誤；假 handler 都沒被呼叫 | 全部參數通過 |
| `test_adopt_and_delegate_explicit_help_prints_usage` | 參數：`adopt`、`delegate` 各帶 `--help`、`-h`。exit 0，stdout 以 `usage: loopctl <命令>` 開頭，記錄用的假 handler 沒被呼叫 | 突變：暫時拿掉 `parse` 裡 `adopt`／`delegate` 的 help 分支 → 失敗在 `code == 0`（假 handler 被呼叫，回 7） | 全部參數通過 |
| `test_each_command_prints_one_json_envelope` | 參數：8 個命令各帶最少的合法參數，不換 handler。stdout 恰一行 JSON 物件，鍵恰為 `ok, revision, result, blocked, next, safety`；stderr 為空。不斷言 exit code，所以後面的 task 換掉 stub 後仍然成立 | stdout 恰一行：前一個測試的 `HANDLERS` 還是空表，查表失敗（記在 `exc`），沒有輸出 | 每個命令都輸出單行 envelope |
| `test_usage_errors_are_json_envelopes_with_exit_2` | 參數：沒有命令；`merge`；`init` 缺 `--actor`；`register other`；`--repo noslash`；`--repo ../x`；`--feature a/b`。每個都 exit 2，`ok` 為 false，`result.error == "usage"`，`result.message` 指出該參數或命令；stderr 沒有 argparse 的 usage 文字 | `result.error == "usage"`：argparse 預設丟出 `SystemExit(2)` 並寫 stderr，helper 記下 exit 2，但 stdout 是空的 | 全部參數通過 |
| `test_python_m_loopctl_matches_the_in_process_entry` | `cli_proc` 跑 `--help`、`merge`、`status --repo a/b --feature F-1`，exit code 與 stdout 都和 in-process 相同 | `merge` 的 `code == 2`：先建立只呼叫 `main()`、不把回傳值當 exit code 的 `__main__.py`，子程序回 0 | 三者都相同 |
| `test_cli_proc_runs_the_prelude_first_and_starts_processes_together` | (a) `cli_proc("--help", prelude="import os; os._exit(9)")` → `code == 9`，stdout 為空，證明 prelude 先於 loopctl 執行。(b) `cli_proc_many(4, "--help")` → 4 個結果都 exit 0 並含 usage，而且 barrier 檔在 4 個程序都回報就緒之後才建立 | (a) 的 `code == 9`：helper 先實作成忽略 prelude，得到 0 | 兩者都成立 |

`scripts/dist-smoke.sh` 的三項具名檢查（D12）：

- Red 以突變證明：暫時讓 `main` 在 envelope 之前多印一行 → 失敗在具名檢查 `envelope`（印出 `dist-smoke: FAIL: envelope`）。
- Green：三項都通過，印出 `dist-smoke: ok`，exit 0。

## 2. CI 與政策檔

- [x] 2.1 建立 `unit-linux` 的 GitHub workflow 與 `workflow.yaml`，並檢查兩者的結構；驗證：`uv run pytest tests/test_ci.py` 與完整的完成條件通過

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

- `src/loopctl/store.py`，照 D3、D4。其中授權先於一切，讀取與被拒的命令不寫檔，另有物件引用檢查與 fsync。transition 冪等與前移屬 4.1，衝突屬 4.2（D4 第 3、4、8.1 步）。
- `src/loopctl/state.py`：初始狀態（含 `coordinator`）、視圖（D11 的投影）、`--human`、token digest。
- `src/loopctl/next.py`：`derive`，本 task 只有 `unclaimed` 與 `plan_not_registered` 兩條。
- `src/loopctl/clock.py`。
- `cli.py` 裡 `init`、`claim`、`status`、`next` 的 handler。
- conftest 的 `started_run(repo, feature, actor) -> token`。
- token 用 `secrets.token_hex(32)`，以 `hmac.compare_digest` 比對。

**擁有路徑**：上列各檔，以及 `tests/test_state.py`。

**依賴**：1.1，從它取得：

- `main(argv) -> int`：以 `HANDLERS` 派送，只寫一行 envelope；exit code 照 D2。
- fixture：
  - `cli`、`cli_proc`、`cli_proc_many`，回傳 `Result(code, out, stdout, stderr, exc)`；未攔截的例外使 `code is None`；
  - `prelude` 先於 loopctl 執行；
  - `home`、`repo`。
- `init`、`claim`、`status`、`next` 的參數固定，本 task 不改。

**AC**：D01（phase、協調者、owner、gate、blockers、next）、D02（手改）、D03、D09、D10（未提交的變更不被接受）、D11、O01（`init` 保存協調者 identity）、O15。

**Commit**：`feat(store): keep one durable state per repo and feature run`

`tests/test_state.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_init_creates_a_planning_run_per_repo_and_feature` | `init --actor agent:implementer` exit 0、revision 1，而且沒有任何交接紀錄。`status`（D11 的投影）：repo、feature、issue；`coordinator.actor == "agent:implementer"`；owner `null`；phase `planning`；三個 gate 為 `not_evaluated` 且原因非空；blockers `[unclaimed]`；envelope 的 next 為 `{action: human, blockers: [unclaimed], decision_kinds: []}`。狀態檔 `runs/yschiang/loop-engineering/F-1/feature.json`：`coordinator`、`phase`、`owner`、`gates`、`blockers`、`next` 各自等於上列值；`history/1.json` 存在。另一個 repo 的同名 feature 也 exit 0，是另一個 run | `result.phase == "planning"`：stub 回 `{}` | 全部成立 |
| `test_status_human_renders_the_same_view` | `status --human` 的 `result.human` 逐行含 phase、協調者、owner（unclaimed）、每個 gate 的狀態與原因、blockers、next | `"human" in result` | 成立 |
| `test_init_never_overwrites_an_existing_run` | 同一 repo＋feature 再 `init`，issue 或 actor 相同或不同，都是 exit 1 `run_exists`；run 目錄的 bytes 不變 | `code == 1`：既有目錄讓 rename 失敗（記在 `exc`），或被覆寫 | 成立 |
| `test_claim_grants_the_coordination_right_once_and_stores_only_the_token_digest` | 依序執行：`claim --actor agent:implementer` → exit 0，token 是 64 位 hex，revision 2；`status` 的 `owner.actor` 為該值，`coordinator` 不變。狀態檔的 `owner.token_digest` 是 token 的 sha256，run 目錄裡沒有任何檔案含明文 token。另一個 actor 再 `claim` → exit 1 `already_claimed`，並附目前的 owner | token 符合 64 位 hex：stub 沒有回 token | 成立 |
| `test_uninitialised_run_is_not_found_and_nothing_is_created` | 另有 F-2 已 `init` 並 `claim`。對 F-9 執行 `status`、`next`、`claim`，都是 exit 1 `run_not_found`；`$LOOPCTL_HOME` 的快照不變 | `code == 1`（`next`）：`next` 的 handler 還是 stub，回 0 | 成立 |
| `test_concurrent_claims_leave_one_owner_and_a_controlled_answer_for_every_loser` | `cli_proc_many(8, "claim", …)`，各用不同 actor；prelude 在 `os.link` 前設 D13 的 gate。結果：<br>- 恰一個 exit 0；<br>- 其餘 7 個都 exit 1，`result == {error: "already_claimed", owner: <得勝的 actor>}`（精確比較），沒有例外；<br>- 之後 `status` exit 0、revision 2、owner 為得勝者；history 恰為 `1.json`、`2.json` | 每個落敗者的 `result == {error: "already_claimed", owner: …}`：沒有 flock 時，8 個程序到 gate 之前都已讀到沒有 owner 的狀態；gate 等齊才放行時，它們一起搶 write-once 的 `history/2.json`，只有一個成功，其餘拋 `FileExistsError`（記在 `exc`，沒有受控回應）。若單次 `claim` 已加 flock → 突變：暫時拿掉 flock，失敗在同一斷言。存 Red 證據時一併存 gate 紀錄：到達數必須是 8、放行原因必須是 `all_arrived`；逾時放行的那次不算，重跑 | 成立 |
| `test_interrupt_after_history_keeps_the_new_revision_once` | `claim` 時以 prelude 把 `os.replace` 換成 `os._exit(9)` → exit 9。之後 `status` exit 0、revision 2、owner 已設定；另一個 actor 再 `claim` → `already_claimed`；run 目錄的 bytes 在這兩個命令前後相同，也就是讀取與被拒的命令都不修復 `feature.json`；history 只有 `1.json`、`2.json` | `revision == 2`：讀取只看 `feature.json`，得到 1 | 成立 |
| `test_interrupt_before_history_keeps_the_old_revision` | 以 prelude 把 `os.link` 換成 `os._exit(9)` → exit 9；`status` 回 revision 1、owner `null`；再 `claim` exit 0、revision 2 | 突變：暫時改成先替換 `feature.json` 再寫 history → 失敗在 `revision == 1` | 成立 |
| `test_a_failed_sync_before_the_link_commits_nothing` | `claim` 時以 prelude 讓第一次 `os.fsync` 拋出 `OSError(EIO)`。依 D4 第 8 步，這是 history 暫存檔的 fsync，在 `os.link` 之前。結果：`code != 0`；`status` 回 revision 1、owner `null`；history 只有 `1.json`。`os.link` 之後的同步失敗不在本測試範圍（D4 的提交邊界） | `code != 0`：提交路徑還沒有呼叫 fsync，`claim` 成功 | 成立 |
| `test_commit_with_a_stale_revision_writes_nothing` | `claim` 之後（rev 2），以 `store.commit(key, 1, "t-x", payload, mutate, authorize=<不檢查>)` 提交 → `RevisionConflict`；run 目錄的 bytes 不變 | `pytest.raises(RevisionConflict)`。若 `claim` 已依 D4 核對 revision → 突變：暫時略過第 5 步 | 成立 |
| `test_commit_rejects_missing_or_corrupt_object_references` | 以 `store.commit` 驗證，參數：(a) `mutate` 加入一個指向不存在物件的 `{"$object": d}`；(b) 先提交一個有效的引用，刪掉該物件檔後，再提交一個只改其他欄位的 transition；(c) 物件檔的內容被改掉。依序得到 `UntrustedState` 與原因 `object_missing:<d>`（(a)、(b)）或 `object_corrupt:<d>`（(c)），run 目錄的 bytes 不變。另外，一般的 `sha256:` 字串欄位照常提交 | `pytest.raises(UntrustedState)`（(a)）：提交路徑還沒有引用檢查 | 成立 |
| `test_untrusted_state_stops_with_reason_and_files` | 參數：刪掉 `feature.json`（`state_missing`）；壞 JSON（`state_corrupt`）；`schema_version: 9`（`unknown_schema:9`）；刪掉 `history/2.json`（`history_missing:2`）；空的 run 目錄（`state_missing`）。`status`、`next`、`claim`、`init` 都 exit 5，`result.error == "untrusted_state"`，`reason` 如上，`files` 等於現存檔案排序後的相對路徑；bytes 不變；`init` 不建立任何東西 | `code == 5`：讀取時的例外記在 `exc` | 成立 |
| `test_manual_edit_is_detected_and_never_trusted` | 參數（保持 JSON 與 schema 合法）：把 g1 改成 `passed`；把 phase 改成 `approved`；改 owner；插入一筆 `{kind: approve_plan, actor: human:x}` decision。`status`、`next`、`claim` 都 exit 5 `manual_edit`；輸出不含 `passed` 或 `approved`；bytes 不變 | `code == 5`：只核對 schema 時會照單全收 | 成立 |

## 4. 人工決策紀錄

- [ ] 4.1 `decide` 的共同核對與紀錄、授權優先、重送冪等、history 的前移、`budget_extension`、`revise`、`handoff`，以及 `adopt`／`delegate` 與後續 kind 的 `unsupported`；驗證：`uv run pytest tests/test_decisions.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `src/loopctl/decisions.py`：
  - D10 的完整 kind 表與 D2 的核對順序；
  - `approve_plan`、`scope_change`、`policy_change`、`resolve_conflict` 在本 task 只做共同核對並記錄，檢查與效果由 4.2、5.1、6.1 加上。這樣後面的 Red 會落在行為斷言上，不是 `unsupported`。
- `store.py`：
  - D4 第 3 步中「等於接受的內容 → 回原 revision」這一支；
  - 第 8.1 步的前移，維持「history 最多領先一版」。
- `state.py`：`decisions` 視圖。
- `cli.py`：
  - `decide`、`adopt`、`delegate` 的 handler；
  - `register`、`decide` 的 `authorize` 核對 token。

**擁有路徑**：上列各檔，以及 `tests/test_decisions.py`。

**依賴**：3.1，從它取得：

- **store**：
  - `load(key) -> (rev, state)`，錯誤是 `RunNotFound`、`UntrustedState(reason, files)`；領先一版的 history 會被當成現況讀回。
  - `commit(key, expected_revision, transition_id, payload, mutate, *, authorize)` 的順序是：讀取 → `authorize`（在任何寫入之前）→ revision 核對 → `mutate` → 物件引用 → 寫入。寫入時 history 先 `os.link`，`feature.json` 後 `os.replace`。
  - `derive(mutate(state))` 等於現況時是 no-op；`mutate` 必須是純函式，拋出 `Rejected` 時不寫任何檔。
  - 讀取與被拒的命令不寫檔。
  - 呼叫端遇到 `RevisionConflict` 時重讀重做。
- **順序限制**：
  - 冪等只能插在 `authorize` 之後、revision 核對之前（D4 第 3 步）；
  - 前移只能放在第 8 步的開頭；
  - 不改不可信原因與寫入順序。
- **fixture**：`started_run` 回傳 token。

**AC**：D02（decision 只經 `decide` 產生，帶來源與影響）、D03（寫入要 token，非 owner 的重送被拒）、D09、D10（重送只生效一次；連續中斷可恢復）、D25、O19、O30。

**Commit**：`feat(decisions): record human decisions once with their provenance`

`tests/test_decisions.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_a_human_decision_is_recorded_with_its_provenance` | 參數 `revise`、`handoff`：`human:alice` 帶齊欄位 → exit 0、revision +1。`status` 的 `result.decisions[id]` 與狀態檔的 `decisions[id]`（兩者原樣投影，D11）都含 kind、actor、target、reason、source、impact、at、`seq == 1`、`status == "in_effect"`；phase、owner、gates 不變 | `result.decisions[id].source == <值>`：stub 什麼都沒記 | 成立 |
| `test_only_human_actors_can_decide` | actor 為 `agent:implementer`、`project_lead`、`session:lead/child-1`、`human:`、`Human:alice`，kind 為 7 種 → exit 1 `actor_not_human`；revision 與 bytes 不變 | `code == 1`：前一個測試的實作照單全收 | 成立 |
| `test_missing_fields_are_rejected` | 參數：id、actor、target、reason、source、impact 逐一缺少；`approve_plan`、`policy_change` 缺 `--version`；`resolve_conflict` 缺 `--choice`。每個都是 exit 1，`result == {error: "missing_fields", fields: [<缺的欄位>]}`（精確比較），狀態不變 | 缺 `--source` 的參數，精確比較 `result == {error: "missing_fields", fields: ["source"]}`：前面的實作把 source 記成 `null`，exit 0 | 全部參數通過 |
| `test_writes_need_the_coordinator_token` | 新的 decision，沒有 token 或 token 不符 → exit 4 `not_owner`，bytes 不變；同一個呼叫者 `status` exit 0 | `code == 4`：尚未核對 token | 成立 |
| `test_resending_a_decision_takes_effect_once` | 同一筆 decision 送兩次 → 第二次 exit 0、`result.duplicate` 為 true、revision 不變、只有一筆、`seq` 不變。另一情境：第一次以 prelude 讓 `os.replace` 中斷，重送後結果相同，revision 等於已提交的那版 | revision 不變：3.1 的 store 對同一個 id 再提交一次 | 成立 |
| `test_consecutive_interruptions_keep_every_committed_revision` | 已 `claim`（rev 2）。decision X 以 prelude 在換進 revision 3 時中斷（exit 9）；接著 decision Y 以 prelude 在換進 revision 4 時中斷（exit 9）（D13 的 `os.replace` 包裝）。之後：<br>- `status` exit 0、revision 4，`decisions` 同時有 X 與 Y；<br>- 重送 X、Y → 都是 duplicate，revision 仍是 4，各只有一筆；<br>- 再送新的 decision Z → exit 0、revision 5；<br>- history 恰為 `1.json`～`5.json`，狀態檔的 revision 為 5 | `result.revision == 4`：沒有前移時，Y 從讀回的 rev 3 提交了 `history/4.json`，但 `feature.json` 仍是 rev 2，讀取只看得到 rev 3 | 成立 |
| `test_non_owners_cannot_resend` | 參數：(a) 以錯誤的 token 原樣重送一筆已提交的 decision；(b) 同上，但不帶 token；(c) owner 的 decide 以 prelude 在 `os.replace` 中斷（history 領先一版）之後，非 owner 原樣重送同一筆。全部 exit 4 `not_owner`；run 目錄的 bytes（含落後的 `feature.json`）與 revision 都不變 | 突變：暫時把 `authorize` 移到 D4 第 3 步之後 → (a) 得到 exit 0 duplicate，失敗在 `code == 4` | 成立 |
| `test_budget_extension_only_records_a_human_ruling` | 目標 `active:60`、`rounds:+1`、`attempts:1.1:+1`、`ci_wait:<40 hex>` → 各 exit 0，各一筆帶 actor 與 reason 的紀錄；`repo/workflow.yaml` 的 bytes 不變；狀態檔除了 `decisions`、`transitions`、`revision` 以外都不變。會被拒的（exit 1，revision 不變）：agent actor；缺 reason；目標 `active:0`、`rounds:+2`、`wallclock:30`、`ci_wait:abc` | `result.error == "invalid_target"`（`rounds:+2`）：尚未核對目標，exit 0 | 成立 |
| `test_adopt_delegate_and_later_kinds_are_unsupported` | 頂層 `adopt --repo R --feature F`、`delegate --to x` → exit 2，`result == {error: "unsupported", command: <名稱>}`。`decide` 的 `adopt`、`delegate`、`accept`、`return`、`resolve_read`、`resolve_operation`、`resolve_finding`、`nonsense`，帶與不帶 token → exit 2，`result == {error: "unsupported", kind: <值>}`（D2 的分工：頂層命令由 parser 認得、handler 回；kind 由 handler 回）。`$LOOPCTL_HOME` 的 bytes 不變（owner、核准、revision 都相同） | 頂層 `adopt` 的參數，精確比較 `result == {error: "unsupported", command: "adopt"}`：它的 handler 還是 1.1 的 stub，回 exit 0、`result == {}` | 成立 |

- [ ] 4.2 同一 identity 內容不同時的衝突、非 owner 不能製造衝突，以及 `resolve_conflict` 的三種選擇；驗證：`uv run pytest tests/test_conflicts.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `store.py`：D4 第 3 步的其餘兩支（`TransitionRejected`、記下衝突）、第 4 步（Blocked 的優先序：`resolves` 有值但不是未解衝突 → `unknown_target`；有效則繼續；沒有 `resolves` 且有未解衝突 → exit 3）、`resolves`、D6 的衝突紀錄。
- `decisions.py`：`resolve_conflict` 的三種選擇（D6）。
  - 本 task 的撤銷只標 `voided`，因為只記錄的 kind 沒有效果可清；
  - D10 表中各 kind 的清除規則由 5.1（`approve_plan`）與 6.1（`scope_change`、`policy_change`）加上。
- `next.py`：衝突的 blocker。
- `state.py`：`conflicts` 視圖。

**擁有路徑**：上列各檔，以及 `tests/test_conflicts.py`。

**依賴**：4.1，從它取得：

- `decide` 的共同核對與紀錄欄位。
- `decide:<id>` 的 payload 冪等：等於接受的內容 → duplicate；這一支在 `authorize` 之後。
- 前移維持「history 最多領先一版」。
- `attempted` 要把 A 當成同一個 id 的 decision 照常核對時，用的是 4.1 的核對與紀錄流程。

**AC**：D03（非 owner 不能製造衝突）、D10、D11（衝突）。

**Commit**：`feat(decisions): block a conflicting resend until a human resolves it`

`tests/test_conflicts.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_same_decision_id_with_other_content_blocks_the_run` | owner 以 id X 先送 reason `a`，再送 reason `b` → exit 3 `transition_conflict`。`conflicts[cid]` 含 transition_id、已提交的 revision，以及兩份完整 payload；`decisions[X].reason` 仍是 `a`。`status`、`next` 都 exit 3，blockers `[transition_conflict:<cid>]`、kinds `[resolve_conflict]`，`files` 含 `feature.json` 與 history。另一筆新的 decide → exit 3，不寫。重送 X/`a` → exit 0、duplicate | `code == 3`：4.1 的 store 只有「等於接受的內容」這一支，不同內容不會變成 Blocked | 成立 |
| `test_non_owners_cannot_create_conflicts` | 參數：(a) 以錯誤的 token 送同一個 id、不同內容；(b) 不帶 token 同上；(c) owner 的 decide 以 prelude 在 `os.replace` 中斷之後，非 owner 送同一個 id、不同內容。全部 exit 4 `not_owner`；run 目錄的 bytes、revision 與 `conflicts` 都不變 | 突變：暫時把 `authorize` 移到 D4 第 3 步之後 → (a) 得到 exit 3，失敗在 `code == 4` | 成立 |
| `test_a_human_resolve_conflict_can_keep_the_original` | 接續衝突：人工 `resolve_conflict --target <cid> --choice original` → exit 0；`conflicts[cid]` 的 `resolved_by` 等於該 decision 的 id，`choice == "original"`，兩份 payload 仍在；`decisions[X]` 是 reason `a`、`in_effect`；`status` exit 0，next 回到衝突前的值。之後：重送 `a` → duplicate；重送 `b` → exit 1 `transition_rejected:<cid>`，不再 Blocked；第三種內容 → 新的衝突（exit 3）。被拒的情況，都不寫任何檔：agent 送出 → `actor_not_human`，仍 Blocked；衝突 K 還沒解時，以不存在的 `cid` 解除 → exit 1 `unknown_target`（不是 exit 3），K 仍未解；`--choice maybe` → `invalid_choice`；第三種內容造成新衝突 K2 之後，再解除已解除的 K → exit 1 `unknown_target`，K2 仍未解 | `code == 0`：所有寫入都被擋，exit 3 | 成立 |
| `test_resolve_conflict_can_take_the_attempted_content_or_abandon_it` | 參數（kind `revise`）：<br>`attempted` → `decisions[X].reason == "b"`，`replaces[0]` 是 reason `a` 的紀錄且帶 `voided_by`；重送 `b` → duplicate；重送 `a` → `transition_rejected:<cid>`。<br>`abandon` → `decisions[X]` 保留 reason `a`，但 `status == "voided"` 並帶 `voided_by`；重送 `a` → duplicate，回傳的紀錄是 `voided`；重送 `b` → `transition_rejected:<cid>`。<br>另外：被衝突的 decision 本身是 `resolve_conflict` 時，`attempted`／`abandon` → exit 1 `choice_not_allowed`，`original` 可以 | `decisions[X].reason == "b"`（`attempted` 參數）：前一個測試的實作把每種選擇都當 `original` | 成立 |

## 5. 登記原生文件與開工確認

- [ ] 5.1 `register plan|binding|policy`、`approve_plan` 的檢查、效果與清除規則、`status` 顯示版本與核准，以及核准後的 `dispatch`；驗證：`uv run pytest tests/test_approval.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `decisions.py`：
  - D9 的登記、D10 的 `approve_plan`，以及已核准時的 `scope_change_required`；
  - D10 表中 `approve_plan` 的清除規則：撤銷 X 時，`approval.decision == X` 才把 `approval` 設為 `null`；不還原任何核准。
- `cli.py`：`register` 的 handler。在邊界讀取 locator 或 `--content-from`，並存成物件。
- `next.py`：D7 的 plan 阻擋與 `dispatch`（D8）。
- `state.py`：plan、binding、核准的投影與 `--human` 的文字。

**擁有路徑**：上列各檔，以及 `tests/test_approval.py`。

**依賴**：4.1 與 4.2，從它們取得：

- 4.1：
  - `decide` 的共同核對，順序依 D2，錯誤是 `unsupported`、`missing_fields`、`actor_not_human`、`not_owner`；
  - 紀錄欄位，以及 `decide:<id>` 的 payload 冪等。
- 4.2：
  - `resolve_conflict` 三種選擇的流程：`attempted` 先撤銷，再把 A 當成同一個 id 的 decision 照常核對。本 task 只替撤銷補上 `approve_plan` 的清除規則；
  - 未解的衝突會擋下所有寫入，`register` 也包括在內；只有指向未解衝突的 `resolve_conflict` 例外，指向其他 `cid` 的回 `unknown_target`（D4 第 4 步）。

3.1 的 store（含物件引用檢查）與 `derive` 照舊。

**AC**：O01（直接交付不需要交接紀錄，協調者不能自己批准）、O03、O05、O19（`approve_plan` 的情境）、O22、O26、O29、D01（版本與核准）、D10（已生效的核准發生衝突）。

**Commit**：`feat(decisions): approve a calibrated plan with its bindings`

`tests/test_approval.py`：以 `repo` fixture 的文件為準。

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_native_documents_are_registered_in_place_and_read_back` | 登記：plan `tasks.md`（implementer，帶 `--calibrated-from`）；兩份 spec、ac、design；locator 為 issue URL、內容來自 `--content-from issue-29.md` 的 binding。每筆 exit 0，登記項的 role、locator（原樣）、version、source、`digest == sha256(內容)` 與物件引用都正確；`objects/<hex>` 的 bytes 等於登記的內容，改掉原檔之後仍然相等；`repo` 的檔案清單不變 | 狀態檔 `plan.locator == "tasks.md"`：stub 沒有登記 | 成立 |
| `test_unreadable_documents_are_not_registered` | 參數：locator 不存在；locator 是目錄；URL 但沒有 `--content-from`；`--content-from` 不存在；`policy` 帶 `--content-from` → exit 1 `locator_unreadable`，revision 不變。另外，沒有 token 或 token 不符的 `register` → exit 4 `not_owner`，bytes 不變 | `code == 1`：讀檔的例外記在 `exc` | 成立 |
| `test_status_shows_versions_and_awaiting_approval` | 登記完成後分兩個投影斷言（D11）：<br>`status`：phase `awaiting_approval`；plan 的 locator、version、digest、producer、`calibrated_from`；spec、ac、design 各自的 version；`approval == {status: "not_approved", plan_version: V}`；envelope 的 next 為 `human`、`[plan_not_approved]`、`[approve_plan]`；`--human` 含 plan、spec、design 的版本與核准這一行。<br>狀態檔：`approval is None`、`phase == "awaiting_approval"`、`plan.version == V`、`next` 等於 envelope 的 next | `status` 的 `approval == {status: "not_approved", plan_version: V}`：視圖還沒有核准的投影 | 成立 |
| `test_only_a_human_approve_plan_on_a_calibrated_plan_approves` | run 以直接 `init` 建立，由 `agent:implementer` `claim`，沒有任何交接紀錄。<br>(a) 沒有 decision，時鐘前進 30 天 → 仍未核准。<br>(b) O26：登記 `sa` binding（version `2026-09-30`，source「Project Lead 確認，#29」）→ `status` 的 `bindings.sa[<locator>]` 與狀態檔的 `versions.bindings.sa[<locator>]` 都保存這個 version 與 source；`approval` 仍是 `not_approved`，phase 仍是 `awaiting_approval`。<br>(c) `approve_plan --actor agent:implementer` → `actor_not_human`。<br>(d) plan 由 `project_lead` 登記 → `plan_not_calibrated`。<br>(e) implementer 的 plan 沒有 `--calibrated-from` → `plan_not_calibrated`。<br>(f) target 或 version 不是登記的 plan → `plan_version_mismatch`。<br>(g) 校準後的 plan 取代草案，人工 `approve_plan` → exit 0、phase `approved`：`approval` 含 decision、actor、at、plan 的釘選，以及 spec、ac、design 的 binding digest，但不含 `sa`；狀態裡只有一份 `plan`；再以另一個 id 送 `approve_plan` → exit 1 `already_approved` | (d) 的 `result.error == "plan_not_calibrated"`：4.1 只記錄，exit 0 | 全部成立 |
| `test_approve_plan_needs_spec_ac_and_design_bindings` | 已校準的 plan，只登記 spec、ac、design 的 7 種不完整子集 → exit 1 `missing_bindings`，恰好列出缺的角色，revision 不變，next 列出 `missing_binding:<role>`。三者都登記後，同一個 plan version 可以批准 | `code == 1`：前一個測試的實作不看 binding | 成立 |
| `test_next_after_approval_reports_dispatch` | 核准後，envelope 的 next 與狀態檔的 `next` 都是 `{action: dispatch, plan: {locator, version, digest}, approval: <id>}`；blockers `[]` | `next.action == "dispatch"`：`derive` 對核准還沒有規則 | 成立 |
| `test_changing_an_approved_document_needs_scope_change` | 核准後，以下都 exit 1 `scope_change_required`，核准與 revision 不變：新的 plan version；同一個 plan locator 但 bytes 改了；spec、ac、design 的內容改了；新增一份 spec。內容相同的重登 → exit 0、revision 不變。登記 `sa` 或 `policy` → exit 0，核准保留 | `code == 1`：登記會直接取代 | 成立 |
| `test_a_conflict_on_an_applied_approve_plan_follows_the_chosen_content` | 以 id X 人工批准（reason `a`），再以 X、reason `b` 重送 → exit 3。參數：<br>`original` → `approval.decision == X`，`decisions[X].reason == "a"`，phase `approved`。<br>`attempted` → phase `approved`，`approval.decision == X`，`decisions[X].reason == "b"`，`replaces[0]` 是 reason `a` 的紀錄並標 `voided_by`。<br>`abandon` → 狀態檔的 `approval is None`，phase `awaiting_approval`，next 回 `approve_plan`，`decisions[X].status == "voided"`；之後以新的 id Y 人工批准 → `approved`、`approval.decision == Y` | `abandon` 參數的狀態檔 `approval is None`：4.2 的撤銷只標 `voided`，核准還在（`attempted` 參數同樣失敗：沒清掉就再批准，得到 `already_approved`） | 成立 |

## 6. 範圍變更與政策核准

- [ ] 6.1 `scope_change` 撤銷核准並取代 plan，`policy_change` 綁定政策檔的 digest，`status` 顯示 policy 狀態，兩者被撤銷時只清掉自己的效果、不還原核准；驗證：`uv run pytest tests/test_scope_policy.py` 與完整的完成條件通過

**模式與 effort**：預設模式（D72）；Implementer Claude Opus 5.5、Reviewer GPT-6 Astra；effort（Implementer／Reviewer）xhigh／xhigh。

**交付**：

- `decisions.py`：
  - `scope_change`、`policy_change` 的檢查與效果；
  - `policy_change` 在 D10 表中的清除規則（`scope_change` 不需清除規則）；
  - 重登已被取代的 plan 時回 `plan_superseded`（D9）；
  - `approve_plan` 加上「未被取代」的檢查。
- `next.py`：`plan.superseded_by` 的衍生（D7）與 `plan_superseded` 阻擋。登記、`approve_plan` 與 next 都只用這一個衍生判斷 plan 是否被取代。
- `state.py`／`cli.py`：policy 狀態，依 D11 在讀取時計算。

**擁有路徑**：上列各檔，以及 `tests/test_scope_policy.py`。

**依賴**：5.1，從它取得：

- **登記項的形狀**：`plan`、`versions.bindings[role][locator]`、`versions.policy`，登記項帶 `path`、`digest`。
- **`approval` 的形狀與撤銷的清除規則**：只清除仍歸屬於該 decision 的效果，不還原任何核准（D10）。
- **`approve_plan` 的檢查順序**：「未被取代」插在「已校準」之後、「version 相符」之前。
- **已核准時的 `scope_change_required`**。
- **`derive` 的順序**：`plan_superseded` 放在 plan 阻擋中，不改其他條件的位置。

**AC**：O01（協調者不能自己做 scope 變更）、O07、O23、G22、D10（撤銷不還原核准）。

**Commit**：`feat(decisions): revoke approval on scope_change and bind policy`

`tests/test_scope_policy.py`：

| 測試 | 斷言的行為 | Red 失敗在 | Green |
| --- | --- | --- | --- |
| `test_scope_change_stops_the_run_and_supersedes_the_plan` | 參數：已核准、等待核准。人工 `scope_change`，帶 impact、reason 與兩個 `--open-question` → exit 0。紀錄含 impact、reason、`open_questions` 與 `supersedes`（舊 plan 的釘選）；狀態檔的 `approval is None`；phase `awaiting_approval`；`plan.superseded_by == [<id>]`；next 為 `human`、`[plan_superseded:<id>]`、`[]`。`agent:implementer` 送出 → `actor_not_human`，核准保留 | 狀態檔 `approval is None`（已核准的參數）：4.1 只記錄 | 成立 |
| `test_only_a_new_plan_version_is_approvable_after_scope_change` | 接續前一個測試：批准舊 plan → `plan_superseded`；以相同的 version 與 digest 重登 → `plan_superseded`。登記新 version 後，next 回 `approve_plan`；人工批准 → `approved`，next 為 `dispatch` | `code == 1`（批准舊 plan）：`approve_plan` 還不看是否被取代 | 成立 |
| `test_undoing_a_scope_change_never_restores_the_approval` | 參數都從「以 X 核准 plan P1 與 binding B1，再以 S 做 `scope_change`」開始，每個參數都斷言狀態檔的 `approval is None`：<br>(i) 只登記改過的 spec B2、plan 不變，以 S、不同內容重送 → exit 3，`--choice abandon` → exit 0。結果：`plan.superseded_by == []`；`decisions[S].status == "voided"`；next 為 `human`、`[plan_not_approved]`、`[approve_plan]`。之後以新的 id Y 人工批准 → `approved`，`approval.decision == Y`，`approval.bindings` 釘住 B2。<br>(ii) 同 (i) 的起點，改選 `--choice attempted`（A 是 impact 不同的 `scope_change`）→ `decisions[S]` 是 A 的內容，`replaces[0]` 是原內容並標 `voided_by`；`plan.superseded_by == [S]`；next 為 `human`、`[plan_superseded:S]`。<br>(iii) 登記新的 plan P2 之後，再對 S 製造衝突並選 `abandon` → exit 0；P2 不受影響；next 回 `approve_plan`。<br>(iv) 疊加：S 之後，對同一個 P1 再做 `scope_change` S2；對 S2 製造衝突並選 `abandon` → exit 0。`plan.superseded_by == [S]`；next 為 `human`、`[plan_superseded:S]`；批准 P1 → exit 1 `plan_superseded`；以 P1 相同的 version 與 digest 重登 → exit 1 `plan_superseded` | (i) 的 `next.blockers == ["plan_not_approved"]`。若 p1 的實作已經只算 `in_effect` 的 `scope_change` → 突變：暫時把 `voided` 的也算進去，(i) 得到 `[plan_superseded:S]`，(iv) 得到兩條 | 全部成立 |
| `test_policy_is_approved_only_by_policy_change_on_its_digest` | 未登記時，`policy.status` 為 `not_registered`，此時 `policy_change` → `policy_not_registered`。登記 `workflow.yaml` 後為 `not_approved`，帶 digest。以下都被拒：agent → `actor_not_human`；digest 不符 → `policy_digest_mismatch`；locator 不符 → `policy_digest_mismatch`。人工且正確 → exit 0，狀態 `approved`，帶 decision id 與 digest。`next` 不受 policy 影響 | `result.policy.status == "not_registered"`：視圖還沒有 policy | 成立 |
| `test_policy_changed_after_approval_is_not_approved` | 接續前一個測試：改動 `workflow.yaml` → `digest_mismatch`，帶核准時與目前的 digest；刪檔 → `unreadable`；還原後以改過的內容重登 → `not_approved`；對新 digest 做 `policy_change` → `approved` | `policy.status == "digest_mismatch"`：前一個測試的實作只看狀態，回 `approved` | 成立 |
| `test_undoing_a_policy_change_removes_its_policy_approval` | 以 P 核准 policy，再以 P、不同 reason 重送 → exit 3。參數：<br>`original` → `policy.status == "approved"`，decision 為 P 的原內容。<br>`attempted` → `approved`，`decisions[P]` 是新內容，`policy_approval.decision == P`。<br>`abandon` → `policy.status == "not_approved"`，狀態檔 `policy_approval is None`；之後以新的 id 做 `policy_change` → `approved` | `abandon` 參數的 `policy.status == "not_approved"`：5.1 的清除規則只處理 `approve_plan`，`policy_approval` 仍在 | 成立 |

## 驗收驗證

- 每條 AC 都由下表的測試在 G1（全新 clone、完整套件）與 PR 上的 `unit-linux` 通過來證明。
- to-pr 把結果彙整到 #29 的 PR Pass package，每條 AC 附測試名稱、Red 與 Green 的證據位置，以及 CI run 的連結。
- 「通過」指下表的每個測試都 Green，而且整個 session 依測試政策以 exit 0 結束。

| AC | 驗證的測試（task） | 通過代表 |
| --- | --- | --- |
| O01 | 3.1 `…creates_a_planning_run…`；5.1 `…only_a_human_approve_plan…`；6.1 `…scope_change_stops…` | 直接 `init` 就進入 planning，保存協調者 identity，不需要交接紀錄；協調者既不能批准，也不能做 scope 變更 |
| O03 | 5.1 `…registered_in_place…`、`…unreadable_documents…` | 登記保存原生 locator、version、digest，登記時的內容可讀回；原檔不改名、不搬移；讀不到就拒絕，狀態不變 |
| O05 | 5.1 `…status_shows_versions…`、`…only_a_human_approve_plan…`(a)(c) | 顯示等待開工確認與待確認的 plan 版本；時間經過或 agent 的表示都不產生核准 |
| O07 | 6.1 前兩個測試、`…undoing_a_scope_change…`(iv) | `scope_change` 保存影響與理由、撤銷核准、舊 plan 標為被取代；只要還有一筆有效的 `scope_change` 取代它，舊版就不能批准；新版本批准後 next 才是 `dispatch` |
| O15 | 3.1 `…uninitialised_run_is_not_found…` | 沒有 `init` 的 run：查不到、不建立、不接管其他 run |
| O19 | 4.1 `…only_human_actors_can_decide…`；5.1 (c)；6.1 agent 參數 | 非 `human:<name>` 的 actor 一律被拒，狀態不變 |
| O22 | 5.1 (d)(e)(g) | 只有 Implementer 校準過的 plan 能被批准，而且只有一份現行 plan |
| O23 | 6.1 前兩個測試（兩種起點）、`…undoing_a_scope_change…`(iv) | 保存影響與待決事項；整個 run 停在等待批准，直到新版本被批准 |
| O26 | 5.1 (b)(g) | `sa` binding 保存確認的版本與來源，但不產生核准；之後只有人工 `approve_plan` 產生核准，而且核准不以 `sa` 為依據 |
| O29 | 5.1 `…needs_spec_ac_and_design_bindings…` | 缺任一 binding 就拒絕並列出，三者都有之後同一個 plan 版本可以批准 |
| O30 | 4.1 `…unsupported…` | `adopt`、`delegate` 回 `unsupported`，revision、owner、核准都不變 |
| G21 | 1.1 t1、t2、t4、t5、t6；2.1 三個測試；PR 上的 `unit-linux` run | 違反政策時，本機的測試 session 以失敗結束；`unit-linux` 執行同一個命令、同一份設定，而且 t1～t6 在 Linux 上也通過 |
| G22 | 2.1 `…declares_unit_linux…`；6.1 兩個 policy 測試；驗收示範（見下） | 宣告了必要 check，但沒有綁定目前 digest 的 `policy_change`，或核准後檔案被改 → `status` 顯示未核准或 digest 不符 |
| D01 | 3.1 `…creates_a_planning_run…`、`…status_human…`；5.1 `…status_shows_versions…` | 狀態檔與 `status`（含 `--human`）都直接顯示 phase、協調者、owner、版本、核准、gate 的狀態與原因、blockers、next |
| D02 | 3.1 `…manual_edit…`；4.1 `…recorded_with_its_provenance…`、`…missing_fields…` | 手改被偵測、不覆寫，也不被當成決策；decision 只能經 `decide` 產生，並保存決策者、來源、理由與影響 |
| D03 | 3.1 `…claim_grants…`、`…concurrent_claims…`；4.1 `…need_the_coordinator_token…`、`…non_owners_cannot_resend`；4.2 `…non_owners_cannot_create_conflicts`；5.1 `…unreadable_documents…`（`register` 的 token） | 恰一方取得協調權，其餘得到受控的 `already_claimed`；另一方可以讀取，但任何寫入（包括重送與不同內容的重送）都被拒，bytes 不變 |
| D09 | 3.1 兩個 interrupt 測試、`…failed_sync_before_the_link…`、`…stale_revision…`、`…object_references…`；4.1 `…consecutive_interruptions…` | 中斷或第一個同步點失敗後讀到完整的舊版或新版，連續兩次中斷也不遺漏已提交的 revision；revision 會被核對；引用的物件缺失或毀損時不提交 |
| D10 | 3.1 `…interrupt_before…`；4.1 `…takes_effect_once…`、`…consecutive_interruptions…`；4.2 `…blocks_the_run…`、兩個 `resolve_conflict` 測試；5.1 `…conflict_on_an_applied_approve_plan…`；6.1 兩個 `…undoing…` 測試 | 已提交的不重複生效；未提交的不被接受；內容不同時 Blocked，保留兩份內容，直到人工 decision 選定原內容、改採嘗試的內容或放棄；撤銷只清掉自己的效果，從不還原核准 |
| D11 | 3.1 `…untrusted_state…`、`…never_overwrites…`、`…object_references…`；4.2 `…blocks_the_run…` | 顯示具體原因與現存檔案，原檔不變；`init` 不覆寫，也不建立空 run |
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
- 兩個平台跑同一套測試。測試覆蓋的是：`flock` 下的並行 `claim`；`os.link`、`os.replace` 前後中斷的恢復，包括連續兩次中斷；第一個同步點失敗時不提交，這個同步點是 history 暫存檔的 fsync，在 `os.link` 之前。
- 以下沒有測試證據，列為限制（design Risks）：`os.link` 之後的同步失敗、`F_FULLFSYNC` 是否被呼叫、資料是否真的寫到裝置、斷電後的持久性。

## 風險

- 產品層的風險見 design 的「Risks / Trade-offs」。
- **並行測試（3.1）**：gate 讓所有程序在 `os.link` 前會合，或在 3 秒後逾時，並記下到達數與放行原因。
  - 沒有 lock 時，只有 8 個都到齊才放行的那次，才確定發生了競態；Red 證據要附這份 gate 紀錄，逾時放行的那次重跑。
  - 有 lock 時，只有持 lock 的程序到得了 gate，逾時一次後依序執行，所以這個測試約多花 3 秒。
  - 斷言「每個落敗者都得到受控的 `already_claimed`」與排程無關。若 flaky，追根因，保留嚴格斷言，不加 retry。
- **突變 Red**：共 9 項，Reviewer 要核對每項的突變與輸出。
  - 固定要突變的：t4、dist-smoke、`…has_one_source`、`…interrupt_before…`、`…non_owners_cannot_resend`、`…non_owners_cannot_create_conflicts`。
  - 視實作順序而定的：`…concurrent_claims…`（單次 `claim` 已加 flock 時）、`…stale_revision…`（已核對 revision 時）、`…undoing_a_scope_change…`（p1 已只算 `in_effect` 時）。
- **`unit-linux` 第一次實跑在 to-pr**：結構已由 2.1 在本機檢查；實跑失敗走 to-pr 的修正迴圈。
- **task 的份量**：
  - 本版把原本的 4.1 拆成 4.1（紀錄、授權、重送、前移，9 個測試）與 4.2（衝突與三種解除，4 個測試）；
  - 3.1 有 13 個測試，是最大的一個，但都落在同一個 store 與四個命令上。
  - 任何 task 超出一個 session 時，停下，依 D71 拆成更小的垂直切片（例如 3.1 拆成「`init`、`status`、`next` 與不可信偵測」和「`claim`、並行與中斷恢復」）；改過的計畫回到計畫審查，不在 task 內部硬塞。

## 執行界線

- 依 D13：主動執行時間最多 4 小時；修正最多 3 輪；每個 infra 操作額外重試最多 2 次。到限時保存現況，轉 Blocked 交人（D70）。
- 每個 task 最多 3 次 attempt，修正也算在內（plan-to-code）。
