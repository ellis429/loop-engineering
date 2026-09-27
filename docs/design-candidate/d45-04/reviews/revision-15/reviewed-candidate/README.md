# D45-04：AC 審核修訂後的設計候選

**狀態（revision-15）：本表是目前唯一的 review 狀態來源；其他文件開頭只標作者提交的版本。revision-15 由 Opus 5.5 主持，依 D52 與 Herdr 交接補上具體執行預設、內部介面契約與派工缺口；獨立覆核見下表。目前尚未實作，也未通過 D11；沒有任何產品檢查已通過。** 要你決定的事集中在 [D11 確認包](d11-confirmation.md)。本候選依 D51 處理 [88 AC 審核](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-27-ac-audit/README.md)，保留 D50 的精簡範圍；不以文件通過代替產品 gates。revision-14 的 `clean` 只適用 revision-14，已保存在 [reviews/revision-14-publication](reviews/revision-14-publication/)。

## Review 狀態

| 版本 | Review | 結論 | 適用範圍 |
| --- | --- | --- | --- |
| revision-15（本版） | 獨立覆核進行中（GPT-6 Astra xhigh，fresh session） | pending | 結果寫入 `reviews/revision-15/`，完成後更新本列 |
| revision-14 | [Astra xhigh 獨立覆核](reviews/revision-14-publication/review.md) | `clean`：原 16 項及 R12-01／R12-02 全部 verified | 歷史；限該批文件修正，不涵蓋 revision-15 |
| revision-13 | [review-02](reviews/revision-13/review.md) | `changes_requested`：原 16 項與 R12-02 verified，R12-01 路徑優先序仍待修正 | 歷史；revision-14 已回應 |
| revision-12 | [review-01（獨立覆核）](reviews/revision-12/review.md) | `changes_requested`：原 16 項中 15 項 verified，M5 有一句規範措辭殘留；另有 2 項設計阻擋（R12-01、R12-02） | 歷史；15 項 verified 是 review-01 的結論，本版已回應其餘 3 項 |
| Opus 審查時的固定快照 | [Opus 5.5 review](/Users/johnson.chiang/workspace/loop-engineering/docs/reviews/2026-09-28-opus-review-d45-04.md)（2026-09-28） | `changes_requested`：0 blocking、6 major、10 minor | 歷史；本版已回應 |
| 更早的版本 | GPT review-15（[前一版覆核](reviews/review-15/review.md)） | 已關閉 D51-R01–R07 | 歷史；與上面 16 項不同，不適用本版 |

舊 review 與報告保持不變，只作為前一版的紀錄。

## 這次改了什麼

### revision-15（Opus 5.5 主持）

- **D52 對齊**：tasks 新增「派工與模型」，區分 bootstrap 開發分工與產品 profile；B1 的 G2 改為「與所有 Implementer 不同實際模型的獨立 Reviewer（預設 GPT-6 Astra xhigh）」。
- **具體執行預設（待 D11）**：產品 profile（design §6）、角色 timeout 與 active 區間（design §10）、讀取與寫入的時限與輪詢（design §4、§5）、CI 與 `workflow.yaml` 全文（validation §6）。
- **W1 改從 `origin/main` 出發**：避免新 lineage 含 PR #2 的 head `4ce1110`；目前未提交的文件原樣提交為 A0，再組成正式 spec；建議先以 docs PR 進 main（tasks T0.1）。
- **spec-delta 可機械組合**：每個覆寫寫明取代範圍，會自相矛盾的 scenario 改寫為全文（AC-D10、AC-D23、AC-G13、AC-G15、AC-O15、AC-O23、GAT-06），新增組合規則 §12；保留 D45-02 的「Green 在獨立 checkout」。唯一收窄：移除 D45-02 的「本機同步程序」重試例外。
- **可派工**：內部契約（store、op 紀錄、assignment、review result、`next` 動作詞彙）；共用檔案補上 `cli.py`、`tools/herdr.py`、`next.py`、`writes.py`；消除三處往後相依（d7、g6、h13）；每個 task 有派工卡。
- **驗法**：新增或強化約 20 個案例（s7、d7a／d7b、d10、o3、w2、w8、w11、g5、g6、g14、h8、h10、h11、h13、r1、r10、r13、p4、p6、p7、b2–b4、f4、f5），R1／R2 的通過標準改為正向結果。
- 依據：兩個 GPT-6 Sol high 的有界查核（`.delivery/herdr-design-plan-20260928/helpers/`）與協調者自查；處置見 [revision-15.json](revision-15.json)。

### revision-14（協調者修正）

- 先判斷任一必要 gate 是否無法取得，再決定等待；只有 G1 適用且 G2／G3 各有終態或有效在途結果才收齊。預算與安全條件仍優先，混合狀態由 r12b 驗證。

### Opus revision-13

