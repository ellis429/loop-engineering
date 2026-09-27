# Cleanup map：舊 S1 `src/delivery/` 21 模組的去向（D45 候選 design-02）

> **狀態**：候選，未 D11。
> - D45-R05／R06 已在 review-04 verified；本版只更新狀態與引用，§3 的歷史程式證據沒有改動。
> - D46 已確認（隔離重建），D47–D49 已確認。
> - 本文不刪除正式 src/tests，只提出去向與完成條件。實際清理步驟在 [tasks.md](tasks.md) H1-0 與 H1-15，驗證在 [validation.md](validation.md)。
> - §3「新責任」欄的模組名稱只是暫定落點。依 [design.md](design.md) §2，模組數量不預先規定，可以合併。
> 依據：inputs 快照（HEAD `4ce111011fde83c3a2784402cea111e52a954b3c` 加上未提交文件）的原始碼閱讀；[source-inventory.json](/Users/johnson.chiang/workspace/loop-engineering/.delivery/bootstrap/herdr-design-d45-01/source-inventory.json) 是靜態 import 盤點，只作參考，**import 可達不代表功能正確，也不代表產品路徑真的會呼叫到**。

## 1. 結論

- **沒有全部 stale，但產品路徑幾乎沒有被使用**：`cli.py` 只呼叫 `loop.start_run`／`loop.Context`；`loop.step()`／`run_until_idle()` 只在 `tests/test_loop.py` 被呼叫；`cmd_resume`、`cmd_reconcile` 對外部工作一律回 exit 3（`cli.py:247,257`）；`resume.resume()` 沒有任何產品呼叫者。所以主迴圈、outbox、整合、G2／G3 只由測試驅動。
- 這不代表 CLI 不寫狀態（D45-R06）：`decide`、abandon，以及 resume／reconcile 的本機 reconcile 都會提交狀態；逐項去向見 §3 第 14 列。
- 去向：**重用（提取）10、重寫 4、不帶入 7**。「重用」仍須通過缺陷覆核與新測試才可進新樹（§4）；不整批複製。
- 17 項 S1 findings 全部維持 open；移除舊模組不算關閉 finding。

## 2. 新工作區（D46 已確認：「要沿用的就包進 new worktree or dir 不要混了」）

- 目標目錄 `/Users/johnson.chiang/workspace/loop-engineering-thin`，目前只有 README 與 `docs/design-candidate`，還不是 Git worktree。
- 建議接回方式 **W1**（接法本身尚待採用；要在使用者採用及 D11 後才執行，本輪不做）：
  1. 在 `loop-engineering` 提交採用後的文件，記為 commit B。
  2. 把 thin 目錄現有內容移到旁邊保存，再執行 `git worktree add -b delivery/thin-controller <thin> B`。
  3. 新 branch 的第一個 commit 只移除舊 `src/delivery/`、`tests/` 與 CI 裡的 `delivery` 設定，並加上 `docs/implementation/removed-s1.md`，指向 `4ce1110`、`5d334d5`、PR #2 與 S1 證據封存位置。
- 不採用的方案：W2 orphan branch（沒有共同歷史，PR 困難）、W3 新 repo 或純目錄（違反「不擅建 repo」，而且產生不了 G1 需要的 commit／snapshot）。
- 規則：
  - 新套件改名為 `loopctl`，只有一個 console 入口。
  - 不設定指向舊 src 的 `PYTHONPATH`，不用 editable 依賴，不建 `legacy/`、`v2/`。
  - 以測試確認 `import delivery` 會失敗。
  - 正式規格仍只在 `loop-engineering` 的 `openspec/changes/implement-delivery-loop/`。

## 3. 21 模組逐項

去向欄的意思：
- **重用**：提取指定 symbol，修正後附新測試。
- **重寫**：新樹重新實作，舊碼只作行為參考。
- **不帶入**：新樹沒有對應程式，歷史查 Git／PR。

