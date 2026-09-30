# Design

## Context

- 動機與範圍見 [proposal.md](proposal.md)；要成立的行為見三份 spec delta（11 條 requirement、20 條 AC）。本文只寫怎麼做。
- 本 repo 的 main（`c91b774`）沒有任何 loopctl 程式、測試、CI 或 `pyproject.toml`，本 Feature 從零建立（[research](../../../docs/research/2026-09-30/run-decisions/research.md) §3.4）。
- 高層設計是 D45-04 revision-17（`docs/design-candidate/d45-04/`）加[勘誤](../../../docs/design-candidate/d45-04-errata.md) E-1～E-4。本 Feature 只取其中四塊：§2 的 CLI 與 envelope、§3 的狀態與持久化、§8 的政策檔與 `policy_change`，以及 §11 的測試政策。另外取 validation 的 §0 與 §6.1。刻意不同之處列在本文最後一節。
- 參考實作 `delivery/thin-controller@fcefecc` 證明了兩件事可行：store 契約（history-first、`flock`、revision 核對）與 CLI envelope。本 design 沿用這些介面的形狀；程式照 TDD 重做，舊測試與審查不算證據（D75）。
- 限制：
  - 單一主機、本機檔案系統；共享磁碟與多主機 writer 不宣稱支援（DUR-05）。
  - Python 3.12＋uv；本機 macOS，CI Linux。

## Goals / Non-Goals

**Goals:**

- 一個只用 stdlib 的 `loopctl` CLI。每次呼叫都是核對 → 更新 → 返回；不常駐，不開子程序，不啟動 agent（ORC-01）。
- 每個 repo＋feature 一份現行狀態：
  - 人可直接閱讀；
  - 只能經 controller 改變，手改可被偵測；
  - 中斷後只會讀到完整的舊版或新版。
- 決策紀錄層只收人工 decision。每筆記下決策者、來源、理由與影響；同一筆 decision 重送只生效一次。
- 本機與 `unit-linux` 跑同一個測試命令，讀同一份政策設定。

**Non-Goals**（design 層級；產品範圍的「不做」見 proposal）：

- 不預先建立後續 Feature 的狀態欄位（`attempts`、`writes`、`read_budget`、`findings`、`budget` 等）。各 Feature 加自己的頂層欄位，讀取時缺欄位視為空（見 D3）。
- 不解析 plan 的內容，task→AC 的核對在 Feature 2；也不解析 `workflow.yaml` 的結構，G3 在 Feature 3。
- token 遺失後，本 Feature 沒有收回協調權的方法（見 Risks）。
- 不支援 Windows，因為用 `fcntl.flock`。

## Decisions

### D1. 模組與相依方向

| 模組 | 責任 | 依賴 |
| --- | --- | --- |
| `cli.py` | 解析參數、輸出 envelope、決定 exit code；在邊界讀檔、存物件、取時間；把例外轉成輸出 | 其餘全部 |
| `store.py` | run 目錄、`load`／`create`／`commit`、transition 冪等與衝突、lock、不可信偵測與檔案清單、objects | `next`、`clock` |
| `state.py` | 新 run 的初始狀態、`status` 視圖與 `--human` 文字、token digest | — |
| `next.py` | `derive(state)`：從其餘欄位算出 `phase`、`blockers`、`next` | — |
| `decisions.py` | `register` 與 `decide` 的檢查與 mutate，都是純函式 | — |
| `clock.py` | 唯一的時鐘 `now()`（高層設計 tasks 通用規則） | — |
| `__main__.py` | `python -m loopctl` | `cli` |

- `decisions` 與 `next` 不讀檔、不看時鐘。檔案內容、物件 digest 與時間都在 `cli` 取得後傳入，所以同一請求的 payload 可以重現（D5）。
- 執行期零依賴。dev 依賴是 pytest、ruff、mypy，以及 CI 結構測試讀 YAML 用的 pyyaml。
- 參考實作把 pyyaml 列為執行依賴；本 Feature 不採用，因為產品程式不讀 YAML。

### D2. CLI 與 envelope

| 命令 | 參數 |
| --- | --- |
| `init` | `--repo R --feature F --issue I --actor A` |
| `claim` | `--repo R --feature F --actor A` |
| `status` | `--repo R --feature F [--human]` |
| `next` | `--repo R --feature F` |
| `register plan\|binding\|policy` | `--repo --feature --token --locator L --version V --source S [--content-from P] [--role spec\|ac\|design\|sa] [--producer implementer\|project_lead] [--calibrated-from C]` |
| `decide <kind>` | `--repo --feature --token --id --actor --target --reason --source --impact [--version V] [--choice C] [--open-question Q]…` |
| `adopt`、`delegate` | 接受任何參數，一律回 `unsupported` |

