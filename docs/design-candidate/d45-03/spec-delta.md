# Spec delta：D50 替換語意（候選 design-03）

> **狀態**：候選，未 D11，未套用正式 specs。
> **基準**：[D45-02 spec-delta](../d45-02/spec-delta.md)（D45-02 已審的版本）。本文只替換下面列出的段落，其他條文沿用該基準。
> **不變的部分**：88 個 AC ID 全部保留，沒有新增 AC，也沒有刪除義務。
> **D50 的差異只有兩類**：
> - 實作機制簡化；
> - 自動化的時點延後：由 skill 或人承擔，controller 只記錄。
>
> 沒有放寬任何品質判定。

## 1. DUR-06：外部寫入與唯讀觀察分開（取代基準版 DUR-06 的補充段）

> 外部寫入限於有限的種類（派工、prompt、stop、worktree 建立、push、PR／issue 發布）。每種都 SHALL 先登記，再只被一個呼叫者執行一次，並保存 receipt。
>
> 結果不明時，只讀回原操作，SHALL NOT 重發。以下情況 SHALL NOT 單獨作為重試證明：查不到效果（not_found）、client 已結束、經常駐 server 或遠端處理的請求。只有已記錄確定未送達，或已驗證原生冪等時，才可重試；否則 unknown，並 Blocked 交人。
>
> 每次自動讀回都 SHALL 計入上限，到限就停止自動讀回。
>
> 唯讀觀察（CI、PR、worker 狀態、native 紀錄）SHALL NOT 需要執行許可，SHALL 以有 timeout 與重試上限的方式取得。
>
> 每次取得之前，SHALL 先持久化一個單調遞增的順序識別，匯入時 SHALL 依此順序，而非完成時間。observation SHALL 分開保存請求脈絡與觀察到的 head／base／binding 事實，並保留來源與 raw 證據。
>
> 共用的版本事實（head、base、merge_base、binding digests）SHALL 以一個 feature 層級、跨所有目的的順序水位保護。只有順序比水位新的觀察 SHALL 更新這些事實並推進水位；事實改變時 SHALL 使相關 gates 與 Pass 失效，即使該請求是以舊版本發出。順序不比水位新的晚到觀察，不論目的為何，SHALL NOT 改寫共用版本事實或恢復舊版本。
>
> 各目的的結果快取 SHALL 分開保存。快取結果 SHALL NOT 重定共用版本，也只有在它觀察到的版本等於目前版本時，才可作為 gate 依據（D50-R02）。

差異：基準版把首次唯讀觀察也納入 begin，本版撤回這一點。R01 的單一執行者規則與 S04 的「重新觀察」反例，都改在本段的新語意下驗證（validation V4、V7）。

## 2. DUR-02：workspace（在基準版末尾加上）

> 第一個可用切片中，每個 feature SHALL 只有一個 Implementer worktree，tasks 與 fix 依序執行。
>
> - 前一個 attempt 未確認結束時，SHALL NOT 派下一個；writer 狀態 unknown → Blocked。
> - Reviewer SHALL 使用獨立的 clone 與 session。
> - 需要平行 writer 時，SHALL 另外定義隔離與整合規則，並經 D11 確認後才可採用。

## 3. GAT-03：replay 與整合追溯（取代基準版 GAT-03 的補充段）

> 歷史 Red SHALL 為實作前捕捉的原始紀錄：raw output、exit code、task／attempt、snapshot 與 provenance 缺一不可，並逐項核對。
>
> - 最終 Green 與 regression SHALL 由協調方以核准的 policy 命令，在整合 head 執行。controller SHALL NOT 執行 worker 提供的命令。
> - Coordinator replay SHALL 只在證據矛盾，或有特定風險時執行，作為診斷；replay 與 transcript 都 SHALL NOT 取代或補造原始 Red。
> - task 的追溯 SHALL 以 attempt 的 commit 範圍（必須在 scope 內）連到整合 head。

AC-G06、AC-G08 的「task commit→integration commit 對應」改讀為「attempt 的 commit 範圍→整合 head」。

**AC-G06：刪除基準版所加的 replay 句子（D50-R06）**。基準版 `review-09/spec-delta.md:110` 為 AC-G06 THEN 加上「coordinator 以核准命令從 R 重放得到相同失敗，只作為佐證」，本版**整句刪除**。AC-G06 THEN 回到原始 spec 的文字，並補上：

> 正常路徑不需要 replay。只有證據矛盾或有特定風險時，才以 replay 作診斷；replay 不能補造原始 Red。

原始 Red、scope／lineage、目前的 Green 與 regression 仍然必要。AC-G07 不變。

## 3a. GAT-05：G2 判定（補充，不放寬 AC-G11）

> G2 SHALL 只在以下全部成立時通過：經授權的獨立 Reviewer、對目前版本完整 PR diff（base…head）與適用 spec／design／AC 及先前 findings 所做的 review、verdict 為 `clean`、沒有未解的 blocking finding。
>
> `changes_required` SHALL 為 failed；`blocked` SHALL 為 unknown，且不開修正輪。缺 verdict、格式錯誤、只審部分 diff，SHALL NOT 通過（D50-R03）。

## 3b. ORC-06：bootstrap 到第一個 feature 的交接（補充）

> 依賴 controller 本身的第一個交付 feature，SHALL 在 controller 的 bootstrap PR 經人工 accepted、實際 merge，並登記採用的 baseline 之後才開始實作；SHALL NOT 自動 merge。在此之前的真實執行只算隔離的能力 probe（D27、D50-R04）。

## 4. ORC-04／ORC-06／ORC-07／ORC-01（委派）：自動化時點（在各 requirement 末尾加上）

> 第一個可用切片中，adopt、跨 feature 依賴解除、Retro 候選產生，以及 Project Lead 的委派路由，由 workflow／skill 與人依既有契約執行，controller 只記錄相關 decision 與證據。
>
> 尚未支援的 controller 入口 SHALL 明確回 `unsupported`。它 SHALL NOT 讓任何路徑略過 D11、G1、依賴（D27）或 owner 的核對，也 SHALL NOT 把這些情境標為已完成。

受影響的 AC：O08、O09、O12、O13、O14、O18。它們的義務保留，實作在後續切片（見 coverage）。

## 5. DUR-08（補充）

讀回上限只適用於外部寫入；唯讀觀察依 §1 的 fetch 重試上限。D47 的語意不變。

## 6. 仍有效且不再重述的基準條文

以下條文沿用基準版：
- D45-S01／S05：文件缺陷可修正，G1 失敗可在正式 review 前修正；
- S02：信任邊界；
- S08：`tested-sha`；
- S09：bootstrap gates 的區分；
- D47–D49 相關條文。
