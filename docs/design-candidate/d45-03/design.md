# Design：薄 controller 第一個可用切片（D50 精簡候選 design-03）

> **狀態**：候選，未 D11，也不授權實作。review-10 的 D50-R01–R07 已在 revision-07 提交修正，待獨立覆核。
> 本文**取代** design-02 候選，不是它的補充；design-02 中沒有在本文重述的機制，一律視為不採用。
> 已確認的政策：D46–D50。仍待決定：CI check 集合、reviewer model、timeout 預設（見 result.json）。

## 1. 範圍

- **第一片交付**：一個新 feature 從批准的 plan 開始，依序做 TDD 實作，經 G1、PR、獨立 review＋CI，發生 fix → re-review，最後到 PR Pass。
  - 附證據的 Blocked 是正確的安全停止，但**不算示範完成**（D50-R05）。
  - 這個 feature 要等 controller 的 bootstrap PR 經人工 accepted、實際 merge，並登記採用的 baseline 之後，才開始（D27；不自動 merge，D50-R04）。
  - 在那之前的真實執行，只算隔離的能力 probe。
- **組成**：
  - 一個 Implementer worktree，tasks 與 fix 都在同一個 worktree 依序進行；
  - 一個獨立的 Reviewer clone＋session；
  - 最小的 orchestrate skill；
  - `loopctl` controller；
  - Herdr 原生 transport。
- **不變的部分**：三 gates、G1 先於正式 G2、原始 Red＋目前 Green、最新版本綁定、finding 由 Reviewer 或人關閉、單一 feature 狀態／writer／預算、D47–D49、unknown 就停下交人。

## 2. 移除或延後（D50）

| 項目 | 處理方式 |
| --- | --- |
| 每個 attempt 一個 worktree、CAS 整合 log | 移除。第一片是序列式的單一 writer。平行 writer 留到後續切片 |
| 唯讀查詢的 prepare/begin/readback 生命週期 | 移除。唯讀改為 §5 的有界 fetch |
| 每次都 replay 歷史 Red | 改為只在證據矛盾或有特定風險時做的診斷 |
| adopt、epoch 放棄的自動化、delegate、跨 feature 依賴、Retro operation、Project 自動化 | 延後。由 workflow／skill／人依既有契約處理，controller 只記錄 decision。未支援的入口明確回 `unsupported` |
| OpenCode-only transport、其他 runtime | 延後 |
| 逐 symbol 的提取 manifest、每個模組都要有 caller 的硬 gate | 移除，見 cleanup-map |

## 3. 公開介面：`loopctl`

每次呼叫都是短命的：核對 → 更新 → 返回。stdout 是一個 JSON 物件，欄位為 `ok`、`revision`、`result`、`blocked`、`next`、`safety`。Exit code：0 成功、1 拒絕、2 用法錯誤、3 Blocked、4 not_owner、5 狀態不可信。

| 命令 | 效果 |
| --- | --- |
| `init --repo --repo-id --feature --issue` / `claim --actor` | 建立 feature；取得協調權，token 只存 digest |
| `status` / `next` | 唯讀：現況、下一個允許動作與安全動作（到期 stop、寫入操作的讀回） |
| `register plan\|binding\|policy` / `decide <kind>` | 登記原生 artifact 的版本；記錄人工決策。第一片支援的 decision kinds：`approve_plan`、`revise`、`scope_change`、`resolve_finding`、`waive_finding`、`resolve_operation`、`budget_extension`、`policy_change`、`accept`、`return`、`handoff` |
| `write <op> --id`（需 token） | 外部寫入，見 §5 |
| `observe ci\|pr\|worker` | 唯讀的有界 fetch，結果匯入為 observation |
| `evidence red --command-id`（worker）/ `evidence green`（coordinator） | 只執行 policy 定義的命令，不接受任意 argv |
| `result import --attempt` / `assess` | 匯入結果；計算 gates |

Orchestrate skill 只能照 `next` 或 `safety` 做事，不直接改狀態。

## 4. 狀態與不變式

