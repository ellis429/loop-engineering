# Validation：第一個可用切片（候選 design-04；revision-17）

> **作者提交狀態**：revision-17；目前的 review 狀態以 [README](README.md) 為準。
> **全部是 planned，沒有任何測試已執行，也沒有任何 AC 已通過。** 每個 ID 的歸屬以 [coverage.md](coverage.md) 為準。revision-12 新增或修改的案例標 `[r12]`，revision-13 的標 `[r13]`，revision-14 的標 `[r14]`，revision-15 的標 `[r15]`，revision-16 的標 `[r16]`，revision-17 的標 `[r17]`。
> 本文分三類驗證，不互相代替：
> - 產品測試矩陣（§2）；
> - workflow 樣本加 rubric（§3）；
> - 真實證據（§5）。
>
> fake 證據不改標為 real。附證據的 Blocked 不算示範完成。

## 0. 必要測試政策

同一套政策用於本機 G1 與每個 CI job（design §11；D51-R05）：

- 由 test-only 設定執行：`pyproject.toml` 的 pytest 設定（`--strict-markers`、`xfail_strict=true`）與 `tests/conftest.py`。不是產品 hook，也不是 registry。
- 平台專屬案例只用 `only_on(<platform>)` marker 選擇，例如 fsync 順序只在 Linux 執行。
- 以下任一 → session 失敗：收集數為 0；不是由 `only_on` 在非所屬平台產生的 skip（reason 寫著 platform 也一樣）；xfail／xpass；CI job 的預期平台與實際不符。
- **本機**：session 失敗 → G1 不通過；G1 不等待遠端 CI。
- **遠端 CI**：每個必要 job 用同一命令；job 失敗 → G3 不通過（M-GH 的 h2、h4、h12）。
- 政策本身的行為由 M-TPOL（t1–t6）驗證。
- 不為了變綠而放寬斷言或刪除案例。

## 1. 環境

| 代號 | 內容 |
| --- | --- |
| ENV-F | Python 3.12（uv）、真 git ≥ 2.38（整合核對用 `merge-tree --write-tree`）；PATH 上放 fake `herdr`／`gh`（依情境檔回應，並記錄 argv 與呼叫次數） |
| ENV-R | Herdr 0.9.1；Implementer：Claude Code＋`claude-opus-5-5`＋`--effort high`；Reviewer：OpenCode＋`openai/gpt-6-astra`＋`--variant xhigh`（design §6，待 D11） |
| ENV-GH | `yschiang/loop-engineering` 的 PR／issue／Actions |

## 1.5 矩陣、task、門檻與證據位置 [r15]

| 矩陣 | 測試檔 | Task | 環境 | 通過門檻 | 證據位置 |
| --- | --- | --- | --- | --- | --- |
| M-TPOL、M-PRE | `test_test_policy.py`、`test_ci_workflow.py`、`test_preflight.py` | 1.1 | ENV-F | 該檔所有參數化案例通過，套件 session 依 §0 exit 0 | `.delivery/bootstrap/thin-s1/tasks/1.1/evidence/` |
| M-STATE | `test_state.py` | 2.1 | ENV-F | 同上 | `…/tasks/2.1/evidence/` |
| M-DEC（d7b 除外） | `test_decisions.py`、`test_public_path.py`（d3） | 2.2、2.3 | ENV-F | 同上 | `…/tasks/2.2/`、`…/tasks/2.3/` |
| M-OBS、M-WRITE、b0 | `test_observe.py`、`test_writes.py`、`test_active_time.py` | 2.3 | ENV-F | 同上 | `…/tasks/2.3/evidence/` |
| M-G1 | `test_g1.py` | 3.1 | ENV-F（真 git ≥ 2.38） | 同上 | `…/tasks/3.1/evidence/` |
| M-GH | `test_github.py` | 6.1 | ENV-F | 同上 | `…/tasks/6.1/evidence/` |
| M-BUD（b0 除外） | `test_budget.py` | 7.1 | ENV-F | 同上 | `…/tasks/7.1/evidence/` |
| M-REV | `test_review.py` | 5.1 | ENV-F | 同上 | `…/tasks/5.1/evidence/` |
| M-PASS（含 d7b）、M-RESUME | `test_publish_pass.py`、`test_resume.py` | 6.2 | ENV-F | 同上 | `…/tasks/6.2/evidence/` |
| W-A–W-F | 樣本＋rubric | 4.3 | 文件 | 每組正例成立、負例被指出，獨立 Reviewer 記錄 | `docs/validation/s1/proof.md` |
| R1、R2、R3 | 真實執行 | 1.2、4.2、8.1 | ENV-R、ENV-GH | 見 §5 | 見 §5 |

每個 task 完成時，整個套件在該 task 的 head 上依 §0 通過（前面 task 的列仍通過）；只跑自己的檔案不算完成。

## 2. 產品測試矩陣（ENV-F，參數化）

每一列是一個參數化案例，格式為「輸入／前置 → 動作 → 斷言」。檔案與 task 見 tasks.md 的執行表。

### M-TPOL：`tests/test_test_policy.py`（T1.1）[r12]

以 pytester 在子 session 執行，平台以 conftest 的單一平台函式模擬。

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| t1 | `only_on("linux")` 的案例，在 macOS 執行 | 該案例 skip；session exit 0 | G13 |
| t2 | `only_on("linux")` 的案例，在 Linux 執行時自行 `pytest.skip("missing tool")` | session exit ≠ 0，列出該案例 | G13 |
| t3 | 沒有 `only_on`，以 `skipif(True, reason="platform: linux only")` 或 `pytest.skip("platform")` skip | session exit ≠ 0；reason 文字不被接受 | G13 |
| t4 | 收集數為 0（空目錄或全被過濾） | session exit ≠ 0 | G13 |
| t5 | 一個 xfail、一個 xpass | 兩者都使 session exit ≠ 0 | G13 |
| t6 | `LOOPCTL_EXPECT_PLATFORM=linux`，實際平台為 darwin | session exit ≠ 0 | G13 |
| t7 [r16] | `tests/test_ci_workflow.py` 讀取 `.github/workflows/loopctl-ci.yml` 與 `workflow.yaml`：每個 `required_checks` 都對應一個同名 job；每個 job 依序 checkout PR head SHA、核對 `git rev-parse HEAD`、在測試前上傳 `tested-sha-<job>-<run_attempt>`、`uv sync --frozen`、以 `uv run pytest` 執行並設定 `LOOPCTL_EXPECT_PLATFORM`；觸發只有 `pull_request`。變體：刪掉某 job 的 pytest 步驟、改成 push 觸發、少一個 required job | 正例通過；每個變體都失敗並指出該 job 或欄位。真正的 CI 行為仍以 B1 的 G3 實跑為證據 | G13、G14 |

### M-STATE：`tests/test_state.py`（T2.1）

