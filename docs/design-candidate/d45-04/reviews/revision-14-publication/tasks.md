# Tasks：第一個可用切片（候選 design-04；revision-13）

> **作者提交狀態**：revision-13；候選，未 D11，不授權實作。目前的 review 狀態以 [README](README.md) 為準。
> **方法**：沿用 writing-plans 6.4.1 的適配版，只寫 scope、owned paths、介面、相依、驗證命令與完成條件，不放實作碼。行為案例以 validation.md 的矩陣列（例如 s1、h8）為準。
> **派工**：D11 後，bootstrap 期間依 D39 由協作者派給 Opus 5.5，GPT 做獨立 review。
> **PR 界線**：
> - task 不等於 PR；
> - T0–T7 放在 bootstrap PR，gate 紀錄見 B1；
> - 第一個有用的 feature 是 T8，要在 T8.0 的 D27 交接之後才開始。

## 通用規則

- **Red**：必須是行為失敗；ImportError 不算。改變行為的修正 attempt 也要有綁定 finding 與 batch 的原始 Red（design §7）。
- **困難狀態**：先寫 fake 測試（PATH 上的假 `herdr`／`gh`＋真 git），才接真實副作用。
- **真實 writer**：只能在 M-OBS o1（讀取預算）、w5（worker 讀取與 writer 結束）與 M-BUD 都通過之後啟動。
- **必要測試政策**：依 validation §0，本機與每個 CI job 用同一套 test-only 設定（T1.1）。
  - 本機套件 session 通過是 G1 的條件，不需要遠端 CI。
  - 遠端必要的 CI job 是否齊全且成功，在 push／PR 之後由 G3 判定。
- **Branch 歷史**：active run 期間只做一般 fast-forward push；整合 base 用 Implementer 在本機 worktree 產生的 merge commit，不是 GitHub PR merge，也不需要 merge 權限；不 rebase、不 squash、不 force-push（design §4、§8）。
- **證據位置**：`.delivery/bootstrap/thin-s1/evidence/<task>/`，索引在 `docs/validation/s1/index.md`。
- **隔離**（D46）：
  - 不 import 舊碼、不用舊的 PYTHONPATH，也不建立 `legacy/`；
  - `import delivery` 必須失敗。

## 0. W1 工作區（協作者，需 D11；本文只描述步驟，不執行）

- [ ] **0.1** 依序執行（全部在 D11 之後）：
  1. **正式 OpenSpec 採用完整基準**：D11 核准時必須同時點名兩層來源與各自的 sha256：D45-02 baseline spec-delta，以及本版 spec-delta（它的「沒列出者沿用基準」依賴 D45-02）。在 `openspec/changes/implement-delivery-loop/specs/` 的四份正式 spec 上，依序套用：
     - D45-02 baseline 的全部條目（含 §0.1 的 banner 替換），被本版覆寫的條目除外；
     - 本版 spec-delta 的全部覆寫；
     - banner 改為記錄 D11 採用來源，移除「scope revision pending」與「D40 已核准」的現行效力敘述。

     結果是四份自足、完整的正式 spec，不再需要另讀任何未採用的 delta。
     - 建一張對照表：正式 spec 的每個 requirement／AC ID → 來源（原文不變、D45-02 條目，或本版覆寫），並記下兩份來源與同步前後各檔的 sha256；
     - 同步只照抄已審的語意。由獨立 Reviewer 依對照表核對組合結果（文件檢查）；有任何與已審版本不同的語意、衝突或遺漏 → 停下回使用者（D11），不自行批准。
  2. **舊計畫退為歷史**：正式 change 內仍描述 D40 舊計畫的 design／tasks，以及正式 spec Purpose 所引用的 `docs/validation/implement-delivery-loop.md`（若存在），都要改為採用後的 design／tasks／validation，或只留一段指向它們的說明。舊內容保留在 Git 歷史，或移到明示「superseded、只作歷史」的位置。`approval.json` 維持原樣，作為歷史。
     - 完成後，除了採用的版本之外，沒有任何檔案自稱是現行的 design、tasks 或 validation。
  3. 在 `loop-engineering` commit 採用後的文件（含第 1、2 步的結果與對照表），記為 **B**。之後 assignment 綁定的 spec digest 取自 B。
  4. **保存既有目錄**：把 `/Users/johnson.chiang/workspace/loop-engineering-thin/{README.md,docs/}` 移到 `…/loop-engineering-thin.pre-w1/`，並記錄移動前後的檔案清單與 sha256。worktree 目的地必須為空。
  5. 執行 `git -C /Users/johnson.chiang/workspace/loop-engineering worktree add -b delivery/thin-controller /Users/johnson.chiang/workspace/loop-engineering-thin B`。
  6. 把候選文件放回 `docs/design-candidate/`，以 sha256 比對確認一致；它們是採用前的來源紀錄，現行權威以 B 中的正式文件為準。
  7. 第一個 commit 移除舊的 `src/delivery`、`tests`，並新增 `docs/implementation/removed-s1.md`，指向 `4ce1110`、`5d334d5`、PR #2。
  - 完成條件：
    - 對照表涵蓋四份正式 spec 的全部 88 個 AC 與每個 requirement，兩份來源的 sha256 等於 D11 核准的版本，並有獨立 Reviewer 的核對紀錄；
    - 正式 change 內沒有與採用版本競爭的現行 design／tasks／validation；
    - `git ls-files src tests` 為空；放回的文件與 `.pre-w1` 的 sha256 一致。