- `main(argv)` 解析參數後查 `cli.HANDLERS`（命令名 → `handler(args) -> (exit code, envelope)`），印出 envelope、回傳 exit code。這是 CLI 本來的派送結構；1.1 的骨架測試靠它驗證參數確實轉送。
- parser 強制的參數：
  - 每個命令的 `--repo`、`--feature`；
  - `init` 的 `--issue`、`--actor`，以及 `claim` 的 `--actor`；
  - `register` 的 `--locator`、`--version`、`--source`。
- `--token` 與 `decide` 的欄位在 parser 都是選填：缺 token 當作不符（exit 4）；欄位由 handler 核對。`binding` 缺 `--role`、`plan` 缺 `--producer` → exit 1 `missing_fields`。
- **parser 與 handler 的分工**，每種錯誤只由一方處理：

  | 輸入 | 誰處理 | 結果 |
  | --- | --- | --- |
  | 未知的頂層命令（例如 `merge`）、缺少必填參數、`--repo`／`--feature` 格式不符 | parser | exit 2，`result.error == "usage"` |
  | `register` 的種類不是 `plan\|binding\|policy`；`--role`、`--producer` 不在選項內 | parser | exit 2 `usage` |
  | 頂層 `adopt`、`delegate`（parser 認得，接受任何參數） | handler | exit 2，`result == {error: "unsupported", command: <名稱>}` |
  | `decide` 的 kind（parser 當自由字串）不在本 Feature 的集合 | handler | exit 2，`result == {error: "unsupported", kind: <值>}` |
  | `decide --choice` 不是 `original\|attempted\|abandon` | handler | exit 1 `invalid_choice` |

- stdout 永遠是一行 JSON，欄位為 `ok`、`revision`、`result`、`blocked`、`next`、`safety`。`safety` 在本 Feature 永遠是 `null`，保留欄位讓 envelope 形狀不變。
- Exit code：

  | code | 意義 |
  | --- | --- |
  | 0 | 成功 |
  | 1 | 拒絕 |
  | 2 | 用法錯誤，或 `unsupported` |
  | 3 | Blocked（有未解的 transition 衝突） |
  | 4 | `not_owner` |
  | 5 | 狀態不可信 |

- argparse 的錯誤不走 `SystemExit`：一律轉成 exit 2 的 envelope，`result.error` 為 `usage`，`result.message` 指出參數。`--help` 例外，exit 0 並印出 usage。
- `--repo` 必須是 `owner/name`，`--feature` 必須是單一路徑段；兩段都以英數字開頭，只含 `[A-Za-z0-9._-]`。parser 核對格式，不合格回 exit 2，所以任何輸入都跳不出 `$LOOPCTL_HOME`。
- `decide` 的核對順序：
  1. 無狀態的核對，依序：kind 不在本 Feature 的集合 → exit 2 `unsupported`，不讀也不寫狀態；缺欄位 → exit 1，`result == {error: "missing_fields", fields: [...]}`；actor 不符合 `human:<name>` → exit 1 `actor_not_human`。
  2. 在 lock 內、對最新狀態，依 D4 的順序：run 存在 → token（授權先於任何冪等、衝突處理或寫入）→ transition 的冪等與衝突 → 該 kind 自己的檢查 → 效果。
- 參考實作以 `--feature` 為唯一鍵，而且 `status` 可以不帶參數；本 Feature 不採用，因為 DUR-01 與 DUR-02 以 repo＋feature 為單位。

### D3. 狀態佈局與欄位

```
$LOOPCTL_HOME/                        預設 ~/.loopctl
  runs/<owner>/<name>/<feature>/
    feature.json                      唯一現行狀態（鍵排序、縮排的 JSON）
    history/<rev>.json                write-once 紀錄（欄位見下）
    lock                              commit 用的 flock
    .tmp-*                            中斷留下的未完成寫入，只作診斷
  objects/<sha256 hex>                登記內容，content-addressed
```

- history 紀錄的欄位：`revision`、`transition_id`、`payload_digest`、`prev_digest`、`state_digest`、`committed_at`、`state`。
- `feature.json` 的頂層欄位：

