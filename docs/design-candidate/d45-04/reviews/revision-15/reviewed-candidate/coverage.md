# Coverage（候選 design-04；revision-15）

> **作者提交狀態**：revision-15；目前的 review 狀態以 [README](README.md) 為準。
> **全部是 planned。沒有任何測試已執行，也沒有任何 AC 已通過。** 17 項 S1 findings 全部仍 open。revision-12、13、15 只增加驗證引用，類別與計數不變。每個矩陣所屬的 task 見 validation §1.5。
> 88 個 AC 與 17 項 S1 findings 各一列，依 `expected-coverage-02.json`；類別沿用 AC audit。

**類別**
- 核心：58 項；
- WF：workflow／人工契約，17 項；
- 後續：6 項；
- 改寫：3 項；
- 證據：證據規則，3 項；
- 歷史：1 項。

**其他欄位**
- **Owner**：C＝controller、S＝orchestrate skill、H＝人或角色 agent。
- **階段**：
  - S1＝第一片產品測試；
  - S1-W＝第一片的 workflow 樣本加 rubric，由獨立 Reviewer 審查並記在 `proof.md`，不需要逐樣本的使用者簽核；
  - S2／S3＝延後，不算完成；
  - handoff＝只留在交接紀錄。
- **驗證**：對應 validation.md 的矩陣列、樣本或 R 項目。

## delivery-orchestration

| ID | 類別 | Owner | 階段 | 驗證 |
| --- | --- | --- | --- | --- |
| AC-O01 | WF | H＋C | S1、S1-W | d1；W-C |
| AC-O02 | 核心 | C＋S | S1 | s4；r1（沒有授權的 review 不進 G2） |
| AC-O03 | 核心 | C | S1 | d6 |
| AC-O04 | WF | H＋C | S1-W | W-B |
| AC-O05 | 核心 | C | S1 | d1、d2 |
| AC-O06 | 核心 | C＋S | S1 | d3；R2 |
| AC-O07 | 核心 | C＋H | S1 | d4（整個 run 停下等批准） |
| AC-O08 | 後續 | S＋H | S2 | 第一片只驗 d8 的拒絕，不算覆蓋 |
| AC-O09 | 後續 | S＋H | S2 | 同上 |
| AC-O10 | 核心 | C＋H | S1 | p6（含 `write merge\|close\|release\|deploy` 被拒、0 次外部呼叫）；r12（整合 base 是本機 merge commit，0 次 GitHub PR merge） |
| AC-O11 | 核心 | C | S1 | d7a、d7b |
| AC-O12 | WF | S＋H | S1-W | W-D；T8.0；自動化延到 S2 |
| AC-O13 | WF | S＋H | S1-W | W-D；T8.0 |
| AC-O14 | 後續 | S＋H | S2 | Retro op 延後 |
| AC-O15 | 歷史 | H＋C | handoff、S1 | s7（沒有 `init` 不接管）；W-F（產品不做 P03 特判） |
| AC-O16 | WF | S＋C | S1-W | W-E；T4.1 DOC |
| AC-O17 | WF | H＋S | S1-W | W-E |
| AC-O18 | 後續 | H＋S | S2 | 第一片只驗 d8 的拒絕 |
| AC-O19 | WF | C＋H | S1、S1-W | d5；W-E |
| AC-O20 | WF | H | S1-W | W-A |
| AC-O21 | WF | H | S1-W | W-A |
| AC-O22 | WF | H＋C | S1、S1-W | d2；W-C |
| AC-O23 | WF | H＋C | S1、S1-W；部分 S2 | d4、W-C：第一片 scope_change 讓整個 run 停下。只停受影響工作、其餘繼續 → 延到 S2，不算完成（spec-delta §9、design §1、tasks 延後清單） |
| AC-O24 | WF | H | S1-W | W-A |
| AC-O25 | WF | H | S1-W | W-B |
| AC-O26 | WF | H＋C | S1、S1-W | d2；W-C |
| AC-O27 | WF | H | S1-W | W-B |
| AC-O28 | WF | H | S1-W | W-A |

## delivery-gates

