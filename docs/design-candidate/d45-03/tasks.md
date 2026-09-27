# Tasks：第一個可用切片（D50 候選 design-03；revision-07）

> **狀態**：候選，未 D11，不授權實作。
> **方法**：沿用 writing-plans 6.4.1 的適配版，只寫 scope、擁有的路徑與公開契約、相依、行為測試、證據與完成條件，不放實作碼或測試碼。
> **派工**：D11 後，bootstrap 期間依 D39 由協作者派給 Opus 5.5，GPT 做獨立 review。
> **PR 界線**：
> - task 不等於 PR；
> - T0–T7 是 controller 開發，整體放在 bootstrap PR，gate 紀錄見 B1；
> - **第一個有用的 feature 是 T8**，要等 B1 通過 D27 門檻後才開始（見 8.0）。

## 通用規則

- **Red**：必須是行為失敗；ImportError 不算。
- **困難狀態**：先寫 fake 測試（PATH 上的假 `herdr`／`gh`＋真 git），才接真實副作用。
- **真實 writer**：只能在 fake 情境都通過的 worker 狀態讀取（6.1）與停止／預算（7.1）之後啟動（D50-R01）。
- **證據位置**：`.delivery/bootstrap/thin-s1/evidence/<task>/`，索引在 `docs/validation/s1/index.md`。
- **隔離**（D46）：
  - 不 import 舊碼、不用舊的 PYTHONPATH，也不建立 `legacy/`；
  - `import delivery` 必須失敗。

## 0. W1 工作區（協作者，需 D11；本文只描述步驟，不執行）

- [ ] **0.1** 依序執行：
  1. 在 `loop-engineering` commit 採用後的文件，記為 **B**。
  2. **保存既有目錄**：把 `/Users/johnson.chiang/workspace/loop-engineering-thin` 的 `README.md` 與 `docs/`（含 `docs/design-candidate/`）移到 `/Users/johnson.chiang/workspace/loop-engineering-thin.pre-w1/`，並記錄移動前後的檔案清單與 sha256。worktree 目的地必須為空。
  3. 執行 `git -C /Users/johnson.chiang/workspace/loop-engineering worktree add -b delivery/thin-controller /Users/johnson.chiang/workspace/loop-engineering-thin B`。
  4. 把保存的 candidate 文件放回 `loop-engineering-thin/docs/design-candidate/`；以 sha256 比對，確認內容相同。
  5. 第一個 commit 移除舊 `src/delivery`、`tests`，並新增 `docs/implementation/removed-s1.md`，指向 `4ce1110`、`5d334d5`、PR #2。
  - 完成條件：`git ls-files src tests` 為空；`.pre-w1` 的 sha256 清單與放回後的內容一致。

## 執行表（owned paths／介面／相依／驗證命令）

