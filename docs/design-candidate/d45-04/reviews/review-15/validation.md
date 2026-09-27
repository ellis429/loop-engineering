# Validation：第一個可用切片（候選 design-04）

> **全部是 planned，沒有任何測試已執行，也沒有任何 AC 已通過。** 每個 ID 的歸屬以 [coverage.md](coverage.md) 為準。
> 本文分三類驗證，不互相代替：
> - 產品測試矩陣（§2）；
> - workflow 樣本加 rubric（§3）；
> - 真實證據（§5）。
>
> fake 證據不改標為 real。附證據的 Blocked 不算示範完成。

## 0. 必要測試政策

驗證分兩層（D51-R05）：

- **本機驗證與 G1**：在本機跑適用的完整測試套件。
  - 平台專屬的案例只用一般的 pytest 平台條件選擇，例如 fsync 順序只在 Linux 執行。
  - 以下任一情況 G1 不通過：套件缺失或收集不完整（例如 0 個）、有無法以平台條件解釋的 skip、有 failure。
  - G1 不等待遠端 CI。
- **遠端 CI 與 G3**：push 並建立 PR 之後，§6 的必要 job／check 是否齊全且成功，由 G3 判定（M-GH 的 h2、h4）。
- 不為了變綠而放寬斷言或刪除案例。

## 1. 環境

| 代號 | 內容 |
| --- | --- |
| ENV-F | Python 3.12（uv）、真 git；PATH 上放 fake `herdr`／`gh`（依情境檔回應，並記錄 argv 與呼叫次數） |
| ENV-R | Herdr 0.9.1、Claude Code（Opus 5.5 Implementer）、OpenCode（Reviewer，model 待 D11） |
| ENV-GH | `yschiang/loop-engineering` 的 PR／issue／Actions |

## 2. 產品測試矩陣（ENV-F，參數化）

每一列是一個參數化案例，格式為「輸入／前置 → 動作 → 斷言」。檔案與 task 見 tasks.md 的執行表。

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
| d4 | implementing 期間送 `scope_change` | 批准失效，進入 awaiting_approval；不 crash | O07 |
| d5 | 以 runtime 父 session 身分，或 Project Lead 角色標記 `decide approve_plan` | 拒絕；權限只看人工 decision 與 token | O19 |
| d6 | 登記原生路徑的 plan 與 spec，並讀回 | locator、版本與內容可讀回；不改名；task 不另外變成 PR | O03 |
| d7 | 接受與退回矩陣：pending 時 `return`（ac_defect）；在 V1 上 `accept` 後 head 變成 V2；`accept` 指向舊版本 | 退回 → `source=human_acceptance` 的 finding、預算相同、Pass 失效；V2 為 pending，V1 歷史保留；指向舊版本 → 拒絕 | O11、F11 |
| d8 | 呼叫 `adopt` 或 `delegate` 入口 | 回 `unsupported`；狀態不變；沒有繞過任何核對 | O08、O09、O18（僅負例） |

### M-WRITE：`tests/test_writes.py`（T2.3）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| w1 | 兩個程序同時 `write prompt` 同一個 op | fake herdr 被呼叫 1 次 | D13 |
| w2 | 送出後 receipt 遺失，查回原 marker | 讀回後轉為 succeeded，沒有重送 | D12、D13 |
| w3 | 延後生效的 worktree、查無的 prompt、client 已結束 | unknown＋Blocked；0 次重送 | D13、S1-R05 |
| w4 | 讀回結果依序為「仍在執行」×3 | 第 4 次讀回被拒；變成 `blocked(readback_exhausted)` | D16 |
| w5 | writer 結束矩陣：只有 terminal idle／Herdr `done`；結果已匯入＋native turn 完成；stop 經 process-info 確認；狀態 unknown | 前一項 → 0 次派下一個；中間兩項 → 允許派下一個；unknown → Blocked | D04 |
| w6 | result 的身份、cwd、head、scope 不符，或內含 worker 提供的 argv | 拒收；原件保存；列出差異 | D05 |
| w7 | 同一個 result 重送；同 attempt 但 bytes 不同 | 前者沒有新的 transition；後者雙方都保存並 Blocked | D08 |
| w8 | 沒有結果檔、也沒有通知，native transcript 裡有 marker 之後的結果 JSON | 工具寫出 result，帶 `producer=tool`、native session／message ID、原文 digest，並匯入一次；無法解析 → unknown | D06 |
| w9 | Claude uuid 與 OpenCode `ses_…` 兩種 handle 的 round-trip；result 的 native ID 不符 | 以 attempt ID 對回；不符 → 拒收；不補造 ID | D21 |

