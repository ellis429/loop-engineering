# Spec delta：現行覆寫（候選 design-04；revision-16）

> **作者提交狀態**：revision-16（回應 revision-15 覆核的 R15-09、R15-10）；候選，未 D11，未套用正式 specs。目前的 review 狀態以 [README](README.md) 為準。
> **revision-15 [R15]**：只把每個覆寫的**取代範圍**寫明確，並為字面組合會自相矛盾的 scenario 提供全文（AC-D10、AC-D23、AC-G13、AC-G15、AC-O15、AC-O23、GAT-06）。語意沿用 revision-14；唯一收窄是移除 D45-02 DUR-06 的「本機同步程序」重試例外（§1），D45-02 的其他重試條件與人工再核對都保留（revision-16 補回），理由見該節。組合規則見 §12。
> **基準**：[D45-02 spec delta](../d45-02/spec-delta.md)（D45-02 版）。它本身也尚未採入正式 specs。本文列出**目前所有**對該基準的覆寫，已包含 outputs-03、AC audit 與 revision-12 的修正。沒列在這裡的條文，沿用基準。
> **採用方式**：本文不能單獨套用。D11 後，tasks T0.1 第 1 步以正式 specs＋D45-02 基準的全部條目＋本文覆寫，組成四份自足、完整的正式 spec，並附逐項來源對照。
> 88 個 AC ID 全部保留：沒有新增 AC，也沒有刪除義務。revision-12 的條文標 `[R12]`，是待審提案，不是已核准政策。

**標記說明**
- **[D50]**：機制簡化或自動化時點延後。
- **[A0x]**：AC audit 的修正。
- **[R12]**：回應 2026-09-28 Opus review 的修正。
- **[R13]**：回應 review-01（M5 殘留、R12-01、R12-02）的修正。
- **[延後]**：後續切片的能力，第一片不算完成。

## 1. DUR-06：外部寫入、唯讀觀察、讀取失敗預算 [D50]、[A05]、[R12]

**取代範圍 [R15]**：D45-02 在 DUR-06 requirement 內文末尾追加的整段（自「登記同一外部操作可以重送且無副作用」起，至「（D45-S04）。」止），由本節以下五段整段取代；正式 DUR-06 原文與 D45-02 對 AC-D12 WHEN 的替換保留。D45-02 三種可重試情況中的「本機程序內直接、同步完成、原程序已不存在且查無效果」**不再保留**：第一片的外部寫入（design §4 的 op 種類）都經 Herdr server 或 GitHub 處理，沒有這類操作；收窄後只會更早停下交人，不減少任何義務。另外兩種（權威證據證明未送達或已完成且排除之後才生效；已驗證的原生冪等）與「到限後只能經人工 decision 再核對」都保留在下文 [R16]。`evidence green` 的臨時 checkout 是 loopctl 自己的本機證據工具，不是外部寫入 op，受 design §7 的執行界線管理。

