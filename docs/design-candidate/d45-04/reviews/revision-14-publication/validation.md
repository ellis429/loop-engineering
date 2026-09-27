# Validation：第一個可用切片（候選 design-04；revision-14）

> **作者提交狀態**：revision-13；目前的 review 狀態以 [README](README.md) 為準。
> **全部是 planned，沒有任何測試已執行，也沒有任何 AC 已通過。** 每個 ID 的歸屬以 [coverage.md](coverage.md) 為準。revision-12 新增或修改的案例標 `[r12]`，revision-13 的標 `[r13]`。
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
| ENV-R | Herdr 0.9.1、Claude Code（Opus 5.5 Implementer）、OpenCode（Reviewer，model 待 D11） |
| ENV-GH | `yschiang/loop-engineering` 的 PR／issue／Actions |

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

### M-STATE：`tests/test_state.py`（T2.1）

| 案例 | 輸入／前置 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| s1 | rev 3；在新 revision **提交前**中斷，再 `status` | revision 為 3；未提交的變更不存在；沒有任何 write | D09、D10 |
| s2 | 在 revision 4 **已提交**後中斷，再 `status` | revision 為 4；沒有重複的 transition；history 可讀 | D09、D10 |
| s3 | 缺檔、壞 JSON、`schema_version=9`、手改的 gate、transition ID 衝突，各一次 → `status` 與 `next` | exit 5，或 Blocked 並附原因；原檔的 bytes 不變；預算不被清空；0 次派工、0 次寫入 | D11、D02 |
| s4 | 兩個程序同時 `claim`；兩個程序同時 commit | 恰一方成功；token 明文不在狀態中 | D03、O02 |
| s5 | `status --human` | 可讀到 phase、每個 gate 的狀態與原因、blockers、下一步 | D01 |
| s6 | 文件 digest 欄位指向不存在的物件；證據物件引用缺失 | 前者正常提交（digest 不被當作物件引用）；後者拒絕提交 | S1-R06 |

### M-DEC：`tests/test_decisions.py`（T2.2；d3 在 T2.3 的 `tests/test_public_path.py`）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| d1 | 使用者直接 `init` 並登記 plan，沒有 Project Lead 交接 | 進入 planning；沒有 `approve_plan` 時 0 次派工 | O01、O05 |
| d2 | 批准來源矩陣：沉默、timeout、agent 身分、只有 SA 確認、草案 plan（producer=project_lead）、校準後的 plan＋人工 `approve_plan` | 只有最後一項產生 approval；只有 SA 確認時仍然 0 次派工 | O05、O22、O26 |
| d3 | 批准後透過公開 CLI（T2.3）執行 `next` | 第一個 assignment 帶有 task 的 AC IDs 與驗法；之後的正常 fix 不需要逐 task 再批准 | O06 |
| d4 | implementing 期間送 `scope_change` | 批准失效，整個 run 進入 awaiting_approval（第一片不做部分接續）；不 crash | O07、O23（第一片部分） |
| d5 | 以 runtime 父 session 身分，或 Project Lead 角色標記 `decide approve_plan` | 拒絕；權限只看人工 decision 與 token | O19 |
| d6 | 登記原生路徑的 plan 與 spec，並讀回 | locator、版本與內容可讀回；不改名；task 不另外變成 PR | O03 |
| d7 | 接受與退回矩陣：pending 時 `return`（ac_defect）；在 V1 上 `accept` 後 head 變成 V2；`accept` 指向舊版本 | 退回 → `source=human_acceptance` 的 finding、預算相同、Pass 失效；V2 為 pending，V1 歷史保留；指向舊版本 → 拒絕 | O11、F11 |
| d8 | 呼叫 `adopt` 或 `delegate` 入口 | 回 `unsupported`；狀態不變；沒有繞過任何核對 | O08、O09、O18（僅負例） |
| d9 [r12] | `resolve_read`／`resolve_operation` 由 agent 身分送出；缺原因或目標 ID；人工且完整 | 前兩種拒絕；第三種只寫入 decision 紀錄，0 次外部寫入、0 次 fetch（效果由 o1、w10 驗證） | D13、D16 |

