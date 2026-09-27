# Validation 候選：implement-delivery-loop（D45 候選 design-02）

> **狀態：全部都是 planned，沒有任何項目已執行，也沒有 gate 結論。** 每個 AC 與 S1 finding 的處置和驗證層級，以 [coverage.md](coverage.md) 為權威；本文把 H1 做成可執行的情境，並把 H2／H3 的真實要求分開列出。計畫見 [tasks.md](tasks.md)。

## 1. 可宣稱的範圍

- **H1 可以獨立 review**。它驗證核心狀態、規則、執行許可、gates、findings、預算，以及外部工具的 argv 與讀回邏輯。
- H1 的外部程式是 **fake**：PATH 上的假 `herdr`／`gh` 可執行檔，搭配真 git 暫存 repo。所以 H1 通過**不代表** Herdr、OpenCode、Claude Code、GitHub 或 CI 的真實能力，也**不是**完整 end-to-end 交付，不能因此勾選 H2 或 H3 的項目。
- 真實能力與 E2E 在 H2（本 repo）、H3（cross-node-file-transfer）另行收集證據。fake 證據不改標成 real。
- **兩種不同的主張要分開（D45-S09）**：
  - H1 自身 PR 的 bootstrap gates（依 D39 由協調者組出，並經獨立 Reviewer 審查，見 §3a）可以依其實際證據判定；
  - loopctl 的自我託管（H2）仍待證。前者成立不代表後者成立。

## 2. 環境

| 代號 | 環境 | 用途 |
| --- | --- | --- |
| ENV-L | 本機 macOS arm64、Python 3.12（uv）、系統 `/usr/bin/git`；PATH 前置 `tests/fakes/bin` | H1 開發時的 Red／Green |
| ENV-CI | GitHub Actions `ubuntu-24.04` 與 `macos-15`，Python 3.12（uv）；fake bin 同上 | H1 回歸；候選 check 集合（§4） |
| ENV-R | 本機 Herdr 0.9.1＋OpenCode 1.18.32（ChatGPT OAuth）＋Claude Code（Claude 帳號），版本以 H2 preflight 固定 | H2 真實 profile、權限、停止、讀回 |
| ENV-GH | `yschiang/loop-engineering` 的真實 PR／issue／Actions | H2 的 G3、發布、E2E |
| ENV-X | cross-node-file-transfer 獨立 repo | H3 |

## 3. H1 情境（全部為 ENV-L＋ENV-CI，fake 外部程式）

**共通門檻**：
- 命令 exit 0；junit 中列名的測試全部 passed，failure、error 都是 0；
- 除非情境另有標註，不允許 skipped；
- Red 必須是行為失敗（見 tasks 的 Global Constraints）。

**證據位置**：
- 每個 task 的 Red／Green：`.delivery/bootstrap/thin-h1/evidence/<task-id>/{red,green}.{json,stdout,stderr}`；
- CI 的 junit artifact：`h1-junit-<job>.xml`；
- 索引：`docs/validation/h1/index.md`。

