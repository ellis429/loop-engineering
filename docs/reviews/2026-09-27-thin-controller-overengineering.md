# Thin controller 過度設計審核

日期：2026-09-27。範圍：D45-02 候選 spec/design/H1 plan/validation/cleanup。方法：codebase-design 的 Interface、Depth、Locality 與 deletion test；由目前協作者直接審核，未另派 agent、未執行產品測試。下列是設計成本與切片建議，不是新發現的產品 bug，也不是使用者已核准的 scope 變更。

## 結論

**仍有過度設計，不建議照目前 H1 原樣開工。** 問題集中在第一個真實 loop 之前必須完成的範圍，以及協調者每次操作必須理解的協定。檔案數與文件長度不是判定依據。

上輪 review 驗證了設計中的狀態轉移、錯誤路由與文件一致性；那些已修正的問題仍有效。但「設計內部一致」不能證明「這些機制全部值得現在實作」。前一輪協調太著重補齊既有設計，對第一切片的最小範圍控制不足。

本次建議不撤銷三 gates、獨立 Reviewer、原始 TDD、最新版本、finding 覆核、持久化、有界執行與未知時停止。D47–D49 維持。H2／H3 的多人、Project loop、保留 worktrees 與後續 stacked gating 目標也維持。

## Findings（依優先序）

### OE-01：第一個真實 loop 出現得太晚（高）

依據：[tasks 1–15、16](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/tasks.md:319)、[orchestrate 契約](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:429)、[尚未驗證能力](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:30)。

H1 先完成 store、claim、operations、binding、decisions、results、evidence、gates、correction、budget、engine、tools 與整合測試；orchestrate skill、正式 runtime 權限、native 讀回、真實停止與 E2E 留在 H2。H0 和這次文件派工證明部分能力，尚不等於正式 implementation/reviewer profile 可用。

代價：最關鍵的實際接合若不成立，前面已完成的大量 fake 設計可能需要改寫。這是實際風險尚未消除，不是聲稱 runtime 已失敗。

建議：先做小範圍的正式 profile／結果交接／reviewer 能力查核，並把最低限度 orchestrate skill 納入第一個可用切片；先完成「一個 feature 的 G1 → review＋CI → fix → re-review」再擴充 controller 的其餘流程。困難狀態仍先以 fake 測試驗證，保留 H1/H2 假與真實證據的區分。

**決策影響**：要修訂候選 tasks、coverage 與 D45 的階段接合說明，經 D11 採用；不是現在擅自執行 H2 或啟動 example。

### OE-02：序列實作卻每個 attempt 都建立 worktree 與整合（高）

依據：[並行度 1 的 task 路徑](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:310)、[每個 attempt 的 worktree/CAS/整合 log](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:423)。

目前每個 task／fix attempt 都有 worktree、branch、T0、建立 operation、整合 CAS 與 integration log。對第一版的序列任務，這些流程不是隔離不同同時寫入者所必需，卻使建立、整合、恢復與 ref 核對成為每個 task 的成本。

建議：第一版每個 feature 保留一個 Implementer worktree，任務依序執行；Reviewer 仍使用獨立 clone/session。以 task/attempt ID、commit、scope、原始 Red snapshot 追溯每個任務。確認前一 writer 已結束後才交給下一個；unknown writer 仍 Blocked，不能直接重用。需要平行 writer 時，再配置獨立 worktree 與整合規則。

這仍符合使用者要保留 worktrees 的目標。Git push／版本比對仍必要；刪減的是序列 task 之間不必要的跨 worktree 整合，不是全部 git 安全檢查。

**決策影響**：改候選 workspace／assignment／task 路徑與測試，保留 D46 的新舊隔離及 D27 的跨 feature 規則。

### OE-03：唯讀查詢也套完整 operation 執行協定（高）

依據：[prepare/begin/record 含唯讀查詢](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:91)、[operation 狀態與程序身份](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:145)、[observation 週期](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:194)。