| 欄位 | 內容 | 寫入者 |
| --- | --- | --- |
| `schema_version`、`revision`、`transitions` | `1`；目前 revision；`transition_id → {revision, payload_digest}` | store |
| `repo`、`feature`、`issue` | `init` 的參數 | `init` |
| `coordinator` | `{actor, at}`：直接交付時接下 feature 的協調者 identity（AC-O01）。只是紀錄，不授予協調權，也不授予任何決策權 | `init` |
| `owner` | `null` 或 `{actor, token_digest, claimed_at}`：協調權，靠 token 證明 | `claim` |
| `plan` | `null` 或登記項（D9），另有 `producer`、`calibrated_from`、`superseded_by` | `register plan`、`scope_change` |
| `versions` | `{bindings: {spec\|ac\|design\|sa: {<locator>: 登記項}}, policy: 登記項 \| null}` | `register` |
| `approval` | `null` 或 `{decision, actor, at, plan: {locator, version, digest}, bindings: {role: {locator: digest}}}` | `approve_plan`、`scope_change` |
| `policy_approval` | `null` 或 `{decision, locator, digest}` | `policy_change` |
| `gates` | `g1`、`g2`、`g3` 各為 `{status: "not_evaluated", reasons: ["not_started"]}` | `init`（本 Feature 不改） |
| `decisions` | `id → 紀錄`（D10）；紀錄帶 `status`（`in_effect` 或 `voided`） | `decide` |
| `conflicts` | `cid → {transition_id, committed_revision, committed_payload, attempted_payload, detected_at, resolved_by, choice}` | store |
| `phase`、`blockers`、`next` | 衍生欄位（D7） | store 每次提交時重算 |

- 狀態檔只含 token 的 digest。明文 token 只在 `claim` 的輸出出現一次。
- 後續 Feature 可以新增自己的頂層欄位，讀取時缺欄位視為空。`schema_version` 只在不相容的改動時遞增。

### D4. Store 契約

| 函式 | 行為 |
| --- | --- |
| `load(key) -> (revision, state)` | 見下方「讀取」 |
| `create(key, transition_id, payload, state) -> 1` | 在旁邊建好目錄，再 `os.rename` 到位；run 目錄已存在時不覆寫 |
| `commit(key, expected_revision, transition_id, payload, mutate, *, authorize, resolves=None) -> revision` | 見下方「提交」 |
| `put_object(bytes) -> digest`、`get_object(digest) -> bytes` | content-addressed；讀取時核對 digest |

**讀取**：run 目錄不存在 → `RunNotFound`。其餘情況回傳 `(revision, state)`，或拋出 `UntrustedState(reason, files)`：

| 情況 | 結果 |
| --- | --- |
| `feature.json` 不存在（包括空目錄） | `state_missing` |
| JSON 無法解析，或不是物件 | `state_corrupt` |
| `schema_version` 不是 1 | `unknown_schema:<v>` |
| 現行 revision 的 history 紀錄不存在 | `history_missing:<rev>` |
| history 紀錄的 `state_digest` 不等於 `feature.json` 的 digest，或紀錄本身的 state 與它的 digest 不符 | `manual_edit` |
| 下一版的 history 紀錄存在，而且它的 `prev_digest` 等於 `feature.json` 的 digest | 回傳那一版（已提交、但現行檔還沒替換）。讀取不寫檔；下一次成功的提交寫入更新的一版時，自然取代落後的 `feature.json` |
| 下一版的 history 紀錄存在，但 `prev_digest` 對不上 | `history_fork:<rev>` |

`files` 是 run 目錄下現存檔案的相對路徑，排序後輸出。

**提交**（在 run 的 `flock` 內依序；第 8 步之前任何一步失敗，都不寫任何檔）：

1. 讀取（不寫）。
2. **授權**：`authorize(state)`。`register`、`decide` 以它核對 `--token` 與 `owner.token_digest`，不符或缺少 → `NotOwner`（exit 4）。`claim` 傳入不檢查的 `authorize`，它自己的檢查（還沒有 owner）在 `mutate` 裡。授權先於冪等、衝突與任何寫入，所以非 owner 不能靠重送取得 duplicate 回應，也不能製造衝突。
3. **transition 已提交過**，比對 payload digest：
   - 等於目前接受的內容 → 回傳原 revision；
   - 等於某個已解除衝突中被否決的內容 → `TransitionRejected(cid)`（exit 1）；
   - 其他 → 依 D6 記下衝突，然後拋出 `TransitionConflict(cid)`。
4. 有未解的衝突，而且 `resolves` 不是其中一個 → `TransitionConflict`。
5. 目前 revision 不等於 `expected_revision` → `RevisionConflict`。
6. `new = derive(mutate(state))`。
   - `mutate` 可以拋出 `decisions.Rejected`。
   - store 自己寫的欄位（D6 的衝突紀錄、`resolves` 的解除紀錄）在 `derive` 之前寫入，所以 blockers 與 next 一併反映。
   - `new` 與現況相同 → 回傳現行 revision（no-op）。
7. **物件引用**：`new` 裡每個 `{"$object": d}`，不論是這次新增的還是早就存在的，對應的物件都必須存在，而且內容的 digest 等於 `d`；否則 → `UntrustedState("object_missing:<d>" 或 "object_corrupt:<d>", files)`（exit 5）。登記項的 `digest` 是一般的 `sha256:` 字串，不是引用（高層設計 s6）。
8. **寫入**：
   1. 補上 bookkeeping；
   2. 把 history 紀錄寫到暫存檔並 fsync；
   3. 以 `os.link` write-once 連到 `history/<rev+1>.json`，再 fsync 目錄；
   4. 把 `feature.json` 的新內容寫到暫存檔並 fsync，以 `os.replace` 原子替換，再 fsync 目錄；
   5. darwin 對檔案另加 `F_FULLFSYNC`。

   任何 `OSError` 都往上拋。在 `os.link` 之前失敗 → 沒有提交。

