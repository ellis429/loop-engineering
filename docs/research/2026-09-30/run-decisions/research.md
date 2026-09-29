---
date: 2026-09-30T07:30:23+08:00
researcher: Claude（Opus 5.5），research-codebase 方法
repository: yschiang/loop-engineering
topic: Feature 1「人工決策與下一步」（change id run-decisions）的現況研究
tags: [research, loopctl, run-decisions, feature-1, m1]
git_commit: 37ff4f071cd480df34b098c5465af96eec4dae83
branch: feature/run-decisions（基於 main c91b774）
working_tree: clean（撰寫前）；本報告是唯一新增的檔案
reference_commit: fcefeccf2a5e76d11fc5a740e69a6b7ab53c557a（delivery/thin-controller，唯讀參考）
status: complete
last_updated: 2026-09-30
last_updated_by: Claude（Opus 5.5）
---

# Feature 1「人工決策與下一步」研究

## 研究問題與界線

問題：Feature 1（`run-decisions`）首先驗證的 23 條 AC，每條在 Feature 1 結束時哪些子句能成立、哪些要等後續階段；高層設計與既有參考實作對這個 Feature 描述了哪些行為；有哪些已知缺口與需要 Project Lead 決定的範圍問題。

本文只記錄現況與推導，不寫 spec、design 或 plan，也不核准任何切法。參考實作 `delivery/thin-controller@fcefecc` 依 D75 只是「一種既有行為的描述」，它的測試、逐 task 審查與 preflight 都不算新 Feature 的證據（[roadmap](../../../roadmap.md) L45–50）。

## 摘要

- 23 條 AC 中，recut 認定 9 條在 Feature 1 完成（D01、D02、D03、D09、D10、D11、O03、O05、O07），14 條跨階段（[recut](../controller-recut.md) L63–118）。逐子句看，這 9 條裡有 5 條含「派工」「外部操作」「預算」子句（D03、D09、D11、O05、O07），Feature 1 沒有派工與外部寫入，這些子句在 Feature 1 只是空真。
- 14 條跨階段 AC 在 Feature 1 只有「拒絕」或「只記錄」：D13、D16 靠 d9，D17、F07 靠 d10，F11、O11 靠 d7a，G13 靠 t1–t7；O01、O15、O19、O22、O23、O26 的 workflow 樣本部分在 M1 驗收。
- 參考實作的 Feature 1 部分（store、state、next 的 phase 判斷、decisions、cli 的相關子命令、測試政策、CI）大致照 design §2、§3 做，另加了 `--feature`、`--token`、`--id` 三個 design 沒列的選項。`status` 的輸出不含版本、plan 或 approval；state 檔裡有這些欄位。
- 13 種 `decide` 中，只有 `approve_plan`、`scope_change` 在 Feature 1 有效果。`resolve_read`、`resolve_operation`、三種 finding kind、`accept`、`return` 要求目標已存在於狀態中，Feature 1 的公開路徑上沒有這些目標，只能驗拒絕。
- issue #6（`approve_plan` 不要求 design 與 spec／AC binding）仍 open。T2.1-01、T2.2-05（Red 有效性）在參考實作裡留到 B1，一直沒有處理。另一個待決問題是：保存下來的 transition 衝突沒有任何命令能解除。

## 1. 來源

| 來源 | 路徑 | 版本 |
| --- | --- | --- |
| roadmap | `docs/roadmap.md` | `cf50449`（sha256 `ba07d7c7e1ef…`） |
| 重切研究 | `docs/research/2026-09-30/controller-recut.md` | `51d3e82`（`c56aa58b809e…`） |
| 需求輸入 | `docs/requirements/delivery-controller/specs/{delivery-orchestration,delivery-gates,durable-delivery,finding-resolution}/spec.md` | `cf50449`（`8eaafa4d14e1…`、`7cdf2ee0b1bd…`、`ace2b0e5b18f…`、`e46512eb6061…`） |
| 高層設計 | `docs/design-candidate/d45-04/{design,tasks,validation,coverage}.md`（revision-17） | `ed03aae`（`3944ac04c806…`、`1a793b5a7e7d…`、`600dd2174576…`、`84076c5c249d…`） |
| 勘誤 | `docs/design-candidate/d45-04-errata.md`（E-1～E-4） | `cf50449`（`6c4f0c94542f…`） |
| 決策 | `docs/decisions.md`：D53、D55、D57、D58、D59、D69、D75 | `cf50449`（`4aaff4d03c5b…`） |
| project intent | `docs/project-intent.md` | `7ee8291`（`eb2182645cdf…`） |
| Feature worktree | `/Users/johnson.chiang/workspace/loop-engineering-run-decisions` | `37ff4f0`（只新增 `openspec/changes/run-decisions/.openspec.yaml`） |
| 參考實作 | `/Users/johnson.chiang/workspace/loop-engineering-thin`：`src/loopctl/{store,state,next,decisions,cli,clock,__init__}.py`、`pyproject.toml`、`workflow.yaml`、`scripts/dist-smoke.sh`、`.github/workflows/loopctl-ci.yml`、`tests/{conftest,test_state,test_decisions,test_cli,test_test_policy,test_ci_workflow}.py` | `fcefecc`；T2.1 結束 `f8fe614`、T2.2 結束 `aa4790a`、T2.2 最後修正 `267b416` |
| 逐 task 審查紀錄 | `loop-engineering-thin/.delivery/bootstrap/thin-s1/tasks/{1.1,2.1,2.2}/`（coordinator-check.json、review-*、attempt-*/result.json）；`loop-2-3/morning-report.md` | 本機未追蹤檔案，2026-09-30 讀取 |
| issue #6 | `gh issue view 6`（唯讀） | OPEN，建立於 2026-09-28，無留言 |

注意：design 目錄的 task 代號在 `.delivery` 下沒有 `T` 前綴（`tasks/1.1`、`2.1`、`2.2`）。

## 2. 逐條 AC