> **外部寫入**限於有限種類：worktree 建立、派工、prompt、stop、push、PR ensure、PR 與 issue 發布。每種 SHALL 先登記，再只被一個呼叫者執行一次，並保存 receipt。結果不明時，SHALL 只讀回原操作，SHALL NOT 重發。以下情況 SHALL NOT 作為重試證明：查不到效果、client 已結束、經常駐 server 或遠端處理的請求。只有在以下情況才可重試：已有權威證據證明原請求未送達，或已完成且排除之後才生效；或外部操作有已驗證的原生冪等。否則 unknown 並 Blocked。以查詢判斷 PR 是否存在 SHALL NOT 視為冪等：建立 PR 的結果不明、之後又查不到時，SHALL NOT 再建立第二次（D51-R01）。自動讀回每次 SHALL 計入上限（包括原操作仍在執行、結果未定的那次）；到限仍無法確認時 SHALL Blocked 並停止自動讀回，直到人工 decision 授權一次新的讀取核對；worker 維持 active／unknown，SHALL NOT 重送（D45-S06）。
>
> **PR ensure 的身份** [R12]：外部呼叫之前，SHALL 先持久化預期身份（repo、head repo 與 branch、目前 head SHA、base repo 與 branch）與唯一的 operation marker。沿用既有 PR SHALL 要求上述身份全部相符，並記錄為既有 PR，SHALL NOT 記成本次建立；任一欄不符（包括同 branch、不同 base）SHALL Blocked，SHALL NOT 另建。結果不明後的讀回 SHALL 同時要求 marker 與完整身份相符，才算本次建立成功。
>
> **人工處理 unknown** [R12]：人工 decision SHALL 只記錄，SHALL NOT 執行外部寫入。綁定觀察到的結果時，SHALL 先以新的讀取核對它符合預期身份；標記未送達時，SHALL 附上未送達的證據，查不到效果本身 SHALL NOT 算證據。之後的重試仍受原有的重試上限。
>
> **Branch 歷史** [R12]：受控 run 期間，feature branch SHALL 只以一般 fast-forward push 更新；SHALL NOT rebase、squash 或 force-push。這不是 repo 全域規則。整合 base 所用的 merge commit 是 feature branch 上的本機 git 操作，SHALL NOT 被視為或需要 GitHub PR merge 權限；外部寫入種類 SHALL NOT 因此增加 merge（AC-O10 不變）。
>
> **唯讀觀察** SHALL NOT 需要執行許可。每次取得之前 SHALL 先持久化一個單調遞增的順序識別，並依此順序匯入；請求脈絡與觀察到的事實 SHALL 分開保存。共用的版本事實 SHALL 由 feature 層級、跨所有目的的水位保護：只有比水位新的觀察才能更新，而且更新時 SHALL 使相關 gates 與 Pass 失效；晚到的舊觀察 SHALL NOT 恢復舊版本。各目的的快取 SHALL 分開保存，只在觀察到的版本等於目前版本時才可作為 gate 依據。
>
> **讀取失敗預算**：同一個邏輯讀取目標（目的＋對象）的連續傳輸失敗 SHALL 持久計數，SHALL NOT 因新的順序識別、session 或 restart 而重置。初次加兩次重試都失敗後 SHALL Blocked，並停止自動讀取，也 SHALL NOT 自動取得新的額度。之後只有明確的人工 decision 能授予一次新的有界額度，而且不重置其他計數。成功取得但內容為 pending，不算失敗。

基準版把首次唯讀觀察也納入單次執行許可，本版撤回這一點（D50 OE：唯讀 observation 不使用外部寫入的單次執行協定）。

## 2. DUR-02：workspace 與 writer 結束 [D50]、[A03]

**取代範圍 [R15]**：下段追加在 D45-02 取代後的 DUR-02 requirement 內文之後；AC-D03 沿用 D45-02 的替換；AC-D04 THEN 依序保留正式原文、D45-02 的追加句，再追加下方補充。

> 第一片中，每個 feature SHALL 只有一個 Implementer worktree，tasks 與 fix 依序執行。Reviewer SHALL 使用獨立的 clone 與 session。平行 writer **[延後 S2]** 需要另外定義規則，並經 D11 確認；第一片不提供。

**AC-D04 THEN 補充**：「確認停止或 idle」SHALL 以可核對的權威證據判定，二選一：

- 該 attempt 的結果已匯入，**且** native 紀錄顯示該 turn 已完成；
- stop 已經過 process-info 確認。

terminal idle、runtime 的 idle／done 狀態，SHALL NOT 單獨作為 writer 已結束的證據。

## 3. GAT-03：replay、整合追溯、證據適用性 [D50]、[R12]

**取代範圍 [R15]**：D45-02 在 GAT-03 requirement 內文末尾追加的整段（自「歷史 Red SHALL 是實作前捕捉的原始紀錄」起，至「在整合 head 的獨立 checkout 執行。」止），由下方引文整段取代；正式 GAT-03 原文保留。AC-G06、AC-G07、AC-G08、AC-G05、AC-G17 依下方各條。

