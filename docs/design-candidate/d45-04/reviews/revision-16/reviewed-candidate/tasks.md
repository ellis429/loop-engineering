# Tasks：第一個可用切片（候選 design-04；revision-16）

> **作者提交狀態**：revision-16；候選，未 D11，不授權實作。目前的 review 狀態以 [README](README.md) 為準。revision-15 的變更標 `[R15]`，回應 revision-15 覆核的變更標 `[R16]`。
> **方法**：沿用 writing-plans 6.4.1 的適配版，只寫 scope、owned paths、介面、相依、驗證命令與完成條件，不放實作碼。行為案例以 validation.md 的矩陣列（例如 s1、h8）為準。
> **派工**：D11 後由協作者依下方「派工與模型」（D52）派工；它是 bootstrap 的開發分工，不是產品 profile（design §6）。
> **PR 界線**：
> - task 不等於 PR；
> - T1–T7 放在 bootstrap PR，gate 紀錄見 B1；
> - 第一個有用的 feature 是 T8，要在 T8.0 的 D27 交接之後才開始。

## 通用規則

- **Red**：必須是行為失敗；ImportError 不算。改變行為的修正 attempt 也要有綁定 finding 與 batch 的原始 Red（design §7）。
- **困難狀態**：先寫 fake 測試（PATH 上的假 `herdr`／`gh`＋真 git），才接真實副作用。
- **真實 writer**：只能在 M-OBS o1（讀取預算）、w5（worker 讀取與 writer 結束）與 M-BUD 都通過之後啟動。
- **必要測試政策**：依 validation §0，本機與每個 CI job 用同一套 test-only 設定（T1.1）。
  - 本機套件 session 通過是 G1 的條件，不需要遠端 CI。
  - 遠端必要的 CI job 是否齊全且成功，在 push／PR 之後由 G3 判定。
- **時間相依的案例** [R15]：以 in-process 呼叫 `loopctl.cli.main(argv)`，用 pytest `monkeypatch` 替換 `loopctl` 內唯一的時鐘函式；不新增只給測試用的產品旗標或環境變數。
- **Branch 歷史**：active run 期間只做一般 fast-forward push；整合 base 用 Implementer 在本機 worktree 產生的 merge commit，不是 GitHub PR merge，也不需要 merge 權限；不 rebase、不 squash、不 force-push（design §4、§8）。
- **交接位置** [R15]：每個 task 的 assignment 與 result 在 `.delivery/bootstrap/thin-s1/tasks/<task>/`（`assignment.json`、`result.json`），原始證據在同目錄的 `evidence/`（不進 Git）；程式與 tracked 文件在 `delivery/thin-controller` branch 的 commits。`docs/validation/s1/index.md` 由 B1 彙整。
- **舊碼提取** [R15]：從 `4ce1110` 提取行為的 task，在 `docs/implementation/extraction-log.md` 追加自己的一節（來源 commit 與路徑、適用的舊 findings、改動理由、新的矩陣列 ID）；只追加，不改其他 task 的內容（cleanup-map §1）。
- **隔離**（D46）：
  - 不 import 舊碼、不用舊的 PYTHONPATH，也不建立 `legacy/`；
  - `import delivery` 必須失敗；
  - 新 branch 的 lineage 不含 `4ce1110`（T0.1）。

## 派工與模型（D52）[R15]

**這是 bootstrap 開發的分工**：協作者派 agents 撰寫與審查 T0–T7，那些 sessions 不受 loopctl 管理。T8 與 R1–R3 由 loopctl 依產品 profile（design §6）派工。

| 角色 | 預設 model／effort | 用在 | 可替代 |
| --- | --- | --- | --- |
| 協作者（唯一協調者） | Claude Opus 5.5 xhigh | 派工、T0.1 組合、1.2／4.2 的真實 probe 操作、B1 彙整 | — |
| Implementer | Claude Opus 5.5 **high** | 1.1、2.1、2.2、7.1、4.1、4.3（樣本）、6.2 | GPT-6 Sol high，派工前記入 assignment |
| Implementer（困難狀態／證據） | Claude Opus 5.5 **xhigh** | 2.3、3.1、6.1、5.1 | 不替代；需換時先回報使用者 |
| Reviewer | GPT-6 Astra **xhigh** | B1 的 G2、T0.1 對照表核對、4.3 rubric 審查、爭議覆核 | 不自動替代；Astra 不可用 → 停下，附可行替代交使用者決定 |

