# Controller detailed design review — design-02

Verdict: **changes_required**。9 個 confirmed blocking 設計缺口（8 P1、1 P2）；這是固定快照文件 review，不是產品 G2，也不是 D11 開工批准。15 份 inputs 與 4 份 outputs 的完整 SHA-256 見 review.json；草稿宣告的 hashes 均相符。

## Findings

### DR-01 [P1 / blocking] clone＋環境清理＋事後比較不能證明 Reviewer 或 worker 的寫入權限隔離

**位置：** outputs/design.md:184–188、outputs/design.md:230–238、outputs/tasks.md:72、outputs/validation.md:73。

**依據：** delivery-gates/spec.md GAT-05 / AC-G12；durable-delivery/spec.md DUR-02 / DUR-09 / AC-D24；D09、D23、D38。

**反例：** Reviewer 以同 UID 執行 shell/test subprocess，可使用作者 repo 的絕對路徑寫檔或 update-ref，之後還原；clone 不共享 refs 只保護預設 cwd，HOME/env 清理不改 filesystem 權限，事後 refs/status 不變不能證明中間不可寫。同樣可修改 run/evidence；載入前或同時修改 evidence 及 digest 不會被單次 digest 比對辨識。草稿一面承認沒有防止能力，一面允許三項檢查齊全即 isolation=verified，與 task 的『寫 author branch 應失敗』無法同時成立。

**修正要求：** 提出可實施的權限邊界（例如經驗證的 sandbox/不同 UID），明確允許工作區、結果通道、state/author repo/credential 拒絕規則及 subprocess 繼承；未具拒絕能力的 profile 必須維持 unverified，不能藉事後比對升格。補同 UID/跨目錄/子程序負例及 controller authority 寫入拒絕測試。平台與 reviewer 型號待選本身不是此 finding；問題是候選 verified 條件不足。

**驗證缺口：** AC-G12 表已要求真實拒寫，但 task 4.3 只有 clone/env/ref 實作，未安排能使該測試通過的機制。

### DR-02 [P1 / blocking] issue 觀察時間進入 version_key，使內容未變的 reconcile 也淘汰所有結果

**位置：** outputs/design.md:154–165、outputs/tasks.md:47。

**依據：** delivery-gates/spec.md GAT-01 / GAT-07 / AC-G01、G16；delivery-orchestration/spec.md ORC-02 / AC-O03；D01、D19。

**反例：** 同一 issue body 在 t1、t2 讀到完全相同 bytes，但 spec_digests 含 observed_at；canonical JSON hash 因此變成 V2。於 V1 派出的 review 在下一次 reconcile 到達時被第163行判歷史，G1/G2/G3 無法穩定收齊。若凍結採用時間避免此問題，草稿也未定義 observed_at 是不可變採用時間或每次讀取時間。

**修正要求：** 將觀察/查核時間與採用內容版本分離；明定同內容重讀 version_key 不變、何時建立新的 adopted binding，以及保存每次觀察的方式。補固定內容多次 poll/restart 可到 Pass 的測試，並驗真正 body 更新才失效。

**驗證缺口：** 逐列重述失效矩陣未驗證 unchanged-content polling 的穩定性。

### DR-03 [P1 / blocking] PR 建立及 base 更新後，保留的 G1 沒有重新綁定當前版本的規則

**位置：** outputs/design.md:106–109、outputs/design.md:154–164、outputs/design.md:204、outputs/validation.md:78。

**依據：** delivery-gates/spec.md GAT-01 / GAT-07 / AC-G01、G17；delivery-orchestration/spec.md ORC-04 / AC-O08；workflow-contracts.md Gate 評估與版本失效；D01、D19。

**反例：** 新 feature 先在沒有 PR 的 VersionSet 判 G1，之後才建立 PR；pr=null→PR number 改了 version_key，但沒有此變化的失效/沿用轉移。另一條明文路徑是 base B1→B2 時 g1 保留、直接 checking；其結果仍綁 V1，而新 G2/G3 綁 V2。Pass 又嚴格要求三者相同 key，故永遠無法完成；若直接改 key 則遺失必要的 evidence 適用性理由。

**修正要求：** 分開不可變 evidence source binding 與當前 gate assessment，為首次 PR binding、base/merge-base 改變明定重評/沿用條件及理由，產生綁當前 key 的新 assessment；不得改寫原證據身份。base 變動須評估整合風險，不無條件沿用。補 pre-PR→create PR→Pass、base-only change→recheck→Pass/Blocked 的端到端狀態機案例。

**驗證缺口：** AC-G17 目前只斷言 g2 stale/spec await approval，沒有驗重新收齊同版本三 gates。

