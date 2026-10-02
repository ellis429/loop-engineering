# Proposal：loopctl：登記 run、記錄人工決策、查詢狀態與下一步（run-decisions）

## Why

薄 controller 依 [roadmap](../../../docs/roadmap.md)（D75）重切成四個 Feature，這是第一個。後面的派工、三 gates 與審查，都要寫進同一份持久狀態，也都要依人工決策與 `next` 前進；先交付這條最小的完整路徑：Engineer 登記一個 Feature run，人記錄開工確認等決策，任何人都能從 `status`／`next` 讀到目前狀態與唯一允許的下一步，中斷後從檔案接續。

需求輸入：[`docs/requirements/delivery-controller/`](../../../docs/requirements/delivery-controller/README.md)。現況研究：[research.md](../../../docs/research/2026-09-30/run-decisions/research.md)。

## What Changes

- **專案骨架**：Python 3.12＋uv 的 `loopctl` 套件；pytest 的測試政策（收集數為 0、非 `only_on` 產生的 skip、xfail／xpass 都讓 session 失敗）、ruff、mypy、打包後的 smoke 檢查；GitHub Actions 的必要 check `unit-linux`，依 validation §6.1，以 `pull_request` 觸發。
- **政策檔 `workflow.yaml`**：只放本 Feature 讀到的內容，也就是必要 check `unit-linux` 的宣告；以人工 `policy_change` 綁定 digest（D53）。profiles、timeouts、limits 由 Feature 2、3 各自用 `policy_change` 加入。
- **CLI**：`init`、`claim`、`status [--human]`、`next`、`register`（plan 與各種 binding）、`decide`。
- **持久狀態**：
  - 每個 repo＋feature 只有一份現行狀態。
  - 先寫歷史再原子替換，另有 lock 與 revision 檢查。claim token 只存 digest。
  - 偵測手改；狀態缺失、無法解析、schema 不符或 transition 衝突時，說明原因並列出現存檔案，不覆寫也不建立空 run。
  - 由人工 decision 解除 transition 衝突。
- **`decide` 的種類**：只收對象已存在的種類。
  - `approve_plan`：plan 必須由 Implementer 校準，而且 spec、AC 與 design 的 binding 都已登記（#6）。
  - `scope_change`：整個 run 停下，撤銷核准，等新版本再批准。
  - `policy_change`。
  - `budget_extension`：四種目標都只保存紀錄，效果由 Feature 2～4 實作。
  - `revise`、`handoff`。
  - 每筆 decision 都保存決策者、來源、理由與影響；只有人（`human:<name>`）能做決策。
  - `adopt`、`delegate` 明確回 `unsupported`。
- **`status`／`next`**：顯示階段、owner、plan／spec／design 的版本、核准、三 gate 的初始狀態、blockers，以及唯一允許的下一步。核准後，`next` 回報下一步是派工；派工能力在 Feature 2。

## Capabilities

### New Capabilities

四個 capability 都依需求輸入以 ADDED 帶入；每條 requirement 與 scenario 只寫本 Feature 結束時成立的部分，其餘由後面的 Feature 以 MODIFIED 補上（roadmap「跨 Feature 的 AC」）。

- `delivery-orchestration`：ORC-01、ORC-02、ORC-03、ORC-07、ORC-11、ORC-12。
- `delivery-gates`：GAT-06（必要 check 政策的宣告與綁定，以及本機與 CI 同一套測試政策；G3 判定在 Feature 3）。
- `durable-delivery`：DUR-01、DUR-02、DUR-05、DUR-08。

AC（20 條）：D01、D02、D03、D09、D10、D11、D25、G21、G22、O01、O03、O05、O07、O15、O19、O22、O23、O26、O29、O30。其中 D25、G21、G22、O29、O30 是新 ID，依據見下一節。

### Modified Capabilities

無。`openspec/specs/` 目前是空的。