| ID | 類別 | Owner | 階段 | 驗證 |
| --- | --- | --- | --- | --- |
| AC-G01 | 核心 | C | S1 | p1（Pass package）、p7（Pass 前確認觀察）、h10（PR 身份與 marker；G1 未通過 0 次 push）；R3 |
| AC-G02 | 核心 | C | S1 | p2 |
| AC-G03 | 核心 | C | S1 | r1（`blocked` → G2 unknown＋feature Blocked） |
| AC-G04 | 核心 | C | S1 | g3、g3b、g10 |
| AC-G05 | 核心 | C | S1 | g5（Green 記錄的 SHA 等於 D；D 上失敗 → 不通過） |
| AC-G06 | 核心 | C | S1 | g1、g2、g3b（scope、對應到 attempt 的捕捉紀錄、attempt 到 H 的 lineage；兄弟 snapshot 無效）；g10（修正 Red 綁定 finding 與 batch）、g11（放棄的 attempt）、g12（歷史改寫）、g13（merge 整合）；r11 |
| AC-G07 | 核心 | C | S1 | g2、g4、g10、g11 |
| AC-G08 | 核心 | C | S1 | g6、r13（整合 regression → `pre_review_g1`）、g3b、g13（整合 merge 的匯入與作者編輯對應）；g14（Green 在 H 的乾淨 checkout）；Green 只在實際的 head 執行（h7） |
| AC-G09 | 核心 | C＋H | S1 | g7（含只改註解的設定檔與測試檔） |
| AC-G10 | 核心 | C | S1 | g8（依實際行為判定） |
| AC-G11 | 核心 | C＋S | S1 | r1；f4（兩個 profile 的 model 相同 → unverified）；R1 |
| AC-G12 | 核心 | C＋S | S1 | r1；f5（負例未被拒或資源改變 → unverified）；R1（權限負例與資源檢查） |
| AC-G13 | 核心 | C | S1 | h1、h2、h3、h9、h12（逐 job 的 tested SHA）；t1–t6（本機與每個 CI job 同一 skip 政策）；b4（CI 等待逾時 → unknown）；p1（`github_rules_verified`）（check 集合提案見 validation §6，待 D11） |
| AC-G14 | 核心 | C | S1 | h4、h4a–h4e（只由 PR 事件觸發；事件／PR 不符 → unknown；每個 run 取最新 attempt；同一 H 的多個 run 都計入；`run_id` 只作識別；無法排序 → unknown；只有 commit status → unknown）；h12 |
| AC-G15 | 改寫 | C | S1（負例）／S2（正向） | 第一片只驗 h5 的 unknown；映射能力延後，不算覆蓋 |
| AC-G16 | 核心 | C | S1 | h6 |
| AC-G17 | 核心 | C | S1 | h7（沒有整合觸發：在 H 重跑 Green 並重新綁定）；h13、r12（整合觸發、finding 去重、一般收齊與 `base_integration` 路徑的界線、新 head 完整 gates）；g12、g13、h11（merge 整合保留 lineage，匯入與作者編輯分開核對 scope 與 Red；只 fast-forward push；歷史改寫 → Blocked） |
| AC-G18 | 核心 | C | S1 | p3、p7 |
| AC-G19 | 證據 | H | S1-W | `proof.md` rubric（§4） |
| AC-G20 | 證據 | H＋S | S1 | r1（clean 時 0 個新 finding，不虛構 blocker）；R3（feature 待 T8 的 D11 選定，必須是 B1 尚未實作的行為）；沒有真實 finding 或 Blocked → 維持 open |

## durable-delivery