> 歷史 Red SHALL 是實作前捕捉的原始紀錄，逐項核對 raw、exit、task／attempt、snapshot、provenance。
>
> **需要 Red 的單位** [R12]：核准 plan 的每個 task，以及每個改變行為的修正 attempt（含正式 review 前的 G1 修正、review／CI 修正、整合 base 時作者自己寫的解法、人工退回）。修正的 Red SHALL 另外綁定所處理的 finding ID 與 batch ID；batch 內每個改變行為的 finding SHALL 至少有一個列出它的 Red。是否改變行為依實際 diff 判定。
>
> Red SHALL 另外滿足三項適用資格，每項獨立判定，任一不成立即無效（D51-R07）：
> - snapshot 的變更與 attempt 的 commit 範圍 SHALL 位於核准的 task（或 batch 的 finding）scope 內；整合 attempt 只以作者編輯計算 scope，可重現地驗證為原樣匯入的 base 內容不算作者編輯 [R13]；
> - 原始 snapshot SHALL 有捕捉當時記錄的、對應到該 task／attempt 的適用紀錄：捕捉 provenance 帶有該 task／attempt，並且 snapshot 的測試內容或 delta 出現在 attempt 的 commit 中，或 snapshot 本身位於 attempt 的歷史上。只有共同祖先 SHALL NOT 足夠。尚未 commit 時捕捉的原始 Red，可以經由這份記錄的對應連到 attempt；
> - attempt SHALL 是目前 head 的祖先。
>
> **被放棄的 attempt** [R12]：不在目前 head lineage 的 attempt，其 Red SHALL NOT 轉移給其他 attempt。某個單位沒有合格的原始 Red 時，G1 SHALL 不通過，feature SHALL Blocked 並附原因；SHALL NOT 以 replay 或回退程式重新捕捉的方式製造 Red。
>
> **歷史被改寫** [R12]：目前 head 不是先前記錄 head 的後代時，依 lineage 判定的 Red 資格 SHALL 失效並 Blocked，SHALL NOT 補造證據。
>
> raw 與 producer 正確，SHALL NOT 補足這些資格；replay 也 SHALL NOT 補足。本條不要求 Red 與 Green 在同一 SHA，也不要求強制 replay。
>
> Red、Green 與 regression SHALL 只以核准政策定義的命令產生；最終 Green 與 regression SHALL 由協調方在目前實際的 head H 的獨立乾淨 checkout 執行，SHALL NOT 在 Implementer worktree 執行；controller SHALL NOT 執行 worker 或 result 提供的命令。以暫時合併的 snapshot 取得的結果，SHALL NOT 當作 H 的 Green（D51-R02）[R15：保留 D45-02 的「獨立 checkout」與「只以核准命令」]。
>
> replay SHALL 只在證據矛盾或有風險時作為診斷，SHALL NOT 補造 Red。

- **AC-G06**：刪除 D45-02 加在 THEN 末尾的 replay 句子，改為追加：
  > 正常路徑不需要 replay；只有矛盾或風險時才以 replay 作診斷，而且不能補造原始 Red。
- **AC-G07**：沿用 D45-02 的 THEN 替換。
- **AC-G08**：THEN 中的「task commit 到 integration commit」改為「attempt commit 範圍到整合 head」，其餘原文保留。
- **AC-G05 補充**（追加在正式 THEN 之後）：程式之後只改文件的新 head，SHALL 在新 head 重跑 Green，並記錄「只有文件差異」這個適用理由；tracked 文件 SHALL NOT 被要求引用自身的 commit SHA。
- **AC-G17 補充**（追加在正式 THEN 之後）[R12 修訂]：head 不變而 base 改變、且沒有整合觸發時，SHALL 在 H 重跑必要的 Green 與 regression，並綁定新的 base，同時重新 review；這不代表已驗證與新 base 的整合。G3 沿用 H 的 head-only 結果時，SHALL 保存適用理由。整合觸發只有：GitHub 回報不可合併、Reviewer finding 判定不相容、人工 decision；可合併性尚未算出時 SHALL 等待，逾時 SHALL Blocked。整合以保留歷史的本機 merge commit 產生新的真實 head，所有 gates 重新判定 [R13 修訂如下]：
  - **路徑 [R14]**：先套用 owner／writer 安全、D47 預算／stop 與修正輪數限制，SHALL NOT 因整合而繞過。觸發成立且適用 G1 未通過，或任一必要 G2／G3 已過時、無法啟動、已確定不可用或逾時時，SHALL 優先走既有正式 review 前的 G1 修正機制（原因 base 整合）；即使另一 gate 仍在途，也 SHALL NOT 等待無法取得的結果。只有適用 G1 通過，且 G2、G3 各自都有同版本終態結果或確實在途且可取得的執行，才 SHALL 照常收齊，併為同一 correction batch；均為終態時直接合併。終態的 policy unknown／review blocked 等獨立 blockers SHALL 保留。各 gate 保存真實原因，缺少 CI SHALL NOT 算成功。
  - **共同規則**：兩者都 SHALL 只有一個 writer、一個 batch，實際派修時計一輪；派修前 SHALL 確認先前的 writer 已停止（unknown 依 DUR-08）；過時的結果只存歷史，已收到的 findings SHALL 保留。
  - **去重**：整合需求 SHALL 以（base、釘住的 base tip、目前 head）決定的穩定 finding identity 記錄並去重，作為整合 Red 的綁定對象。
  - **整合 assignment**：SHALL 釘住先前的 feature head 與確切的 base tip，分別授權原樣匯入該 base 的變更，以及作者編輯（限衝突路徑與 batch finding 的 scope）。merge commit SHALL 以這兩者為 parents。
  - **Red 與 scope**：原樣匯入 SHALL 以可重現的 git 自動合併結果核對。純匯入 SHALL NOT 要求補造上游 Red，也不宣稱 N/A；作者編輯改變行為時 SHALL 有綁定整合 finding 與 batch 的原始 Red；超出 scope 的作者編輯 SHALL 被拒收，需要時回 D11。

