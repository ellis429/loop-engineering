讀完了。以下是對照結果。

**verdict: gaps_found**

---

### Blocking

**G-01**｜task 5.1｜blocking｜**`register` 寫物件的時機沒有定在授權之後，和 D4「被拒的命令不寫檔」矛盾；測試的「bytes 不變」範圍也沒定**
- 情境：非 owner（錯 token、沒 token）、run 不存在、狀態不可信、或 run 處於 Blocked 時執行 `register --content-from <任意大檔>`。計畫說「在邊界讀取 locator 或 `--content-from`，並存成物件」，也就是在 `commit`（授權在 `commit` 內的第 2 步）之前就呼叫 `put_object`，`$LOOPCTL_HOME/objects/` 會被未授權的呼叫者寫入。`test_unreadable_documents_are_not_registered` 要求 not_owner「bytes 不變」，但沒說是 run 目錄還是整個 `$LOOPCTL_HOME`——若照 4.1 的 `test_adopt_delegate…` 以 `home` 快照，寫物件就會讓測試失敗；若只快照 run 目錄，則留下未授權寫入的洞。
- 依據：`tasks.md:319`（存成物件在邊界）、`tasks.md:345`（bytes 不變）、`design.md:174`（授權先於任何寫入）、`design.md:204`（被拒的命令不寫任何檔）、`store.py:304-312`（`authorize` 只在 `_commit` 內跑）、`store.py:474-489`（`put_object` 直接寫 `objects/`）、`cli.py:62-75`。
- 建議的最小規則：`register` 的順序明寫為：無狀態核對（讀 locator／`--content-from` → `locator_unreadable`；缺 `--role`／`--producer` → `missing_fields`）→ `store.load` 並以 `owner_token(token)(state)` 預核（`run_not_found`／`untrusted_state`／`not_owner`）→ `put_object` → `commit_latest`（store 內再核一次）。Blocked 時物件可能已寫但 content-addressed、不在 run 目錄，接受為無害並在計畫寫明；測試對 not_owner 以 `$LOOPCTL_HOME` 快照，其餘以 run 目錄快照。

**G-02**｜task 5.1｜blocking｜**「內容相同的重登 → no-op」的「相同」沒有定義，而登記項帶 `registered_at`**
- 情境：(a) 已核准後把同一份 spec 原樣重登：D5 說 no-op、revision 不變；但 D9 的登記項含 `registered_at`，`clock.now()` 是秒級，`mutate` 若寫入新的 `registered_at`，D4 第 6 步的 `new == state` 只在同一秒內成立——有時 no-op、有時多一版（且已核准時變成「改變內容」）。(b) `test_only_a_human_approve_plan…` (e)→(g)：implementer 先登記 `tasks.md` 沒帶 `--calibrated-from`，再以相同檔案、相同 version 補上 `--calibrated-from`。若「相同」只看 digest，(g) 變成 no-op，plan 仍未校準，核准回 `plan_not_calibrated`。(c) 已核准時，同 digest 但改 `version`／`source`／`producer` 算不算「改變內容」也沒說。
- 依據：`design.md:294`（`registered_at`）、`design.md:212`（register 重送 no-op）、`design.md:186`（第 6 步比對整份狀態）、`design.md:303-304`、`tasks.md:347`(e)(g)、`tasks.md:350`、`clock.py:10`（秒級）。
- 建議的最小規則：登記項除 `registered_at`（以及 6.1 之後由 derive 寫入的 `superseded_by`）之外全部相等 → `mutate` 回傳原狀態（保留舊的 `registered_at`），由第 6 步判為 no-op；否則取代。已核准時，plan／spec／ac／design 的任何非 no-op 登記（含 version、source、producer 不同）→ `scope_change_required`。`approval.plan`、`scope_change.supersedes`、`next.dispatch.plan` 的釘選只取 `{locator, version, digest}`。

**G-03**｜task 6.1｜blocking｜**`scope_change` 在沒有 plan 時的行為沒定義**
- 情境：run 在 `planning`（plan 為 `null`），人工送 `scope_change`。D10 說它沒有有狀態的檢查，效果是「記錄 `supersedes`（plan 的 locator、version、digest）」——plan 為 `null` 時取欄位會 `TypeError`，變成沒有 envelope 的 traceback（違反 D2「stdout 永遠是一行 JSON」），或實作者自行決定記成 `supersedes: null`。測試表兩個參數都有 plan，不會攔到。
- 依據：`design.md:320`、`tasks.md:387`、`decisions.py:91-99`（目前只記錄，無任何 plan 存取）。
- 建議的最小規則：仿 `policy_change` 的 `policy_not_registered`，`scope_change` 加一條有狀態檢查「有 plan，否則 `plan_not_registered`」；D10 表與 6.1 交付各補一句。