### 和 roadmap 不同的地方

依 Project Lead 2026-09-30 對範圍的回答（第 2 題「對象存在才收」），`decide` 種類跟著產生對象的 Feature 走：

- `resolve_read`、`resolve_operation` 移到 Feature 2，AC-D13、D16 跟著移過去，所以 DUR-06 不在本 Feature。
- `accept`、`return` 移到 Feature 4，AC-F11、O11 跟著移過去，所以 ORC-05、FIN-05 不在本 Feature。
- `budget_extension` 的 `rounds` 目標在本 Feature 只有紀錄；FIN-03（AC-F07）整條留到 Feature 4。

寫 spec delta 時，另有三條 AC 在本 Feature 連觸發情境都不存在，改由後面的 Feature 首先驗證；它們在本 Feature 成立的部分改用新 ID 表達，原 ID 不改寫、不重用：

| 原 AC | 觸發情境 | 改到 | 本 Feature 成立的部分 |
| --- | --- | --- | --- |
| AC-O02 拒絕第二個外層 loop | 請求派發外層實作 | Feature 2 | 非 owner 只能讀取，已由 AC-D03 涵蓋 |
| AC-D17 Active budget 到限與恢復 | 累計主動時間到 4h | Feature 2 | 預算調整只記錄人工裁決：新增 AC-D25 |
| AC-G13 非成功 check 與空集合 | G3 判定必要 check | Feature 3 | 本機與 CI 同一測試政策：新增 AC-G21；必要 check 政策需要核准：新增 AC-G22 |

另外兩個新 ID 來自 requirement 本文與已確認的範圍：AC-O29（binding 不齊時不能批准，#6）、AC-O30（`adopt`、`delegate` 回 `unsupported`，ORC-01）。

roadmap 的 Feature 1 列與[重切研究](../../../docs/research/2026-09-30/controller-recut.md)的對照，在本 change 一起更新。

## 不做

- 派工、外部寫入與讀回、active 預算的計時與到期、`resolve_read`／`resolve_operation`、task→AC 結構的核對（需要解析 plan）、orchestrate skill：Feature 2。
- G1、G3 判定、GitHub 讀取（包括 ORC-02 的 issue 觀察時間）、push 與 PR：Feature 3。
- G2、finding 與修正批次、輪次上限的效果、`accept`／`return`、PR Pass：Feature 4。
- workflow 樣本（W-A～W-F）與 R3：M1 驗收。
- adopt、Project Lead 委派、Retro：M2；本 Feature 只回 `unsupported`，Retro 候選依 D55 由 project-lead skill 承接。
- CI 的 commit-msg 檢查：main 沒有對應的 hook 與規範檔。

## 待決與依賴

| 項目 | 是否阻擋 Design | 負責 |
| --- | --- | --- |
| 依賴：無上游 Feature；base 是 `main@c91b774` | 否 | — |
| 核准後 `next` 回報「下一步是派工」的具體動作名稱與欄位 | 否，屬 design | Implementer |
| 解除 transition 衝突用哪個 decision（新種類，或沿用 `revise`） | 否，屬 design | Implementer |
| GitHub branch protection 是否把 `unit-linux` 設為必要 check | 否；不影響本 Feature 的驗收 | Project Lead |
| 參考實作 `delivery/thin-controller@fcefecc` 只作參考；沿用的程式照 TDD 重做，舊測試與審查不算證據（D75） | 否 | Implementer |

## Spec 確認

- 確認人：Project Lead（使用者本人，同時是 Engineer 與驗收人，D75）
- 時間：2026-09-30
- 原話：「現在確認」（回答「確認 Feature 1 的 spec（commit `85255da`）嗎？」）
- 確認的版本：commit `85255da`（proposal 與三份 spec delta）
- 這是 spec 確認，不是開工確認；開工確認在 spec-to-plan 寫完 design 與 tasks 後另外進行（D11）。