| ID | 類別 | Owner | 階段 | 驗證 |
| --- | --- | --- | --- | --- |
| AC-D01 | 核心 | C | S1 | s5（`status --human` 在 T2.1 實作，不再是 T8 的候選） |
| AC-D02 | 核心 | C | S1 | s3（D48 邊界） |
| AC-D03 | 核心 | C | S1 | s4 |
| AC-D04 | 核心 | C＋S | S1 | w5（T2.3 的 `observe worker\|native`）；w8（turn 未完成不算結束）；b2（逾時 stop 未確認 → 不派新 attempt）；R1 |
| AC-D05 | 核心 | C | S1 | w6 |
| AC-D06 | 核心 | C | S1 | w8（含其他 attempt 的 marker、turn 未完成）、o2；R2 |
| AC-D07 | 核心 | C＋S | S1 | u1 |
| AC-D08 | 核心 | C | S1 | w7 |
| AC-D09 | 核心 | C | S1 | s1、s2 |
| AC-D10 | 改寫 | C | S1 | s1、s2（對外語意；history-first 只是設計細節） |
| AC-D11 | 核心 | C | S1 | s3 |
| AC-D12 | 核心 | C＋S | S1 | w2（含 marker／身份不符的讀回）、p5、w10、h10 |
| AC-D13 | 核心 | C | S1 | w1、w3、w10（`resolve_operation` 只記錄）、w11（寫入逾時 → unknown）、d9、h10、h11 |
| AC-D14 | 核心 | C＋S | S1 | u1；R3（中斷後接續） |
| AC-D15 | 核心 | C | S1 | u2、h7 |
| AC-D16 | 核心 | C | S1 | w4、o1、o3（讀取逾時計入）、h8（含分頁失敗）、d9 |
| AC-D17 | 核心 | C | S1 | b1–b4（active 區間、角色 timeout 與到限路徑）、d10（`budget_extension` 只記錄）；R1 |
| AC-D18 | 核心 | C | S1 | f3、w6；R1 |
| AC-D19 | 核心 | C | S1 | f1、f4、f5；R1 |
| AC-D20 | 後續 | S | S2 | OpenCode-only，未覆蓋 |
| AC-D21 | 核心 | C | S1 | w9 |
| AC-D22 | 證據 | H | S1-W | `proof.md` rubric；只有 Herdr 兩條路徑，其他接法 none |
| AC-D23 | 改寫 | C | S1 | f2（第一片未選的選配接入）；OpenCode-only 變體延到 S2 |
| AC-D24 | 後續 | C＋S | S2 | 同一 OpenCode 承載兩個角色；R1 不能證明 |

## finding-resolution

| ID | 類別 | Owner | 階段 | 驗證 |
| --- | --- | --- | --- | --- |
| AC-F01 | 核心 | C＋H | S1 | r2 |
| AC-F02 | 核心 | C＋H | S1 | r3 |
| AC-F03 | 核心 | C | S1 | r4 |
| AC-F04 | 核心 | C＋H | S1 | r4 |
| AC-F05 | 核心 | C＋S | S1 | r5 |
| AC-F06 | 核心 | C | S1 | r6 |
| AC-F07 | 核心 | C | S1 | r7、r13(c)、d10 |
| AC-F08 | 核心 | C＋S | S1 | r8 |
| AC-F09 | 核心 | C | S1 | r8 |
| AC-F10 | 核心 | C | S1 | r8 |
| AC-F11 | 核心 | C＋H | S1 | d7a、d7b |
| AC-F12 | WF | H | S1-W | W-C |
| AC-F13 | 核心 | C＋S | S1 | p4（含讀回被竄改） |
| AC-F14 | 核心 | C | S1 | p5、u1 |
| AC-F15 | 核心 | C | S1 | r9 |
| AC-F16 | 核心 | C | S1 | r9 |

## S1 findings（全部 open；新測試通過、再經獨立覆核之後才可能關閉）

| ID | 第一片的處置 | 驗證 |
| --- | --- | --- |
| S1-R01 | controller 不執行 argv；證據工具只接受 `command_id` | g9；R1 |
| S1-R02 | 每次嘗試只呼叫外部一次；不遞迴、不盲目重試 | w1、w3、w10 |
| S1-R03 | transition 衝突 → Blocked | s3 |
| S1-R04 | 已提交與未提交的狀態分開 | s1、s2 |
| S1-R05 | worktree 建立結果 unknown → 交人 | w3 |
| S1-R06 | 文件 digest 與物件引用分型 | s6 |
| S1-R07 | plan 有 provenance；批准後的第一個 assignment | d2、d3 |
| S1-R08 | 預算只在 feature 層，不因換 session 重置 | s4、b1 |
| S1-R09 | D47：在線時停止，離線恢復時計入並 Blocked | b1；R1 |
| S1-R10 | scope_change 不 crash | d4 |
| S1-R11 | task 集合為空 → G1 fail（audit 已重現舊碼的這個缺陷）；adopt 部分延到 S2 | g4 |
| S1-R12 | 派修附完整 finding 快照，派出後不隨 registry 改變 | r10 |
| S1-R13 | 原始 Red 逐項核對，並要求 scope、對應到 attempt 的捕捉紀錄、lineage 三項資格 | g3、g3b、g9、g10、g11 |
| S1-R14 | 403 且沒有適用政策 → Blocked，不耗修正輪 | h1 |
| S1-R15 | N/A 與 G2 共用獨立性核對 | g8、r1 |
| S1-R16 | 已 resolved 的同一缺陷再現 → reopen | r9 |
| S1-R17 | 例外只接受有 decision 的 skipped／neutral | h3 |