呼叫端的規則：

- `cli` 的寫入命令在 `mutate` 內對最新狀態重做全部有狀態的檢查。遇到 `RevisionConflict` 時重讀、重做，所以不會有改動在舊版本上核對過就提交。
- 「已提交」的定義是 `history/<rev>.json` 存在。中斷在 `os.link` 之前 → 讀到舊版；中斷在 `os.link` 之後 → 讀到新版。crash 測試的接縫就是這兩個函式（D13）。
- 讀取與被拒的命令都不寫任何檔，包括落後的 `feature.json`。

### D5. Transition identity 與冪等

| 命令 | `transition_id` | 重送 |
| --- | --- | --- |
| `init` | 只走 `create`，不經 commit | run 已存在 → exit 1 `run_exists`，不覆寫 |
| `claim` | `claim:<token digest>`，每次呼叫都不同 | 已有 owner → exit 1 `already_claimed`，附目前 owner |
| `register` | `register:<rev>:<登記項 digest>` | 內容與現有登記相同 → no-op，revision 不變 |
| `decide` | `decide:<id>` | 等於接受的內容 → exit 0、`duplicate: true`、revision 不變；其他內容 → 衝突，或在衝突解除後回 `transition_rejected`（D6） |

- payload 是請求欄位的正規化 JSON，不含時間與 token。
- 參考實作的冪等是「重跑 mutate，比對整份 state」。decision 紀錄帶有時間，重送必然不同，所以參考實作只好在 CLI 預先攔下 id 重複，而且只回拒絕（exit 1）。改比 payload 後，冪等與衝突都由 store 判定，也符合 DUR-05「內容不同時 Blocked」。
- `register` 的 id 帶 revision，所以 A → B → A 會真的換回 A。`decide` 的 id 由呼叫者給，跨 revision 穩定。

### D6. Transition 衝突與解除（待決項之二）

本 Feature 只有 `decide:<id>` 會衝突，因為 `claim` 與 `register` 的 transition id 每次都不同（D5）。以下以 C 表示已提交的內容，A 表示這次嘗試的內容。

- **記錄**：第一次發現某個衝突時（已通過授權），store 用 transition `conflict:<cid>` 提交一個新 revision，寫入 `conflicts[cid]`：
  - 內容是 `transition_id`、已提交的 revision、C 與 A 兩份完整 payload、偵測時間；
  - `cid` 取 `sha256(transition_id + A 的 digest)` 的前 16 個 hex，所以同樣的嘗試再來一次會對到同一個衝突，不產生新 revision。
- **未解期間**：
  - `status`、`next` 回 exit 3，blockers 為 `transition_conflict:<cid>`，`decision_kinds` 為 `[resolve_conflict]`；
  - 其他寫入一律 exit 3，不寫；
  - owner 重送 C，仍回原 revision（D4 第 3 步在第 4 步之前）。
- **解除用新的 kind**：`resolve_conflict --target <cid> --choice original|attempted|abandon`，只收人工 decision，以 `resolves=<cid>` 提交。三種選擇都在同一個 revision 記下 `resolved_by` 與 `choice`：

  | 選擇 | 效果 | 之後 C 的 identity 接受的內容 |
  | --- | --- | --- |
  | `original` | C 照常有效；A 只留作診斷 | C |
  | `attempted` | 依 D10 撤銷 C，再把 A 當成同一個 id 的 decision，在撤銷後的狀態上照常核對並生效。`decisions[id]` 變成 A 的紀錄，C 移到它的 `replaces`，標 `voided_by`。A 的核對不過 → 整個解除被拒，什麼都不寫，人可以改選另外兩種 | A |
  | `abandon` | 依 D10 撤銷 C：`decisions[id].status = voided`，保留內容；A 不生效 | C（已撤銷） |

  - 兩份內容都一直保留在 `conflicts[cid]`。
  - 解除後，重送接受的內容 → `duplicate`；`abandon` 時回傳的紀錄顯示 `voided`。
  - 重送被否決的內容 → exit 1 `transition_rejected:<cid>`，不再 Blocked。
  - 送第三種內容 → 新的衝突。
  - 被衝突的 decision 本身是 `resolve_conflict` 時，只能選 `original`（`choice_not_allowed`），因為撤銷一次解除沒有定義。
  - `cid` 不存在或已解除 → exit 1 `unknown_target`。
