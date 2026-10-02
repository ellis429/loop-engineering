verdict: changes_requested

22 項缺口在**計畫層均已 resolved**；未發現新增的產品行為、固定 spec 或 Red 可達性問題。另有一處 attempt 計數需要更正，屬 **minor，不阻擋功能實作**。本次確認的是計畫，T4.2-03 的程式修正仍待完成。

以下 `design.md`、`tasks.md` 均指 `openspec/changes/run-decisions/` 下的檔案。

| 缺口 | 判定 | 依據與結論 |
|---|---|---|
| DG-01 | resolved | design.md:176、228：明定 duplicate → 歷次否決 → 未解衝突，符合協調者裁定；沒有採用原檢查建議的相反順序。 |
| DG-02 | resolved | design.md:94、172、229、232：補齊衝突提交的 revision、物件檢查、前移、其他 identity 衝突及重送例外。 |
| DG-03 | resolved | design.md:239；tasks.md:315、365：A 驗證失敗回原錯誤、exit 1、不提交且 K 保持未解，並加入測試。 |
| DG-04 | resolved | design.md:353：再次撤銷更新 `voided_by`；354：`replaces` 攤平、最新在前。 |
| DG-05 | resolved | design.md:78、79：明定 `blocked`、錯誤 envelope，以及讀取／寫入衝突的 revision 差異。 |
| DG-06 | resolved | design.md:339：D10 已列出 C、A 各自的 `choice_not_allowed` 條件。 |
| DG-07 | resolved | design.md:304；tasks.md:329、359：採授權預核後才寫物件，並區分整個 HOME 與 run 的快照範圍。 |
| DG-08 | resolved | design.md:335；tasks.md:407：沒有 plan 時拒絕 `scope_change`，回 `plan_not_registered`。 |
| G-01 | resolved | design.md:304；tasks.md:359：非 owner、run 不存在等情況在 `put_object` 前拒絕；owner 的後續拒絕可能留下物件，已明文界定。 |
| G-02 | resolved | design.md:313、321；tasks.md:361、364：排除時間及衍生欄位判定相同登記，保留原時間；校準資料與其他 metadata 改變仍算新登記。 |
| G-03 | resolved | design.md:335；tasks.md:377、407：補齊無 plan 的檢查與測試。 |
| G-04 | resolved | design.md:320、334；tasks.md:358、361、362：錯誤名稱、缺少角色欄位及成功結果均已明定。 |
| G-05 | resolved | design.md:303；tasks.md:359：policy 只要帶 `--content-from` 就拒絕，包含 locator 可讀的情況。 |
| G-06 | resolved | design.md:314；tasks.md:381、408：核准守門 → superseded → no-op → 寫入，並測交疊情況。 |
| G-07 | resolved | design.md:292、298；tasks.md:331、358：相對 cwd、保存原 locator／絕對 path，無關參數忽略。 |
| G-08 | resolved | tasks.md:330、382：明確把 superseded 檢查留給 6.1，避免指定 Red 被 5.1 提前做完。 |
| G-09 | resolved | tasks.md:362、363、494：兩項可能提前變綠的測試均有條件式突變。 |
| G-10 | resolved | tasks.md:35、331、385：前置 helper 留在各自測試模組，不需修改未擁有的 conftest。 |
| G-11 | resolved | design.md:336、348；tasks.md:410、412：同 digest 新 decision 可更新核准；撤銷舊 P 不清除 P2。 |
| G-12 | resolved | design.md:335；tasks.md:378、409(v)：attempted scope 的 `supersedes` 取解除當下 P2，已有反例測試。 |
| G-13 | resolved | tasks.md:443：驗收命令已補齊 token、來源、版本、target 等必要參數及 digest 擷取。 |
| T4.2-03 | resolved | design.md:176；tasks.md:275、314：要求修改順序，新增兩種歷次否決重送的回歸測試；尚不代表現行程式已修正。 |

**P9-01｜minor（不阻擋）**

- **位置**：[tasks.md:273](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md:273)
- **問題**：「還有一次 attempt（第 3 次，也是最後一次）」與既有紀錄不符。第 3 次已完成；接續修正不能再被描述為原額度內尚未使用的第 3 次。
- **依據（事實）**：[attempt-3/result.json:3](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/tasks/4.2/attempt-3/result.json:3) 記載 attempt 3 與 commit `75e6877`；[review-2/result.json:4](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/.delivery/run-decisions/tasks/4.2/review-2/result.json:4) 正是審查該版本並提出 T4.2-03；[tasks.md:504](/Users/johnson.chiang/workspace/loop-engineering-run-decisions/openspec/changes/run-decisions/tasks.md:504) 仍寫最多 3 次、包含修正。
- **建議**：更正為實際的後續 attempt 編號，並記明本次協調者裁定如何適用於既有上限。這是執行紀錄的校正，不需改產品規則或測試。

新增或改寫的 Red 核對如下；「可達」指依計畫順序能在指定斷言失敗，本次沒有執行會寫檔的測試。