### 2.1 首先由 Feature 1 驗證的 23 條

「F1 成立」指 Feature 1 結束時可由它自己的公開入口觀察到的部分。「空真」指 Feature 1 沒有那個機制，所以子句不會被違反，但也沒有實際觀察。驗證欄照 [coverage.md](../../../design-candidate/d45-04/coverage.md)。

| AC | Req | Scenario（WHEN → THEN，引自需求輸入） | 驗證 | F1 成立 | 需後續階段（原因） |
| --- | --- | --- | --- | --- | --- |
| D01 | DUR-01 | 「使用者打開目前 run 的狀態檔或請求 status」→「可辨識當前進度、適用版本、gate/evidence 理由、需人或外部解決的項目及下一步，無須從整份歷史猜測目前結論」 | s5 | 狀態檔與 `status [--human]` 顯示 phase、owner、三 gate（`pending`／`not_evaluated`）、blockers、next；版本在狀態檔的 `plan`、`versions` | gate／evidence 理由的實際內容：G1、G3 在 F3，G2、Pass 在 F4；`status` 的 budget 欄在 F2（E-2）。recut 把它算在 1 完成。參考實作的 `status` 不輸出版本（§3.1） |
| D02 | DUR-01 | 「設定已變更或有人手改 gate 為 passed，但沒有可核對的 evidence／人工決策」→「系統核對新設定 schema/版本並重評受影響結果，不把手改值當批准；合法 decision 經可驗證操作保存來源與理由。手改可被偵測，且永不當作決策。…（D48）」 | s3 | 手改 `feature.json` → `manual_edit`，exit 5；schema 不符 → exit 5；decision 只能經 `decide`（human actor、reason）；重新登記 plan／spec／design／AC／skill 使 approval 失效 | 「重評受影響結果」：gate 在 F3、F4 才存在；若「設定」指 `workflow.yaml`，G3 重評在 F3。decision 沒有獨立的「來源」欄（§3.5） |
| D03 | DUR-02 | 「兩個 controller 以不同 run IDs 同時 start/adopt 同一 repo+feature」→「最多一方取得協調權；另一方可讀狀態，但不能取得派工許可或新預算。衝突與現有協調者可查。」 | s4 | `claim` 恰一方成功；敗方得 `already_claimed` 與 owner；寫入命令以 token 核對（exit 4） | 「派工許可」要到 F2 才存在，F1 只能以「非 owner 不能寫入」成立；「新預算」空真（預算在 F2）。參考實作沒有 run ID，以 feature id 為鍵；`adopt` 回 unsupported |
| D09 | DUR-05 | 「controller 在更新 state 提交前或提交後被中斷，再次 resume」→「讀到完整舊版或新版；已提交版本可恢復，未引用 evidence 不自動成為已接受結果，且不發出未先持久登記的外部操作」 | s1、s2 | history-first、原子替換、物件先存再引用 | 「不發出未先持久登記的外部操作」要到 F2 的外部寫入才有實質內容 |
| D10 | DUR-05 | 「現行 state 更新時被中斷，或同一 transition 被重複提交」→「已提交的 revision SHALL 可恢復，而且不重複生效；中斷時尚未提交的變更 SHALL NOT 被接受，只可保留作診斷；同一 transition identity 內容不同時 SHALL Blocked。系統 SHALL NOT 以事件重放作為第二份現行狀態來源。」 | s1、s2 | 全部 | — （衝突 Blocked 之後如何解除未定，§5） |
| D11 | DUR-05 | 「resume 遇到 run state 缺失、無法解析、schema 不相容或衝突」→「顯示具體原因與現存檔案，停止派工且保留原資料，不建立空 run 以抹去歷史／budget；未驗證的共享磁碟或多主機 writer 不宣稱受支援」 | s3 | 原因、exit 5（衝突為 3）、原檔 bytes 不變、`init` 不覆寫 | 「停止派工」空真。參考實作只輸出原因，不列現存檔案；s3 也沒有斷言這一點 |
| D13 | DUR-06 | 「外部請求結果 unknown，查不到 marker 且無法證明未執行或可去重」→「保留 outcome unknown 與查詢證據並 Blocked，不盲目再派或再貼；明確失敗時只在原操作 retry budget 內恢復」 | w1、w3、w10、w11、d9、h10、h11 | 只有 d9：`resolve_operation` 由人記錄、需證據與已知 op、0 次外部寫入 | THEN 全部在 F2（w）與 F3（h10、h11）。F1 沒有 op，公開路徑上的 target 一律 `unknown_target`（§4） |
| D16 | DUR-08 | 「同一 infra operation 初次失敗及兩次額外重試均無法完成」→「保存三次 attempts 與 evidence 並 Blocked；不把診斷出的程式／測試缺陷繼續包裝成 infra retry，改回受三輪限制的 correction 流程」 | w4、o1、o3、h8、d9 | d9：`resolve_read` 只記錄 | 讀回與讀取預算在 F2（w4、o1、o3）、F3（h8）；「改回 correction 流程」在 F4 |
| D17 | DUR-08 | 「累計主動時間達 4h 時協調 session 在線；或到限發生在協調 session 離線期間…；或 restart 後讀回已到限的 run」→「不再派新工作。…要調整預算，需保存明確的使用者裁決，不因等待而自動歸零。」 | b0、b1–b7、g15、d10；R1 | d10：`budget_extension` 四種目標只寫紀錄，不改 `workflow.yaml`、不重置計數 | 聯集計時、到期 stop、worker timeout、`active`／`attempts` 延長在 F2；證據命令與 CI 等待在 F3（g15、b4、b6、b7）；review 逾時在 F4（b3） |
| F07 | FIN-03 | 「同一 run 已派三輪 correction，仍有待修缺陷或人工退回」→「保存已做修正、未解 findings、evidence 與待決問題並 Blocked，不派第四輪；明確追加預算須保存使用者裁決而非偷偷重建 run」 | r7、r13(c)、r14、d10 | d10 的 `rounds:+1` 紀錄 | 輪數、Blocked、`rounds` 延長的效果在 F4（T5.1，參考實作沒有做） |
| F11 | FIN-05 | 「PR Pass 仍 acceptance pending，使用者指出原 AC 缺陷」→「保存版本化退回與 finding，核對剩餘 correction 預算後才派修，解除仍須 Reviewer 覆核或明確人工裁決」 | d7a、d7b | d7a：agent 身分、缺 actor／版本／理由、沒有 Pass 時的 `return`／`accept` 都被拒，revision 不變 | 正向路徑在 F4（d7b）。F1 沒有 `pass` phase，`return` 只會得到 `no_pass` |
| G13 | GAT-06 | 「required 集合未設定／為空，或任一 required check missing、pending、cancelled、timed-out、failed、unknown、stale」→「G3 不通過並逐項顯示原因。規則不可讀、且沒有適用的已核准政策時，G3 為 unknown 並 Blocked，不消耗修正輪。…」 | h1–h3、h9、h12、t1–t7、b4、p1 | t1–t6（本機與每個 CI job 同一套收集／skip／xfail 政策）、t7（workflow 結構）；`workflow.yaml` 宣告 `unit-linux` | THEN 全是 G3 判定，在 F3（h、b4）；`github_rules_verified` 在 Pass package，F4（p1）。F1 只建立 GAT-06 內文「同一套政策」的前提 |
| O01 | ORC-01 | 「使用者直接交付已選定的 feature 給 Implementer」→「系統允許進入 design/plan 準備，保留 feature owner 與協調者 identity，不要求經 Project Lead 轉達，也不因此取得開工確認或 scope 變更權限」 | d1；W-C | `init` 不需 Project Lead 交接；phase 為 planning；沒有 `approve_plan` 時 next 為 human | W-C 樣本在 M1 驗收。參考實作只記協調者（`owner.actor`），沒有另記 feature owner；決策者以各 decision 的 `human:<name>` 表示 |
| O02 | ORC-01 | 「Implementer 的 skill、Project Lead 或另一個 session 請求派發同一 feature 的外層實作／正式 review」→「系統只接受經 controller 許可、由持有該 feature 協調權的 orchestrate 派出的 assignment。沒有協調權的 session 只能讀取狀態；局部 review 不能更新 G2，也不能繞過 controller。」 | s4；r1 | 協調權唯一；非 owner 只能讀 | assignment 許可在 F2；「局部 review 不能更新 G2」在 F4（r1） |
| O03 | ORC-02 | 「feature 使用 issue 內文與 `docs/superpowers/plans/P03-ingest.md` 等既有原生文件」→「交接保留實際位置與適用版本，能讀回採用內容；不因採用 OpenSpec 而把舊成果重新命名或把 task 各自建立為 PR」 | d6 | `register plan|binding` 原樣保存 locator、version、digest 與內容物件；讀不到的 plan 拒絕 | 「task 不各自建 PR」空真（PR 在 F3）。ORC-02 內文要求 issue 內文帶 issue identity 與觀察時間；參考實作的 `init --issue` 只存一個字串 |
| O05 | ORC-03 | 「design/plan 已準備但沒有適用版本的明確使用者確認」→「狀態顯示等待開工確認及待確認版本，不派 implementation worker；沉默、timeout 或 agent 同意不視為批准」 | d1、d2 | next 為 `human`（`plan_not_approved`，可用 `approve_plan`）；只有 human actor 的 `approve_plan` 產生 approval | 「不派 worker」在 F2 之前空真。「待確認版本」在狀態檔的 `plan.version`；參考實作的 `status`／`next` 輸出不含 |
| O07 | ORC-03 | 「修正需要改 AC、spec 或已核准設計，或使用者提出範圍外想法」→「系統保存未完成項與影響，提出獨立 feature 候選或版本化 scope 決策；取得適用確認後才依新契約派工」 | d4 | `scope_change` 記錄、撤銷 approval、轉 awaiting_approval、舊 plan 標為 superseded；登記新版本後才能再 approve | 「未完成項」與「依新契約派工」要有 tasks 與派工（F2）；g13(f) 回 D11 在 F3；「提出獨立 feature 候選」由 Project Lead 負責（D55） |
| O11 | ORC-05 | 「使用者已接受版本 V1，之後 PR head、適用 spec 或 design 改成 V2」→「保存 V1 的接受歷史，V2 的 acceptance 為 pending 並重評相關 gates；不把 V1 accepted 移植到 V2」 | d7a、d7b | d7a 紀錄層拒絕 | 正向路徑全部在 F4（d7b） |
| O15 | ORC-07 | 「使用者只查看流程或規格，尚未以明確的 `init` 或授權啟動某項工作（例如暫停中的試用或 Retro）」→「系統 SHALL NOT 接管該工作，也 SHALL NOT 啟動 Retro 或 PR gating；…產品 SHALL NOT 含針對特定歷史試用（例如 P03、Q-TARGET）的特判。」 | s7；W-F | 沒有 `init` 時 status／next／claim 回 `feature_not_found`，不建狀態，也不接管其他 feature | W-F（`rg "P03|Q-TARGET" src/` 為空、樣本）在 M1 驗收；Retro 不做（M2） |
| O19 | ORC-01 | 「agents 使用相同入口，或 runtime 將 Project Lead 與 Implementer 顯示為父子 sessions」→「系統仍依角色責任與使用者明確授權判定可執行動作，不從入口／父子標記新增委派權或 scope 變更權…；正式 Reviewer 仍符合 G2 獨立契約」 | d5；W-E | 非 `human:<name>` 的 actor 一律拒；權限只看 token 與人工 decision | 「正式 Reviewer 符合 G2 獨立」在 F4（profile 在 F2）；W-E 在 M1 驗收 |
| O22 | ORC-11 | 「Project Lead 交出 feature spec 與初步工作包，Implementer 研究後發現需要合併、補充或重排任務」→「Implementer…保存最終 tasks／介面／依賴／AC 驗法及版本，再依 D11 一次確認；controller 不依尚未確認的草案提前派工，也不另建一份 Project Lead 的執行計畫」 | d2；W-C | `producer=project_lead` 或沒有 `--calibrated-from` 的 plan 不能批准；狀態只有一個 `plan` 欄 | 「不提前派工」在 F2 之前空真。plan 裡的 task／AC 結構要到 F2 才由 `loopctl-plan` 區塊解析（#6）；W-C 在 M1 驗收 |
| O23 | ORC-11 | 「Implementer 發現任務調整需要改 AC、突破高層設計限制或改變其他 feature 依賴的契約」→「保存具體影響與待決事項…未取得適用決策前 SHALL NOT 依該變更派工。第一片：整個 run SHALL 停下等待批准，不派任何新 attempt（d4、W-C）。**[延後 S2]**…」 | d4、W-C | 同 O07 的 d4 | 「不派新 attempt」在 F2；W-C 在 M1 驗收；只停受影響的工作在 M2 |
| O26 | ORC-12 | 「當前 SA 已滿足完成條件且有適用使用者確認，或引用的既有成果與確認經核對仍適用」→「保存 readiness 理由、版本及確認來源並交下一階段，不重做已確認的完整 grill；controller 仍須在 feature design＋plan 完成後核對 D11，不能依 SA 確認直接派 implementation worker」 | d2；W-C | `register binding --role sa` 不會產生 approval | W-C 在 M1 驗收。D59：同一人兼任時，SA 確認併入開工確認 |