- **獨立性**：Reviewer 的實際模型必須不同於被審範圍內**每一個** Implementer 的實際模型，並使用新的獨立 session 與獨立 clone；只換 effort、別名或 session 不算不同模型。同一 PR 混用 Opus 與 Sol 實作時，由未參與實作的 Astra 審查。Reviewer 不改作者 branch，也不自行修完再批准；已修正 finding 的覆核仍由合格的獨立 Reviewer 完成。
- **Runtime**：Claude 模型經 Claude Code（在 Herdr 管理的 pane 中，或 `claude -p` headless）；OpenAI 模型經 Herdr＋OpenCode，或 `codex exec`。2026-09-28 已以 native `turn_context` 核對 `codex exec` 的 `gpt-6-sol`／`gpt-6-astra`；OpenCode 的 OpenAI 推論尚未驗證，驗證前不用於 bootstrap review。不把 Claude 訂閱接到 OpenCode（D44）。
- **核對**：每個 attempt 保存 runtime、session ID、要求的與 native 讀回的 model（Claude Code transcript 的 assistant `model`、Codex `turn_context.model`／`effort`、OpenCode message 的 `modelID`）。讀不到 native model → 該 attempt 不算已派給指定 model，交使用者。不讀取私密 chain-of-thought。
- **界線**：每個 task attempt 沿用 D13 的數字：主動時間最多 4h、同一 PR 修正最多 3 輪、每項 infra 操作額外重試 2 次；到限保存現況並回報使用者，不換 session 重新計數。

## 0. W1 工作區（協作者，需 D11；本文只描述步驟，不執行）[R15 修訂]

**為什麼不以 `4ce1110` 為基底**：`4ce1110` 是 PR #2（open，head `delivery/s1-controller-core`）的 head。新 branch 若包含它，bootstrap PR 合併後，GitHub 會把 PR #2 顯示為 merged，而它的 17 項 blocking findings 仍 open。`origin/main`（`359ffcf`）不含 `src/`、`tests/`，所以從 main 出發就自然與舊碼隔離；舊碼只以 `git show 4ce1110:<path>` 讀取。