| Task | Owned paths | 公開介面 | 相依 | 驗證命令 |
| --- | --- | --- | --- | --- |
| 1.1 | `pyproject.toml`、`src/loopctl/{__init__,cli}.py`、`src/loopctl/tools/{__init__,herdr}.py`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`tests/test_cli.py`、`tests/test_preflight.py` | `loopctl status`、`loopctl preflight --role R --out P`；CI workflow（validation §4） | 0.1 | `uv run pytest tests/test_cli.py tests/test_preflight.py -q && uv run ruff check . && uv run mypy src && scripts/dist-smoke.sh` |
| 1.2 | `docs/validation/s1/preflight/` | 同上（真實） | 1.1 | `loopctl preflight --role implementer --out docs/validation/s1/preflight/implementer.json`（reviewer 同樣執行一次） |
| 2.1 | `src/loopctl/store.py`、`src/loopctl/state.py`、`tests/test_state.py` | `init`、`claim`、`status`、`next` | 1.1 | `uv run pytest tests/test_state.py -q` |
| 2.2 | `src/loopctl/decisions.py`、`tests/test_decisions.py` | `register`、`decide` | 2.1 | `uv run pytest tests/test_decisions.py -q` |
| 2.3 | `src/loopctl/writes.py`、`src/loopctl/assignments.py`、`src/loopctl/tools/herdr.py`、`tests/fakes/bin/herdr`、`tests/test_writes.py` | `write <op>`、`result import`、`safety` | 2.2 | `uv run pytest tests/test_writes.py -q` |
| 3.1 | `src/loopctl/evidence.py`、`src/loopctl/gates.py`（G1）、`src/loopctl/tools/evidence.py`、`tests/test_g1.py` | `evidence red\|green`、`assess` | 2.3 | `uv run pytest tests/test_g1.py -q` |
| 6.1 | `src/loopctl/observe.py`、`src/loopctl/gates.py`（G3）、`src/loopctl/tools/gh.py`、`tests/fakes/bin/gh`、`tests/test_observe.py` | `observe worker\|ci\|pr` | 2.1 | `uv run pytest tests/test_observe.py -q` |
| 7.1 | `src/loopctl/budget.py`、`tests/test_budget.py` | `next`、`safety`（到期 stop） | 2.3、6.1 | `uv run pytest tests/test_budget.py -q` |
| 4.1 | `skills/orchestrate/SKILL.md` | 只依 `next`／`safety` 行動 | 2.3 | DOC 審查清單 `docs/validation/s1/doc/orchestrate.md` |
| 4.2 | `docs/validation/s1/probe/` | 真實 probe | 1.2、3.1、4.1、6.1、7.1 | 依 validation R2 執行 |
| 5.1 | `src/loopctl/findings.py`、`src/loopctl/gates.py`（G2）、`tests/test_review.py` | `write agent_start`（reviewer）、`result import` | 3.1、4.1 | `uv run pytest tests/test_review.py -q` |
| 6.2 | `src/loopctl/publish.py`、`tests/test_publish_pass.py` | `write publish_*`、`assess`（Pass） | 5.1、6.1 | `uv run pytest tests/test_publish_pass.py -q` |
| B1 | `docs/validation/s1/bootstrap-gates.md` | — | 1–7 | 獨立 Reviewer 審查該紀錄 |
| 8.0–8.1 | `docs/validation/s1/delivery/` | 真實 loop | B1 accepted＋merged＋baseline 已採用 | 依 validation R3 執行 |

執行順序：0.1 → 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 6.1 → 7.1 → 4.1 → 4.2 → 5.1 → 6.2 → B1 → 8.0 → 8.1。

## 行為測試與完成條件

- [ ] **1.1 骨架、preflight、CI**
  - 未知 feature → exit 5；profile 缺少必要項目 → `unverified`。
  - 安裝後的 wheel 在 source checkout 外可執行，且 `import loopctl.tools` 成功。
  - 建立 CI workflow。它的 check 集合只是候選，需經 D11 核准。
- [ ] **1.2 真實 preflight（受限的能力 probe）**
  - 項目：載入 skills、native model／marker 讀回、權限負例、stop 並以 process-info 確認。
  - 兩個 role 都 verified 才能繼續。unverified → Blocked，不做任何真實派工。
- [ ] **2.1 狀態**
  - history-first，中斷後不生效；手改 → exit 5；transition 衝突 → Blocked。
  - 同時 commit 或同時 claim，恰一成功；token 明文不落地。
- [ ] **2.2 決策**
  - plan 保存 provenance；`approve_plan` 綁定 digest；草案 plan、agent 身分或沉默都不算批准；`scope_change` 讓批准失效。
  - adopt、delegate 回 `unsupported`，不繞過任何核對。
- [ ] **2.3 寫入與派工**
  - 同一 op 的外部呼叫只有 1 次；receipt 遺失時靠讀回收斂。
  - 延後生效或查無 → unknown＋Blocked、0 次重送；讀回 3 次上限，包括「仍在執行」。
  - 前一個 writer 未確認結束時，不派下一個。
  - 身份、scope、argv 不符 → 拒收並保存原件；重複結果或衝突結果依規則處理。
- [ ] **3.1 G1**（D50-R06）
  - 只執行 `command_id`，任意 argv 不被執行；每一種 Red 污染都各自無效。
  - **正常路徑**：原始 Red 有效、head Green 通過、不做 replay → G1 通過。
  - **矛盾路徑**：證據互相矛盾 → 觸發 replay 作診斷；replay 失敗 → Blocked。replay 本身不能補造原始 Red。
  - 缺原始 Red → fail；task 集合為空 → fail。
  - 可修的整合失敗 → `pre_review_g1`（計一輪）；N/A 需經獨立 eligibility。