### M-OBS：`tests/test_observe.py`（T2.3）[r12]

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| o1 | `worker:<attempt>` 連續傳輸失敗 3 次，之後換新 seq、新 session、restart；再以 `resolve_read` 恢復，又失敗 3 次 | 第 3 次失敗後 Blocked；之後 0 次自動 fetch；計數不重置；`resolve_read` 只給一次 3 次額度，用完再次 Blocked | D16 |
| o2 | `native:<attempt>` 讀取：同 purpose 較舊 seq 晚到 | 只存歷史，不覆蓋目前事實 | G16、D06 |

### M-WRITE：`tests/test_writes.py`（T2.3）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| w1 | 兩個程序同時 `write prompt` 同一個 op | fake herdr 被呼叫 1 次 | D13 |
| w2 | 送出後 receipt 遺失，查回原 marker | 讀回後轉為 succeeded，沒有重送 | D12、D13 |
| w3 | 延後生效的 worktree、查無的 prompt、client 已結束 | unknown＋Blocked；0 次重送 | D13、S1-R05 |
| w4 | 讀回結果依序為「仍在執行」×3 | 第 4 次讀回被拒；變成 `blocked(readback_exhausted)` | D16 |
| w5 | writer 結束矩陣（經 T2.3 的 `observe worker\|native`）：只有 terminal idle／Herdr `done`；結果已匯入＋native turn 完成；stop 經 process-info 確認；狀態 unknown | 前一項 → 0 次派下一個；中間兩項 → 允許派下一個；unknown → Blocked | D04 |
| w6 | result 的身份、cwd、head、scope 不符，或內含 worker 提供的 argv | 拒收；原件保存；列出差異 | D05 |
| w7 | 同一個 result 重送；同 attempt 但 bytes 不同 | 前者沒有新的 transition；後者雙方都保存並 Blocked | D08 |
| w8 | 沒有結果檔、也沒有通知，native transcript 裡有 marker 之後的結果 JSON（經 T2.3 的 `observe native`） | 工具寫出 result，帶 `producer=tool`、native session／message ID、原文 digest，並匯入一次；無法解析 → unknown | D06 |
| w9 | Claude uuid 與 OpenCode `ses_…` 兩種 handle 的 round-trip；result 的 native ID 不符 | 以 attempt ID 對回；不符 → 拒收；不補造 ID | D21 |
| w10 [r12] | `resolve_operation` 矩陣，對象為 unknown 的 `prompt` op：`--bind` 且新讀取相符；`--bind` 但不符；`--not-delivered` 只附 controller 的查無觀察；`--not-delivered` 附 client 未送達紀錄，之後重試到第 3 次 | 相符 → succeeded（`resolved_by=human`），0 次重送；不符 → 拒絕；只有查無 → 拒絕，仍 unknown；未送達紀錄 → failed(確定未送達)，重試最多額外 2 次，第 3 次重試被拒；decision 本身 0 次外部寫入 | D12、D13、S1-R02 |

### M-G1：`tests/test_g1.py`（T3.1）