## 執行表

| Task | Owned paths | 公開介面 | 相依 | 驗證命令（矩陣列） |
| --- | --- | --- | --- | --- |
| 1.1 | `pyproject.toml`（含 pytest 設定）、`workflow.yaml`（loopctl 政策檔）、`src/loopctl/{__init__,cli}.py`、`src/loopctl/tools/{__init__,herdr}.py`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`tests/conftest.py`、`tests/test_test_policy.py`、`tests/test_cli.py`、`tests/test_preflight.py` | `status`、`preflight --role R --out P`；CI workflow；測試政策 | 0.1 | `uv run pytest tests/test_test_policy.py tests/test_cli.py tests/test_preflight.py && scripts/dist-smoke.sh`（t1–t6、f1–f3） |
| 1.2 | `docs/validation/s1/preflight/` | preflight（真實） | 1.1 | `loopctl preflight --role implementer --out …/implementer.json`，reviewer 同樣執行一次（R1） |
| 2.1 | `src/loopctl/{store,state}.py`、`tests/test_state.py` | `init`、`claim`、`status [--human]`、`next` | 1.1 | `uv run pytest tests/test_state.py`（s1–s6） |
| 2.2 | `src/loopctl/decisions.py`、`tests/test_decisions.py` | `register`、`decide`（含 `resolve_read`、`resolve_operation` 的紀錄） | 2.1 | `uv run pytest tests/test_decisions.py`（d1、d2、d4–d9） |
| 2.3 | `src/loopctl/{writes,assignments,observe}.py`（observe 由此建立：seq、版本水位、讀取預算、`worker`／`native`）、`src/loopctl/tools/herdr.py`、`tests/fakes/bin/herdr`、`tests/test_observe.py`、`tests/test_writes.py`、`tests/test_public_path.py` | `write <op>`、`result import`、`safety`、`observe worker\|native`；`resolve_read`／`resolve_operation` 的效果 | 2.2 | `uv run pytest tests/test_observe.py tests/test_writes.py tests/test_public_path.py`（o1–o2、w1–w10、d3） |
| 3.1 | `src/loopctl/{evidence,gates}.py`（G1，含整合 attempt 的 parents、匯入與作者編輯分類、scope 核對）、`src/loopctl/tools/evidence.py`（git 呼叫，含 `merge-tree --write-tree`）、`tests/test_g1.py` | `evidence red\|green`、`assess` | 2.3 | `uv run pytest tests/test_g1.py`（g1–g13、g3b） |
| 6.1 | `src/loopctl/observe.py`（延伸 `pr`／`ci`）、`src/loopctl/gates.py`（G3）、`src/loopctl/tools/gh.py`、`tests/fakes/bin/gh`、`tests/test_github.py` | `observe pr\|ci`、`write push\|pr_ensure` | 2.3、3.1 | `uv run pytest tests/test_github.py`（h1–h13，含 h4a–h4e） |
| 7.1 | `src/loopctl/budget.py`、`tests/test_budget.py` | `next`、`safety`（到期 stop） | 2.3、6.1 | `uv run pytest tests/test_budget.py`（b1） |
| 4.1 | `skills/orchestrate/SKILL.md` | 只依 `next`／`safety` 行動 | 2.3 | DOC 清單 `docs/validation/s1/doc/orchestrate.md` |
| 4.2 | `docs/validation/s1/probe/` | 真實 probe | 1.2、3.1、4.1、6.1、7.1 | R2 |
| 4.3 | `docs/validation/s1/workflow-samples/`、`docs/validation/s1/proof.md` | workflow 樣本＋rubric | 4.1 | 經授權的獨立 Reviewer 依 validation §3、§4 審查，並把結果記在 `proof.md`（W-A–W-F） |
| 5.1 | `src/loopctl/findings.py`（含整合 finding 的 ID 與去重、路徑選擇、`base_integration` batch）、`src/loopctl/gates.py`（G2）、`tests/test_review.py` | reviewer 派工、整合 assignment、`result import` | 3.1、4.1、6.1（需要 PR identity） | `uv run pytest tests/test_review.py`（r1–r12、r12b） |
| 6.2 | `src/loopctl/publish.py`、`src/loopctl/gates.py`（Pass、Pass package）、`tests/test_publish_pass.py`、`tests/test_resume.py` | `write publish_*`、`assess`（Pass） | 5.1、6.1 | `uv run pytest tests/test_publish_pass.py tests/test_resume.py`（p1–p6、u1–u2） |
| B1 | `docs/validation/s1/bootstrap-gates.md` | — | 1–7 | 獨立 Reviewer 審查該紀錄 |
| 8.0–8.1 | `docs/validation/s1/delivery/` | 真實 loop | B1 accepted＋merged＋baseline 已登記；feature 已由 D11 選定 | R3 |

