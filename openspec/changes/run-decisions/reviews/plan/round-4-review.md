verdict: clean

P3 三項已解；P1、P2 沒有退回。另有一項 **minor、不阻擋** 的介面摘要文字問題。

已核對 HEAD `020b046` 與差異；spec 未變，工作目錄無變更。以下 `design.md`、`tasks.md` 均指 `openspec/changes/run-decisions/`，行號為本輪版本。這是計畫審查，Red 可達性依契約推演，未執行測試。

| ID | 判定 | 依據 |
|---|---|---|
| P3-01 | resolved | `superseded_by` 改由所有仍 `in_effect`、匹配目前 plan 的 scope 推導；登記、批准、next 共用判斷。新增 S／S2 疊加後放棄 S2 的案例，同時驗證 next、批准與重登仍受 S 阻擋。`design.md:252`、`:254`、`:289`、`:317`；`tasks.md:380`。 |
| P3-02 | resolved | D4 已明定有值的 `resolves` 先驗未解目標，未知／已解除目標回 exit 1；沒有 `resolves` 的其他寫入才受一般 Blocked 檢查。5.1 依賴與測試已同步。`design.md:163`、`:164`、`:165`；`tasks.md:296`、`:323`。4.2 摘要措辭另見 P4-01。 |
| P3-03 | resolved | gate 保存到達數與放行原因；只有八個到齊且 `all_arrived` 才算競態 Red 證據，timeout 不算。`design.md:392`、`:393`；`tasks.md:202`、`:441`。 |

P1、P2 各條維持原判定：

| ID | 判定 | 本輪核對依據 |
|---|---|---|
| P1-01 | resolved | 授權仍先於重送與衝突；兩類非 owner 測試保留。`design.md:158`；`tasks.md:260`、`:295`。 |
| P1-02 | resolved | init 保存 coordinator，claim 才授予 token 協調權。`design.md:116`、`:117`；`tasks.md:197`、`:200`。 |
| P1-03 | resolved | 全部物件引用仍在提交前驗證。`design.md:171`；`tasks.md:207`。 |
| P1-04 | resolved | 三種選擇及 A 的重新驗證契約保留；撤銷不還原核准。`design.md:219`、`:220`、`:310`；`tasks.md:297`、`:342`。 |
| P1-05 | resolved | 測試順序與精確錯誤斷言保留；競態 Red 現另有施加成功的證據。`tasks.md:101`、`:202`、`:256`、`:262`。 |
| P1-06 | resolved | 入口、參數轉送、子程序接縫自測與 smoke Red 保留。`tasks.md:116`、`:119`、`:120`、`:124`。 |
| P1-07 | resolved | parser／handler 分工及 status 投影沒有退回。`design.md:70`、`:326`；`tasks.md:337`。 |
| P1-08 | resolved | SA version、source 的保存斷言保留。`tasks.md:338`。 |
| P1-09 | resolved | Commit 格式及 build／ci 例外保留。`tasks.md:24`、`:25`、`:98`、`:150`。 |
| P1-10 | resolved | fsync、F_FULLFSYNC 與斷電證據界線維持限縮。`design.md:430`；`tasks.md:435`。 |
| P2-01 | resolved | 前移仍只在授權、驗證通過後執行；連續中斷案例保留。`design.md:153`、`:173`、`:188`；`tasks.md:259`。 |
| P2-02 | resolved | B2 案例仍要求新的 Y 批准，不會復活 X 的核准。`design.md:310`、`:317`；`tasks.md:380`。 |
| P2-03 | resolved | Red 仍驗落敗者的受控回應，且要求 gate 等齊的紀錄。`tasks.md:202`。 |
| P2-04 | resolved | 同步失敗測試仍限定 link 前；link 後失敗另按提交邊界處理。`design.md:180`；`tasks.md:205`。 |

推導規則與既有預期可以一致成立：