finding ID 與 batch ID 在 T3.1 以 attempt metadata 的 fixture 提供；完整派修流程在 r11 驗證。

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| g1 | 原始 Red 有效，head Green 通過，不做 replay | G1 passed | G06 |
| g2 | 證據互相矛盾 → 觸發 replay：成功與失敗各一 | replay 只作診斷：成功 → 繼續，失敗 → Blocked；都不能補造 Red | G06、G07 |
| g3 | 分別污染 raw、exit、task、snapshot、producer | 每一種各自使 G1 失敗，並列出原因 | G04 |
| g3b | 適用資格（D51-R07）。各情境的 raw 與 producer 都有效，而且都另做一次 replay 且成功：<br>(a) snapshot 或 attempt 的 commit 超出核准 scope；<br>(b) **兄弟 snapshot**：與 attempt 有共同的 parent，但沒有對應到該 task／attempt 的捕捉紀錄，它的測試內容也不在 attempt 的 commit 中；<br>(c) attempt 不是 H 的祖先；<br>(d) 正例：尚未 commit 時捕捉的原始 Red，provenance 帶有 task／attempt，而且它的測試 delta 出現在 attempt 的 commit 中，attempt 是 H 的祖先 | (a)、(b)、(c) 各自使 Red 無效，replay 成功也不能補救；(d) 有效，不需要同 SHA，也不需要 replay | G04、G06、G08、S1-R13 |
| g4 | 缺原始 Red；task 集合為空；只有語法錯誤的 Red | G1 fail；缺原始 Red → Blocked（`original_red_unavailable`） | G07、S1-R11 |
| g5 | 證據存在 repo 外；C 之後的文件 commit 產生 head D | tracked 文件只引用 result ID 與 digest；在 D 需要重跑 Green；Red 依 lineage 仍適用；記錄「只有文件差異」的理由 | G05 |
| g6 | 整合 regression 失敗 | 開 `pre_review_g1`（計一輪）；G1 passed 前 0 次 G2 | G08 |
| g7 | N/A 正向：(a) 純文件 diff；(b) [r12] YAML 設定檔與測試檔只改註解；兩者都有獨立 Reviewer eligibility（model、權限都相符），判定無行為變更 | 兩者 G1 passed；G2／G3 仍然 pending；不因檔案類型被排除 | G09 |
| g8 | N/A 負例：自我宣告、pending、被拒絕、model 不符；[r12] 改 config 值、改測試斷言、migration，由 Reviewer 判定有行為變更 | G1 不通過，並列出原因 | G10、S1-R15 |
| g9 | `evidence red` 帶任意 argv | 被拒；marker 檔不存在（證明沒執行） | S1-R01、R13 |
| g10 [r12] | 改變行為的修正 attempt（`pre_review_g1` 與 G2 修正 batch 各一）：(a) Red 綁定 task／attempt、finding ID、batch ID，符合三項資格；(b) 只有 Green，沒有 Red；(c) Red 列的是其他 finding 或其他 batch；(d) batch 有兩個改變行為的 finding，Red 只列其中一個；(e) 修正只改文件，走 N/A 並被接受 | (a) 有效；(b) G1 不通過並 Blocked（`original_red_unavailable`）；(c) 無效；(d) G1 不通過，列出缺 Red 的 finding；(e) G1 passed，不要求 Red | G06、G07、G04 |
| g11 [r12] | 被放棄的 attempt：task 的 A1 捕捉 Red 後被停止，A2 從頭重做：(a) A2 有自己的原始 Red，在 H lineage；(b) 只有 A1 的 Red（A1 不是 H 的祖先），行為已在 H；另外 replay 成功 | (a) 有效；A1 的 Red 不轉移；(b) G1 不通過並 Blocked（`original_red_unavailable`），replay 不能替代 | G06、G07 |
| g12 [r12] | 歷史被外部改寫：新觀察到的 H 不是先前記錄 head 的後代（rebase＋force-push） | 所有依 lineage 的 Red 資格失效；G1 Blocked（`history_rewritten`）；不補造證據；0 次自動 rebase 或 push | G06、G17 |
| g13 [r13] | 整合 attempt 的核對，以真 git 依序執行：<br>1. 建 base B0，在其上建 feature head H；task 的 Red 綁定 H 上的 attempt。finding F-I（`source=base_integration`）的 scope 是路徑 A 與其測試。<br>2. 在 base 上做 B1：改 A（與 H 衝突），並改無關的路徑 P。<br>3. 整合 assignment 釘住 H 與 B1。<br>4. 產生 merge commit M（parents [H, B1]），再以 `merge-tree --write-tree H B1` 分類 M 的每個路徑。<br>變體：<br>(a) 沒有衝突的乾淨 merge，只有匯入；<br>(b) P 原樣匯入，A 的衝突解法改變行為，並有綁定 F-I 與 batch 的原始 Red；<br>(c) 同 (b)，但另外改了 P（範圍外的作者編輯藏在匯入裡）；<br>(d) 同 (b)，但沒有 Red；<br>(e) M 的第二個 parent 不是 B1，或 M 只有一個 parent（squash）；<br>(f) 解法需要改 scope 外的路徑 | (a) P 分類為匯入，不要求上游 Red 或 N/A；H 仍是祖先，原 task Red 有效；在新 H 重跑 Green。(b) 可執行：P 是匯入、A 是作者解法且在 scope 內，Red 有效。(c) P 被分類為作者額外編輯 → 拒收。(d) G1 不通過並 Blocked（`original_red_unavailable`）。(e) 拒收。(f) Blocked，回 D11。所有變體之後新 H 都仍需完整的 G2／G3 | G06、G08、G17、O07 |

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
| h8 | 讀取失敗預算：同一個 `ci:<H>` 連續失敗 3 次，之後換新的 seq、新的 session、restart | 第 3 次失敗後 Blocked；之後 0 次自動 fetch；計數不因 seq／session／restart 重置；`resolve_read` 只給一次新的 3 次額度 | D16 |
| h9 | pending→pending→success（每次都成功取得） | 失敗計數維持 0；依輪詢間隔再觀察 | G13、D16 |
| h10 | PR 正向路徑：G1 passed → `push` → `pr_ensure` → 記錄 PR identity。[r12] 建立前查詢矩陣：0 個 → 建立一次，body 帶 marker，`origin=created`；1 個且 head repo／branch、head SHA、base repo／branch 全相符 → 沿用，`origin=existing`；1 個同 branch 但 base 不同；1 個 head SHA 不同；2 個。**延遲建立的反例**（D51-R01）：建立結果 unknown，讀回查無，之後 fake GitHub 才出現這個 PR。[r12] unknown 後讀回：marker＋身份相符；有 marker 但 base 不符；身份相符但沒有 marker；`resolve_operation --bind` 綁定無 marker 的相符 PR | 預期身份與 marker 在外部呼叫前已持久化；相符 → identity 已保存，正式 review 只在此之後派出；base 或 SHA 不符、2 個 → Blocked，建立請求 0 次；延遲建立 → unknown＋Blocked，建立請求共 1 次；marker＋身份相符 → succeeded；其餘兩種讀回 → Blocked；`--bind` → succeeded，`origin=existing` | G01、A04、D12、D13 |
| h11 [r12] | `write push`：檢查 argv；遠端拒絕 non-fast-forward；push 結果 unknown 後讀回遠端 ref 等於該 SHA；同一 SHA 的 fast-forward 重送 | argv 從不含 force 選項；non-FF → failed＋Blocked，0 次 rebase 或 force；讀回相符 → succeeded；重送同 SHA 在重試上限內允許 | D13、G17 |
| h12 [r12] | 每個 job 的 tested SHA 產物：三個 job 各有 `tested-sha-<job>-<run_attempt>` 且相符；缺一個 job 的產物；產物的 run_id、run_attempt、job 或 check 名稱不符；產物 SHA≠H；重跑後只有舊 attempt 的產物 | 只有第一種計入；其餘 → unknown，不能 pass | G13、G14 |
| h13 [r12] | 整合 base 的觸發：base 移動且 `mergeable=true`、沒有 finding；`mergeable=false`；`mergeable=null` 後轉為 true；`mergeable=null` 直到 timeout；Reviewer finding 判定不相容；人工 `revise` 註明整合 | 第一種 → 不整合，只重新綁定（h7）；`false`、finding、人工 → 狀態記 `integration_required` 並附觸發來源（batch 由 r12 驗證）；null→true → 等待後不整合；null 到 timeout → Blocked。[r13] 同一組（base、B、H）重複觀察到 `mergeable=false` → 同一個整合 finding ID；PR 有衝突而 H 沒有候選 CI run → G3 為 unknown（`ci_unavailable_conflict`），不是 pending 也不是 success | G17、G13 |

