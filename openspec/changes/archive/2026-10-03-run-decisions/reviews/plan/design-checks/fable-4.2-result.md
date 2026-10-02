`verdict: gaps_found`（8 條，全部 minor；沒有會讓 run 卡死或讓已撤銷核准復活的情況，見末段）

---

**DG-01**
- 嚴重度：minor
- 情境：X/a 已提交；X/b → Kb，以 `original` 解除（b 被否決）；再送 X/c → Kc 未解。此時重送 X/b。D4 第 3 步的順序是 duplicate → 已否決 → 衝突，得 exit 1 `transition_rejected:Kb`；D6 卻寫「已有未解衝突 K 時，對同一 identity 送來的**任何**不同內容都回 exit 3、指向 K」，得 exit 3。第 13 輪審查以 D4 的順序理解（「先處理 duplicate、歷次否決，再套用單一未解衝突規則」），實作落在 D6 的讀法（未解衝突檢查在已否決檢查之前）。
- 依據：`design.md:175-178`、`design.md:226`、`reviews/plan/round-13-review.md`、`store.py:351-358`
- 建議的最小規則：D4 第 3 步明寫三支的順序為「等於接受的內容 → 原 revision；同一 identity 已有未解衝突 → exit 3 指向它；等於已否決內容 → `transition_rejected`；其他 → 記衝突」（維持現行行為），D6:226 的「任何不同內容」加註「不含等於接受內容的重送」。
- 影響的 task：4.2（文件）

**DG-02**
- 嚴重度：minor
- 情境：(a) K1（identity X）未解；owner 把已提交的 Y 以不同內容重送 → 第 3 步在第 4 步之前，記下 K2 並提交新 revision——`tasks.md:304` 的「run 有兩個未解衝突」就靠這個；但 D6「其他寫入一律 exit 3，不寫」與 D4「第 8 步之前任何一步失敗，都不寫任何檔」都說不寫。(b) 衝突紀錄這次提交不經第 5 步 `expected_revision` 核對；是否做第 7 步物件檢查與第 8.1 步前移沒有說（實作兩者都做）。(c) D2「已提交後重送：同一 transition identity 的重送回 duplicate」——`conflict:<cid>` 的提交在 `os.link` 之後失敗（`committed: true`）時，重送同一嘗試得到的是 exit 3 指向 K，不是 duplicate。
- 依據：`design.md:171`、`design.md:178`、`design.md:223-226`、`design.md:229`、`design.md:93`、`tasks.md:304`、`store.py:369-376`
- 建議的最小規則：D6「記錄」一段補一句：「衝突紀錄是 store 自己的一次完整提交（走第 7、8 步含 8.1），不受 `expected_revision` 約束，也不被其他 identity 的未解衝突擋下」；D6:229、D4:171 加上這個例外；D2:93 補「衝突紀錄已提交後重送 → exit 3」。
- 影響的 task：4.2（文件）

**DG-03**
- 嚴重度：minor
- 情境：`attempted` 時 A 的核對不過，D6 只說「整個解除被拒，什麼都不寫，人可以改選另外兩種」，沒定義 exit code、`result.error`（A 的錯誤原樣？包一層？），也沒明寫 K 仍未解；4.2、5.1、6.1 的測試表都沒有這個參數。4.2 就到得了：X = `budget_extension --target active:60` 已提交，重送 X、target `rounds:+2`——`invalid_target` 是 kind 自己的檢查，在衝突判定之後（D2 的順序），所以先記成衝突 K；對 K 選 `attempted` → 套用 A 時 `invalid_target`。5.1 的版本：approve_plan X 核准後重送 X 帶另一個 `--version` → K；`attempted` → `plan_version_mismatch`。
- 依據：`design.md:236`、`design.md:98-99`、`design.md:322`、`tasks.md:303`、`tasks.md:351`
- 建議的最小規則：D6:236 補「回 exit 1，`result.error` 為 A 的核對錯誤原樣（如 `invalid_target`、`already_approved`），不寫，K 仍未解」；在 4.2 或 5.1 的測試表加一個參數。
- 影響的 task：4.2／5.1

**DG-04**
- 嚴重度：minor
- 情境：X/a；X/b → Kb，`abandon`（a 標 `voided`，`voided_by = R1`）。依 D6:242 再送 X/c → Kc，C 是已 voided 的 a。對 Kc 選 `abandon` 或 `attempted` 時，D10 的撤銷規則只定義 in_effect → voided：已 voided 的 C 的 `voided_by` 是覆寫成 R2 還是保留 R1？`attempted` 時移入 `replaces` 的那份帶哪個值？C 本身已有 `replaces`（前一次 attempted 留下）時是巢狀還是攤平？（實作：覆寫、攤平。）
- 依據：`design.md:236-237`、`design.md:242`、`design.md:314`、`design.md:337`、`decisions.py:131-148`
- 建議的最小規則：D10 補「已 voided 的 decision 再被撤銷：`status` 不變，`voided_by` 記最後一次撤銷它的 decision（歷次可由 `conflicts[*].resolved_by` 回溯）；`replaces` 是攤平的清單，最新的在前」。
- 影響的 task：4.2（文件）；5.1、6.1 的清除規則不受影響（效果早已清掉）