### DR-04 [P1 / blocking] git stash create 無法保存一般 TDD 新增的 untracked 測試

**位置：** outputs/design.md:171–174、outputs/tasks.md:33–35。

**依據：** delivery-gates/spec.md GAT-02 / GAT-03 / AC-G06、G07；D01、D26。

**反例：** worker 新建 tests/test_new.py 並執行 Red，尚未 git add。只有新檔時 stash create 回空而落到 HEAD；另有 tracked 變更時 snapshot 仍不含新檔。日誌含 failing test，保存的 source tree 卻沒有該測試；always-on replay 找不到原測試而把合法 test-first 判 invalid/unknown。協作者另以純 tmp git repo 重現此兩種情境，證據見 review/red-snapshot-probe.json（本 reviewer 未重跑）。

**修正要求：** 設計不污染 worker index/worktree 的完整 snapshot 程序，或明訂並驗證必要的 tracked/staged 前置條件；必須保存實際執行所用的授權新測試與 tracked 修改，排除 secrets/ignored 非 scope 資料。補僅 untracked 新測試、tracked＋untracked 混合的真 git 測試，從 snapshot checkout 可重現相同 failing IDs。

**驗證缺口：** task 1.2 雖寫『含未提交測試檔』，未區分 staged、tracked dirty 與 untracked；現有選用命令無法達成其通過標準。

### DR-05 [P1 / blocking] 直接 feature branch 與 per-attempt branch 兩種整合模型互相矛盾

**位置：** outputs/design.md:174、outputs/design.md:236–237、outputs/design.md:242、outputs/tasks.md:41、outputs/tasks.md:64。

**依據：** delivery-gates/spec.md GAT-03 / AC-G08；durable-delivery/spec.md DUR-02 / DUR-05 / DUR-07；D01、D13、D19。

**反例：** G1 以 task commits 直接進 feature branch、ancestry 即 lineage 為前提；ownership 卻要求每個 attempt 專屬 branch，只有 controller 整合有效 lease 的 branch。若照前者做，舊 attempt 可直接改整合來源而 fencing 不成立；若照後者做，沒有選定 fast-forward/merge/cherry-pick、整合前置 SHA、task→integration mapping 與 crash recovery，且 operation kinds 無 integration。crash 在 ref 已更新、task 尚未標整合之間，resume 無明確準則辨識是否需重做。

**修正要求：** 選定唯一 writer/branch/整合策略，定義有效 attempt 的選取、整合前後 SHA、原子 ref 更新或可查回 operation、衝突及 crash 恢復，補對應 task。歷史 Red lineage 規則須對該策略成立。補兩 task 依序整合、舊 attempt 晚到、整合提交前後 crash、整合 regression 失敗的真 git/controller 測試。

**驗證缺口：** 目前 AC-G08 只注入『整合 regression 紅』；未驗 task 產物如何真正成為同一個可恢復的 integration head。

### DR-06 [P1 / blocking] 全主機 flock 配 repo-local registry，不能在換 clone 或 crash 後保存同 feature 控制權及預算

**位置：** outputs/design.md:61–64、outputs/design.md:233–237、outputs/design.md:263、outputs/validation.md:89–103。

**依據：** durable-delivery/spec.md DUR-02 / DUR-07 / DUR-08 / AC-D03、D04、D17；finding-resolution/spec.md FIN-03 / AC-F07；D08、D13。

**反例：** clone A 的 run 已耗三輪或 controller crash 而 worker 尚活著；process flock 已釋放。clone B 用相同 GitHub repo+feature 取得同一 host lock，但 B 的 .delivery/project.json 不含 A 的 active run、worker handles 或累計預算。第234行僅查本地登記，第263行也僅依該 project.json 累計，故新 run 可從零派工。holder 資訊沒有規定持久 authority locator/恢復步驟，無法修補此缺口。

**修正要求：** 在 canonical repo+feature identity 下保存可恢復的 authority locator/owner 與預算 lineage，所有 clone/start/adopt 先解析並 reconcile 原 authority，缺失/不可讀不能建立空白替代。或明確拒絕同 feature 的另一 clone，且拒絕資訊須在 process 結束後仍可核對。定義 project 指標更新/修復與 budget authority，補跨 clone、不同 run、原 controller 結束/崩潰後的測試。

**驗證缺口：** 只有同時 start 的兩 subprocess 測試及同 run restart 到限；沒有 sequential replacement clone/run 的繞過案例。

### DR-07 [P1 / blocking] dispatch 只查 session marker 就成功，未處理建立 session 與送 prompt 之間的中斷