- [ ] **0.1** 依序執行（全部在 D11 之後）：
  1. **現況紀錄**：在 `loop-engineering` 記下 HEAD、branch、`git status --porcelain` 與每個已修改或未追蹤的文件（`docs/`、`openspec/`、`README.md`、`CONTEXT.md`）的 sha256，寫入 `.delivery/w1/pre-state.json`。原工作區之後不修改。
  2. **文件分支 A0**：`git -C /Users/johnson.chiang/workspace/loop-engineering worktree add -b docs/d11-adoption /Users/johnson.chiang/workspace/loop-engineering-adopt origin/main`。把原工作區上述路徑的現況原樣複製過去（包含刪除），另把 `/Users/johnson.chiang/workspace/loop-engineering-thin/docs/design-candidate/` 複製到 `docs/design-candidate/`；不複製 `src/`、`tests/`、`pyproject.toml`、`uv.lock`、`.delivery/`。逐檔 sha256 與來源相同後 commit，記為 **A0**（`docs: carry D41–D52 document state (no code)`）。
  3. **正式 OpenSpec 採用完整基準**：D11 核准時必須同時點名兩層來源與各自的 sha256：D45-02 baseline spec-delta，以及本版 spec-delta（它的「沒列出者沿用基準」依賴 D45-02）。在 A0 的 `openspec/changes/implement-delivery-loop/specs/` 四份正式 spec 上，依 spec-delta §12 的組合規則套用：
     - D45-02 baseline 的全部條目（含 §0.1 的 banner 替換），被本版覆寫的條目除外；
     - 本版 spec-delta 的全部覆寫（依各節的「取代範圍」與「全文」標示）；
     - banner 改為記錄 D11 採用來源，移除「scope revision pending」與「D40 已核准」的現行效力敘述。

     結果是四份自足、完整的正式 spec，不再需要另讀任何未採用的 delta。
     - 對照表寫在 `openspec/changes/implement-delivery-loop/adoption/source-map.md`：正式 spec 的每個 requirement／AC ID → 來源（原文不變、D45-02 條目，或本版覆寫），並記下兩份來源與同步前後各檔的 sha256；
     - 同步只照抄已審的語意。由獨立 Reviewer（GPT-6 Astra xhigh）依對照表核對組合結果，結果寫在同目錄的 `review.json` 與 `review.md`；有任何與已審版本不同的語意、衝突或遺漏 → 停下回使用者（D11），不自行批准。
  4. **舊計畫退為歷史**：正式 change 內仍描述 D40 舊計畫的 design／tasks，以及正式 spec Purpose 所引用的 `docs/validation/implement-delivery-loop.md`（若存在），都要改為採用後的 design／tasks／validation，或只留一段指向它們的說明。舊內容保留在 Git 歷史，或移到明示「superseded、只作歷史」的位置。`approval.json` 維持原樣，作為歷史。
     - 完成後，除了採用的版本之外，沒有任何檔案自稱是現行的 design、tasks 或 validation。
  5. 第 3、4 步的結果（含對照表與覆核結果）commit 在 `docs/d11-adoption`，記為 **B**。
  6. **採用進入 main**（依 D11 選項）：
     - **W1-A（建議）**：push `docs/d11-adoption`，開 docs PR 到 `main`，由人檢閱與 merge（不自動 merge）。merge 後以 main 上包含 B 內容的 commit 作為 **B′**。bootstrap PR 的 diff 因此只有 T1–T7 的程式與 tracked 驗收文件。
     - **W1-B**：不開 docs PR；下一步直接從 B 建立 worktree，bootstrap PR 會同時包含 A0、B 的文件差異，由 B1 的 G2 一併審查。
     - 之後 assignment 綁定的 spec digest 取自 B′（W1-A）或 B（W1-B）。
  7. **保存既有目錄**：把 `/Users/johnson.chiang/workspace/loop-engineering-thin/{README.md,docs/}` 移到 `…/loop-engineering-thin.pre-w1/`，並記錄移動前後的檔案清單與 sha256。worktree 目的地必須為空。
  8. 執行 `git -C /Users/johnson.chiang/workspace/loop-engineering worktree add -b delivery/thin-controller /Users/johnson.chiang/workspace/loop-engineering-thin <B′ 或 B>`。
  9. 確認 worktree 中的 `docs/design-candidate/` 與 `.pre-w1` 的 sha256 一致。第一個 commit 新增 `docs/implementation/removed-s1.md`，指向 `4ce1110`、`5d334d5`、PR #2，說明舊碼不在本 lineage。
  - 完成條件：
    - `source-map.md` 涵蓋四份正式 spec 的全部 88 個 AC 與每個 requirement，兩份來源的 sha256 等於 D11 核准的版本，並有獨立 Reviewer 的 `review.json`；
    - 正式 change 內沒有與採用版本競爭的現行 design／tasks／validation；
    - `git merge-base --is-ancestor 4ce1110 HEAD` 為 false；`git ls-files src tests` 為空；放回的文件與 `.pre-w1` 的 sha256 一致；原工作區的 `pre-state.json` 與完成後重算的結果相同。

## 執行表