### Minor

**G-04**｜task 5.1｜minor｜**幾個名稱沒定**：D10 `approve_plan` 的「有 plan」沒有錯誤名；`missing_bindings` 列出缺角色的欄位名；`register` 成功時 `result` 放什麼。
- 依據：`design.md:319`、`tasks.md:348`、`cli.py:118-119`（`Rejected` 的 fields 原樣進 result）。
- 建議：沒有 plan → `plan_not_registered`（與 D7 的 blocker 同名）；`{error: "missing_bindings", roles: [...]}`；`register` 的 `result` 為登記項（去掉 `content`）加 `unchanged: true|false`。

**G-05**｜task 5.1｜minor｜**`policy` 帶 `--content-from` 的規則與 D9 矛盾**
- 情境：`register policy --locator workflow.yaml --content-from issue-29.md`。D9 說 locator 可讀就讀它（`--content-from` 不看），測試表卻說 `policy` 帶 `--content-from` → `locator_unreadable`。兩種讀法得到不同 exit code。
- 依據：`design.md:296-299`、`tasks.md:345`。
- 建議：明寫「`policy` 一律不接受 `--content-from`，有給就回 `locator_unreadable`（不看 locator 是否可讀）」，或把該參數改成 locator 為 URL。

**G-06**｜task 5.1／6.1｜minor｜**`register plan` 三種拒絕／no-op 的順序沒寫**
- 情境：(a) 6.1 兩個測試要求「以相同 version 與 digest 重登被取代的 plan → `plan_superseded`」，所以 `plan_superseded` 必須排在 no-op 之前，否則得到 exit 0。(b) 已核准＋被取代可同時成立：X 核准 P1 → S 取代 P1 → 登記 P2 → Y 核准 P2 → 重登 P1：`scope_change_required` 和 `plan_superseded` 都適用，誰先沒說。
- 依據：`design.md:212`、`design.md:303-306`、`tasks.md:388`、`tasks.md:389`(iv)。
- 建議：在 D9 寫明順序：已核准守門（`scope_change_required`）→ `plan_superseded` → no-op → 取代。

**G-07**｜task 5.1｜minor｜**locator 的相對路徑基準、以及與種類無關的參數**
- 情境：測試斷言狀態檔 `plan.locator == "tasks.md"`（原樣），而 `repo` fixture 在 `tmp_path/repo`，所以相對 locator 必須以 cwd 解析、測試要 `monkeypatch.chdir(repo)`（`cli_proc` 用 `cwd=os.getcwd()`，一致）。另外 `plan --role x`、`binding --producer x`、`policy --calibrated-from x` 是忽略還是拒絕沒說。
- 依據：`design.md:290-291`、`tasks.md:344`、`conftest.py:204`、`conftest.py:309-317`。
- 建議：明寫「相對 cwd 解析，`path` 存絕對路徑；測試 chdir 到 `repo`」；與種類無關的參數忽略。

**G-08**｜task 5.1／6.1｜minor｜**5.1 與 6.1 在 `approve_plan`「未被取代」與 `plan_superseded:<id>` blocker 的邊界可被讀寬，會讓 6.1 的 Red 提前變綠**
- 情境：5.1 交付寫「D10 的 `approve_plan`」與「D7 的 plan 阻擋」；D10 那列含「未被取代」、D7 那列含 `plan_superseded:<id>`。若 5.1 照字面做了（讀 `plan.get("superseded_by") or []`），6.1 第一個測試先實作衍生後，第二個測試的 Red（`approve_plan` 還不看是否被取代）一寫就綠，依規則要停下。
- 依據：`tasks.md:317`、`tasks.md:321`、`tasks.md:365-366`、`tasks.md:388`、`design.md:266`、`design.md:319`。
- 建議：5.1 交付明寫「不含『未被取代』檢查與 `plan_superseded:<id>` 阻擋，兩者由 6.1 加」。

**G-09**｜task 5.1｜minor｜**兩個 Red 很可能提前變綠，計畫沒給條件突變**
- `test_approve_plan_needs_spec_ac_and_design_bindings`：前一個測試 (g) 已要求把 spec／ac／design 的 binding digest 釘進 `approval`，實作時自然會一併發現缺角色；`test_next_after_approval_reports_dispatch`：第三個測試重寫 `_next` 時自然會照 D7 整表加上 approval 列。兩者都沒標「突變」。
- 依據：`tasks.md:347-349`、`tasks.md:453-455`（風險節只列了三個「視實作順序而定」的突變）。
- 建議：比照風險節加兩條條件突變：前者「若已核對 binding → 暫時拿掉 `missing_bindings` 檢查」；後者「若已加 approval 列 → 暫時拿掉它」。