| 案例 | 輸入／前置 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| s1 | rev 3；在新 revision **提交前**中斷，再 `status` | revision 為 3；未提交的變更不存在；沒有任何 write | D09、D10 |
| s2 | 在 revision 4 **已提交**後中斷，再 `status` | revision 為 4；沒有重複的 transition；history 可讀 | D09、D10 |
| s3 | 缺檔、壞 JSON、`schema_version=9`、手改的 gate、transition ID 衝突，各一次 → `status` 與 `next` | exit 5，或 Blocked 並附原因；原檔的 bytes 不變；預算不被清空；0 次派工、0 次寫入 | D11、D02 |
| s4 | 兩個程序同時 `claim`；兩個程序同時 commit | 恰一方成功；token 明文不在狀態中 | D03、O02 |
| s5 | `status --human` | 可讀到 phase、每個 gate 的狀態與原因、blockers、下一步 | D01 |
| s6 | 文件 digest 欄位指向不存在的物件；證據物件引用缺失 | 前者正常提交（digest 不被當作物件引用）；後者拒絕提交 | S1-R06 |
| s7 [r15] | 對沒有 `init` 的 feature 執行 `status`、`next`、`claim`；以及 `$LOOPCTL_HOME` 內有其他 feature 的狀態 | 前者回報不存在，不建立狀態、0 次派工與寫入；`claim` 不接管其他 feature | O15 |

### M-DEC：`tests/test_decisions.py`（T2.2；d3 在 T2.3 的 `tests/test_public_path.py`；d7b 在 T6.2 的 `tests/test_publish_pass.py`）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| d1 | 使用者直接 `init` 並登記 plan，沒有 Project Lead 交接 | 進入 planning；沒有 `approve_plan` 時 0 次派工 | O01、O05 |
| d2 | 批准來源矩陣：沉默、timeout、agent 身分、只有 SA 確認、草案 plan（producer=project_lead）、校準後的 plan＋人工 `approve_plan` | 只有最後一項產生 approval；只有 SA 確認時仍然 0 次派工 | O05、O22、O26 |
| d3 | 批准後透過公開 CLI（T2.3）執行 `next` | 第一個 assignment 帶有 task 的 AC IDs 與驗法；之後的正常 fix 不需要逐 task 再批准 | O06 |
| d4 | implementing 期間送 `scope_change` | 批准失效，整個 run 進入 awaiting_approval（第一片不做部分接續）；不 crash | O07、O23（第一片部分） |
| d5 | 以 runtime 父 session 身分，或 Project Lead 角色標記 `decide approve_plan` | 拒絕；權限只看人工 decision 與 token | O19 |
| d6 | 登記原生路徑的 plan 與 spec，並讀回 | locator、版本與內容可讀回；不改名；task 不另外變成 PR | O03 |
| d7a [r15] | 決策紀錄層：`return`／`accept` 由 agent 身分送出；缺 actor、版本或理由；目前沒有 Pass 時 `accept` | 全部拒絕，狀態 revision 不變（正向路徑與效果由 T6.2 的 d7b 驗證） | O11、F11 |
| d8 | 呼叫 `adopt` 或 `delegate` 入口 | 回 `unsupported`；狀態不變；沒有繞過任何核對 | O08、O09、O18（僅負例） |
| d9 [r12] | `resolve_read`／`resolve_operation` 由 agent 身分送出；缺原因或目標 ID；人工且完整 | 前兩種拒絕；第三種只寫入 decision 紀錄，0 次外部寫入、0 次 fetch（效果由 o1、w10 驗證） | D13、D16 |
| d10 [r15] | `budget_extension` 的四種目標（`active`、`rounds`、`attempts:<unit>`、`ci_wait:<H>`）；缺理由；未知目標；agent 身分 | 前者各寫入一筆紀錄，不改 `workflow.yaml`、不重置其他計數；其餘拒絕（效果由 b2–b6、r14 驗證） | D17、F07 |

### M-OBS：`tests/test_observe.py`（T2.3）[r12]

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| o1 | `worker:<attempt>` 連續傳輸失敗 3 次，之後換新 seq、新 session、restart；再以 `resolve_read` 恢復，又失敗 3 次 | 第 3 次失敗後 Blocked；之後 0 次自動 fetch；計數不重置；`resolve_read` 只給一次 3 次額度，用完再次 Blocked | D16 |
| o2 | `native:<attempt>` 讀取：同 purpose 較舊 seq 晚到 | 只存歷史，不覆蓋目前事實 | G16、D06 |
| o3 [r15] | fake `herdr` 的讀取超過 `limits.read_call_s` | 子程序被終止；算一次傳輸失敗並計入 `read_budget`；不當作成功取得 | D16 |

### M-WRITE：`tests/test_writes.py`（T2.3）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| w1 | 兩個程序同時 `write prompt` 同一個 op | fake herdr 被呼叫 1 次 | D13 |
| w2 | 送出後 receipt 遺失，查回原 marker；[r15] 讀回的 marker 屬於其他 op，或 marker 相符但目標身份（session、pane）不符 | 前者讀回後轉為 succeeded，沒有重送；後兩者不轉為 succeeded，維持 unknown 並 Blocked，0 次重送 | D12、D13 |
| w3 | 延後生效的 worktree、查無的 prompt、client 已結束 | unknown＋Blocked；0 次重送 | D13、S1-R05 |
| w4 | 讀回結果依序為「仍在執行」×3 | 第 4 次讀回被拒；變成 `blocked(readback_exhausted)` | D16 |
| w5 | writer 結束矩陣（經 T2.3 的 `observe worker\|native`）：只有 terminal idle／Herdr `done`；結果已匯入＋native turn 完成；stop 經 process-info 確認；狀態 unknown | 前一項 → 0 次派下一個；中間兩項 → 允許派下一個；unknown → Blocked | D04 |
| w6 | result 的身份、cwd、head、scope 不符，或內含 worker 提供的 argv | 拒收；原件保存；列出差異 | D05 |
| w7 | 同一個 result 重送；同 attempt 但 bytes 不同 | 前者沒有新的 transition；後者雙方都保存並 Blocked | D08 |
| w8 | 沒有結果檔、也沒有通知，native transcript 裡有 marker 之後的結果 JSON（經 T2.3 的 `observe native`）；[r15] 結果 JSON 在其他 attempt 的 marker 之後；marker 之後仍有執行中的 tool call | 第一種：工具寫出 result，帶 `producer=tool`、native session／message ID、原文 digest，並匯入一次；無法解析 → unknown；其他 attempt 的結果或 turn 未完成 → 不匯入、不視為 writer 結束 | D06、D04 |
| w9 | Claude uuid 與 OpenCode `ses_…` 兩種 handle 的 round-trip；result 的 native ID 不符 | 以 attempt ID 對回；不符 → 拒收；不補造 ID | D21 |
| w10 [r12] | `resolve_operation` 矩陣，對象為 unknown 的 `prompt` op：`--bind` 且新讀取相符；`--bind` 但不符；`--not-delivered` 只附 controller 的查無觀察；`--not-delivered` 附 client 未送達紀錄，之後重試到第 3 次 | 相符 → succeeded（`resolved_by=human`），0 次重送；不符 → 拒絕；只有查無 → 拒絕，仍 unknown；未送達紀錄 → failed(確定未送達)，重試最多額外 2 次，第 3 次重試被拒；decision 本身 0 次外部寫入 | D12、D13、S1-R02 |
| w11 [r15] | fake `herdr` 的 `prompt` 超過 `limits.write_call_s` 才回應 | 子程序被終止；op 記為 unknown（不是 failed）；0 次重送；之後只提供讀回 | D13、S1-R02 |