## 4. GAT-04：N/A 資格 [R12 說明]

沿用基準與 D26：eligibility 依 diff 的實際行為判定，由獨立 Reviewer 確認；設定、migration、測試檔不因檔案類型一律排除（例如只改註解可以申請），改變行為即不合格。本版沒有收窄 D26。

## 5. GAT-05：G2 判定 [D50]、[R12]

**取代範圍 [R15]**：下方引文追加在 D45-02 取代後的 GAT-05 requirement 內文之後；AC-G11、AC-G12 沿用 D45-02 的讀法。

> G2 SHALL 只在以下全部成立時通過：經授權的獨立 Reviewer、對目前版本的完整 PR diff、適用的 spec／design／AC 以及先前 findings 做了 review、verdict 為 `clean`、沒有未解的 blocking。
>
> `changes_required` SHALL 為 failed；`blocked` SHALL 使 G2 為 unknown，**且 feature SHALL Blocked**，不開修正輪 [R12]；缺 verdict、格式錯誤或只審部分 diff SHALL NOT 通過。
>
> 正式 review SHALL 在 PR identity 已記錄之後才派出 [A04]。

## 6. GAT-06：CI 政策來源、只認 head、例外 [A01]、[R12]

**取代範圍 [R15]**：下方引文是 GAT-06 requirement 內文的**全文**，取代正式原文與 D45-02 的替換文字；兩者中仍有效的義務（check 身份各欄、完整分頁、非成功狀態、例外限制）都已寫入引文，不需另讀。

> G3 SHALL 從 GitHub 查核必要 check 集合，空集合 SHALL NOT 算成功。政策來源依序為：
> 1. 可讀的 repo 規則；
> 2. 規則讀取回 403 或不可讀時，**只有** `yschiang/loop-engineering`，而且存在一份以人工 `policy_change` 核准、綁定政策檔（repo 根目錄 `workflow.yaml`，不是 GitHub workflow）digest 的宣告集合，才採用該集合；此時 G3 與 Pass package SHALL 標示 GitHub rules 未核對。
>
> 沒有適用政策（缺少、未核准、digest 不符、其他 repo）時，G3 SHALL 為 unknown 並 Blocked，SHALL NOT 開修正批次或增加修正輪次。403 本身 SHALL NOT 自動授權任何集合，此政策來源 SHALL NOT 泛用到其他 repo。必要 check 的名稱、app 與 workflow SHALL 在政策檔列明並經核准；範例名稱不構成核准。
>
> 每項必要 check SHALL 核對 name/context、app/provider、workflow 來源、source SHA、head/base 關係、run 與 attempt 的身份及順序、status/conclusion 與可讀 URL，涵蓋完整分頁。Missing、pending、cancelled、timed-out、failed、unknown、stale SHALL NOT 視為成功。
>
> 第一片 SHALL 只採用來源是 PR head 的 check：metadata 的 head SHA 與該 job 實際受測的 SHA 都 SHALL 等於 head。每個 job 的受測 SHA SHALL 以唯一對應該 run、attempt、job 與 check 的紀錄證明；缺少或不符 SHALL NOT 通過 [R12]。
>
> 本機 G1 與每個必要 CI job SHALL 套用同一套收集／skip／失敗政策：收集數為 0、任何不是由 `only_on` 在非所屬平台產生的 skip、xfail／xpass 都 SHALL 使測試 session 失敗；skip reason 的文字 SHALL NOT 作為平台條件的證據 [R12；R13 修正措辭]。
>
> 例外機制 SHALL 只允許 skipped／neutral，而且每一項 SHALL 綁定一個核准的 decision；failure、cancelled、timed_out、unknown SHALL NOT 被例外放行。具體採用的政策可以不設任何例外；第一片的候選政策就是如此。（來源：D01、D29、D49、D51）

