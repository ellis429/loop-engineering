# Tasks：第一個可用切片（候選 design-04，AC audit 修訂）

> **狀態**：候選，未 D11，不授權實作。
> **方法**：沿用 writing-plans 6.4.1 的適配版，只寫 scope、owned paths、介面、相依、驗證命令與完成條件，不放實作碼。行為案例以 validation.md 的矩陣列（例如 s1、h8）為準。
> **派工**：D11 後，bootstrap 期間依 D39 由協作者派給 Opus 5.5，GPT 做獨立 review。
> **PR 界線**：
> - task 不等於 PR；
> - T0–T7 放在 bootstrap PR，gate 紀錄見 B1；
> - 第一個有用的 feature 是 T8，要在 T8.0 的 D27 交接之後才開始。

## 通用規則

- **Red**：必須是行為失敗；ImportError 不算。
- **困難狀態**：先寫 fake 測試（PATH 上的假 `herdr`／`gh`＋真 git），才接真實副作用。
- **真實 writer**：只能在 M-GH h8（讀取預算）、worker 讀取與 M-BUD 都通過之後啟動。
- **必要測試政策**：依 validation §0。
  - 本機適用的套件必須完整收集並 pass，且只允許平台條件造成的 skip；這是 G1 的條件，不需要遠端 CI。
  - 遠端必要的 CI job 是否齊全，在 push／PR 之後由 G3 判定。
- **證據位置**：`.delivery/bootstrap/thin-s1/evidence/<task>/`，索引在 `docs/validation/s1/index.md`。
- **隔離**（D46）：
  - 不 import 舊碼、不用舊的 PYTHONPATH，也不建立 `legacy/`；
  - `import delivery` 必須失敗。

## 0. W1 工作區（協作者，需 D11；本文只描述步驟，不執行）

- [ ] **0.1** 依序執行：
  1. 在 `loop-engineering` commit 採用後的文件，記為 **B**。
  2. **保存既有目錄**：把 `/Users/johnson.chiang/workspace/loop-engineering-thin/{README.md,docs/}` 移到 `…/loop-engineering-thin.pre-w1/`，並記錄移動前後的檔案清單與 sha256。worktree 目的地必須為空。
  3. 執行 `git -C /Users/johnson.chiang/workspace/loop-engineering worktree add -b delivery/thin-controller /Users/johnson.chiang/workspace/loop-engineering-thin B`。
  4. 把候選文件放回 `docs/design-candidate/`，以 sha256 比對確認一致。
  5. 第一個 commit 移除舊的 `src/delivery`、`tests`，並新增 `docs/implementation/removed-s1.md`，指向 `4ce1110`、`5d334d5`、PR #2。
  - 完成條件：`git ls-files src tests` 為空；放回的文件與 `.pre-w1` 的 sha256 一致。

## 執行表

| Task | Owned paths | 公開介面 | 相依 | 驗證命令（矩陣列） |
| --- | --- | --- | --- | --- |
| 1.1 | `pyproject.toml`、`src/loopctl/{__init__,cli}.py`、`src/loopctl/tools/{__init__,herdr}.py`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`tests/test_cli.py`、`tests/test_preflight.py` | `status`、`preflight --role R --out P`；CI workflow | 0.1 | `uv run pytest tests/test_cli.py tests/test_preflight.py -q && scripts/dist-smoke.sh`（f1–f3） |
| 1.2 | `docs/validation/s1/preflight/` | preflight（真實） | 1.1 | `loopctl preflight --role implementer --out …/implementer.json`，reviewer 同樣執行一次（R1） |
| 2.1 | `src/loopctl/{store,state}.py`、`tests/test_state.py` | `init`、`claim`、`status [--human]`、`next` | 1.1 | `uv run pytest tests/test_state.py -q`（s1–s6） |
| 2.2 | `src/loopctl/decisions.py`、`tests/test_decisions.py` | `register`、`decide` | 2.1 | `uv run pytest tests/test_decisions.py -q`（d1、d2、d4–d8） |
| 2.3 | `src/loopctl/{writes,assignments}.py`、`src/loopctl/tools/herdr.py`、`tests/fakes/bin/herdr`、`tests/test_writes.py`、`tests/test_public_path.py` | `write <op>`、`result import`、`safety` | 2.2 | `uv run pytest tests/test_writes.py tests/test_public_path.py -q`（w1–w9、d3） |
| 3.1 | `src/loopctl/{evidence,gates}.py`（G1）、`src/loopctl/tools/evidence.py`、`tests/test_g1.py` | `evidence red\|green`、`assess` | 2.3 | `uv run pytest tests/test_g1.py -q`（g1–g9、g3b） |
| 6.1 | `src/loopctl/observe.py`、`src/loopctl/gates.py`（G3）、`src/loopctl/tools/gh.py`、`tests/fakes/bin/gh`、`tests/test_github.py` | `observe pr\|ci\|worker\|native`、`write push\|pr_ensure`、`decide resolve_read` | 2.3、3.1 | `uv run pytest tests/test_github.py -q`（h1–h10） |
| 7.1 | `src/loopctl/budget.py`、`tests/test_budget.py` | `next`、`safety`（到期 stop） | 2.3、6.1 | `uv run pytest tests/test_budget.py -q`（b1） |
| 4.1 | `skills/orchestrate/SKILL.md` | 只依 `next`／`safety` 行動 | 2.3 | DOC 清單 `docs/validation/s1/doc/orchestrate.md` |
| 4.2 | `docs/validation/s1/probe/` | 真實 probe | 1.2、3.1、4.1、6.1、7.1 | R2 |
| 4.3 | `docs/validation/s1/workflow-samples/`、`docs/validation/s1/proof.md` | workflow 樣本＋rubric | 4.1 | 經授權的獨立 Reviewer 依 validation §3、§4 審查，並把結果記在 `proof.md`（W-A–W-F） |
| 5.1 | `src/loopctl/findings.py`、`src/loopctl/gates.py`（G2）、`tests/test_review.py` | reviewer 派工、`result import` | 3.1、4.1、6.1（需要 PR identity） | `uv run pytest tests/test_review.py -q`（r1–r10） |
| 6.2 | `src/loopctl/publish.py`、`tests/test_publish_pass.py`、`tests/test_resume.py` | `write publish_*`、`assess`（Pass） | 5.1、6.1 | `uv run pytest tests/test_publish_pass.py tests/test_resume.py -q`（p1–p6、u1–u2） |
| B1 | `docs/validation/s1/bootstrap-gates.md` | — | 1–7 | 獨立 Reviewer 審查該紀錄 |
| 8.0–8.1 | `docs/validation/s1/delivery/` | 真實 loop | B1 accepted＋merged＋baseline 已登記；feature 已由 D11 選定 | R3 |