### M-G1：`tests/test_g1.py`（T3.1）

finding ID 與 batch ID 在 T3.1 以 attempt metadata 的 fixture 提供；完整派修流程在 r11 驗證。

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| g1 | 原始 Red 有效，head Green 通過，不做 replay | G1 passed | G06 |
| g2 | 證據互相矛盾 → 觸發 replay：成功與失敗各一 | replay 只作診斷：成功 → 繼續，失敗 → Blocked；都不能補造 Red | G06、G07 |
| g3 | 分別污染 raw、exit、task、snapshot、producer | 每一種各自使 G1 失敗，並列出原因 | G04 |
| g3b | 適用資格（D51-R07）。各情境的 raw 與 producer 都有效，而且都另做一次 replay 且成功：<br>(a) snapshot 或 attempt 的 commit 超出核准 scope；<br>(b) **兄弟 snapshot**：與 attempt 有共同的 parent，但沒有對應到該 task／attempt 的捕捉紀錄，它的測試內容也不在 attempt 的 commit 中；<br>(c) attempt 不是 H 的祖先；<br>(d) 正例：尚未 commit 時捕捉的原始 Red，provenance 帶有 task／attempt，而且它的測試 delta 出現在 attempt 的 commit 中，attempt 是 H 的祖先 | (a)、(b)、(c) 各自使 Red 無效，replay 成功也不能補救；(d) 有效，不需要同 SHA，也不需要 replay | G04、G06、G08、S1-R13 |
| g4 | 缺原始 Red；task 集合為空；只有語法錯誤的 Red | G1 fail；缺原始 Red → Blocked（`original_red_unavailable`） | G07、S1-R11 |
| g5 | 證據存在 repo 外；C 之後的文件 commit 產生 head D；[r15] fake Green 命令記錄它執行時的 SHA，另一變體讓 Green 在 D 失敗 | tracked 文件只引用 result ID 與 digest；Green 的紀錄 SHA 等於 D（不是 C）；Red 依 lineage 仍適用；記錄「只有文件差異」的理由；Green 在 D 失敗 → G1 不通過 | G05 |
| g6 | 整合 regression 失敗 | `gates.g1=failed`，原因 `integration_regression`；G1 passed 前 0 次 G2 許可（開 batch 由 r13 驗證）[r15] | G08 |
| g7 | N/A 正向：(a) 純文件 diff；(b) [r12] YAML 設定檔與測試檔只改註解；兩者都有獨立 Reviewer eligibility（model、權限都相符），判定無行為變更 | 兩者 G1 passed；G2／G3 仍然 pending；不因檔案類型被排除 | G09 |
| g8 | N/A 負例：自我宣告、pending、被拒絕、model 不符；[r12] 改 config 值、改測試斷言、migration，由 Reviewer 判定有行為變更 | G1 不通過，並列出原因 | G10、S1-R15 |
| g9 | `evidence red` 帶任意 argv | 被拒；marker 檔不存在（證明沒執行） | S1-R01、R13 |
| g10 [r12] | 改變行為的修正 attempt（`pre_review_g1` 與 G2 修正 batch 各一）：(a) Red 綁定 task／attempt、finding ID、batch ID，符合三項資格；(b) 只有 Green，沒有 Red；(c) Red 列的是其他 finding 或其他 batch；(d) batch 有兩個改變行為的 finding，Red 只列其中一個；(e) 修正只改文件，走 N/A 並被接受 | (a) 有效；(b) G1 不通過並 Blocked（`original_red_unavailable`）；(c) 無效；(d) G1 不通過，列出缺 Red 的 finding；(e) G1 passed，不要求 Red | G06、G07、G04 |
| g11 [r12] | 被放棄的 attempt：task 的 A1 捕捉 Red 後被停止，A2 從頭重做：(a) A2 有自己的原始 Red，在 H lineage；(b) 只有 A1 的 Red（A1 不是 H 的祖先），行為已在 H；另外 replay 成功 | (a) 有效；A1 的 Red 不轉移；(b) G1 不通過並 Blocked（`original_red_unavailable`），replay 不能替代 | G06、G07 |
| g12 [r12] | 歷史被外部改寫：新觀察到的 H 不是先前記錄 head 的後代（rebase＋force-push） | 所有依 lineage 的 Red 資格失效；G1 Blocked（`history_rewritten`）；不補造證據；0 次自動 rebase 或 push | G06、G17 |
| g13 [r13] | 整合 attempt 的核對，以真 git 依序執行：<br>1. 建 base B0，在其上建 feature head H；task 的 Red 綁定 H 上的 attempt。finding F-I（`source=base_integration`）的 scope 是路徑 A 與其測試。<br>2. 在 base 上做 B1：改 A（與 H 衝突），並改無關的路徑 P。<br>3. 整合 assignment 釘住 H 與 B1。<br>4. 產生 merge commit M（parents [H, B1]），再以 `merge-tree --write-tree H B1` 分類 M 的每個路徑。<br>變體：<br>(a) 沒有衝突的乾淨 merge，只有匯入；<br>(b) P 原樣匯入，A 的衝突解法改變行為，並有綁定 F-I 與 batch 的原始 Red；<br>(c) 同 (b)，但另外改了 P（範圍外的作者編輯藏在匯入裡）；<br>(d) 同 (b)，但沒有 Red；<br>(e) M 的第二個 parent 不是 B1，或 M 只有一個 parent（squash）；<br>(f) 解法需要改 scope 外的路徑 | (a) P 分類為匯入，不要求上游 Red 或 N/A；H 仍是祖先，原 task Red 有效；在新 H 重跑 Green。(b) 可執行：P 是匯入、A 是作者解法且在 scope 內，Red 有效。(c) P 被分類為作者額外編輯 → 拒收。(d) G1 不通過並 Blocked（`original_red_unavailable`）。(e) 拒收。(f) Blocked，回 D11。所有變體之後新 H 都仍需完整的 G2／G3 | G06、G08、G17、O07 |
| g14 [r15] | Green 的執行位置：Implementer worktree 有一個未追蹤檔案，會讓 Green 在該 worktree 通過（或失敗），但 H 本身相反 | Green 依 H 的乾淨 checkout 判定，不受該檔影響；紀錄中的 checkout `HEAD` 等於 H；結束後臨時 checkout 已移除 | G08、G06 |
| g15 [r16] | 證據命令的執行界線（測試用的 `workflow.yaml` 把 `evidence_call_s` 設為 1 秒，fake suite 會睡 5 秒）：(a) `evidence green` 逾時；(b) 剩餘 active 預算比 `evidence_call_s` 短；(c) 臨時 checkout 移除失敗 | (a) 整個 process group 被終止；`activities` 有這段開始與結束時間；G1 不通過（`evidence_timeout`），feature Blocked，0 次派新 worker、0 次自動重跑；臨時 checkout 已移除。(b) 時限等於 `budget.remaining`（狀態以 store API 建立、已用掉大部分 active 的 fixture），到限後結果為 `evidence_timeout`，已用時間記入 `activities`（`next` 的到期路由由 T7.1 的 b7 驗證）[r17]。(c) 判定照常記錄，路徑列入 blockers | D17、G07、G08 |