查一次 CI 也要登記 operation、消耗 begin、保存 receipt；成功但 pending 又建立下一個 cycle。為此引入 operation attempt、process identity、readback 次數、observe_seq、查回模式等交互規則。這些機制有部分用途，但唯讀查詢不具有重複發文／重複派工的相同風險。

建議分開：

- 外部寫入（派工、push、PR/issue 發布）：保留先登記、單次執行、marker／結果查回；不明就 Blocked，不能盲目重送。
- 純讀取：直接進行有 timeout 與上限的 fetch，將 observation 的 identity、適用版本、觀察順序、來源及 raw evidence 匯入 state；不需要「只能執行一次」的副作用許可。

讀取仍可能失敗、過期或晚到，必須保留 retry/budget、版本與順序檢查。Pass 前也仍要重新觀察。目前 S04 的 sequence 有實際用途，可以作 observation 欄位，不必因此保留所有 read-operation lifecycle。

**決策影響**：候選 DUR-06 目前將首次唯讀查詢納入 begin，須同步修訂 spec/design/tasks，而不是只改 code 跳過 guard。之前 R01/S04 的反例應在新契約下重新驗證。

### OE-04：原始 Red 核對被擴張為每次都重跑歷史測試（中）

依據：[validating 固定 replay 每個 Red](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:311)、[replay 成為每項 Red 有效條件](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:334)、[設計承認 replay 不能證明時序](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/design.md:335)。

原始 Red 捕捉、task/attempt lineage、失敗原因與目前 Green 都是必要。全面 replay 額外要求歷史環境可重建、執行驗證 checkout、比對 failing IDs、維護 replay 路由。它能提供可重現性的補充證據，但不能補造歷史或證明 test-first 時序。

建議：正常路徑核對原始工具證據＋snapshot/provenance＋目前整合 Green，Reviewer 檢查行為及必要時序依據；replay 用於證據矛盾、特定風險或診斷。缺原始 Red 仍不得 Pass。不能藉此把本機 Green 或 CI 任一項刪掉，也不能以 agent 自述取代證據。

**決策影響**：D48 未要求所有 Red 全面 replay，但歷史 D40 設計與新版候選已有相關規則；需明確提出 spec/design 差異並採用，不可直接關閉必需驗證。未提供新的節省量估算。

### OE-05：Project／交付後自動化提前進入 H1 engine（中）

依據：[15 種 decision kinds](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/tasks.md:197)、[依賴、Retro、P03 guard](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/tasks.md:337)。

第一個新 feature 的 review/fix loop 尚未完成，H1 已包含一般化 adopt、epoch abandonment、delegate、accept/return、跨 feature dependency、Retro 操作等路由。這些功能各自合理，但不是全部都必須先寫成程式。

建議第一片集中批准來源、feature owner、派工／結果、三 gates、finding 修正、人工 Blocked 接管。Project Lead 的需求與優先序判斷、驗收後 Retro 候選及尚未支援的 intake 情境先由既有 workflow／skill 依契約處理；controller 記錄結果和批准，不自動啟動下一 feature。Adopt 等未實作入口明示 unsupported，不能接受後再繞過檢查。

**決策影響**：這是自動化時點與責任分配的變更，不是刪除 AC 或最終能力。需在 coverage 標記 controller／skill／人工／後續切片；不能默默將 H1 未做項目算完成。D09 finding closure、D11、D27、D28 保留。

### OE-06：重用稽核過度綁定 symbol／測試實作結構（中）

依據：[逐 symbol／測試案例的 extraction manifest](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/cleanup-map.md:64)、[每個模組必須有 production caller 的硬性測試](/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/d45-02/tasks.md:403)。

來源、已知缺陷及新證據需要記錄。但逐 symbol、逐測試 case 的來源 hash／搬移對照，加上強制每個模組有生產 caller，會使重構必須更新多份結構清單，且仍不能證明入口真正執行了功能。候選文件自己已指出静態可達不等於執行。

