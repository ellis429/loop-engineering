# Coverage 候選：88 AC 與 17 項 S1 findings（Stage 02A）

> revision-04 已提交 review-05 的 D45-S01、S02，以及 review-06 的 S03–S06 對應修正（AC-F05、D02、D13、D17、G08、G13 列），待覆核。
> 依據（authority）：原始四份 specs、[scope-reconciliation](/Users/johnson.chiang/workspace/loop-engineering/.delivery/bootstrap/herdr-design-d45-01/inputs/docs/harness/scope-reconciliation.md)，以及 D46–D49。本文是規劃對照，不是測試證據：所有驗證都是 **planned**，尚未執行，也沒有任何 gate 結論。

## 讀表方式

**處置**
- **retain**：義務與執行者都不變。
- **transfer**：改由 orchestrate 或工具執行，controller 仍負責核對。
- **replace**：舊的平台機制被取代，可觀察的保證不變。
- **revised(D4x)**：依已核准的政策修訂承諾與邊界，細節見 spec-delta。

沒有任何 AC 被刪除。

**驗證層級**
- **H1-F**：pytest＋fake Herdr／GitHub＋真 git tmp repo。
- **H2-R**：真實 Herdr＋OpenCode／Claude Code。
- **H2-GH**：真實 GitHub／CI。
- **H2-E2E**：本 repo 真實 issue→PR Pass。
- **H3**：cross-node-file-transfer 示範。
- **DOC**：文件／skill 審查清單。
- **UNCOV**：本 change 規劃的切片未涵蓋，另需環境；如實列為未覆蓋，不能勾完成。

## delivery-orchestration（28）

| ID | 處置 | 新 owner／契約 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-O01 | retain | orchestrate／人；controller 沒有 D11 就不發實作許可 | H1-F 直接交付→planning、0 許可；H2-E2E |
| AC-O02 | transfer | 持協調權的 orchestrate＋controller 許可（ORC-01） | H1-F 無協調權的命令被拒、未經許可的 review 不進 G2 |
| AC-O03 | retain | controller binding（locator＋digest） | H1-F 重讀相同 bytes 時 key 不變 |
| AC-O04 | retain | 角色 agent＋人；controller 停止派工 | H1-F 衝突→Blocked、0 許可 |
| AC-O05 | retain | controller | H1-F 沉默／timeout／agent 同意都不算批准 |
| AC-O06 | transfer | controller 許可、orchestrate 派出 | H1-F 經公開入口 approve_plan→第一個許可（S1-R07）；H2-E2E |
| AC-O07 | retain | controller＋Project Lead／人 | H1-F 經公開入口 scope_change 不 crash（S1-R10） |
| AC-O08 | retain | orchestrate＋controller | H1-F；H2 若不含 adopt 則列 UNCOV |
| AC-O09 | retain | controller；以完整核准 task 集合判定（spec-delta ORC-04） | H1-F 空集合／缺 Red 不能通過（S1-R11） |
| AC-O10 | retain | controller＋人 | H1-F 0 merge／close；H2-E2E |
| AC-O11 | retain | controller | H1-F V1 accepted 不移植到 V2 |
| AC-O12 | retain（Q-STACK 待決） | controller＋GitHub 查詢 | H1-F fake；H3 |
| AC-O13 | retain（Q-STACK 待決） | 同上 | H1-F fake；H3 |
| AC-O14 | transfer | orchestrate／Project Lead＋controller 去重 | H1-F 重送／restart 只產生 1 個 retro op；H3 |
| AC-O15 | retain | orchestrate | DOC＋H1-F 無 P03 操作 |
| AC-O16 | transfer | orchestrate 唯一外層 loop（ORC-08） | H1-F 結果需匯入才生效；H2 DOC skill 審查 |
| AC-O17 | retain | 角色 agent＋controller policy binding | DOC |
| AC-O18 | transfer | Project Lead／人＋orchestrate＋controller | H1-F 有授權→許可、無授權被拒 |
| AC-O19 | retain | orchestrate＋controller | H1-F 父子標記不增加權限 |
| AC-O20 | retain | Project Lead | DOC；H3 |
| AC-O21 | retain | Project Lead | DOC；H3 |
| AC-O22 | retain | Implementer＋人 | H1-F 草案 plan 不能批准派工；DOC |
| AC-O23 | retain | Implementer→Project Lead／人 | H1-F 受影響 task 停派、其他繼續 |
| AC-O24 | retain | Project Lead | DOC；H3 |
| AC-O25 | retain | Project Lead／人 | DOC |
| AC-O26 | retain | Project Lead＋controller | H1-F 有 SA 確認但無 D11→0 許可 |
| AC-O27 | retain | Project Lead／人 | DOC |
| AC-O28 | retain | Project Lead／Reviewer | DOC；H3 |

## delivery-gates（20）