| # | 模組（行數） | 現有責任 | 可觀察呼叫關係 | 去向 | 一句依據 | 新責任／新測試 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `__init__`（1） | 套件標記 | 無 | 不帶入 | 新套件是 `loopctl`，沿用同名套件會讓舊碼有機會被誤載 | `loopctl/__init__`；`test_cleanliness` |
| 2 | `store`（205） | 原子 snapshot、blob、引用完整性、手改偵測 | cli、loop、authority、events、results、resume | 重用（僅 `_full_fsync`、`_write_tmp`、`put_blob` 的 link 協定） | `_refs` 用 regex 把所有 `sha256:` 字串都當成 blob（`store.py:103-110`），這是 R06 的根因；commit 也沒有先寫歷史 | `store.FeatureStore`（history-first、typed BlobRef）；`test_store` |
| 3 | `findings`（67） | registry、blocking 分類、closure 權限 | loop、decisions | 重用 | `import_review` 在 `matches` 指到已 resolved 的 finding 時只覆寫欄位，狀態仍是 resolved（`findings.py:19-31`），這是 R16 | `findings`，加上 reopen 與 closure_history；`test_findings` |
| 4 | `runner`（209） | baseline＋overlay Red snapshot、junit 分類 | cli evidence、loop | 重用（`snapshot_worktree`、`_drifted`、`_classify`、`_case_ids`） | snapshot 語意已有真 git 測試；但 `run_evidence` 接受任意 argv（R01／R13 的入口） | `tools/evidence_run`，只接受 policy `command_id`；`test_evidence_tool` |
| 5 | `controller`（101） | intake 路由、派工授權、D27 依賴、reassess | cli adopt、loop、decisions、resume | 重寫（`dependency_ready` 規則可參考） | `authorize_dispatch` 要求 `plan_producer`，但 `approve_plan` 從不寫入這個欄位（`controller.py:49` 對照 `decisions.py:128`），這是 R07 | `engine.next_action`；`test_engine`、`test_decisions` |
| 6 | `resume`（50） | 載入→歷史→operations→results→版本 | 無產品呼叫者（只有 `test_resume`） | 不帶入 | 產品入口不可達，依賴的 outbox／events 模型也不再使用 | `engine` 的 reconcile 動作；`test_ops` |
| 7 | `results`（64） | inbox 匯入、去重、衝突、身份核對 | loop、resume | 重用（`_identity_problems`、duplicate／conflict 判定） | 先存原件再判定、同 bytes 去重、不同 bytes 衝突的語意正確；欄位要從 clone 改成 worktree | `assignments.import_result`；`test_results` |
| 8 | `events`（111） | events.jsonl 追加、尾筆截斷、ID 去重 | loop、cli、resume | 不帶入 | 狀態提交與歷史寫入分成兩次 commit（`loop.py:565-574`，R04）；`_scan` 遇到同 ID 以後者覆蓋（`events.py:49`，R03） | `store` 的 history-first revisions；`test_store` |
| 9 | `budget`（68） | active 聯集、crash 區間、失敗路由 | loop、cli | 重用 | 函式是純的，算法可沿用；但舊流程只在派工 guard 檢查（R09），新 engine 每次呼叫都要算 | `budget`＋deadline／overrun；`test_budget` |
| 10 | `decisions`（172） | 人工 decision、接受／退回、解除 | cli、loop | 重寫（驗證規則可參考） | `scope_change` 寫入 `pending_scope`，但 `start_run` 建的狀態沒有這個 key（`decisions.py:131` 對照 `loop.py:92-105`），R10 會 crash；`approve_plan` 也沒有保存 provenance（R07） | `decisions`；`test_decisions` |
| 11 | `gates`（213） | G1／G2／G3／Pass 純函式 | loop、測試 | 重用 | 結構是確定性的，但 `_red_problems` 沒驗 exit／stderr／身份（`gates.py:22-36`，R13），`allow_non_success` 接受任意 conclusion（`gates.py:170-175`，R17） | `gates`＋`evidence`；`test_gate_g1/g2/g3`、`test_pass` |
| 12 | `integration`（43） | fetch、scope 核對、CAS fast-forward | loop | 重用（檢查順序與 `update-ref A T0`） | CAS 語意正確；per-attempt clone fetch 在 Herdr worktree 模型下不需要 | `tools/git.integrate`；`test_git_tool` |
| 13 | `sandbox`（102） | Seatbelt profile、負例套件 | 只有 cli `preflight` 的基本 probe | 不帶入 | D41 已排除自建 OS sandbox；隔離改由 runtime 既有權限提供並實測 | H2 的 runtime 權限能力報告 |
| 14 | `cli`（337） | 10 個命令 | 唯一入口 | 重寫 | 從未驅動 delivery loop（沒有呼叫 `step`／`run_until_idle`；resume／reconcile 在外部工作前回 exit 3，`cli.py:247,257`）。但會寫狀態的命令不只 start／adopt（D45-R06）：`cmd_decide` 寫 decision（`cli.py:141-160`），`_abandon` 寫 authority 與 run（`:165-181`），resume／reconcile 經 `_reconcile_local` 寫 crash 區間預算與 flush 歷史（`:223-239`）。這些 decision／budget／history 行為在新樹分別由 `decide`、`abandon_epoch`、design §13 的 gap 計入與 design §4 的 history-first 提交**明確取代**，不是隨舊 CLI 消失 | `loopctl` 單一 CLI；`test_cli` |
| 15 | `authority`（135） | 主機層 feature locator、run lineage、預算加總 | cli、loop | 不帶入 | 預算加總只存在於 `Authority.budget()`，派工 guard 只看本 run（`loop.py:138-140`，R08）；兩份 authority 會不同步 | `feature.json`＋epoch＋`claim`；`test_claim` |
| 16 | `publication`（51） | review 發文內容、status 渲染 | loop | 重寫（發文模板可參考） | `render_status` 讀取不存在的 `versions_key` 欄位（`publication.py:42`）；發布要改用新的 operation 模型 | `status`、`tools/gh.publish`；`test_status` |
| 17 | `loop`（616） | 主迴圈：派工、整合、Red replay、Green、N/A、PR、reread、修正 | 只有測試呼叫 `step`／`run_until_idle` | 不帶入 | 會執行 worker 結果裡的 argv（`loop.py:233`，R01）；先 clone 後登記（`loop.py:166` 對照 `:184`，R05）；fix task 缺 finding 內容（`loop.py:460-463`，R12）；G1 只看有變更的 task（`:396-399`，R11） | `engine`＋`ops`＋tools；`test_scenarios` |
| 18 | `correction`（89） | batch、輪次、一次爭議、recurrence | loop、decisions、publication | 重用 | `ready_for_batch` 把 G3 unknown 也當終態並進入修正（`correction.py:11,18`），這是 R14 | `correction`，加 G3 route；`test_correction` |
| 19 | `versions`（141） | binding／observation、VersionSet、依賴矩陣 | controller、loop、resume | 重用 | 純函式，未列欄位 fail-closed（`versions.py:109`）；skills×G3 的歧義要用新測試固定為 R-reobserve | `versions`；`test_versions` |
| 20 | `retro`（22） | acceptance＋版本去重、P03 guard | decisions | 重用（併入 decisions） | 去重 key `decision@version` 語意正確，也夠小 | `decisions.accept`；`test_decisions` |
| 21 | `outbox`（194） | GitHub marker 查回、runtime session 分段派工 | loop、resume、publication | 不帶入 | `RuntimePort` 是 session／prompt 的 HTTP 形，和 Herdr 不同；unknown 時會遞迴重建 session（`outbox.py:162-163`，R02） | `ops`（prepare／begin／record）＋`tools/gh`；`test_ops` |