- `$LOOPCTL_HOME/features/<id>/feature.json` 是唯一的現行狀態。
  - 寫入流程：先取 lock，把 `history/<rev>.json` 以 write-once 寫入，再原子替換現行檔。
  - 歷史中同一 transition ID 出現不同內容 → Blocked。
  - 缺檔、壞檔、未知 schema、手改 → exit 5，永不重建空狀態。
- 最小欄位：`phase`、`owner`、`plan{digest, producer, tasks[]}`、`approval`、`versions`（head、base、merge_base、spec／design／plan／policy digests）、`attempts`、`writes`、`observations`、`gates`、`findings`、`batches`、`budget`、`decisions`、`blockers`。
- 證據與 raw 輸出存成 content-addressed 物件。文件 digest 欄位不被當作物件引用。
- **序列 writer**：同一時間只有一個 active attempt。只有前一個 attempt 的結果已匯入，且 worker 確認停止或 idle 時，才可以派下一個；writer 狀態 unknown → Blocked。每個 task 以 attempt ID、commit 範圍（diff 必須在 scope 內）與 Red snapshot 追溯。

## 5. 外部寫入與唯讀觀察

**外部寫入**（有限種類：`agent_start`、`prompt`、`stop`、`push`、`pr_ensure`、`publish_pr`、`publish_issue`、`worktree_create`）的狀態流程：

`prepared → in_flight → succeeded | failed(確定未送達) | unknown`

- `write` 命令在同一程序內：consume 一次 → 呼叫固定 argv 一次 → 記錄 receipt。
- 重試只在兩種情況允許：記錄了確定未送達，或已驗證的原生冪等（例如 CAS、`--force-with-lease`）。
- 查不到效果（not_found）、client 已結束，**都不構成證明**。Herdr socket 與 GitHub 的請求都可能晚一點才生效 → unknown，交人。
- 讀回只看既有的 write，不重發。每個 attempt 最多 3 次，每次查詢都計入（包括「仍在執行」）。到上限就 `blocked(readback_exhausted)`，等人。
- 嘗試上限 3 次（D13）。

**唯讀觀察**（CI checks、PR head／base、worker 狀態、native transcript）：

- **發出 fetch 之前**，先在 lock 內配置並持久化一個單調遞增的 `seq`（只是一次計數器更新）。之後直接 fetch，有 timeout；每次呼叫最多 3 次。
- 匯入時依 `seq` 排序，不依完成時間（D50-R02）。
- observation 分開保存兩類資料：
  - **請求脈絡**：`purpose`、請求時的 `version_key`；
  - **觀察到的事實**：head、base、merge_base、binding digests、checks、`observed_at`、來源、raw 物件。
- **共用版本事實**（head、base、merge_base、binding digests）有一個 feature 層級的水位 `version_seq`，跨所有 purpose 共用（pr、pass、ci 等，只要該觀察帶有版本事實）。只有 `seq > version_seq` 的觀察能更新這些事實，並把 `version_seq` 設為自己的 `seq`：
  - 事實與現行版本不同 → 相關 gates 與 Pass 失效；
  - 即使請求是以舊版本發出，只要觀察到的是新的 head 或 base，仍然有效。
- `seq ≤ version_seq` 的晚到觀察，不論 purpose，都不能改寫共用版本事實，也不能恢復舊版本。例：`pass` 的 `seq=10`（H1）比 `pr` 的 `seq=11`（H2）晚到 → head 仍是 H2（D50-R02）。
- **各 purpose 的結果快取**（例如 CI checks、Pass 觀察結果）分開保存，只以該 purpose 內較大的 `seq` 更新。快取結果不能重定共用的 `version_key`，也只有在它觀察到的版本等於目前版本時才可以被 gates 採用；否則只存歷史。
- 不需要執行許可。

## 6. Runtime 與獨立性