- **M5**：spec-delta 的 skip 規範改用 design 的原句「任何不是由 `only_on` 在非所屬平台產生的 skip」，與 t1 的 exit 0 一致。
- **R12-01**：整合需求有明確的決策界線。在途且有效的 review／CI 照常收齊；其他情況立即走既有的 `pre_review_g1`（原因 `base_integration`），不等待無法開始的 G2 或因衝突不會出現的 CI，缺少的 CI 不算成功。整合 finding 以（base、B、H）去重。整合後的新 head 需要完整的三 gates。
- **R12-02**：整合 assignment 釘住先前的 head 與確切的 base tip。以 `git merge-tree` 重算自動合併結果，把原樣匯入和作者編輯分開：純匯入不需補造上游 Red；作者編輯受 scope 限制，改變行為要有綁定整合 finding 的 Red；藏在匯入裡的範圍外編輯被拒收。
- **說明**：每個 job 同一 attempt 的產物是保守規則，只重跑失敗 job 時可能需要改為重跑全部；controller 不新增 rerun 功能。

## revision-12 的修正（review-01 已覆核）

- **CI（M1、m6、m8）**：候選 workflow 只由 `pull_request` 觸發，綁定已記錄的 PR 與 head；事件或 PR 不符 → unknown。每個 run 取最新 attempt，同一 head 的多個 run 都計入。每個 job 上傳自己的 tested SHA 產物。政策檔定名為 repo 根目錄的 `workflow.yaml`，由 T1.1 擁有。
- **Red（M2、m3）**：改變行為的修正（含 `pre_review_g1`）需要綁定 finding 與 batch 的原始 Red。被放棄的 attempt 的 Red 不轉移，缺原始 Red → Blocked，不製造 Red。N/A 依實際行為判定，不按檔名排除。
- **Branch 歷史（M3、m5）**：受控 run 只做 fast-forward push，整合 base 用本機 merge commit（不是 GitHub PR merge，也不需要 merge 權限），歷史被外部改寫 → Blocked。整合只在衝突、Reviewer 判定不相容或人工決定時進行（路徑由 revision-13 修訂）。
- **任務（M4、m4）**：通用觀察與 `worker`／`native` 讀取移到 T2.3，共用檔案依序擁有。T0.1 在 D11 之後、B 之前採用完整的正式 spec 基準，並讓舊 design／tasks 退為歷史。
- **測試政策（M5）**：本機與每個 CI job 用同一份 test-only 的 pytest 設定，不是產品 hook，也不是 registry。
- **PR（M6、m7）**：`pr_ensure` 先持久化完整預期身份與 marker；身份不符 → Blocked，不另建。`resolve_operation` 只記錄，查無不算未送達的證據。
- **其他（m1、m2、m9）**：Pass package 由狀態投影；O23 的部分接續明示延到 S2；G2 `blocked` 使 feature Blocked。

## 閱讀與交接

| 文件 | 用途 |
| --- | --- |
| [D11 確認包](d11-confirmation.md) | 要你決定的具體預設與問題 |
| [Design](design.md) | 責任、公開介面、gates、失效與停止規則 |
| [Tasks](tasks.md) | 第一片的 owned paths、共用檔案順序、相依與完成條件 |
| [Validation](validation.md) | 產品矩陣、workflow rubric、真實 R1–R3 與候選 CI |
| [Spec delta](spec-delta.md) | 對 D45-02 基準的現行覆寫；尚未採入正式 OpenSpec |
| [Coverage](coverage.md) | 88 AC 與 17 舊 finding 的逐項歸屬；全部 planned／open |
| [Cleanup map](cleanup-map.md) | 隔離重建與選擇性重用 |
| [revision-15.json](revision-15.json) | 本版每項修改的來源（helper finding 或自查）、影響章節與案例 |
| [revision-14.json](revision-14.json) | 協調者最後一處優先序修正與來源；已獨立覆核 |
| [revision-13.json](revision-13.json) | Opus 3 項修正的處置、影響章節與規劃中的案例 |
| `revision-12.json` | 歷史：16 項 finding 的處置（review-01 已覆核） |

本版取代 D45-03 作為現行候選。舊稿、review 及修訂記錄保留追溯，不是並行的實作計畫。文件核對與 publication manifest 由協調者在核對本版後產生；舊版的相同檔案不適用本版。

## 開工前仍待定

[D11 確認包](d11-confirmation.md) 的 A–F 與三個問題。W1 尚未執行；此目錄仍不是 Git worktree。

D11 之後，T0.1 以正式 specs＋D45-02 基準＋本版 spec-delta 依其 §12 組成完整的正式 spec，經獨立核對後採用；正式 change 內的 D40 舊 design／tasks 同時退為歷史，不再與採用版本競爭。完成後才建立 B 與派工。本版 spec-delta 不能單獨套用。

Bootstrap B1 與後續 T8 分開驗收。T8 要另選 B1 尚未實作的有界功能並有自己的 D11；須等 B1 人工接受、實際 merge、baseline 採用後開始。PR Pass 不自動 merge。真實 finding → fix → re-review、目前三 gates、成功接續缺一，示範都維持未完成。

此次沒有產品碼／產品測試、GitHub 發文、gigaxfer 修改或 example 啟動。既有 H0 與舊測試不能轉作新版驗收證據。
