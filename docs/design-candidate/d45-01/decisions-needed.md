# Decisions needed（D45 候選 design-01，分段交付）

> 本文只列會**改變既有 AC 或承諾**、因此必須由使用者決定的三項。以下項目不重問，也不在本文處理：
> - D45 的 Herdr 選型、D44 的 runtime 接法、D46 的隔離工作區；
> - Q-STACK、Q-DEMO-PEOPLE：維持原待決狀態，不阻擋單 feature 切片。
>
> 技術細節（operation 許可、feature 單一狀態、typed refs、history-first 提交、Pass 前觀察等）由設計自行處理。未決前，相關 AC 維持原文且不標完成，相依 tasks 標為 blocked。

## DN-1：協調 session 離線時，4 小時 active 上限怎麼執行

**為何需要決定**
- D13 與 AC-D17 要求到 4h 就停止新派工，並處理仍有執行權的 worker。
- D41 取消常駐 supervisor 後，controller 只在被呼叫時運作。協調 session 在線時，可以用有界等待（每次最多約 60 秒）加上 deadline 及時停止。
- 但若 session 關閉或主機睡眠，沒有程序會在 4h 那一刻停下 worker；要等到下次呼叫才會發現超時（S1-R09）。
- 另外，H0 已觀察到 Claude Code 收到 `ctrl+c` 後程序仍在；停止必須以 process-info 確認。

| 選項 | 內容 | 影響 |
| --- | --- | --- |
| **A（推薦）** 線上即時、離線事後如實處理 | 線上：有界等待加每個派工的 `deadline_at`，到時只允許 stop，且以 process-info 確認停止。離線：下次呼叫把整段期間保守計入 active time，記錄 `overrun` 秒數，只允許 stop，然後 Blocked 交人。AC-D17 補寫「協調 session 離線期間不保證即時停止，恢復時計入並 Blocked」 | 不新增常駐程式。承諾在離線時明確變弱，但超時不會被隱藏，也不會繼續派工 |
| B 每個 worker 自帶硬截止 | 在 A 之外，用 runtime 參數或程序 alarm 包住 worker，時間到就由 OS 結束它 | 離線時也能停止 worker 程序。需要在 H2 先 probe 確認 Herdr `agent start` 能包 wrapper；worker 被強制中斷後，常會留下 outcome_unknown 需要人處理；程式也比 A 多 |
| C 維持原本的全時硬截止 | 要一個常駐 watchdog（例如 launchd） | 違反 D41「不另起常駐 supervisor」；不建議 |

**推薦 A**：它不增加平台責任，且把弱化部分寫進規格、做成可觀察的紀錄。若日後需要更強保證，B 可以另開一項評估。B、C 會增加平台責任，只能經你明確選擇才採用，不作預設 fallback。

無論選哪一項，線上時到 deadline 都能對已知 active worker 發 stop，即使 feature 已因其他原因 Blocked（design §9，D45-R02）。

**受阻**
- AC-D17 的 spec 修訂文字，以及其 validation 通過標準；
- S1-R09 的處置；
- budget／overrun 相關 tasks 中與離線行為有關的步驟。

線上計時、gap 計入與「到限拒絕派工」不受影響，可以先做。

## DN-2：證據與狀態的信任邊界

**為何需要決定**
- 舊 v3 用自建 OS sandbox 禁止 worker 寫 controller 狀態、讀 credentials（AC-D02、DUR-02 的原實作前提）。D41 已排除自建 sandbox。
- 在同一 OS 使用者之下，只要能繞過 runtime 權限，程序就可能：
  - 讀到協調 token；
  - 改寫 `$LOOPCTL_HOME`；
  - 偽造 evidence 物件；
  - 以人工身分呼叫 `decide`；
  - 移動共用的整合 ref。
- 歷史 Red 也只能證明 snapshot 是 lineage 上、以核准命令真實失敗的狀態；無法用機械方式證明 worker 在 session 中確實先寫了測試。

| 選項 | 內容 | 影響 |
| --- | --- | --- |
| **A（推薦）** 防誤用且可偵測，不防同權限惡意 | 協調 token 只存雜湊；每個 revision 有歷史與 hash chain；手改會被偵測、不當決策；整合 ref 被移動會 Blocked。Worker 與 Reviewer 的 runtime 權限設定（Claude Code／OpenCode 內建）禁止呼叫 `loopctl` 狀態命令、`git push`、`gh`、`herdr`，也禁止寫出自己的 worktree／inbox，並在 H2 以真實負例驗證，未驗證就 Blocked。Red 由 coordinator 從 snapshot replay，Reviewer 再從 native transcript 核對「測試先於實作」。規格明示不抵抗同主機同權限的惡意偽造 | 不自建平台，並保留所有偵測與 fail-closed 行為。AC-D02 與 DUR-02 需要補寫這條信任邊界 |
| B 以 OS 帳號分離 | Worker 以專用 OS 使用者執行，controller 狀態與 credentials 只屬於協調者帳號（用現成 OS 功能，不自建 sandbox） | 防護最強。需要建立帳號、調整 Herdr／runtime 的啟動方式與檔案權限，會增加 H2 的平台工作 |
| C 只記錄，不要求權限驗證 | 只做偵測，不要求 runtime 權限負例通過 | 會削弱 AC-G12 與 DUR-02；不建議 |