| ID | 情境（可觀察結果） | 命令 | 額外門檻 | Coverage IDs |
| --- | --- | --- | --- | --- |
| V-H1-01 | 單一入口、envelope 六欄、exit code，以及 Unicode／空白的 `LOOPCTL_HOME` | `uv run pytest tests/test_cli.py -q` | 未知 feature 回 exit 5 | AC-D01（部分） |
| V-H1-02 | history-first、typed ref、不可信狀態、手改偵測、transition 衝突、併發提交 | `uv run pytest tests/test_store.py -q` | 併發 20 次都恰好一方成功 | AC-D02、D09、D10、D11；S1-R03、R04、R06 |
| V-H1-03 | 協調權、token 不落地、epoch 不重置預算 | `uv run pytest tests/test_claim.py -q` | 併發 claim 恰好 1 個 token | AC-O02、O19、D03、F07；S1-R08 |
| V-H1-04 | prepare 可重送、begin 只消耗一次、讀回不經 begin、嘗試上限、各 kind 的重試安全條件（查無不等於可重試）、讀回上限 | `uv run pytest tests/test_ops.py -q` | 第 4 次 begin 被拒；`agent_start`／`prompt`／`stop`／`worktree_create`（Herdr socket）讀回查無時從不給重試；持有者仍存活時，連續 3 次 `in_progress` 都計入名額，第 4 次自動讀回被拒 | AC-D13、D16；S1-R02；D45-S03、S06 |
| V-H1-05 | 版本矩陣、candidate、base recheck、G3 重新觀察、晚到結果 | `uv run pytest tests/test_versions.py -q` | 矩陣的列等於 VersionSet 全部欄位 | AC-O03、G16、G17、D15 |
| V-H1-06 | plan 來源與批准的本地轉移（approval 綁 digest、保存 provenance、phase 轉換）、scope_change、accept／return、delegate、policy_change。公開路徑到 next action 的斷言在 V-H1-12（D45-S10） | `uv run pytest tests/test_decisions.py -q` | 沉默或 agent 同意都不產生 approval | AC-O05、O06（本地）、O07、O10、O11、O18、O22、F11、F12；S1-R07（本地）、R10 |
| V-H1-07 | 身份不符、去重、衝突、非 UTF-8、完整 finding 快照、native-only 結果、handle 分欄 | `uv run pytest tests/test_results.py -q` | 原件都保存 | AC-D05、D06、D07、D08、D21；S1-R12 |
| V-H1-08 | 只跑 policy 命令、snapshot（真 git）、Red 逐項污染、replay 不能取代原始 Red、worker 的 green 不採用 | `uv run pytest tests/test_evidence_tool.py tests/test_evidence.py -q` | 惡意 argv 的 marker 檔不存在 | AC-G04、G05、G06、G07、G08；S1-R01、R13 |
| V-H1-09 | G1 完整 task 集合、獨立性、G2 unknown／blocked、G3 非成功矩陣、分頁與 app、merge mapping、受測 SHA 對應（H≠M 時只有 `tested-sha==H` 才計入，D45-S08）、policy route、D49 宣告來源、例外限制、Pass 阻擋條件 | `uv run pytest tests/test_gates.py tests/test_pass.py -q` | 每種非成功狀態都有自己的測試；`tested-sha` 為 M 或缺失 → 不計入 | AC-G01、G02、G03、G09、G10、G11、G12、G13、G14、G15、G18；S1-R11、R14、R15、R17 |
| V-H1-10 | 分類、ID、closure 權限、batch、文件缺陷與驗證缺失可修正、輪次上限、一次爭議、反覆、reopen | `uv run pytest tests/test_findings.py -q` | 第 4 輪為 0；reopen 立即 Blocked；`pre_review_g1` 批次計一輪且不需要 G2／G3 | AC-F01–F10、F15、F16；S1-R16；D45-S01、S05 |
| V-H1-11 | 聯集只算一次、離線 gap 與 overrun、時鐘倒退、deadline、延長 | `uv run pytest tests/test_budget.py -q` | overrun 秒數等於計算值 | AC-D16、D17；S1-R09 |
| V-H1-12 | 公開 CLI 路徑 register → approve_plan → 第一個 `worktree_create`（S1-R07、AC-O06，從 V-H1-06 移來，D45-S10）、到期 stop 優先（含 prepare 後中斷的 stop）、stop 讀回用盡後移出 safety_actions、同一版本的觀察週期、正式 review 前 G1 失敗的修正路徑、phase 路由、發布先於 Pass 觀察、adopt、依賴、retro 去重、P03 guard | `uv run pytest tests/test_engine.py -q` | 同一 stop 的 op_id 只 send-keys 1 次；pending→pending→success 產生 3 個週期；G2 在整合 G1 passed 之前是 0 次 | AC-O01、O04、O06、O08、O09、O12、O13、O14、O15、O23、O26、D04、D14、D17、F05、F13、G08、G13；S1-R07；D45-S04、S05、S06、S10 |
| V-H1-13 | 兩個 CLI 程序同時執行同一 op、receipt 遺失後讀回收斂、A 執行中 B 讀回查無仍不能重試、遠端發布在本機程序結束後查無 marker 仍是 unknown（D45-S03 保守化）；Herdr worktree 的 client 結束後查無路徑仍是 unknown，server 晚完成時也不重建（D45-S03）；gh observe 取回 `tested-sha`；讀回上限，包括持有者仍存活時的發布：3 次 `in_progress` 後移出自動讀回（D45-S06）；worktree 讀回、CAS 整合、herdr argv 快照、marker 不重貼、沒有 herdr 時核心仍可用、profile 不符與能力缺口 | `uv run pytest tests/test_tools.py -q` | fake 呼叫計數：副作用恰好 1 次；reconcile 的查詢恰好 3 次 | AC-D12、D13、D18、D19、D20（部分）、D23、F14；S1-R05；D45-S03、S06 |
| V-H1-S | fake 端到端與負例矩陣（tasks 14.1 的全部情境）。**包括**：文件或驗證 finding → fix → 獨立 re-review（D45-S01）；整合回歸 → pre-review 修正 → 第一次正式 G2（D45-S05）；同一版本 CI 多週期觀察（D45-S04） | `uv run pytest tests/test_scenarios.py -q --junitxml=h1-scenarios.xml` | 每項都斷言狀態欄位與外部呼叫次數 | AC-G01、G02、O16、D01、D07、F03、F04、F06；A01–A12（fake 版本） |
| V-CLEAN | 單一入口、沒有舊套件與 legacy、每個模組都有生產呼叫者、manifest 涵蓋重用列、核心不 import subprocess | `uv run pytest tests/test_cleanliness.py -q` | 無 | cleanup-map §6 |
| V-STATIC | lint 與 type | `uv run ruff check . && uv run mypy src` | 0 個 finding | — |
| V-DIST | 發佈物 smoke（D45-S07）：`uv build`，在全新 venv 安裝 wheel（不設 PYTHONPATH），在 source checkout 外執行已安裝的 `loopctl` | `scripts/dist-smoke.sh` | 已安裝的 `loopctl inspect --feature f-missing` 回 exit 5 並輸出合法 JSON；`import loopctl.tools` 成功（task 1.1 起就有 `src/loopctl/tools/__init__.py` 骨架；task 15.2 對完整套件重跑）；任一失敗都擋 H1。證據記錄 wheel sha256 與命令／exit | AC-D01；cleanup-map §6（單一入口） |