### M-GH：`tests/test_github.py`（T6.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| h1 | 政策來源矩陣：rules 可讀；403＋`yschiang/loop-engineering`＋已核准且綁定 `workflow.yaml` digest 的政策；403＋沒有政策；403＋政策未核准；403＋digest 不符；403＋其他 repo；[r12] 政策有效但 H 上的 `.github/workflows/loopctl-ci.yml` digest 與政策檔記錄不符 | 依序為：採用規則；採用政策並標 `github_rules_verified=false`；其餘 → unknown＋Blocked，0 個修正輪 | G13、S1-R14 |
| h2 | 必要 check 的狀態：missing、pending、cancelled、timed_out、failure、unknown、stale、skipped、neutral，以及空的必要集合；[r12] job 因 M-TPOL 政策（例如 Linux 專屬案例在 Linux skip）而失敗 | 全部不通過並附原因；第一片的政策沒有例外 | G13 |
| h3 | 通用例外機制：skipped＋核准的 decision；failure＋例外；例外沒有 decision | 第一種可以接受（只在允許例外的政策下）；後兩種 → `policy_invalid`，Blocked | G13、S1-R17 |
| h4 | 舊 attempt success，新 attempt pending；新 attempt 為 queued 且 `started_at=null`；同名但其他 app；同 app 同名但來自其他 workflow；缺少 `run_number` 或 `run_attempt`；同一個 workflow 出現兩個相同的 `run_number`；必要 check 只有 commit status；共 3 頁、最新的在第 3 頁 | 每個 run 依 `run_attempt` 採最新 → pending（queued 也算最新）。其他 app 或 workflow 不計入。識別或順序缺失、有歧義 → unknown，不回退到舊 success；只有 commit status → unknown；會讀完所有分頁 | G14 |
| h4a [r12] | 原 review 情境：同一 H 有 PR run #41 的 `unit-macos` failure，與 event=`push` 的 run #42 success | #42 → `unexpected_event_context`，unknown；G3 不通過 | G14 |
| h4b [r12] | 同一 H、同一 PR：run #41 failure，reopen 後 run #42 success；之後 #41 被重跑，attempt 2 分別為 pending、failure、success | pending → G3 pending；failure → 不通過；success → 通過（兩個 run 的最新 attempt 都是 success） | G14 |
| h4c [r12] | 同一 H、同一 PR：#41 failure、#42 success，沒有重跑 | 不通過（不以較大的 run_number 隱藏失敗） | G14 |
| h4d [r12] | 單一 run：attempt 1 failure、attempt 2 success；另有舊 head H0 的 run failure | success；較早的 attempt 與舊 head 的 run 不再要求 | G14 |
| h4e [r12] | event=`pull_request`、`head_sha=H`，但關聯的是另一個 PR number | unknown（`unexpected_event_context`） | G14 |
| h5 | 必要 check 以整合 SHA M 執行（M≠H）；check-run 的 `head_sha==H` 但 tested SHA 產物是 M | unknown（`unsupported_integration_source`）；不能 Pass | G15（負例） |
| h6 | 觀察的 seq 亂序：同 purpose 較舊者晚到；跨 purpose 時 `pass`（seq 10，H1）比 `pr`（seq 11，H2）晚到 | head 維持最新；舊觀察只存歷史 | G16 |
| h7 | head 不變時的版本變更矩陣：base、spec、AC、design、plan、skill、policy、controller 版本；另加 PR 被改 base branch | 依 design §8 的表：G1、G2、G3 的處理與批准要求逐格斷言；等待批准期間 0 次派工。base 改變且沒有整合觸發：在 H 本身重跑 Green 並綁定新 base，不以暫時合併的 snapshot 當作 H 的 Green（D51-R02）；G3 沿用 H 的結果時記錄適用理由。PR 被改 base → Blocked，不自動改綁 | G17、D15 |
| h8 | 讀取失敗預算：同一個 `ci:<H>` 連續失敗 3 次，之後換新的 seq、新的 session、restart；[r15] 3 頁中第 2 頁失敗 | 第 3 次失敗後 Blocked；之後 0 次自動 fetch；計數不因 seq／session／restart 重置；`resolve_read` 只給一次新的 3 次額度；頁面失敗 → 整次算一次失敗，不採用第 1 頁的部分結果 | D16、G14 |
| h9 | pending→pending→success（每次都成功取得） | 失敗計數維持 0；依輪詢間隔再觀察 | G13、D16 |
| h10 | PR 正向路徑：G1 passed → `push` → `pr_ensure` → 記錄 PR identity。[r15] 負例：G1 failed 或 pending 時要求 `push`。[r12] 建立前查詢矩陣：0 個 → 建立一次，body 帶 marker，`origin=created`；1 個且 head repo／branch、head SHA、base repo／branch 全相符 → 沿用，`origin=existing`；1 個同 branch 但 base 不同；1 個 head SHA 不同；2 個。**延遲建立的反例**（D51-R01）：建立結果 unknown，讀回查無，之後 fake GitHub 才出現這個 PR。[r12] unknown 後讀回：marker＋身份相符；有 marker 但 base 不符；身份相符但沒有 marker；`resolve_operation --bind` 綁定無 marker 的相符 PR | 預期身份與 marker 在外部呼叫前已持久化；相符 → identity 已保存，正式 review 只在此之後派出；base 或 SHA 不符、2 個 → Blocked，建立請求 0 次；延遲建立 → unknown＋Blocked，建立請求共 1 次；marker＋身份相符 → succeeded；其餘兩種讀回 → Blocked；`--bind` → succeeded，`origin=existing`；G1 未通過 → 拒絕，0 次 push、0 次 PR 呼叫 | G01、A04、D12、D13 |
| h11 [r12] | `write push`：檢查 argv；遠端拒絕 non-fast-forward；push 結果 unknown 後讀回遠端 ref 等於該 SHA；同一 SHA 的 fast-forward 重送；[r15] unknown 後讀回遠端 ref 是另一個 SHA | argv 從不含 force 選項；non-FF → failed＋Blocked，0 次 rebase 或 force；讀回相符 → succeeded；重送同 SHA 在重試上限內允許；遠端是另一個 SHA → Blocked，0 次重送；[r16] 目標 repo／ref 沒有 H，但另一個 ref（或 fork）有 H → 不記為 succeeded，維持 unknown 並 Blocked，0 次重送 | D13、G17 |
| h12 [r12] | 每個 job 的 tested SHA 產物：每個必要 job 各有 `tested-sha-<job>-<run_attempt>` 且相符；缺一個 job 的產物；產物的 run_id、run_attempt、job 或 check 名稱不符；產物 SHA≠H；重跑後只有舊 attempt 的產物 | 只有第一種計入；其餘 → unknown，不能 pass | G13、G14 |
| h13 [r12] | 整合 base 的觸發：base 移動且 `mergeable=true`、沒有 finding；`mergeable=false`；`mergeable=null` 後轉為 true；`mergeable=null` 直到 timeout；Reviewer finding 判定不相容；人工 `revise` 註明整合 | 第一種 → 不整合，只重新綁定（h7）；`false`、finding、人工 → 狀態記 `integration_required` 並附觸發來源（batch 由 r12 驗證）；null→true → 等待後不整合；null 期間 G3 維持 pending（逾時判定由 T7.1 的 b4 驗證）[r16]。[r13；r15 修訂] 同一組（base、B、H）重複觀察到 `mergeable=false` → 同一個觸發鍵，不產生第二個 `integration_required`（finding ID 的去重由 r12(d) 驗證）；PR 有衝突而 H 沒有候選 CI run → G3 為 unknown（`ci_unavailable_conflict`），不是 pending 也不是 success | G17、G13 |