| Task | Owned paths | 公開介面 | 相依 | 驗證命令（矩陣列） |
| --- | --- | --- | --- | --- |
| 1.1 | `pyproject.toml`（含 pytest 設定）、`uv.lock`（新產生並提交 [R16]）、`workflow.yaml`（loopctl 政策檔，含 `profiles`、`timeouts`、`limits`）、`profiles/implementer.claude-settings.json`、`profiles/reviewer.opencode.json`、`src/loopctl/{__init__,cli,clock,preflight}.py`、`src/loopctl/tools/{__init__,herdr}.py`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`tests/conftest.py`、`tests/fakes/bin/herdr`、`tests/fakes/scenarios/herdr/`、`tests/test_test_policy.py`、`tests/test_ci_workflow.py`、`tests/test_cli.py`、`tests/test_preflight.py` | `status`（空狀態）、`preflight --role R --out P`；CI workflow；測試政策 | 0.1 | `uv run pytest tests/test_test_policy.py tests/test_ci_workflow.py tests/test_cli.py tests/test_preflight.py && scripts/dist-smoke.sh`（t1–t7、f1–f6） |
| 1.2 | `docs/validation/s1/preflight/` | preflight（真實） | 1.1 | `loopctl preflight --role implementer --out docs/validation/s1/preflight/implementer.json`，reviewer 同樣執行一次（R1） |
| 2.1 | `src/loopctl/{store,state,next}.py`、`tests/test_state.py` | `init`、`claim`、`status [--human]`、`next`；store 內部契約（design §3） | 1.1 | `uv run pytest tests/test_state.py`（s1–s7） |
| 2.2 | `src/loopctl/decisions.py`、`tests/test_decisions.py` | `register`、`decide`（含 `resolve_read`、`resolve_operation`、`budget_extension` 的紀錄） | 2.1 | `uv run pytest tests/test_decisions.py`（d1、d2、d4–d6、d7a、d8–d10） |
| 2.3 | `src/loopctl/{writes,assignments,observe}.py`（observe 由此建立：seq、版本水位、讀取預算、`worker`／`native`）、`src/loopctl/tools/herdr.py`（延伸）、`tests/fakes/bin/herdr`（延伸）、`tests/fakes/scenarios/herdr/`、`tests/test_observe.py`、`tests/test_writes.py`、`tests/test_public_path.py` | `write <op>`、`result import`、`safety`、`observe worker\|native`；op 紀錄與 assignment 契約（design §4）；`resolve_read`／`resolve_operation` 的效果 | 2.2 | `uv run pytest tests/test_observe.py tests/test_writes.py tests/test_public_path.py`（o1–o3、w1–w11、d3） |
| 3.1 | `src/loopctl/{evidence,gates}.py`（G1，含整合 attempt 的 parents、匯入與作者編輯分類、scope 核對、乾淨 checkout 的 Green、證據命令的執行界線與 `activities` 紀錄 [R16]）、`src/loopctl/tools/evidence.py`（git 呼叫，含 `merge-tree --write-tree`、`worktree add --detach`）、`tests/test_g1.py` | `evidence red\|green`、`assess`（G1） | 2.3 | `uv run pytest tests/test_g1.py`（g1–g15、g3b） |
| 6.1 | `src/loopctl/observe.py`（延伸 `pr`／`ci`）、`src/loopctl/writes.py`（新增 `push`、`pr_ensure` 兩種 op）、`src/loopctl/gates.py`（G3）、`src/loopctl/tools/gh.py`、`tests/fakes/bin/gh`、`tests/fakes/scenarios/gh/`、`tests/test_github.py` | `observe pr\|ci`、`write push\|pr_ensure` | 2.3、3.1 | `uv run pytest tests/test_github.py`（h1–h13，含 h4a–h4e） |
| 7.1 | `src/loopctl/budget.py`、`src/loopctl/next.py`（延伸：到期 stop 與 timeout 路徑優先）、`tests/test_budget.py` | `next`、`safety`（到期 stop、角色 timeout、`active`／`attempts`／`ci_wait` 延長的效果） | 2.3、3.1、6.1 | `uv run pytest tests/test_budget.py`（b1–b6） |
| 4.1 | `skills/orchestrate/SKILL.md`、`docs/validation/s1/doc/orchestrate.md` | 只依 `next`／`safety` 的動作詞彙行動（design §2） | 2.3、7.1 | DOC 清單 `docs/validation/s1/doc/orchestrate.md` |
| 4.3 | `docs/validation/s1/workflow-samples/`、`docs/validation/s1/proof.md` | workflow 樣本＋rubric | 4.1 | 經授權的獨立 Reviewer 依 validation §3、§4 審查，並把結果記在 `proof.md`（W-A–W-F） |
| 4.2 | `docs/validation/s1/probe/`（含 `fixture/` 與預期軌跡） | 真實 probe | 1.2、3.1、4.1、6.1、7.1 | R2 |
| 5.1 | `src/loopctl/findings.py`（含整合 finding 的 ID 與去重、路徑選擇、`pre_review_g1` 與 `base_integration` batch、`rounds` 延長的效果）、`src/loopctl/assignments.py`（延伸：`review`／`correction` body 驗證 [R16]）、`src/loopctl/gates.py`（G2）、`src/loopctl/next.py`（延伸：修正路徑）、`tests/test_review.py` | reviewer 派工、整合 assignment、`result import`（review 與修正） | 3.1、4.1、6.1（需要 PR identity） | `uv run pytest tests/test_review.py`（r1–r14、r12b） |
| 6.2 | `src/loopctl/publish.py`、`src/loopctl/writes.py`（新增 `publish_pr`、`publish_issue`）、`src/loopctl/gates.py`（Pass、Pass package）、`src/loopctl/next.py`（延伸：發布與 Pass）、`tests/test_publish_pass.py`、`tests/test_resume.py` | `write publish_*`、`observe pr\|ci --purpose pass`、`assess`（Pass） | 2.2、5.1、6.1 | `uv run pytest tests/test_publish_pass.py tests/test_resume.py`（p1–p7、d7b、u1–u2） |
| B1 | `docs/validation/s1/bootstrap-gates.md`、`docs/validation/s1/index.md` | — | 1–7 | 獨立 Reviewer 審查該紀錄 |
| 8.0–8.1 | `docs/validation/s1/delivery/` | 真實 loop | B1 accepted＋merged＋baseline 已登記；T8 的 D11 packet 已核准 | R3 |