| ID | 處置 | 新 owner／契約 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-G01 | retain | controller；G1 通過前不發 G2 許可（GAT-01） | H1-F；H2-E2E |
| AC-G02 | retain | controller | H1-F 兩種組合都不 Pass |
| AC-G03 | retain | controller | H1-F G2 unknown、Blocked、輪次不變 |
| AC-G04 | revised(D48) | controller 逐項核對＋Reviewer；producer 須是核准的捕捉工具 | H1-F 每種不一致都被拒 |
| AC-G05 | transfer | 證據工具捕捉＋controller | H1-F |
| AC-G06 | revised(D48) | 原始 Red＋整合 head 的 Green；replay 只是佐證 | H1-F 真 git；H2-E2E |
| AC-G07 | revised(D48) | replay／transcript 不能補足缺失的原始 Red | H1-F 缺 Red、語法錯誤、replay 冒充都無效 |
| AC-G08 | transfer | 協調方在整合 head 跑 Green＋controller；正式 review 前 G1 失敗走修正路徑（FIN-03，D45-S05） | H1-F 真 git 整合後回歸失敗 → 授權修正 → Green → 才有第一次正式 G2，預算不重置 |
| AC-G09 | retain | 獨立 Reviewer（共用獨立性核對）＋controller | H1-F；H2-R |
| AC-G10 | retain | controller | H1-F 自我宣告或獨立性不符都被拒（S1-R15） |
| AC-G11 | transfer | orchestrate＋runtime＋controller；model 從原生紀錄讀回 | H1-F；H2-R reviewer profile 真實負例 |
| AC-G12 | transfer | runtime 既有權限能力（不自建 sandbox）＋controller | H1-F；H2-R，未驗證即 G2 unknown |
| AC-G13 | revised(D49) | GitHub 工具＋controller；repo 規則或本 repo 人工核准的版控政策 | H1-F 403 且無政策→unknown、不開修正批次；同一版本 CI pending→pending→success 時每個週期都重新觀察（D45-S04）；H2-GH（check 集合待 D11） |
| AC-G14 | retain | GitHub 工具＋controller | H1-F；H2-GH |
| AC-G15 | retain | GitHub／git＋controller；check 只有在 `head_sha` 與受測 SHA 產物都等於 H 時才計入 head 來源（D45-S08） | H1-F（H≠M 的 PR 案例）；H2-GH |
| AC-G16 | retain | controller；區分晚到結果與新觀察（spec-delta GAT-07） | H1-F |
| AC-G17 | retain | controller＋Reviewer | H1-F |
| AC-G18 | transfer | 工具重新觀察＋controller；Pass 需晚於判定的新觀察 | H1-F；H2-GH |
| AC-G19 | retain | 驗收報告按接法分列 | DOC（每個階段） |
| AC-G20 | retain | Reviewer＋驗收報告 | H2-E2E；沒有成立的 finding 就列 UNCOV |

## durable-delivery（24）

| ID | 處置 | 新 owner／契約 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-D01 | retain | controller；一份 feature 狀態、一套入口（DUR-01） | H1-F＋DOC |
| AC-D02 | revised(D48) | controller 歷史與手改偵測，只承諾偵測可核對的不一致（DUR-02，D45-S02）；不承諾偵測或阻止同帳號協同偽造 | H1-F 手改被偵測且不當決策（不測試也不宣稱能偵測協同偽造） |
| AC-D03 | transfer | 協調權＋feature 單一 authority | H1-F 兩個程序同時 claim，恰一方成功 |
| AC-D04 | retain | orchestrate＋runtime＋controller | H1-F；H2-R 真實 stop 讀回 |
| AC-D05 | retain | controller | H1-F |
| AC-D06 | transfer | runtime 讀回工具＋controller | H1-F fake；H2-R |
| AC-D07 | transfer | orchestrate 讀回＋controller | H1-F 只匯入一次、0 重派 |
| AC-D08 | retain | controller | H1-F |
| AC-D09 | retain | controller | H1-F crash fixture |
| AC-D10 | replace | revision 歷史先寫（取代事件重放） | H1-F 中斷時的 revision 不生效、transition 衝突→Blocked |
| AC-D11 | retain | controller | H1-F |
| AC-D12 | transfer | orchestrate＋GitHub 工具 marker 讀回 | H1-F；H2-GH |
| AC-D13 | retain | controller＋orchestrate；讀回不消耗許可、查無不等於可重試（DUR-06，D45-S03） | H1-F A 已 begin 後暫停、B 讀回查無、再讓 A 繼續：B 永遠拿不到重試許可，外部呼叫恰好 1 次 |
| AC-D14 | transfer（承諾收斂） | orchestrate resume＋controller；無法確認→交人 | H1-F |
| AC-D15 | retain | controller＋外部觀察 | H1-F |
| AC-D16 | retain | controller＋單次工具呼叫 | H1-F 初次＋2 次後 Blocked |
| AC-D17 | revised(D47) | 在線時有界停止／讀回；離線恢復時計入並 Blocked | H1-F fake clock（在線／離線／prepare 後 crash；讀回 3 次錯誤或仍在執行→停止自動讀回並 Blocked，D45-S06）；H2-R 真實停止 |
| AC-D18 | transfer | Herdr／runtime 工具＋controller | H1-F；H2-R |
| AC-D19 | retain | preflight＋controller | H1-F；H2-R |
| AC-D20 | retain | OpenCode-only 工具接法 | H1-F 核心不依賴 Herdr；公司環境 UNCOV |
| AC-D21 | retain | transport 轉接＋controller | H1-F |
| AC-D22 | retain | 各接法分開驗收 | DOC；Herdr 走 H2，其他接法 UNCOV |
| AC-D23 | retain | profile preflight | H1-F；H2-R |
| AC-D24 | retain | runtime＋controller | H2-R |