### M-REV：`tests/test_review.py`（T5.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| r1 | G2 verdict 矩陣：完整範圍＋目前版本＋`clean`；`changes_required`；`blocked`；缺 verdict；只審部分 diff；舊版本；非獨立的 session；model 不符；capability unverified | 只有第一種 passed，[r15] 而且 registry 沒有新增任何 finding（不虛構 blocker）；`changes_required` → failed；`blocked` → G2 unknown，[r12] **feature Blocked**，0 個新輪、0 次派修；其餘都 unknown 或不通過 | G03、G11、G12、G20 |
| r2 | Reviewer 給 `spec_ac` 的 AC 缺陷，和 `preference` 的命名建議 | 前者 blocking，後者 nonblocking；兩者都有 ID 與依據 | F01 |
| r3 | 同一問題移了行（有 `matches`）；同一行但不同問題（沒有 `matches`） | 前者沿用同一 ID；後者新 ID；不做自動合併 | F02 |
| r4 | 關閉矩陣：Implementer 自稱已修；GitHub thread resolved；目前版本的 Reviewer 覆核＋證據；人工 `resolve_finding` 指定版本；人工指定舊版本。[r16] 經公開的 `result import`：re-review 對 F-1 `verified_fixed`、對 F-2 `still_open`；漏掉 F-3 的 disposition；F-4 的 disposition 綁定舊 head；verdict `clean` 但沒有任何 disposition | 只有第 3、4 種能關閉，並記錄 actor、版本、證據；F-1 關閉，F-2 維持 blocking；漏掉 F-3 → F-3 不關閉、result 不完整、G2 不 passed 並列出 F-3；F-4 不關閉；只有 `clean` → 0 個 finding 被關閉 | F03、F04 |
| r5 | CI 先失敗，review 尚未完成 | 0 個 batch，直到 review 完成；文件缺陷可以列為修正項 | F05 |
| r6 | batch 含 F-1、F-2，回應只含 F-1；[r16] 經公開的 `result import`，另有：F-1 的 `fix_submitted` 沒有綁定 F-1／batch 的 Red 引用；回應含 batch 外的 F-9 | 拒收並列出 missing `[F-2]`；F-1 與 F-2 都不解除；缺 Red 引用 → 依 §7 G1 不通過；batch 外的 ID → 拒收 | F06 |
| r7 | 已用 3 輪；換 session 後嘗試第 4 輪 | 0 次派工；Blocked | F07 |
| r8 | 爭議（經公開的 `result import` 提交 `disputed` 回應，覆核以 `dispute_accepted`／`dispute_upheld` disposition 回覆）[r16]：接受；維持；restart 後重送同一反證；反證伴隨新 head | 接受 → 依覆核關閉，輪數不變；維持 → Blocked；重送 → 0 次第二次覆核；新 head → 先 G1，再做新的 review 與 CI | F08、F09、F10 |
| r9 | `failed_rechecks=2`；已 resolved 的 finding 被 `matches` 再現 | 下一次派修前 Blocked；reopen 並保留歷史 | F15、F16、S1-R16 |
| r10 | 派修的 assignment；[r17] 另外兩種：re-review 的 assignment、爭議覆核的 assignment；[r15] 派出後修改 registry 中該 finding 的分類與依據；[r16] 並加入一筆新的修正證據 | 三種 assignment 都帶有完整的 finding 快照、finding IDs、先前 review 的 result ID 與版本、先前修正的 commits 與證據引用（派修另帶 batch ID，爭議覆核另帶反證回應）；修改後各 assignment 內的快照（含這些引用）與其 digest 都不變 | S1-R12、F08 |
| r11 [r12] | finding → fix → re-review：`correctness_security` finding F-3 → 派修 batch B2 → (a) fix attempt 回傳綁定 F-3／B2 的原始 Red 與 H 上的 Green；(b) 只有 Green | (a) G1 passed → 以新 H 派 re-review；(b) G1 不通過並 Blocked，0 次 re-review，F-3 不解除 | G06、F04、A02、A13 |
| r12 [r13] | 整合路徑選擇，依序執行：<br>(a) **一般收齊**：H 的 G1 已通過，review 已派出、仍在進行，CI run 仍在進行，之後出現 `integration_required` → 收齊 review 與 CI 後開一個 batch，含整合 finding 與 review finding；<br>(b) **不等待**：H 的 G1 尚未通過（或 review 尚未派出），PR 有衝突，H 沒有 CI run → 立即開 `pre_review_g1` batch（原因 `base_integration`）；<br>(c) 同 (b)，但 Implementer 的前一個 attempt 仍 active，或狀態 unknown；<br>(d) 重複的 `mergeable=false` 觀察與重複的人工 `revise`，對同一組（base、B、H）；<br>(e) 整合後產生新 H；<br>(f) 已用 3 輪時再出現整合需求 | (a) 一個 batch，派修時計一輪。(b) 0 次為 H 派 G2、0 次等待 CI；G3 在 H 記 unknown，不算 success；一個 batch，計一輪；assignment 釘住 H 與 B，授權匯入與作者編輯範圍；0 次 GitHub PR merge 呼叫，外部寫入沒有 merge。(c) 確認 writer 已結束前 0 次派修；unknown → 依 D47 停止或 Blocked。(d) 同一個 finding ID，只有一個未結 batch。(e) H 上舊的 G2／G3 結果標為 obsolete、已收到的 findings 保留；新 H 需要完整的 G1、G2、G3 才能 Pass。(f) Blocked，0 次派工 | G17、F05、F07、O10、G01 |
| r12b [r14] | 路徑優先序混合矩陣：<br>(a) 適用 G1 passed、review 在途、PR 衝突且沒有 CI run；<br>(b) 適用 G1 passed、review 有終態結果、CI 真正在途；<br>(c) 適用 G1 passed、review／CI 都有同版本終態結果；<br>(d) 同 (a)，但 active-time 或三輪修正上限已用盡；<br>(e) 同 (b)，但 CI 後來變得過時／確定不可用；<br>(f) 同 (c)，但 G2 verdict 為 blocked 或 G3 policy unknown | (a) 前置整合優先，0 次等待不存在的 CI；不新增 G2；writer 安全核對後只派一個 pre_review_g1 batch，整合後重新取得三 gates。(b) 只等 CI，0 次提前派修。(c) 不等待，合併為一個 batch。(d) Blocked，0 次派工，預算不重置。(e) 重新走優先路徑，不把舊結果當成功。(f) 保留獨立 blocker，不派修也不 Pass | G17、F05、F07、D17 |
| r13 [r15] | 正式 review 前 G1 失敗：(a) `integration_regression`；(b) `original_red_unavailable`；(c) 已用 3 輪時的 (a) | (a) 開一個 `pre_review_g1` batch，派修時計一輪，G1 passed 前 0 次 G2；(b) Blocked，不開 batch；(c) Blocked，0 次派工 | G08、F07、G07 |
| r14 [r16] | `budget_extension rounds:+1`：(a) 已用 3 輪後核准一次 → 可派第 4 個 batch；(b) 同一筆 decision replay 或 restart 後；(c) 延長後 Implementer 前一個 attempt 仍 unknown | (a) 恰好多一輪；(b) 不會再多出第 5 輪；(c) 仍 Blocked，延長不解除 writer 條件；其他計數不變 | F07、D17 |