執行順序：0.1 → 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 6.1 → 7.1 → 4.1 → 4.3 → 4.2 → 5.1 → 6.2 → B1 → 8.0 → 8.1。

pytest 參數（`--strict-markers` 等）由 `pyproject.toml` 提供，所以各命令不另加旗標。

### 共用檔案（依序擁有，不並行修改）

| 檔案 | 順序 | 規則 |
| --- | --- | --- |
| `src/loopctl/observe.py` | T2.3 建立 → T6.1 延伸 | T6.1 只加 `pr`／`ci` 來源；不改 T2.3 的 seq、水位、預算語意；o1–o2 須在 T6.1 後仍通過 |
| `src/loopctl/gates.py` | T3.1（G1）→ T6.1（G3）→ T5.1（G2）→ T6.2（Pass） | 後一個 task 只加自己的 gate；前面各 task 的矩陣列須仍通過 |
| `src/loopctl/decisions.py` | 只由 T2.2 擁有 | `resolve_read`、`resolve_operation` 在此只記錄；效果在 `observe.py`、`writes.py`，後續 task 不改此檔 |
| `workflow.yaml` | 只由 T1.1 擁有 | 之後的改動需要新的 `policy_change`（design §8） |

相依方向只從前往後：T2.3 不需要 T6.1 的任何介面；w5、w8 使用 T2.3 自己的 `observe worker|native`。沒有循環。

## 完成條件