| tasks.md 位置／測試 | Red 判斷 |
|---|---|
| :314 `…rejected_content_stays_rejected…` | 可達。兩個參數在 `75e6877` 都回 exit 3，直接違反 `code == 1`；前置衝突與解除可完成。 |
| :315 `…attempted_is_refused…` | 可達。只在套用 A 時吞掉驗證錯誤、留下撤銷，會提交並回 0；前置的有效 budget decision 與衝突建立不受影響。 |
| :358 `…native_documents…` | 可達。原 `plan.locator` 斷言仍能區分 stub；新增 result／無關參數斷言不改其前置。 |
| :359 `…unreadable_documents…` | 可達。讀檔例外由 harness 收進 `exc`，`code == 1` 可失敗；新增授權快照案例不會迫使先前 Red 變綠。 |
| :361 `…only_a_human_approve_plan…` | 可達。指定的未校準檢查仍可回 0 而違反錯誤斷言；新增無 plan、補校準案例不改此原因。 |
| :362 `…needs_spec_ac_and_design_bindings` | 可達。若已實作，移除缺 binding 守門；不完整子集觸發 `code == 1` 失敗，完整前置不受影響。 |
| :363 `…next_after_approval_reports_dispatch` | 可達。移除 D7 的核准列不會阻止核准提交，但 next 回 human，違反 `next.action == "dispatch"`。 |
| :364 `…changing_an_approved_document…` | 可達。指定的已核准變更拒絕尚未實作時仍回 0；新增 metadata／時間案例可獨立驗證。 |
| :365 `…conflict_on_an_applied_approve_plan…` | 可達。原 abandon 參數仍能暴露未清核准；新增錯版本 attempted 能走到 A 的核對，不停在 usage 或衝突建立。 |
| :407 `…scope_change_stops…` | 可達。指定已核准參數仍能暴露 `approval` 未清除；無 plan 是另一參數。 |
| :408 `…only_a_new_plan_version…` | 可達。5.1 明文排除 superseded 檢查；新增核准守門優先序案例不改原 Red。 |
| :409 `…undoing_a_scope_change…` | 可達。既有突變會使 (i) 的 blocker 仍為 superseded；新增 (v) 的 P2 前置及 attempted 路徑成立。 |
| :410 `…policy_is_approved_only…` | 可達。缺少 policy 投影時，指定 status 斷言失敗；精確形狀與第二次核准可另行斷言。 |
| :412 `…undoing_a_policy_change…` | 可達。原 abandon 參數仍暴露 policy 核准未清；新增舊 P／新 P2 案例驗證效果歸屬。 |

15 項突變清單也已逐項核對。相對原風險清單新增列入的 6 項為：

| 測試 | 指定突變及結果 |
|---|---|
| :118 `…explicit_help_prints_usage` | 移除專用 help 分支 → 假 handler 回 7，`code == 0` 失敗。 |
| :160 `…verifies_the_head_and_uploads_the_tested_sha` | 三個獨立突變分別使 SHA 不符卻成功、上傳 path 不符、uv 版本不符；各自命中指定斷言。 |
| :311 `…attempted_cannot_apply_another_resolve_conflict` | 只移除 A 條件、保留 C 條件 → attempted 回 0，`code == 1` 失敗。 |
| :315 `…attempted_is_refused…` | 吞掉 A 驗證錯誤 → 回 0，指定斷言失敗。 |
| :362 `…needs_spec_ac_and_design_bindings` | 條件式移除缺 binding 檢查，指定拒絕斷言失敗。 |
| :363 `…next_after_approval_reports_dispatch` | 條件式移除核准列，指定 next 斷言失敗。 |

其餘 9 項——t4、dist-smoke、單一政策來源、並行 claim、history 前中斷、stale revision、非 owner 重送、非 owner 製造衝突、撤銷 scope——本輪未改變其突變或前置；此次修訂沒有使指定 Red 失去可達性。

5.1／6.1 的擁有路徑足夠：兩者均涵蓋 `cli.py`、`decisions.py`、`state.py`、`next.py` 與各自測試模組，helper 的放置及先後順序已明定。新增規則保留 token 授權、歷史提交邊界、撤銷不還原核准及單一現行 plan；固定 spec 與 proposal 在指定範圍內沒有變動。

實際核對的主要檔案：

- `openspec/changes/run-decisions/{design.md,tasks.md,proposal.md}` 與指定 git diff。
- 同 change 的三份 `specs/*/spec.md`。
- `.delivery/run-decisions/design-check-4.2/result.md`、`design-check/result.md`。
- `.delivery/run-decisions/tasks/4.2/review-2/result.json`、三次 attempt 的 `result.json`。
- `src/loopctl/{cli,store,decisions,state,next}.py` 的相關路徑。
- `/Users/johnson.chiang/.claude/skills/{spec-to-plan,plan-to-code}/SKILL.md` 的相關規則。