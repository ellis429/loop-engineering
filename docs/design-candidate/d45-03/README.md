# D50：薄 controller 精簡候選

> **後續 AC 全面審核（2026-09-27）**：[合理性／驗法／實現狀態審核](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-27-ac-audit/README.md) 發現 CI 語意差異、驗法缺口及 runtime 覆蓋錯配，建議先修訂再 D11。下文 ready_for_human_review 是先前七項定點修正的結論，不是 88 AC 全數驗證充分。


**文件覆核完成，ready_for_human_review；尚未 D11、未開始產品實作。**

先看 [切片與任務](tasks.md)，再看 [設計](design.md)。[最新獨立審查](review.md) 已覆核本次七項修正，沒有未解阻擋；這是限定範圍文件 review，不是產品 G2 或全部需求已驗收。

## 執行順序

1. **前置能力查核**：核對正式 profiles、原生結果、Reviewer 權限及停止能力；缺能力就回報，不自建執行平台。
2. **Bootstrap PR（T0–T7）**：在隔離 worktree 建立最小 orchestrate、薄 controller 與必要工具。先測困難狀態；worker 觀察及停止／預算可用後才做真實 writer probe。此 PR 本身仍需三 gates。
3. **第一個真實 feature loop（T8）**：B1 人工接受、實際 merge、採用 baseline 後，依 D11 確認小 feature，再跑真實 finding → fix → re-review、CI 與中斷接續。候選是 `loopctl status --human`。Blocked 是安全停止，不算 demo 完成；沒有真實 finding 就保留未覆蓋。
4. **後續 outline**：adopt、跨 feature／Project 自動化、多人與 cross-node-file-transfer。Stacked PR 政策仍未定，不自動啟動 example。

Task 是派工單位，不等於 PR。以上第 2、3 步明確區分 controller 開發證據與工具完成後的自我託管證據。

## 這次實際刪減

- 序列 tasks／fix 共用 feature Implementer worktree，Reviewer 獨立；不再每 attempt 建 worktree 並整合。
- 唯讀查詢不使用寫入操作生命週期；仍保留有界 fetch、版本順序、raw evidence。
- 歷史 Red replay 只作診斷；原始 Red 與目前 Green／regression 維持必要。
- Project／跨 feature 等自動化延後；owner 與義務在 coverage 明示，不冒充完成。
- 重用依行為規則或提取 commit 追溯，移除逐 symbol 清單及每模組 caller 硬 gate。

## 文件與方法

| 文件 | 用途 |
| --- | --- |
| [design.md](design.md) | 新版完整候選設計，取代 D45-02 design |
| [tasks.md](tasks.md) | 可派工路徑、相依、介面、驗法；後續 S2/S3 只有 outline |
| [validation.md](validation.md) | Fake／真實證據分開、具體 CI 候選、demo 成功條件 |
| [spec-delta.md](spec-delta.md) | 相對 [D45-02 delta](../d45-02/spec-delta.md) 的精確修訂，正式 specs 尚未套用 |
| [coverage.md](coverage.md) | 88 AC＋17 舊 findings；owner／切片／驗證對照，全部 planned |
| [cleanup-map.md](cleanup-map.md) | 隔離重建與選擇性重用；不把刪除視為 finding closure |

Opus 5.5 產出設計與 plan，GPT 獨立 review。協作者以 Matt `codebase-design` 檢查介面與必要性；OpenSpec 管理規格差異，Writing Plans 6.4.1 的適配方法提供任務 scope／依賴／驗證，不另寫平行權威 plan，也不另啟 Superpowers 外層 loop。本輪尚未安裝或實作 `orchestrate` skill。

## 開工前仍須收斂

依 [D11／D50](/Users/johnson.chiang/workspace/loop-engineering/docs/decisions.md)，本候選仍需一次具體採用／開工確認：spec/design/tasks、W1 工作區接合與 CI 集合；Reviewer 精確 model 與執行 timeout 設定須明定。CI 候選是 `unit-linux`、`unit-macos`、`static`（含 wheel 安裝 smoke），只有最新 head 的實際成功結果可通過。完整待決項見 [作者結果](result.json)，它保留提交當時 pending 狀態，最新文件 review 以 [review-result.json](review-result.json) 為準。

舊 17 項 S1 findings 全部仍 open。未執行產品測試、建立 worktree、push、發 GitHub 訊息或初始化 example。

[第一輪審查](reviews/review-10.md) · [第二輪定點覆核](reviews/review-11.md) · [最終覆核](review.md) · [發布來源對照](publication-manifest.json)