### M-G1：`tests/test_g1.py`（T3.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| g1 | 原始 Red 有效，head Green 通過，不做 replay | G1 passed | G06 |
| g2 | 證據互相矛盾 → 觸發 replay：成功與失敗各一 | replay 只作診斷：成功 → 繼續，失敗 → Blocked；都不能補造 Red | G06、G07 |
| g3 | 分別污染 raw、exit、task、snapshot、producer | 每一種各自使 G1 失敗，並列出原因 | G04 |
| g3b | 適用資格（D51-R07）。各情境的 raw 與 producer 都有效，而且都另做一次 replay 且成功：<br>(a) snapshot 或 attempt 的 commit 超出核准 scope；<br>(b) **兄弟 snapshot**：與 attempt 有共同的 parent，但沒有對應到該 task／attempt 的捕捉紀錄，它的測試內容也不在 attempt 的 commit 中；<br>(c) attempt 不是 H 的祖先；<br>(d) 正例：尚未 commit 時捕捉的原始 Red，provenance 帶有 task／attempt，而且它的測試 delta 出現在 attempt 的 commit 中，attempt 是 H 的祖先 | (a)、(b)、(c) 各自使 Red 無效，replay 成功也不能補救；(d) 有效，不需要同 SHA，也不需要 replay | G04、G06、G08、S1-R13 |
| g4 | 缺原始 Red；task 集合為空；只有語法錯誤的 Red | G1 fail | G07、S1-R11 |
| g5 | 證據存在 repo 外；C 之後的文件 commit 產生 head D | tracked 文件只引用 result ID 與 digest；在 D 需要重跑 Green；Red 依 lineage 仍適用；記錄「只有文件差異」的理由 | G05 |
| g6 | 整合 regression 失敗 | 開 `pre_review_g1`（計一輪）；G1 passed 前 0 次 G2 | G08 |
| g7 | N/A 正向：純文件 diff＋獨立 Reviewer eligibility（model、權限都相符） | G1 passed；G2／G3 仍然 pending | G09 |
| g8 | N/A 負例：自我宣告、pending、被拒絕、model 不符、diff 含 config 或 test code | G1 不通過，並列出原因 | G10、S1-R15 |
| g9 | `evidence red` 帶任意 argv | 被拒；marker 檔不存在（證明沒執行） | S1-R01、R13 |

