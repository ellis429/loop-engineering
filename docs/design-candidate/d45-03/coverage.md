# Coverage（D50 候選 design-03）

> **全部是 planned，沒有任何項目已執行。**
> - 88 個 AC 與 17 項 S1 findings 各一列，依 `expected-coverage-02.json`；
> - 17 項 findings 全部仍 open；
> - 延後項目不標為 covered。

**讀表方式**
- **Owner**：C＝controller、S＝orchestrate skill／workflow、H＝人或角色 agent。
- **切片**：
  - S1＝第一片；
  - S2／S3＝後續切片；
  - DOC＝文件審查。
- **驗證**：V／R／B 編號對應 validation.md；T 編號對應 tasks.md 的 task。
- 「S1 unsupported」表示第一片對該入口明確回 `unsupported`，不繞過任何核對，但**不算覆蓋**。

## delivery-orchestration

| ID | Owner | 切片 | 規劃驗證／處置 |
| --- | --- | --- | --- |
| AC-O01 | C＋H | S1 | V3 沒有 D11 就 0 次派工；R3 |
| AC-O02 | C＋S | S1 | V2 單一 owner；V6 未經許可的 review 不進 G2 |
| AC-O03 | C | S1 | T2.2 binding digest |
| AC-O04 | H＋C | S1 | T2.2 來源衝突 → Blocked（fake） |
| AC-O05 | C | S1 | V3 |
| AC-O06 | C＋S | S1 | T2.2、R2 |
| AC-O07 | C＋H | S1 | V3 scope_change |
| AC-O08 | S＋H | S2 | S1 unsupported（V3）；adopt 在 S2 實作 |
| AC-O09 | S＋H | S2 | 同上；unsupported 不繞過 G1／D11 |
| AC-O10 | C＋H | S1 | V8 |
| AC-O11 | C | S1 | V8 |
| AC-O12 | S＋H | S2 | S1 由 skill／人依 D27 核對：T8 的前置是 B1 已 accepted、已 merge、baseline 已登記（tasks 8.0），不自動 merge；controller 的依賴等待自動化在 S2 |
| AC-O13 | S＋H | S2 | 同上 |
| AC-O14 | S＋H | S2 | Retro 候選由 skill 產生；controller 以 op 去重的部分在 S2 |
| AC-O15 | S | S1 | DOC（skill 不自行啟動 P03） |
| AC-O16 | S＋C | S1 | T4.1 DOC；結果只能經匯入生效（V4）|
| AC-O17 | H＋S | DOC | 審查清單 |
| AC-O18 | H＋S | S2 | delegate 在 S1 unsupported |
| AC-O19 | C | S1 | V2 |
| AC-O20 | H | S3 | DOC＋示範 |
| AC-O21 | H | S3 | DOC＋示範 |
| AC-O22 | H＋C | S1 | V3 草案 plan 被拒 |
| AC-O23 | H＋C | S2 | S1 的 scope_change 讓全部派工停止（保守）；只停受影響的 task、其他繼續，留在 S2 |
| AC-O24 | H | S3 | DOC |
| AC-O25 | H | DOC | 審查清單 |
| AC-O26 | C | S1 | V3 |
| AC-O27 | H | DOC | 審查清單 |
| AC-O28 | H | S3 | DOC |

## delivery-gates

| ID | Owner | 切片 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-G01 | C | S1 | V8；R3 |
| AC-G02 | C | S1 | V8 |
| AC-G03 | C | S1 | V6 |
| AC-G04 | C | S1 | V5 |
| AC-G05 | C | S1 | V5 |
| AC-G06 | C | S1 | V5：正常路徑不做 replay 也能通過；矛盾路徑以 replay 作診斷（基準版的 replay 句子已刪除）。R2 |
| AC-G07 | C | S1 | V5（replay 不能補造原始 Red） |
| AC-G08 | C | S1 | V5（attempt 的 commit 範圍→整合 head；pre_review_g1） |
| AC-G09 | C＋H | S1 | V5 |
| AC-G10 | C | S1 | V5 |
| AC-G11 | C＋S | S1 | V6：只有完整範圍、目前版本、`clean` 才通過；`changes_required`、缺 verdict、只審部分 diff 都不通過。R1 |
| AC-G12 | C＋S | S1 | V6；R1（runtime 權限負例） |
| AC-G13 | C | S1 | V7（check 集合待 D11） |
| AC-G14 | C | S1 | V7 |
| AC-G15 | C | S1 | V7（`tested-sha`） |
| AC-G16 | C | S1 | V7（feature 層級的 `version_seq` 跨 purpose 共用；晚到的舊觀察不論 purpose 都不能恢復舊版本；新 head 仍會生效）、V8 |
| AC-G17 | C | S1 | T2.2、V7 |
| AC-G18 | C | S1 | V8 |
| AC-G19 | H | S1 | DOC（報告區分 fake 與 real） |
| AC-G20 | H＋S | S1 | R3；附證據的 Blocked 或沒有真實 finding → 維持 open，不算示範完成 |