執行順序：0.1 → 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 6.1 → 7.1 → 4.1 → 4.3 → 4.2 → 5.1 → 6.2 → B1 → 8.0 → 8.1。

- 1.2（R1）不通過時，只阻擋 4.2、R3 與任何由 loopctl 管理的真實派工；以 fake 驗證的 2.1–7.1 開發可以繼續。
- pytest 參數（`--strict-markers` 等）由 `pyproject.toml` 提供，所以各命令不另加旗標。

### 共用檔案（依序擁有，不並行修改）

| 檔案 | 順序 | 規則 |
| --- | --- | --- |
| `src/loopctl/cli.py` [R15] | T1.1 建立 → 每個 task 只新增自己公開介面欄列出的子命令 | 不改既有子命令的參數與輸出；`tests/test_cli.py` 的案例須仍通過 |
| `src/loopctl/tools/herdr.py`、`tests/fakes/bin/herdr` [R15] | T1.1 建立（preflight 用的啟動、讀回、stop、process-info）→ T2.3 延伸 | T2.3 只新增 op 需要的函式；不改 T1.1 函式的語意；f1–f5 須仍通過 |
| `src/loopctl/next.py` [R15] | T2.1 建立（依 phase）→ T7.1（到期 stop 與 timeout 優先）→ T5.1（修正路徑）→ T6.2（發布與 Pass） | 後一個 task 只加自己的判斷，不改前面判斷的優先序；前面各 task 的矩陣列須仍通過 |
| `src/loopctl/writes.py` [R15] | T2.3 建立（op 狀態機與通用規則）→ T6.1（`push`、`pr_ensure`）→ T6.2（`publish_*`） | 後面的 task 只新增 op 種類，不改狀態機、重試與讀回規則；w1–w11 須仍通過 |
| `src/loopctl/observe.py` | T2.3 建立 → T6.1 延伸 | T6.1 只加 `pr`／`ci` 來源；不改 T2.3 的 seq、水位、預算語意；o1–o3 須在 T6.1 後仍通過 |
| `src/loopctl/gates.py` | T3.1（G1）→ T6.1（G3）→ T5.1（G2）→ T6.2（Pass） | 後一個 task 只加自己的 gate；前面各 task 的矩陣列須仍通過 |
| `src/loopctl/decisions.py` | 只由 T2.2 擁有 | `resolve_read`、`resolve_operation`、`budget_extension` 在此只記錄；效果在 `observe.py`、`writes.py`、`budget.py`，後續 task 不改此檔 |
| `workflow.yaml`、`profiles/` | 只由 T1.1 擁有 | 之後的改動需要新的 `policy_change`（design §8） |
| `pyproject.toml`、`uv.lock` [R16] | T1.1 建立並提交兩者 | 之後需要新依賴的 task，在同一個 commit 更新兩者並在 result 記錄；不刪改其他 task 的依賴；全新 clone 的 `uv sync --frozen` 須仍成功 |
| `src/loopctl/assignments.py` [R16] | T2.3 建立（assignment、共同 result envelope、`body_kind` 驗證表）→ T5.1 延伸 | T5.1 只在驗證表加入 `review`、`correction` 的 body 驗證函式；不改 envelope 與身份核對；w6、w7 須仍通過 |
| `docs/implementation/extraction-log.md` [R15] | 提取舊行為的 task 依執行順序追加 | 只追加自己的一節 |