- [ ] **6.1 觀察與 G3**（D50-R02）
  - 每次 fetch **之前**先配置並持久化 `seq`；匯入依 `seq` 排序，不依完成時間。
  - 分開保存「請求時的版本」與「觀察到的 head／base」。
  - 案例：
    - 亂序完成：A（`seq=1`，H1）比 B（`seq=2`，H2）晚完成 → A 只存歷史，不能恢復 H1；
    - 新 head：B 即使是以 H1 發出的請求，觀察到 H2 仍然有效，並讓 H1 的 gates 與 Pass 失效；
    - 跨 purpose 亂序：`pass` 的觀察（`seq=10`，H1）比 `pr` 的觀察（`seq=11`，H2）晚完成 → head 仍是 H2，`version_seq` 仍為 11；這筆 pass 結果只存歷史，不能讓 Pass 成立。
  - pending 可以再觀察；fetch 最多 3 次。
  - `tested-sha==H` 且 `head_sha==H` 才計入；403 且沒有政策 → Blocked，不耗修正輪；例外只接受有 decision 的 skipped／neutral。
  - worker 狀態讀取是 7.1 與 4.2 的前置。
- [ ] **7.1 預算與停止（D47）**
  - 重疊時間只算一次；到期的 stop 優先於無關的 blocker 與讀回；已 prepared 的 stop 執行同一 op。
  - stop 讀回上限用盡 → 等人。
  - 離線超時會計入並 Blocked；worker 狀態 unknown → 不算已停止。
- [ ] **4.1 orchestrate v0**
  - 遇 Blocked 時列出選項，交人決定；不直接改狀態。
- [ ] **4.2 隔離的真實能力 probe（D50-R01、R04）**
  - 在 thin repo 的 `probe/s1-g1` branch 上用固定的小 fixture task，跑 批准 → 真實 Implementer → 原始 Red → head Green → G1。
  - 這**不是** T8 的交付 feature，也不 merge。
  - 期間 deadline、stop、worker 讀取都由 6.1／7.1 負責。
  - 完成條件：G1 依證據判定，或附證據 Blocked。結果只算能力證據。
- [ ] **5.1 Review 與 G2**（D50-R03）
  - Reviewer 的 assignment 要綁定：完整 PR diff（base…head）、適用的 spec／design／AC 與 digests、先前的 findings。
  - G2 只有在以下全部成立時才 passed：授權且獨立的 Reviewer、完整範圍、目前版本、verdict 為 `clean`、沒有未解的 blocking。
  - 其他結果：
    - `changes_required` → failed；
    - `blocked` → unknown，不開修正輪；
    - 缺 verdict、格式錯誤、只審部分 diff → 不能 passed。
  - Finding 與修正：`matches` 沿用 ID；已 resolved 的再出現 → reopen；GitHub thread resolved 不算 closure；batch 收齊後才開，文件缺陷可修；派修附完整快照；上限 3 輪、一次反證、反覆 → Blocked。
- [ ] **6.2 發布與 Pass**
  - 先發 PR review，再發 issue 摘要，之後才做新的 Pass 觀察；發布 unknown → 不重貼；有新 push → 放棄或讓 Pass 失效；acceptance 綁定版本。
- [ ] **B1 Bootstrap gates**
  - 協作者依 D39 組出紀錄：
    - G1：原始 Red／Green；
    - G2：依 5.1 的規則，由獨立 GPT review；
    - G3：D11 核准的集合加 `policy_change` 綁定，且 `tested-sha==H`。
  - 缺任何一項就是 unknown。這份紀錄不是自我託管。
- [ ] **8.0 D27 交接（skill／人，D50-R04）**
  - 確認 B1 的 PR 已經人工 accepted。
  - 以 GitHub 讀取確認已實際 merge，並記下 merge commit。
  - 以 `register binding --role baseline` 登記採用的 baseline。
  - 不自動 merge；任何一項不成立就不開始 T8。
- [ ] **8.1 第一個有用的交付（D50-R05）**
  - 在 bounded feature 上跑：issue → TDD → PR → review＋CI → 真實 finding → fix → re-review → PR Pass；途中至少中斷並接續一次。
  - **示範完成**需要全部成立：真實的 finding → fix → re-review、三 gates 在目前版本都通過、中斷後成功接續。
  - 附證據的 Blocked 是正確的安全停止，但**不算示範完成**，缺的部分維持 open。
  - 沒有真實 finding → 該覆蓋維持 open，不人為製造 blocker。

## 後續切片（只列 outline）

- **S2**：adopt、跨 feature 依賴自動化、Retro op、平行 worktree 與整合規則、OpenCode-only transport。
- **S3**：cross-node-file-transfer 示範、多人交接、Q-STACK。