### M-REV：`tests/test_review.py`（T5.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| r1 | G2 verdict 矩陣：完整範圍＋目前版本＋`clean`；`changes_required`；`blocked`；缺 verdict；只審部分 diff；舊版本；非獨立的 session；model 不符；capability unverified | 只有第一種 passed；`changes_required` → failed；`blocked` → G2 unknown，[r12] **feature Blocked**，0 個新輪、0 次派修；其餘都 unknown 或不通過 | G03、G11、G12 |
| r2 | Reviewer 給 `spec_ac` 的 AC 缺陷，和 `preference` 的命名建議 | 前者 blocking，後者 nonblocking；兩者都有 ID 與依據 | F01 |
| r3 | 同一問題移了行（有 `matches`）；同一行但不同問題（沒有 `matches`） | 前者沿用同一 ID；後者新 ID；不做自動合併 | F02 |
| r4 | 關閉矩陣：Implementer 自稱已修；GitHub thread resolved；目前版本的 Reviewer 覆核＋證據；人工 `resolve_finding` 指定版本；人工指定舊版本 | 只有第 3、4 種能關閉，並記錄 actor、版本、證據 | F03、F04 |
| r5 | CI 先失敗，review 尚未完成 | 0 個 batch，直到 review 完成；文件缺陷可以列為修正項 | F05 |
| r6 | batch 含 F-1、F-2，回應只含 F-1 | 拒收並列出 missing `[F-2]`；F-1 與 F-2 都不解除 | F06 |
| r7 | 已用 3 輪；換 session 後嘗試第 4 輪 | 0 次派工；Blocked | F07 |
| r8 | 爭議：接受；維持；restart 後重送同一反證；反證伴隨新 head | 接受 → 依覆核關閉，輪數不變；維持 → Blocked；重送 → 0 次第二次覆核；新 head → 先 G1，再做新的 review 與 CI | F08、F09、F10 |
| r9 | `failed_rechecks=2`；已 resolved 的 finding 被 `matches` 再現 | 下一次派修前 Blocked；reopen 並保留歷史 | F15、F16、S1-R16 |
| r10 | 派修的 assignment | 帶有完整的 finding 快照、batch ID、finding IDs 與先前 review 的引用 | S1-R12 |
| r11 [r12] | finding → fix → re-review：`correctness_security` finding F-3 → 派修 batch B2 → (a) fix attempt 回傳綁定 F-3／B2 的原始 Red 與 H 上的 Green；(b) 只有 Green | (a) G1 passed → 以新 H 派 re-review；(b) G1 不通過並 Blocked，0 次 re-review，F-3 不解除 | G06、F04、A02、A13 |
| r12 [r13] | 整合路徑選擇，依序執行：<br>(a) **一般收齊**：H 的 G1 已通過，review 已派出、仍在進行，CI run 仍在進行，之後出現 `integration_required` → 收齊 review 與 CI 後開一個 batch，含整合 finding 與 review finding；<br>(b) **不等待**：H 的 G1 尚未通過（或 review 尚未派出），PR 有衝突，H 沒有 CI run → 立即開 `pre_review_g1` batch（原因 `base_integration`）；<br>(c) 同 (b)，但 Implementer 的前一個 attempt 仍 active，或狀態 unknown；<br>(d) 重複的 `mergeable=false` 觀察與重複的人工 `revise`，對同一組（base、B、H）；<br>(e) 整合後產生新 H；<br>(f) 已用 3 輪時再出現整合需求 | (a) 一個 batch，派修時計一輪。(b) 0 次為 H 派 G2、0 次等待 CI；G3 在 H 記 unknown，不算 success；一個 batch，計一輪；assignment 釘住 H 與 B，授權匯入與作者編輯範圍；0 次 GitHub PR merge 呼叫，外部寫入沒有 merge。(c) 確認 writer 已結束前 0 次派修；unknown → 依 D47 停止或 Blocked。(d) 同一個 finding ID，只有一個未結 batch。(e) H 上舊的 G2／G3 結果標為 obsolete、已收到的 findings 保留；新 H 需要完整的 G1、G2、G3 才能 Pass。(f) Blocked，0 次派工 | G17、F05、F07、O10、G01 |
| r12b [r14] | 路徑優先序混合矩陣：<br>(a) 適用 G1 passed、review 在途、PR 衝突且沒有 CI run；<br>(b) 適用 G1 passed、review 有終態結果、CI 真正在途；<br>(c) 適用 G1 passed、review／CI 都有同版本終態結果；<br>(d) 同 (a)，但 active-time 或三輪修正上限已用盡；<br>(e) 同 (b)，但 CI 後來變得過時／確定不可用；<br>(f) 同 (c)，但 G2 verdict 為 blocked 或 G3 policy unknown | (a) 前置整合優先，0 次等待不存在的 CI；不新增 G2；writer 安全核對後只派一個 pre_review_g1 batch，整合後重新取得三 gates。(b) 只等 CI，0 次提前派修。(c) 不等待，合併為一個 batch。(d) Blocked，0 次派工，預算不重置。(e) 重新走優先路徑，不把舊結果當成功。(f) 保留獨立 blocker，不派修也不 Pass | G17、F05、F07、D17 |

