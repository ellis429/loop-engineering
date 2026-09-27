# Spec delta：現行覆寫（候選 design-04）

> **狀態**：候選，未 D11，未套用正式 specs。
> **基準**：[D45-02 spec delta](../d45-02/spec-delta.md)（D45-02 版）。本文列出**目前所有**對該基準的覆寫，已包含 outputs-03 的內容與這次 AC audit 的修正。沒列在這裡的條文，沿用基準。
> 88 個 AC ID 全部保留：沒有新增 AC，也沒有刪除義務。

**標記說明**
- **[D50]**：機制簡化或自動化時點延後。
- **[A0x]**：AC audit 的修正。
- **[延後]**：後續切片的能力，第一片不算完成。

## 1. DUR-06：外部寫入、唯讀觀察、讀取失敗預算 [D50]、[A05]

> **外部寫入**限於有限種類：worktree 建立、派工、prompt、stop、push、PR ensure、PR 與 issue 發布。每種 SHALL 先登記，再只被一個呼叫者執行一次，並保存 receipt。結果不明時，SHALL 只讀回原操作，SHALL NOT 重發。以下情況 SHALL NOT 作為重試證明：查不到效果、client 已結束、經常駐 server 或遠端處理的請求。只有在已記錄確定未送達，或有已驗證的原生冪等時，才可重試；否則 unknown 並 Blocked。以查詢判斷 PR 是否存在 SHALL NOT 視為冪等：建立 PR 的結果不明、之後又查不到時，SHALL NOT 再建立第二次（D51-R01）。自動讀回每次 SHALL 計入上限，到限就停止。
>
> **唯讀觀察** SHALL NOT 需要執行許可。每次取得之前 SHALL 先持久化一個單調遞增的順序識別，並依此順序匯入；請求脈絡與觀察到的事實 SHALL 分開保存。共用的版本事實 SHALL 由 feature 層級、跨所有目的的水位保護：只有比水位新的觀察才能更新，而且更新時 SHALL 使相關 gates 與 Pass 失效；晚到的舊觀察 SHALL NOT 恢復舊版本。各目的的快取 SHALL 分開保存，只在觀察到的版本等於目前版本時才可作為 gate 依據。
>
> **讀取失敗預算**：同一個邏輯讀取目標（目的＋對象）的連續傳輸失敗 SHALL 持久計數，SHALL NOT 因新的順序識別、session 或 restart 而重置。初次加兩次重試都失敗後 SHALL Blocked，並停止自動讀取，也 SHALL NOT 自動取得新的額度。之後只有明確的人工 decision 能授予一次新的有界額度，而且不重置其他計數。成功取得但內容為 pending，不算失敗。

基準版把首次唯讀觀察也納入 begin，本版撤回這一點。

## 2. DUR-02：workspace 與 writer 結束 [D50]、[A03]

> 第一片中，每個 feature SHALL 只有一個 Implementer worktree，tasks 與 fix 依序執行。Reviewer SHALL 使用獨立的 clone 與 session。平行 writer 需要另外定義規則，並經 D11 確認。

**AC-D04 THEN 補充**：「確認停止或 idle」SHALL 以可核對的權威證據判定，二選一：

- 該 attempt 的結果已匯入，**且** native 紀錄顯示該 turn 已完成；
- stop 已經過 process-info 確認。

terminal idle、runtime 的 idle／done 狀態，SHALL NOT 單獨作為 writer 已結束的證據。

## 3. GAT-03：replay、整合追溯、證據適用性 [D50]

> 歷史 Red SHALL 是實作前捕捉的原始紀錄，逐項核對 raw、exit、task／attempt、snapshot、provenance。
>
> Red SHALL 另外滿足三項適用資格，每項獨立判定，任一不成立即無效（D51-R07）：
> - snapshot 的變更與 attempt 的 commit 範圍 SHALL 位於核准的 task scope 內；
> - 原始 snapshot SHALL 有捕捉當時記錄的、對應到該 task／attempt 的適用紀錄：捕捉 provenance 帶有該 task／attempt，並且 snapshot 的測試內容或 delta 出現在 attempt 的 commit 中，或 snapshot 本身位於 attempt 的歷史上。只有共同祖先 SHALL NOT 足夠。尚未 commit 時捕捉的原始 Red，可以經由這份記錄的對應連到 attempt；
> - attempt SHALL 是目前 head 的祖先。
>
> raw 與 producer 正確，SHALL NOT 補足這些資格；replay 也 SHALL NOT 補足。本條不要求 Red 與 Green 在同一 SHA，也不要求強制 replay。
>
> 最終 Green 與 regression SHALL 由協調方以 policy 命令，在目前實際的 head H 上執行；controller SHALL NOT 執行 worker 提供的命令。以暫時合併的 snapshot 取得的結果，SHALL NOT 當作 H 的 Green（D51-R02）。
>
> replay SHALL 只在證據矛盾或有風險時作為診斷，SHALL NOT 補造 Red。

- **AC-G06**：刪除基準版加在 THEN 的 replay 句子，改為：
  > 正常路徑不需要 replay；只有矛盾或風險時才以 replay 作診斷，而且不能補造原始 Red。
- **AC-G08**：將「task commit→integration commit」讀作「attempt commit 範圍→整合 head」。
- **AC-G05 補充**：程式之後只改文件的新 head，SHALL 在新 head 重跑 Green，並記錄「只有文件差異」這個適用理由；tracked 文件 SHALL NOT 被要求引用自身的 commit SHA。
- **AC-G17 補充**：head 不變而 base 改變時，SHALL 在 H 重跑必要的 Green 與 regression，並綁定新的 base，同時重新 review。需要整合新 base 時，SHALL 產生新的真實 head，所有 gates 重新判定。