- 為什麼不沿用 `revise`：
  - `revise` 在 Feature 3、4 會有效果（整合觸發、開修正批次）；用它解除衝突，會在解除時意外觸發那些效果；
  - 兩者的目標也不同：`revise` 指向 feature 的內容，解除指向一個 `cid`。
  - `resolve_*` 的命名也與高層設計的 `resolve_read`、`resolve_operation`、`resolve_finding` 一致。

### D7. 衍生欄位：`phase`、`blockers`、`next`

`next.derive(state)` 是純函式；store 在每次提交前呼叫它。所以狀態檔裡的衍生欄位永遠等於由其餘欄位算出的值；手改衍生欄位也會被 digest 偵測（D4）。

- `phase`：
  - 有 `approval` → `approved`；
  - 否則，有 `plan` → `awaiting_approval`；
  - 否則 → `planning`。
- `next`：依序取第一個成立的：

| 條件 | `next` |
| --- | --- |
| 有未解的衝突 | `human`；blockers 為每個 `transition_conflict:<cid>`；kinds `[resolve_conflict]` |
| 沒有 owner | `human`；`[unclaimed]` |
| 有 `approval` | `dispatch`（D8） |
| 沒有 `plan` | `human`；`[plan_not_registered]` |
| plan 有任何阻擋 | `human`；列出全部阻擋，kinds `[]`。阻擋有三種：`plan_superseded:<id>`；`plan_not_calibrated`（producer 不是 implementer，或沒有 `calibrated_from`）；`missing_binding:<role>`（spec、ac、design 各一） |
| 其他 | `human`；`[plan_not_approved]`；kinds `[approve_plan]` |

- `blockers`：`next.action` 為 `human` 時等於它的 blockers，否則為 `[]`。
- 本 Feature 的 `next` 只由狀態決定，所以存下的值與 `status` 重算的一致。`policy` 的狀態在讀取時計算（D11），不影響 `next`。

### D8. 核准後的 `next`（待決項之一）

```json
{"action": "dispatch", "plan": {"locator": "…", "version": "…", "digest": "sha256:…"}, "approval": "<approve_plan decision id>"}
```

- 核准後的下一步就是派出第一個 task，這個動作名稱照實回報。`plan` 與 `approval` 讓讀者不必再查狀態，就知道要派的是哪一版。
- 高層設計的動作詞彙是封閉的：orchestrate 遇到未列的動作一律停下交人。所以 Feature 2 之前，任何讀 `next` 的程式都會停在這裡，不會自行派工。
- Feature 2 以 MODIFIED 決定 `dispatch` 如何接到實際的派工動作。
- 否決的做法：`human` 加上 `dispatch_unavailable`。沒有待人決定的事，卻回報成 `human`，會把「已核准」誤報成「等人」；而且 `decision_kinds` 是空的，讀者看不出為什麼停。

### D9. 登記原生文件

- 登記項的欄位：
  - `locator`：原樣保存；
  - `path`：locator 是本機檔案時，保存解析後的絕對路徑；
  - `version`、`source`；
  - `digest`：內容的 `sha256:`；
  - `content`：`{"$object": digest}`；
  - `registered_at`。
- 內容的來源：
  - locator 是可讀的一般檔案時，讀它；
  - 否則讀 `--content-from`，例如以 `gh issue view --json body` 匯出的 issue 內文；
  - 兩者都讀不到 → exit 1 `locator_unreadable`，狀態不變；
  - `policy` 必須是本機檔案，因為 `status` 要重讀它（D11）。
- binding 以 `role` 與 `locator` 為鍵。一個角色可以有多份文件，例如三份 spec delta。
- 只有一份現行 `plan`，新登記取代舊的（ORC-11）。Project Lead 的草案可以登記，但不能批准（D7 的 `plan_not_calibrated`）。
- 已核准時：
  - 登記會改變 plan 或 spec、ac、design binding 的內容 → exit 1 `scope_change_required`，狀態不變；
  - 內容相同的重登是 no-op；
  - `sa` binding 與 `policy` 不受核准涵蓋，照常登記。
- `scope_change` 之後，重登已被取代的 plan（`version` 與 `digest` 都等於某筆 `scope_change` 的 `supersedes`）→ exit 1 `plan_superseded`。

### D10. 決策種類與紀錄

- 每筆紀錄的欄位：
  - `id`、`kind`、`actor`、`target`、`reason`、`source`、`impact`；
  - `version`（有才記）、`choice`（只有 `resolve_conflict`）、`open_questions`（只有 `scope_change`）；
  - `at`、`seq`；
  - `status`（`in_effect` 或 `voided`）、`voided_by`、`replaces`（D6）；
  - `effect`（見下方的撤銷規則）。
- 必填：`id`、`actor`、`target`、`reason`、`source`、`impact`。另外 `approve_plan` 與 `policy_change` 需要 `version`，`resolve_conflict` 需要 `choice`。

