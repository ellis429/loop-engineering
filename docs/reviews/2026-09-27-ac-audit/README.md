# AC 合理性、驗法與實現狀態審核

日期：2026-09-27。對象：D50 / D45-03 候選，連同其繼承的 D45-02 spec delta 與四份正式舊 specs。由目前協作者直接逐項審查，沒有另派 agent；方法沿用 codebase-design 的必要性／介面原則，另核對 scenario→task→驗法→實際證據。

**結論：核心要求大多合理，但不能說 88 項都已合理歸位、驗法充分或已實現。** 先前的 105 唯一 ID 完整性及定點文件 review，不等於 88 AC 的語意覆蓋審查。本次發現需要先處理的規格／驗法差異；建議在 D11 前補齊，不據前次 `ready_for_human_review` 直接開工。

本審核沒有刪改已確認需求、正式 specs、候選 source artifacts 或產品程式。分類與最小修正是審核建議；D50 原來刪除的平台機制不應因此復活。

## 1. AC 是否合理

以下為互斥的**建議主要歸屬**，不是新決策或完成率：

| 類別 | 數量 | 判斷 |
| --- | ---: | --- |
| 保留核心行為 | 58 | 三 gates、版本、證據、finding、單一 writer、持久化、有界失敗等必要行為；不等於每項都已有充分測項 |
| Workflow／人工契約 | 17 | SA、角色、需求裁決、Project／feature 交接合理；以工作樣本與人工 rubric 驗收，不全塞進 controller |
| 後續能力 | 6 | O08/O09/O14/O18/D20/D24；adopt、委派、Retro、不同部署／雙角色配置，延期不能算完成 |
| 改寫或下移細節 | 3 | G15 的 CI SHA 語意、D10 的存儲機制細節、D23 的配置適用範圍 |
| 驗收證據規則 | 3 | G19/G20/D22；區分 mock、profile、真實 demo，不是三個新的產品 gates |
| 歷史限制 | 1 | O15 的 P03/session/Q-TARGET 保留在 handoff；通用「未授權不接管」仍保留，不寫 P03 特判 |

不要為湊小數字刪掉必要反例，也不要為保留 88 個 ID 就承諾第一片全數自動化。O20/O21/O24 可以共用一組 Project→feature 文件樣本；O05/O22/O26 可以共用帶不同批准來源的矩陣；多個 AC 可以共用一項有辨識力的測試。

完整逐項理由：[88 項矩陣](ac-matrix.md)。原文、來源行號、原 coverage owner/slice、分類與輸入 hashes：[JSON ledger](ac-ledger.json)。

## 2. 驗證方法是否合理

| 本次計畫充分性評估 | AC 數量 |
| --- | ---: |
| 主要情境明列 | 27 |
| 只有部分驗法／缺少關鍵情境 | 38 |
| 文件驗收尚待具體化 | 13 |
| 規格矛盾或測項錯配 | 4 |
| 明確延期未覆蓋 | 5 |
| 歷史，不作產品測項 | 1 |

這不是測試 coverage 百分比；27 也不是 passed。評估單位是 AC 的主要 WHEN/THEN 是否在現有 design/tasks/validation 中有對應檢驗，並不要求每個 AC 都獨立寫一個測試。所有新產品驗證目前仍 planned。

### AC-A01：先消除 CI 的兩個契約差異（高；開工前）

- **G13 / D49**：[design §7](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/design.md:111>) 寫「403 或政策 unknown → Blocked」，但繼承的 spec delta 與 validation 允許本 repo 在 rules 403 時使用人工核准且版本化的 policy。照 design 字面做會拒絕已批准路徑。最小修正：`403 且沒有適用人工政策` 才是 unknown；測「403＋已批准」與「403＋未批准」兩條路徑。
- **G15**：正式 AC 與 [D45-02 delta](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/spec-delta.md:151>) 保留合法 integration SHA 映射；新版 [validation §4](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/validation.md:47>) 一律要求 check head 與 tested SHA 都等於 H。它能驗證 head-only policy，不能驗收「CI 使用不同 integration SHA」的情境。建議首片明定 head-only；不支援的 integration-source 回可解釋的 unknown，G15 的正向映射能力延期並同步 delta/coverage。不要為此立即建立通用 merge CI 平台。