## 4. GAT-05：G2 判定 [D50]

> G2 SHALL 只在以下全部成立時通過：經授權的獨立 Reviewer、對目前版本的完整 PR diff、適用的 spec／design／AC 以及先前 findings 做了 review、verdict 為 `clean`、沒有未解的 blocking。
>
> `changes_required` SHALL 為 failed；`blocked` SHALL 為 unknown，且不開修正輪；缺 verdict、格式錯誤或只審部分 diff SHALL NOT 通過。
>
> 正式 review SHALL 在 PR identity 已記錄之後才派出 [A04]。

## 5. GAT-06：CI 政策來源、只認 head、例外 [A01]

取代基準版的 GAT-06 內文。原本的 check 身份、完整分頁、非成功狀態等核對，仍依下文保留。

> G3 SHALL 從 GitHub 查核必要 check 集合，空集合 SHALL NOT 算成功。政策來源依序為：
> 1. 可讀的 repo 規則；
> 2. 規則讀取回 403 或不可讀時，**只有** `yschiang/loop-engineering`，而且存在一份以人工 `policy_change` 核准、綁定該設定版本 digest 的宣告集合，才採用該集合；此時 G3 與 Pass package SHALL 標示 GitHub rules 未核對。
>
> 沒有適用政策（缺少、未核准、digest 不符、其他 repo）時，G3 SHALL 為 unknown 並 Blocked，SHALL NOT 開修正輪。403 本身 SHALL NOT 自動授權任何集合。
>
> 第一片 SHALL 只採用來源是 PR head 的 check：metadata 的 head SHA 與實際受測的 SHA 都 SHALL 等於 head。
>
> 例外機制 SHALL 只允許 skipped／neutral，而且每一項 SHALL 綁定一個核准的 decision；failure、cancelled、timed_out、unknown SHALL NOT 被例外放行。具體採用的政策可以不設任何例外；第一片的候選政策就是如此。

- **AC-G13 THEN**：規則不可讀、**且沒有適用的已核准政策**時，才是 unknown 並 Blocked。
- **AC-G15（覆寫基準版的映射承諾）[延後]**：第一片中，以非 head 的整合 snapshot 執行的必要 check SHALL 為 unknown（不支援的來源），SHALL NOT Pass。「可驗證的 head／base 映射後採用」這項正向能力延到 S2。
- **AC-G14 補充（D51-R03）**：第一片只支援 GitHub Actions 的 check-run。
  - 候選 SHALL 同時符合預期的 app、workflow 路徑與 check 名稱；
  - 最新 attempt SHALL 先依所選 workflow 內的 run number，再依 run attempt 判定；run ID 只作識別，不代表先後；不依開始時間；
  - 會讀完所有分頁；
  - 無法排序或有歧義時 SHALL 為 unknown，SHALL NOT 回退到舊的 success；
  - 只以 commit status 回報的必要 check SHALL 為 unknown。

## 6. DUR-05：AC-D10 對外語意 [A 補充]

> 已提交的狀態 SHALL 可恢復，而且不重複生效；中斷時尚未提交的變更 SHALL NOT 被接受；同一 transition 的內容衝突 SHALL Blocked。

具體的提交順序（history-first）是設計與測試的細節，不是 spec 承諾。

## 7. DUR-09：第一片的 runtime 範圍 [A03]

- **AC-D23**：第一片的已選 profile 是 Claude Code（Implementer）加 OpenCode（Reviewer）。未選用的選配接入（Orca、Codex CLI、其他 profile）即使缺失或故障，SHALL NOT 阻斷已選路徑，也 SHALL NOT 被自動改用；已選 profile 本身不可用時，SHALL Blocked。OpenCode-only 部署的變體 **[延後]**。
- **AC-D24 [延後]**：同一個 OpenCode 承載兩個角色的配置，延到後續切片驗收。第一片的 profile 組合不構成此 AC 的證據。
- **AC-D20 [延後]**：維持原文，由後續切片負責。

## 8. ORC-01／04／06／07：自動化時點 [D50]

> 第一片中，adopt、Project Lead 委派、Retro 候選產生、跨 feature 依賴解除，都由 workflow／skill 與人依既有契約執行；controller 只記錄相關的 decision 與證據。未支援的 controller 入口 SHALL 明確回 `unsupported`，SHALL NOT 讓任何路徑略過 D11、G1、D27 或 owner 的核對。

- O08、O09、O14、O18 **[延後]**。
- O12、O13 由 skill 與人核對，controller 不自動解除等待。
- **ORC-06 補充**：依賴 controller 本身的第一個 feature，SHALL 在 bootstrap PR 已經人工 accepted、實際 merge，並登記 baseline 之後才開始；SHALL NOT 自動 merge。
- **AC-O15（歷史限制）**：P03／Q-TARGET 的暫停只保留在 handoff 紀錄，產品 SHALL NOT 有 P03 特判。通用規則是：沒有明確的啟動或授權，SHALL NOT 接管任何工作。

## 9. DUR-08

讀回上限只適用於外部寫入；唯讀觀察依 §1 的讀取失敗預算。D47 的語意不變。

## 10. 沿用基準、不再重述的條文

- D45-S01／S05：文件缺陷可修正；G1 失敗可在正式 review 前修正（計一輪）。
- S02：信任邊界。
- S08：受測 SHA 的核對。
- S09：bootstrap gates 的區分。
- D47、D48 相關條文；finding、修正、發布的其他條文。