相依方向只從前往後：T2.3 不需要 T6.1 的任何介面；w5、w8 使用 T2.3 自己的 `observe worker|native`；G1（T3.1）只讀 assignment 的 batch／finding 欄位，不建立 batch（design §7）；T6.1 只記錄 CI 等待的開始與 mergeable 狀態，逾時判定在 T7.1（b4）[R16]。沒有循環。

## 派工卡 [R15]

每張卡加上執行表的 owned paths、相依與驗證命令，就是可交給 fresh-context agent 的完整 assignment。所有卡的共同輸入：採用後的正式 specs（B′ 或 B）、本候選的 design、validation、coverage、cleanup-map。

| Task | 範圍 | 不在範圍 | 輸入與相鄰介面 | 輸出與交接 |
| --- | --- | --- | --- | --- |
| 1.1 | 專案骨架、`pyproject.toml` 與新產生的 `uv.lock`、測試政策、政策檔與兩個 profile 權限設定檔、CI workflow 與其結構檢查、preflight 的判定邏輯（含位置核對）與 fake、dist-smoke | 任何 feature 狀態、真實 preflight；沿用舊的 `uv.lock` | design §6、§11；validation §0、§6 的 workflow 與 `workflow.yaml` 全文 | `workflow.yaml` 與 profile 檔的 digest；fake scenario 格式（`tests/fakes/scenarios/<tool>/<name>.json`：依序的呼叫比對、stdout／stderr／exit、效果，呼叫紀錄寫入 `$FAKE_LOG`） |
| 1.2 | 以已核准 profile 執行真實 preflight 兩次 | 修改 profile、改用其他 runtime／model | T1.1 的 `loopctl preflight`、Herdr 0.9.1、Claude Code、OpenCode | `implementer.json`、`reviewer.json` receipt（design §6，含要求與實際的 repo／worktree／branch）；任一 unverified → 回報使用者 |
| 2.1 | 狀態檔、history-first 提交、lock、owner token、`status`／`next` 的 phase 判斷 | 外部呼叫、gates | design §3 的內部契約 | `store`／`state` API 與 `feature.json` 的 `schema_version` |
| 2.2 | decision 紀錄與驗證、plan 登記與批准來源 | decision 的效果（由後續 task 實作） | T2.1 的 `store.commit` | decision 紀錄格式；d7a 只驗紀錄層 |
| 2.3 | op 狀態機、Herdr ops、assignment、共同 result envelope 與匯入、observe 通用機制與 `worker`／`native`、worker／review attempt 的 `activities` 紀錄 | GitHub ops、gates、review／correction body 的內容驗證（T5.1） | T2.1、T2.2；T1.1 的 `tools/herdr.py` | op 紀錄、assignment 與 envelope 契約（design §4、§8）；`safety` 的讀回動作 |
| 3.1 | G1：Red 資格、Green 在乾淨 checkout、證據命令的執行界線與 `activities` 紀錄、N/A、整合 attempt 核對 | 建立 batch 或 finding（T5.1）；active 聯集計算（T7.1） | T2.3 的 assignment 欄位與 evidence 匯入 | `gates.g1` 與逐單位原因（design §7） |
| 6.1 | PR／CI 觀察、`push`／`pr_ensure`、G3、整合觸發的偵測、CI 等待開始的 `activities` 紀錄 | 整合 finding 的建立與去重（T5.1）；CI 等待與 mergeable 的逾時判定（T7.1） | T2.3 的 writes／observe；T3.1 的 `gates.g1`（push 前必須 passed） | PR identity、`gates.g3`、`integration_required` 與其觸發鍵 |
| 7.1 | active 區間聯集、到期 stop、角色 timeout（含 CI 等待與 mergeable 未算出）、`active`／`attempts`／`ci_wait` 延長的效果 | 修改 timeout 值（屬政策檔）；`rounds` 延長（T5.1） | T2.3 的 stop op、讀回與 `activities`；T3.1 的證據命令 `activities`；T6.1 的 CI 等待開始 | `next`／`safety` 的預算與 timeout 動作 |
| 4.1 | orchestrate skill：只依動作詞彙呼叫 loopctl，遇 `human` 停下 | 自行判斷 gate、另起外層 loop | design §2 的動作詞彙；T2.3、T7.1 | skill 與 DOC 清單 |
| 4.3 | W-A–W-F 樣本與 rubric 審查紀錄 | 產品程式 | validation §3、§4 | `proof.md`；Reviewer 見「派工與模型」 |
| 4.2 | 在 `probe/s1-g1` 上以 fixture 跑到 G1 | 交付 feature、merge | T1.2 的 receipt；fixture 與預期軌跡寫在 `probe/fixture/`（一個 task：新增一個小函式與其測試；預期 G1 passed） | probe 軌跡、狀態 export、G1 結果 |
| 5.1 | G2、findings、batch、爭議、整合路徑與整合 assignment、review 的 `dispositions` 與修正的 `responses`、`rounds` 延長的效果 | 發布、Pass | T3.1 的 G1 原因；T6.1 的 PR identity 與 `integration_required`；T2.3 的 envelope 與驗證表 | `gates.g2`、finding registry、batch |
| 6.2 | 發布、Pass 前確認觀察、Pass package、resume、人工退回的效果 | merge／close／release／deploy | T5.1 的 registry；T6.1 的 observe；T2.2 的 `return`／`accept` 紀錄 | Pass package 投影 |
| B1 | 彙整 bootstrap PR 的三 gates 紀錄與 `index.md` | 以 loopctl 審自己的 PR | 各 task 的 result 與 evidence | `bootstrap-gates.md`、`index.md` |
| 8.0–8.1 | 依 D27 核對後跑 R3 | 選擇 feature | **T8 的 D11 packet**：issue、feature spec／AC、plan 版本與 digest（由使用者另行核准；本計畫不代選） | R3 證據 |