**位置：** outputs/design.md:242–254、outputs/design.md:275–281、outputs/tasks.md:42。

**依據：** durable-delivery/spec.md DUR-03 / DUR-06 / DUR-07 / AC-D06、D12、D13、D14；D09、D24、D38。

**反例：** OpenCode 派工至少包含建立 session 與送 prompt；session title 已有 attempt_id，controller 在 prompt 送出前 crash。resume lookup 找到 session marker，依第247行便把 dispatch 判 succeeded，但實際未派出工作。相反，prompt 已被接受而回應遺失時，session 存在不能判斷是否可重送。marker 在『首則訊息』也沒有規定建立 session 成功但首訊息不存在時的安全路徑。

**修正要求：** 將 dispatch 的可恢復階段具體化，分別持久記錄 session 建立、prompt/request identity、runtime 接受及 completion；lookup 必須核對目標/payload 與實際訊息或可靠 idempotency 能力，而非 session 存在即成功。prompt outcome 無法證實未送達時維持 unknown/Blocked。補 session create 前後、prompt accept 前後及 receipt 保存前後的故障矩陣，對照查回與外部呼叫次數。

**驗證缺口：** outbox 測試目前集中 GitHub comment 回應遺失；native-message result 測試也不能驗證 dispatch 的兩階段恢復。

### DR-08 [P2 / blocking] G3 僅查 head SHA，取得不到設計允許的衍生 merge snapshot checks

**位置：** outputs/design.md:197–199、outputs/validation.md:76、outputs/tasks.md:51。

**依據：** delivery-gates/spec.md GAT-06 / AC-G15；D01、D29。

**反例：** repo 的必要 check 綁定經核對的 integration commit M，而不是 PR head H。第197行只向 H 取得 check-runs/statuses，結果是 missing；第199行的 M parents 驗證沒有候選 check 可執行。若 fake 直接餵 M 的 check 給 evaluator，AC-G15 會通過，但真實 adapter 仍永久拒絕此合法 CI 路徑。

**修正要求：** 定義候選 CI source SHAs 的發現及 readback，從固定 head/base/PR merge mapping 取得 M，再查相應 checks；保存 mapping 與適用 policy，拒絕過期 base/head 的 M。補 adapter contract 及 GH 案例：H 無 check、M 有 required check，合法 M 可採用、舊 M 不可採用，不能只測 parents 純函式。

**驗證缺口：** Pass 標準只有 parents 驗證，未涵蓋取得該 check 的完整查詢路徑。

### DR-09 [P1 / blocking] write-once blob 沒有定義先於 run snapshot 的持久化屏障

**位置：** outputs/design.md:229–232、outputs/design.md:244–246、outputs/tasks.md:40、outputs/validation.md:93–96。

**依據：** durable-delivery/spec.md DUR-04 / DUR-05 / AC-D07、D09；docs/file-state.md 最小一致性策略第3、4項；D14、D24。

**反例：** snapshot 明定 fsync→replace→目錄 fsync，但 assignments/results/evidence/receipts 只規定 os.link(tmp, final)。link 的原子名稱建立不等於檔案內容及 directory entry 已持久；在 blob 仍未同步時先提交引用它的 durable run.json，主機 crash 後可留下現行 gate/operation 引用缺失或不完整 blob。write-once 與同 attempt 衝突規則也不能重建遺失原文。

**修正要求：** 定義 blobs（含其原始 log、receipt、assignment）的 write/flush/fsync、不可覆寫發布、目錄同步及失敗處理；只有全部依賴已完成持久保存才可提交引用 snapshot/發外部操作。記錄 macOS/Linux 的適用保證。補各持久化邊界的故障注入及引用完整性測試，區分 process kill 與主機/儲存 crash 的驗證範圍，不宣稱 os._exit 已驗 power-loss durability。

**驗證缺口：** 現有測法驗 snapshot 舊/新版及 result 去重，沒有驗已提交 snapshot 的每個引用必然先完成持久保存。

## 未列為 blocker 的事項

模型／平台待查、方法適配、3 PR 切片與候選 timeout/recurrence 的提案狀態保留。D27 的 accepted＋merged 前置、bootstrap 與產品執行區分、finding closure/dispute，以及 final Pass 的觀察式競態處理均未另外發現可證明 blocker。

A13 是 project-intent.md 的既有 E2E 情境，建議補來源標籤；不是四份 spec 的新增 AC。88/88 AC 對照僅證明索引完整，不能補足上述語意測試缺口。

本 reviewer 未跑產品測試，未讀或改 live repo，未發文或派子代理；未宣稱執行 git-diff code-review skill。DR-04 的 tmp git probe 由協作者執行並提供摘要。