跨階段的完成點（recut L86–116）：D17 1→2→3→4；D13、D16 1→2→3；G13 1→3→4；F07、F11、O02、O11 1→4；O01、O15、O19、O22、O23、O26 1→V（M1 驗收）。

### 2.2 同一批 requirement 下，Feature 1 不碰的 scenario

| Req | Scenario | 落在哪裡 |
| --- | --- | --- |
| ORC-01 | O18 授權 Project Lead 協調與委派 | M2；F1 只驗 d8 的拒絕（§2.3） |
| ORC-02 | O04 權威來源衝突 | M1 驗收（W-B） |
| ORC-03 | O06 核准後按 plan 前進 | F2（d3），R2 在 F3 |
| ORC-05 | O10 Pass 尚未接受或 merge | F4（p6、r12）。F1 的 CLI 已把 `merge|close|release|deploy` 當 usage error（test_cli.py:31–45），但 coverage 不把它算進 O10 |
| ORC-07 | O14 重複接受事件（Retro） | M2（D55 改由 project-lead skill 承接） |
| ORC-12 | O24、O25、O27、O28 | M1 驗收（W-A、W-B） |
| GAT-06 | G14 舊成功不能蓋過新 attempt；G15 衍生整合 snapshot | F3（h4、h4a–h4e、h12；G15 只驗 h5 的負例），G15 正向在 M2。validation 的 t7 列也標了 G14，但 coverage 的 G14 列沒有 t7 |
| DUR-02 | D04 Worker 狀態 unknown | F2（w5、w8、b2；R1） |
| DUR-06 | D12 發文成功但回應遺失 | F2（w2、w10）→ F3（h10）→ F4（p5） |
| FIN-03 | F05 CI 先失敗仍收齊 review；F06 完整回應批次 | F4（r5、r6） |
| FIN-05 | F12 新需求或規格錯誤 | M1 驗收（W-C） |