- **提交路徑：** 一般更新、衝突紀錄與解除紀錄都在最終 `derive` 前形成新狀態；duplicate、拒絕與讀取不寫檔（`design.md:167`、`:169`、`:188`）。`attempted` 另受「在撤銷後的狀態上照常核對」約束，因此對 A 的驗證也須採用該時點的 D7 判斷，不能沿用撤銷前的欄位值（`:219`、`:254`）。
- **既有 scope 案例：** 單筆 S 放棄後清單為空；B2 仍須重新批准；S2 放棄後仍留下 S；新版本 P2 不匹配舊 scope，仍可批准並回 `dispatch`。測試已同步將 scalar 改成 list，沒有改掉這些行為預期（`tasks.md:378`、`:379`、`:380`）。
- **錯誤優先序：** 4.1 的授權與 payload 冪等仍在前；4.2 加入目標檢查；5.1 採用相同例外。原樣重送已接受的解除 decision，仍先依 D4 第 3 步回 duplicate；`unknown_target` 是後續目標檢查的結果（`design.md:159`、`:164`；`tasks.md:282`、`:323`）。

**P4-01**

- **嚴重度：minor，不阻擋**
- **位置：** `tasks.md:270`
- **問題：** 4.2 的括號摘要寫成「`resolves` 不是未解衝突 → `unknown_target`，否則有未解衝突 → exit 3」，漏掉「有值／沒有值」的分支條件。字面上會把有效的解除目標也導向 exit 3。
- **依據：**
  - **事實：** D4 明確規定有效 `resolves` 繼續執行；只有沒有 `resolves` 且有未解衝突才 exit 3（`design.md:164`、`:165`）。
  - **事實：** 5.1 依賴與 4.2 正向測試已採正確語意（`tasks.md:323`、`:296`）。
  - **推論：** 這是摘要抄寫不完整；完整契約與驗收預期已一致，故不阻擋。
- **建議：** 改成：「`resolves` 有值但不是未解衝突 → `unknown_target`；有效則繼續；沒有 `resolves` 且有未解衝突 → exit 3。」

只列有變動的 Red 可達性：

| 測試／位置 | 判斷 |
|---|---|
| `test_concurrent_claims_leave_one_owner_and_a_controlled_answer_for_every_loser`，`tasks.md:202` | **可達。** 無 flock 且八個等齊時，輸家沒有 `already_claimed` 回應，精確 `result` 比較失敗。新增紀錄排除了 timeout 未施加競態卻被當成 Red 的情況。 |
| `test_a_human_resolve_conflict_can_keep_the_original`，`:296` | **可達。** 尚未加入解除例外時，合法解除仍被擋成 exit 3，`code == 0` 失敗。新增未知／已解除 cid 案例的 Green 已與 D4 一致。 |
| `test_scope_change_stops_the_run_and_supersedes_the_plan`，`:378` | **可達。** 4.1 的 scope 僅記錄，既有核准仍在，`approval is None` 失敗。改為 `[id]` 不影響此 Red。 |
| `test_undoing_a_scope_change_never_restores_the_approval`，`:380` | **條件式突變可達。** 若前列已實作 `in_effect` 過濾，本列自然先 Green；把 voided 也算入後，前置流程仍成立，放棄 S 後卻得到 `[plan_superseded:S]`，可在指定的 `next.blockers == ["plan_not_approved"]` 比較失敗。該突變也會使 list 斷言失敗，測試應把指定 Red 斷言排在相關後置比較之前。新增 (iv) 則驗證放棄 S2 不會消除 S。 |

實際核對過的檔案：

- 本輪完整重讀：[design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/design.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md)，以及 `8020cbd..020b046` 差異。
- 本輪重讀相關段落：[proposal.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/proposal.md)、[durable-delivery/spec.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/durable-delivery/spec.md)、[delivery-orchestration/spec.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-orchestration/spec.md)、[delivery-gates/spec.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/specs/delivery-gates/spec.md)、[config.yaml](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/config.yaml)、[spec-to-plan/SKILL.md](/Users/johnson.chiang/.claude/skills/spec-to-plan/SKILL.md)。
- 沿用本 session 前輪核對、且本輪確認未變：[decisions.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/decisions.md)、高層 [design.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/design.md)、[validation.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/validation.md)、[tasks.md](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04/tasks.md)、[勘誤](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/design-candidate/d45-04-errata.md)、[現況研究](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/docs/research/2026-09-30/run-decisions/research.md)。