**任何選項都不變的前提（reviewer 澄清）**：
- 原始歷史 Red 仍是 G1 的必要條件。worker 在實作前捕捉的 raw output、exit code、task／attempt、snapshot 與 provenance 缺一項就不通過。
- Coordinator replay 與 transcript 核對只作**補充**，不能取代或補造原始 Red。
- 接受同 UID 的威脅邊界，不代表允許用重建或事後 replay 的 Red 通過 G1。

**推薦 A**：它符合 D41 的收斂方向，也把弱化部分寫明。若要示範給多人或跨團隊使用，可再評估 B。B 會增加平台責任，只能經你明確選擇才採用，不作預設 fallback。

**受阻**
- AC-D02、DUR-02 的 worker 限制文字（AC-D03、D04 不受影響）；
- AC-G04／G07 的「可信程度」說明；
- H2 的 Reviewer／Implementer 權限能力報告的通過標準；
- S1-R01、R13 closure 時所需的真實 probe 範圍。

H1 的 token、歷史 chain、手改偵測與 Red 逐項驗證不受影響，可以先做。

## DN-3：GitHub required-check 規則讀不到（HTTP 403）時，G3 能否放行

**為何需要決定**
- GAT-06 與 AC-G13 要求必要 check 集合「與可讀 repo 規則核對」，而且 unknown policy 不能通過。
- 本 repo 的 branch protection／rulesets API 回 403（S1 紀錄；Q-S1-CI-POLICY 尚未回答）。
- 既有 CI job 成功，和「必要 check 政策可查證」是兩件事。
- 設計已固定兩點，都不需要決定：
  - 403 時 G3 為 unknown 且 Blocked，並且**不**消耗修正輪（S1-R14）；
  - 例外只接受有核准的 skipped／neutral（S1-R17）。
- 需要決定的只是：H2 能不能在 403 下到達 PR Pass。

| 選項 | 內容 | 影響 |
| --- | --- | --- |
| A 讓 rules 可讀 | 由使用者調整 repo 權限或方案，讓 API 可讀 | 規格不改。需要使用者在 GitHub 側處理，也可能有成本 |
| **B（推薦）** 明確宣告必要 check 集合 | 以人工 `policy_change` decision 宣告本 repo 的必要 check（例如 GitHub Actions 的 `test`），並記錄 403 證據與理由。G3 只核對宣告集合，PR Pass package 會明示「GitHub rules 未核對」。可撤回；不適用其他 repo；不會自動套用 | GAT-06 與 AC-G13 需加一段有條件的例外文字。放寬幅度可見、可追溯 |
| C 維持 fail-closed | 403 時永遠不可 PR Pass | 規格不改，但 H2 無法完成 PR Pass 驗收；A13 情境只能列為未覆蓋 |

**B 的邊界（reviewer 澄清）**：
- B 是本 repo 範圍、帶版本的人工 policy 例外，在狀態與 Pass package 中和「已核對的 GitHub rules」分開標示。
- 收到 403 **不會**自動改用宣告集合；`test` 只是範例名稱，不構成核准。沒有這筆人工 decision 前，G3 維持 unknown 並 Blocked。
- 協調者補充的 `ci-policy-recheck.json` 確認這次 403 是方案限制。舊 CI 成功只是執行證據；舊的 macOS sandbox job 也不能證明新的 runtime profile。

**推薦 B**：它以明確、可稽核的決定取代默認，而且不增加 GitHub 權限成本。若使用者願意處理 A，A 更好，規格也不必動。

**受阻**
- GAT-06 與 AC-G13 的 spec 修訂；
- H2 的 PR Pass 任務；
- S1-R14、R17 的真實 GH 驗證。

G3 的 route 分類、例外核對與 fake 測試不受影響，可以先做。

## 回覆方式

請對每項回覆選項代號，例如「DN-1 A、DN-2 A、DN-3 B」。可以附條件。

收到回覆後，才展開相依的 spec-delta、tasks 與 validation；在這之前不視為已核准，也不派產品實作。