### AC-A02：測試引用不等於場景已覆蓋（中；核心驗法先補）

[coverage](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/coverage.md>) 把很多 AC 指到 V6/V8/V9，但 [validation](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/validation.md>) 和 tasks 的行為段沒有下列關鍵反例：

| AC | 現有不足 | 最小補強 |
| --- | --- | --- |
| G02 | V8 只有發布／push | review clean＋CI fail；review fail＋CI green，兩者都不能 Pass |
| G14/G17 | observation seq 不能代替 CI attempt／contract 適用性 | 舊 check success／新 attempt pending；同名不同 app；head 不變而 base/spec/skill 變更 |
| F06 | V6 有一般 fix/re-review，沒有完整批次檢查 | batch 兩項只回一項→列 missing ID、不解除任何未覆核 blocker |
| F08–F10 | 「一次反證」只是一句限制 | 接受反證不加輪、拒絕／重送不重抽 review、新 head 仍先 G1 |
| D07/D14/F14 | V4 是寫入處理，V9 是 budget，不等同恢復交接 | 已完成 worker＋保存 review＋issue pending＋漏通知→接續只發布 issue，不重派／重 review／洗掉 budget |
| F11/O11 | acceptance 綁定版本不等於完整退回 | pending 驗收直接退回、同一 finding／預算、Pass 失效；V2 不繼承 V1 accepted |

以上可以併入現有測試檔的少量參數化情境，不需要新增一套測試框架。其他不足逐項列在矩陣中；Workflow AC 使用文件樣本，不強迫 controller 做語意判斷。

### AC-A03：Runtime 的 R1 覆蓋範圍標錯（中；修正對照）

D24 的 WHEN 是 Implementer 與 Reviewer **同為 OpenCode**；首片正式 profiles 卻是 Claude Code Implementer＋OpenCode Reviewer。這個 R1 即使通過，也不能證明 D24，應列後續配置驗收。D23 的「未選接入故障不影響已選路徑」也不能用 V1「缺 profile 回 unverified」替代；需明確不同的已選／未選配置反例，或隨 OpenCode-only 延期。

D04 的「worker 已確認停止或 idle」還應明定：是可核對的 native attempt 完成／writer 結束證據，不能只拿 terminal idle 接手；這不要求自建 fencing 平台。

### AC-A04：正向 PR 交接缺明確任務責任（中；補一條工作路徑）

Design 已列 `write push`、`pr_ensure`，但 [tasks 執行表](</Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-03/tasks.md:31>) 的 T2.3 只列 agent/worktree 寫入，T6.1 是觀察，T6.2 只列 publish/Pass。R3 假設 PR 已能建立，但沒有明確 owned task 與公開入口驗證「G1→push→建立或核對唯一 PR→record PR identity」。

最小修正是在現有 git/GitHub 任務內指定這條正向路徑及 fake 測試，並保留 unknown 不盲目重送；不另加管理層或新 subsystem。

### AC-A05：純讀取的重試耗盡路由需寫清楚（中）

D16 要求同一 infra 操作初次＋兩次額外嘗試後 Blocked；design 現在只寫純 fetch「每次呼叫最多 3 次」。需明定連續傳輸失敗耗盡後停止自動呼叫，不能用新 seq／新 session 重新取得同一失敗的三次機會。合法 pending polling 與失敗 retry 要分開。只需清楚的失敗紀錄／停止規則，不恢復純讀取 prepare/begin 協定。

### 驗證規則的補充建議（非新增產品 blocker）

- V1–V9 的「failure/error/skipped 全為 0」應界定為**本環境適用的必要測試集合**。平台專屬 case 可分流到對應 CI job；不可靠跳過必要測試變綠，也不應將有明確 Linux owner 的測試在 macOS 不適用誤判成產品故障。
- G05 的文件／程式版本分離、F13 的 GitHub read-back 內容、Project 的 DOC rubric 需要具體通過標準；不是只列檔名或輸出 URL。
- D10 的 history-first 是設計選擇；頂層 AC 應主張已確認 state 不丟、不重複、不接受未提交事件。具體提交順序留給相應行為／crash 測試。