## 4. 來源提取契約（每個「重用」項都要符合）

- 每次提取在新樹的 `docs/implementation/extraction-manifest.json` 加一筆，欄位如下：

```json
{"id": "X-03", "source": {"commit": "4ce111011fde83c3a2784402cea111e52a954b3c", "path": "src/delivery/findings.py",
  "symbols": ["import_review", "close", "open_blocking"], "file_sha256": "45530ad6…(inputs manifest 值)"},
 "target": {"path": "src/loopctl/findings.py", "symbols": ["import_review", "close", "open_blocking"]},
 "findings": ["S1-R16"], "modifications": ["matches 指向 resolved/waived 時 reopen，closure 移入 closure_history"],
 "new_tests": ["tests/test_findings.py::test_resolved_match_reopens_and_blocks"],
 "red_evidence": {"blob": "sha256:…"}, "review": {"reviewer": "…", "result": "…"}, "status": "proposed|accepted|rejected"}
```

- 規則：
  - 只複製列出的 symbol，逐段改寫到新介面，不整檔搬移。
  - 新測試先在新樹 Red，確認舊行為的缺陷存在，再改到 Green。
  - 舊測試逐個案例評估（§5），不整檔複製。通過評估的行為測試可選擇性提取改寫：改 import／介面並在 manifest 記來源 `test_file::test_name`、檔案 sha256 與修改內容。舊 pass 數不作新證據，提取的測試必須在新樹重新執行。
  - `feat/s1-fix-01`（`5d334d5`）的未覆核修正可作參考，但 manifest 必須標 `unreviewed_source`，而且同樣要附新測試。
  - 提取不算 finding closure；closure 要等獨立 Reviewer 覆核。