## 完成條件

- [ ] **1.1** t1–t7、f1–f6 通過；dist-smoke 通過；`pyproject.toml` 與 `uv.lock` 已提交，全新 clone 執行 `uv sync --frozen` 成功；CI workflow 只以 `pull_request` 觸發，每個 job 上傳唯一名稱的 tested SHA 產物；`workflow.yaml` 與兩個 profile 檔依 validation §6 建立（內容以 D11 核准為準）。
- [ ] **1.2** 兩個 role 都 verified，receipt 含每個負例的拒絕與資源檢查。任一 unverified → 回報使用者，不做任何由 loopctl 管理的真實派工。這一步不涵蓋 D24。
- [ ] **2.1** s1–s7 通過。
- [ ] **2.2** d1、d2、d4–d6、d7a、d8–d10 通過。adopt 與 delegate 只驗證會被拒絕，不算覆蓋。
- [ ] **2.3** o1–o3、w1–w11 與 d3（公開路徑：批准後第一個 assignment 帶 AC 與驗法）通過。
- [ ] **3.1** g1–g15 與 g3b 通過。Red 必須同時符合三項資格：在 scope 內、有捕捉時記錄的對應到 attempt、attempt 是 H 的祖先。只有共同祖先的兄弟 snapshot 無效（D51-R07）。改變行為的修正需要綁定 finding 與 batch 的 Red；被放棄 attempt 的 Red 不轉移；歷史被改寫 → Blocked。g13 依 validation 的步驟，以真 git 分類整合 merge 的匯入與作者編輯：純匯入不要求上游 Red；藏在匯入裡的範圍外作者編輯被拒收。Green 只在 H 的乾淨 checkout 執行（g14）；證據命令到限 → 終止、計入 active、不產生 passed（g15）。
- [ ] **6.1** h1–h13 通過，其中 h4 含 queued 與其他 workflow 的案例（D51-R03），h4a–h4e 含 push 事件與舊 run 重跑，h10 含延遲建立的反例（D51-R01）、G1 未通過時 0 次 push 與身份比對。
  - PR 正向路徑（AC-A04）：G1 passed → `push` → `pr_ensure`（先持久化預期身份與 marker）→ 記錄 PR identity；結果 unknown 時不盲目重試。
  - G15 只驗負例；非 head 的整合 SHA 映射延到 S2。