### M-PASS：`tests/test_publish_pass.py`（T6.2）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| p1 | 三 gates 都 passed，且在同一版本；[r12] 兩個變體：G3 政策來源為 rules；為 403＋已核准的 `workflow.yaml` | 先 `publish_pr`，再 `publish_issue`，之後做 `pass` 觀察 → Pass。Pass package 含 version_key、PR identity（含 origin）、head、base、三 gates 的理由與 result ID／digest、findings（未解 blocking 為空，列出未解 nonblocking 與已關閉項的 closure 引用）、政策來源、`github_rules_verified`（前者 true、後者 false）、限制、發布狀態與 receipts、pass 觀察 seq、acceptance=pending，且 `status --human` 可讀；package 由狀態投影，改一筆被引用的紀錄 → 重新投影，舊 package 不能放行 | G01、G13 |
| p2 | review clean＋CI failure；CI green＋`changes_required` | 兩種都沒有 Pass；兩個 gate 的結果分別保存；第一種開修正 batch | G02 |
| p3 | Pass 前的 `pass` 觀察看到新 head；Pass 之後有 push | 前者放棄這次 Pass；後者讓 Pass 失效，保留舊紀錄 | G18 |
| p4 | 讀回 PR review 與 issue 摘要的內容 | PR review 含 verdict、finding 表（ID、分類、blocking、位置、依據、預期）、result ID、head、base、spec digest；issue 含待辦、blocking 的 ID、PR review 連結；兩者的 body digest 與 marker 都相符 | F13 |
| p5 | 發布結果 unknown；GitHub 已接受但回應遺失 | 依 marker 查回原 URL；共 1 則留言；review 不重做 | D12、F14 |
| p6 | 在 Pass 狀態下列出所有 write | 沒有 merge、close、release、deploy；acceptance 為 pending | O10 |