## 5. 舊測試的去向

- `tests/` 下共 34 個檔案（30 個 `test_*.py`、`fakes.py`、`fake_agents.py` 與兩個 `__init__.py`），**不整批複製，也不強制全部重寫**（D45-R05）。以測試案例為單位，依三項評估：
  - 是否驗證新契約仍保留的行為；
  - 是否帶有已知的來源缺陷（R01–R17）；
  - 是否耦合到不帶入的平台。
- 評估後三種處理：合格的案例依 §4 選擇性提取改寫；平台專屬的案例退役；新 CLI 的行為另寫新回歸測試。舊 pass 數不沿用為新證據。
- 以下檔案耦合不帶入的模組或平台，預設退役、只留在歷史中（個別案例若只驗保留行為，仍可依 §4 評估）：
  - `test_loop`、`test_controller_e2e`、`test_dispatch_recovery`、`test_outbox`、`test_resume`、`test_events`
  - `test_authority`、`tests/os/test_sandbox_*`、`test_cli`、`test_cli_commands`
- 以下檔案對應重用或重寫的規則，逐案評估後可選擇性提取改寫。例如 `test_budget.py::test_overlapping_worker_and_ci_count_once` 驗證的正是沿用的 active 聯集算法，改 import 並記錄來源即可。含已知缺陷的案例（如 R13、R16、R17 相關）必須改寫成新測試：
  - `test_store`、`test_store_crash`、`test_runner`、`test_results`、`test_budget`
  - `test_gate_g1/g2/g3`、`test_pass`、`test_findings`、`test_correction`、`test_versions`
  - `test_assessments`、`test_integration`、`test_decisions`、`test_retro`、`test_status`、`test_publication`
  - `test_controller_flow`

## 6. 完成條件（已併入 tasks.md H1-15 與 validation.md V-CLEAN）

1. 新樹中只有 `loopctl` 一個 console script；沒有 `delivery` 套件，也沒有 `legacy/`、`v2/`。
2. `tests/test_cleanliness.py` 通過，檢查以下幾點：
   - 核心模組不 import `subprocess` 或 `loopctl.tools`；
   - 每個模組至少有一個非測試的生產呼叫者，或是 CLI 子命令；
   - `import delivery` 會失敗。

   靜態引用只能證明「可達」，不能證明實際會執行（D45-R06）。實際路徑以經公開 CLI 的行為測試驗證，包括 decide、abandon_epoch、預算 gap 計入、history 提交，以及兩個 tool 程序同時 begin 同一 op。
3. extraction-manifest 涵蓋所有「重用」列與所有提取的測試案例，每筆都有在新樹實際執行的測試紀錄。修正缺陷的項目另需 Red 證據，證明舊缺陷在修正前確實重現；「重寫」與「不帶入」列在 manifest 中標 `not_extracted`，並附一句理由。
4. 移除舊 src／tests 和新入口在同一個 branch 交付，不留並存期；`docs/implementation/cli.md` 同步改寫。
5. 17 項 findings 各有對應的新回歸測試，狀態仍是 open，等待獨立覆核。