ORC-11、DUR-01、DUR-05、DUR-08 沒有其他 scenario。

### 2.3 O08、O09、O18：只驗拒絕，不算覆蓋

coverage L35、L36、L45 寫明「第一片只驗 d8 的拒絕，不算覆蓋」；recut L80 也這樣記。d8（validation L91）：`adopt`、`delegate` 回 `unsupported`，狀態不變，沒有繞過任何核對。參考實作中，`decide adopt|delegate` 回 exit 2 `unsupported`（decisions.py:74–75，cli.py:423）；頂層 `adopt`／`delegate` 是 argparse 的 usage error，也是 exit 2（test_decisions.py:512–548）。design §2 L56 對兩種結果都接受（「exit 2 或 `unsupported`」）。

## 3. 行為清單：design 與參考實作

引用格式：design 指 `docs/design-candidate/d45-04/design.md`，參考實作的路徑都在 `loop-engineering-thin@fcefecc` 下，另註明者除外。

### 3.1 CLI

| 命令 | design | 參考實作 | 與 design 的關係 |
| --- | --- | --- | --- |
| 輸出 envelope 與 exit code | §2 L39–40：`ok, revision, result, blocked, next, safety`；0／1／2／3／4／5 | cli.py:31–32、53–68 | 一致 |
| `status`（不帶 feature） | §2 L45 | cli.py:257–262：`phase: empty`，next 為 `human no_feature` | 一致（test_cli.py:18–28） |
| `status --feature F [--human]` | §2 L45 寫 `status [--human]` | cli.py:117–119、235–254；state.py:61–90 | 多了 `--feature`（2.1 coordinator-check）。輸出只有 feature、phase、owner.actor、三 gate、blockers；不含 plan、versions、approval。`fcefecc` 另加 `budget` 與 timeout gate（cli.py:244–245，屬 T7.1，依 E-2 是 F2） |
| `next --feature F` | §2 L45 | cli.py:120–121、248–249；next.py | 多了 `--feature`；`result` 只有 feature 與 phase |
| `init --repo --repo-id --feature --issue` | §2 L44 | cli.py:122–126、265–287 | 一致。已存在 → `feature_exists`（exit 1）；狀態不可信時不重建 |
| `claim --actor` | §2 L44 | cli.py:127–129、294–321；state.py:40–54 | 多了 `--feature`。已有 owner → `already_claimed` 並附 owner actor。token 只回傳一次，狀態只存 sha256 digest，以 `hmac.compare_digest` 比對。token 用 64 位 hex，不會以 `-` 開頭（`a63833c`） |
| `register plan|binding|policy` | §2 L46：locator、版本、digest；plan 另記 producer 與校準來源 | cli.py:130–141、356–394；decisions.py:210–260 | 另有 `--feature --token --digest --producer --calibrated-from --role`。binding role 可為 spec、design、ac、sa、skill、baseline（decisions.py:36）。plan 必須是可讀檔案（T2.2-03）；重新登記時，plan 的綁定欄位或 approval 涵蓋的 digest 改變就撤銷 approval（T2.2-02） |
| `decide <kind>` | §2 L47：13 種 | cli.py:142–154、397–434；decisions.py:72–207 | 另有 `--feature --token --id`（2.2 coordinator-check），以及 `--actor --target --version --reason --evidence --bind --not-delivered --category`。actor 必須符合 `human:<name>`（decisions.py:45、67–69）。同一 id、同內容重送是冪等，內容不同 → `decision_id_conflict`。未知 kind → exit 2 `unsupported`。要有 claim token，所以人工決策經由協調者送出 |
| 未知子命令（merge、close、release、deploy、adopt、delegate） | §2 L56 | argparse usage error，exit 2，0 次外部呼叫（test_cli.py:31–45） | 一致 |
| `safety` | §2 L71 | cli.py:167–168、505–519 | T2.3 加的（F2）。F1 範圍內 envelope 的 `safety` 一律為 null |

