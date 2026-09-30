# AGENTS.md — 所有 agent 的共同規則

適用於在本 repo 寫碼、審查或跑 Loop Engineering 流程的每個 agent（Claude、Codex、OpenCode 等），以及它們派出的 subagent。流程 skills（`feature-to-spec`、`spec-to-plan`、`plan-to-code`、`to-pr`、`project-lead`）開始前都會先讀本檔；本檔與 skill 衝突時，以本檔為準。

本檔以 `templates/AGENTS.md`（`setup.sh --project` 放進產品 repo 的範本）為底，補上本 repo 的 scope 與 commit 檢查。改範本的通用規則時，兩份一起改。

## 不做 temp fix

目標是每個修改都是完整、可長期維護的解法。以下四類一律不做；真的無法避免時，走本節最後的「例外」程序，不要默默留在程式裡。

### 1. 不為測試改 production 程式

- 不加只給測試呼叫的方法、建構子、hook 或 accessor。
- 不加只給測試用的設定開關，例如「關掉背景排程」、「縮短重試間隔」這類專為測試存在的屬性。
- 測試改用這些方式：
  - 透過公開行為與可觀察的結果（資料列、檔案、指標、回傳值）斷言。
  - 用設計本來就有的注入點替換依賴，例如時鐘、外部系統的介面、資料來源。
  - 時序與故障用 test sources 裡的包裝器控制。
- 如果不加 hook 就測不到某個行為，先檢討設計：通常代表缺一個正式的注入點，應該把它做成正式設計的一部分，而不是測試後門。

### 2. 不在程式裡留「以後再改」

- 不寫 `TODO`、`FIXME`、`HACK`、`XXX`，也不寫「暫時」「先這樣」「之後再補」「真的遇到再改」這類承諾式註解。
- 要嘛現在就做對；要嘛確定超出本票範圍，那就依事項交給對應的流程：
  - 範圍外的問題：開 issue 追蹤，連回原本的 ticket；
  - 需求或範圍要改：交給人決定，由 `feature-to-spec` 修改 spec；
  - 偏離設計：寫進決策紀錄。
- 程式註解只寫「為什麼現在這樣是對的」：不變式、前提、設計依據。不寫「目前不夠好、將來要改」。

### 3. 修根因，不修症狀

- 不只修 ticket 提到的那一條路徑。先找出所有經過同一機制的呼叫端，在擁有這個不變式的那一層修一次。
- 不吞例外、不在呼叫端加特判繞過問題、不把錯誤降級成 log 了事。
- 測試失敗時不做這些事：放寬斷言、把期望值改成目前的錯誤輸出、加 `sleep` 或 retry 讓它剛好通過、標成 skip／disabled、把 flaky 測試排除。
- flaky 測試要找出根因。找不到時保留嚴格斷言，並把重現次數與已排除的原因寫進報告。

### 4. 不為本機環境繞路

- 本機工具鏈的問題（例如版本與某個測試依賴不相容）不改 production 行為，也不降級測試來迴避。
- 環境限制寫進 PR 與 ticket 的說明，由人決定是否調整環境或依賴版本。

### 例外

真的只能用上述做法時：

1. 在 PR 說明列為「例外」，寫出理由與替代方案為何不可行；
2. 開 issue 追蹤移除；
3. 程式裡只留一行事實陳述，並附 issue 編號，不寫承諾。

沒有走這三步的 temp fix，審查時視為阻擋項。

## Commit 訊息

`scripts/hooks/commit-msg` 依本節檢查。每個 clone 執行一次 `git config core.hooksPath scripts/hooks` 啟用（各 worktree 共用）；也可以用 `scripts/hooks/commit-msg --range <base>..<head>` 檢查一段範圍。不用 `--no-verify` 繞過。

本節約束的是含有「新增 `scripts/hooks/commit-msg`」那個 commit 的 commit。更早的 commit 維持原訊息、不改寫：它們的 SHA 可能綁著證據（Red／Green、receipt）。舊分支合入該 commit 後，之後的新 commit 才受檢。

### 粒度

- 一個 commit 只做一件邏輯變更；每個 commit 自身 build 與測試全綠，`git bisect` 才可用。
- 先整理結構再改行為時，結構調整另成 `refactor` commit，放在行為變更之前。
- 隨程式一起變的文件與程式放同一個 commit。

### 格式