### M-RESUME：`tests/test_resume.py`（T6.2）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| u1 | worker 已完成、結果檔已存在但通知遺失、review 已保存、`publish_pr` 已成功、`publish_issue` pending → 協調者 restart，執行 `next` | 只有「匯入結果（一次）」和「`publish_issue`」兩個動作；0 次派工、0 次 review；預算與 findings 不變 | D07、D14、F14 |
| u2 | resume 時觀察到 head、base 或 spec 已改變 | 依 h7 的規則失效；acceptance 不沿用；不重新初始化 | D15 |

### M-BUD：`tests/test_budget.py`（T7.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| b1 | 時間區間重疊；到期的 stop 加上一個無關的 blocker；已 prepared 的 stop；stop 讀回用盡；離線超時；換 session | 重疊只算一次；stop 優先；同一個 op 只送一次；用盡 → 等人；離線 → 計入並 Blocked；換 session 不重置 | D17、S1-R09 |

### M-PRE：`tests/test_preflight.py`（T1.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| f1 | 已選的 reviewer profile 缺少 model 設定 | `unverified` → Blocked | D19 |
| f2 | 已選的兩個 profile 都 verified；未選的 Orca、Codex CLI 不在 PATH 或登入失敗 | preflight 仍 verified；未選項不被呼叫或使用 | D23 |
| f3 | profile 要求的 model 與 native 讀回的 model 不符 | `unverified` | D18 |

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
| W-F 歷史限制 | O15 | handoff 記錄 P03／Q-TARGET 為暫停狀態；產品沒有針對 P03 的特判程式 | 在產品程式寫 P03 特判；沒有明確 `init` 卻接管工作 | 協作者 |