- **AC-G13 THEN（全文）[R15]**：
  > G3 不通過並逐項顯示原因。規則不可讀、**且沒有適用的已核准政策**時，G3 為 unknown 並 Blocked，不消耗修正輪。沒有明確核准例外的 skipped／neutral 也不通過；failure、cancelled、timed-out、unknown 永遠不因例外設定通過。
- **AC-G15（整個 scenario 全文）[R15；正向映射延後]**：
  > - **WHEN** CI 使用不同於 PR head 的 integration snapshot
  > - **THEN** 第一片：該必要 check SHALL 為 unknown（不支援的來源）並顯示原因，SHALL NOT Pass。**[延後 S2]**：只有可驗證的 head/base 映射與適用接受規則成立才採用；不能只比名稱或因 SHA 字串不同一概接受或拒絕，無法確認時為 unknown。
- **AC-G14 補充（追加在正式 THEN 之後；D51-R03；[R12] 修訂）**：第一片只支援 GitHub Actions 的 check-run，且候選 workflow 只由 PR 事件觸發。
  - 候選 SHALL 同時符合預期的 app、workflow 路徑、check 名稱，以及 run 的事件類型、head SHA 與已記錄的 PR；
  - 同一 workflow、同一 head，但事件或 PR 不符的 run SHALL 為 unknown，SHALL NOT 被忽略；
  - 每個 run 內 SHALL 以最新的 run attempt 為準；同一 head 有多個 run 時，每個 run 的最新 attempt 都 SHALL 計入，全部成功才算成功；run ID 只作識別；不依開始時間；
  - 會讀完所有分頁；
  - 無法識別、無法排序或有歧義時 SHALL 為 unknown，SHALL NOT 回退到舊的 success；
  - 只以 commit status 回報的必要 check SHALL 為 unknown。

## 7. DUR-05：AC-D10 對外語意 [A 補充]

**取代範圍 [R15]**：AC-D10 整個 scenario 以下文取代（取代正式原文與 D45-02 的替換）；DUR-05 requirement 內文、AC-D09、AC-D11 維持正式原文。

> - **WHEN** 現行 state 更新時被中斷，或同一 transition 被重複提交
> - **THEN** 已提交的 revision SHALL 可恢復，而且不重複生效；中斷時尚未提交的變更 SHALL NOT 被接受，只可保留作診斷；同一 transition identity 內容不同時 SHALL Blocked。系統 SHALL NOT 以事件重放作為第二份現行狀態來源。

具體的提交順序（history-first）是設計與測試的細節，不是 spec 承諾。

## 8. DUR-09：第一片的 runtime 範圍 [A03]

- **AC-D23（整個 scenario 全文）[R15]**：
  > - **WHEN** run 選用已核准且可用的 profiles（第一片：Herdr＋Claude Code 的 Implementer、Herdr＋OpenCode 的 Reviewer），而未選用的接入（Orca、Codex CLI 或其他 profile）不存在、未登入或連線失敗
  > - **THEN** controller SHALL NOT 以未選用接入的失敗阻斷已選路徑，仍按原 profile 核對版本、gates 與預算，SHALL NOT 自動改派其他 runtime／model。已選 profile 本身不可用或未驗證時 SHALL Blocked。只用 OpenCode 的部署下同一情境 **[延後 S2，隨 AC-D20]**。
- **AC-D24 [延後]**：同一個 OpenCode 承載兩個角色的配置，延到後續切片驗收。第一片的 profile 組合不構成此 AC 的證據。
- **AC-D20 [延後]**：維持原文，由後續切片負責。

## 9. ORC-01／04／05／06／07：自動化時點與 Pass package [D50]、[R12]

**取代範圍 [R15]**：下方引文追加在 D45-02 取代後的 ORC-01 requirement 內文之後。ORC-05、ORC-06 的「補充」追加在各自 requirement 內文之後；AC-O23、AC-O15 依下方全文。

> 第一片中，adopt、Project Lead 委派、Retro 候選產生、跨 feature 依賴解除，都由 workflow／skill 與人依既有契約執行；controller 只記錄相關的 decision 與證據。未支援的 controller 入口 SHALL 明確回 `unsupported`，SHALL NOT 讓任何路徑略過 D11、G1、D27 或 owner 的核對。