| kind | 有狀態的檢查 | 效果 |
| --- | --- | --- |
| `approve_plan` | 依序：phase 不是 `approved`（`already_approved`）、有 plan、plan 已校準、未被取代、`target`／`version` 等於 plan 的 locator 與 version、spec、ac、design 都至少各有一份 binding（缺的全部列出，`missing_bindings`） | `approval` 釘住 plan 與 binding digest；phase 轉為 `approved` |
| `scope_change` | — | 記錄 `supersedes`（plan 的 locator、version、digest）與 `open_questions`；`plan.superseded_by = id`；`approval = null` |
| `policy_change` | 已登記 policy（`policy_not_registered`）；`target`／`version` 等於它的 locator 與 digest（`policy_digest_mismatch`） | `policy_approval` |
| `budget_extension` | `target` 必須符合 `active:<正整數分鐘>`、`rounds:+1`、`attempts:<unit>:+1`、`ci_wait:<40 hex>` 之一（`invalid_target`） | 只記錄；效果屬 Feature 2～4 |
| `revise`、`handoff` | — | 只記錄 |
| `resolve_conflict` | `target` 是未解的 `cid`（`unknown_target`）；`choice` 是三者之一（`invalid_choice`）；被衝突的是 `resolve_conflict` 時只收 `original`（`choice_not_allowed`） | D6 |

- **撤銷規則**（D6 的 `attempted` 與 `abandon` 使用）：
  - 每筆 decision 記下 `effect`：它改變的頂層欄位（`approval`、`policy_approval`、`plan`）各自的 `before` 與 `after`。只記錄的 kind 沒有 `effect`。
  - 撤銷時，只有這些欄位目前的值全部仍等於各自的 `after`，才全部還原成 `before`。只要有一欄已被之後的 transition 改寫 → exit 1 `effect_overwritten`，列出欄位，什麼都不寫；人可以改選 `original`。
  - 被撤銷的 decision 留在 `decisions`，標 `status: voided` 與 `voided_by`。後續 Feature 讀 decision 時略過 `voided` 的紀錄。
  - `approve_plan` 的 `already_approved` 看的是目前的 `approval`，所以撤銷一筆核准之後，可以用新的 id 再批准。
- 其他 kind（包括 `adopt`、`delegate`、`accept`、`return`、`resolve_read`、`resolve_operation`、三種 finding kind）與頂層的 `adopt`、`delegate` 一律 exit 2 `unsupported`，狀態不讀不寫。

### D11. `status` 視圖

狀態檔與 `status` 是同一份狀態的兩種投影。測試分別斷言兩者，不要求它們逐欄相等。

| `status` 的 `result` 欄位 | 由狀態檔怎麼投影 |
| --- | --- |
| `repo`、`feature`、`issue`、`phase`、`coordinator`、`plan`、`gates`、`blockers`、`decisions`、`conflicts` | 原樣 |
| `revision` | 原樣 |
| `owner` | `{actor, claimed_at}`，去掉 `token_digest` |
| `bindings` | `versions.bindings` 原樣 |
| `approval` | 狀態檔為 `null` 時是 `{status: "not_approved", plan_version: <plan.version 或 null>}`；否則是 `{status: "approved", decision, actor, at, plan, bindings}` |
| `policy` | 讀取時計算（見下表），另帶登記項與 `policy_approval` |
| `transitions` | 不顯示 |

- 狀態檔裡的 `next` 原樣放在 envelope 的 `next`。
- `--human` 另加 `result.human`，是同一份內容的逐行文字。
- `policy` 在讀取時計算，唯讀地重讀登記的 `path`：

| 狀態 | 條件 |
| --- | --- |
| `not_registered` | 沒有登記 policy |
| `unreadable` | 登記的檔案讀不到 |
| `not_approved` | 沒有 `policy_approval`，或它的 digest 不等於登記的 digest |
| `digest_mismatch` | 檔案目前的 digest 不等於核准時的 digest（帶出兩個 digest） |
| `approved` | 其餘情況 |

- 狀態不可信時，所有命令都回 exit 5，`result` 為 `{error: untrusted_state, reason, files}`，不讀也不改任何其他東西。

### D12. 測試政策、CI 與政策檔

- 測試政策（GAT-06、validation §0）：
  - `pyproject.toml` 的 `[tool.pytest.ini_options]`：`--strict-markers`、`xfail_strict = true`、`testpaths = ["tests"]`、`only_on` marker。
  - `tests/conftest.py`：以唯一的平台函式 `current_platform()` 決定 `only_on(<platform>)` 是否 skip。session 結束時，以下任一都讓 session 失敗：收集數為 0（pytest 本身的 exit 5 不被改寫）、任何不是 `only_on` 在非所屬平台產生的 skip、xfail、xpass，以及 `LOOPCTL_EXPECT_PLATFORM` 與實際平台不符。
  - 本機與 CI 都只執行 `uv run pytest`，不加旗標。