**DG-05**
- 嚴重度：minor
- 情境：exit 3 的 envelope 形狀沒定完。D2 列出 `blocked` 欄位但沒像 `safety` 那樣說本 Feature 永遠 null；D6「`status`、`next` 回 exit 3，blockers 為…」沒說放在 `result.blockers`、`next.blockers` 還是 `blocked`；`ok` 的值；decide 記下新衝突（已提交新 revision）後的 exit 3，envelope 的 `revision` 是新值還是 null（實作：null）。`tasks.md:281` 只定義了 decide 的 `result`。
- 依據：`design.md:78`、`design.md:86`、`design.md:228`、`tasks.md:281`、`tasks.md:300`、`cli.py:101-107`、`cli.py:199-204`
- 建議的最小規則：D2 加「`blocked` 本 Feature 永遠 null」；D6:228 寫明 exit 3 時 `ok: false`，`result` 含 `error: transition_conflict`、`blockers`、`files`，`next` 照狀態；decide 的 exit 3 `revision` 擇一寫明（照現行為 null）。
- 影響的 task：4.2（文件）

**DG-06**
- 嚴重度：minor
- 情境：`choice_not_allowed` 在 D6 有兩條（C 是 `resolve_conflict` → 只收 `original`；A 是 `resolve_conflict` → 不收 `attempted`），D10 的 kind 表只列第一條。`tasks.md:304` 測的是第二條。
- 依據：`design.md:243`、`design.md:324`、`tasks.md:304`
- 建議的最小規則：D10 表的 `resolve_conflict` 列補上第二條。
- 影響的 task：4.2（文件）

**DG-07**
- 嚴重度：minor
- 情境：D1 說 cli 在邊界讀檔、存物件後才把 digest 傳入（`mutate` 是純函式，第 7 步又要求物件先存在），所以 5.1 的 `register` 必然在 `commit` 之前 `put_object`。非 owner 的 `register`（`tasks.md:345`「exit 4，bytes 不變」）或 Blocked 期間的 `register`（D6「其他寫入一律 exit 3，不寫」、`tasks.md:332`）都會先在 `objects/` 寫下物件再被拒。D4:204「不寫任何檔」沒說範圍是 run 目錄還是整個 `$LOOPCTL_HOME`（4.2 的測試寫「run 目錄的 bytes」，5.1 的只寫「bytes 不變」）。
- 依據：`design.md:38`、`design.md:46`、`design.md:187`、`design.md:204`、`design.md:229`、`tasks.md:319`、`tasks.md:332`、`tasks.md:345`
- 建議的最小規則：D4:204 與 D6:229 的「不寫」寫明指 run 目錄；content-addressed 物件可在授權前寫入，不算狀態寫入；`tasks.md:345` 的「bytes 不變」限定為 run 目錄。
- 影響的 task：5.1

**DG-08**（D6 之外，但在 D10；6.1 會碰到）
- 嚴重度：minor
- 情境：D10 的 `scope_change` 沒有有狀態的檢查，效果是「記錄 `supersedes`（plan 的 locator、version、digest）」。phase `planning`（`plan` 為 null）時直接送 `scope_change`，`supersedes` 未定義。經衝突的 `attempted` 到不了（C 提交時必有 plan，plan 不會變回 null），是直接送出的情況；`tasks.md:387` 只有「已核准、等待核准」兩個起點。
- 依據：`design.md:320`、`tasks.md:387`
- 建議的最小規則：D10 擇一：沒有 plan → exit 1（例如 `plan_not_registered`），或 `supersedes: null` 只記錄。
- 影響的 task：6.1

---

**已核對、沒有缺口的情境**（供對照）

- 衝突落在 `approve_plan`／`scope_change`／`policy_change`／`resolve_conflict` 本身：D6 三種選擇 × D10 撤銷規則都有定義，與 `tasks.md:351`、`389`、`392` 一致；`resolve_conflict` 永遠不會被 voided 或被 `replaces`（兩條 `choice_not_allowed` 把路封死）。
- 解除後重送：接受的內容 → duplicate；被否決的 → `transition_rejected`；其他 → 新衝突且 C 是當下接受的內容。「接受的內容」與「被否決的集合」永遠不相交（被否決後沒有任何路徑能再被接受），所以第 3 步三支沒有歧義。
- **無法解除的狀態**：找不到。任何衝突都可用 `original` 解除（只記錄、不會被拒），`resolve_conflict` 的 `--id` 由人給，撞到舊 id 只是多一個衝突；兩個 identity 各有未解衝突時 D4 第 4 步允許逐一解除。唯一卡死的路是 token 遺失，那是既有的 #34。
- **已撤銷的核准重新生效**：找不到。`original` 不動核准；`abandon` 只清；`attempted` 若套用 `approve_plan`，是 A 在撤銷後的狀態上重新通過 `already_approved`／未被取代／version 相符等檢查後**新建**的核准，不是還原——S 仍 in_effect 時會被 `plan_superseded` 擋下，別的 Y 已核准時會被 `already_approved` 擋下。
- 授權先於一切：非 owner 在 history 領先一版時也不能製造衝突（`tasks.md:301`(c)）；io_error 的提交邊界對 `resolve_conflict` 提交成立（已提交後重送 → duplicate）。

**實際讀過的檔案**

- `openspec/changes/run-decisions/design.md`（全文）
- `openspec/changes/run-decisions/tasks.md`（全文）
- `openspec/changes/run-decisions/specs/durable-delivery/spec.md`
- `openspec/changes/run-decisions/reviews/plan/README.md`、`round-10-review.md`、`round-11-review.md`、`round-12-review.md`、`round-13-review.md`
- `src/loopctl/store.py`、`src/loopctl/decisions.py`、`src/loopctl/next.py`、`src/loopctl/cli.py`（只用來確認設計的落點）

全程唯讀，沒有修改任何檔案。