### M-GH：`tests/test_github.py`（T6.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| h1 | 政策來源矩陣：rules 可讀；403＋`yschiang/loop-engineering`＋已核准且綁定 digest 的政策；403＋沒有政策；403＋政策未核准；403＋digest 不符；403＋其他 repo | 依序為：採用規則；採用政策並標 `github_rules_verified=false`；後四種 → unknown＋Blocked，0 個修正輪 | G13、S1-R14 |
| h2 | 必要 check 的狀態：missing、pending、cancelled、timed_out、failure、unknown、stale、skipped、neutral，以及空的必要集合 | 全部不通過並附原因；第一片的政策沒有例外 | G13 |
| h3 | 通用例外機制：skipped＋核准的 decision；failure＋例外；例外沒有 decision | 第一種可以接受（只在允許例外的政策下）；後兩種 → `policy_invalid`，Blocked | G13、S1-R17 |
| h4 | 舊 attempt success，新 attempt pending；新 attempt 為 queued 且 `started_at=null`；同名但其他 app；同 app 同名但來自其他 workflow；`run_id` 較小但 `run_number` 較大的 run；缺少 `run_number` 或 `run_attempt`；同一個 workflow 出現兩個相同的 `run_number`；必要 check 只有 commit status；共 3 頁、最新的在第 3 頁 | 依所選 workflow 的 `run_number`、再依 `run_attempt` 採最新 → pending（queued 也算最新）。`run_id` 不用來判斷先後，所以 `run_number` 較大者勝出。其他 app 或 workflow 不計入。識別或順序缺失、有歧義 → unknown，不回退到舊 success；只有 commit status → unknown；會讀完所有分頁 | G14 |
| h5 | 必要 check 以整合 SHA M 執行（M≠H）；check-run 的 `head_sha==H` 但 `tested-sha==M` | unknown（`unsupported_integration_source`）；不能 Pass | G15（負例） |
| h6 | 觀察的 seq 亂序：同 purpose 較舊者晚到；跨 purpose 時 `pass`（seq 10，H1）比 `pr`（seq 11，H2）晚到 | head 維持最新；舊觀察只存歷史 | G16 |
| h7 | head 不變時的版本變更矩陣：base、spec、AC、design、plan、skill、policy、controller 版本 | 依 design §8 的表：G1、G2、G3 的處理與批准要求逐格斷言；等待批准期間 0 次派工。base 改變時：在 H 本身重跑 Green 並綁定新 base；不以暫時合併的 snapshot 當作 H 的 Green；需要整合 → 新 head 讓所有 gates 重新判定（D51-R02） | G17、D15 |
| h8 | 讀取失敗預算：同一個 `ci:<H>` 連續失敗 3 次，之後換新的 seq、新的 session、restart | 第 3 次失敗後 Blocked；之後 0 次自動 fetch；計數不因 seq／session／restart 重置；`resolve_read` 只給一次新的 3 次額度 | D16 |
| h9 | pending→pending→success（每次都成功取得） | 失敗計數維持 0；依輪詢間隔再觀察 | G13、D16 |
| h10 | PR 正向路徑：G1 passed → `push` → `pr_ensure`（事先查到 0 個 open PR → 建立一次；1 個 → 沿用；2 個 → Blocked）→ 記錄 PR identity。**延遲建立的反例**（D51-R01）：建立結果 unknown，讀回查無，之後 fake GitHub 才出現這個 PR | PR identity 已保存；正式 review 只在此之後派出；延遲建立的案例 → unknown＋Blocked，建立請求共 1 次，沒有第二次 | G01、A04 |

### M-REV：`tests/test_review.py`（T5.1）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| r1 | G2 verdict 矩陣：完整範圍＋目前版本＋`clean`；`changes_required`；`blocked`；缺 verdict；只審部分 diff；舊版本；非獨立的 session；model 不符；capability unverified | 只有第一種 passed；`changes_required` → failed；`blocked` → unknown 且 0 個新輪；其餘都 unknown 或不通過 | G03、G11、G12 |
| r2 | Reviewer 給 `spec_ac` 的 AC 缺陷，和 `preference` 的命名建議 | 前者 blocking，後者 nonblocking；兩者都有 ID 與依據 | F01 |
| r3 | 同一問題移了行（有 `matches`）；同一行但不同問題（沒有 `matches`） | 前者沿用同一 ID；後者新 ID；不做自動合併 | F02 |
| r4 | 關閉矩陣：Implementer 自稱已修；GitHub thread resolved；目前版本的 Reviewer 覆核＋證據；人工 `resolve_finding` 指定版本；人工指定舊版本 | 只有第 3、4 種能關閉，並記錄 actor、版本、證據 | F03、F04 |
| r5 | CI 先失敗，review 尚未完成 | 0 個 batch，直到 review 完成；文件缺陷可以列為修正項 | F05 |
| r6 | batch 含 F-1、F-2，回應只含 F-1 | 拒收並列出 missing `[F-2]`；F-1 與 F-2 都不解除 | F06 |
| r7 | 已用 3 輪；換 session 後嘗試第 4 輪 | 0 次派工；Blocked | F07 |
| r8 | 爭議：接受；維持；restart 後重送同一反證；反證伴隨新 head | 接受 → 依覆核關閉，輪數不變；維持 → Blocked；重送 → 0 次第二次覆核；新 head → 先 G1，再做新的 review 與 CI | F08、F09、F10 |
| r9 | `failed_rechecks=2`；已 resolved 的 finding 被 `matches` 再現 | 下一次派修前 Blocked；reopen 並保留歷史 | F15、F16、S1-R16 |
| r10 | 派修的 assignment | 帶有完整的 finding 快照與先前 review 的引用 | S1-R12 |