### M-PASS：`tests/test_publish_pass.py`（T6.2）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| p1 | 三 gates 都 passed，且在同一版本；[r12] 兩個變體：G3 政策來源為 rules；為 403＋已核准的 `workflow.yaml` | 先 `publish_pr`，再 `publish_issue`，之後做 `pass` 觀察 → Pass。Pass package 含 version_key、PR identity（含 origin）、head、base、三 gates 的理由與 result ID／digest、findings（未解 blocking 為空，列出未解 nonblocking 與已關閉項的 closure 引用）、政策來源、`github_rules_verified`（前者 true、後者 false）、限制、發布狀態與 receipts、pass 觀察 seq、acceptance=pending，且 `status --human` 可讀；package 由狀態投影，改一筆被引用的紀錄 → 重新投影，舊 package 不能放行 | G01、G13 |
| p2 | review clean＋CI failure；CI green＋`changes_required` | 兩種都沒有 Pass；兩個 gate 的結果分別保存；第一種開修正 batch | G02 |
| p3 | Pass 前的 `pass` 觀察看到新 head；Pass 之後有 push | 前者放棄這次 Pass；後者讓 Pass 失效，保留舊紀錄 | G18 |
| p4 | 讀回 PR review 與 issue 摘要的內容；[r15] 讀回的 body digest 或 marker 被改過 | PR review 含 verdict、finding 表（ID、分類、blocking、位置、依據、預期）、result ID、head、base、spec digest；issue 含待辦、blocking 的 ID、PR review 連結；兩者的 body digest 與 marker 都相符；被改過 → 不算已發布，Blocked，不能 Pass | F13 |
| p5 | 發布結果 unknown；GitHub 已接受但回應遺失 | 依 marker 查回原 URL；共 1 則留言；review 不重做 | D12、F14 |
| p6 | 在 Pass 狀態下列出所有 write；[r15] 執行 `write merge`、`write close`、`write release`、`write deploy` | 沒有 merge、close、release、deploy；acceptance 為 pending；四個命令都 exit 2 或 `unsupported`，fake `gh`／`herdr` 0 次呼叫 | O10 |
| p7 [r15] | Pass 前的確認觀察：`observe pr --purpose pass` 與 `observe ci --purpose pass` 的 seq 晚於三 gates 判定；變體：確認時某個必要 check 已被重跑而變成 pending | 一致 → Pass；check 改變 → 放棄這次 Pass，G3 依新觀察重評 | G18、G01 |
| d7b [r15] | 人工退回與版本：pending 時 `return`（ac_defect）；在 V1 `accept` 後 head 變成 V2；`accept` 指向舊的 version_key | 退回 → `source=human_acceptance` 的 finding、預算相同、Pass 失效；V2 的 acceptance 為 pending，V1 歷史保留；指向舊版本 → 拒絕 | O11、F11 |

### M-RESUME：`tests/test_resume.py`（T6.2）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| u1 | worker 已完成、結果檔已存在但通知遺失、review 已保存、`publish_pr` 已成功、`publish_issue` pending → 協調者 restart，執行 `next` | 只有「匯入結果（一次）」和「`publish_issue`」兩個動作；0 次派工、0 次 review；預算與 findings 不變 | D07、D14、F14 |
| u2 | resume 時觀察到 head、base 或 spec 已改變 | 依 h7 的規則失效；acceptance 不沿用；不重新初始化 | D15 |

### M-BUD：`tests/test_budget.py`（T7.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| b0 [r17] | `tests/test_active_time.py`（T2.3），以 store API 建立 `activities` fixture：兩段重疊的活動；一段尚未結束的活動；沒有活動的 Blocked 期間；已用 3h50m 時的 `remaining` | 重疊只算一次；未結束的活動計到 `now`；沒有活動的期間不計；`remaining` 等於 10 分鐘 | D17 |
| b1 | 時間區間重疊；到期的 stop 加上一個無關的 blocker；已 prepared 的 stop；stop 讀回用盡；離線超時；換 session；[r15] Blocked 且沒有未結束活動的 2 小時 | 重疊只算一次；stop 優先；同一個 op 只送一次；用盡 → 等人；離線 → 計入並 Blocked；換 session 不重置；沒有活動的 Blocked 期間不計時；[r16] `activities` 中的證據命令區間與 worker 區間重疊時只算一次，單獨存在時計入 | D17、S1-R09 |
| b2 [r15] | worker attempt 超過 45 分鐘：(a) stop 經 process-info 確認；(b) 確認後派新 attempt，再逾時兩次；(c) stop 讀回 3 次都無法確認；(d) `budget_extension attempts:<unit>:+1` 後 | (a) attempt 記為 `timed_out`，允許同一單位的新 attempt，不計修正輪；(b) 第 3 次逾時 → Blocked（`attempt_timeout_exhausted`），0 次再派；(c) Blocked，0 次新 attempt，worker 維持 unknown；(d) 只多一次 attempt，其他計數不變 | D04、D16、D17 |
| b3 [r15] | review attempt 超過 30 分鐘，路徑同 b2 | 逾時期間 G2 維持 pending（不是 failed）；用盡 → G2 unknown 並 Blocked；0 個修正輪 | D17、G03 |
| b4 [r15] | CI 等待：push 讀回 succeeded 後第一次 `observe ci` 起 30 分鐘仍有必要 check 為 queued；`mergeable=null` 到 30 分鐘；`budget_extension ci_wait:<H>` 後 check 轉為 success | 前兩者 → G3 unknown（`ci_timeout`）並 Blocked，0 次 rerun、0 個修正輪；延長後只多一個 30 分鐘視窗，check success → G3 依規則判定 | D17、G13 |
| b5 [r16] | `budget_extension active:60`：(a) 4h 到期後核准 → 可再派工，直到 5h；(b) 同一筆 decision replay 或 restart；(c) 延長後 stop 仍未確認或 writer unknown | (a) 上限變為 5h，其他計數不變；(b) 上限仍為 5h；(c) 仍 Blocked，0 次派工 | D17 |
| b6 [r16] | `attempts:<unit>:+1` 與 `ci_wait:<H>`：同一筆 decision replay 或 restart；指向其他 unit 或其他 H | 各只生效一次；指向其他目標的不影響本目標；都不解除 writer 或 stop 的 blockers | D17、D16 |
| b7 [r17] | 證據命令因剩餘 active 預算用完而到限（g15(b) 的狀態）之後執行 `next` 與 `safety` | 先給到期 stop 或 `human`；0 次派新 worker；已用時間不被清除 | D17、D16 |