### 3.2 Store 契約與狀態檔

| 項目 | design §3 | 參考實作 | 與 design 的關係 |
| --- | --- | --- | --- |
| 位置 | L75 `$LOOPCTL_HOME/features/<id>/feature.json` | store.py:3–13、64–65：`feature.json`、`history/<rev>.json`（write-once）、`conflicts/`、`lock`、`objects/<sha256>`；預設 `~/.loopctl` | 一致；目錄以 feature id 為鍵，不含 repo |
| `load` | L85 | store.py:189–194；另有 `FeatureNotFound` | 一致 |
| `commit` | L86 | store.py:289–325：在 lock 內讀取、核對 revision（318–319）、同 transition 同內容回傳原 revision（310–315）、內容不同則把衝突存進 `conflicts/` 並拋出（316–317） | 一致。之後每次 commit 都因保存的衝突而被拒（308–309），沒有命令能清除 |
| history-first | L82 | `_write_once` 以 `os.link` 保證 write-once（114–126），再原子替換 `feature.json`（129–132、322–324）；history 領先一版時讀者取新版（181–185），下一次 commit 修復 `feature.json`（306–307） | 一致 |
| lock | L86 | `flock` 在 `features/<id>/lock`（135–142） | 一致；只適用單機 |
| 不可信狀態 | L83 | 缺檔、壞 JSON、`schema_version≠1`、history 缺或壞、手改（`state_digest` 與 history 不符，179–180）、history 分岔 → `UntrustedState`（exit 5） | 一致 |
| 首次建立 | — | 在旁邊建好目錄再 rename 到位（266–279） | 設計細節 |
| 證據物件 | L87 | `put_object`／`get_object`（331–354）；commit 時核對每個 `{"$object": digest}` 引用存在且未毀損（243–250，T2.1-02）；純 digest 字串不算物件引用（357–359，s6） | 一致 |
| fsync | 未指定 | `os.fsync`，darwin 另加 `F_FULLFSYNC`（85–89） | 設計細節 |
| 狀態欄位 | L76 的 16 欄 | state.py:16–37 相同 16 欄，另有 repo、repo_id、issue；store 補 schema_version、feature、revision、transitions（209–223） | 一致 |
| owner token | L88 | state.py:40–54 | 一致 |

### 3.3 `next` 在 Feature 1 用到的部分

design §2 L58–71 定義 8 個動作。Feature 1 只會產生 `human`（帶 `blockers` 與 `decision_kinds`）；`done` 需要 `pass`／`accepted` phase，F1 的公開路徑到不了。

參考實作的優先順序（`fcefecc` next.py:79–110 裡屬於 F1 的部分，以及 `aa4790a` next.py:19–35）：記錄的 blockers 與 transition 衝突 → `unclaimed` → `plan_not_registered` → `plan_not_calibrated` → `plan_superseded:<scope_change id>`（不提供任何 kind，T2.2-06）→ `plan_not_approved`（提供 `approve_plan`）→ `approved`／`implementing`：F2 的派工路由 → `pass`／`accepted`：`done`。

在 T2.2 結束的 `aa4790a`，phase 為 `approved` 時 next 回 `human(["no_next_action:approved"])`（next.py:35）；派工是 T2.3 加上去的。另外，`init` 之後 phase 是 `planning`；登記 plan 不會改 phase。`awaiting_approval` 只在 approval 被撤銷（重新登記或 `scope_change`）時出現（decisions.py:203–206、254–259）。

### 3.4 專案骨架、測試政策、`workflow.yaml`、CI、dist-smoke

main（`c91b774`）沒有 `src/`、`tests/`、`pyproject.toml`、`scripts/`、`.github/`、`AGENTS.md`。

