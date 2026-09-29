# Roadmap：薄 controller（loopctl）

> **草稿**，2026-09-30。Project Lead 確認前（D63），不開 Feature、不派工。

來源（皆為 `main@a1d8906`，另註明者除外）：

- 需求輸入：`openspec/changes/implement-delivery-loop/specs/`，四個 capability、36 條 requirement、88 條 AC；D53 採用，組成方式見同目錄的 `adoption/source-map.md`。
- 高層設計：D45-04 revision-17（[`docs/design-candidate/d45-04/`](design-candidate/d45-04/)，D53 核准），以及[勘誤](design-candidate/d45-04-errata.md) E-1～E-3。
- 既有實作：本機 branch `delivery/thin-controller@fcefecc`（未 push）。6,054 行程式、8,825 行測試、549 個測試；完成 T1.1～T3.1、T6.1、T7.1，T5.1 以後沒做。
- 行數、依賴與 AC 對照：[重切研究](research/2026-09-30/controller-recut.md)。

**為什麼重切**：D53 把整個薄 controller 當成一個 change、17 個 task，做完會是一個約 15,000 行（含測試）、跨四個 capability 的 PR。之後 D57 定為一個 Feature 一個 change、一個 PR 做得完，太大就拆；D74 要求 Feature 垂直切。所以改成四個 Feature，每個都是從 CLI 操作到持久狀態與驗收測試的一條完整路徑，能單獨驗收，各走 feature-to-spec → spec-to-plan → plan-to-code → to-pr。

**原則**：roadmap 只有 Milestone 與 Feature 兩層（D57、D65）。task 寫在各 Feature change 的 `tasks.md`，不上 roadmap。M1 的切法有既有實作與已核准的設計當依據，所以整批列出；M2 先只寫交付能力。每個 Feature 驗收後回來重切。

## Milestones

| Milestone | 目標日期 | 可以展示的成果 | 完成條件 | 交付能力 |
| --- | --- | --- | --- | --- |
| **M1：薄 controller 可用** | 建議 2026-10-16（五），待定 | 一個真實 Feature 由 orchestrate 透過 loopctl，從開工確認走到 PR Pass 或 Blocked。過程包含派工、三 gates、finding → fix → re-review，中途中斷一次後接續；狀態與證據都可查。 | 1. 四個 Feature 都已接受、merge 並 archive。<br>2. R3：用 loopctl 跑完一個真實 Feature。三 gates 在目前版本都通過；改變行為的修正有綁定 finding 的原始 Red；中斷後成功接續。Blocked 或沒有 finding 時，R3 維持 open，M1 不算完成。 | 人工決策與可追溯狀態；派工與結果回收；三 gates；finding 迴圈與 PR Pass |
| **M2：example 與延後能力**（暫不切） | M1 完成後定 | cross-node-file-transfer 由 orchestrate＋loopctl 從 Project 跑到多個 Feature（D43、D56） | M1 完成後定 | adopt（AC-O08、O09）、Retro op（O14）、Project Lead 委派（O18）、OpenCode-only 部署（D20、D24）、跨 Feature 依賴、平行 worktree、Q-STACK、多人交接（Q-DEMO-PEOPLE） |