**G-10**｜task 5.1／6.1｜minor｜**擁有路徑沒有 `tests/conftest.py`，但兩個 task 都需要「已登記 plan＋三個 binding（＋核准）」的前置**
- 情境：5.1 八個測試、6.1 六個測試都要這套前置；若實作者想做成共用 fixture，conftest 不在擁有路徑，共用檔案表也沒有 5.1／6.1 的項，會像 4.2 的 `cli.py` 一樣停下。
- 依據：`tasks.md:35`、`tasks.md:323`、`tasks.md:369`。
- 建議：二選一寫明：「helper 留在各自測試模組」，或共用檔案表加「5.1 加 `approved_run`（只新增）→ 6.1 重用」。

**G-11**｜task 6.1｜minor｜**policy 已核准、同一 digest 再做一次 `policy_change`（新 id）沒定義**
- 情境：D10 的 `policy_change` 沒有 `already_approved`。是拒絕、還是覆蓋 `policy_approval.decision`？影響撤銷：覆蓋後撤銷舊的 P 時 `decision` 已不等，依 D10 不動。
- 依據：`design.md:321`、`design.md:333`。
- 建議：允許，`policy_approval` 換成最新那筆（不變式「只來自建立它的那筆」仍成立）。

**G-12**｜task 6.1｜minor｜**`attempted` 時 A 是 `scope_change`，`supersedes` 的計算基準要明寫**
- 情境：(iii) 登記 P2 後對 S 製造衝突，測試只用 `abandon`；若選 `attempted`，依 D6「在撤銷後的狀態上照常核對並生效」，A 的 `supersedes` 應是當下的 P2，不是衝突紀錄裡 C 的 P1。計畫沒寫，實作從 `conflicts[cid].committed_payload` 或舊紀錄取 `supersedes` 不會被測試攔到。
- 依據：`design.md:236`、`tasks.md:389`(ii)(iii)。
- 建議：6.1 交付補一句「A 的 `supersedes` 以解除當下的 plan 計算」。

**G-13**｜task 6.1（G22 驗收示範）｜minor｜**示範命令缺 parser 強制的參數**
- 情境：`register policy --locator workflow.yaml` 缺 `--version`、`--source`，parser 會回 exit 2 `usage`；`decide policy_change --actor human:<name>` 缺 `--token`、`--id`、`--target`、`--reason`、`--source`、`--impact`、`--version`。
- 依據：`tasks.md:427-428`、`design.md:63-66`、`cli.py:348-350`。
- 建議：補齊成可直接執行的命令（`--version` 任意、`--target workflow.yaml --version <登記的 digest>`）。

---

### 其餘核對（沒有問題）

- 5.1 的 Red：T1（`plan.locator`，stub 不登記）、T2（讀檔例外進 `exc`）、T3（視圖沒有 `approval`）、T4 (d)（4.1 只記錄）、T7（登記直接取代）、T8（`void` 只標 `voided`，`approval` 還在）都能失敗在所列斷言上。
- 6.1 的 Red：T1（`approval` 不清）、T3（計畫已給條件突變）、T4（視圖沒有 `policy`）、T5、T6 都可達。
- 既有測試不受影響：4.1 對 `approve_plan`／`scope_change`／`policy_change` 只送無狀態就被拒的請求（`test_decisions.py:115-157`），沒有任何測試預期這三種 kind exit 0；`test_cli.py:211` 的 `register` 參數在 5.1 之後仍會印一行 envelope。
- D7 的優先序安全：`approval` 不可能與 `plan.superseded_by` 非空同時存在（`scope_change` 清核准並取代；被取代的 plan 批不過；`attempted` 套 `approve_plan` 時 A 的 `plan_superseded` 會讓整個解除被拒）。
- 衝突落在 `approve_plan`／`scope_change`／`policy_change` 上的三種選擇，以及撤銷不還原核准，D6＋D10 的組合都能推出確定結果；`store.py:385-402` 的 `attempted` 路徑和 `decisions.py:109-140` 的 `void`→`decide(A)` 流程不需改。

### 實際讀過的檔案

- `openspec/changes/run-decisions/tasks.md`（全文）
- `openspec/changes/run-decisions/design.md`（全文）
- `openspec/changes/run-decisions/proposal.md`
- `openspec/changes/run-decisions/specs/{delivery-orchestration,durable-delivery,delivery-gates}/spec.md`
- `openspec/changes/run-decisions/reviews/plan/README.md`、`round-12-review.md`、`round-13-review.md`
- `src/loopctl/{cli,store,state,next,decisions,clock}.py`
- `tests/{conftest,test_cli,test_state,test_decisions,test_conflicts}.py`
- `git log`（commit 列表與 `48b4201`、`a3808d7` 的 stat）