| 項目 | design／validation | 參考實作 | 與 design 的關係 |
| --- | --- | --- | --- |
| `pyproject.toml`、`uv.lock` | tasks L78、L111 | pyproject.toml:1–25：只支援 Python 3.12；執行依賴只有 pyyaml；dev 依賴 pytest、ruff、mypy、types-PyYAML；uv_build | 一致。pyyaml 只有 F2、F3 的模組用到（assignments、observe、preflight、gates）；F1 的模組都不 import yaml |
| 單一時鐘 | tasks 通用規則 L19 | clock.py:1–7 | 一致 |
| 測試政策 | design §11 L401–416；validation §0 | pyproject.toml:18–25（`--strict-markers`、`xfail_strict`）；conftest.py:1–69（`only_on`、session 失敗條件、`LOOPCTL_EXPECT_PLATFORM`） | 一致。conftest.py:72–104 另有 `fakes` fixture，在 PATH 放 fake `herdr`（T1.1 preflight 用，屬 F2）；test_state、test_decisions 用 `fakes.calls() == []` 斷言「0 次派工」 |
| `workflow.yaml` | validation §6.2 L292–331；D53 採 §6.3（只有 `unit-linux`） | workflow.yaml:1–30，`required_checks` 只有 `unit-linux`（L10） | 照 D53。其中 `profiles`、`timeouts`、`limits`、`evidence` 只有 F2、F3 會讀 |
| policy_change 綁定 | design §8 L257；D53「T1.1…以 `policy_change` 綁定」 | `register policy` ＋ `decide policy_change --target <locator> --version <digest>`（decisions.py:176–181）；效果在 gates.py:663–711（G3，F3） | F1 只能記錄 |
| CI | validation §6.1 L268–290；D53 | .github/workflows/loopctl-ci.yml:1–59：只由 `pull_request` 觸發、只有 `unit-linux`、checkout PR head、核對 SHA、在測試前上傳 `tested-sha-*`、`uv sync --frozen`、pytest、ruff、mypy、dist-smoke | 另加 commit-msg 檢查步驟（L56–59，`e091b61`）與 `fetch-depth: 0`，§6.1 沒有 |
| t7 | validation L66 | test_ci_workflow.py（583 行）：檢查結構，並在 scratch 目錄以最小環境執行 SHA 檢查與產物步驟 | 經 T1.1-02、04、05 修正（§5） |
| dist-smoke | validation §6.1 L277 | scripts/dist-smoke.sh:1–21：build wheel、在新 venv 安裝、在 checkout 外跑 `loopctl --help` 與 `import loopctl.tools`，並確認 `import delivery` 失敗 | 一致。`loopctl.tools` 在 roadmap 裡屬於 F2（herdr） |

### 3.5 協調者記下的偏差，以及對照需求原文的缺口

| 項目 | 出處 | 狀態 |
| --- | --- | --- |
| `status`／`next` 多一個 `--feature` | 2.1 coordinator-check | 留給 B1 判斷；B1 沒有執行 |
| `decide` 多 `--id` 與 `--token` | 2.2 coordinator-check | 同上 |
| actor 必須是 `human:<name>` | 2.2 coordinator-check | 同上 |
| `accept`／`return` 的契約（phase `pass` 加 `acceptance.version_key`） | 2.2 coordinator-check；decisions.py:161–166 | 預先為 T6.2 定義 |
| token 可能以 `-` 開頭，導致 `--token <value>` 解析失敗 | 2.2 coordinator-check follow_up | 已修（`a63833c`，改用 hex） |
| plan 要有一段 `loopctl-plan` YAML | 2.3 coordinator-check；assignments.py:1–13、49 | 屬 F2。F1 的 `register plan` 不驗證這段 |
| 保存的 transition 衝突沒有命令能解除 | 2.1、2.2 coordinator-check；morning-report L53 | 未決 |
| t4 與 `import delivery` 防護沒有有效 Red；stub commit 早於 Red | 1.1 coordinator-check | 留給 B1；B1 沒有執行 |
| ORC-05 要求人工決策保存「actor、來源、時間、問題／版本、選擇、理由與影響」 | 需求原文 L85 | 參考實作的 decision 有 id、kind、actor、target、version、reason、at、seq（另依種類有 evidence、resolution、category、supersedes）；沒有「來源」與「影響」欄 |
| DUR-01 要使用者能「直接找到…版本…」 | 需求原文 L20 | 狀態檔有；`status` 輸出沒有（§3.1） |
| AC-D11「顯示具體原因與現存檔案」 | 需求原文 L90 | 只輸出原因（cli.py:214–221） |
| DUR-01、DUR-02「同一 repo＋feature」 | 需求原文 L20、L32 | 狀態以 feature id 為鍵（store.py:68–71），repo 只是欄位 |

## 4. 屬於後續 Feature 的 decide 種類

design §2 L47 列出 13 種。tasks L109：`decisions.py` 只由 T2.2 擁有，`resolve_read`、`resolve_operation`、`budget_extension` 在這裡只記錄，效果寫在其他模組。validation d9、d10 也寫明「只寫入 decision 紀錄」。

| kind | design | 記錄前的核對（decisions.py） | 效果在哪裡（參考實作 → Feature） | F1 公開路徑能驗到什麼 | validation |
| --- | --- | --- | --- | --- | --- |
| `approve_plan` | §2、§8 L280 | phase、plan 已登記、producer=implementer 且有 calibrated_from、target／version 等於 plan、沒有被 supersede（146–160） | decisions.py:195–202 → **F1** | 正向與負向都能驗 | d1、d2、d5 |
| `scope_change` | §1 L30、§2 | 共同欄位 | decisions.py:191–193、203–206 → **F1** | 從 `approved` 觸發能驗；`implementing` 要到 F2 才進得去（參考測試用 `store.commit` 做出這個 phase） | d4 |
| `policy_change` | §8 L253–257 | 已登記 policy，且 target／version 等於它的 locator／digest（176–181） | gates.py:663–711、1117–1125 → F3 | 只能記錄 | 無 F1 列（參考實作另有 test_decisions.py:774–795）；h1 在 F3 |
| `budget_extension` | §10 L396–399 | target 只用 regex 檢查（47–49、100–105），不看狀態 | `active`、`attempts` → budget.py（F2）；`ci_wait` → F3；`rounds` → T5.1（F4，參考實作沒有） | 四種目標都能記錄，但沒有效果 | d10；b2–b6、r14 |
| `revise` | §2；§8 L288（整合觸發） | 共同欄位 | gates.py:964（整合觸發，T6.1）→ F3；開 batch 在 F4 | 只能記錄 | h13、r12 |
| `handoff` | 只在 §2 列名，沒有定義語意 | 共同欄位 | 沒有效果；preflight 把它當負例命令（preflight.py:177，F2） | 只能記錄 | 無 |
| `resolve_read` | §5 L141 | target 必須在 `read_budget` 裡（173–175） | observe.py:205–222 → F2（F3 延伸到 ci／pr key） | F1 沒有 `read_budget`，只會得到 `unknown_target`；正向紀錄要用 store API 預先做出狀態 | d9；o1、h8 |
| `resolve_operation` | §4 L125–127 | target 必須在 `writes` 裡；`--bind` 與 `--not-delivered` 二選一；需要 evidence（77–95、170–172） | writes.py:224、466–481 → F2 | 同上，只會得到 `unknown_target` | d9；w10、h10 |
| `resolve_finding`、`waive_finding`、`reclassify_finding` | §9 L344、L348 | target 必須在 `findings` 裡；reclassify 另檢查 category（96–99、167–169） | T5.1 → F4（參考實作沒有效果） | 只會得到 `unknown_target` | r4（F4）；參考實作另有 test_decisions.py:745–772 |
| `accept`、`return` | §9 L361–365 | phase 為 `pass`、acceptance pending、version 等於 `version_key`（161–166） | T6.2 → F4（d7b） | 只會得到 `no_pass` 等拒絕 | d7a；d7b |

