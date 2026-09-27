# D11 確認包：薄 controller 第一片（D45-04 revision-16）

> **狀態：待你確認，尚未核准。** 獨立覆核的結論見 [README](README.md)。本頁只放需要你決定的事；細節在 [design](design.md)、[tasks](tasks.md)、[validation](validation.md)、[spec-delta](spec-delta.md)。
> 核准後才執行 W1 與產品實作；核准前不寫產品碼、不做 GitHub 寫入、不啟動 example。

## 1. 第一片能做什麼

- 一個 feature 從已核准的 plan 出發，依序 TDD → G1 → push → 建立或核對唯一的 PR → 獨立 review 與 CI 並行 → 修正 → 再審 → **PR Pass**，停在等待你的人工接受。
- 不 merge、不關 issue、不 release、不 deploy。
- 任何結果不明、證據不足或預算用盡，都保存現況、停下並交給你（Blocked），不猜測、不重複派工。
- 交付分兩段：
  1. **Bootstrap PR（T1–T7）**：`loopctl`、orchestrate skill、CI 與測試政策，以及 B1 的三 gates 紀錄；
  2. **T8**：第一個真實 feature。它必須是 bootstrap 尚未實作的新行為，由你另外做一次 D11 選定，並等 bootstrap PR 經你接受、實際 merge、登記 baseline 之後才開始。

## 2. 如何驗收

| 層次 | 內容 | 通過標準 |
| --- | --- | --- |
| 產品測試（fake） | 109 個參數化案例，涵蓋狀態、決策、外部寫入、G1／G2／G3、Pass、resume、預算與 timeout | 每個 task 完成時，整個套件在該 head 通過；收集數為 0、未經平台 marker 的 skip、xfail 都算失敗 |
| Workflow 樣本 | W-A–W-F 共 6 組，每組一個正例、一個負例 | 獨立 Reviewer 依 rubric 審查並記錄 |
| 真實證據 | R1 兩個 profile 的能力 probe；R2 在 probe branch 跑到 G1；R3 真實 finding → fix → re-review、三 gates、中斷後接續 | R1 全部負例被拒且資源未變；R2 的 G1 passed；R3 三 gates 在目前版本通過 |

- 88 個 AC 與 17 項舊 S1 findings 的逐項歸屬在 [coverage](coverage.md)；全部仍是 planned／open，核准不代表任何一項已通過。
- 附證據的 Blocked 是安全停止，不算示範完成。

## 3. 請確認的具體預設

| 項目 | 建議值 | 理由 | 其他選擇與影響 |
| --- | --- | --- | --- |
| **A. 採用文件** | design、tasks、validation、coverage、cleanup-map 的 revision-16；正式 spec 以「正式 specs＋D45-02 spec-delta（sha256 `7ebd8d01…c18565`）＋D45-04 spec-delta（revision-16，sha256 見 README 的 publication manifest）」依 spec-delta §12 組成 | 沿用已覆核的 revision-14，只補派工與執行預設；唯一的語意收窄是移除 D45-02 的「本機同步程序」重試例外（spec-delta §1），只會讓系統更早停下交人 | 不採用 → 回設計，不開工 |
| **B. 產品 profile**（loopctl 管理的 attempts） | Implementer：Herdr＋Claude Code＋`claude-opus-5-5`＋effort high；Reviewer：Herdr＋OpenCode＋`openai/gpt-6-astra`＋variant xhigh | 符合 D36／D52 的 Opus 預設與不同模型審查；Astra xhigh 是先前文件覆核實際用過的模型 | OpenCode 上的 Astra 尚未實際推論驗證；R1 不通過就 Blocked，不自動換 runtime 或 model |
| **C. Bootstrap 開發分工** | Opus 5.5 high 實作一般 task，xhigh 做 2.3、3.1、6.1、5.1；GPT-6 Astra xhigh 做所有審查；允許一般 task 改用 GPT-6 Sol high（派工前記錄） | D52：預設 Opus 實作、GPT 審查；Reviewer 必須是不同的實際模型與獨立 session | Astra 不可用 → 停下交你決定，不默默替換 |
| **D. 必要 CI** | `unit-linux`（ubuntu-24.04：測試套件＋ruff、mypy、dist-smoke）、`unit-macos`（macos-15：測試套件），只由 `pull_request` 觸發，只認 PR head，沒有 skipped／neutral 例外；兩個 job 都套用同一測試政策；政策檔 `workflow.yaml` 全文見 validation §6 | Linux 是本機無法覆蓋的平台；macOS 提供乾淨 runner 的獨立證據 | 去掉 `unit-macos` 可省 private repo 的 macOS 計費，macOS 只剩本機 G1 覆蓋（validation §6.3） |
| **E. Timeout 與讀取界線** | worker 45 分、review 30 分、CI 等待 30 分；逾時先確認停止，同一單位最多再派 2 次，之後 Blocked；本機證據命令（Red／Green）15 分鐘，且不超過剩餘 active 預算，逾時 → Blocked；讀取子程序 30 秒、寫入 60 秒（push／PR 120 秒）、輪詢 30／60 秒 | 沿用 D45-02 起的 45／30／30 候選，重試次數沿用 D13 的「額外 2 次」 | 值放在 `workflow.yaml`，之後改動需 `policy_change` |
| **F. W1 基底** | 從 `origin/main` 建 `docs/d11-adoption`：先把目前工作區**尚未提交的文件原樣**提交為 A0（不含程式），再組成正式 spec 為 B；**W1-A**：開 docs PR 由你 merge 後，再從 main 建 `delivery/thin-controller` worktree | 若沿用 `4ce1110`，bootstrap PR 合併後 GitHub 會把仍有 17 項 blocking 的 PR #2 顯示為 merged；docs 先進 main 也讓 bootstrap PR 只含程式 | **W1-B**：不開 docs PR，bootstrap PR 同時包含文件差異，少一次 merge，但 review 範圍變大 |

## 4. 需要你回答的問題

1. **是否依第 3 節的建議一次核准 D11（A–F）？** 若要改其中某項，只需指出該項與要改的值。
2. **W1 採 W1-A（先 docs PR，由你 merge）還是 W1-B（不開 docs PR）？** 建議 W1-A。
3. **CI 是否保留 `unit-macos`？** 建議保留；若在意 private repo 的 macOS 計費，可改為只保留 `unit-linux`（validation §6.3）。

## 5. 這次不核准、仍延後的事

- S2：adopt（O08、O09）、Project Lead 委派（O18）、Retro op（O14）、scope 變更只停受影響工作（O23 的後半）、跨 feature 依賴自動化、平行 worktree、非 head 的整合 SHA 映射（G15 正向）、OpenCode-only 部署（D20）、同一 OpenCode 承載兩個角色（D24）。
- S3：cross-node-file-transfer 示範、多人交接、Q-STACK。
- T8 要實作的 feature：由你之後另做一次 D11 選定。
- 仍待回答的 Q-STACK、Q-DEMO-PEOPLE 不影響第一片。

## 6. 核准後的第一步

協作者執行 tasks **T0.1**：記錄目前工作區 → 建 `docs/d11-adoption`（A0）→ 組成正式 spec 並由 Astra xhigh 獨立核對對照表（B）→ 依 W1 選項進 main → 建 `delivery/thin-controller` worktree。完成後派 **T1.1** 給 Opus 5.5 high。