- `.github/workflows/loopctl-ci.yml` 依 validation §6.1，只有 `unit-linux`：
  - 觸發：只有 `pull_request`（opened、synchronize、reopened；`branches: [main]`）；`permissions: contents: read`；`ubuntu-24.04`，`timeout-minutes: 15`。
  - 步驟依序：checkout PR head SHA → 核對 `git rev-parse HEAD` → 在測試前上傳 `tested-sha-<job>-<run_attempt>` → 安裝釘版的 uv 與 Python 3.12 → `uv sync --frozen` → `uv run pytest`（`LOOPCTL_EXPECT_PLATFORM=linux`）→ `uv run ruff check .` → `uv run mypy src` → `scripts/dist-smoke.sh`。
  - 每個 `uses:` 都釘到完整 commit SHA。沒有 commit-msg 步驟。
- `workflow.yaml`（repo 根目錄，loopctl 的政策檔，不是 GitHub workflow）：

  ```yaml
  schema_version: 1
  repo: yschiang/loop-engineering
  g3:
    required_checks:
      - {name: unit-linux, app: github-actions, workflow: .github/workflows/loopctl-ci.yml}
  ```

  - 沿用高層設計的 `g3` 巢狀結構，Feature 3 可以在同一段加鍵；每次改動都需要新的 `policy_change`。
- 對本 repo 這份檔案的實際 `policy_change`，由 Project Lead 在驗收示範中記錄（tasks「驗收驗證」）。
- `scripts/dist-smoke.sh`：`uv build` 出 wheel，安裝到全新 venv，然後在 checkout 外做三項具名檢查。任一項失敗就印出 `dist-smoke: FAIL: <檢查名>` 並 exit 1：
  1. `help`：`loopctl --help` exit 0，而且輸出含 `usage: loopctl`；
  2. `envelope`：`loopctl status --repo a/b --feature F-1` 的 stdout 恰為一行 JSON，鍵恰為六個 envelope 欄位；
  3. `isolation`：`import delivery` 失敗（D46 的隔離）。

  不檢查 `loopctl.tools`，那屬於 Feature 2。

### D13. 測試接縫

- **in-process**：fixture `cli(*argv)` 呼叫 `loopctl.cli.main(argv)`，回傳 `Result(code, out, stdout, stderr, exc)`：
  - `out` 是解析後的 envelope；
  - 未攔截的例外記在 `exc`，此時 `code` 為 `None`；`SystemExit` 記成對應的 code，stdout 保持原樣。這樣程式崩潰的 Red 也會停在第一個斷言上，而不是停在呼叫。
  - 巢狀欄位用不會拋例外的取值方式讀，缺值時得到 `None`，比較失敗才會是 AssertionError。
- **派送**：以 `monkeypatch.setitem(cli.HANDLERS, <命令>, <記錄用的假 handler>)` 驗證參數轉送與輸出契約（1.1）。
- **子程序**：fixture `cli_proc(*argv, prelude="")` 以 `python -m loopctl` 執行，`prelude` 在載入 loopctl 前執行；`cli_proc_many(n, *argv, prelude="")` 讓 n 個子程序都就緒後，才建立 barrier 檔讓它們一起開始。
  - crash 測試用 prelude 把 `os.link` 或 `os.replace` 換成 `os._exit(9)`；
  - sync 失敗測試把 `os.fsync` 換成拋出 `OSError(EIO)`；
  - 並行測試把 `os.link` 包成先睡 0.2 秒再呼叫原函式，讓所有程序都先讀到同一版狀態。
  - 1.1 以自測驗證 prelude 先於 loopctl 執行、barrier 讓程序一起開始。
- **隔離**：autouse fixture 把 `LOOPCTL_HOME` 設到 `tmp_path`。這是產品本來就有的設定，不是測試旗標。
- **時間**：以 `monkeypatch` 替換 `loopctl.clock.now`。
- **文件**：fixture `repo` 在 `tmp_path` 建好範例 plan、草案、spec（兩份）、ac、design、sa、匯出的 issue 內文與 `workflow.yaml`。
- 產品不為測試加任何旗標、hook 或環境變數。

### D14. PR 與規模

- 只影響 `yschiang/loop-engineering`，一個 PR（D61），base `main@c91b774`。
- 估計程式約 800–1,000 行，測試約 1,500 行。PR 依 task 的 commit 分段，可以審查。
- 骨架與 CI（tasks 1.1、2.1）能單獨驗收 AC-G21。roadmap（D75）把它們放在本 Feature；PR 仍可審，所以不提議拆分。Project Lead 若要拆，1.1＋2.1 可以成為獨立 Feature，其餘 task 不需要改。