所有種類共同的核對：必填 feature、id、actor、target、version、reason；actor 必須是 human；要有 claim token；同一 id 冪等（decisions.py:72–87、184–190；cli.py:397–434）。效果模組以 decision id 讀取 `decisions`，所以同一筆 decision 只生效一次（decisions.py:5–8；design §10 L397）。

## 5. 已知缺口與審查 finding

逐 task 審查使用 `codex exec` 的 GPT-6 Sol high、唯讀 sandbox；紀錄都標 `not_g2`。

| ID | 內容（簡述） | 屬於哪個 Feature | 狀態（參考實作） |
| --- | --- | --- | --- |
| #6（T2.2-01） | `approve_plan` 只要求 plan 是 implementer 產出且有 calibrated_from，不要求已登記 design、spec／AC binding、task→AC、依賴、scope、驗法（ORC-03） | F1 | Lead 降為 nonblocking：第一片由人工 D11 確認負責內容完整；issue OPEN，等 spec／design 說明 loopctl 是否要強制檢查。roadmap F1 列（L31）把它列在「勘誤與 issue」 |
| T2.1-01 | s1–s7 的 Red 全部停在 `init` 這個未知命令，沒有碰到各列要驗的行為 | F1（證據） | before-B1，未處理（B1 沒有執行） |
| T2.1-02 | 物件毀損時 commit 與 `put_object` 仍然接受 | F1 | 已修（`3f11cf6`），覆審 clean |
| T2.2-02 | approval 失效只比對 digest | F1 | 已修（`f1ff495`） |
| T2.2-03 | 讀不到內容的 plan 帶上 `--digest` 就能登記並批准 | F1 | 已修（`339e1ab`） |
| T2.2-04 | `scope_change` 後可直接重新批准同一份 plan | F1 | 已修（`9fe50e6`，照 Lead 裁定：要登記新 binding） |
| T2.2-05 | d2、d4、d5、d7a 的 Red 沒有證明各列的行為 | F1（證據） | before-B1，未處理 |
| T2.2-06 | `scope_change` 之後 next 仍提供 `approve_plan` | F1 | 已修（`267b416`），覆審 clean |
| （協調者待決） | 保存的 transition 衝突沒有 `decide` 種類或命令能解除 | F1 | 未決 |
| T1.1-02 | t7 沒有真正檢查 SHA 比對與產物內容 | F1（CI） | 已修（`9efff47`、`7a09e82`） |
| T1.1-04 | t7 的輔助程式以完整環境執行 workflow 裡任意的 `run:` | F1（CI） | 已修（`eea81ef`） |
| T1.1-05 | t7 丟掉 job 層級的 env | F1（CI） | 已修（`07f2294`），rereview-3 clean |
| T1.1-01、T1.1-03 | preflight 不核對版本；f 案例的 Red 無效 | F2 | 已修 |
| E-1、E-2、E-3 | op 終態 `superseded`；T7.1 擁有 cli 的 budget 部分；h7 的 G2 格子 | F2、F2、F4 | 勘誤已裁定 |

T1.1 的 review-1 被使用者中止（`exit=stopped-by-user`），沒有結果。依 roadmap L49，上表「已修」只描述參考實作的行為，不是 Feature 1 的證據。

## 6. 行數

| 範圍 | `aa4790a`（T2.2 結束） | `fcefecc` |
| --- | ---: | ---: |
| `store.py` | 354 | 359 |
| `state.py` | 84 | 90 |
| `next.py` | 35 | 110（F1 部分約 40，其餘是 T2.3、T3.1、T6.1、T7.1 加的） |
| `decisions.py` | 230 | 264 |
| `cli.py` | 386（含 preflight 約 25 行） | 557（加了 write、result、observe、evidence、assess、safety） |
| `clock.py`、`__init__.py` | 7、1 | 7、1 |
| `tests/test_state.py` | 356 | 428（20 個測試） |
| `tests/test_decisions.py` | 672 | 795（66 個） |
| `tests/test_cli.py` | 49 | 99（20 個；observe 的案例屬 F2） |
| `tests/test_test_policy.py` | 99 | 99（9 個） |
| `tests/test_ci_workflow.py` | 178 | 583（37 個） |
| `tests/conftest.py` | 104 | 104 |
| `pyproject.toml`、`workflow.yaml`、`dist-smoke.sh`、CI | 25、30、21、54 | 25、30、21、59 |

- 測試個數是在 scratchpad 以 `git archive fcefecc` 展開後，執行 `uv run --frozen --offline pytest --collect-only` 得到的收集數，不是執行結果。
- 參考實作中對應 F1 的程式約 1,070 行（`aa4790a`），測試約 1,460 行。修正後（`fcefecc`，只計 F1 部分）程式約 1,100 行，測試約 2,100 行。recut 的估計是程式 1,000–1,300 行、含測試約 3,000 行（L39）。
- 耗時：T2.1 的 agent 時間 14 分 17 秒，T2.2 為 12 分 21 秒，都用 high（morning-report L13–14）；之後的修正與逐 task 審查沒有計時。