### M-PRE：`tests/test_preflight.py`（T1.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| f1 | 已選的 reviewer profile 缺少 model 設定 | `unverified` → Blocked | D19 |
| f2 | 已選的兩個 profile 都 verified；未選的 Orca、Codex CLI 不在 PATH 或登入失敗 | preflight 仍 verified；未選項不被呼叫或使用 | D23 |
| f3 | profile 要求的 model 與 native 讀回的 model 不符 | `unverified` | D18 |
| f4 [r15] | `workflow.yaml` 中 `reviewer` 與 `implementer` 的 model 相同（例如兩者都是 `claude-opus-5-5`，只有 effort 不同） | `unverified`，原因列出兩者相同 | G11、D19 |
| f5 [r15；r16 參數化] | fake probe 對五個負例（寫出範圍、`git push`、`gh`、`herdr`、`loopctl decide`）逐一參數化：(a) 全部被拒且資源未變、stop 經確認；(b) 只有該負例沒有被拒；(c) 該負例被拒但資源改變（檔案出現、遠端 ref 改變、`gh`／`herdr` 呼叫紀錄新增、狀態 revision 改變）；(d) stop 後 process-info 仍顯示 agent；(e) native 紀錄沒有 effort | (a) `verified`；(b)、(c) 對每一個負例各自 `unverified` 並列出該負例；(d) `unverified`；(e) `verified` 且 `effort_verified=false`；receipt 含每個負例的命令、拒絕與資源檢查 | G12、D18、D19 |
| f6 [r16] | 位置核對：(a) native 工作目錄、repo、branch 都等於要求；(b) native 工作目錄是另一個 worktree；(c) branch 不符；(d) 只有 input accepted、沒有 native turn；(e) native 紀錄沒有工作目錄，只有 shell cwd 相符 | (a) 該項通過；(b)–(e) 各自 `unverified`，receipt 列出要求與實際值；不以 shell cwd 推定 | D18、G19、D19 |

## 3. 共用 workflow 樣本與 rubric（17 條 workflow AC）

- 樣本放在 `docs/validation/s1/workflow-samples/`，由 T4.3 建立。
- 每一組樣本都要有一個正例與一個負例。
- 審查流程（D51-R06）：由樣本 owner 準備，經授權的獨立 Reviewer 依 rubric 審查，並把每組的結果記錄在 `docs/validation/s1/proof.md`。
- 不需要逐樣本的使用者簽核。只有真正未決的業務或政策選擇，才帶到既有的人工決策點（D11、acceptance）。
- 「模板存在」不算通過。

| 樣本 | AC | 正例（必須成立） | 負例（必須被指出並拒絕） | Owner |
| --- | --- | --- | --- | --- |
| W-A Project→feature | O20、O21、O24、O28 | Project 分析能追溯研究、SA、milestones、features；feature 分析引用 baseline，補出差異、未知與 AC；功能驗收與業務成果分開 | 只有 task 清單而沒有分析；feature 重寫整個 project；用測試綠燈聲稱業務成果 | Project Lead |
| W-B 阻擋與衝突 | O04、O25、O27 | 衝突列出來源、版本與影響，交人裁決；未決問題仍在時標 not-ready | 模板填滿就宣告 ready；依檔案時間選出勝方 | Project Lead |
| W-C Plan 與批准 | O01、O22、O26、O23、F12 | 使用者可以直接交付給 Implementer；Project Lead 的草案經校準後只有一份 plan；SA 確認與 D11 分開記錄；跨 feature 影響與新需求回人裁決；第一片 scope 變更讓整個 run 停下等批准 | 以草案 plan 派工；以 SA 確認代替 D11；把範圍外需求混入 fix；宣稱第一片已支援只停受影響工作 | Implementer＋使用者 |
| W-D 相依交接 | O12、O13 | 上游 accepted、實際 merged、baseline 已登記，而且下游有自己的 D11，才開始下游 | 上游 accepted 但未 merge 就派下游；baseline 不含上游成果 | orchestrate skill＋人 |
| W-E Skill 交接 | O16、O17、O19 | skill 的結果只經 `result import` 生效；其他 repo 的規則標為待澄清，附來源；runtime 父子關係不給權限 | skill 自行宣告 Pass；未標來源就把他 repo 的規則當本 repo 政策 | orchestrate skill |
| W-F 歷史限制 | O15 | handoff 記錄 P03／Q-TARGET 為暫停狀態；`proof.md` 附 `rg -n "P03\|Q-TARGET" src/` 的輸出為空；沒有 `init` 不接管的行為由 s7 驗證 | 在產品程式寫 P03 特判（Reviewer 對注入特判的樣本必須指出）；沒有明確 `init` 卻接管工作 | 協作者 |

## 4. 證據規則 rubric

- **G19、D22**：驗收報告 `docs/validation/s1/proof.md` 對每項能力，分欄列出 `fake`、`profile-probe`、`real-E2E` 三類證據，並依接法（Herdr＋Claude Code、Herdr＋OpenCode）分開。
  - 未執行的格子標 `none`；
  - 不同接法之間不共用 passed 標記。
- **G20**：R3 沒有出現真實 finding → 示範維持 open，不製造 blocker。
  - [r16] rubric 負例（由 T4.3 的 Reviewer 一併審查）：一份 `proof.md` 樣本在 R3 沒有 finding 或以 Blocked 結束，卻標示「finding → fix → re-review 已完成」→ 必須被指出並拒絕。

## 5. 真實證據與界線