- [ ] **1.1** t1–t6、f1–f3 通過；dist-smoke 通過；CI workflow 只以 `pull_request` 觸發，每個 job 上傳唯一名稱的 tested SHA 產物；`workflow.yaml` 已建立（check 集合只是候選）。
- [ ] **1.2** 兩個 role 都 verified。任一 unverified → Blocked，不做任何真實派工。這一步不涵蓋 D24。
- [ ] **2.1** s1–s6 通過。
- [ ] **2.2** d1、d2、d4–d9 通過。adopt 與 delegate 只驗證會被拒絕，不算覆蓋。
- [ ] **2.3** o1–o2、w1–w10 與 d3（公開路徑：批准後第一個 assignment 帶 AC 與驗法）通過。
- [ ] **3.1** g1–g13 與 g3b 通過。Red 必須同時符合三項資格：在 scope 內、有捕捉時記錄的對應到 attempt、attempt 是 H 的祖先。只有共同祖先的兄弟 snapshot 無效（D51-R07）。改變行為的修正需要綁定 finding 與 batch 的 Red；被放棄 attempt 的 Red 不轉移；歷史被改寫 → Blocked。g13 依 validation 的步驟，以真 git 分類整合 merge 的匯入與作者編輯：純匯入不要求上游 Red；藏在匯入裡的範圍外作者編輯被拒收。
- [ ] **6.1** h1–h13 通過，其中 h4 含 queued 與其他 workflow 的案例（D51-R03），h4a–h4e 含 push 事件與舊 run 重跑，h10 含延遲建立的反例（D51-R01）與身份比對。
  - PR 正向路徑（AC-A04）：G1 passed → `push` → `pr_ensure`（先持久化預期身份與 marker）→ 記錄 PR identity；結果 unknown 時不盲目重試。
  - G15 只驗負例；非 head 的整合 SHA 映射延到 S2。
- [ ] **7.1** b1 通過。
- [ ] **4.1** orchestrate DOC 清單審查通過。
- [ ] **4.3** W-A–W-F 每組的正例與負例，都由獨立 Reviewer 依 rubric 審查，結果記錄在 `proof.md`。不需要逐樣本的使用者簽核。
- [ ] **4.2** R2：在 `probe/s1-g1` 上跑 fixture，不是交付 feature，也不 merge。結果只算能力證據。
- [ ] **5.1** r1–r12、r12b 通過；review 只在 PR identity 已記錄之後才派出；G2 `blocked` 使 feature Blocked。`integration_required` 依 design §8 的界線處理：在途且有效的 review／CI 照常收齊；其他情況立即走 `pre_review_g1`（原因 `base_integration`），不等待無法開始的 G2 或不會出現的 CI。兩種都是一個 writer、一個 batch、派修時計一輪，只在本機 merge，不呼叫 GitHub PR merge。
- [ ] **6.2** p1–p6、u1–u2 通過；Pass package 由狀態投影。
- [ ] **B1** 協作者依 D39 組出三 gates 紀錄：
  - G1：原始 Red／Green；
  - G2：依 r1 的規則，由獨立 GPT review；
  - G3：D11 核准的集合加上 `policy_change` 綁定 `workflow.yaml`，逐 job 的 tested SHA 等於 H。

  缺任何一項就是 unknown。這份紀錄不是自我託管。
- [ ] **8.0** skill 或人依 D27 核對 B1 的 PR：已人工 accepted、以 GitHub 讀取確認實際 merged 並記下 merge commit、以 `register binding --role baseline` 登記 baseline。不自動 merge；任何一項不成立就不開始 T8。
- [ ] **8.1** R3，使用 D11 選定的 feature。它必須是 B1 尚未實作的有界新行為，才可能有誠實的實作 Red（D51-R04）；本計畫不代為選擇。完成條件：真實 finding → fix（有綁定 finding 與 batch 的原始 Red）→ re-review、三 gates 在目前版本都通過、中斷後成功接續。Blocked 或沒有 finding → 維持 open。

## 延後（只列 outline，不算完成）

- **S2**：
  - adopt（O08、O09）；
  - Project Lead 委派（O18）；
  - Retro op（O14）；
  - O23 的部分接續（scope 變更只停受影響工作）；
  - 跨 feature 依賴自動化；
  - 平行 worktree 與整合規則；
  - G15 整合 SHA 映射；
  - OpenCode-only 部署（D20、D23 的變體）；
  - 同一個 OpenCode 承載兩個角色（D24）。
- **S3**：
  - cross-node-file-transfer 示範；
  - 多人交接；
  - Q-STACK。
