# D45-04：AC 審核修訂後的設計候選

**狀態：D51 AC 修訂已完成 GPT 覆核；另一次 Opus 5.5 review 要求修改（6 項 major、10 項 minor）。目前尚未實作，也未通過 D11。** 本版依 D51 處理 [88 AC 審核](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-27-ac-audit/README.md)，保留 D50 的精簡範圍。Opus 5.5 撰寫，獨立 GPT 初審與覆核；不以文件通過代替產品 gates。

## 最新 Opus 5.5 review（2026-09-28）

Opus 5.5 對固定快照的 verdict 為 `changes_requested`；沒有 blocking 等級項目，但列出 6 項 major、10 項 minor findings。完整報告見 [Opus review](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-28-opus-review-d45-04.md)。Finding 尚未套用，D11 維持 pending。

## 這次改了什麼

- CI：修正 D49 的 403／已批准政策路徑，首片只接受 head 來源；明確辨識 workflow 與最新 attempt。
- 核心驗法：補齊 gate 獨立性、版本失效、Red 適用性、finding 覆核、漏通知／重啟與發布接續的情境。
- 任務：指定 G1 → push → 唯一 PR → review 的責任與相依；讀取重試耗盡不因 session 重置。
- Workflow：17 條契約使用共享正反樣本及 rubric，不新增逐樣本人工簽核。
- **刪除**逐測試登錄／自訂彙整工具與額外簽核；**延期**仍有需求的 adopt、委派、Retro、自動跨 feature、其他 runtime 配置與 integration SHA 映射。延期不算完成。

## 閱讀與交接

| 文件 | 用途 |
| --- | --- |
| [Design](design.md) | 責任、公開介面、gates、失效與停止規則 |
| [Tasks](tasks.md) | 第一片的 owned paths、相依與完成條件 |
| [Validation](validation.md) | 產品矩陣、workflow rubric、真實 R1–R3 與候選 CI |
| [Spec delta](spec-delta.md) | 對 D45-02 基準的現行覆寫；尚未採入正式 OpenSpec |
| [Coverage](coverage.md) | 88 AC 與 17 舊 finding 的逐項歸屬；全部 planned／open |
| [Cleanup map](cleanup-map.md) | 隔離重建與選擇性重用 |
| [獨立覆核](review.md) | 本版適用範圍與 finding 結論 |
| [文件核對](document-check.json) | ID 完整性、原始產品／spec／歷史快照未改 |

本版取代 D45-03 作為現行候選。舊稿、初審及修訂記錄保留追溯，不是並行的實作計畫。原始固定快照與可閱讀版的差異只允許基準連結轉換，見 [publication manifest](publication-manifest.json)。

## 開工前仍待定

具體 design＋plan 的 D11 確認、Reviewer 精確 model、CI check 集合與 timeout 預設。W1 尚未執行；此目錄仍不是 Git worktree。正式 OpenSpec 維持 scope revision pending，須依採用的候選同步後開工。

Bootstrap B1 與後續 T8 分開驗收。T8 要另選 B1 尚未實作的有界功能並有自己的 D11；須等 B1 人工接受、實際 merge、baseline 採用後開始。PR Pass 不自動 merge。真實 finding → fix → re-review、目前三 gates、成功接續缺一，示範都維持未完成。

此次沒有產品碼／產品測試、GitHub 發文、gigaxfer 修改或 example 啟動。既有 H0 與舊測試不能轉作新版驗收證據。