- O08、O09、O14、O18 **[延後]**。
- **AC-O23 THEN（全文）[部分延後，R12；R15 寫成全文]**：WHEN 維持正式原文。
  > - **THEN** 保存具體影響與待決事項，交 Project Lead 分析並回使用者裁決；未取得適用決策前 SHALL NOT 依該變更派工。第一片：整個 run SHALL 停下等待批准，不派任何新 attempt（d4、W-C）。**[延後 S2]**：核准範圍內未受影響的工作依現有計畫繼續；第一片不算完成。
- O12、O13 由 skill 與人核對，controller 不自動解除等待。
- **ORC-05 補充 [R12]**：Pass package SHALL 由 feature 狀態投影，不是另一份權威，也 SHALL NOT 單獨放行。它 SHALL 人可讀，並列出版本、PR identity、三 gates 的理由與結果引用、findings、限制、G3 政策來源與 GitHub rules 是否核對、發布狀態，以及 acceptance 為 pending。
- **ORC-06 補充**：依賴 controller 本身的第一個 feature，SHALL 在 bootstrap PR 已經人工 accepted、實際 merge，並登記 baseline 之後才開始；SHALL NOT 自動 merge。
- **AC-O15（整個 scenario 全文，歷史限制）[R15]**：
  > - **WHEN** 使用者只查看流程或規格，尚未以明確的 `init` 或授權啟動某項工作（例如暫停中的試用或 Retro）
  > - **THEN** 系統 SHALL NOT 接管該工作，也 SHALL NOT 啟動 Retro 或 PR gating；待確認的 feature／session、交接版本與原 owner 只記錄在 handoff。產品 SHALL NOT 含針對特定歷史試用（例如 P03、Q-TARGET）的特判。

## 10. DUR-08

讀回上限只適用於外部寫入；唯讀觀察依 §1 的讀取失敗預算。D47 的語意不變；D45-02 對 DUR-08 與 AC-D17 的修訂全部沿用。

**D11 後的第二段 [R15]**：若 D11 核准 design §10 的 active 區間定義與 timeout 值，T0.1 把 D45-02 DUR-08 第二段（「Active time 算法…確認前不視為已核准。」）替換為：
> Active time 以 design 定義的活動區間聯集計算；未知區間的計入方式、worker／review／CI 的 timeout 與到限路徑，以 D11 核准的 design 與政策檔 `workflow.yaml` 的 `timeouts` 為準；變更 SHALL 經人工 `policy_change`。

D11 未核准這些值時，第二段維持 D45-02 原文。

## 11. 沿用基準、不再重述的條文

- D45-S01／S05：文件缺陷可修正；G1 失敗可在正式 review 前修正（計一輪）。
- S02：信任邊界。
- S08：受測 SHA 的核對（逐 job 的產物見 §6）。
- S09：bootstrap gates 的區分。
- D47、D48 相關條文；finding、修正、發布的其他條文。

## 12. 組合規則（T0.1 用）[R15]

每個 requirement 與 scenario 依序套用三層，結果不需要再讀任何未採用的 delta：

1. **正式 spec 原文**；
2. **D45-02**：依其標示（[不變]、[移交]、[取代平台承諾]、[政策修訂]、[新增約束]）替換或追加；
3. **本文**：依各節的「取代範圍」或「全文」標示替換或追加；本文沒有提到的單位，停在第 2 步的結果。

- 本文標「全文」的單位（GAT-06 內文、AC-G13 THEN、AC-G15、AC-D10、AC-D23、AC-O15、AC-O23 THEN），直接以本文的文字為準，不再與前兩層逐句合併。
- 四份 spec 的開頭 banner 依 D45-02 §0.1 替換後，再改為記錄 D11 採用的來源與 sha256（tasks T0.1）。
- **Purpose 的 D40 字句 [R16]**：finding-resolution 的 Purpose 首句「本文是本 change 的D40 已核准的規格」替換為「本文是 D45–D49 修訂、經 D11 採用的規格」（D45-02 只替換了該段後面的 S1／S2／S3 字句）。四份 spec 的 Purpose 若仍引用 `docs/validation/implement-delivery-loop.md` 作為驗證對照，改為指向 T0.1 第 4 步採用後的 validation。組合後任何 Purpose 或 banner 都不得宣稱 D40 核准適用現行版本；`approval.json` 維持歷史。
- 組合結果若出現本文未預期的語意重疊或衝突，T0.1 停下回使用者，不自行選擇。