## durable-delivery

| ID | Owner | 切片 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-D01 | C | S1 | V2；R3（`status --human`） |
| AC-D02 | C | S1 | V2（D48 邊界） |
| AC-D03 | C | S1 | V2 |
| AC-D04 | C＋S | S1 | V4；R1 |
| AC-D05 | C | S1 | V4 |
| AC-D06 | C | S1 | V4（fake）；R2 |
| AC-D07 | C＋S | S1 | V4 |
| AC-D08 | C | S1 | V4 |
| AC-D09 | C | S1 | V2 |
| AC-D10 | C | S1 | V2 |
| AC-D11 | C | S1 | V2 |
| AC-D12 | C＋S | S1 | V8 |
| AC-D13 | C | S1 | V4 |
| AC-D14 | C＋S | S1 | V9；R3（中斷後接續） |
| AC-D15 | C | S1 | V7 |
| AC-D16 | C | S1 | V4 |
| AC-D17 | C | S1 | V9（在任何真實 writer 之前完成，tasks 7.1→4.2）；R1 |
| AC-D18 | C | S1 | V4；R1 |
| AC-D19 | C | S1 | V1；R1 |
| AC-D20 | S | S2 | 未覆蓋（OpenCode-only transport） |
| AC-D21 | C | S1 | T2.3 |
| AC-D22 | H | DOC | 各接法分開報告；S1 只有 Herdr |
| AC-D23 | C | S1 | V1 |
| AC-D24 | C＋S | S1 | R1 |

## finding-resolution

| ID | Owner | 切片 | 規劃驗證 |
| --- | --- | --- | --- |
| AC-F01 | C＋H | S1 | V6 |
| AC-F02 | C＋H | S1 | V6 |
| AC-F03 | C | S1 | V6 |
| AC-F04 | C＋H | S1 | V6 |
| AC-F05 | C＋S | S1 | V6（文件缺陷可修；policy unknown 不構成修正項） |
| AC-F06 | C | S1 | V6 |
| AC-F07 | C | S1 | V6、V9 |
| AC-F08 | C＋S | S1 | V6 |
| AC-F09 | C | S1 | V6 |
| AC-F10 | C | S1 | V6 |
| AC-F11 | C＋H | S1 | T2.2、V8 |
| AC-F12 | H | S1 | T2.2 路由到 Blocked |
| AC-F13 | C＋S | S1 | V8 |
| AC-F14 | C | S1 | V8 |
| AC-F15 | C | S1 | V6 |
| AC-F16 | C | S1 | V6 |

## S1 findings（全部 open）

| ID | 第一片的處置 | 規劃驗證 |
| --- | --- | --- |
| S1-R01 | controller 不執行 argv；證據工具只接受 `command_id` | V5；R1 |
| S1-R02 | 每次嘗試只有一次外部呼叫；不遞迴、不盲目重試 | V4 |
| S1-R03 | 同一 transition ID 出現不同內容 → Blocked | V2 |
| S1-R04 | 先寫歷史，再更新現行狀態 | V2 |
| S1-R05 | worktree 建立結果 unknown → 交人，不重建 | V4 |
| S1-R06 | 文件 digest 與物件引用分型 | V2 |
| S1-R07 | plan 保存 provenance；批准後可取得第一個許可 | V3；R2 |
| S1-R08 | 預算只在 feature 層，不因換 session 重置 | V2、V9 |
| S1-R09 | D47：在線時有界停止，離線恢復時計入並 Blocked | V9；R1 |
| S1-R10 | scope_change 經公開入口不 crash | V3 |
| S1-R11 | G1 以完整 task 集合判定；adopt 部分延到 S2，此項維持 open | V5 |
| S1-R12 | 派修附完整 finding 快照 | V6；R3 |
| S1-R13 | 原始 Red 逐項核對 | V5 |
| S1-R14 | policy unknown → Blocked，不耗修正輪 | V7 |
| S1-R15 | N/A 與 G2 共用獨立性核對 | V5、V6 |
| S1-R16 | 已 resolved 的同一缺陷再現 → reopen 並 Blocked | V6 |
| S1-R17 | 例外只接受有 decision 的 skipped／neutral | V7 |