## 7. 事實、假設、未知

**事實**

- 23 條 AC、各自的驗證案例、recut 的階段對照，以及「1 完成 9 條」（D01、D02、D03、D09、D10、D11、O03、O05、O07），都出自上述檔案。
- 參考實作的行為、偏差與審查狀態，都已在 `fcefecc` 或各 commit 核對過原始碼與 `.delivery` 紀錄。
- main 沒有程式骨架、CI、`AGENTS.md` 或 commit-msg hook；參考 branch 有（`c603a93`、`072dc9f`、`c934ce9`）。
- 依 D53，必要 CI 只有 `unit-linux`；D75 之後 D53 的核准只是歷史，D45-04 是高層設計參考（roadmap L93）。

**假設**（推論，未驗證）

- F1 的 PR 會是 repo 第一次跑 `unit-linux`，所以 F1 會留下第一筆真實 CI 紀錄；但 loopctl 自己的 G3 判定要到 F3 才有。
- 如果照參考實作的做法，F1 只做紀錄的 kind 由後續 Feature 依 decision id 讀取並生效，F2–F4 不需要改 `decisions.py` 的紀錄格式（tasks L109）。這一點取決於後續 Feature 的 design。

**未知**

- F1 在 `approved` 時 `next` 要回什麼。參考實作在 T2.2 結束時回 `human no_next_action:approved`，design 的動作詞彙沒有對應的定義。
- F1 沒有任何外部呼叫時，如何證明「0 次派工／寫入」。參考實作靠 F2 的 fake `herdr` 與呼叫紀錄。
- `handoff` 這個 kind 的語意（design 只列名）。
- `workflow.yaml` 裡 F2、F3 才用到的段落，如果在 F1 就綁定，之後改動時是否每個 Feature 都要一筆新的 `policy_change`（tasks L110 要求如此）。
- DUR-01、ORC-02、ORC-05、AC-D11 原文中參考實作沒有做的部分（§3.5 後四列）要在 F1、之後的 Feature，還是 M2 處理。

## 8. 需要 Project Lead 決定的範圍問題

1. **`workflow.yaml` 與 CI 的內容**（骨架與 `unit-linux` 在 F1，已由 roadmap L31 與 D75 定案）
   - 選項 A：照參考實作建立完整的 `workflow.yaml`（含 `profiles`、`timeouts`、`limits`、`evidence`），CI 帶 commit-msg 步驟，dist-smoke 檢查 `import loopctl.tools`。
   - 選項 B：F1 只放它自己讀到的段落（`g3`、`budget`），F2、F3 各自以 `policy_change` 補上；CI 只照 validation §6.1；dist-smoke 不檢查 `loopctl.tools`。
   - 選項 C：介於兩者，例如檔案完整但 CI 不加 commit-msg。
   - 依據：validation §6.2 L292–331；tasks L110（改動需要 `policy_change`）；roadmap L31、L32（profiles 與 preflight 屬 F2）；ref CI L56–59；main 沒有 `scripts/hooks` 與 `AGENTS.md`。
2. **後續 Feature 的 decide 種類**
   - 選項 A：13 種都在 F1 做成「只記錄」。這與參考實作、validation d7a／d9／d10、recut 的 AC 對照一致。其中 `resolve_*`、finding kinds、`accept`／`return` 在 F1 的公開路徑上只能驗拒絕。
   - 選項 B：F1 只做有效果、或不需要狀態目標的種類（`approve_plan`、`scope_change`、`policy_change`、`budget_extension`、`revise`、`handoff`），其餘到擁有效果的 Feature 再加。這樣 D13、D16、F11、O11 的首先驗證會移到後面，需要改 recut 的對照。
   - 選項 C：F1 只做 `approve_plan`、`scope_change`（`policy_change` 視問題 1 的答案）。
   - 依據：§4 表；tasks L109；roadmap L42（F07 的例子）；D58（archive 時必須已經成立）。
3. **#6：批准前是否強制檢查 binding**
   - 選項 A：維持 Lead 在 2026-09-28 的裁定，由人工 D11 負責內容完整，#6 保持 open。
   - 選項 B：F1 的 `approve_plan` 要求 spec／AC（以及 design）binding 已登記，d2 的正例 fixture 要跟著改。
   - 選項 C：再加上 task→AC 結構的檢查。這需要解析 plan，而參考實作是在 F2 的 `assignments.py`（`loopctl-plan`）解析的。
   - 依據：ORC-03 L55；AC-O06 L63（批准綁定 plan 版本與 producer／校準來源）；validation d2 L85；#6 內文；decisions.py:114–116。
4. **recut 算作「F1 完成」的 AC 中，空真子句怎麼寫**（D03、D09、D11、O05、O07）
   - 選項 A：F1 的 spec delta 照原文寫進，依 recut 當作 F1 完成。
   - 選項 B：只寫 F1 觀察得到的部分，F2 再以 MODIFIED 補上派工子句。這會讓這些 AC 變成跨階段。
   - 依據：roadmap L40–41（spec delta 只寫 Feature 結束時已經成立的部分）；D58；recut L118。
5. **需求原文有、參考實作沒有的部分是否進 F1**
   - 項目：decision 的「來源／影響」欄（ORC-05）；`status` 顯示版本與 approval（DUR-01、O05）；不可信狀態時列出現存檔案（D11）；以 repo＋feature 為鍵（DUR-01、DUR-02）；issue 觀察時間（ORC-02）；解除 transition 衝突的方法（D10）；`approved` 時 next 的回應。
   - 選項：F1 補齊；列為 F1 不做並記在 proposal 的「不做」；或延到 M2。
   - 依據：§3.5 表；§7 未知。