日期的估法見[重切研究](research/2026-09-30/controller-recut.md#時間估計的依據)：每個 Feature 約 1.5 個工作日，R3 約 1 個工作日，另留一週給修正輪與人工確認的等待。

## M1 的 Feature

「近期」是接下來要開 change 寫 spec 的；「暫定」只有名稱、範圍與依賴，排進近期時才寫 spec，也可能重切。

| # | Feature | 狀態 | 看得到的行為 | 可參考的既有實作（`fcefecc`） | 依賴 | 相關需求輸入 | 勘誤與 issue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 人工決策與下一步 | 近期 | Engineer 登記一個 Feature run，含 spec、design 與 plan 的版本。人用 `decide` 記錄開工確認等決策。`status` 與 `next` 顯示持久狀態，以及唯一允許的下一步。中斷後從檔案接續。包含專案骨架，以及 CI `unit-linux`（D53）。 | T2.1、T2.2；T1.1 的 CLI、測試政策、CI、`workflow.yaml` | — | ORC-01、02、03、05、07、11、12；GAT-06；DUR-01、02、05、06、08；FIN-03、05（首先驗證 23 條 AC） | #6 |
| 2 | 派工與結果回收 | 暫定 | `next` 給出派工。loopctl 用 preflight 驗證過的 profile（R1），經 Herdr 啟動 Implementer。外部寫入先登記、再讀回；逾時轉成 unknown，由人用 `decide` 處理。結果先保存，再去重匯入。觀察 worker 活動，計算 active 預算（4 小時）與 worker 時限（45 分鐘），到期就拒絕派工。每個 profile 分開報告能力與缺口。 | T1.1 的 profiles 與 preflight、T1.2、T2.3、T7.1 | 1 | ORC-03；GAT-05、08；DUR-02、03、04、06、09（首先驗證 12 條，另加 AC-G19、AC-D22） | E-1（#9）、E-2（#11）、#7 |
| 3 | TDD 證據、PR 與 CI | 暫定 | Implementer commit 後，loopctl 核對 G1：原始 Red 的資格、乾淨 checkout 的 Green、N/A 紀錄、整合 attempt。接著 push，建立或更新 PR，等待 CI（30 分鐘），只認 PR head 上 `unit-linux` 的 success 判定 G3。R2：在 probe branch 用 fixture 真實跑到 G1。 | T3.1、T6.1 | 2 | GAT-01、02、03、04、06、07；DUR-07（首先驗證 13 條） | #15 |
| 4 | 獨立審查與 PR Pass | 暫定 | loopctl 派獨立 Reviewer：不同模型、新 session，review 時限 30 分鐘。G2 綁定 head、base 與文件版本。finding 流程包含登記、合併成修正批次、覆核、一次爭議覆核、反覆 finding 提前升級，上限三輪。最後發布 review 與 PR Pass 驗收包。orchestrate 只依 `next` 與 `safety` 行動，串起 plan-to-code 與 to-pr。 | 無（T4.1、T5.1、T6.2 沒有實作） | 3 | GAT-01、07、08；DUR-04、07；FIN-01～07；ORC-05（首先驗證 20 條） | E-3（#12） |

**依賴**：四個 Feature 是一條鏈，依 D27 依序開工：上游接受並 merge 後，下游才開始實作。等上游時，可以先準備下游的 spec。

**跨 Feature 的 AC**：18 條 AC 的驗證跨兩個以上的 Feature，清單見[重切研究](research/2026-09-30/controller-recut.md#跨-feature-的-ac)。

- 每個 Feature 的 spec delta 只寫這個 Feature 結束時已經成立的部分。
- 原 AC 由最後一個 Feature 補齊。對前面已經 archive 的 requirement，後面的 Feature 用 MODIFIED。
- 例如 AC-F07「三輪已用完」：1 只記錄延長輪次的人工決策，轉 Blocked 要到 4 才成立。

**既有實作怎麼用**：`delivery/thin-controller` 保留為唯讀參考，不 merge，也不再加 commit。

- 每個 Feature 從 `origin/main` 開 `feature/<change-id>` 與自己的 worktree（D67）。
- 要沿用舊程式時照 TDD：先寫計畫列的測試，存下原始 Red，再移植或重寫實作。
- 舊的測試結果、逐 task 審查與 preflight 紀錄，都不算新 Feature 的證據。profile 已經改過，preflight 要重跑。
- 舊實作審查留下的已知問題，已列在上表最後一欄。

## 不放進 M1 的需求

**只由 workflow 樣本驗證的 12 條 AC**：AC-F12、O04、O12、O13、O16、O17、O20、O21、O24、O25、O27、O28。

- 這些描述的是 Project Lead 與 skills 的行為，例如權威來源衝突、從 project 分析拆出 Feature、上游接受但還沒 merge；不是 loopctl 的行為。
- 建議不放進任何 controller Feature。在搬移需求輸入時附一張對照表，逐條指到實作它的 skill 段落（project-lead、feature-to-spec、research-codebase）與決策（D55～D72）。
- 找不到對應的，列為缺口並開 issue。
- 它們不是 M1 的完成條件。

**延後 S2 的 6 條 AC**：列在 M2 的交付能力（D45-04 tasks「延後」一節）。

## `implement-delivery-loop` 退役

這個 change 把整個薄 controller 當成一個交付（D53），和 D57「一個 Feature 一個 change」不符；內容也還寫著 D55、D56 之前的規則（#5）。建議在 roadmap 確認後，用同一個 docs PR 做這些事：

1. 把 `specs/` 的四份 capability 與 `adoption/source-map.md`，原樣搬到 `docs/requirements/delivery-controller/` 當需求輸入，不改寫內容。
2. 刪除 change 目錄，不 archive。這個 change 沒有交付；archive 會把還沒實作的行為寫進 `openspec/specs/`，違反 D58。`proposal.md`、`design.md`、`tasks.md`、`approval.json` 與 adoption 審查紀錄留在 Git 歷史裡。
3. D53 的核准保留為歷史紀錄。D45-04 design 改作高層設計的參考；每個 Feature 的 `design.md` 由 Implementer 依它的章節寫（D69）。
4. 相關 issue：
   - #5 隨退役關閉。
   - #1（S1 epic）改為追蹤 M1，或關閉。
   - #8 隨重做失效：新的 commit 各自綠燈。

## 待 Project Lead 決定

建議都寫在括號裡；確認後記入決策紀錄（D63）。

1. **切法與順序**：四個 Feature，照 1 → 2 → 3 → 4 依序做（建議照這個）。
2. **M1 目標日期**：建議 2026-10-16。
3. **`implement-delivery-loop` 退役與需求輸入搬移**：照上一節的做法。
4. **12 條 workflow AC**：移出 M1，改用對照表處理。
5. **D61 的解讀**：D61 說 loop-engineering「不當任何產品的 root」。建議解讀為不當其他產品（例如 cross-node-file-transfer）的 root；loopctl 本身是單一 repo 的產品，root 就是本 repo，所以 roadmap、需求輸入與 change 都放在這裡，不需要 `repos.yaml`。
6. **既有實作的可讀性**：`delivery/thin-controller` 目前只在本機。建議授權 push 成唯讀參考 branch，讓 Reviewer 與其他成員從 GitHub 讀到。
7. **R3 用哪個 Feature**：建議用 cross-node-file-transfer 的第一個 Feature（D56）。它是真實的新行為，也是 M2 的起點。在 Feature 4 收尾時選定。
8. **分工**：建議 spec 由 Claude（Opus 5.5）用 feature-to-spec 準備，Project Lead 確認；Engineer 與驗收人是 Project Lead（D62）。G2 建議用 review-panel（D73）。