## 3. 實現狀態：分四層看

| 層次 | 本次核對結果 | 能否算新版交付 |
| --- | --- | --- |
| Workflow / SA 文件 | docs/workflow、決策與交接文件存在 | 是方法文件；沒有正式 skill 執行驗收，不等於 runtime 功能已完成 |
| Herdr / runtime probes | H0 曾有 Luna/OpenCode、Sonnet/Claude Code 真實小型交接；本次 Opus 也完成文件交接 | 部分底座能力證據；不替代正式權限 profile、G1/G2/G3 或 delivery E2E |
| 舊 `src/delivery` | 有 21 個 Python 模組與測試；部分 CLI 可改本地狀態，但 runtime adapters 空、完整 loop 未接入生產 CLI | 歷史候選／重用材料；17 blocking findings 仍未關閉，不能直接搬成果 |
| 新 `loop-engineering-thin` | 實際只有 README 與 docs；不是 git worktree；無 src/tests、pyproject、CI、orchestrate SKILL | 新 controller 尚未實作；新產品 AC 尚無驗收證據 |

程式查核依據：舊 [CLI 的 AVAILABLE_RUNTIMES](../../../src/delivery/cli.py:33) 是空集合；[cmd_reconcile / cmd_resume](../../../src/delivery/cli.py:245) 只做本地核對或回 adapter unavailable。`loop.step/run_until_idle` 的呼叫端在 tests；`resume.resume` 也只見測試呼叫，不是已接好的正式外部 loop。[test_controller_e2e.py](../../../tests/test_controller_e2e.py) 組 synthetic review/CI；[fake_agents.py](../../../tests/fake_agents.py) 是腳本式 fake。名稱含 E2E 不能當真實 agents＋GitHub 的 E2E。

### 本輪實際執行

1. 在現行舊程式 HEAD `4ce111011fde83c3a2784402cea111e52a954b3c` 跑 `uv run --offline pytest -q`：**226 passed、1 failed、1 skipped**。失敗是本次我指定的 PATH 沒包含 `/usr/local/bin/gh`，不是已證實的產品錯誤。
2. 保留系統 git 優先並補回 `/usr/local/bin`，只重跑失敗的 credential probe：**1 passed**。沒有修改程式、放寬斷言或排除測試。這不是宣稱整套在同一次重跑得到 227 passed。
3. 一項 skipped 是 `test_blob_and_dir_fsync_precede_snapshot_rename`，本機 macOS 不適用，測試明示由 Linux＋strace CI 負責。本輪沒有在 Linux 重跑。
4. **直接重現 S1-R11**：用合成 Green 呼叫舊 `evaluate_g1([], green, head, ...)`，實際得到 `{status: passed, tasks: {}}`；合理預期是不通過。這是受控反例，不是真實 gate evidence。說明正常測試大量通過仍有必要 AC 缺陷，不可無條件重用 gate 邏輯。
5. 唯讀查回 [PR #2](https://github.com/yschiang/loop-engineering/pull/2)：仍 OPEN、未 merge，head 同上；所見兩次 CI runs 的 linux/macos/test 均 SUCCESS。它是舊 head 的 checks，不是新 checks 集合或新 G3 通過。舊獨立 review 的 17 項 findings 在保存结果中全為 open；未發佈本審核到 GitHub。

工具觀察摘要與反例：[execution-summary.json](execution-summary.json)。本輪建立了本機 `.venv` 並執行舊測試，沒有產品碼或正式規格修改；沒有啟動新 native agent、修改 gigaxfer 或執行 example。

## 4. 建議下一步

先處理 AC-A01 的規格差異、AC-A02 的核心驗證缺口、AC-A03 的錯配，再補 A04/A05 的交接與停止規則。把 17 條 Workflow 契約交由 skill／人工樣本驗收，把 6 條後續能力維持 deferred，歷史 P03 限制留在交接記錄。

**保留品質要求，修正歸屬與驗法；不要因「88 AC 都要 cover」把平台 scope 加回來。** 完成這些最小修訂再作 D11；本次只有審核結果，沒有自行改寫需求或重新派產品開發。