- **Profile**：Implementer 是 Herdr＋Claude Code＋`claude-opus-5-5`；Reviewer 是 Herdr＋OpenCode＋核准的 OpenAI model（待 D11）。transport、runtime、provider、model 分欄保存。
- **真實 writer 的前置**：第一個真實 writer（tasks 4.2 的隔離 probe）只在 worker 狀態讀取與 D47 停止／預算的 fake 情境都通過後才啟動（D50-R01）。preflight 那一次成功的 stop，不能取代持續的停止能力。
- **Capability preflight**（最早執行，見 tasks 1.2）：
  - 載入核准 skills 的正式 profile，不使用 safe-mode／pure；
  - 以 native 紀錄讀回 model 與 marker；
  - 權限負例：寫出 worktree 範圍、`git push`、`gh`、`herdr`、`loopctl decide` 都要被拒；
  - 送 stop 後以 process-info 確認停止。
- **限制**：preflight 結果只綁定該版本與該 profile；未驗證就 Blocked。它不證明能抵抗同一 OS 帳號的偽造（D48），只保證能偵測可核對的不一致。
- **Reviewer**：在獨立 clone 工作，沒有寫作者 branch 的路徑。G2 需要：session 獨立、讀回的 model 相符、capability verified、`read_digests` 等於目前版本。
- **不安全的結果一律拒收並保存原件**：身份、cwd、head、scope 不符；worker 提供的 argv；producer 不符；版本過期。unknown → 交人，附證據。

## 7. 證據、gates、修正、預算

- **G1**：
  - 核准 plan 的每一個 task 都要有原始 Red：raw、exit、task／attempt、snapshot、provenance 逐項核對；
  - coordinator 以 policy 命令在 head 跑 Green 與 regression；
  - 正常路徑不做 replay；只有證據矛盾或有特定風險時才以 replay 作診斷，診斷失敗 → Blocked；
  - 缺原始 Red → fail closed；
  - 純文件的 N/A 需經獨立 eligibility review。
- **正式 review 前 G1 失敗**：若失敗可歸因且可修正，開 `pre_review_g1` batch（計一輪），修完重做 G1。缺 Red 或需要改 spec → Blocked。
- **G2**（D50-R03）：
  - Reviewer 的 assignment 與 result 都要綁定：完整 PR diff（base…head）、適用的 spec／design／AC digests、先前的 findings。
  - 只有以下全部成立才 passed：§6 的授權與獨立性條件、完整範圍、目前版本、verdict 為 `clean`、沒有未解的 blocking。
  - `changes_required` → failed；`blocked` → unknown，不開修正輪。
  - 缺 verdict、格式錯誤、只審部分 diff → 不能 passed。
- **G3**：依 D49：
  - 必要集合只來自可讀的 repo 規則，或人工 `policy_change` 綁定的集合；
  - check 只有在 `head_sha==H` 且 `tested-sha==H` 時才計入；
  - 非成功狀態不放行；
  - 403 或政策 unknown → Blocked，不耗修正輪。
- **Correction batch**：
  - 同版本 review 與 CI 都收齊後才開 batch；
  - 可修正的項目包括程式、測試、文件缺陷、缺少的必要驗證；
  - 派修時計一輪，上限 3 輪；
  - 反證只給一次覆核機會；
  - 反覆出現的 finding（`failed_rechecks≥2`，或已解決又 reopen）→ Blocked；
  - assignment 要附完整的 finding 快照。
- **Pass**：
  - 三 gates 在同一 `version_key` 都通過；
  - 沒有未解的 blocking；
  - 必要發布已完成（先 PR review，再 issue 摘要）；
  - 之後再做一次新的 `purpose=pass` 觀察，結果一致。
- **預算（D47）**：
  - 4h active 以時間區間聯集計算，換 session 也不重置；
  - 到期時優先 stop 已知的 active worker，這不受其他 blocker 影響；
  - 協調者離線期間的時間，在恢復時計入並記錄超出量，然後 Blocked；
  - unknown 不等於已停止。

## 8. 風險

- [preflight 不通過] → 在大量實作之前就先 Blocked，改由人決定 profile。
- [單一 worktree 沒辦法平行] → 第一片接受；平行 writer 屬於後續切片。
- [replay 不再每次執行] → 原始 Red 仍是必要條件；證據矛盾時觸發 replay。