```
<type>(<scope>)!: <description>

Why: <為什麼要改>

Behavior: <套用後什麼成立>

Tradeoff: <選填>

BREAKING-CHANGE: <不相容之處與遷移方式>
Refs: #<ticket>
```

- 全部用英文。
- Subject 用祈使句（`add`、`keep`、`reject`），不超過 72 字元，結尾不加句號。
- Body 每行不超過 72 字元（含 URL 的行除外）；標籤段落依 `Why` → `Behavior` → `Tradeoff` 順序，彼此空一行。

### Body

- `feat`、`fix`、`refactor` 必須有 `Why:` 與 `Behavior:`；其他 type 在 subject 已說清楚時可省略 body。
- `Why:` 寫動機。`fix` 寫根因的機制，不寫症狀：寫不出根因，代表還沒修到根因。
- `Behavior:` 寫套用後成立的預期行為或不變式。`refactor` 寫 `Behavior: unchanged — <維持不變的行為>`。
- `Tradeoff:` 寫否決的做法與理由；只寫已成立的事實，不寫「之後再補」。
- 不寫改了哪些檔案、逐步怎麼改（diff 已有），也不寫驗收清單（屬於 PR 與 ticket）。需要一長串條列時，通常該拆 commit。

### Type

| type | 用於 |
| --- | --- |
| `feat` | 新增外部可觀察的能力 |
| `fix` | 修正與規格或設計不符的行為 |
| `refactor` | 不改行為的結構調整，含 prefactor |
| `test` | 只動測試 |
| `docs` | 產品與設計文件 |
| `build` | 建置設定、依賴、工具鏈版本 |
| `ci` | CI 設定 |
| `chore` | 開發流程與工具，不影響系統本身 |

`revert` 用 git 產生的 `Revert "…"`，不另用 type。

### Scope

- 寫變更所在的 component，不寫 ticket 或階段編號；ticket 由 `Refs` 表達。
- `build`、`ci` 與無法拆開的跨 scope 變更不填 scope。
- Skills：skill 名稱，例如 `project-lead`、`feature-to-spec`、`spec-to-plan`、`plan-to-code`、`to-pr`、`review-panel`、`research-codebase`；第三方 skill 用它的名稱。
- 程式（loopctl）：`src/loopctl/` 的模組名（檔名去掉 `.py`，或子套件名），例如 `store`、`state`、`decisions`、`writes`、`gates`、`cli`、`tools`；新增模組即新增 scope。測試用受測模組的 scope，例如 `test(gates): …`。
- 安裝與範本：`setup`（`setup.sh`）、`templates`（`templates/`）。
- 文件與流程：

  | scope | 範圍 |
  | --- | --- |
  | `guide` | `docs/guide` |
  | `roadmap` | `docs/roadmap.md` |
  | `design` | `docs/design-candidate`、`docs/decisions.md`、`docs/project-intent.md`、`docs/requirements`、`docs/harness`、`docs/implementation`、`docs/research`、`docs/references`、`docs/experiments`、`docs/reviews`、`CONTEXT.md` |
  | `validation` | `docs/validation` |
  | `openspec` | `openspec/` |
  | `readme` | `README.md`、`docs/README.md` |
  | `workflow` | `AGENTS.md`、`CLAUDE.md`、`docs/workflow`、`docs/handoffs`、`scripts/hooks`、`.agents/`、`.claude/`（type 用 `chore`） |

- scope 粒度是專案層級的選擇，由 Project Lead 在本節調整。

### Trailer

- 放在最後一段，前面空一行，一行一個。
- `Refs: #N`：有對應 ticket 就必填，一行一張。
- `BREAKING-CHANGE:` 與 subject 的 `!` 同時出現。不相容包含 skill 之間的交接格式（handoff package、ticket 欄位）、loopctl 的指令與 JSON 輸出、store／state 的持久化格式、`workflow.yaml` schema。
- 禁止：`Co-Authored-By` 或任何 AI 署名；closing keyword（`Closes`、`Fixes`、`Resolves #N`），關票屬於 PR 與驗收。

### 範例

```
fix(state): generate claim tokens that never parse as an option

Why: secrets.token_urlsafe can start with '-' (about 1 in 64); argparse
read such a token as an option, so every writing command failed with a
usage error.

Behavior: state.new_token() returns secrets.token_hex(32), so
"--token <value>" always parses as a value; tokens keep 256 bits and are
still stored only as digests.
```