## finding-resolution（16）

| ID | 處置 | 新 owner／契約 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-F01 | retain | Reviewer＋controller | H1-F |
| AC-F02 | retain | Reviewer 指認相同 finding＋controller | H1-F |
| AC-F03 | retain | controller | H1-F |
| AC-F04 | retain | 獨立 Reviewer／人＋controller | H1-F |
| AC-F05 | transfer | orchestrate＋controller；核准範圍內的文件缺陷與必要驗證缺失可以修正，policy unknown 與 infra 不是修正項（FIN-03，D45-S01） | H1-F；**規劃情境**：只改文件的 feature 經 N/A 後，Reviewer 指出交付說明的必要命令錯誤或缺必要驗證 → 進 batch → fix → 獨立 re-review → 解除（validation V-H1-S；未執行） |
| AC-F06 | retain | controller | H1-F |
| AC-F07 | retain | controller；feature 層輪次，換 epoch 不重置 | H1-F |
| AC-F08 | transfer | orchestrate＋獨立 Reviewer | H1-F |
| AC-F09 | retain | controller | H1-F |
| AC-F10 | retain | controller＋orchestrate | H1-F |
| AC-F11 | retain | 人＋controller | H1-F |
| AC-F12 | retain | Project Lead／人 | H1-F＋DOC |
| AC-F13 | transfer | orchestrate＋GitHub 工具；Pass 前必須完成發布 | H1-F；H2-GH |
| AC-F14 | retain | controller＋orchestrate | H1-F；H2-GH |
| AC-F15 | retain | Reviewer＋controller | H1-F |
| AC-F16 | retain | Reviewer＋controller | H1-F |

合計：28＋20＋24＋16＝88。

## S1 findings（17，全部仍 open）

每項都要等新程式與新證據完成，並經獨立 Reviewer 覆核後，才能關閉；移除舊機制不算關閉。

| ID | 處置 | 新 owner／契約 | 規劃驗證 |
| --- | --- | --- | --- |
| S1-R01 | replace | controller 不執行任何命令；證據工具只跑核准 policy 命令（GAT-03） | H1-F 惡意 argv 不被執行；H2-R 權限 probe |
| S1-R02 | replace | 每個 operation 的一次嘗試＝一次外部呼叫＋begin 計次（DUR-06） | H1-F create／查詢連續失敗時不遞迴，且不超過上限 |
| S1-R03 | replace | revision 歷史；同一 transition identity 內容不同→Blocked | H1-F |
| S1-R04 | replace | 歷史先寫，再更新現行狀態 | H1-F 在邊界中斷時仍可識別 |
| S1-R05 | transfer | worktree 操作先登記再讀回；比對不符或查無都交人，Herdr socket 請求不因 client 已結束就重試（D45-S03） | H1-F 真 git；H2-R Herdr worktree |
| S1-R06 | retain | 文件 digest 與 blob 引用分型 | H1-F 經公開 CLI 使用真 sha256 |
| S1-R07 | retain | plan provenance；approve_plan→第一個許可 | H1-F 從未批准開始經公開入口 |
| S1-R08 | retain | feature 層單一預算／協調權；換 epoch 不重置 | H1-F 4h／三輪用盡後新 session 仍被拒 |
| S1-R09 | revised(D47) | 在線時有界停止；離線恢復時計入、記錄超時並 Blocked | H1-F fake clock；H2-R 真實停止讀回 |
| S1-R10 | retain | scope_change 決策路徑與初始 schema 一致 | H1-F 經公開入口 |
| S1-R11 | retain | adopt 以完整核准 task／AC 集合判定 G1 | H1-F；H2 不含 adopt 則此項保持 open |
| S1-R12 | retain | assignment 附完整 finding 快照（FIN-03） | H1-F；H2-E2E 真實 fix／re-review |
| S1-R13 | retain | 原始 Red 逐項驗證（GAT-03） | H1-F 每一種污染各自被拒 |
| S1-R14 | retain | G3 policy unknown→Blocked、不耗輪次（GAT-06、FIN-03） | H1-F；H2-GH 403 情境 |
| S1-R15 | retain | N/A 與 G2 共用獨立性核對（GAT-04） | H1-F；H2-R |
| S1-R16 | retain | 已 resolved 的 finding 被指認再現→reopen 並阻擋 | H1-F |
| S1-R17 | revised(D49) | 例外只限 skipped／neutral，且需核准的 decision | H1-F；H2-GH |