### M-PASS：`tests/test_publish_pass.py`（T6.2）

| 案例 | 輸入 → 動作 | 斷言 | AC |
| --- | --- | --- | --- |
| p1 | 三 gates 都 passed，且在同一版本 | 先 `publish_pr`，再 `publish_issue`，之後做 `pass` 觀察 → Pass | G01 |
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
| W-C Plan 與批准 | O01、O22、O26、O23、F12 | 使用者可以直接交付給 Implementer；Project Lead 的草案經校準後只有一份 plan；SA 確認與 D11 分開記錄；跨 feature 影響與新需求回人裁決 | 以草案 plan 派工；以 SA 確認代替 D11；把範圍外需求混入 fix | Implementer＋使用者 |
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
| R2 | 在 `probe/s1-g1` 上用 fixture 跑到 G1；不是交付 feature，也不 merge | R1、M-G1、M-GH（h8）、M-BUD | G1 依證據判定，或附證據 Blocked；只算能力證據 | `docs/validation/s1/probe/` |
| R3 | 第一個有用的交付：一個 B1 尚未實作、由 D11 選定的新行為（D51-R04），走真實 finding → fix → re-review，中間中斷一次 | B1 accepted＋merged＋baseline（T8.0）；feature 已經過 D11 選定 | 三 gates 在目前版本都通過，且中斷後成功接續。Blocked 或沒有 finding → 維持 open | PR、issue、CI URL、狀態 export |

- **R1 不涵蓋 D24**：第一片的 profile 組合是 Claude Code＋OpenCode，不是兩個角色都在 OpenCode。

## 6. D49 CI 候選（未核准）

- **Workflow**：`.github/workflows/loopctl-ci.yml`（T1.1），名稱 `loopctl-ci`，app `github-actions`，`source: head`，沒有例外。
- **必要 checks**：
  - `unit-linux`（ubuntu-24.04）：`uv run pytest -q -ra`；
  - `unit-macos`（macos-15）：`uv run pytest -q -ra`。
  - `static`：`ruff`、`mypy`、`scripts/dist-smoke.sh`（`uv build` → 在全新 venv 安裝 wheel → 在 checkout 外執行 `loopctl`，並 `import loopctl.tools`）。
- **Checkout**：
  - PR 事件 checkout `github.event.pull_request.head.sha`，push 事件 checkout `github.sha`；
  - `git rev-parse HEAD` 與預期 SHA 不符時，job 失敗；
  - 上傳 `tested-sha` 產物。
  - G3 只計入 `head_sha==H` 且 `tested-sha==H` 的 check。
- **生效條件**：D11 核准這個集合，並記錄 `policy_change` 綁定 `workflow.yaml` 的 digest。
  - G3 與 Pass package 顯示 `github_rules_verified=false`；
  - 這份核准也可用於 B1。