**H1 完成條件**：
- 以上各列（包括 V-DIST）在 ENV-L 與 ENV-CI 都達到門檻；
- 每個 task 都有 Red／Green 證據；
- extraction manifest 完整；
- 完成 tasks 15.3 的獨立 review 與修正循環。

即使這些都達成，也**不等於** S1 findings 已關閉，也不等於 loopctl 已能自我託管。H1 自身 PR 的 bootstrap gates 另依 §3a 判定。

## 3a. H1 自身 PR 的 bootstrap gate 紀錄（D39、D45-S09）

依 D39，controller 自身 PR 的三 gates 由協調者組出紀錄 `docs/validation/h1/bootstrap-gates.md`，再交獨立 Reviewer 審查。每個 gate 依實際要求判定，不自動給過。

| Gate | 判定依據 | 不成立時 |
| --- | --- | --- |
| G1 | 每個 task 的原始 Red／Green（`.delivery/bootstrap/thin-h1/evidence/`），加上 head 的 CI Green（`tested-sha==H`） | 缺原始 Red 或 head 的 Green → missing 或 failed |
| G2 | tasks 15.3 的獨立 GPT review：同一 head／base／文件 digest，verdict clean，沒有未解的 blocking | 否則 failed 或 unknown |
| G3 | D11 已核准 §4 的集合，且 H1 期間已記錄 `policy_change` 綁定；head 上每個必要 check 都 success，且 `tested-sha==H`；顯示 `github_rules_verified=false` | 缺核准、缺綁定、或缺有效 check 證據 → unknown |

三 gates 在同一 head 都成立，才列為「bootstrap PR Pass 候選，待人工接受」。這不主張 H2 的 runtime、capability 或 self-hosted E2E；S1 findings 只有 Reviewer 能關閉。

## 4. 新 CI check 集合：D11 候選（**未核准**）

依 D49，本 repo 可以用人工核准、版控的集合作為 G3 政策來源。以下只是提供 D11 決定的候選；它不是已核准集合，舊的 `test` check 也不在其中。