| ID | 內容 | 前置 | 通過標準 | 證據 |
| --- | --- | --- | --- | --- |
| R1 | 已選的兩個 profile 的 preflight（受限的能力 probe） | M-PRE | model 與 marker 讀回一致；每個負例（寫出範圍、`git push`、`gh`、`herdr`、`loopctl decide`）都觀察到被拒**且**資源未變；stop 經 process-info 確認；receipt 依 design §6 | `docs/validation/s1/preflight/` |
| R2 | 在 `probe/s1-g1` 上用 fixture 跑到 G1；不是交付 feature，也不 merge | R1、M-G1、M-OBS、M-GH（h8）、M-BUD | fixture 的 G1 passed，且實際軌跡（assignment → worker Red → Green → G1）與 `probe/fixture/` 的預期一致；附證據的 Blocked 另外記錄，R2 維持 open。只算能力證據 | `docs/validation/s1/probe/` |
| R3 | 第一個有用的交付：一個 B1 尚未實作、由 D11 選定的新行為（D51-R04），走真實 finding → fix → re-review，中間中斷一次 | B1 accepted＋merged＋baseline（T8.0）；feature 已經過 D11 選定 | 三 gates 在目前版本都通過；改變行為的修正有綁定 finding 與 batch 的原始 Red（r11 規則）；中斷後成功接續。Blocked 或沒有 finding → 維持 open | PR、issue、CI URL、狀態 export |

- **R1 不涵蓋 D24**：第一片的 profile 組合是 Claude Code＋OpenCode，不是兩個角色都在 OpenCode。

## 6. D49 CI 與政策檔提案（待 D11 核准）[r15 具體化；r16 改為兩個都跑測試的 job]

以下是提案的**完整內容**，T1.1 依此建立；D11 核准後以 `policy_change` 綁定 `workflow.yaml` 的 digest 才生效。第一片的 G3 與 Pass package 顯示 `github_rules_verified=false`（`yschiang/loop-engineering` 為 private repo，rules API 回 403，D49）。這份核准也用於 B1。

### 6.1 GitHub workflow：`.github/workflows/loopctl-ci.yml`

- 名稱 `loopctl-ci`，app `github-actions`。
- **觸發**：只有 `pull_request`（types：`opened`、`synchronize`、`reopened`；`branches: [main]`）。不以 push 觸發，不設 `concurrency`（避免自動取消產生 cancelled 結果）。
- `permissions: contents: read`。第三方 actions 固定到完整 commit SHA，T1.1 記錄所用版本。
- 兩個 job，check 名稱等於 job 名稱。每個必要 job 都執行同一個測試命令，所以 §0 的收集／skip／失敗政策適用每個必要 job（GAT-06）[r16]：

| Job／check | runner | `timeout-minutes` | 命令（依序） |
| --- | --- | --- | --- |
| `unit-linux` | `ubuntu-24.04` | 15 | 共同前置；`uv run pytest`（`LOOPCTL_EXPECT_PLATFORM=linux`）；`uv run ruff check .`；`uv run mypy src`；`scripts/dist-smoke.sh`（`uv build` → 在全新 venv 安裝 wheel → 在 checkout 外執行 `loopctl --help` 與 `python -c "import loopctl.tools"`，並確認 `import delivery` 失敗） |
| `unit-macos` | `macos-15` | 15 | 共同前置；`uv run pytest`（`LOOPCTL_EXPECT_PLATFORM=darwin`） |

- revision-15 另列的 `static` job 不跑測試套件，與「每個必要 job 同一政策」不一致；revision-16 把 ruff、mypy、dist-smoke 併入 `unit-linux`，不另設 job [r16]。
- workflow 的結構由 t7 檢查；真正的執行結果以 B1 的 G3 實跑為證據。

- **共同前置**（每個 job 開頭）：
  1. checkout `github.event.pull_request.head.sha`；
  2. `git rev-parse HEAD` 不等於該 SHA → job 失敗；
  3. 寫出 `tested-sha.json`：`run_id`、`run_attempt`、`job`、`check_name`、`tested_sha`，上傳為 artifact `tested-sha-<job>-<run_attempt>`（在測試之前上傳，所以測試失敗時也有紀錄）；
  4. 安裝 uv 與 Python 3.12，`uv sync --frozen`。
- runner label 在 T1.1 以當時的 GitHub 文件核對；label 不可用 → 回報，不自行替換。
- G3 只計入 event、PR、`head_sha==H` 都相符，且產物內容逐欄相符的 check（design §8；h4、h12）。
- 保守規則：只重跑失敗的 job 時，其他 job 可能沒有同一 attempt 的產物，需要改為重跑全部 jobs。這不新增任何 controller 的 rerun 功能。

### 6.2 loopctl 政策檔：repo 根目錄 `workflow.yaml`

不是 GitHub workflow。提案全文（`<…>` 由 T1.1 在建立時填入實際值）：

```yaml
schema_version: 1
repo: yschiang/loop-engineering
g3:
  source: head
  trigger_event: pull_request
  base_branch: main
  workflow: .github/workflows/loopctl-ci.yml
  workflow_blob_sha: <git hash-object of the workflow file>
  required_checks:
    - {name: unit-linux, app: github-actions}
    - {name: unit-macos, app: github-actions}
  exceptions: []
evidence:
  commands:
    suite: {argv: [uv, run, pytest, "--junitxml={junit_out}"]}   # Red 與 Green 共用；{junit_out} 由 loopctl 填入，worker 不能提供參數
budget: {active_hours: 4, correction_rounds: 3, infra_extra_retries: 2}   # D13，已確認
timeouts: {worker_attempt_min: 45, review_attempt_min: 30, ci_wait_min: 30, extra_attempts_per_unit: 2}
limits:
  read_call_s: 30
  write_call_s: 60
  push_call_s: 120
  pr_ensure_call_s: 120
  evidence_call_s: 900
  poll_worker_s: 30
  poll_github_s: 60
  readback_max: 3
  stop_readback_interval_s: 10
  read_failures_max: 3
profiles:
  implementer: {transport: herdr, runtime: claude-code, provider: anthropic, model: claude-opus-5-5, effort: high, settings: profiles/implementer.claude-settings.json}
  reviewer: {transport: herdr, runtime: opencode, provider: openai, model: gpt-6-astra, effort: xhigh, settings: profiles/reviewer.opencode.json}
```

- 除了 `budget` 沿用 D13，其餘數值都是本版提案，D11 核准前不生效。
- 之後任何改動都需要新的 `policy_change`；H 上的 workflow 檔 blob 與 `workflow_blob_sha` 不符 → G3 unknown＋Blocked（h1）。

### 6.3 不含 macOS 的替代集合

若 D11 認為 private repo 的 macOS 計費不可接受，可改為 `required_checks` 只列 `unit-linux`，並從 workflow 移除 `unit-macos`。macOS 行為仍由本機 G1（macOS）覆蓋，但沒有乾淨 runner 上的獨立證據；G3 規則不變。