執行順序：0.1 → 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 6.1 → 7.1 → 4.1 → 4.3 → 4.2 → 5.1 → 6.2 → B1 → 8.0 → 8.1。

## 完成條件

- [ ] **1.1** f1–f3 通過；dist-smoke 通過；CI workflow 已建立（check 集合只是候選）。
- [ ] **1.2** 兩個 role 都 verified。任一 unverified → Blocked，不做任何真實派工。這一步不涵蓋 D24。
- [ ] **2.1** s1–s6 通過。
- [ ] **2.2** d1、d2、d4–d8 通過。adopt 與 delegate 只驗證會被拒絕，不算覆蓋。
- [ ] **2.3** w1–w9 與 d3（公開路徑：批准後第一個 assignment 帶 AC 與驗法）通過。
- [ ] **3.1** g1–g9 與 g3b 通過。Red 必須同時符合三項資格：在 scope 內、有捕捉時記錄的對應到 attempt、attempt 是 H 的祖先。只有共同祖先的兄弟 snapshot 無效（D51-R07）。
- [ ] **6.1** h1–h10 通過，其中 h4 含 queued 與其他 workflow 的案例（D51-R03），h10 含延遲建立的反例（D51-R01）。
  - PR 正向路徑（AC-A04）：G1 passed → `push` → `pr_ensure` → 記錄 PR identity；結果 unknown 時不盲目重試。
  - G15 只驗負例；非 head 的整合 SHA 映射延到 S2。
- [ ] **7.1** b1 通過。
- [ ] **4.1** orchestrate DOC 清單審查通過。
- [ ] **4.3** W-A–W-F 每組的正例與負例，都由獨立 Reviewer 依 rubric 審查，結果記錄在 `proof.md`。不需要逐樣本的使用者簽核。
- [ ] **4.2** R2：在 `probe/s1-g1` 上跑 fixture，不是交付 feature，也不 merge。結果只算能力證據。
- [ ] **5.1** r1–r10 通過；review 只在 PR identity 已記錄之後才派出。
- [ ] **6.2** p1–p6、u1–u2 通過。
- [ ] **B1** 協作者依 D39 組出三 gates 紀錄：
  - G1：原始 Red／Green；
  - G2：依 r1 的規則，由獨立 GPT review；
  - G3：D11 核准的集合加上 `policy_change` 綁定，`tested-sha==H`。

  缺任何一項就是 unknown。這份紀錄不是自我託管。
- [ ] **8.0** skill 或人依 D27 核對 B1 的 PR：已人工 accepted、以 GitHub 讀取確認實際 merged 並記下 merge commit、以 `register binding --role baseline` 登記 baseline。不自動 merge；任何一項不成立就不開始 T8。
- [ ] **8.1** R3，使用 D11 選定的 feature。它必須是 B1 尚未實作的有界新行為，才可能有誠實的實作 Red（D51-R04）；本計畫不代為選擇。完成條件：真實 finding → fix → re-review、三 gates 在目前版本都通過、中斷後成功接續。Blocked 或沒有 finding → 維持 open。

## 延後（只列 outline，不算完成）

- **S2**：
  - adopt（O08、O09）；
  - Project Lead 委派（O18）；
  - Retro op（O14）；
  - 跨 feature 依賴自動化；
  - 平行 worktree 與整合規則；
  - G15 整合 SHA 映射；
  - OpenCode-only 部署（D20、D23 的變體）；
  - 同一個 OpenCode 承載兩個角色（D24）。
- **S3**：
  - cross-node-file-transfer 示範；
  - 多人交接；
  - Q-STACK。