建議：以一次提取 commit 或功能規則為單位，記來源 commit/path、已知 finding、改動理由與新驗證。保留必要的依賴方向檢查與乾淨安裝測試；將模組 caller 盤點當 review 輔助，不作每個模組永久維護的硬 gate。不為了滿足稽核表保留舊碼。

**決策影響**：精簡候選 cleanup/tasks，不取消來源追溯、TDD 或獨立覆核。舊 17 findings 仍需個別判斷適用性；移除機制不等於已修，也不授權直接關閉。

## 不應為了精簡而刪除的內容

- 三 gates 獨立判定；G1 在正式 G2 前；最新 head/base/spec/design/plan/policy 綁定。
- 原始 Red 與目前 Green、必要 regression、raw evidence；缺證據 fail closed。
- Reviewer 獨立性與已選 profile 的真實能力驗證；Implementer 不得自行解除 blocker。
- Feature 單一狀態／writer／budget，基本 lock 與 owner claim。這些是防止意外競爭，不應升級為身份平台。
- 原子保存、必要歷史、結果去重與衝突保留；重啟不抹去進度／findings／budget。
- 外部寫入先登記、避免重複派工／發文；unknown 保存並交人。通知仍只是喚醒。
- D47 的時間限制與線上停止／離線核算；修正及 infra retry 上限。
- 最新 CI 的完整必要集合／可信來源／非成功處理，以及正常的 package build／安裝 smoke。

History-first snapshot、digest、基本 claim token 本身有明確用途，不宜因為看起來像資料庫就刪掉。Content-addressed objects 可以評估改為可讀路徑加 digest，但不是前三個優先項；必須先證明能同樣處理原子保存、不可變證據與衝突，不能直接換成會覆寫的 logs。

## 建議下一版的第一個可用切片

1. 先確認選用 runtime 的最小正式交接能力與獨立 Reviewer 權限；能力不足如實 Blocked，不加自建安全平台。
2. 一個新 feature、一個 Implementer worktree、一個獨立 Reviewer；minimum orchestrate skill 呼叫小型 controller。
3. Controller 保存 feature/task/result/finding/decision、判 gates 與必要允許動作；規則仍由程式計算。工具細節由窄 adapter 處理，不把低階查詢協定全部暴露給 skill。
4. 跑通原始 TDD → PR → review/CI → fix → re-review → Pass／Blocked；有界重试、過期結果、重複通知、發布未知與重啟接續都要有適用測試。
5. 再補需要的自動 intake／Project orchestration／並行 task worktrees／更多 runtime，最後到 example 的多 features 與多人展示。

這是修訂建議，尚未採用。不能只把目前一堆操作改名成單一命令而宣稱精簡；必須真的減少第一片要實作的生命週期與自動化承諾。也不建議為此再重寫所有歷史文件：優先修改本次候選的 workspace、operation、evidence、切片計畫及相應 AC 對照，再作針對性 review。

## 審核界線

沒有修改候選 spec/design/tasks/validation、正式 OpenSpec、產品 src/tests 或 GitHub；沒有核准 D11。既有 correctness review 作為其固定版本的證據保留；本報告新增「最小範圍／成本」觀點，不能冒充其原 reviewer 改判。

## 固定輸入 SHA-256

| 檔案 | SHA-256 |
| --- | --- |
| `design.md` | `0293e3d966a2e3c1b13d4e341a09318fd0dd48a0b78ee51a3da30f465b5648ea` |
| `tasks.md` | `7aa1a49036e81c5fb909031a9df72cecfc574889f4e6a98ad825c0a8dac2804e` |
| `validation.md` | `c1aecd0b867f6d1199cda71ca80b21ad1b3cd50f3f327f25d2af8f455b379b20` |
| `spec-delta.md` | `7ebd8d014f5765cc35767a6a4372f4871d70f1af4ef72c3cb940da11a2c18565` |
| `cleanup-map.md` | `f4d092ed2a5f88fc7d71b5eb259e8fb07df6de81a82a1f6b402257b87301691e` |
| `coverage.md` | `2bab038ca6168dc12a565464264d3259526f796834c1ab3be4752b00806b0573` |