| 項目 | 候選 |
| --- | --- |
| Workflow 檔案與名稱 | `.github/workflows/loopctl-ci.yml`，`name: loopctl-ci`；觸發條件為 `pull_request`（target `main`）與 `push` 到 `delivery/**` |
| App 與 source | `github-actions`；`source: head` |
| Checkout 與受測 SHA（D45-S08） | GitHub 對 `pull_request` 事件預設會 checkout 合併提交 M，因此明確指定要測的 SHA：<br>• PR build：`actions/checkout` 設 `ref: ${{ github.event.pull_request.head.sha }}`；push build：`ref: ${{ github.sha }}`。<br>• checkout 後比對 `git rev-parse HEAD` 與預期 SHA，不符就讓 job fail。<br>• 上傳 `tested-sha` 產物（內容為實際 HEAD 與事件名稱）。<br>• G3 只有在 check-run metadata 的 `head_sha==H`，且 `tested-sha==H` 時，才把該 check 計入 `source: head`。不假設 checkout 設定本身會改變 check-run metadata；H≠M 時不做靜默改標。 |
| 必要 check-runs（job 名稱） | • `unit-linux`（ubuntu-24.04：`uv run pytest -q --junitxml=h1-junit-linux.xml`）<br>• `unit-macos`（macos-15：同樣命令）<br>• `static`（`uv run ruff check . && uv run mypy src && uv run pytest tests/test_cleanliness.py -q && scripts/dist-smoke.sh`；發佈物 smoke 併在這個既有 job，D45-S07） |
| 非成功例外 | 無；skipped、neutral 一律不接受 |
| 在 `workflow.yaml` 的表示 | `ci: {policy_source: declared, repo: yschiang/loop-engineering, required: [{name: unit-linux, app: github-actions, source: head}, {name: unit-macos, app: github-actions, source: head}, {name: static, app: github-actions, source: head}], allow_non_success: []}` |
| 生效條件 | 使用者在 D11 核准此集合，再記錄一筆 `policy_change` decision，綁定該 `workflow.yaml` 版本的 digest。生效後，G3 與 Pass package 固定顯示 `github_rules_verified=false`。 |

在 D11 核准這個集合、且 `policy_change` 綁定之前，這個 workflow 只作為執行紀錄，G3 為 unknown。兩者都完成後，這份核准與綁定可以在 H1 期間用於 §3a 的 bootstrap G3，不必等 H2 自我託管（D45-S09）。

## 5. H2 要求（本 repo，真實；尚未規劃成可派工的 tasks）

| ID | 要求 | 環境 | 通過標準 | 證據位置 | Coverage |
| --- | --- | --- | --- | --- | --- |
| V-H2-01 | 正式 profile 的 preflight：版本、載入核准 skills（不使用 safe-mode／pure）、以 native 讀回 model 與 marker | ENV-R | 兩個 runtime 都讀到 requested 與實際 model 一致，且找到 marker | `docs/validation/h2/preflight/` | AC-D18、D19、D23、D24 |
| V-H2-02 | Implementer 與 Reviewer 的權限負例（寫出範圍、push、gh、herdr、`loopctl decide|record`） | ENV-R | 全部被拒、允許項成功 → capability report 為 verified；任一例外 → unverified | `docs/validation/h2/capability/` | AC-G11、G12、D19、D24；S1-R01、R15（真實部分） |
| V-H2-03 | 推論中停止（Claude Code、OpenCode），以 process-info 確認 | ENV-R | 停止確認，或確認不了時 Blocked；不會重送 | `docs/validation/h2/stop/` | AC-D04、D17；S1-R09 |
| V-H2-04 | gh 真實：分頁、app、attempt、merge mapping；403 的紀錄；marker 查回 | ENV-GH | 各案例與 H1 的預期一致 | `docs/validation/h2/github/` | AC-G13–G15、D12、F13、F14；S1-R14、R17 |
| V-H2-05 | 由 loopctl 自己計算 G3：核准的 CI 集合（§4）加上 `policy_change`，以受測 SHA 對應；G3 顯示 `github_rules_verified=false` | ENV-GH | 最新 head 的三個 check 都 success 且 `tested-sha==H`，loopctl 算出 G3 passed | PR checks、`docs/validation/h2/g3/` | AC-G13；D49 |
| V-H2-06 | orchestrate skill 的 DOC 審查（只有一個外層 loop，不在背景呼叫 user-only skill） | 人＋Reviewer | 清單全部符合 | `docs/validation/h2/doc/` | AC-O16、O17 |
| V-H2-07 | 本 repo 真實 E2E：issue → D11 → TDD → PR → review／CI → 真實 finding → fix → re-review → PR Pass；中斷後 resume；通知遺失 | ENV-R＋ENV-GH | 三 gates 同一 key；沒有真實 finding 就記為未覆蓋 | feature 狀態 export＋PR／issue URL | AC-G19、G20、D14、A13 |

## 6. H3 要求

- V-H3-01：cross-node-file-transfer 的 Project baseline 到多個 features、人工驗收、Retro，保留 worktrees（ENV-X；AC-O20、O21、O24、O28、O12、O13）。
- 公司 OpenCode-only 環境（AC-D20、D22）不在本 change 的切片內，如實列為未覆蓋。

## 7. DOC 審查項目

AC-O15、O17、O20、O21、O24、O25、O27、O28、G19、D22 以 Reviewer 審查清單驗證。證據位置：`docs/validation/<stage>/doc/`。審查清單不取代 TDD 或 CI。