## 4. 證據規則 rubric

- **G19、D22**：驗收報告 `docs/validation/s1/proof.md` 對每項能力，分欄列出 `fake`、`profile-probe`、`real-E2E` 三類證據，並依接法（Herdr＋Claude Code、Herdr＋OpenCode）分開。
  - 未執行的格子標 `none`；
  - 不同接法之間不共用 passed 標記。
- **G20**：R3 沒有出現真實 finding → 示範維持 open，不製造 blocker。

## 5. 真實證據與界線

| ID | 內容 | 前置 | 通過標準 | 證據 |
| --- | --- | --- | --- | --- |
| R1 | 已選的兩個 profile 的 preflight（受限的能力 probe） | M-PRE | model 與 marker 讀回一致；負例都被拒；stop 經確認 | `docs/validation/s1/preflight/` |
| R2 | 在 `probe/s1-g1` 上用 fixture 跑到 G1；不是交付 feature，也不 merge | R1、M-G1、M-OBS、M-GH（h8）、M-BUD | G1 依證據判定，或附證據 Blocked；只算能力證據 | `docs/validation/s1/probe/` |
| R3 | 第一個有用的交付：一個 B1 尚未實作、由 D11 選定的新行為（D51-R04），走真實 finding → fix → re-review，中間中斷一次 | B1 accepted＋merged＋baseline（T8.0）；feature 已經過 D11 選定 | 三 gates 在目前版本都通過；改變行為的修正有綁定 finding 與 batch 的原始 Red（r11 規則）；中斷後成功接續。Blocked 或沒有 finding → 維持 open | PR、issue、CI URL、狀態 export |

- **R1 不涵蓋 D24**：第一片的 profile 組合是 Claude Code＋OpenCode，不是兩個角色都在 OpenCode。

## 6. D49 CI 候選（未核准）

- **GitHub workflow**：`.github/workflows/loopctl-ci.yml`（T1.1），名稱 `loopctl-ci`，app `github-actions`。
  - **觸發**：只有 `pull_request`（types：opened、synchronize、reopened；branches：預期 base）。不以 push 觸發。
- **必要 checks**（每個 job 以同一個測試命令，並設 `LOOPCTL_EXPECT_PLATFORM`）：
  - `unit-linux`（ubuntu-24.04）：`uv run pytest`（M-TPOL 政策由 `pyproject.toml` 與 `tests/conftest.py` 生效）；
  - `unit-macos`（macos-15）：同上；
  - `static`：`ruff`、`mypy`、`scripts/dist-smoke.sh`（`uv build` → 在全新 venv 安裝 wheel → 在 checkout 外執行 `loopctl`，並 `import loopctl.tools`）。
- **Checkout 與 tested SHA**：
  - checkout `github.event.pull_request.head.sha`；`git rev-parse HEAD` 與它不符 → job 失敗；
  - 每個 job 上傳 `tested-sha-<job>-<run_attempt>`，內容為 run_id、run_attempt、job、check 名稱與 tested SHA；
  - G3 只計入 event、PR、`head_sha==H` 都相符，且產物內容逐欄相符的 check（design §8；h4、h12）。
  - 保守規則：只重跑失敗的 job 時，其他 job 可能沒有同一 attempt 的產物，需要改為重跑全部 jobs。這不新增任何 controller 的 rerun 功能。
- **政策檔**：repo 根目錄的 `workflow.yaml`（loopctl 政策檔，不是 GitHub workflow；T1.1 建立）記錄上述 checks、GitHub workflow 路徑與 blob digest、`source: head`、沒有例外、`evidence` command IDs。
- **生效條件**：D11 核准這個集合，並記錄 `policy_change` 綁定 `workflow.yaml` 的 digest。
  - G3 與 Pass package 顯示 `github_rules_verified=false`；
  - 這份核准也可用於 B1。