- [ ] **7.1** b1–b6 通過。
- [ ] **4.1** orchestrate DOC 清單審查通過：動作詞彙的每一項都有對應步驟，未列動作一律停下交人。
- [ ] **4.3** W-A–W-F 每組的正例與負例，都由獨立 Reviewer 依 rubric 審查，結果記錄在 `proof.md`。不需要逐樣本的使用者簽核。
- [ ] **4.2** R2：在 `probe/s1-g1` 上跑 fixture，不是交付 feature，也不 merge。通過標準是 fixture 的 G1 passed 且軌跡與 `probe/fixture/` 的預期一致；附證據的 Blocked 另外記錄，R2 維持 open。結果只算能力證據。
- [ ] **5.1** r1–r14、r12b 通過；finding 只經附證據、綁定目前 H 的 disposition 或人工裁決關閉；review 只在 PR identity 已記錄之後才派出；G2 `blocked` 使 feature Blocked。`integration_required` 依 design §8 的界線處理：在途且有效的 review／CI 照常收齊；其他情況立即走 `pre_review_g1`（原因 `base_integration`），不等待無法開始的 G2 或不會出現的 CI。兩種都是一個 writer、一個 batch、派修時計一輪，只在本機 merge，不呼叫 GitHub PR merge。
- [ ] **6.2** p1–p7、d7b、u1–u2 通過；Pass package 由狀態投影。
- [ ] **B1** 協作者組出三 gates 紀錄：
  - G1：原始 Red／Green；
  - G2：依 r1 的規則，由「派工與模型」中與所有 Implementer 不同實際模型的獨立 Reviewer（預設 GPT-6 Astra xhigh）審查完整 PR；
  - G3：D11 核准的集合加上 `policy_change` 綁定 `workflow.yaml`，逐 job 的 tested SHA 等於 H。

  缺任何一項就是 unknown。這份紀錄不是自我託管。
- [ ] **8.0** skill 或人依 D27 核對 B1 的 PR：已人工 accepted、以 GitHub 讀取確認實際 merged 並記下 merge commit、以 `register binding --role baseline` 登記 baseline。不自動 merge；任何一項不成立就不開始 T8。
- [ ] **8.1** R3，使用 T8 的 D11 packet 選定的 feature。它必須是 B1 尚未實作的有界新行為，才可能有誠實的實作 Red（D51-R04）；本計畫不代為選擇。完成條件：真實 finding → fix（有綁定 finding 與 batch 的原始 Red）→ re-review、三 gates 在目前版本都通過、中斷後成功接續。Blocked 或沒有 finding → 維持 open。

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