### 與高層設計刻意不同之處

| 高層設計 | 本 Feature | 依據 |
| --- | --- | --- |
| `features/<id>/`，以 feature id 為鍵；`status`／`next` 不帶參數 | `runs/<owner>/<name>/<feature>/`；每個命令都帶 `--repo --feature` | DUR-01、DUR-02 的 repo＋feature |
| `init --repo --repo-id --feature --issue`；只有 `claim` 記下 actor | 不收 `--repo-id`（Feature 3 讀 GitHub 時再加 repo identity）；加 `--actor`，保存協調者 identity，與 `claim` 的協調權分開 | 本 Feature 不讀 GitHub，無法核對；AC-O01 |
| 13 種 `decide` | 6 種加 `resolve_conflict`，其餘回 `unsupported` | proposal「對象存在才收」；D6 |
| `approve_plan` 只看 producer 與校準 | 另外要求 spec、ac、design binding | #6、AC-O29 |
| binding 改變使核准失效（design §8 版本表） | 已核准時拒絕，要先 `scope_change` | ORC-03「經 `scope_change`」 |
| decision 沒有來源與影響欄 | 有 `source`、`impact`，`scope_change` 另有 `open_questions` | DUR-01、AC-O23 |
| `status` 不含版本與核准；不可信時只給原因 | 含 plan／spec／design 版本、核准、policy；不可信時列出檔案 | DUR-01、AC-D11 |
| 衝突放在旁邊的 `conflicts/` 目錄，沒有解除方法；token 在 mutate 裡核對 | 衝突記在現行狀態，以 `resolve_conflict` 選定原內容、改採嘗試的內容或放棄；授權先於冪等與衝突 | DUR-05、AC-D10、AC-D03 |
| 以重跑 mutate 判定冪等 | 比對 payload digest | D5 |
| 動作詞彙 8 個 | 加 `dispatch` | D8 |
| 可只給 `--digest` 登記 | 必須讀得到內容；非檔案 locator 用 `--content-from` | ORC-02「讀不到的文件 SHALL 拒絕登記」 |
| 完整的 `workflow.yaml`；兩個 CI job；CI 有 commit-msg；dist-smoke 檢查 `loopctl.tools`；pyyaml 為執行依賴 | 只宣告 `unit-linux`；一個 job；沒有 commit-msg；不檢查 `loopctl.tools`；pyyaml 只在 dev | proposal 範圍；D53；validation §6.1、§6.3 |
| gate 以 `pending` 加原因 `not_evaluated` 表示 | `status: not_evaluated`，原因 `not_started` | AC-D01「標明未評估」 |

## Risks / Trade-offs

- [token 遺失：協調者 session 消失，沒有人能再寫入這個 run] → 本 Feature 的 spec 沒有收回協調權的機制，`handoff` 只記錄。`status` 仍可讀。收回方法需要 spec 決定，是交給 Project Lead 的問題。
- [actor 是自己聲明的：agent 可以打 `--actor human:x`] → 依 D50 的「可信本機協作」，controller 只核對格式。每筆決策都留下 history，可以稽核。真正的身分驗證不在範圍內。
- [`flock` 只保護單一主機] → DUR-05 已排除共享磁碟與多主機。
- [crash 測試只殺程序，沒有模擬斷電] → 測試能證明的有兩件：`os.link`／`os.replace` 前後中斷的恢復，以及 fsync 失敗時不提交（3.1）。以下都沒有測試證據，在 validation 的限制中註明：fsync 是否真的把資料寫到裝置、darwin 的 `F_FULLFSYNC` 是否被呼叫、斷電後的持久性。
- [並行測試依排程而定] → 用 8 個程序加 barrier。斷言「恰一個成功」與排程無關；若出現 flaky，追根因，不加 retry。
- [存下的 `next` 在後續 Feature 可能依賴時間或外部讀取] → 本 Feature 的 `next` 只依狀態，所以一致。之後加入時間或外部輸入的 Feature 要在自己的 design 重新界定。
- [`unit-linux` 第一次實際執行在 PR 開出時] → 2.1 在本機檢查結構；runner label 依當時的 GitHub 文件核對；PR 上的失敗走 to-pr 的修正迴圈。
- [dist-smoke 第一次 `uv build` 可能要下載 `uv_build`] → CI 有網路；本機第一次也需要網路，之後有快取。
- [decide 的欄位多，人工輸入繁瑣] → 換到的是每筆決策都可稽核（DUR-01）；呼叫由協調者代打，人只提供內容。

## Migration Plan

- 新建，沒有既有狀態或程式需要遷移；`schema_version` 從 1 開始。
- 部署方式是合併 PR。回滾就是 revert 該 PR；使用者的 `$LOOPCTL_HOME` 不受影響。
